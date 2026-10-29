"""Deduplicate identical imports, annotate outcomes, and replay frozen policies."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import re

POLICY = 'execution-record/v5'
TOOL_REQUIRED_POLICY = 'execution-record/v4'
INFRASTRUCTURE_POLICY = 'execution-record/v3'
PREVIOUS_POLICY = 'execution-record/v2'
LEGACY_POLICY = 'successful-task/v1'


def selection_mode(value='all'):
    if value not in ('all', 'success_only'):
        raise ValueError('轨迹范围请选择全部结果或仅成功')
    return value


def trajectory_summary(record, include_reasoning=True):
    metadata = record.data.get('metadata')
    metadata = metadata if isinstance(metadata, dict) else {}
    result = metadata.get('result')
    result = result if isinstance(result, dict) else {}
    if result.get('scored') is True and type(result.get('pass')) is bool:
        outcome = 'success' if result['pass'] else 'failure'
    else:
        outcome = 'unscored' if result.get('scored') is False else 'unknown'
    tools = sum(len(e.get('tool_calls', [])) for e in record.data['events'])
    flags = []
    # A failed test or an absent score alone does not establish an infrastructure fault.
    if result.get('scored') is False and result.get('errorCode') == 'command_exec_failed':
        flags.append('infrastructure_failure')
    if tools == 0:
        flags.append('no_tool_calls')
    task = metadata.get('task_id') or result.get('question_id')
    summary = {'id': record.trajectory_id, 'title': record.data['query']['title'],
            'task_id': task if isinstance(task, str) else '', 'events': len(record.data['events']),
            'outcome': outcome, 'flags': flags, 'tool_calls': tools}
    if include_reasoning:
        summary['reasoning_events'] = sum(
            e.get('source') == 'agent' and isinstance(e.get('thought'), str)
            and bool(e['thought'].strip()) for e in record.data['events'])
    return summary


def record_hash(record):
    # Include attempt/source metadata: equal event text from different runs stays distinct.
    # Ignore only file naming, JSON key order and serialization whitespace.
    value = json.dumps(record.data, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def select_records(records, mode='all', policy=POLICY):
    if policy == LEGACY_POLICY:
        return select_successful(records)
    if policy not in (POLICY, TOOL_REQUIRED_POLICY, INFRASTRUCTURE_POLICY, PREVIOUS_POLICY):
        raise ValueError('轨迹筛选规则版本无效')
    mode = selection_mode(mode)
    hashes = {r.trajectory_id: record_hash(r) for r in records}
    representatives = {}
    for record in sorted(records, key=lambda r: r.trajectory_id):
        representatives.setdefault(hashes[record.trajectory_id], record.trajectory_id)
    rows, kept = [], []
    for record in records:
        # Historical reports are compared byte-for-structure with their frozen
        # selection.json. Only v5 adds the reasoning count and new decisions.
        row = trajectory_summary(record, include_reasoning=policy == POLICY)
        digest = hashes[record.trajectory_id]
        representative = representatives[digest]
        row.update(record_hash=digest, retained=True, reason_code='retained', reason='保留独立执行记录')
        if representative != record.trajectory_id:
            row.update(retained=False, reason_code='duplicate_record', reason='相同执行记录的重复导入',
                       duplicate_of=representative)
        elif policy in (POLICY, TOOL_REQUIRED_POLICY, INFRASTRUCTURE_POLICY) and 'infrastructure_failure' in row['flags']:
            row.update(retained=False, reason_code='infrastructure_failure',
                       reason='环境 / 运行器故障导致执行中断')
        elif policy == TOOL_REQUIRED_POLICY and 'no_tool_calls' in row['flags']:
            row.update(retained=False, reason_code='no_tool_calls',
                       reason='整条轨迹无工具调用，缺少工具交互建边依据')
        elif policy == POLICY and row['tool_calls'] == 0 and row['reasoning_events'] == 0:
            row.update(retained=False, reason_code='no_node_content',
                       reason='整条轨迹没有工具调用，也没有非空的 agent reasoning 内容')
        elif mode == 'success_only' and row['outcome'] != 'success':
            row.update(retained=False, reason_code='result_filter', reason='当前选择仅成功，该记录不符合结果条件')
        if row['retained']:
            if policy == POLICY and row['tool_calls'] == 0:
                row['reason'] = '保留含 reasoning 内容的轨迹（无工具调用）'
            kept.append(record)
        rows.append(row)
    retained_rows = [r for r in rows if r['retained']]
    return kept, {'policy': policy, 'mode': mode, 'input_count': len(records),
                  'retained_count': len(kept), 'excluded_count': len(records) - len(kept),
                  'excluded_by_reason': dict(Counter(r['reason_code'] for r in rows if not r['retained'])),
                  'outcome_counts': dict(Counter(r['outcome'] for r in retained_rows)),
                  'flag_counts': dict(Counter(flag for r in retained_rows for flag in r['flags'])),
                  'retained_ids': [r.trajectory_id for r in kept], 'rows': rows}


def attempt_time(metadata):
    value = metadata.get('started_at')
    if isinstance(value, str):
        try:
            date = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if date.tzinfo is not None:
                return int(date.astimezone(timezone.utc).timestamp() * 1_000_000_000)
        except ValueError:
            pass
    if metadata.get('adapter') == 'omp-completed-messages/v1':
        match = re.search(r'/agent/omp-[^/]+-(\d{19})/omp\.jsonl$', metadata.get('source_file', ''))
        if match:
            return int(match[1])
    return None


def select_successful(records):
    """Legacy v1: keep its exact report and replay semantics for existing experiments."""
    groups, rows = defaultdict(list), {}
    for record in records:
        metadata = record.data.get('metadata', {})
        result = metadata.get('result', {})
        task = metadata.get('task_id') or result.get('question_id')
        code, reason = 'retained', '保留成功执行'
        if result.get('scored') is False:
            code, reason = 'unscored', '执行未取得有效评分'
        elif result.get('pass') is False:
            code, reason = 'failed', '任务未通过测试'
        elif result.get('pass') is not True or result.get('scored') is not True:
            code, reason = 'unknown_result', '缺少明确的成功评分'
        elif not isinstance(task, str) or not task.strip():
            code, reason = 'missing_task_id', '缺少任务编号，无法按任务去重'
        elif not record.data['events']:
            code, reason = 'empty', '执行记录没有事件'
        row = {'id': record.trajectory_id, 'title': record.data['query']['title'],
               'task_id': task if isinstance(task, str) else '', 'reason_code': code,
               'reason': reason, 'retained': code == 'retained'}
        rows[record.trajectory_id] = row
        if row['retained']:
            groups[task].append(record)

    for task, attempts in groups.items():
        if len(attempts) == 1:
            continue
        times = {r.trajectory_id: attempt_time(r.data.get('metadata', {})) for r in attempts}
        indices = {r.trajectory_id: r.data.get('metadata', {}).get('attempt_index') for r in attempts}
        if all(t is not None for t in times.values()):
            order, basis = times, 'execution_time'
        elif all(type(i) is int and i >= 0 for i in indices.values()):
            order, basis = indices, 'attempt_index'
        else:
            raise ValueError(f'任务 {task} 有多条成功轨迹，请补充 started_at 或 attempt_index 以确定最后一次成功执行')
        winner = max(attempts, key=lambda r: (order[r.trajectory_id], r.trajectory_id))
        rows[winner.trajectory_id].update(reason='保留该任务最后一次成功执行', order_basis=basis)
        for record in attempts:
            if record != winner:
                rows[record.trajectory_id].update(retained=False, reason_code='duplicate_success',
                    reason='同一任务已有更晚或同时间的成功执行', kept_id=winner.trajectory_id, order_basis=basis)

    ordered = [rows[r.trajectory_id] for r in records]
    kept = [r for r in records if rows[r.trajectory_id]['retained']]
    counts = Counter(row['reason_code'] for row in ordered if not row['retained'])
    return kept, {'policy': LEGACY_POLICY, 'input_count': len(records), 'retained_count': len(kept),
                  'excluded_count': len(records) - len(kept), 'excluded_by_reason': dict(counts),
                  'retained_ids': [r.trajectory_id for r in kept], 'rows': ordered}
