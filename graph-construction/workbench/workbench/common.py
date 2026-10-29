import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = ROOT.parent / 'predicate-discovery'
PROMPTS = DISCOVERY / 'src/discover_predicates/prompts'
sys.path.insert(0, str(DISCOVERY))

from src.discover_predicates.prompt_loader import PROMPT_FILES, PromptManager
from src.discover_predicates.window_loader import load_windows, manifest


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path, default=None):
    path = Path(path)
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else default


def write(path, value, private=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600 if private else 0o644)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    os.replace(temporary, path)


def text_field(value, key, default='', limit=20000):
    result = value.get(key, default)
    if not isinstance(result, str) or len(result) > limit:
        raise ValueError(f'{key} 需要 {limit} 字以内的文字')
    return result.strip()
