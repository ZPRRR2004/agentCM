"""Upgrade the working prompt bundle while retaining previous editable content."""
import hashlib
import json
from .common import now, read, write


def upgrade_node_contract(data, defaults):
    path = data / 'prompts.json'
    current = read(path)
    if current is None:
        write(path, defaults)
    elif 'predicate-definition/v2' not in current.get('common/granularity_examples.txt', ''):
        # Experiment-local snapshots are immutable; only future experiments use v2.
        digest = hashlib.sha256(json.dumps(current, sort_keys=True).encode()).hexdigest()[:16]
        backup = data / 'prompt_migrations' / f'before-typed-nodes-v2-{digest}.json'
        if not backup.exists():
            write(backup, {'saved_at': now(), 'files': current})
        write(path, defaults)
