"""Fresh, sequential cluster abstraction using the existing discovery LLM client.

Saved results and call records are for inspection only. No result is ever read
to skip a model call; each invocation starts with an empty generated registry.
"""
import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from urllib.parse import urlparse

from .common import PROMPTS, now, read, text_field, write
from src.discover_predicates.llm_client import StageCallError
from src.discover_predicates.storage import atomic_write_text
from src.discover_predicates.validator import validate_predicate, validate_registry


SCHEMA = 'predicate-cluster-abstraction/v1'
FILES = ('system.txt', 'user.txt')
VARIABLES = {'cluster_id', 'arity', 'cluster_members', 'existing_names'}
PLACEHOLDER = re.compile(r'{{([a-z_]+)}}')
CLUSTER_ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')


def _hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _prompt_hashes(files):
    return {name: _hash(files[name]) for name in FILES}


def _prompt_hash(files):
    return _hash(json.dumps(_prompt_hashes(files), sort_keys=True, separators=(',', ':')))


def _validate_prompts(files):
    if set(files) != set(FILES) or any(not isinstance(text, str) or not text.strip()
                                     for text in files.values()):
        raise ValueError('抽象 Prompt 必须包含完整的 system.txt 和 user.txt')
    for name in FILES:
        placeholders = re.findall(r'{{.*?}}', files[name], re.S)
        expected = VARIABLES if name == 'user.txt' else set()
        if (set(PLACEHOLDER.findall(files[name])) != expected or
                any(not PLACEHOLDER.fullmatch(token) for token in placeholders)):
            raise ValueError(f'抽象 Prompt {name} 的模板变量无效')


def snapshot(settings, root):
    """Freeze only these two prompts, independently of Discovery PROMPT_FILES."""
    files = {name: (PROMPTS / 'cluster_abstraction' / name).read_text(encoding='utf-8')
             for name in FILES}
    _validate_prompts(files)
    model = text_field(settings, 'model', limit=200)
    base_url = text_field(settings, 'base_url', limit=2000).rstrip('/')
    parsed = urlparse(base_url)
    try:
        parsed.port
    except ValueError:
        raise ValueError('抽象 Chat API 地址端口无效') from None
    if (not model or parsed.scheme not in ('http', 'https') or not parsed.hostname or
            parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('请先配置实验模型及无凭据、查询参数的 HTTP(S) Chat Base URL')
    config = {'schema': SCHEMA, 'model': model, 'base_url': base_url,
              'max_retries': 3, 'max_tokens': 32768, 'context_tokens': 1048576,
              'timeout_seconds': 600, 'prompt_hash': _prompt_hash(files),
              'prompt_hashes': _prompt_hashes(files)}
    for name, content in files.items():
        atomic_write_text(root / 'prompts/cluster_abstraction' / name, content)
    return config


def load_snapshot(root, config):
    files = {name: (root / 'prompts/cluster_abstraction' / name).read_text(encoding='utf-8')
             for name in FILES}
    _validate_prompts(files)
    if (config.get('schema') != SCHEMA or config.get('prompt_hash') != _prompt_hash(files)
            or config.get('prompt_hashes') != _prompt_hashes(files)):
        raise ValueError('抽象 Prompt 快照或 SHA-256 不一致，拒绝运行')
    return {**config, 'files': files}


def _safe_record(llm_client, value):
    value = llm_client.client.redactor.walk(value)
    # Protect both configured provider keys, including keys embedded in errors.
    def safe(item):
        if isinstance(item, str):
            for variable in ('DEEPSEEK_API_KEY', 'AGENTCM_EMBEDDING_API_KEY'):
                key = os.environ.get(variable, '')
                if key:
                    item = item.replace(key, '[REDACTED]')
            return item
        if isinstance(item, list):
            return [safe(v) for v in item]
        if isinstance(item, dict):
            return {k: safe(v) for k, v in item.items()}
        return item
    return safe(value)


def _validate_final(groups, registry, mapping):
    validate_registry(registry)
    if (not groups or not isinstance(mapping, list) or
            len(registry) != len(groups) or len(mapping) != len(groups)):
        raise ValueError('抽象 Registry 未满足每个 Cluster 恰好一个谓词的约束')
    for group, predicate, item in zip(groups, registry, mapping):
        expected = {'cluster_id': group['cluster_id'], 'abstracted_predicate': predicate['name'],
                    'arity': group['arity'], 'source_predicates': [p['name'] for p in group['members']]}
        if item != expected or len(predicate['parameters']) != group['arity']:
            raise ValueError('抽象 Registry 的元数或原始成员映射不一致')


def abstract_clusters(groups, llm_client, prompt_snapshot, output_dir, progress):
    """Call every cluster in its existing order, including singleton clusters."""
    if not groups or len({g['cluster_id'] for g in groups}) != len(groups):
        raise ValueError('抽象输入 Cluster 为空或 ID 重复')
    for group in groups:
        if not isinstance(group['cluster_id'], str) or not CLUSTER_ID.fullmatch(group['cluster_id']):
            raise ValueError('抽象输入 Cluster ID 无效')
        validate_registry(group['members'])
        if (type(group['arity']) is not int or group['arity'] < 1 or not group['members']
                or any(len(p['parameters']) != group['arity'] for p in group['members'])):
            raise ValueError('抽象输入 Cluster 的成员元数不一致')

    output_dir = Path(output_dir)
    directory = output_dir / 'cluster_abstraction'
    run_id = uuid.uuid4().hex
    manifest = {'schema': SCHEMA, 'run_id': run_id, 'status': 'running',
                'started_at': now(), 'prompt_hash': prompt_snapshot['prompt_hash'],
                'model': llm_client.model, 'total_clusters': len(groups),
                'completed_clusters': 0, 'current_cluster_id': None}
    write(directory / 'execution.json', manifest)
    # A new stage has no final registry until every fresh call has succeeded.
    for name in ('abstracted_registry.json', 'abstraction_mapping.json'):
        (output_dir / name).unlink(missing_ok=True)
    registry, mapping, names = [], [], set()

    def report(stage, message, current=None):
        manifest.update(completed_clusters=len(registry), current_cluster_id=current,
                        updated_at=now())
        write(directory / 'execution.json', manifest)
        progress(stage, stage=stage, abstraction_run_id=run_id,
                 abstraction_total_clusters=len(groups),
                 completed_abstraction_clusters=len(registry),
                 generated_predicates=len(registry), current_abstraction_cluster=current,
                 message=message)

    try:
        for group in groups:
            cluster_id, arity = group['cluster_id'], group['arity']
            report('cluster_abstraction',
                   f'Predicate Abstraction：已完成 {len(registry)}/{len(groups)} 个 Cluster；'
                   f'当前 {cluster_id}；已生成 {len(registry)} 个 Predicate', cluster_id)
            values = {'cluster_id': cluster_id, 'arity': str(arity),
                      'cluster_members': json.dumps(group['members'], ensure_ascii=False, indent=2),
                      'existing_names': json.dumps([p['name'] for p in registry], ensure_ascii=False)}
            # Substitute only original template variables; member text is never a template.
            user = PLACEHOLDER.sub(lambda match: values[match[1]], prompt_snapshot['files']['user.txt'])

            def validate(value):
                try:
                    validate_predicate(value)
                except ValueError as exc:
                    raise ValueError(_safe_record(llm_client, str(exc))) from None
                if len(value['parameters']) != arity:
                    raise ValueError(f'{cluster_id} 生成谓词必须保持 {arity} 元')
                if value['name'] in names:
                    raise ValueError(f'抽象谓词名称重复：{value["name"]}')
                for variable in ('DEEPSEEK_API_KEY', 'AGENTCM_EMBEDDING_API_KEY'):
                    key = os.environ.get(variable, '')
                    if key and key in json.dumps(value, ensure_ascii=False):
                        raise ValueError('抽象输出包含受保护的模型凭据')

            call_path = directory / 'calls' / run_id / (cluster_id + '.json')
            try:
                predicate, record = llm_client.call(
                    stage='cluster_abstraction', window_name=cluster_id,
                    prompt_version=prompt_snapshot['prompt_hash'],
                    system=prompt_snapshot['files']['system.txt'], user=user, validator=validate)
            except StageCallError as exc:
                write(call_path, _safe_record(llm_client, exc.record))
                raise
            write(call_path, _safe_record(llm_client, record))
            names.add(predicate['name'])
            registry.append(predicate)
            sources = [p['name'] for p in group['members']]
            write(directory / (cluster_id + '.json'), {
                'run_id': run_id, 'cluster_id': cluster_id, 'arity': arity,
                'source_predicate_names': sources, 'prompt_hash': prompt_snapshot['prompt_hash'],
                'model': llm_client.model, 'abstracted_predicate': predicate})
            mapping.append({'cluster_id': cluster_id, 'abstracted_predicate': predicate['name'],
                            'arity': arity, 'source_predicates': sources})
            report('cluster_abstraction',
                   f'Predicate Abstraction：已完成 {len(registry)}/{len(groups)} 个 Cluster；'
                   f'已生成 {len(registry)} 个 Predicate', cluster_id)
        _validate_final(groups, registry, mapping)
        report('cluster_abstraction_save', '保存完整抽象 Registry 与原始成员映射')
        write(output_dir / 'abstracted_registry.json', registry)
        write(output_dir / 'abstraction_mapping.json', mapping)
        manifest.update(status='completed', completed_at=now())
        write(directory / 'execution.json', manifest)
        return registry
    except Exception:
        manifest.update(status='failed', updated_at=now())
        write(directory / 'execution.json', manifest)
        raise


def results(output_dir, run_id):
    """Read only results produced during the current abstraction invocation."""
    directory = output_dir / 'cluster_abstraction'
    manifest = read(directory / 'execution.json', {})
    items = []
    if not run_id or manifest.get('run_id') != run_id:
        return {'execution': {}, 'results': []}
    if manifest.get('run_id'):
        for path in sorted(directory.glob('*.json')):
            if path.name == 'execution.json':
                continue
            item = read(path, {})
            if item.get('run_id') == manifest['run_id'] and 'abstracted_predicate' in item:
                items.append(item)
    return {'execution': manifest, 'results': items}


def export(workspace, identity, mapping=False):
    root, output = workspace.paths(identity)
    meta = read(root / 'experiment.json')
    if meta.get('kind') != 'clustering' or 'abstraction' not in meta:
        raise ValueError('该实验没有 LLM 谓词抽象阶段')
    state = read(output / 'execution_state.json', {})
    manifest = read(output / 'cluster_abstraction/execution.json', {})
    if (state.get('status') != 'completed' or manifest.get('status') != 'completed' or
            not state.get('abstraction_run_id') or
            manifest.get('run_id') != state['abstraction_run_id']):
        raise ValueError('全部 Cluster 抽象完成并校验通过后才能导出抽象结果')
    registry = read(output / 'abstracted_registry.json')
    saved_mapping = read(output / 'abstraction_mapping.json', [])
    _validate_final(read(output / 'clusters.json', {}).get('groups', []), registry, saved_mapping)
    if len(registry) != meta['config']['target_clusters']:
        raise ValueError('抽象 Registry 的谓词数量与 Cluster 数量不一致')
    return saved_mapping if mapping else registry
