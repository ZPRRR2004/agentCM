"""Hand-picked windows are the exact frozen inputs of a discovery experiment."""
import unittest
import urllib.error

import test_workbench as fixtures
from workbench.common import load_windows, read, write
from workbench.predicate_inputs import verify
from workbench.prompt_upgrade import upgrade_node_contract
from src.trajectory_nodes import window_nodes


class PredicateInputTests(unittest.TestCase):
    setUp = fixtures.WorkbenchTests.setUp
    tearDown = fixtures.WorkbenchTests.tearDown
    get = fixtures.WorkbenchTests.get
    post = fixtures.WorkbenchTests.post
    split = fixtures.WorkbenchTests.split
    wait_status = fixtures.WorkbenchTests.wait_status

    def test_nonconsecutive_windows_are_frozen_and_run_in_source_order(self):
        model = fixtures.WorkbenchTests.model(self)
        source = self.split()
        windows = self.get('experiment?id=' + source['id'])['windows']
        selected = [windows[0]['id'], windows[2]['id']]
        experiment = self.post('experiment/create', {'title': 'Two selected windows',
            'source_experiment_id': source['id'], 'window_ids': list(reversed(selected)), 'batch_size': 10})
        self.assertEqual(experiment['window_ids'], selected)
        self.assertEqual(experiment['window_count'], 2)
        self.assertEqual([w['id'] for w in experiment['windows']], selected)
        root, _ = self.workspace.paths(experiment['id'])
        self.assertEqual([r.run_name for r in load_windows(root/'inputs')], selected)
        self.assertEqual(read(root/'experiment.json')['window_ids'], selected)
        self.assertEqual(experiment['schema'], 'predicate-definition/v2')
        self.assertEqual(experiment['node_counts'], {'action': 2, 'observation': 2, 'reasoning': 2})
        for r in load_windows(root/'inputs'):
            frozen = read(root/'nodes'/(r.run_name + '.json'))
            self.assertEqual(frozen, window_nodes(r.data))
            shown = self.get(f'window?dataset=fixture-v1&experiment={experiment["id"]}&id={r.run_name}')
            self.assertEqual(shown['nodes'], frozen)
            self.assertEqual(shown['node_source'], 'snapshot')
        self.post('experiment/start', {'id': experiment['id']})
        finished = self.wait_status(experiment['id'], 'completed')
        self.assertEqual(finished['completed'], 2)
        self.assertEqual(model.stages.count('discovery'), 2)
        for r in load_windows(root/'inputs'):
            self.assertEqual(read(root/'output/node_windows'/(r.run_name + '.json')),
                             read(root/'nodes'/(r.run_name + '.json')))

    def test_changed_nodes_or_legacy_contract_are_rejected_before_start(self):
        source = self.split()
        e = self.post('experiment/create', {'title': 'Frozen nodes',
            'source_experiment_id': source['id'], 'window_limit': 1})
        root, _ = self.workspace.paths(e['id'])
        meta = read(root/'experiment.json')
        verify(root, meta)
        with self.assertRaisesRegex(ValueError, '旧版节点定义'):
            verify(root, {**meta, 'predicate_schema_version': 'predicate-definition/v1'})
        p = next((root/'nodes').glob('*.json'))
        graph = read(p); graph['core']['nodes'][0]['type'] = 'action'; write(p, graph)
        with self.assertRaisesRegex(ValueError, '节点快照与输入不一致'):
            verify(root, meta)
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/start', {'id': e['id']})
        self.assertNotIn(e['id'], self.workspace.processes)

    def test_prompt_upgrade_preserves_previous_bundle_and_is_idempotent(self):
        defaults = self.workspace.source_prompts()
        old = dict(defaults)
        old['common/granularity_examples.txt'] = '# predicate-definition/v1\nCustom instructions'
        write(self.workspace.data/'prompts.json', old)
        upgrade_node_contract(self.workspace.data, defaults)
        backups = list((self.workspace.data/'prompt_migrations').glob('*.json'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(read(backups[0])['files'], old)
        self.assertEqual(self.workspace.prompts()['files'], defaults)
        upgraded = dict(defaults); upgraded['discovery/system.txt'] += '\nMy v2 edits'
        write(self.workspace.data/'prompts.json', upgraded)
        upgrade_node_contract(self.workspace.data, defaults)
        self.assertEqual(self.workspace.prompts()['files'], upgraded)
        self.assertEqual(list((self.workspace.data/'prompt_migrations').glob('*.json')), backups)

    def test_v1_results_remain_readable_without_reinterpreting_their_input(self):
        source = self.split()
        e = self.post('experiment/create', {'title': 'Historical definition',
            'source_experiment_id': source['id'], 'window_limit': 1})
        root, output = self.workspace.paths(e['id'])
        meta = read(root/'experiment.json')
        for key in ('predicate_schema_version', 'node_schema_version', 'node_counts'):
            meta.pop(key)
        write(root/'experiment.json', meta)
        definition = fixtures.fixture.predicate('USES', ('action', 'information'))
        write(output/'predicate_registry.json', [definition])
        write(output/'execution_state.json', {'predicate_schema_version': 'predicate-definition/v1',
                                             'status': 'completed', 'completed_windows': 1})
        before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
        detail = self.get('experiment?id=' + e['id'])
        shown = self.get(f'window?dataset=fixture-v1&experiment={e["id"]}&id={e["window_ids"][0]}')
        self.assertEqual(detail['schema'], 'predicate-definition/v1')
        self.assertEqual(detail['registry'], [definition])
        self.assertEqual(shown['node_source'], 'legacy_events')
        self.assertNotIn('nodes', shown)
        self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_empty_invalid_and_unknown_window_selections_are_rejected(self):
        source = self.split()
        windows = self.get('experiment?id=' + source['id'])['windows']
        valid = windows[0]['id']
        before = sorted(p.name for p in (self.workspace.data/'experiments').iterdir())
        for selected in ([], None, valid, [1], [valid, valid], ['unknown'], [valid, 'unknown']):
            with self.subTest(selected=selected), self.assertRaises(urllib.error.HTTPError) as error:
                self.post('experiment/create', {'title': 'Invalid input', 'source_experiment_id': source['id'],
                    'window_ids': selected})
            self.assertEqual(error.exception.code, 400)
        self.assertEqual(sorted(p.name for p in (self.workspace.data/'experiments').iterdir()), before)

    def test_limit_applies_to_selected_windows_and_legacy_requests_still_work(self):
        source = self.split()
        windows = self.get('experiment?id=' + source['id'])['windows']
        picked = [windows[1]['id'], windows[2]['id']]
        body = {'title': 'Limited', 'source_experiment_id': source['id'], 'window_ids': picked}
        limited = self.post('experiment/create', {**body, 'window_limit': 1})
        self.assertEqual(limited['window_ids'], picked[:1])
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create', {**body, 'window_limit': 3})
        legacy = self.post('experiment/create', {'title': 'Legacy task selection',
            'source_experiment_id': source['id'], 'trajectory_ids': ['test-trajectory'], 'window_limit': 1})
        self.assertEqual(legacy['window_ids'], [windows[0]['id']])


if __name__ == '__main__':
    unittest.main()
