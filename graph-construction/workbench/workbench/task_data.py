"""Read original Harbor task packages without executing their scripts."""
import hashlib
import tomllib
from pathlib import Path


def task_list(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError('请先下载官方数据集')
    result = []
    for task in sorted(p for p in directory.iterdir() if p.is_dir()):
        instruction = task / 'instruction.md'
        config = task / 'task.toml'
        if not instruction.is_file() or not config.is_file():
            raise ValueError(f'任务文件不完整：{task.name}')
        metadata = tomllib.loads(config.read_text(encoding='utf-8')).get('metadata', {})
        result.append({'id': task.name, 'title': task.name,
                       'category': metadata.get('category', ''),
                       'difficulty': metadata.get('difficulty', ''),
                       'tags': metadata.get('tags', [])})
    return result


def task_detail(directory, identity):
    task = next((t for t in task_list(directory) if t['id'] == identity), None)
    if task is None:
        raise ValueError('找不到这个数据集任务')
    path = Path(directory) / identity
    instruction = (path / 'instruction.md').read_bytes()
    return {**task, 'instruction': instruction.decode('utf-8'),
            'config_toml': (path / 'task.toml').read_text(encoding='utf-8'),
            'instruction_sha256': hashlib.sha256(instruction).hexdigest(),
            'files': [{'path': p.relative_to(path).as_posix(), 'bytes': p.stat().st_size}
                      for p in sorted(path.rglob('*')) if p.is_file()]}
