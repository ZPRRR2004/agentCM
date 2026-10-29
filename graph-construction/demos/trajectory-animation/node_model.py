"""Typed demo nodes from ATIF messages, calls and recorded feedback blocks."""
import copy
from urllib.parse import quote

NODE_TYPES = {'reasoning', 'action', 'observation'}


def build_nodes(trace, steps):
    trajectory = quote(str(trace['session_id']), safe='')
    nodes, edges, refs = [], [], {}
    for step in steps:
        sid = step['step_id']
        prefix = f'{trajectory}/step-{sid}'

        def add(kind, index, content, field, **extra):
            suffix = 'reasoning' if kind == 'reasoning' else f'{kind}-{index + 1}'
            node = {'id': f'{prefix}/{suffix}', 'type': kind, 'stepId': sid,
                    'label': f'{kind[0]}{sid}' + (f'.{index+1}' if kind != 'reasoning' else ''),
                    'content': copy.deepcopy(content), 'index': index,
                    'source': {'stepId': sid, 'field': field}, **extra}
            nodes.append(node)
            refs[(sid, kind, index)] = node['id']
            return node['id']

        if step.get('message', '').strip():
            add('reasoning', 0, step['message'], 'message')
        calls = step.get('tool_calls', [])
        call_map = {}
        for i, call in enumerate(calls):
            aid = add('action', i, {'tool_name': call['function_name'],
                      'arguments': call.get('arguments', {})}, f'tool_calls[{i}]',
                      toolCallId=call['tool_call_id'])
            if call['tool_call_id'] in call_map:
                raise ValueError('Duplicate tool call ID')
            call_map[call['tool_call_id']] = aid
        for i, result in enumerate(step.get('observation', {}).get('results', [])):
            oid = add('observation', i, result, f'observation.results[{i}]')
            call_ref = result.get('source_call_id', result.get('tool_call_id'))
            if call_ref is not None and call_ref not in call_map:
                raise ValueError('Unknown feedback call reference')
            action_ids = [call_map[call_ref]] if call_ref is not None else list(call_map.values())
            kind = 'returns' if len(action_ids) == 1 else 'batch_feedback'
            for aid in action_ids:
                edges.append({'id': f'{aid}>{oid}', 'source': aid, 'target': oid,
                              'kind': kind, 'actionIds': action_ids, 'observationId': oid,
                              'evidence': '返回记录包含调用编号。' if call_ref is not None else
                              '本轮只有一次调用和一块反馈。' if len(action_ids) == 1 else
                              '原轨迹将本轮调用的反馈保存为一个整体。各调用指向同一块原始返回。'})
    return nodes, edges, refs


def typed_dependencies(story, nodes, refs):
    by_id = {n['id']: n for n in nodes}
    definitions = {p['name']: p for p in story['predicateDefinitions']}
    if len(definitions) != len(story['predicateDefinitions']):
        raise ValueError('Duplicate predicate name')
    for definition in definitions.values():
        if len(definition['parameters']) != 2 or any(p['type'] not in NODE_TYPES for p in definition['parameters']):
            raise ValueError('This animation uses two explicitly typed node roles per semantic edge')

    def resolve(ref):
        try:
            return refs[(ref['step'], ref['type'], ref.get('index', 0))]
        except KeyError as exc:
            raise ValueError(f'Unknown node reference: {ref}') from exc

    result, seen = [], set()
    for annotation in story['dependencies']:
        name = annotation['predicate']
        if name not in definitions:
            raise ValueError(f'Unknown predicate: {name}')
        definition = definitions[name]
        arguments = [resolve(r) for r in annotation['arguments']]
        if len(arguments) != len(definition['parameters']):
            raise ValueError('Predicate argument count mismatch')
        for arg, parameter in zip(arguments, definition['parameters']):
            if by_id[arg]['type'] != parameter['type']:
                raise ValueError(f'Predicate node type mismatch: {name}')
        source, target = resolve(annotation['source']), resolve(annotation['target'])
        if set(arguments) != {source, target} or source == target:
            raise ValueError('Dependency endpoints must be its two distinct argument nodes')
        a, b = by_id[source], by_id[target]
        rank = {'reasoning': 0, 'action': 1, 'observation': 2}
        if (a['stepId'], rank[a['type']]) >= (b['stepId'], rank[b['type']]):
            raise ValueError('Dependency evidence must be available before its target')
        key = (name, *arguments)
        if key in seen or not annotation.get('evidence'):
            raise ValueError('Dependency needs unique arguments and explicit evidence')
        seen.add(key)
        result.append({**annotation, 'source': source, 'target': target,
                       'arguments': arguments, 'kind': 'semantic',
                       'id': f'semantic-{len(result)+1}', 'basis': 'storyboard_annotation'})
    return result
