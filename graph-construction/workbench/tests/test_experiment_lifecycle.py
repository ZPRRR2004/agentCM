"""Reversible deletion, live process guards, and independent child snapshots."""
import unittest
import urllib.error
from unittest.mock import Mock

import test_workbench as fixtures
from workbench.common import read, write


class ExperimentLifecycleTests(unittest.TestCase):
    setUp = fixtures.WorkbenchTests.setUp
    tearDown = fixtures.WorkbenchTests.tearDown
    get = fixtures.WorkbenchTests.get
    post = fixtures.WorkbenchTests.post
    wait_status = fixtures.WorkbenchTests.wait_status
    split = fixtures.WorkbenchTests.split

    def preprocess(self):
        return self.post('experiment/create', {'kind': 'preprocess', 'title': 'Parent',
            'dataset_id': 'fixture-v1', 'config': {'deduplicate_observation': True,
            'remove_source_lines': False, 'simplify_call_ids': False}})

    def test_delete_restore_keeps_snapshots_and_survives_reload(self):
        e = self.preprocess()
        root, _ = self.workspace.paths(e['id'])
        frozen = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        self.post('experiment/delete', {'id': e['id']})
        self.assertEqual(self.get('experiments'), [])
        self.assertEqual(self.get('bootstrap')['experiments'], [])
        self.assertEqual(self.get('experiments/deleted')[0]['id'], e['id'])
        for path, data in frozen.items():
            self.assertEqual((root/path).read_bytes(), data)
        from workbench.store import Workspace
        fresh = Workspace(self.workspace.data, discovery=self.source, catalog_path=self.catalog_path)
        self.assertEqual(fresh.experiments(), [])
        for endpoint in ('experiment?id='+e['id'],
                         'preprocess-comparison?id='+e['id']+'&trajectory=test-trajectory'):
            with self.assertRaises(urllib.error.HTTPError):
                self.get(endpoint)
        for action in ('start', 'delete'):
            with self.assertRaises(urllib.error.HTTPError):
                self.post('experiment/'+action, {'id': e['id']})
        self.post('experiment/restore', {'id': e['id']})
        self.assertEqual(self.get('experiment?id='+e['id'])['status'], 'draft')
        self.assertEqual(self.get('experiments/deleted'), [])
        self.assertEqual({p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}, frozen)
        self.post('experiment/start', {'id': e['id']})
        self.wait_status(e['id'], 'completed')

    def test_parent_deletion_keeps_child_inputs_tasks_and_reviews(self):
        parent = self.preprocess()
        self.post('experiment/start', {'id': parent['id']})
        self.wait_status(parent['id'], 'completed')
        child_body = {'kind': 'split', 'title': 'Child', 'dataset_id': 'fixture-v1',
            'preprocess_experiment_id': parent['id'], 'config': {'max_window_events': 1,
            'overlap_events': 0, 'max_previous_summary_tokens': 0, 'max_future_summary_tokens': 0}}
        child = self.post('experiment/create', child_body)
        self.post('experiment/delete', {'id': parent['id']})
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create', child_body)
        self.post('experiment/start', {'id': child['id']})
        child = self.wait_status(child['id'], 'completed')
        predicate = self.post('experiment/create', {'kind': 'predicate', 'title': 'Discovery',
            'dataset_id': 'fixture-v1', 'source_experiment_id': child['id'], 'batch_size': 1})
        self.post('task', {'title': 'Keep the association', 'experiment_id': predicate['id']})
        task = read(self.workspace.data/'tasks.json')[0]
        reviews = {predicate['id']: {'sample': {'notes': 'keep this review'}}}
        write(self.workspace.data/'reviews.json', reviews)
        self.post('experiment/delete', {'id': child['id']})
        self.assertEqual(self.get('experiment?id='+predicate['id'])['total'], 3)
        self.post('experiment/delete', {'id': predicate['id']})
        # Existing task links remain editable; new links select active experiments.
        self.post('task', {'id': task['id'], 'status': 'doing'})
        self.assertEqual(read(self.workspace.data/'tasks.json')[0]['experiment_id'], predicate['id'])
        with self.assertRaises(urllib.error.HTTPError):
            self.post('task', {'title': 'New link', 'experiment_id': predicate['id']})
        self.assertEqual(read(self.workspace.data/'reviews.json'), reviews)
        for e in (parent, child, predicate):
            self.post('experiment/restore', {'id': e['id']})
            self.assertEqual(self.get('experiment?id='+e['id'])['kind'], e['kind'])
        self.assertEqual(read(self.workspace.data/'reviews.json'), reviews)

    def test_live_workers_block_deletion_and_late_monitor_keeps_tombstone(self):
        e = self.preprocess()
        root, _ = self.workspace.paths(e['id'])
        process = Mock()
        process.poll.return_value = None
        self.workspace.processes[e['id']] = process
        for waiting in (False, True):
            if waiting:
                write(root/'pending_feedback.json', {'token': 'wait', 'batch': 1})
            with self.assertRaises(urllib.error.HTTPError):
                self.post('experiment/delete', {'id': e['id']})
            self.assertFalse((root/'deleted.json').exists())
        process.poll.return_value = 0
        process.wait.return_value = 0
        write(root/'lifecycle.json', {'status': 'running'})
        self.post('experiment/delete', {'id': e['id']})
        self.workspace._monitor(e['id'], root, process)
        self.assertTrue((root/'deleted.json').is_file())
        self.assertEqual(self.get('experiments'), [])

    def test_delete_restore_validate_identity_and_write_token(self):
        e = self.preprocess()
        for action in ('delete', 'restore'):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.post('experiment/'+action, {'id': e['id']}, token='invalid')
            self.assertEqual(error.exception.code, 403)
            for identity in ('../../settings', None, 'ffffffffffff'):
                with self.assertRaises(urllib.error.HTTPError):
                    self.post('experiment/'+action, {'id': identity})
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/restore', {'id': e['id']})
        self.assertEqual(len(self.get('experiments')), 1)


if __name__ == '__main__':
    unittest.main()
