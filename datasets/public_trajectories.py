"""Download a pinned full Terminal-Bench 2.1 run and convert its OMP events locally."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request

REPOSITORY = 'Lottolabs/terminal-bench-2.1-qwen3.8-27b-traces'
REVISION = 'dbf15f8e97ec7510c55f97fd66748888b2a27ad5'
ROOT = Path(__file__).resolve().parent
DESTINATION = ROOT / 'terminal-bench-2.1/trajectories/qwen3.8-27b-xhigh'
RUNS = ('xhigh', 'xhigh-rerun-prove', 'xhigh-rerun-regex')


def fetch(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'AgentCM dataset import'}), timeout=90) as response:
                return response.read(), response.headers
        except OSError:
            if attempt == 3:
                raise
            time.sleep(attempt + 1)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def source_tree():
    url = f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}?recursive=true&expand=false'
    entries = []
    while url:
        raw, headers = fetch(url)
        entries.extend(json.loads(raw))
        link = re.search(r'<([^>]+)>; rel="next"', headers.get('Link', ''))
        url = link.group(1) if link else None
    return [item for item in entries if item['type'] == 'file' and (
        item['path'] in ('README.md', 'summary.json', 'writeup.md') or
        item['path'].split('/')[0] in RUNS)]


def verify_bytes(data, item):
    if len(data) != item['size']:
        raise ValueError(f'Size mismatch: {item["path"]}')
    if item.get('lfs'):
        digest = hashlib.sha256(data).hexdigest()
        expected = item['lfs']['oid']
    else:
        digest = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
        expected = item['oid']
    if digest != expected:
        raise ValueError(f'Content mismatch: {item["path"]}')


def download(item):
    name = item['path']
    path = DESTINATION / 'source' / name
    if path.is_file():
        data = path.read_bytes()
        verify_bytes(data, item)
    else:
        url = f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{urllib.parse.quote(name)}'
        data, _ = fetch(url)
        verify_bytes(data, item)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + '.download')
        temporary.write_bytes(data)
        temporary.replace(path)
    return {'path': name, 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'upstream_blob': item['oid'], 'lfs': item.get('lfs')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download-only', action='store_true')
    parser.add_argument('--normalize-only', action='store_true')
    args = parser.parse_args()
    if not args.normalize_only:
        tree = source_tree()
        print(f'Downloading {len(tree)} files ({sum(i["size"] for i in tree) / 1024**2:.1f} MiB) at {REVISION}', flush=True)
        records = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            jobs = [pool.submit(download, item) for item in tree]
            for future in as_completed(jobs):
                records.append(future.result())
                if len(records) % 50 == 0 or len(records) == len(tree):
                    print(f'Verified {len(records)}/{len(tree)} files', flush=True)
        save(DESTINATION / 'source-manifest.json', {
            'repository': 'https://huggingface.co/datasets/' + REPOSITORY, 'revision': REVISION,
            'runs': list(RUNS), 'files': sorted(records, key=lambda r: r['path'])})
    if not args.download_only:
        from adapters.omp import convert_dataset
        print(json.dumps(convert_dataset(DESTINATION, ROOT / 'terminal-bench-2.1/source/tasks'), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
