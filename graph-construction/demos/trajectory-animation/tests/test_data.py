"""Verify trace fidelity, shared feedback and typed storyboard bindings."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from build_data import build, DEFAULT_SOURCE
from node_model import build_nodes, typed_dependencies


class TraceFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = DEFAULT_SOURCE.read_bytes()
        cls.story_bytes = (BASE / 'storyboard.json').read_bytes()
        cls.trace = json.loads(cls.source)
        cls.data = build(DEFAULT_SOURCE, BASE / 'storyboard.json')

    def test_rebuild_is_deterministic_and_preserves_sources(self):
        self.assertEqual(self.data, build(DEFAULT_SOURCE, BASE / 'storyboard.json'))
        self.assertEqual(DEFAULT_SOURCE.read_bytes(), self.source)
        self.assertEqual((BASE / 'storyboard.json').read_bytes(), self.story_bytes)
        self.assertEqual(self.data['meta']['sourceSha256'], hashlib.sha256(self.source).hexdigest())
        payload = (BASE / 'data.js').read_text().split('window.TRAJECTORY_DEMO = ', 1)[1]
        self.assertEqual(json.loads(payload.rstrip().removesuffix(';')), self.data)

    def test_every_node_preserves_its_exact_source_content(self):
        self.assertEqual(self.data['meta']['nodeCounts'], {'reasoning': 14, 'action': 28, 'observation': 14})
        self.assertEqual(len({n['id'] for n in self.data['nodes']}), 56)
        steps = {s['step_id']: s for s in self.trace['steps']}
        for node in self.data['nodes']:
            step, index = steps[node['stepId']], node['index']
            if node['type'] == 'reasoning':
                self.assertEqual(node['content'], step['message'])
            elif node['type'] == 'action':
                call = step['tool_calls'][index]
                self.assertEqual(node['content'], {'tool_name': call['function_name'], 'arguments': call['arguments']})
                self.assertEqual(node['toolCallId'], call['tool_call_id'])
            else:
                self.assertEqual(node['content'], step['observation']['results'][index])

    def test_batch_feedback_is_shared_without_copying_outputs(self):
        for step in self.data['steps']:
            nodes = [n for n in self.data['nodes'] if n['stepId'] == step['id']]
            calls = [n['id'] for n in nodes if n['type'] == 'action']
            observations = [n['id'] for n in nodes if n['type'] == 'observation']
            self.assertEqual(len(observations), 1)
            links = [e for e in self.data['structuralEdges'] if e['target'] == observations[0]]
            self.assertEqual({e['source'] for e in links}, set(calls))
            self.assertTrue(all(e['actionIds'] == calls for e in links))
            self.assertTrue(all(e['kind'] == ('batch_feedback' if len(calls) > 1 else 'returns') for e in links))

    def test_summary_coverage_contains_all_three_types(self):
        nodes = {n['id']: n for n in self.data['nodes']}
        leaf_ids = [n for g in self.data['groups'] for n in g['nodeIds']]
        self.assertEqual(len(leaf_ids), 56)
        self.assertEqual(set(leaf_ids), set(nodes))
        parent = self.data['higherGroups'][0]
        self.assertEqual(len(parent['nodeIds']), 28)
        self.assertEqual({nodes[n]['type'] for n in parent['nodeIds']}, {'reasoning', 'action', 'observation'})


class NodeAdapterTests(unittest.TestCase):
    def setUp(self):
        self.trace = {'session_id': 'example/trace'}
        self.step = {'step_id': 2, 'message': 'Read the file.', 'tool_calls': [
            {'tool_call_id': 'c1', 'function_name': 'read', 'arguments': {'path': '/one'}},
            {'tool_call_id': 'c2', 'function_name': 'read', 'arguments': {'path': '/two'}},
        ], 'observation': {'results': [{'content': 'combined outputs'}]}}

    def test_reasoning_only_event_has_an_independent_node(self):
        nodes, edges, _ = build_nodes(self.trace, [{'step_id': 2, 'message': 'Consider the next step.'}])
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]['type'], 'reasoning')
        self.assertIn('example%2Ftrace/step-2/reasoning', nodes[0]['id'])
        self.assertEqual(edges, [])

    def test_empty_reasoning_and_missing_feedback_create_no_nodes(self):
        step = copy.deepcopy(self.step)
        step['message'] = ' \n '
        del step['observation']
        nodes, edges, _ = build_nodes(self.trace, [step])
        self.assertEqual([n['type'] for n in nodes], ['action', 'action'])
        self.assertEqual(edges, [])

    def test_explicit_feedback_references_preserve_pairing_and_empty_result(self):
        self.step['observation']['results'] = [
            {'content': '', 'source_call_id': 'c2'},
            {'content': 'first file', 'tool_call_id': 'c1'},
        ]
        nodes, edges, refs = build_nodes(self.trace, [self.step])
        self.assertEqual([e['source'] for e in edges], [refs[(2, 'action', 1)], refs[(2, 'action', 0)]])
        self.assertTrue(all(e['kind'] == 'returns' and len(e['actionIds']) == 1 for e in edges))
        self.assertEqual(nodes[-2]['content']['content'], '')

    def test_invalid_call_references_and_duplicate_ids_are_rejected(self):
        self.step['observation']['results'][0]['source_call_id'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'Unknown feedback'):
            build_nodes(self.trace, [self.step])
        self.step['tool_calls'][1]['tool_call_id'] = 'c1'
        with self.assertRaisesRegex(ValueError, 'Duplicate tool call'):
            build_nodes(self.trace, [self.step])


class PredicateBindingTests(unittest.TestCase):
    def setUp(self):
        trace = json.loads(DEFAULT_SOURCE.read_text())
        self.nodes, _, self.refs = build_nodes(trace, [s for s in trace['steps'] if s['source'] == 'agent'])
        self.story = json.loads((BASE / 'storyboard.json').read_text())

    def test_role_order_survives_information_flow_direction(self):
        edges = typed_dependencies(self.story, self.nodes, self.refs)
        self.assertEqual(len(edges), 57)
        repair = next(e for e in edges if e['predicate'] == 'ATTEMPTS_REPAIR')
        self.assertEqual(repair['arguments'], [repair['target'], repair['source']])
        self.assertTrue(all(e['basis'] == 'storyboard_annotation' for e in edges))

    def test_wrong_argument_type_is_rejected(self):
        edge = next(e for e in self.story['dependencies'] if e['predicate'] == 'PLANS_ACTION')
        edge['arguments'][0] = {'step': 2, 'type': 'observation'}
        with self.assertRaisesRegex(ValueError, 'type mismatch'):
            typed_dependencies(self.story, self.nodes, self.refs)

    def test_future_to_past_edge_is_rejected(self):
        edge = self.story['dependencies'][0]
        edge['source'], edge['target'] = edge['target'], edge['source']
        with self.assertRaisesRegex(ValueError, 'before its target'):
            typed_dependencies(self.story, self.nodes, self.refs)

    def test_unknown_node_and_duplicate_binding_are_rejected(self):
        self.story['dependencies'][0]['source']['step'] = 999
        with self.assertRaisesRegex(ValueError, 'Unknown node'):
            typed_dependencies(self.story, self.nodes, self.refs)
        self.story = json.loads((BASE / 'storyboard.json').read_text())
        self.story['dependencies'].append(copy.deepcopy(self.story['dependencies'][0]))
        with self.assertRaisesRegex(ValueError, 'unique arguments'):
            typed_dependencies(self.story, self.nodes, self.refs)


if __name__ == '__main__':
    unittest.main()
