"""Freeze and verify the typed nodes used by a predicate experiment."""
from .common import PromptManager, load_windows, read, write
from .datasets import content_hash
from src.trajectory_nodes import NODE_SCHEMA_VERSION, window_nodes
from src.discover_predicates.validator import PREDICATE_SCHEMA_VERSION


def snapshot(root, records):
    graphs = [(record, window_nodes(record.data)) for record in records]
    counts = dict.fromkeys(('action', 'observation', 'reasoning'), 0)
    seen = set()
    for record, graph in graphs:
        write(root / 'nodes' / (record.run_name + '.json'), graph)
        for section in ('core', 'overlap'):
            for node in graph[section]['nodes']:
                if node['id'] not in seen:
                    counts[node['type']] += 1
                    seen.add(node['id'])
    return {'predicate_schema_version': PREDICATE_SCHEMA_VERSION,
            'node_schema_version': NODE_SCHEMA_VERSION, 'node_counts': counts}


def verify(root, meta):
    if (meta.get('predicate_schema_version') != PREDICATE_SCHEMA_VERSION or
            meta.get('node_schema_version') != NODE_SCHEMA_VERSION):
        raise ValueError('这次实验使用旧版节点定义。请从已完成的切分结果新建谓词实验。')
    records = load_windows(root / 'inputs')
    if content_hash(records) != meta['input_hash']:
        raise ValueError('实验输入发生变化，请从切分结果重新创建实验')
    expected = {record.run_name + '.json' for record in records}
    if {path.name for path in (root / 'nodes').glob('*.json')} != expected:
        raise ValueError('节点快照文件集合发生变化，请重新创建实验')
    for record in records:
        if read(root / 'nodes' / (record.run_name + '.json')) != window_nodes(record.data):
            raise ValueError('节点快照与输入不一致，请重新创建实验')
    manager = PromptManager(root / 'prompts', root / 'output')
    manager.validate(manager.load_from_disk())
    return records
