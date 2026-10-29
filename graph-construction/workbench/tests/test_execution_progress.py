"""Progress reflects real requests, persisted results, and human feedback."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import test_workbench as support
from workbench.common import read
from workbench.execution_progress import ExecutionProgress
from workbench.worker import run
from src.discover_predicates.llm_client import PredicateDiscoveryLLM


class ProgressEventsTests(unittest.TestCase):
    def test_wait_is_persisted_before_transport_and_invalid_result_retries(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()) as output:
            root = Path(temporary)
            progress = ExecutionProgress(root)
            progress('started', message='开始运行')
            seen = []
            def transport(payload):
                latest = read(root / 'execution.json')
                self.assertEqual(latest['event'], 'model_wait')
                self.assertEqual(latest['stage'], 'discovery')
                self.assertTrue(latest['waiting_since'])
                seen.append(latest['attempt'])
                return {'choices': [{'finish_reason': 'stop', 'message': {
                    'content': 'invalid JSON' if len(seen) == 1 else '{"ok":true}'}}]}
            llm = PredicateDiscoveryLLM(root / 'output', transport=transport,
                                       max_retries=1, progress=progress)
            parsed, record = llm.call(stage='discovery', window_name='example',
                prompt_version='test', system='test', user='test', validator=lambda value: None)
            self.assertEqual(parsed, {'ok': True})
            self.assertEqual(seen, [1, 2])
            self.assertEqual(read(root / 'execution.json')['event'], 'model_done')
            self.assertIn('即将重试', output.getvalue())
            self.assertIn('正在检查结果格式', output.getvalue())
            self.assertLessEqual(record['attempts'][0]['started_at'], record['completed_at'])

    def test_error_redaction_and_new_run_identity(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'private-test-key'}):
            root = Path(temporary)
            first = ExecutionProgress(root)
            with contextlib.redirect_stdout(io.StringIO()) as output:
                first('failed', message='request failed: private-test-key')
            self.assertNotIn('private-test-key', (root / 'execution.json').read_text())
            self.assertNotIn('private-test-key', output.getvalue())
            second = ExecutionProgress(root)
            self.assertNotEqual(first.current['run_id'], second.current['run_id'])


class ProgressIntegrationTests(unittest.TestCase):
    setUp = support.WorkbenchTests.setUp
    tearDown = support.WorkbenchTests.tearDown
    get = support.WorkbenchTests.get
    post = support.WorkbenchTests.post
    model = support.WorkbenchTests.model
    split = support.WorkbenchTests.split
    create = support.WorkbenchTests.create
    wait_status = support.WorkbenchTests.wait_status

    def test_window_progress_waiting_feedback_revision_and_completion(self):
        self.model()
        identity = self.create()['id']
        self.post('experiment/start', {'id': identity})
        waiting = self.wait_status(identity, 'waiting')
        self.assertEqual(waiting['execution']['event'], 'human_wait')
        self.assertEqual(waiting['execution']['window_number'], 2)
        self.assertIn('第 2/3 个窗口已保存', waiting['log'])
        self.assertIn('等待你在网页提交审核意见', waiting['log'])
        self.post('experiment/feedback', {'id': identity, 'token': waiting['pending']['token'],
                                          'feedback': 'Rename USES to USES_INFORMATION.'})
        done = self.wait_status(identity, 'completed')
        # Completion state is written immediately before the worker's final event.
        self.workspace.processes[identity].wait(timeout=3)
        done = self.get('experiment?id=' + identity)
        self.assertEqual(done['execution']['event'], 'completed')
        self.assertIn('根据你的反馈修改谓词库', done['log'])
        self.assertIn('第 3/3 个窗口已保存', done['log'])
        self.assertNotIn('workbench-test-key', json.dumps(done))

    def test_failed_then_resumed_run_keeps_log_and_skips_saved_stage(self):
        model = self.model(fail=True)
        identity = self.create(batch_size_override=100)['id']
        self.post('experiment/start', {'id': identity})
        failed = self.wait_status(identity, 'failed')
        self.assertEqual(failed['execution']['event'], 'failed')
        self.assertIn('与已有谓词比较', failed['log'])
        previous_run = failed['execution']['run_id']
        self.post('experiment/start', {'id': identity})
        self.wait_status(identity, 'completed')
        self.workspace.processes[identity].wait(timeout=3)
        done = self.get('experiment?id=' + identity)
        self.assertNotEqual(done['execution']['run_id'], previous_run)
        self.assertIn('运行失败', done['log'])
        self.assertIn('实验已完成', done['log'])
        self.assertEqual(model.stages.count('discovery'), 3)

    def test_local_preprocessing_and_splitting_report_saved_outputs(self):
        e = self.post('experiment/create', {'kind': 'preprocess', 'title': 'Local progress',
            'dataset_id': 'fixture-v1', 'config': {'deduplicate_observation': False,
                                                 'remove_source_lines': False}})
        root, _ = self.workspace.paths(e['id'])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            run(root)
        self.assertEqual(read(root / 'execution.json')['event'], 'completed')
        self.assertIn('预处理第 1/1 条轨迹', output.getvalue())
        self.assertIn('已保存第 1/1 条轨迹', output.getvalue())
        split = self.split()
        self.workspace.processes[split['id']].wait(timeout=3)
        split = self.get('experiment?id=' + split['id'])
        self.assertEqual(split['execution']['event'], 'completed')
        self.assertIn('累计 3 个窗口', split['log'])
