"""Lossless text projection of completed OMP messages into AgentCM events.

Original JSONL stays alongside the projection. Message deltas and repeated
agent_end dumps are bookkeeping; complete message_end records supply events.
Tool results are joined by call ID, with execution-end fallback for interrupted
turns. No model is called and no windows are generated here.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def content_text(content):
    if isinstance(content, str):
        return content
    return '\n'.join(part.get('text', part.get('thinking', ''))
                     for part in content if isinstance(part, dict) and part.get('type') != 'toolCall')


def convert_trace(raw, task_id, instruction, source_file):
    events, calls, fallbacks = [], {}, {}
    counts = Counter()
    first_user = None
    flags = []
    for line, text in enumerate(raw.decode('utf-8').splitlines(), 1):
        if not text.strip():
            continue
        item = json.loads(text)
        kind = item.get('type')
        counts[kind] += 1
        if kind == 'trace_filter_summary':
            if item.get('overflowEvents'):
                flags.append({'kind': 'source_overflow', 'line': line, 'events': item['overflowEvents']})
            continue
        if kind == 'tool_execution_end':
            call = calls.get(item.get('toolCallId'))
            if call:
                fallbacks[call['tool_call_id']] = (line, item)
            continue
        if kind == 'message_end':
            message = item['message']
            role = message['role']
            content = message.get('content', [])
            if role == 'toolResult':
                call = calls.get(message.get('toolCallId'))
                if call is None:
                    raise ValueError(f'{source_file}:{line}: tool result has no matching call')
                if call['observation'].get('source_line'):
                    raise ValueError(f'{source_file}:{line}: repeated tool result')
                call['observation'] = {'raw': content_text(content), 'content': content,
                                       'is_error': message.get('isError', False), 'source_line': line}
                continue
            if role == 'user' and first_user is None and not events:
                first_user = content_text(content)
                continue
            event = {'event_id': f'event-{len(events)+1:04d}', 'source_line': line,
                     'source': 'agent' if role == 'assistant' else role,
                     'thought': content_text(content), 'tool_calls': []}
            for index, part in enumerate(content if isinstance(content, list) else []):
                if part.get('type') != 'toolCall':
                    continue
                original_id = part.get('id')
                if not isinstance(original_id, str) or not original_id:
                    raise ValueError(f'{source_file}:{line}: missing tool call ID')
                unique_id = f'{original_id}@{line}:{index}'
                call = {'tool_call_id': unique_id, 'source_call_id': original_id,
                        'tool_name': part['name'], 'arguments': part.get('arguments', {}),
                        'observation': {'raw': ''}}
                calls[original_id] = call
                event['tool_calls'].append(call)
            events.append(event)
        elif kind in ('notice', 'auto_compaction_start', 'auto_compaction_end', 'compaction', 'error'):
            events.append({'event_id': f'event-{len(events)+1:04d}', 'source': 'system',
                           'source_line': line, 'thought': json.dumps(item, ensure_ascii=False),
                           'tool_calls': [], 'context_event': kind})
        elif kind == 'raw_output':
            # This duplicates complete messages when OMP emits its final dump.
            try:
                duplicate = json.loads(item.get('text', '')).get('type') == 'agent_end'
            except (ValueError, AttributeError):
                duplicate = False
            if not duplicate:
                events.append({'event_id': f'event-{len(events)+1:04d}', 'source': 'system',
                               'source_line': line, 'thought': item.get('text', ''), 'tool_calls': [],
                               'context_event': kind})
    for event in events:
        for call in event['tool_calls']:
            if call['observation'].get('source_line'):
                continue
            fallback = fallbacks.get(call['tool_call_id'])
            if fallback:
                line, item = fallback
                content = item.get('result', {}).get('content', [])
                call['observation'] = {'raw': content_text(content), 'content': content,
                                       'is_error': item.get('isError', False), 'source_line': line,
                                       'source_type': 'tool_execution_end'}
            else:
                call['observation']['status'] = 'no_recorded_result'
    return {'query': {'title': task_id, 'text': instruction}, 'events': events,
            'metadata': {'adapter': 'omp-completed-messages/v1', 'task_id': task_id,
                         'source_file': source_file, 'source_sha256': digest(raw),
                         'initial_prompt': first_user, 'source_event_counts': dict(counts), 'flags': flags}}


def convert_dataset(destination, tasks_directory):
    destination, tasks_directory = Path(destination), Path(tasks_directory)
    source = destination / 'source'
    manifest = json.loads((destination / 'source-manifest.json').read_text(encoding='utf-8'))
    for entry in manifest['files']:
        if digest((source / entry['path']).read_bytes()) != entry['sha256']:
            raise ValueError('Source content changed: ' + entry['path'])
    expected = {p.name for p in tasks_directory.iterdir() if (p / 'instruction.md').is_file()}
    main_tasks = {p.name for p in (source / 'xhigh/traces').iterdir() if p.is_dir()}
    if main_tasks != expected:
        raise ValueError('Public full-run task IDs differ from the official dataset')
    normalized = destination / 'normalized'
    normalized.mkdir(exist_ok=True)
    rows, mismatches = [], []
    for path in sorted(source.glob('*/traces/*/agent/*/omp.jsonl')):
        relative = path.relative_to(source)
        run, task_id = relative.parts[0], relative.parts[2]
        task = source / run / 'traces' / task_id
        instruction = (task / 'instruction.txt').read_text(encoding='utf-8')
        official = (tasks_directory / task_id / 'instruction.md').read_text(encoding='utf-8')
        matched = instruction.strip() == official.strip()
        if not matched:
            mismatches.append(run + '/' + task_id)
        result = json.loads((task / 'result.json').read_text(encoding='utf-8'))
        data = convert_trace(path.read_bytes(), task_id, instruction, relative.as_posix())
        data['metadata'].update(run=run, model='qwen3.8-27b', reasoning_effort='xhigh',
                                repository=manifest['repository'], revision=manifest['revision'],
                                instruction_matches_official=matched, result=result)
        identity = run + '__' + task_id
        data['query']['title'] = task_id + (' · 基础设施重跑' if run != 'xhigh' else '')
        output = normalized / (identity + '.json')
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n',
                          encoding='utf-8', newline='\n')
        rows.append({'id': identity, 'task_id': task_id, 'run': run, 'events': len(data['events']),
                     'sha256': digest(output.read_bytes()), 'passed': result.get('pass'),
                     'scored': result.get('scored'), 'instruction_matches_official': matched,
                     'flags': data['metadata']['flags']})
    if len(rows) != 91 or len({r['task_id'] for r in rows}) != 89:
        raise ValueError(f'Expected all 91 attempts covering 89 tasks, found {len(rows)}')
    report = {'schema': 'agentcm-public-trajectories/v1', 'repository': manifest['repository'],
              'revision': manifest['revision'], 'task_count': 89, 'trajectory_count': len(rows),
              'event_count': sum(r['events'] for r in rows), 'instruction_mismatches': mismatches,
              'empty_trajectories': [r['id'] for r in rows if not r['events']],
              'trajectories': rows}
    (destination / 'normalization-manifest.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    return {k: v for k, v in report.items() if k != 'trajectories'}
