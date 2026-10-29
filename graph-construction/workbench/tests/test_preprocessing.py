"""Preprocessing fidelity, frozen comparisons, and split lineage through the API."""
import copy
import json
import unittest
import urllib.error
from unittest.mock import patch

import test_workbench as fixtures
from workbench.common import read, write
from workbench import preprocessing
from src.preprocess.compact import compact_trajectory

CONFIG = {'deduplicate_observation': True, 'remove_source_lines': True}
ID_CONFIG = {**CONFIG, 'simplify_call_ids': True}


def enrich(data):
    data['metadata'] = {**data.get('metadata', {}), 'original': 'kept for tracing'}
    for i, event in enumerate(data['events']):
        event['source_line'] = i + 10
        if not event['tool_calls']:
            event['tool_calls'] = [{'tool_call_id': f'call-{i}', 'tool_name': 'bash',
                'arguments': {'command': 'cat result.txt'},
                'observation': {'raw': 'Exact output\n  preserved whitespace\n<script>sample</script>'}}]
        for call in event['tool_calls']:
            call['source_call_id'] = 'upstream-' + call['tool_call_id']
            obs = call['observation']
            obs['content'] = [{'type': 'text', 'text': obs['raw']}]
            obs['source_line'] = i + 11
            obs['is_error'] = False
    return data


class FieldProjectionTests(unittest.TestCase):
    def test_short_ids_are_unique_stable_and_reversible_by_position(self):
        def call(identity, **extra):
            return {'tool_call_id': identity, 'tool_name': 'read',
                    'arguments': {'tool_call_id': identity, 'source_call_id': 'literal argument'},
                    'observation': {'raw': identity, 'is_error': False}, **extra}
        original = {'events': [
            {'event_id': 'event-1', 'thought': 'keep', 'tool_calls': [
                call('call-0002', source_call_id='upstream'), call('call-0002')]},
            {'event_id': 'event-2', 'thought': 'keep', 'tool_calls': [
                call('call-0003', source_call_id=None), call('long-original')]}]}
        frozen = copy.deepcopy(original)
        config = {**{k: False for k in CONFIG}, 'simplify_call_ids': True}
        after, report = compact_trajectory(original, config)
        calls = [c for e in after['events'] for c in e['tool_calls']]
        self.assertEqual([c['tool_call_id'] for c in calls],
                         ['call-0001', 'call-0002', 'call-0003', 'call-0004'])
        self.assertTrue(all('source_call_id' not in c for c in calls))
        self.assertEqual(report['replaced_fields'], 2)
        self.assertEqual(report['removed_fields'], 2)
        self.assertEqual([c['path'] for c in report['call_id_mapping']],
                         ['events[0].tool_calls[0]', 'events[0].tool_calls[1]',
                          'events[1].tool_calls[0]', 'events[1].tool_calls[1]'])
        restored = copy.deepcopy(after)
        for mapping, call_after, call_original in zip(report['call_id_mapping'],
                [c for e in restored['events'] for c in e['tool_calls']],
                [c for e in original['events'] for c in e['tool_calls']]):
            self.assertEqual(call_after['arguments'], call_original['arguments'])
            self.assertEqual(call_after['observation'], call_original['observation'])
            call_after['tool_call_id'] = mapping['original_tool_call_id']
            if 'original_source_call_id' in mapping:
                call_after['source_call_id'] = mapping['original_source_call_id']
        self.assertEqual(restored, original)
        self.assertEqual(original, frozen)
        self.assertEqual(compact_trajectory(original, config), (after, report))
        self.assertEqual(compact_trajectory(after, config)[1]['changes'], [])
        self.assertEqual(compact_trajectory(original, {**config, 'simplify_call_ids': False})[0], original)

    def test_short_ids_require_a_valid_original_id(self):
        for identity in (None, '', 123):
            with self.subTest(identity=identity), self.assertRaises(ValueError):
                compact_trajectory({'events': [{'event_id': 'e1', 'tool_calls': [
                    {'tool_call_id': identity}]}]}, ID_CONFIG)

    def test_only_proven_text_duplicates_are_removed(self):
        observations = [
            {'raw': 'a\nb', 'content': [{'type':'text', 'text':'a'}, {'type':'text', 'text':'b'}]},
            {'raw': 'a', 'content': [{'type':'text','text':'different'}]},
            {'raw': 'a', 'content': [{'type':'text','text':'a', 'annotation':'needed'}]},
            {'raw': 'a', 'content': [{'type':'text','text':'a'}, {'type':'image','data':'image-data'}]},
        ]
        original = {'query': {'title':'t','text':'q'}, 'metadata': {'keep':True},
                    'events':[{'event_id':'e1','source_line':12,'thought':'reason',
                    'tool_calls':[{'tool_call_id': str(i), 'arguments': {'line': 12},
                                   'observation':obs} for i,obs in enumerate(observations)]}]}
        frozen = copy.deepcopy(original)
        after, report = compact_trajectory(original, CONFIG)
        self.assertEqual(original, frozen)
        self.assertNotIn('content', after['events'][0]['tool_calls'][0]['observation'])
        self.assertEqual([c['observation'] for c in after['events'][0]['tool_calls'][1:]], observations[1:])
        self.assertEqual(after['events'][0]['tool_calls'][0]['arguments'], {'line':12})
        self.assertEqual(after['metadata'], original['metadata'])
        self.assertEqual(report['removed_fields'], 2)
        identity, unchanged = compact_trajectory(original, {k:False for k in CONFIG})
        self.assertEqual(identity, original)
        self.assertEqual(unchanged['reduction_percent'], 0)


class PreprocessingTests(unittest.TestCase):
    setUp = fixtures.WorkbenchTests.setUp
    tearDown = fixtures.WorkbenchTests.tearDown
    get = fixtures.WorkbenchTests.get
    post = fixtures.WorkbenchTests.post
    wait_status = fixtures.WorkbenchTests.wait_status

    def create_preprocess(self, **changes):
        for record in self.workspace.records('fixture-v1'):
            write(record.path, enrich(record.data))
        return self.post('experiment/create', dict(kind='preprocess', title='Output deduplication',
                         dataset_id='fixture-v1', config=changes.pop('config', CONFIG), **changes))

    def test_preview_frozen_output_and_split_lineage(self):
        e = self.create_preprocess(config=ID_CONFIG)
        identity = e['id']
        root, output = self.workspace.paths(identity)
        frozen = read(root/'inputs/test-trajectory.json')
        source = self.workspace.records('fixture-v1')[0]
        source.data['events'][0]['thought'] = 'edited after snapshot'
        write(source.path, source.data)
        endpoint = 'preprocess-comparison?id='+identity+'&trajectory=test-trajectory'
        preview = self.get(endpoint)
        self.assertFalse(preview['saved'])
        self.assertEqual(preview['before'], frozen['events'][0])
        self.assertGreater(preview['statistics']['removed_fields'], 0)
        self.assertEqual(preview['after']['tool_calls'][0]['tool_call_id'], 'call-0001')
        self.assertNotIn('source_call_id', preview['after']['tool_calls'][0])
        self.assertEqual(preview['call_id_mapping'][0]['original_tool_call_id'],
                         frozen['events'][0]['tool_calls'][0]['tool_call_id'])
        self.assertFalse(output.exists())
        # Local preprocessing can run with an empty model key.
        self.post('settings', {'clear_key':True})
        self.post('experiment/start', {'id':identity})
        done = self.wait_status(identity, 'completed')
        saved = self.get(endpoint)
        self.assertTrue(saved['saved'])
        self.assertEqual(saved['after'], preview['after'])
        self.assertEqual(saved['changes'], preview['changes'])
        self.assertEqual(saved['call_id_mapping'], preview['call_id_mapping'])
        mapping = read(output/'call-id-maps/test-trajectory.json')
        self.assertEqual(mapping['schema'], 'call-id-map/v1')
        self.assertEqual(mapping['trajectory_id'], 'test-trajectory')
        self.assertEqual(len(mapping['calls']), 3)
        self.assertEqual(done['statistics']['replaced_fields'], 3)
        self.assertNotIn('call_id_mapping', read(output/'reports/test-trajectory.json'))
        self.assertNotIn('call_id_mapping', saved['statistics'])
        self.assertEqual(read(root/'inputs/test-trajectory.json'), frozen)
        self.assertEqual(read(source.path)['events'][0]['thought'], 'edited after snapshot')
        self.assertEqual(len(done['trajectories']), 1)
        self.assertGreater(done['statistics']['saved_tokens'], 0)
        whole = self.get(endpoint+'&event=__all__')
        self.assertEqual(whole['before']['metadata'], whole['after']['metadata'])
        self.assertEqual([e['event_id'] for e in whole['before']['events']],
                         [e['event_id'] for e in whole['after']['events']])
        body = {'kind':'split','title':'From preprocessed trajectories','dataset_id':'fixture-v1',
                'preprocess_experiment_id':identity,'trajectory_ids':['test-trajectory'],
                'config':{'max_window_events':2,'overlap_events':1,'max_previous_summary_tokens':0,'max_future_summary_tokens':0}}
        split = self.post('experiment/create', body)
        self.assertEqual(split['preprocess_output_hash'], done['statistics']['output_hash'])
        pre = self.post('experiment/split-preview', {**body,'config':{'max_window_events':2,'overlap_events':1}})
        self.post('experiment/start', {'id':split['id']})
        split_done = self.wait_status(split['id'], 'completed')
        self.assertEqual(pre['window_count'], split_done['produced_windows'])
        _, split_output = self.workspace.paths(split['id'])
        windows = [read(f) for f in sorted((split_output/'windows').glob('*.json'))]
        events = [event for window in windows for event in window['core']['events']]
        self.assertEqual(events, whole['after']['events'])
        self.assertEqual(windows[1]['overlap']['events'], [events[1]])
        self.assertEqual(windows[1]['overlap']['events'][0]['tool_calls'][0]['tool_call_id'], 'call-0002')
        from src.discover_predicates.window_loader import serialize_context_window
        model_input = serialize_context_window(windows[1])
        self.assertNotIn('source_call_id', model_input)
        self.assertNotIn('original_tool_call_id', model_input)
        # Saved child inputs are independent of later edits to the parent output.
        parent_file = output/'trajectories/test-trajectory.json'
        data = read(parent_file); data['events'][0]['thought'] = 'tampered'; write(parent_file,data)
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create', body)
        self.assertEqual(self.get('experiment?id='+split['id'])['status'], 'completed')

    def test_invalid_rules_and_comparison_selection(self):
        for config in ({}, {**CONFIG,'delete_events':True}, {**CONFIG,'remove_source_lines':'yes'}):
            with self.assertRaises(urllib.error.HTTPError):
                self.post('experiment/create', {'kind':'preprocess','title':'Bad','dataset_id':'fixture-v1','config':config})
        e = self.create_preprocess()
        for tail in ('&trajectory=../../settings', '&trajectory=test-trajectory&event=missing'):
            with self.assertRaises(urllib.error.HTTPError):
                self.get('preprocess-comparison?id='+e['id']+tail)
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create', {'kind':'split','title':'Early','dataset_id':'fixture-v1',
                 'preprocess_experiment_id':e['id'], 'config':{'max_window_events':1,'overlap_events':0,
                 'max_previous_summary_tokens':0,'max_future_summary_tokens':0}})
        root, _ = self.workspace.paths(e['id'])
        changed = read(root/'inputs/test-trajectory.json');changed['events'].reverse()
        write(root/'inputs/test-trajectory.json', changed)
        with self.assertRaises(urllib.error.HTTPError):
            self.get('preprocess-comparison?id='+e['id']+'&trajectory=test-trajectory')

    def test_resume_rebuilds_deterministic_results(self):
        e = self.create_preprocess(config=ID_CONFIG)
        root, output = self.workspace.paths(e['id'])
        real_write = preprocessing.write
        def interrupted(path, data):
            real_write(path, data)
            if path.parent.name == 'trajectories':
                raise RuntimeError('simulated interruption')
        with patch.object(preprocessing, 'write', side_effect=interrupted):
            with self.assertRaises(RuntimeError):
                preprocessing.run(root)
        preprocessing.run(root)
        self.assertEqual(read(output/'execution_state.json')['status'], 'completed')
        expected, report = compact_trajectory(read(root/'inputs/test-trajectory.json'), ID_CONFIG)
        self.assertEqual(read(output/'trajectories/test-trajectory.json'), expected)
        self.assertEqual(read(output/'call-id-maps/test-trajectory.json')['calls'], report['call_id_mapping'])

    def test_legacy_snapshots_keep_original_ids_on_preview_run_and_resume(self):
        e = self.create_preprocess()
        root, output = self.workspace.paths(e['id'])
        meta = read(root/'experiment.json')
        meta.update(algorithm='trajectory-fields/v1', config=CONFIG)
        write(root/'experiment.json', meta)
        endpoint = 'preprocess-comparison?id='+e['id']+'&trajectory=test-trajectory'
        preview = self.get(endpoint)
        self.assertEqual(preview['before']['tool_calls'][0]['tool_call_id'],
                         preview['after']['tool_calls'][0]['tool_call_id'])
        self.assertEqual(preview['call_id_mapping'], [])
        preprocessing.run(root)
        self.assertFalse((output/'call-id-maps').exists())
        report = read(output/'reports/test-trajectory.json')
        report.pop('replaced_fields')
        for change in report['changes']:
            change.pop('operation')
        write(output/'reports/test-trajectory.json', report)
        self.assertEqual(self.get(endpoint)['after'], preview['after'])
        preprocessing.run(root)
        self.assertEqual(self.get(endpoint)['after'], preview['after'])


if __name__ == '__main__':
    unittest.main()
