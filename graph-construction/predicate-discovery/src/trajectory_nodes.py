"""Typed nodes preserving agent text, arguments and results, with recorded pairs."""
import copy
from urllib.parse import quote


NODE_SCHEMA_VERSION = 'trajectory-nodes/v1'
NODE_TYPES = frozenset({'action', 'observation', 'reasoning'})


def _identity(trajectory, event, suffix):
    return '/'.join((quote(trajectory, safe=''), quote(event, safe=''), suffix))


def build_nodes(trajectory_id, events):
    """One reasoning per nonempty agent text, one action/result per tool call.

    Call position is stable across call-ID compaction and overlapping windows.
    Event groups retain provenance; array order does not assert a dependency.
    """
    if not isinstance(trajectory_id, str) or not trajectory_id:
        raise ValueError('节点需要非空 trajectory_id')
    nodes, edges, groups, context = [], [], [], []
    seen = set()
    for event in events:
        event_id = event.get('event_id')
        if not isinstance(event_id, str) or not event_id or event_id in seen:
            raise ValueError('事件编号必须非空且不重复')
        seen.add(event_id)
        if event.get('source') != 'agent':
            context.append(copy.deepcopy(event))
            continue
        group = {'event_id': event_id, 'node_ids': []}
        groups.append(group)

        def add(kind, suffix, content, field, call=None):
            identity = _identity(trajectory_id, event_id, suffix)
            source = {'event_id': event_id, 'field': field}
            if call is not None:
                source['tool_call_id'] = call.get('tool_call_id')
            nodes.append({'id': identity, 'type': kind,
                          'content': copy.deepcopy(content), 'source': source})
            group['node_ids'].append(identity)
            return identity

        thought = event.get('thought', '')
        if thought is not None and not isinstance(thought, str):
            raise ValueError('reasoning 来源 thought 必须是文本')
        if thought and thought.strip():
            add('reasoning', 'reasoning', thought, 'thought')
        calls = event.get('tool_calls', [])
        if not isinstance(calls, list):
            raise ValueError('tool_calls 必须是数组')
        # All calls in an event are shown before their results: no intra-event
        # serialization of parallel calls is invented.
        action_ids = []
        for index, call in enumerate(calls):
            if not isinstance(call, dict) or not isinstance(call.get('tool_name'), str):
                raise ValueError('action 需要有效工具名称')
            if 'arguments' not in call:
                raise ValueError('action 需要原始工具参数')
            action_ids.append(add('action', f'action-{index + 1}',
                                  {'tool_name': call['tool_name'], 'arguments': call['arguments']},
                                  f'tool_calls[{index}]', call))
        for index, call in enumerate(calls):
            # An absent result is pending; an explicitly empty result is real.
            if 'observation' not in call or call['observation'] is None:
                continue
            observation = add('observation', f'observation-{index + 1}',
                              call['observation'], f'tool_calls[{index}].observation', call)
            edges.append({'type': 'returns', 'source': action_ids[index],
                          'target': observation, 'basis': 'tool_call_result_pair'})
    return {'schema': NODE_SCHEMA_VERSION, 'trajectory_id': trajectory_id,
            'nodes': nodes, 'structural_edges': edges, 'event_groups': groups,
            'context_messages': context}


def window_nodes(window):
    """Derive the same node identities in Core, Overlap and full trajectories."""
    if ({event['event_id'] for event in window['overlap']['events']} &
            {event['event_id'] for event in window['core']['events']}):
        raise ValueError('同一窗口的 Core 和 Overlap 不能包含重复事件')
    overlap = build_nodes(window['trajectory_id'], window['overlap']['events'])
    core = build_nodes(window['trajectory_id'], window['core']['events'])
    return {'schema': NODE_SCHEMA_VERSION, 'trajectory_id': window['trajectory_id'],
            'window_id': window['window_id'], 'overlap': overlap, 'core': core}


def node_counts(graph):
    return {kind: sum(n['type'] == kind for n in graph['nodes'])
            for kind in sorted(NODE_TYPES)}
