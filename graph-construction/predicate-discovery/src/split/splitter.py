"""Deterministically divide an event sequence into cores and overlaps."""

from .token_counter import count_core_tokens


def window_ranges(event_count, config):
    """Shared boundaries for execution and read-only preview, independent of text size."""
    max_events = config['max_window_events']
    overlap_count = config['overlap_events']
    if type(max_events) is not int or max_events < 1:
        raise ValueError('max_window_events must be a positive integer')
    if type(overlap_count) is not int or overlap_count < 0:
        raise ValueError('overlap_events must be a non-negative integer')
    for start in range(0, event_count, max_events):
        yield max(0, start - overlap_count), start, min(event_count, start + max_events)


def split_trajectory(events, config, token_counter=count_core_tokens):
    windows = []
    for overlap_start, core_start, core_end in window_ranges(len(events), config):
        core = events[core_start:core_end]
        core_tokens = token_counter(core)
        windows.append({
            'window_id': f'window_{len(windows) + 1:04d}',
            'previous_events': events[:overlap_start],
            'overlap_events': events[overlap_start:core_start],
            'core_events': core,
            'future_events': events[core_end:],
            'metadata': {
                'overlap_start_index': overlap_start,
                'core_start_index': core_start,
                'core_end_index': core_end,
                'core_event_count': len(core),
                'core_tokens': core_tokens,
                'context_tokens': token_counter(events[overlap_start:core_end]),
            },
        })

    return windows
