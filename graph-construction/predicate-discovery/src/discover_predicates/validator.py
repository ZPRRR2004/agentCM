"""Strict validators for Predicates, stage responses, and revision plans."""
import re
from src.trajectory_nodes import NODE_TYPES


PREDICATE_SCHEMA_VERSION = 'predicate-definition/v2'

PARAMETER_TYPES = NODE_TYPES
PREDICATE_FIELDS = {
    'name', 'definition', 'parameters',
    'assertion_conditions', 'exclusion_conditions',
}
PREDICATE_NAME = re.compile(r'^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$')
PARAMETER_NAME = re.compile(r'^[a-z][a-z0-9_]*$')


class ValidationError(ValueError):
    pass


def _exact_keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValidationError(f'{label} 必须且只能包含字段：{sorted(expected)}')


def validate_predicate(value, label='Predicate'):
    _exact_keys(value, PREDICATE_FIELDS, label)
    for field in ('name', 'definition'):
        if not isinstance(value[field], str) or not value[field].strip():
            raise ValidationError(f'{label}.{field} 必须是非空字符串')
    if not PREDICATE_NAME.fullmatch(value['name']):
        raise ValidationError(
            f'{label}.name 必须使用大写字母、数字和下划线：{value["name"]!r}')
    parameters = value['parameters']
    if not isinstance(parameters, list) or not parameters:
        raise ValidationError(f'{label}.parameters 必须是非空、有序参数数组')
    names = set()
    for index, parameter in enumerate(parameters):
        where = f'{label}.parameters[{index}]'
        _exact_keys(parameter, {'name', 'type', 'description'}, where)
        name = parameter['name']
        if not isinstance(name, str) or not PARAMETER_NAME.fullmatch(name):
            raise ValidationError(f'{where}.name 必须使用小写字母、数字和下划线')
        if name in names:
            raise ValidationError(f'{label} 参数名称重复：{name}')
        names.add(name)
        parameter_type = parameter['type']
        base_type = (parameter_type[:-2] if isinstance(parameter_type, str)
                     and parameter_type.endswith('[]') else parameter_type)
        if not isinstance(base_type, str) or base_type not in PARAMETER_TYPES:
            raise ValidationError(f'{where}.type 必须是已定义对象类型或其 [] 集合类型')
        if not isinstance(parameter['description'], str) or not parameter['description'].strip():
            raise ValidationError(f'{where}.description 必须是非空参数角色说明')
    for field in ('assertion_conditions', 'exclusion_conditions'):
        conditions = value[field]
        if not isinstance(conditions, list) or any(
                not isinstance(item, str) or not item.strip() for item in conditions):
            raise ValidationError(f'{label}.{field} 必须是非空字符串组成的数组')
        if len(conditions) != len(set(conditions)):
            raise ValidationError(f'{label}.{field} 包含重复条件')
    if not value['assertion_conditions']:
        raise ValidationError(f'{label}.assertion_conditions 至少需要一个成立条件')
    return value


def predicate_signature(value):
    """Display ordered roles without asserting an instance or executing a rule."""
    validate_predicate(value)
    arguments = ', '.join(f"{p['name']}: {p['type']}" for p in value['parameters'])
    return f"{value['name']}({arguments})"


def validate_predicate_list(values, label):
    if not isinstance(values, list):
        raise ValidationError(f'{label} 必须是数组')
    names = []
    for index, value in enumerate(values):
        validate_predicate(value, f'{label}[{index}]')
        names.append(value['name'])
    if len(names) != len(set(names)):
        raise ValidationError(f'{label} 中存在重复谓词名称')
    return values


def validate_registry(registry):
    return validate_predicate_list(registry, 'Registry')


def validate_discovery(value):
    _exact_keys(value, {'candidate_predicates'}, 'Discovery 输出')
    validate_predicate_list(value['candidate_predicates'], 'candidate_predicates')
    return value


def validate_comparison(value, candidates, registry):
    _exact_keys(value, {'existing', 'new', 'uncertain'}, 'Comparison 输出')
    for key in ('existing', 'new', 'uncertain'):
        if not isinstance(value[key], list):
            raise ValidationError(f'comparison.{key} 必须是数组')

    candidate_by_name = {item['name']: item for item in candidates}
    registry_by_name = {item['name']: item for item in registry}
    registry_names = set(registry_by_name)
    classified = []

    for index, item in enumerate(value['existing']):
        _exact_keys(item, {'candidate_name', 'matched_existing_name'},
                    f'existing[{index}]')
        for field in ('candidate_name', 'matched_existing_name'):
            if not isinstance(item[field], str) or not item[field].strip():
                raise ValidationError(f'existing[{index}].{field} 必须是非空字符串')
        if item['candidate_name'] not in candidate_by_name:
            raise ValidationError(f'未知候选谓词：{item["candidate_name"]}')
        if item['matched_existing_name'] not in registry_names:
            raise ValidationError(f'未知 Registry 谓词：{item["matched_existing_name"]}')
        candidate = candidate_by_name[item['candidate_name']]
        matched = registry_by_name[item['matched_existing_name']]
        if ([parameter['type'] for parameter in candidate['parameters']] !=
                [parameter['type'] for parameter in matched['parameters']]):
            raise ValidationError('existing 匹配的有序参数类型不兼容；请使用 new 或 uncertain')
        classified.append(item['candidate_name'])

    for category in ('new', 'uncertain'):
        validate_predicate_list(value[category], category)
        for item in value[category]:
            if item['name'] not in candidate_by_name:
                raise ValidationError(f'{category} 包含未知候选谓词：{item["name"]}')
            if item != candidate_by_name[item['name']]:
                raise ValidationError(f'{category} 必须原样保留候选谓词的参数和定义')
            classified.append(item['name'])

    expected = list(candidate_by_name)
    if len(classified) != len(set(classified)):
        raise ValidationError('同一候选谓词被重复分类')
    if set(classified) != set(expected):
        missing = sorted(set(expected) - set(classified))
        extra = sorted(set(classified) - set(expected))
        raise ValidationError(f'候选分类不完整；缺失={missing}，额外={extra}')
    if not registry and (value['existing'] or value['uncertain'] or
                         {item['name'] for item in value['new']} != set(expected)):
        raise ValidationError('Registry 为空时，所有候选谓词必须分类为 new')
    return value


def validate_review(value, candidates, comparison, registry):
    _exact_keys(value, {'accepted_predicates', 'revised_existing_predicates'},
                'Review 输出')
    accepted = validate_predicate_list(value['accepted_predicates'],
                                       'accepted_predicates')
    revisions = value['revised_existing_predicates']
    if not isinstance(revisions, list):
        raise ValidationError('revised_existing_predicates 必须是数组')
    if not candidates and (accepted or revisions):
        raise ValidationError('候选列表为空时不能新增或修订谓词')

    registry_names = {item['name'] for item in registry}
    matched_names = {item['matched_existing_name']
                     for item in comparison['existing']}
    revised_by_name = {}
    for index, item in enumerate(revisions):
        label = f'revised_existing_predicates[{index}]'
        _exact_keys(item, {'original_name', 'revised_predicate'}, label)
        original_name = item['original_name']
        if not isinstance(original_name, str) or not original_name.strip():
            raise ValidationError(f'{label}.original_name 必须是非空字符串')
        if original_name not in registry_names:
            raise ValidationError(f'{label} 引用了未知 Registry 谓词：{original_name}')
        if original_name not in matched_names:
            raise ValidationError(
                f'{label} 的原谓词不在本轮 Comparison existing 匹配中：'
                f'{original_name}')
        if original_name in revised_by_name:
            raise ValidationError(f'同一已有谓词被重复修订：{original_name}')
        validate_predicate(item['revised_predicate'],
                           f'{label}.revised_predicate')
        revised_by_name[original_name] = item['revised_predicate']

    final_names = [revised_by_name.get(predicate['name'], predicate)['name']
                   for predicate in registry]
    final_names.extend(item['name'] for item in accepted)
    if len(final_names) != len(set(final_names)):
        conflicts = sorted(name for name in set(final_names)
                           if final_names.count(name) > 1)
        raise ValidationError(f'Review 更新后 Registry 谓词名称冲突：{conflicts}')
    return value


def validate_registry_update(registry_snapshot, accepted_predicates):
    validate_registry(registry_snapshot)
    validate_predicate_list(accepted_predicates, 'accepted_predicates')
    existing = {item['name'] for item in registry_snapshot}
    conflicts = sorted(existing & {item['name'] for item in accepted_predicates})
    if conflicts:
        raise ValidationError(f'新增谓词名称与 Registry 冲突：{conflicts}')
    return True


REVISION_OPERATIONS = {'KEEP', 'DELETE', 'REVISE', 'MERGE'}


def validate_registry_revision_plan(revision_plan, existing_registry):
    """Validate one order-independent operation for every Registry type."""
    validate_registry(existing_registry)
    _exact_keys(revision_plan, {'revisions'}, 'Registry Revision 输出')
    revisions = revision_plan['revisions']
    if not isinstance(revisions, list):
        raise ValidationError('revisions 必须是数组')

    registry_names = {item['name'] for item in existing_registry}
    revision_by_name = {}
    for index, item in enumerate(revisions):
        label = f'revisions[{index}]'
        if not isinstance(item, dict):
            raise ValidationError(f'{label} 必须是对象')
        original_name = item.get('original_name')
        operation = item.get('operation')
        if not isinstance(original_name, str) or not original_name.strip():
            raise ValidationError(f'{label}.original_name 必须是非空字符串')
        if operation not in REVISION_OPERATIONS:
            raise ValidationError(
                f'{label}.operation 必须是 KEEP、DELETE、REVISE 或 MERGE')
        if original_name not in registry_names:
            raise ValidationError(f'{label} 引用了未知原始谓词：{original_name}')
        if original_name in revision_by_name:
            raise ValidationError(f'原始谓词被重复处理：{original_name}')

        if operation in {'KEEP', 'DELETE'}:
            _exact_keys(item, {'original_name', 'operation'}, label)
        elif operation == 'REVISE':
            _exact_keys(
                item, {'original_name', 'operation', 'revised_predicate'}, label)
            validate_predicate(item['revised_predicate'],
                               f'{label}.revised_predicate')
        else:
            _exact_keys(item, {'original_name', 'operation', 'merge_into'}, label)
            merge_into = item['merge_into']
            if not isinstance(merge_into, str) or not merge_into.strip():
                raise ValidationError(f'{label}.merge_into 必须是非空字符串')
            if merge_into == original_name:
                raise ValidationError(f'{label} 不能合并到自身')
            if merge_into not in registry_names:
                raise ValidationError(
                    f'{label}.merge_into 引用了未知原始谓词：{merge_into}')
        revision_by_name[original_name] = item

    planned_names = set(revision_by_name)
    if planned_names != registry_names:
        missing = sorted(registry_names - planned_names)
        extra = sorted(planned_names - registry_names)
        raise ValidationError(
            f'Revision Plan 未完整覆盖 Registry；缺失={missing}，额外={extra}')

    for original_name, item in revision_by_name.items():
        if item['operation'] != 'MERGE':
            continue
        target = item['merge_into']
        target_operation = revision_by_name[target]['operation']
        if target_operation not in {'KEEP', 'REVISE'}:
            raise ValidationError(
                f'{original_name} 的 MERGE 目标 {target} 必须执行 KEEP 或 REVISE')
        originals = {predicate['name']: predicate for predicate in existing_registry}
        retained = (revision_by_name[target]['revised_predicate']
                    if target_operation == 'REVISE' else originals[target])
        source_types = [parameter['type'] for parameter in originals[original_name]['parameters']]
        target_types = [parameter['type'] for parameter in retained['parameters']]
        if source_types != target_types:
            raise ValidationError(f'{original_name} 与 {target} 的有序参数类型不兼容，不能直接合并')

    final_names = []
    for predicate in existing_registry:
        revision = revision_by_name[predicate['name']]
        if revision['operation'] == 'KEEP':
            final_names.append(predicate['name'])
        elif revision['operation'] == 'REVISE':
            final_names.append(revision['revised_predicate']['name'])
    if len(final_names) != len(set(final_names)):
        duplicates = sorted(
            name for name in set(final_names) if final_names.count(name) > 1)
        raise ValidationError(f'Revision 后谓词名称不唯一：{duplicates}')
    return revision_plan
