"""Typed identities and exact content, without any paid model calls."""
import copy
import json
import unittest
from pathlib import Path

from src.trajectory_nodes import build_nodes, window_nodes
from src.discover_predicates.validator import validate_predicate, ValidationError
from src.discover_predicates.window_loader import serialize_context_window
from test_predicate_discovery import window, predicate, after


def mixed_event():
    return {'event_id': 'event-1', 'source': 'agent', 'thought': '  inspect\nthen decide  ',
            'tool_calls': [
                {'tool_call_id': 'long-call-1', 'tool_name': 'read',
                 'arguments': {'path': '/file'},
                 'observation': {'raw': '  file content\n\n<script>data</script>', 'is_error': False}},
                {'tool_call_id': 'long-call-2', 'tool_name': 'shell',
                 'arguments': {'command': 'pwd'}}]}


class TrajectoryNodeTests(unittest.TestCase):
    def test_mixed_event_splits_reasoning_calls_results_and_preserves_content(self):
        event = mixed_event()
        before = copy.deepcopy(event)
        graph = build_nodes('trace', [event])
        self.assertEqual([n['type'] for n in graph['nodes']],
                         ['reasoning', 'action', 'action', 'observation'])
        self.assertEqual(graph['nodes'][0]['content'], event['thought'])
        self.assertEqual(graph['nodes'][1]['content']['arguments'], event['tool_calls'][0]['arguments'])
        self.assertEqual(graph['nodes'][3]['content'], event['tool_calls'][0]['observation'])
        self.assertEqual(graph['structural_edges'], [{
            'type': 'returns', 'source': 'trace/event-1/action-1',
            'target': 'trace/event-1/observation-1', 'basis': 'tool_call_result_pair'}])
        self.assertEqual(graph['event_groups'][0]['node_ids'], [n['id'] for n in graph['nodes']])
        graph['nodes'][1]['content']['arguments']['path'] = 'mutated'
        self.assertEqual(event, before)

    def test_reasoning_only_events_and_explicit_empty_result(self):
        event = mixed_event()
        event['tool_calls'][1]['observation'] = {'raw': ''}
        only_text = {'event_id': 'event-2', 'source': 'agent', 'thought': 'Conclusion', 'tool_calls': []}
        graph = build_nodes('trace', [event, only_text])
        self.assertEqual(len(graph['structural_edges']), 2)
        self.assertEqual(graph['nodes'][-1]['type'], 'reasoning')
        self.assertEqual(graph['nodes'][-2]['content'], {'raw': ''})
        event['thought'] = '  \n'
        event['tool_calls'][0]['observation'] = None
        graph = build_nodes('trace', [event])
        self.assertEqual([n['type'] for n in graph['nodes']], ['action', 'action', 'observation'])

    def test_context_messages_stay_context(self):
        message = {'event_id': 'user-1', 'source': 'user', 'thought': 'User instruction'}
        graph = build_nodes('trace', [message])
        self.assertEqual(graph['nodes'], [])
        self.assertEqual(graph['context_messages'], [message])

    def test_identity_stable_across_overlap_and_call_id_compaction(self):
        first, second = window(1), window(2)
        first['core']['events'] = [mixed_event()]
        second['overlap'] = copy.deepcopy(first['core'])
        a, b = window_nodes(first)['core'], window_nodes(second)['overlap']
        self.assertEqual(a, b)
        first['core']['events'][0]['tool_calls'][0]['tool_call_id'] = 'c1'
        compact = window_nodes(first)['core']
        self.assertEqual([n['id'] for n in a['nodes']], [n['id'] for n in compact['nodes']])
        self.assertEqual(a['structural_edges'], compact['structural_edges'])
        self.assertNotEqual(build_nodes('a/b', [mixed_event()])['nodes'][0]['id'],
                            build_nodes('a%2Fb', [mixed_event()])['nodes'][0]['id'])

    def test_duplicates_and_incomplete_actions_fail_before_model_call(self):
        event = mixed_event()
        with self.assertRaises(ValueError):
            build_nodes('trace', [event, event])
        w = window(1); w['overlap'] = copy.deepcopy(w['core'])
        with self.assertRaises(ValueError):
            window_nodes(w)
        del event['tool_calls'][0]['arguments']
        with self.assertRaises(ValueError):
            build_nodes('trace', [event])

    def test_serialized_input_contains_nodes_and_exact_returns(self):
        w = window(1); w['core']['events'] = [mixed_event()]
        text = serialize_context_window(w)
        graph = window_nodes(w)['core']
        self.assertEqual(after(text, '[CORE NODES]'), graph['nodes'])
        self.assertEqual(after(text, '[STRUCTURAL EDGES]'), graph['structural_edges'])
        self.assertNotIn('[CORE EVENTS]', text)
        self.assertEqual(after(text, '[EVENT GROUPS]'), graph['event_groups'])

    def test_only_node_parameter_types_are_accepted(self):
        for kind in ('action', 'observation', 'reasoning', 'action[]', 'observation[]', 'reasoning[]'):
            validate_predicate(predicate('HOLDS', (kind,)))
        for kind in ('information', 'artifact', 'goal', 'scope', 'rule', 'event',
                     'information[]', 'action|observation', 'observation[][]'):
            with self.subTest(kind=kind), self.assertRaises(ValidationError):
                validate_predicate(predicate('HOLDS', (kind,)))

    def test_documented_examples_follow_current_protocol(self):
        path = Path(__file__).resolve().parents[1] / 'examples/predicate_definitions.json'
        for definition in json.loads(path.read_text()):
            validate_predicate(definition)


if __name__ == '__main__':
    unittest.main()
