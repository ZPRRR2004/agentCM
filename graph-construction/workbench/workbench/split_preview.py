"""Read-only window length analysis using the execution splitter's boundaries."""
from collections import Counter
import math
from statistics import median

from .common import text_field
from .datasets import content_hash
from .preprocessing import source_records
from .splitting import FIELDS, select_trajectories
from src.split.splitter import window_ranges
from src.split.token_counter import range_token_counter

BOUNDARY_FIELDS = ('max_window_events', 'overlap_events')


def distribution(values):
    values = sorted(values)
    def percentile(fraction):
        return values[max(0, math.ceil(len(values) * fraction) - 1)] if values else 0
    return {'min': min(values, default=0), 'max': max(values, default=0),
            'median': median(values) if values else 0, 'p90': percentile(.9),
            'mean': round(sum(values) / max(1, len(values)), 2)}


def histogram(core, context):
    maximum = max(context, default=0)
    bounds = [0, 1000]
    while bounds[-1] <= maximum:
        bounds.append(bounds[-1] * 2)
    return [{'min': low, 'max_exclusive': high,
             'core_count': sum(low <= n < high for n in core),
             'context_count': sum(low <= n < high for n in context)}
            for low, high in zip(bounds, bounds[1:])]


def preview(workspace, body):
    config = body.get('config')
    if not isinstance(config, dict) or set(config) != set(BOUNDARY_FIELDS):
        raise ValueError('预览需要每窗口事件数和重叠事件数')
    for key in BOUNDARY_FIELDS:
        label, low, high = FIELDS[key]
        if type(config[key]) is not int or not low <= config[key] <= high:
            raise ValueError(f'{label}必须是 {low}–{high} 范围内的整数')
    if not body.get('trajectory_ids'):
        raise ValueError('请选择至少一条轨迹进行预览')
    dataset_id = text_field(body, 'dataset_id', limit=100)
    available, lineage = source_records(workspace, body)
    records = select_trajectories(available, body)
    windows = []
    for record in records:
        events = record.data['events']
        count = range_token_counter(events)
        for index, (overlap_start, start, end) in enumerate(window_ranges(len(events), config), 1):
            windows.append({'trajectory_id': record.trajectory_id, 'title': record.data['query']['title'],
                            'window_id': f'window_{index:04d}', 'core_events': end - start,
                            'overlap_events': start - overlap_start, 'core_tokens': count(start, end),
                            'context_tokens': count(overlap_start, end)})
    core = [w['core_tokens'] for w in windows]
    context = [w['context_tokens'] for w in windows]
    events = Counter(w['core_events'] for w in windows)
    return {**lineage, 'algorithm': 'event-count/v2', 'dataset_id': dataset_id, 'config': config,
            'input_hash': content_hash(records), 'trajectory_count': len(records),
            'window_count': len(windows), 'core_events': sum(w['core_events'] for w in windows),
            'overlap_events': sum(w['overlap_events'] for w in windows),
            'core_tokens': distribution(core), 'context_tokens': distribution(context),
            'token_histogram': histogram(core, context),
            'event_histogram': [{'events': size, 'windows': number} for size, number in sorted(events.items())],
            'longest_windows': sorted(windows, key=lambda w: -w['context_tokens'])[:5],
            'token_estimator': 'ceil(compact_json_characters / 4)'}
