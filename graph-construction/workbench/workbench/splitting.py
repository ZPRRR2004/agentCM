"""Splitting experiments: explicit parameters, frozen trajectories, resumable windows."""
import hashlib
import json
import shutil
import uuid
import os

from .common import DISCOVERY, now, read, text_field, write, load_windows
from .datasets import content_hash, load_trajectories
from .preprocessing import source_records
from src.split.main import output_stems
from src.split.splitter import split_trajectory
from src.split.legacy import split_trajectory as split_legacy
from src.split.token_counter import count_core_tokens
from src.split.window_builder import build_window
from src.split.summary_generator import SummaryGenerator

SPLIT_PROMPTS = DISCOVERY / 'src/split/prompts'
FIELDS = {
    'max_window_events': ('每窗口核心事件上限', 1, 100000),
    'overlap_events': ('重叠事件数', 0, 100000),
    'max_previous_summary_tokens': ('前文摘要 Token 上限', 0, 100000),
    'max_future_summary_tokens': ('后文摘要 Token 上限', 0, 100000),
}


def parameters(body):
    values = body.get('config')
    if not isinstance(values, dict) or set(values) != set(FIELDS):
        raise ValueError('请填写事件数、重叠事件数和两项摘要参数')
    for key, (label, low, high) in FIELDS.items():
        if type(values[key]) is not int or not low <= values[key] <= high:
            raise ValueError(f'{label}必须是 {low}–{high} 范围内的整数')
    return values


def uses_model(config):
    return any(config[k] > 0 for k in ('max_previous_summary_tokens', 'max_future_summary_tokens'))


def select_trajectories(records, body, *, require_events=True):
    selected = body.get('trajectory_ids')
    if selected is not None and (not isinstance(selected, list) or not all(isinstance(s, str) for s in selected)):
        raise ValueError('任务选择无效')
    if selected == []:
        raise ValueError('请至少选择一条轨迹')
    if selected:
        if set(selected) - {r.trajectory_id for r in records}:
            raise ValueError('任务不属于当前数据集')
        records = [r for r in records if r.trajectory_id in selected]
    if not records or (require_events and not any(r.data['events'] for r in records)):
        raise ValueError('请选择包含执行事件的轨迹')
    return records


def create(workspace, body):
    config = parameters(body)
    dataset_id = text_field(body, 'dataset_id', limit=100)
    dataset, _ = workspace.catalog.resolve(dataset_id)
    available, lineage = source_records(workspace, body)
    records = select_trajectories(available, body)
    title = text_field(body, 'title', limit=200)
    if not title:
        raise ValueError('请填写实验名称')
    identity = uuid.uuid4().hex[:12]
    root = workspace.data / 'experiments' / identity
    (root / 'inputs').mkdir(parents=True)
    for record in records:
        shutil.copyfile(record.path, root / 'inputs' / record.path.name)
    shutil.copytree(SPLIT_PROMPTS, root / 'prompts')
    prompt_data = {p.relative_to(root / 'prompts').as_posix(): p.read_text(encoding='utf-8')
                   for p in sorted((root / 'prompts').rglob('*.txt'))}
    prompt_hash = hashlib.sha256(json.dumps(prompt_data, sort_keys=True).encode()).hexdigest()
    settings = workspace.settings()
    write(root / 'experiment.json', {
        **lineage, 'id': identity, 'kind': 'split', 'title': title, 'question': text_field(body, 'question'),
        'dataset_id': dataset_id, 'dataset_name': dataset['name'],
        'trajectory_source': dataset.get('trajectory_source'),
        'trajectory_ids': [r.trajectory_id for r in records], 'trajectory_count': len(records),
        'input_state': 'ready',
        'input_hash': content_hash(records), 'created_at': now(), 'config': config,
        'prompt_hash': prompt_hash, 'model': settings['model'] if uses_model(config) else '',
        'base_url': settings['base_url'], 'algorithm': 'event-count/v2',
        'token_estimator': 'ceil(compact_json_characters / 4)',
    })
    write(root / 'lifecycle.json', {'status': 'draft', 'updated_at': now()})
    return workspace.experiment(identity, detail=True)


def attach(workspace, body):
    """Attach a completed preprocessing result to a historical empty draft."""
    identity = text_field(body, 'id', limit=100)
    root, _ = workspace.paths(identity)
    meta = read(root / 'experiment.json')
    if meta.get('kind') != 'split' or meta.get('input_state') != 'awaiting_input':
        raise ValueError('只有等待轨迹的切分草稿可以接入输入；已有快照请新建对照实验')
    available, lineage = source_records(workspace, {**body, 'dataset_id': meta['dataset_id']})
    records = select_trajectories(available, body)
    dataset, _ = workspace.catalog.resolve(meta['dataset_id'])
    staging = root / ('inputs-' + uuid.uuid4().hex)
    staging.mkdir()
    try:
        for record in records:
            shutil.copyfile(record.path, staging / record.path.name)
        frozen = load_trajectories(staging)
        digest = content_hash(frozen)
        if digest != content_hash(records):
            raise ValueError('导入期间轨迹内容发生变化，请重新选择')
        inputs = root / 'inputs'
        # Pending drafts contain no input snapshot; recover a failed metadata write.
        if inputs.exists():
            shutil.rmtree(inputs)
        staging.rename(inputs)
        meta.update(**lineage, input_state='ready', input_hash=digest, input_attached_at=now(),
                    trajectory_ids=[r.trajectory_id for r in records], trajectory_count=len(records),
                    trajectory_source=dataset.get('trajectory_source'))
        write(root / 'experiment.json', meta)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return workspace.experiment(identity, detail=True)


def run(root, transport=None, progress=None):
    progress = progress or (lambda *args, **kwargs: None)
    meta = read(root / 'experiment.json')
    config = meta['config']
    records = load_trajectories(root / 'inputs')
    if not records or meta.get('input_state') == 'awaiting_input':
        raise ValueError('请先接入执行轨迹，再开始切分')
    if content_hash(records) != meta['input_hash']:
        raise ValueError('输入快照发生变化，请创建新实验')
    output = root / 'output'
    state = read(output / 'execution_state.json', {'completed_keys': []})
    completed = set(state['completed_keys'])
    generator = SummaryGenerator(output, model=meta['model'], base_url=meta['base_url'],
                                 prompts_directory=root / 'prompts', transport=transport) if uses_model(config) else None
    if generator:
        original_transport = generator.client.transport
        def audited_transport(payload):
            directory = output / 'summary_calls' / uuid.uuid4().hex
            write(directory / 'request.json', payload)
            progress('summary_wait', waiting_since=now(), message='摘要请求已发送，等待模型返回')
            try:
                result = original_transport(payload)
                progress('summary_received', message='已收到摘要，正在检查结果')
                write(directory / 'response.json', result)
                return result
            except Exception as exc:
                key = os.environ.get('DEEPSEEK_API_KEY', '')
                error = str(exc).replace(key, '[REDACTED]') if key else str(exc)
                write(directory / 'error.json', {'error': error, 'created_at': now()})
                progress('summary_error', message=f'摘要请求失败：{error}')
                raise
        generator.client.transport = audited_transport
    names = output_stems([r.path for r in records])
    splitter = split_legacy if meta.get('algorithm') == 'event-greedy/v1' else split_trajectory
    state.update(status='running', next_stage='切分轨迹', completed_trajectories=0)
    write(output / 'execution_state.json', state)
    for record in records:
        progress('trajectory_start', stage='split', trajectory_id=record.trajectory_id,
                 message=f'切分第 {state["completed_trajectories"] + 1}/{len(records)} 条轨迹：{record.trajectory_id}')
        for index, window in enumerate(splitter(record.data['events'], config), 1):
            key = f'{names[record.path]}__{window["window_id"]}'
            destination = output / 'windows' / (key + '.json')
            if key not in completed or not destination.is_file():
                progress('window_start', window_id=window['window_id'],
                         message=f'生成 {window["window_id"]}，包含 {len(window["core_events"])} 个 agent event')
                query = record.data['query']
                if generator:
                    progress('summary_start', stage='previous_summary', message='准备前文摘要')
                previous = generator.previous(query, window['previous_events'], config['max_previous_summary_tokens']) if generator else ''
                if generator:
                    progress('summary_start', stage='future_summary', message='准备后文摘要')
                future = generator.future(query, window['future_events'], config['max_future_summary_tokens']) if generator else ''
                result = build_window(trajectory_id=record.trajectory_id, window_id=window['window_id'],
                                      user_query=query, previous_summary=previous, future_summary=future,
                                      core_events=window['core_events'], overlap_events=window['overlap_events'],
                                      metadata={**window['metadata'], 'window_index': index,
                                                'source_file': record.path.name,
                                                'split_experiment_id': meta['id'], 'source_sha256': record.sha256})
                write(destination, result)
                completed.add(key)
                state.update(completed_keys=sorted(completed), window_count=len(completed), updated_at=now())
                write(output / 'execution_state.json', state)
                progress('window_done', stage='split', message=f'已保存 {window["window_id"]}，累计 {len(completed)} 个窗口')
        state['completed_trajectories'] += 1
        write(output / 'execution_state.json', state)
    windows = load_windows(output / 'windows')
    counts = [len(r.data['core']['events']) for r in windows]
    tokens = [r.data['metadata']['core_tokens'] for r in windows]
    context_tokens = [r.data['metadata']['context_tokens'] if 'context_tokens' in r.data['metadata']
                      else count_core_tokens(r.data['overlap']['events'] + r.data['core']['events'])
                      for r in windows]
    stats = {'window_count': len(windows), 'trajectory_count': len(records), 'core_events': sum(counts),
             'min_events': min(counts, default=0), 'max_events': max(counts, default=0),
             'mean_events': round(sum(counts) / max(1, len(counts)), 2),
             'max_core_tokens': max(tokens, default=0),
             'max_context_tokens': max(context_tokens, default=0),
             'output_hash': content_hash(windows)}
    write(output / 'statistics.json', stats)
    state.update(status='completed', next_stage='切分完成', updated_at=now())
    write(output / 'execution_state.json', state)
