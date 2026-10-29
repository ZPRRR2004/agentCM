"""Reversible experiment deletion; snapshots and lineage remain intact."""
from .common import now, read, write


def deleted_experiments(workspace):
    rows = []
    for marker in (workspace.data / 'experiments').glob('*/deleted.json'):
        root, _ = workspace.paths(marker.parent.name, include_deleted=True)
        meta = read(root / 'experiment.json')
        rows.append({'id': root.name, 'title': meta['title'],
                     'kind': meta.get('kind', 'predicate'), 'dataset_name': meta['dataset_name'],
                     'deleted_at': read(marker)['deleted_at']})
    return sorted(rows, key=lambda row: row['deleted_at'], reverse=True)


def delete(workspace, identity):
    with workspace.lock:
        root, _ = workspace.paths(identity)
        process = workspace.processes.get(identity)
        if process is not None and process.poll() is None:
            raise ValueError('请先停止实验，再删除')
        write(root / 'deleted.json', {'id': identity, 'deleted_at': now()})
        return {'id': identity, 'deleted': True}


def restore(workspace, identity):
    with workspace.lock:
        root, _ = workspace.paths(identity, include_deleted=True)
        marker = root / 'deleted.json'
        if not marker.is_file():
            raise ValueError('这个实验已在实验管理中')
        marker.unlink()
        return {'id': identity, 'deleted': False}
