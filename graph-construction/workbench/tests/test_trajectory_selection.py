"""Success evidence, retry ordering, frozen filtering and downstream isolation."""
import copy
from pathlib import Path
import unittest
import urllib.error

import test_workbench as fixtures
from workbench.common import read, write
from workbench.datasets import Trajectory
from workbench.trajectory_selection import (select_successful, select_records, trajectory_summary,
                                            POLICY, TOOL_REQUIRED_POLICY, INFRASTRUCTURE_POLICY, PREVIOUS_POLICY, LEGACY_POLICY)
from workbench.datasets import load_trajectories
from workbench import preprocessing


def attempt(identity, task='task', passed=True, scored=True, index=1, with_tools=True, **metadata):
    data = {'query': {'title': 'Same display title', 'text': 'Task'},
            'events': [{'event_id': 'e1', 'source': 'agent', 'thought': 'keep', 'tool_calls': [{
                'tool_call_id': 'c1', 'tool_name': 'read', 'arguments': {'path': '/tmp/input'},
                'observation': {'raw': 'content', 'is_error': False}}] if with_tools else []}],
            'metadata': {'task_id': task, 'result': {'pass': passed, 'scored': scored},
                         'attempt_index': index, **metadata}}
    return Trajectory(Path(identity + '.json'), identity, data, identity)


class LegacySelectionTests(unittest.TestCase):
    def test_latest_success_survives_later_failure_and_distinct_tasks(self):
        records = [attempt('a-first'), attempt('b-retry', index=2),
                   attempt('c-failed', passed=False, index=3),
                   attempt('d-infra', passed=True, scored=False, index=4),
                   attempt('e-other', task='other'), attempt('f-unknown', passed='true')]
        frozen = copy.deepcopy(records)
        kept, report = select_successful(records)
        self.assertEqual([r.trajectory_id for r in kept], ['b-retry', 'e-other'])
        self.assertEqual(report['excluded_by_reason'], {'duplicate_success': 1,
            'failed': 1, 'unscored': 1, 'unknown_result': 1})
        self.assertEqual(report['rows'][0]['kept_id'], 'b-retry')
        self.assertEqual(records, frozen)
        self.assertEqual(select_successful(kept)[1]['excluded_count'], 0)

    def test_order_uses_recorded_time_instead_of_filename_or_length(self):
        older = attempt('z-old', started_at='2026-08-22T15:00:00+08:00')
        newer = attempt('a-new', started_at='2026-08-22T08:00:00Z')
        self.assertEqual(select_successful([older, newer])[1]['retained_ids'], ['a-new'])
        for r, timestamp in [(older, 1787103890220866275), (newer, 1787409072998432234)]:
            r.data['metadata'].pop('started_at')
            r.data['metadata'].update(adapter='omp-completed-messages/v1',
                source_file=f'xhigh/traces/task/agent/omp-task-{timestamp}/omp.jsonl')
        self.assertEqual(select_successful([older, newer])[1]['retained_ids'], ['a-new'])

    def test_missing_evidence_empty_inputs_and_ambiguous_order(self):
        records = [attempt('no-score', scored=None), attempt('no-task', task=None), attempt('empty')]
        records[-1].data['events'] = []
        self.assertEqual(select_successful(records)[1]['retained_count'], 0)
        self.assertEqual(select_successful([])[1]['input_count'], 0)
        with self.assertRaisesRegex(ValueError, 'started_at'):
            select_successful([attempt('a', index=None), attempt('b', index=None)])


class RecordSelectionTests(unittest.TestCase):
    def test_v5_keeps_reasoning_only_success_failure_and_distinct_attempts(self):
        records = [attempt('success-text', with_tools=False),
                   attempt('failed-text', with_tools=False, passed=False, index=2),
                   attempt('unknown-text', with_tools=False, passed=None, scored=None),
                   attempt('infra-text', with_tools=False, result={
                       'pass': False, 'scored': False, 'errorCode': 'command_exec_failed'})]
        kept, report = select_records(records)
        self.assertEqual(kept, records[:3])
        self.assertEqual(report['policy'], 'execution-record/v5')
        self.assertEqual(report['excluded_by_reason'], {'infrastructure_failure': 1})
        self.assertTrue(all(r['reasoning_events'] == 1 for r in report['rows']))
        self.assertEqual(report['flag_counts'], {'no_tool_calls': 3})
        self.assertEqual(select_records(records, 'success_only')[1]['retained_ids'], ['success-text'])
        self.assertEqual(select_records(records, policy=TOOL_REQUIRED_POLICY)[1]['retained_count'], 0)

    def test_v5_only_counts_nonempty_agent_text_as_reasoning(self):
        empty = attempt('empty', with_tools=False)
        empty.data['events'][0]['thought'] = ' \n '
        user = attempt('user', with_tools=False)
        user.data['events'][0]['source'] = 'user'
        system = attempt('system', with_tools=False)
        system.data['events'][0]['source'] = 'system'
        late = attempt('late', with_tools=False)
        late.data['events'].insert(0, {'event_id': 'empty', 'source': 'agent', 'thought': ''})
        kept, report = select_records([empty, user, system, late])
        self.assertEqual(kept, [late])
        self.assertEqual(report['excluded_by_reason'], {'no_node_content': 3})
        self.assertEqual(report['rows'][-1]['reasoning_events'], 1)

    def test_default_keeps_success_failure_unknown_and_separate_attempts(self):
        records = [attempt('success-1'), attempt('success-2', index=2),
                   attempt('failed', passed=False, index=3),
                   attempt('unscored', passed=False, scored=False),
                   attempt('unknown', passed=None, scored=None, task=None)]
        frozen = copy.deepcopy(records)
        kept, report = select_records(records)
        self.assertEqual(kept, records)
        self.assertEqual(records, frozen)
        self.assertEqual(report['outcome_counts'], {'success': 2, 'failure': 1, 'unscored': 1, 'unknown': 1})
        self.assertEqual(report['flag_counts'], {})
        self.assertEqual(report['excluded_count'], 0)

    def test_only_identical_records_are_deduplicated_with_stable_representative(self):
        first = attempt('original')
        duplicate = copy.deepcopy(first)
        duplicate.trajectory_id = 'zz-copy'
        duplicate.path = Path('zz-copy.json')
        duplicate.data = dict(reversed(list(duplicate.data.items())))
        retry = attempt('retry', index=2)
        changed = copy.deepcopy(first)
        changed.trajectory_id = 'changed-content'
        changed.data['events'][0]['thought'] = 'Different execution content'
        records = [duplicate, retry, first, changed]
        kept, report = select_records(records)
        self.assertEqual([r.trajectory_id for r in kept], ['retry', 'original', 'changed-content'])
        self.assertEqual(report['rows'][0]['duplicate_of'], 'original')
        self.assertEqual(report['excluded_by_reason'], {'duplicate_record': 1})
        self.assertEqual(select_records(list(reversed(records)))[1]['excluded_by_reason'], {'duplicate_record': 1})
        self.assertEqual(select_records(kept)[1]['excluded_count'], 0)

    def test_different_run_provenance_stays_distinct_even_with_same_events(self):
        records = [attempt('run-1', source_file='run1/trace.jsonl'),
                   attempt('run-2', source_file='run2/trace.jsonl')]
        self.assertEqual(records[0].data['events'], records[1].data['events'])
        self.assertEqual(select_records(records)[1]['retained_count'], 2)

    def test_success_only_is_optional_and_keeps_multiple_successes(self):
        records = [attempt('a', index=None, source_file='a'), attempt('b', index=None, source_file='b'),
                   attempt('failed', passed=False), attempt('unscored', scored=False)]
        report = select_records(records, 'success_only')[1]
        self.assertEqual(report['retained_ids'], ['a', 'b'])
        self.assertEqual(report['excluded_by_reason'], {'result_filter': 2})

    def test_infrastructure_and_no_tool_flags_are_independent_and_evidence_based(self):
        infra = attempt('infra', with_tools=False,
                        result={'pass': False, 'scored': False, 'errorCode': 'command_exec_failed'})
        self.assertEqual(trajectory_summary(infra)['flags'], ['infrastructure_failure', 'no_tool_calls'])
        infra.data['events'][0]['tool_calls'] = [{'observation': {'is_error': True}}]
        self.assertEqual(trajectory_summary(infra)['flags'], ['infrastructure_failure'])
        infra.data['metadata']['result']['scored'] = True
        self.assertEqual(trajectory_summary(infra)['flags'], [])
        unknown = attempt('unknown', scored=False, with_tools=False)
        self.assertEqual(trajectory_summary(unknown)['flags'], ['no_tool_calls'])

    def test_infrastructure_interruptions_are_filtered_and_both_rerun_outcomes_survive(self):
        infra = attempt('original-interrupted', result={
            'pass': False, 'scored': False, 'errorCode': 'command_exec_failed'})
        infra.data['events'][0]['tool_calls'] = [{'observation': {'is_error': True}}]
        records = [infra, attempt('success-rerun', index=2),
                   attempt('failed-rerun', passed=False, index=3),
                   attempt('other-unscored', scored=False, index=4)]
        frozen = copy.deepcopy(records)
        kept, report = select_records(records)
        self.assertEqual(kept, records[1:])
        self.assertEqual(report['excluded_by_reason'], {'infrastructure_failure': 1})
        self.assertEqual(report['rows'][0]['flags'], ['infrastructure_failure'])
        self.assertEqual(report['flag_counts'], {})
        self.assertEqual(select_records([infra])[1]['retained_count'], 0)
        self.assertEqual(select_records(records, 'success_only')[1]['retained_ids'], ['success-rerun'])
        self.assertEqual(records, frozen)
        old_kept, old_report = select_records(records, policy=PREVIOUS_POLICY)
        self.assertEqual(old_kept, records)
        self.assertEqual(old_report['policy'], PREVIOUS_POLICY)
        self.assertEqual(old_report['excluded_count'], 0)

    def test_v4_excludes_no_tool_calls_and_counts_whole_trajectory(self):
        records = [attempt('success-text-only', with_tools=False),
                   attempt('failure-text-only', passed=False, with_tools=False),
                   attempt('unknown-text-only', passed=None, scored=None, with_tools=False),
                   attempt('infra-text-only', with_tools=False, result={
                       'pass': False, 'scored': False, 'errorCode': 'command_exec_failed'}),
                   attempt('has-tool-error', passed=False)]
        records[-1].data['events'].insert(0, {'event_id': 'thought-only', 'thought': 'plan'})
        records[-1].data['events'][1]['tool_calls'][0]['observation']['is_error'] = True
        frozen = copy.deepcopy(records)
        kept, report = select_records(records, policy=TOOL_REQUIRED_POLICY)
        self.assertEqual(kept, records[-1:])
        self.assertEqual(report['excluded_by_reason'], {'no_tool_calls': 3, 'infrastructure_failure': 1})
        self.assertEqual(report['excluded_count'], 4)
        self.assertEqual(report['rows'][3]['flags'], ['infrastructure_failure', 'no_tool_calls'])
        self.assertEqual(report['rows'][-1]['tool_calls'], 1)
        self.assertEqual(select_records(records, 'success_only', policy=TOOL_REQUIRED_POLICY)[1]['retained_count'], 0)
        self.assertEqual(select_records(records, policy=INFRASTRUCTURE_POLICY)[1]['retained_count'], 4)
        self.assertEqual(records, frozen)

    def test_empty_events_missing_metadata_and_invalid_options(self):
        record = attempt('empty'); record.data['events'] = []; record.data['metadata'] = None
        report = select_records([record])[1]
        self.assertEqual(report['retained_count'], 0)
        self.assertEqual(report['excluded_by_reason'], {'no_node_content': 1})
        self.assertEqual(report['rows'][0]['outcome'], 'unknown')
        self.assertEqual(select_records([])[1]['input_count'], 0)
        for mode in (None, 'failed', True):
            with self.assertRaises(ValueError):
                select_records([record], mode)
        with self.assertRaises(ValueError):
            select_records([record], policy='unknown-policy')


class SelectionIntegrationTests(unittest.TestCase):
    setUp = fixtures.WorkbenchTests.setUp
    tearDown = fixtures.WorkbenchTests.tearDown
    get = fixtures.WorkbenchTests.get
    post = fixtures.WorkbenchTests.post
    wait_status = fixtures.WorkbenchTests.wait_status

    def test_preview_create_run_resume_and_split_use_identical_selection(self):
        original = self.workspace.records('fixture-v1')[0]
        original.path.unlink()
        first = attempt('first')
        duplicate = copy.deepcopy(first); duplicate.path = Path('zz-copy.json')
        for record in [first, duplicate, attempt('success-retry', index=2),
                       attempt('failed-last', passed=False, index=3),
                       attempt('infra', task='infra', result={
                           'pass': False, 'scored': False, 'errorCode': 'command_exec_failed'}),
                       attempt('no-tools', with_tools=False),
                       attempt('unknown', task='unknown', passed=None, scored=None)]:
            write(original.path.parent / record.path.name, record.data)
        body = {'kind': 'preprocess', 'title': 'Keep attempts', 'dataset_id': 'fixture-v1',
                'config': {'deduplicate_observation': True, 'remove_source_lines': False}}
        preview = self.post('experiment/preprocess-preview', body)
        expected = ['failed-last', 'first', 'no-tools', 'success-retry', 'unknown']
        self.assertEqual(preview['input_count'], 7)
        self.assertEqual(preview['retained_ids'], expected)
        self.assertEqual(self.get('experiments'), [])
        e = self.post('experiment/create', body)
        self.assertEqual(e['selection'], preview)
        self.assertEqual(e['total'], 5)
        self.assertEqual(e['selection_policy'], POLICY)
        self.assertEqual(preview['excluded_by_reason'], {
            'duplicate_record': 1, 'infrastructure_failure': 1})
        self.assertEqual(e['selection_mode'], 'all')
        self.assertEqual([t['id'] for t in e['trajectories']], expected)
        root, output = self.workspace.paths(e['id'])
        self.assertEqual(len(list((root/'inputs').glob('*.json'))), 7)
        # Editing live scores after creation cannot change a frozen experiment.
        source = original.path.parent/'success-retry.json'
        value = read(source); value['metadata']['result']['pass'] = False; write(source, value)
        with self.assertRaises(urllib.error.HTTPError):
            self.get('preprocess-comparison?id='+e['id']+'&trajectory=zz-copy')
        with self.assertRaises(urllib.error.HTTPError):
            self.get('preprocess-comparison?id='+e['id']+'&trajectory=infra')
        self.assertEqual(self.get('preprocess-comparison?id='+e['id']+'&trajectory=no-tools')['assessment']['reasoning_events'], 1)
        self.assertEqual(self.get('preprocess-comparison?id='+e['id']+'&trajectory=failed-last')['assessment']['outcome'], 'failure')
        self.post('experiment/start', {'id': e['id']})
        done = self.wait_status(e['id'], 'completed')
        self.assertEqual(done['statistics']['excluded_trajectory_count'], 2)
        self.assertEqual(sorted(p.stem for p in (output/'trajectories').glob('*.json')), expected)
        preprocessing.run(root)
        self.assertEqual(read(output/'statistics.json'), done['statistics'])
        child = self.post('experiment/create', {'kind': 'split', 'title': 'Filtered child',
            'dataset_id': 'fixture-v1', 'preprocess_experiment_id': e['id'],
            'config': {'max_window_events': 2, 'overlap_events': 0,
                       'max_previous_summary_tokens': 0, 'max_future_summary_tokens': 0}})
        self.assertEqual(child['trajectory_ids'], expected)
        self.post('experiment/start', {'id': child['id']})
        self.wait_status(child['id'], 'completed')
        from src.trajectory_nodes import build_nodes
        text_only = read(output/'trajectories/no-tools.json')
        graph = build_nodes('no-tools', text_only['events'])
        self.assertEqual([n['type'] for n in graph['nodes']], ['reasoning'])
        self.assertEqual(graph['nodes'][0]['content'], 'keep')
        self.assertEqual(graph['structural_edges'], [])
        selection = read(root/'selection.json'); selection['retained_ids'] = ['failed-last']
        write(root/'selection.json', selection)
        with self.assertRaisesRegex(ValueError, '筛选快照'):
            preprocessing.run(root)

    def test_all_failed_can_run_by_default_and_success_only_empty_is_rejected(self):
        original = self.workspace.records('fixture-v1')[0]
        value = original.data; value['metadata']['result']['pass'] = False; write(original.path, value)
        body = {'kind': 'preprocess', 'title': 'No successes', 'dataset_id': 'fixture-v1',
                'config': {'deduplicate_observation': True, 'remove_source_lines': False}}
        self.assertEqual(self.post('experiment/preprocess-preview', body)['retained_count'], 1)
        e = self.post('experiment/create', body)
        self.post('experiment/start', {'id': e['id']})
        self.assertEqual(self.wait_status(e['id'], 'completed')['statistics']['trajectory_count'], 1)
        for extra in ({'selection_mode': 'success_only'}, {'trajectory_ids': []}):
            preview = self.post('experiment/preprocess-preview', {**body, **extra})
            self.assertEqual(preview['retained_count'], 0)
            with self.assertRaises(urllib.error.HTTPError):
                self.post('experiment/create', {**body, **extra})
        self.assertEqual(len(self.get('experiments')), 1)

    def test_successful_task_v1_snapshot_keeps_legacy_selection(self):
        original = self.workspace.records('fixture-v1')[0]
        original.path.unlink()
        for r in [attempt('first'), attempt('success-retry', index=2), attempt('failed', passed=False)]:
            write(original.path.parent/r.path.name, r.data)
        e = self.post('experiment/create', {'kind': 'preprocess', 'title': 'Frozen legacy rule',
            'dataset_id': 'fixture-v1', 'config': {'deduplicate_observation': True, 'remove_source_lines': False}})
        root, output = self.workspace.paths(e['id'])
        kept, legacy = select_successful(load_trajectories(root/'inputs'))
        meta = read(root/'experiment.json')
        meta.update(selection_policy=LEGACY_POLICY, trajectory_count=len(kept), trajectory_ids=legacy['retained_ids'])
        meta.pop('selection_mode')
        write(root/'experiment.json', meta); write(root/'selection.json', legacy)
        preprocessing.run(root)
        preprocessing.run(root)
        self.assertEqual(sorted(p.stem for p in (output/'trajectories').glob('*.json')), ['success-retry'])
        self.assertEqual(self.get('experiment?id='+e['id'])['selection'], legacy)

    def test_execution_record_v2_snapshot_keeps_infrastructure_record(self):
        original = self.workspace.records('fixture-v1')[0]
        infra = attempt('infra', result={
            'pass': False, 'scored': False, 'errorCode': 'command_exec_failed'})
        write(original.path.parent/infra.path.name, infra.data)
        e = self.post('experiment/create', {'kind': 'preprocess', 'title': 'Frozen v2',
            'dataset_id': 'fixture-v1',
            'config': {'deduplicate_observation': True, 'remove_source_lines': False}})
        root, output = self.workspace.paths(e['id'])
        kept, previous = select_records(load_trajectories(root/'inputs'), policy=PREVIOUS_POLICY)
        meta = read(root/'experiment.json')
        meta.update(selection_policy=PREVIOUS_POLICY, trajectory_count=len(kept),
                    trajectory_ids=previous['retained_ids'])
        write(root/'experiment.json', meta); write(root/'selection.json', previous)
        preprocessing.run(root)
        preprocessing.run(root)
        self.assertEqual(len(list((output/'trajectories').glob('*.json'))), 2)
        self.assertTrue((output/'trajectories/infra.json').exists())
        self.assertEqual(self.get('experiment?id='+e['id'])['selection'], previous)

    def test_infrastructure_only_selection_cannot_create_experiment(self):
        original = self.workspace.records('fixture-v1')[0]
        value = original.data
        value['metadata']['result'] = {'pass': False, 'scored': False,
                                      'errorCode': 'command_exec_failed'}
        write(original.path, value)
        body = {'kind': 'preprocess', 'title': 'Infra only', 'dataset_id': 'fixture-v1',
                'config': {'deduplicate_observation': True, 'remove_source_lines': False}}
        preview = self.post('experiment/preprocess-preview', body)
        self.assertEqual(preview['excluded_by_reason'], {'infrastructure_failure': 1})
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post('experiment/create', body)
        self.assertIn('当前结果条件下没有可处理轨迹', error.exception.read().decode())
        self.assertEqual(self.get('experiments'), [])

    def test_no_tools_or_reasoning_cannot_create_experiment(self):
        original = self.workspace.records('fixture-v1')[0]
        value = original.data
        for event in value['events']:
            event['tool_calls'] = []
            event['thought'] = ' \n '
        write(original.path, value)
        body = {'kind': 'preprocess', 'title': 'Text only', 'dataset_id': 'fixture-v1',
                'config': {'deduplicate_observation': True, 'remove_source_lines': False}}
        preview = self.post('experiment/preprocess-preview', body)
        self.assertEqual(preview['excluded_by_reason'], {'no_node_content': 1})
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post('experiment/create', body)
        self.assertIn('当前结果条件下没有可处理轨迹', error.exception.read().decode())
        self.assertEqual(self.get('experiments'), [])

    def test_execution_record_v3_snapshot_keeps_no_tool_record(self):
        original = self.workspace.records('fixture-v1')[0]
        no_tools = attempt('no-tools', with_tools=False)
        write(original.path.parent/no_tools.path.name, no_tools.data)
        e = self.post('experiment/create', {'kind': 'preprocess', 'title': 'Frozen v3',
            'dataset_id': 'fixture-v1',
            'config': {'deduplicate_observation': True, 'remove_source_lines': False}})
        root, output = self.workspace.paths(e['id'])
        kept, previous = select_records(load_trajectories(root/'inputs'), policy=INFRASTRUCTURE_POLICY)
        meta = read(root/'experiment.json')
        meta.update(selection_policy=INFRASTRUCTURE_POLICY, trajectory_count=len(kept),
                    trajectory_ids=previous['retained_ids'])
        write(root/'experiment.json', meta); write(root/'selection.json', previous)
        preprocessing.run(root)
        preprocessing.run(root)
        self.assertEqual(len(list((output/'trajectories').glob('*.json'))), 2)
        self.assertTrue((output/'trajectories/no-tools.json').exists())
        self.assertEqual(self.get('experiment?id='+e['id'])['selection'], previous)

    def test_execution_record_v4_snapshot_still_excludes_reasoning_only(self):
        original = self.workspace.records('fixture-v1')[0]
        no_tools = attempt('no-tools', with_tools=False)
        write(original.path.parent/no_tools.path.name, no_tools.data)
        e = self.post('experiment/create', {'kind': 'preprocess', 'title': 'Frozen v4',
            'dataset_id': 'fixture-v1',
            'config': {'deduplicate_observation': True, 'remove_source_lines': False}})
        root, output = self.workspace.paths(e['id'])
        kept, previous = select_records(load_trajectories(root/'inputs'), policy=TOOL_REQUIRED_POLICY)
        self.assertTrue(all('reasoning_events' not in row for row in previous['rows']))
        meta = read(root/'experiment.json')
        meta.update(selection_policy=TOOL_REQUIRED_POLICY, trajectory_count=len(kept),
                    trajectory_ids=previous['retained_ids'])
        write(root/'experiment.json', meta); write(root/'selection.json', previous)
        preprocessing.run(root)
        self.assertEqual(len(list((output/'trajectories').glob('*.json'))), 1)
        self.assertFalse((output/'trajectories/no-tools.json').exists())
        self.assertEqual(self.get('experiment?id='+e['id'])['selection'], previous)

    def test_old_snapshot_replays_original_selection(self):
        e = self.post('experiment/create', {'kind': 'preprocess', 'title': 'Historical',
            'dataset_id': 'fixture-v1', 'config': {'deduplicate_observation': True, 'remove_source_lines': False}})
        root, output = self.workspace.paths(e['id'])
        meta = read(root/'experiment.json'); meta.pop('selection_policy'); write(root/'experiment.json', meta)
        (root/'selection.json').unlink()
        preprocessing.run(root)
        self.assertEqual(read(output/'statistics.json')['trajectory_count'], 1)
        self.assertIsNone(self.get('experiment?id='+e['id'])['selection'])


if __name__ == '__main__':
    unittest.main()
