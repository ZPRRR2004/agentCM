"""Stage boundaries: splitting consumes completed preprocessing outputs only."""
import unittest
import urllib.error

import test_workbench as fixtures
from workbench.common import read, write


class SplitSourceTests(unittest.TestCase):
    setUp = fixtures.WorkbenchTests.setUp
    tearDown = fixtures.WorkbenchTests.tearDown
    get = fixtures.WorkbenchTests.get
    post = fixtures.WorkbenchTests.post
    completed_preprocess = fixtures.WorkbenchTests.completed_preprocess

    def body(self, **extra):
        return {'kind': 'split', 'title': 'Stage boundary', 'dataset_id': 'fixture-v1',
                'trajectory_ids': ['test-trajectory'], 'config': {'max_window_events': 2,
                'overlap_events': 1, 'max_previous_summary_tokens': 0,
                'max_future_summary_tokens': 0}, **extra}

    def reject_both(self, body):
        before = {str(p): p.read_bytes() for p in self.workspace.data.rglob('*') if p.is_file()}
        for route, config in [('experiment/create', body['config']),
                              ('experiment/split-preview', {'max_window_events': 2, 'overlap_events': 1})]:
            with self.subTest(route=route), self.assertRaises(urllib.error.HTTPError) as error:
                self.post(route, {**body, 'config': config})
            self.assertEqual(error.exception.code, 400)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.workspace.data.rglob('*') if p.is_file()})

    def test_missing_source_and_incomplete_source_rejected(self):
        for value in (None, '', 'missing', '../settings.json'):
            self.reject_both(self.body(preprocess_experiment_id=value))
        self.reject_both(self.body())
        draft = self.post('experiment/create', {'kind': 'preprocess', 'title': 'Pending',
            'dataset_id': 'fixture-v1', 'config': {'deduplicate_observation': False, 'remove_source_lines': False}})
        self.reject_both(self.body(preprocess_experiment_id=draft['id']))

    def test_completed_source_dataset_and_selected_records_are_enforced(self):
        record = self.workspace.records('fixture-v1')[0]
        excluded = read(record.path)
        for event in excluded['events']:
            event['tool_calls'] = []
            event['thought'] = ''
        write(record.path.with_name('raw-only.json'), excluded)
        source = self.completed_preprocess()
        body = self.body(preprocess_experiment_id=source['id'])
        self.reject_both({**body, 'dataset_id': 'alternative-v2'})
        self.reject_both({**body, 'trajectory_ids': ['raw-only']})
        self.reject_both({**body, 'trajectory_ids': []})
        preview = self.post('experiment/split-preview', {**body,
            'config': {'max_window_events': 2, 'overlap_events': 1}})
        draft = self.post('experiment/create', body)
        self.assertEqual(draft['trajectory_ids'], ['test-trajectory'])
        self.assertEqual(draft['input_hash'], preview['input_hash'])
        self.assertEqual(draft['preprocess_output_hash'], source['statistics']['output_hash'])
        self.reject_both(self.body(preprocess_experiment_id=draft['id']))

    def test_deleted_or_modified_output_cannot_be_used_as_new_source(self):
        source = self.completed_preprocess()
        body = self.body(preprocess_experiment_id=source['id'])
        self.post('experiment/delete', {'id': source['id']})
        self.reject_both(body)
        self.post('experiment/restore', {'id': source['id']})
        root, output = self.workspace.paths(source['id'])
        state = read(output/'execution_state.json')
        write(output/'execution_state.json', {**state, 'status': 'failed'})
        self.reject_both(body)
        write(output/'execution_state.json', state)
        path = output/'trajectories/test-trajectory.json'
        data = read(path); data['events'][0]['thought'] = 'Changed after completion'; write(path, data)
        self.reject_both(body)


if __name__ == '__main__':
    unittest.main()
