"""Frozen preprocessing experiments, comparison views, and downstream inputs."""
import shutil
import uuid

from .common import now, read, text_field, write
from .datasets import content_hash, load_trajectories
from .trajectory_selection import POLICY, select_records, selection_mode, trajectory_summary
from src.preprocess.compact import VERSION, LEGACY_VERSION, compact_trajectory, validate_rules


def report_statistics(report):
    return {k: v for k, v in report.items() if k not in ('changes', 'call_id_mapping')}


def selected_inputs(workspace, body):
    from .splitting import select_trajectories
    dataset_id = text_field(body, 'dataset_id', limit=100)
    records = workspace.catalog.records(dataset_id)
    # An explicitly empty selection is different from an omitted selection (all).
    if body.get('trajectory_ids') == []:
        return []
    return select_trajectories(records, body, require_events=False) if records else []


def preview_selection(workspace, body):
    return select_records(selected_inputs(workspace, body), body.get('selection_mode', 'all'))[1]


def create(workspace, body):
    config = validate_rules(body.get('config'))
    dataset_id = text_field(body, 'dataset_id', limit=100)
    dataset, _ = workspace.catalog.resolve(dataset_id)
    records = selected_inputs(workspace, body)
    mode = selection_mode(body.get('selection_mode', 'all'))
    kept, selection = select_records(records, mode)
    if not kept:
        raise ValueError('当前结果条件下没有可处理轨迹，请调整轨迹选择或结果范围')
    title = text_field(body, 'title', limit=200)
    if not title:
        raise ValueError('请填写实验名称')
    identity = uuid.uuid4().hex[:12]
    root = workspace.data / 'experiments' / identity
    (root / 'inputs').mkdir(parents=True)
    for record in records:
        shutil.copyfile(record.path, root / 'inputs' / record.path.name)
    write(root / 'selection.json', selection)
    write(root / 'experiment.json', {
        'id': identity, 'kind': 'preprocess', 'title': title,
        'question': text_field(body, 'question'), 'dataset_id': dataset_id,
        'dataset_name': dataset['name'], 'trajectory_source': dataset.get('trajectory_source'),
        'trajectory_count': len(kept), 'trajectory_ids': [r.trajectory_id for r in kept],
        'input_trajectory_count': len(records), 'selection_policy': POLICY, 'selection_mode': mode,
        'input_hash': content_hash(records), 'config': config, 'algorithm': VERSION,
        'created_at': now(), 'model': '', 'base_url': '', 'prompt_hash': '',
        'token_estimator': 'ceil(compact_event_json_characters / 4)',
    })
    write(root / 'lifecycle.json', {'status': 'draft', 'updated_at': now()})
    return workspace.experiment(identity, detail=True)


def check_input(root):
    meta = read(root / 'experiment.json')
    if meta.get('kind') != 'preprocess' or meta.get('algorithm') not in (VERSION, LEGACY_VERSION):
        raise ValueError('预处理实验类型或规则版本无效')
    config = validate_rules(meta['config'])
    if meta['algorithm'] == LEGACY_VERSION and config['simplify_call_ids']:
        raise ValueError('精简调用标识需要创建新版预处理实验')
    records = load_trajectories(root / 'inputs')
    if not records or content_hash(records) != meta['input_hash']:
        raise ValueError('输入快照发生变化，请创建新实验')
    if meta.get('selection_policy'):
        records, selection = select_records(records, meta.get('selection_mode', 'all'), meta['selection_policy'])
        if (selection != read(root / 'selection.json') or not records
                or selection['retained_ids'] != meta['trajectory_ids']
                or len(records) != meta['trajectory_count']):
            raise ValueError('轨迹筛选快照发生变化，请创建新实验')
    return meta, records


def run(root, progress=None):
    progress = progress or (lambda *args, **kwargs: None)
    meta, records = check_input(root)
    output = root / 'output'
    state = {'status': 'running', 'next_stage': '精简轨迹字段', 'completed_trajectories': 0}
    write(output / 'execution_state.json', state)
    rows = []
    for record in records:
        progress('trajectory_start', stage='preprocess', trajectory_id=record.trajectory_id,
                 message=f'预处理第 {len(rows) + 1}/{len(records)} 条轨迹：{record.trajectory_id}')
        # Pure local projection is cheap and deterministic; resume rebuilds from frozen inputs.
        value, report = compact_trajectory(record.data, meta['config'])
        mapping = report.pop('call_id_mapping')
        write(output / 'trajectories' / record.path.name, value)
        if meta['config'].get('simplify_call_ids'):
            write(output / 'call-id-maps' / record.path.name,
                  {'schema': 'call-id-map/v1', 'trajectory_id': record.trajectory_id, 'calls': mapping})
        write(output / 'reports' / record.path.name, report)
        rows.append(report_statistics(report))
        state.update(completed_trajectories=len(rows), updated_at=now())
        write(output / 'execution_state.json', state)
        progress('trajectory_done', message=f'已保存第 {len(rows)}/{len(records)} 条轨迹，'
                 f'删除 {report["removed_fields"]} 个字段，替换 {report["replaced_fields"]} 个字段')
    before = sum(r['before']['tokens'] for r in rows)
    after = sum(r['after']['tokens'] for r in rows)
    characters_before = sum(r['before']['characters'] for r in rows)
    characters_after = sum(r['after']['characters'] for r in rows)
    stats = {'trajectory_count': len(rows), 'events': sum(r['events'] for r in rows),
             'input_trajectory_count': meta.get('input_trajectory_count', len(records)),
             'excluded_trajectory_count': meta.get('input_trajectory_count', len(records)) - len(records),
             'changed_events': sum(r['changed_events'] for r in rows),
             'removed_fields': sum(r['removed_fields'] for r in rows),
             'replaced_fields': sum(r['replaced_fields'] for r in rows),
             'before_tokens': before, 'after_tokens': after, 'saved_tokens': before - after,
             'reduction_percent': round(100 * (characters_before - characters_after) / max(1, characters_before), 2),
             'output_hash': content_hash(load_trajectories(output / 'trajectories'))}
    write(output / 'statistics.json', stats)
    state.update(status='completed', next_stage='预处理完成')
    write(output / 'execution_state.json', state)


def list_trajectories(root):
    rows = []
    meta = read(root / 'experiment.json')
    for record in load_trajectories(root / 'inputs'):
        if meta.get('selection_policy') and record.trajectory_id not in meta['trajectory_ids']:
            continue
        report = read(root / 'output/reports' / record.path.name, {})
        rows.append({**trajectory_summary(record), 'report': report_statistics(report)})
    return rows


def compare(workspace, identity, trajectory_id, event_id=None):
    root, output = workspace.paths(identity)
    meta, records = check_input(root)
    record = next((r for r in records if r.trajectory_id == trajectory_id), None)
    if record is None:
        raise ValueError('找不到这条实验轨迹')
    saved = read(output / 'execution_state.json', {}).get('status') == 'completed'
    if saved:
        after = read(output / 'trajectories' / record.path.name)
        report = read(output / 'reports' / record.path.name)
        if after is None or report is None:
            raise ValueError('预处理结果文件缺失')
        mapping = []
        if meta['config'].get('simplify_call_ids'):
            artifact = read(output / 'call-id-maps' / record.path.name)
            if artifact is None:
                raise ValueError('调用编号映射文件缺失')
            mapping = artifact['calls']
    else:
        after, report = compact_trajectory(record.data, meta['config'])
        mapping = report['call_id_mapping']
    before = record.data
    events = [{'id': e['event_id'], 'source': e.get('source', ''),
               'tools': [c.get('tool_name', '') for c in e.get('tool_calls', [])]} for e in before['events']]
    changes = report['changes']
    event_id = event_id or (events[0]['id'] if events else '__all__')
    if event_id and event_id != '__all__':
        index = next((i for i, e in enumerate(before['events']) if e['event_id'] == event_id), None)
        if index is None:
            raise ValueError('找不到这个事件')
        before, after = before['events'][index], after['events'][index]
        changes = [c for c in changes if c['event_id'] == event_id]
        mapping = [c for c in mapping if c['event_id'] == event_id]
    return {'id': trajectory_id, 'title': record.data['query']['title'], 'events': events,
            'assessment': trajectory_summary(record),
            'before': before, 'after': after, 'changes': changes,
            'call_id_mapping': mapping, 'statistics': report_statistics(report),
            'saved': saved, 'config': meta['config']}


def source_records(workspace, body):
    """Resolve a verified completed preprocessing result for the next stage."""
    dataset_id = text_field(body, 'dataset_id', limit=100)
    source_id = text_field(body, 'preprocess_experiment_id', limit=100)
    if not source_id:
        raise ValueError('请选择已完成的预处理实验，再进行轨迹切分')
    source = workspace.experiment(source_id)
    if source['kind'] != 'preprocess' or source['status'] != 'completed':
        raise ValueError('请选择已完成的预处理实验')
    if source['dataset_id'] != dataset_id:
        raise ValueError('预处理结果与所选数据集不一致')
    _, output = workspace.paths(source_id)
    records = load_trajectories(output / 'trajectories')
    if not records or content_hash(records) != source['statistics']['output_hash']:
        raise ValueError('预处理结果发生变化，请重新运行预处理实验')
    return records, {'preprocess_experiment_id': source_id, 'preprocess_title': source['title'],
                     'preprocess_output_hash': source['statistics']['output_hash'],
                     'preprocess_config': source['config']}
