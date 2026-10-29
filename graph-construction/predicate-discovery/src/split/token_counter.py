"""Deterministic character-based estimates for length statistics and summaries."""
import json
import math


def serialize_events(events):
    """Serialize events exactly as used by the splitting token estimate."""
    return json.dumps(events, ensure_ascii=False, separators=(',', ':'))


def count_text_tokens(text):
    """Estimate tokens at four Unicode characters per token."""
    return math.ceil(len(text) / 4)


def count_core_tokens(events):
    """Estimate the token count of a complete serialized event array."""
    return count_text_tokens(serialize_events(events))


def range_token_counter(events):
    """Exact equivalent of count_core_tokens for slices, without repeated serialization."""
    prefix = [0]
    for event in events:
        prefix.append(prefix[-1] + len(json.dumps(event, ensure_ascii=False, separators=(',', ':'))))

    def count(start, end):
        characters = prefix[end] - prefix[start] + (end - start - 1 if end > start else 0) + 2
        return math.ceil(characters / 4)
    return count
