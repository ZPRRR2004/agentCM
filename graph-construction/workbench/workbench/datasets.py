"""Flat, version-qualified datasets of complete normalized trajectories."""
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .common import ROOT, read
from .task_data import task_list, task_detail
from .trajectory_selection import trajectory_summary
from src.split.main import validate_trajectory

CATALOG = ROOT.parents[1] / 'datasets/catalog.json'


@dataclass
class Trajectory:
    path: Path
    trajectory_id: str
    data: dict
    sha256: str


def load_trajectories(directory):
    records = []
    for path in sorted(Path(directory).glob('*.json')):
        raw = path.read_bytes()
        data = json.loads(raw)
        validate_trajectory(data, path.name)
        records.append(Trajectory(path, path.stem, data, hashlib.sha256(raw).hexdigest()))
    return records


class DatasetCatalog:
    def __init__(self, path=CATALOG):
        self.path = Path(path).resolve()

    def definitions(self):
        value = read(self.path, {'schema': 'agentcm-datasets/v2', 'datasets': []})
        if value.get('schema') != 'agentcm-datasets/v2' or not isinstance(value.get('datasets'), list):
            raise ValueError('数据集目录格式应为 agentcm-datasets/v2')
        seen = set()
        for item in value['datasets']:
            identity = item.get('id')
            if (not isinstance(identity, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', identity)
                    or identity in seen or not item.get('name')):
                raise ValueError('数据集需要唯一 id 和名称')
            seen.add(identity)
        return value['datasets']

    def directory(self, relative):
        path = (self.path.parent / relative).resolve()
        if not path.is_relative_to(self.path.parent) or path == self.path.parent:
            raise ValueError('输入目录必须位于数据集目录内')
        return path

    def resolve(self, dataset_id):
        dataset = next((d for d in self.definitions() if d['id'] == dataset_id), None)
        if dataset is None:
            raise ValueError(f'找不到数据集：{dataset_id}')
        field = 'tasks_path' if dataset.get('format') == 'harbor-tasks' else 'normalized_path'
        return dataset, self.directory(dataset[field])

    def records(self, dataset_id):
        dataset, directory = self.resolve(dataset_id)
        if dataset.get('format') == 'harbor-tasks':
            directory = self.directory(dataset['normalized_path']) if dataset.get('normalized_path') else None
            return load_trajectories(directory) if directory else []
        return load_trajectories(directory)

    def tasks(self, dataset_id):
        dataset, directory = self.resolve(dataset_id)
        if dataset.get('format') != 'harbor-tasks':
            return []
        tasks = task_list(directory)
        if dataset.get('expected_tasks') and len(tasks) != dataset['expected_tasks']:
            raise ValueError('官方任务数与数据集配置不一致，请校验下载')
        return tasks

    def task(self, dataset_id, identity):
        dataset, directory = self.resolve(dataset_id)
        if dataset.get('format') != 'harbor-tasks':
            raise ValueError('这个数据集包含轨迹，请从轨迹入口浏览')
        return task_detail(directory, identity)

    def describe(self):
        result = []
        for dataset in self.definitions():
            if dataset.get('format') == 'harbor-tasks':
                tasks = self.tasks(dataset['id'])
                records = self.records(dataset['id'])
                source = dataset.get('source', {})
                manifest = read(self.directory(dataset['manifest_path']), {})
                if manifest.get('commit') != source.get('commit'):
                    raise ValueError('官方数据集版本与下载清单不一致')
                result.append({'id': dataset['id'], 'name': dataset['name'], 'format': 'harbor-tasks',
                               'description': dataset.get('description', ''), 'tasks': tasks,
                               'task_count': len(tasks), 'raw_tasks': len(tasks),
                               'trajectories': [trajectory_summary(r) for r in records],
                               'events': sum(len(r.data['events']) for r in records), 'source': source,
                               'trajectory_source': dataset.get('trajectory_source'),
                               'file_count': manifest.get('file_count', 0),
                               'content_hash': manifest.get('archive_sha256', '')})
                continue
            records = self.records(dataset['id'])
            raw = self.directory(dataset['raw_path']) if dataset.get('raw_path') else None
            raw_count = sum(p.is_dir() for p in raw.iterdir()) if raw and raw.is_dir() else 0
            result.append({'id': dataset['id'], 'name': dataset['name'],
                           'format': 'normalized-trajectories', 'task_count': len(records),
                           'description': dataset.get('description', ''), 'raw_tasks': raw_count,
                           'trajectories': [trajectory_summary(r) for r in records],
                           'events': sum(len(r.data['events']) for r in records),
                           'content_hash': content_hash(records)})
        return result


def content_hash(records):
    content = [(r.trajectory_id, getattr(r, 'window_id', ''), r.sha256) for r in records]
    return hashlib.sha256(json.dumps(content, ensure_ascii=False).encode()).hexdigest()
