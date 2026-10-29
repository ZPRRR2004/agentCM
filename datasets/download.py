"""Download the pinned official task dataset and verify every Git blob."""
import argparse
import hashlib
import json
import re
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def request(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={
        'Accept': 'application/vnd.github+json', 'User-Agent': 'AgentCM-dataset-import'}), timeout=120)


def contained(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or path == ROOT:
        raise ValueError('Dataset paths must stay inside datasets/')
    return path


def validate(source, entries, expected_tasks):
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    expected = {p['path'] for p in entries}
    if actual != expected:
        raise ValueError(f'File inventory mismatch: missing {len(expected-actual)}, extra {len(actual-expected)}')
    for entry in entries:
        data = (source / entry['path']).read_bytes()
        digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if digest != entry['git_blob_sha1']:
            raise ValueError('Upstream byte mismatch: ' + entry['path'])
    tasks = sorted(p for p in (source / 'tasks').iterdir() if p.is_dir())
    if len(tasks) != expected_tasks:
        raise ValueError(f'Expected {expected_tasks} tasks, found {len(tasks)}')
    for task in tasks:
        for name in ('instruction.md', 'task.toml', 'environment', 'solution', 'tests'):
            if not (task / name).exists():
                raise ValueError(f'Incomplete task: {task.name}/{name}')
    return tasks


def download(dataset, verify_only=False):
    source = contained(dataset['source_path'])
    manifest_path = contained(dataset['manifest_path'])
    if verify_only:
        manifest = json.loads(manifest_path.read_text())
        if manifest['commit'] != dataset['source']['commit']:
            raise ValueError('Manifest commit differs from catalog')
        tasks = validate(source, manifest['files'], dataset['expected_tasks'])
        print(f'PASS: {len(tasks)} tasks, {len(manifest["files"])} files match official Git blobs.', flush=True)
        return
    if source.exists() or manifest_path.exists():
        raise ValueError('Source already exists; run --verify-only to verify it')
    repo = dataset['source']['repository'].removeprefix('https://github.com/')
    commit = dataset['source']['commit']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) or not re.fullmatch(r'[a-f0-9]{40}', commit):
        raise ValueError('Expected a pinned GitHub repository and 40-character commit')
    with request(f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1') as response:
        tree = json.load(response)
    if tree.get('truncated'):
        raise ValueError('GitHub returned a truncated inventory')
    if any(p['type'] == 'commit' for p in tree['tree']):
        raise ValueError('Submodule content requires an explicit source manifest')
    entries = [{'path': p['path'], 'size': p['size'], 'git_blob_sha1': p['sha'], 'mode': p['mode']}
               for p in tree['tree'] if p['type'] == 'blob']
    source.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='agentcm-dataset-') as temporary:
        temporary = Path(temporary)
        archive = temporary / 'official.tar.gz'
        archive_url = f'https://codeload.github.com/{repo}/tar.gz/{commit}'
        digest = hashlib.sha256()
        size = 0
        with request(archive_url) as response, archive.open('wb') as stream:
            while chunk := response.read(1024 * 1024):
                stream.write(chunk)
                digest.update(chunk)
                size += len(chunk)
                if size % (5 * 1024 * 1024) == 0:
                    print(f'Downloaded {size // (1024*1024)} MiB', flush=True)
        extracted = temporary / 'extracted'
        with tarfile.open(archive) as package:
            package.extractall(extracted, filter='data')
        roots = list(extracted.iterdir())
        if len(roots) != 1:
            raise ValueError('Unexpected archive layout')
        tasks = validate(roots[0], entries, dataset['expected_tasks'])
        manifest = {
            'dataset_id': dataset['id'], 'repository': dataset['source']['repository'],
            'commit': commit, 'archive_url': archive_url, 'archive_sha256': digest.hexdigest(),
            'task_count': len(tasks), 'task_ids': [p.name for p in tasks],
            'file_count': len(entries), 'total_bytes': sum(p['size'] for p in entries),
            'verification': 'Each local file matches the official Git tree blob SHA-1',
            'files': entries,
        }
        shutil.move(str(roots[0]), str(source))
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Imported {len(tasks)} official tasks / {len(entries)} original files into {source}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', default='terminal-bench-2.1')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    dataset = next(d for d in catalog['datasets'] if d['id'] == args.dataset)
    download(dataset, args.verify_only)


if __name__ == '__main__':
    main()
