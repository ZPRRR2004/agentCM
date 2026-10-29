"""Deterministic, auditable field projection of normalized trajectories."""
import copy
import json
import math

VERSION = 'trajectory-fields/v2'
LEGACY_VERSION = 'trajectory-fields/v1'
RULES = {
    'deduplicate_observation': '去除重复工具输出结构',
    'remove_source_lines': '移出事件中的来源行号',
    'simplify_call_ids': '精简调用标识',
}


def validate_rules(config):
    required = set(RULES) - {'simplify_call_ids'}
    if (not isinstance(config, dict) or not required <= set(config) <= set(RULES)
            or any(type(v) is not bool for v in config.values())):
        raise ValueError('请选择有效的预处理规则')
    # Frozen v1 experiments keep the original two rules and their original IDs.
    return {'simplify_call_ids': False, **config}


def size(events):
    characters = len(json.dumps(events, ensure_ascii=False, separators=(',', ':')))
    return {'characters': characters, 'tokens': math.ceil(characters / 4)}


def redundant_content(observation):
    content = observation.get('content')
    if isinstance(content, str):
        return content == observation.get('raw')
    # Extra fields, media, annotations, and mixed block types carry information.
    if not isinstance(content, list) or not content:
        return False
    if not all(isinstance(p, dict) and set(p) == {'type', 'text'}
               and p['type'] == 'text' and isinstance(p['text'], str) for p in content):
        return False
    return '\n'.join(p['text'] for p in content) == observation.get('raw')


def compact_trajectory(original, config):
    config = validate_rules(config)
    value = copy.deepcopy(original)
    changes = []
    call_id_mapping = []
    for i, event in enumerate(value['events']):
        event_id = event['event_id']
        prefix = f'events[{i}]'
        def remove(obj, field, path, rule):
            if field in obj:
                del obj[field]
                changes.append({'event_id': event_id, 'path': path + '.' + field,
                                'operation': 'remove', 'rule': rule, 'reason': RULES[rule]})
        if config['remove_source_lines']:
            remove(event, 'source_line', prefix, 'remove_source_lines')
        for j, call in enumerate(event.get('tool_calls', [])):
            call_path = f'{prefix}.tool_calls[{j}]'
            if config['simplify_call_ids']:
                original_id = call.get('tool_call_id')
                if not isinstance(original_id, str) or not original_id.strip():
                    raise ValueError(f'{call_path}.tool_call_id 需要有效的原始编号')
                short_id = f'call-{len(call_id_mapping) + 1:04d}'
                mapping = {'event_id': event_id, 'path': call_path,
                           'short_id': short_id, 'original_tool_call_id': original_id}
                if 'source_call_id' in call:
                    mapping['original_source_call_id'] = call['source_call_id']
                call_id_mapping.append(mapping)
                if original_id != short_id:
                    call['tool_call_id'] = short_id
                    changes.append({'event_id': event_id, 'path': call_path + '.tool_call_id',
                                    'operation': 'replace', 'rule': 'simplify_call_ids',
                                    'reason': RULES['simplify_call_ids'],
                                    'before': original_id, 'after': short_id})
                remove(call, 'source_call_id', call_path, 'simplify_call_ids')
            observation = call.get('observation', {})
            path = call_path + '.observation'
            if config['deduplicate_observation'] and redundant_content(observation):
                remove(observation, 'content', path, 'deduplicate_observation')
            if config['remove_source_lines']:
                remove(observation, 'source_line', path, 'remove_source_lines')
    before, after = size(original['events']), size(value['events'])
    return value, {'changes': changes, 'before': before, 'after': after,
                   'call_id_mapping': call_id_mapping,
                   'events': len(value['events']),
                   'removed_fields': sum(c['operation'] == 'remove' for c in changes),
                   'replaced_fields': sum(c['operation'] == 'replace' for c in changes),
                   'changed_events': len({c['event_id'] for c in changes}),
                   'saved_tokens': before['tokens'] - after['tokens'],
                   'reduction_percent': round(100 * (before['characters'] - after['characters']) /
                                              max(1, before['characters']), 2)}
