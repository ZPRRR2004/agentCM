"""Integration tests with an isolated, deterministic local HTTP model."""
import importlib.util
import json
import os
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
import copy
from workbench import splitting, preprocessing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from workbench.common import DISCOVERY, PROMPT_FILES, read, write
from workbench.server import make_server
from workbench.store import Workspace
from workbench.worker import WebFeedback
from dataset_fixture import create_catalog, add_official_fixture

spec = importlib.util.spec_from_file_location('predicate_fixture', DISCOVERY / 'tests/test_predicate_discovery.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'discovery'
        self.catalog_path = create_catalog(self.root / 'datasets', fixture.window)
        self.workspace = Workspace(self.root / 'workspace', discovery=self.source, catalog_path=self.catalog_path)
        self.server = make_server(0, self.workspace.data, self.workspace)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.token = self.get('bootstrap')['token']
        self.model_server = None

    def tearDown(self):
        self.workspace.shutdown()
        self.server.shutdown()
        self.server.server_close()
        if self.model_server:
            self.model_server.shutdown()
            self.model_server.server_close()
        self.temp.cleanup()

    def get(self, path):
        with self.opener.open(self.base + '/api/' + path) as response:
            return json.load(response)

    def test_health_is_lightweight_and_identifies_the_workspace(self):
        from unittest.mock import patch
        with patch.object(self.workspace, 'datasets', side_effect=AssertionError('Health must not scan datasets')):
            value = self.get('health')
        self.assertEqual(value['app'], 'agentcm-workbench')
        self.assertEqual(value['workspace'], str(self.workspace.data))
        self.assertEqual(value['pid'], os.getpid())
        self.assertNotIn('token', value)
        self.assertNotIn('settings', value)

    def post(self, path, body, token=None, origin=None):
        headers = {'Content-Type': 'application/json', 'X-Workspace-Token': self.token if token is None else token}
        if origin:
            headers['Origin'] = origin
        request = urllib.request.Request(self.base + '/api/' + path, json.dumps(body).encode(), headers)
        with self.opener.open(request) as response:
            return json.load(response)

    def completed_preprocess(self, dataset='fixture-v1'):
        e = self.post('experiment/create', {'kind': 'preprocess', 'title': 'Prepared '+dataset,
            'dataset_id': dataset, 'config': {'deduplicate_observation': False, 'remove_source_lines': False}})
        root, _ = self.workspace.paths(e['id'])
        preprocessing.run(root)
        return self.get('experiment?id='+e['id'])

    def split(self, dataset='fixture-v1', **changes):
        config = {'max_window_events':1, 'overlap_events':0,
                  'max_previous_summary_tokens':0, 'max_future_summary_tokens':0}
        config.update(changes)
        parent = WorkbenchTests.completed_preprocess(self, dataset)
        e = self.post('experiment/create', {'kind':'split','title':'Split '+dataset,
            'dataset_id':dataset,'preprocess_experiment_id':parent['id'],'config':config})
        self.post('experiment/start', {'id':e['id']})
        return self.wait_status(e['id'], 'completed')

    def create(self, **kwargs):
        source = self.split()
        batch = kwargs.pop('batch_size_override',2)
        return self.post('experiment/create', dict(title='Mechanism pilot', dataset_id='fixture-v1',
                                                  source_experiment_id=source['id'],
                                                  window_limit=3, batch_size=batch, max_retries=0, **kwargs))

    def model(self, fail=False, delay=0):
        model = fixture.Model(fail_comparison=fail)
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                if delay:
                    time.sleep(delay)
                try:
                    output = model(payload)
                    self.send_response(200)
                except Exception as exc:
                    output = {'error': str(exc)}
                    self.send_response(500)
                data = json.dumps(output).encode()
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        self.model_server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=self.model_server.serve_forever, daemon=True).start()
        self.post('settings', {'model': 'test-model', 'base_url': f'http://127.0.0.1:{self.model_server.server_port}',
                               'api_key': 'workbench-test-key'})
        return model

    def wait_status(self, identity, desired):
        deadline = time.monotonic() + 15
        value = None
        while time.monotonic() < deadline:
            value = self.get('experiment?id=' + identity)
            if value['status'] == desired:
                return value
            if value['status'] == 'failed' and desired != 'failed':
                self.fail(str(value['lifecycle']) + value.get('log', ''))
            time.sleep(.05)
        self.fail(f'Expected {desired}, got {value}')

    def test_flat_dataset_and_split_source_selection(self):
        datasets = self.get('bootstrap')['datasets']
        self.assertEqual([d['id'] for d in datasets], ['fixture-v1','alternative-v2'])
        self.assertNotIn('versions', datasets[0])
        self.assertEqual(len(self.get('trajectories?dataset=alternative-v2')),1)
        self.assertEqual(self.get('trajectory?dataset=alternative-v2&id=test-trajectory')['trajectory']['query']['title'], '测试数据集 B v2')
        source = self.split('alternative-v2')
        e = self.post('experiment/create', {'title':'B pilot','source_experiment_id':source['id'],'window_limit':1})
        self.assertEqual(e['dataset_id'],'alternative-v2')
        self.assertEqual(e['windows'][0]['title'],'测试数据集 B v2')
        self.assertEqual(e['source_experiment_id'],source['id'])
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create',{'title':'Mismatch','dataset_id':'fixture-v1','source_experiment_id':source['id']})
        self.catalog_path.unlink()
        self.assertEqual(self.get('experiment?id='+e['id'])['windows'][0]['title'],'测试数据集 B v2')
        self.assertEqual(self.get('experiment?id='+source['id'])['statistics']['window_count'],3)

    def test_official_tasks_are_browsable_and_require_execution_before_splitting(self):
        dataset = add_official_fixture(self.catalog_path)
        info = self.get('bootstrap')['datasets'][-1]
        self.assertEqual((info['task_count'], info['file_count']), (2, 10))
        self.assertEqual(info['trajectories'], [])
        self.assertEqual(info['format'], 'harbor-tasks')
        self.assertEqual(len(self.get('dataset-tasks?dataset='+dataset)), 2)
        task = self.get('dataset-task?dataset='+dataset+'&id=alpha-task')
        self.assertIn('<script>', task['instruction'])
        self.assertEqual(task['category'], 'test-category')
        self.assertEqual({f['path'] for f in task['files']},
                         {'instruction.md', 'task.toml', 'environment/fixture.txt',
                          'solution/fixture.txt', 'tests/fixture.txt'})
        self.assertEqual(self.get('trajectories?dataset='+dataset), [])
        with self.assertRaises(urllib.error.HTTPError):
            self.get('dataset-task?dataset='+dataset+'&id=../../settings.json')
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post('experiment/create', {'kind':'split','title':'Saved design','dataset_id':dataset,
                'config':{'max_window_events':1,'overlap_events':0,
                          'max_previous_summary_tokens':0,'max_future_summary_tokens':0}})
        self.assertIn('已完成的预处理实验', error.exception.read().decode())
        self.assertEqual(self.get('experiments'), [])
        self.assertEqual(self.workspace.processes, {})

    def test_historical_empty_draft_accepts_only_completed_preprocessing(self):
        parent = self.completed_preprocess()
        config = {'max_window_events':1,'overlap_events':0,
                  'max_previous_summary_tokens':0,'max_future_summary_tokens':0}
        draft = self.post('experiment/create', {'kind':'split','title':'Historical pending input',
            'dataset_id':'fixture-v1','preprocess_experiment_id':parent['id'],'config':config})
        root, _ = self.workspace.paths(draft['id'])
        meta = read(root/'experiment.json')
        for key in list(meta):
            if key.startswith('preprocess_'): meta.pop(key)
        meta.update(input_state='awaiting_input',input_hash='',trajectory_ids=[],trajectory_count=0)
        write(root/'experiment.json',meta)
        for path in (root/'inputs').glob('*.json'): path.unlink()
        for extra in ({}, {'preprocess_experiment_id':parent['id'],'trajectory_ids':['wrong-task']}):
            with self.assertRaises(urllib.error.HTTPError):
                self.post('experiment/input-attach', {'id':draft['id'], **extra})
        ready = self.post('experiment/input-attach', {'id':draft['id'],
            'preprocess_experiment_id':parent['id'], 'trajectory_ids':['test-trajectory']})
        self.assertEqual(ready['input_state'], 'ready')
        self.assertEqual(ready['config'], config)
        self.assertEqual(ready['prompt_hash'], draft['prompt_hash'])
        self.assertEqual(ready['preprocess_experiment_id'],parent['id'])
        self.assertEqual(ready['trajectory_count'], 1)
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/input-attach', {'id':draft['id'],'preprocess_experiment_id':parent['id']})
        (self.catalog_path.parent / 'fixture-v1/normalized/test-trajectory.json').unlink()
        self.post('experiment/delete', {'id':parent['id']})
        self.post('experiment/start', {'id':draft['id']})
        finished = self.wait_status(draft['id'], 'completed')
        self.assertEqual(finished['statistics']['window_count'], 3)
        self.assertEqual(finished['input_hash'], ready['input_hash'])

    def test_official_task_count_and_pinned_commit_are_checked(self):
        dataset = add_official_fixture(self.catalog_path)
        catalog = read(self.catalog_path)
        catalog['datasets'][-1]['expected_tasks'] = 3
        write(self.catalog_path, catalog)
        with self.assertRaises(urllib.error.HTTPError):
            self.get('dataset-tasks?dataset='+dataset)
        catalog['datasets'][-1]['expected_tasks'] = 2
        catalog['datasets'][-1]['source']['commit'] = 'c' * 40
        write(self.catalog_path, catalog)
        with self.assertRaises(urllib.error.HTTPError):
            self.get('bootstrap')

    def test_split_parameters_required_and_predicate_requires_completed_source(self):
        base={'kind':'split','title':'Validation','dataset_id':'fixture-v1'}
        for config in ({}, {'max_window_events':2}, {'max_window_events':True,
                'overlap_events':0,'max_previous_summary_tokens':0,'max_future_summary_tokens':0}):
            with self.assertRaises(urllib.error.HTTPError):
                self.post('experiment/create',{**base,'config':config})
        self.assertEqual(self.get('experiments'),[])
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create',{'title':'No source','dataset_id':'fixture-v1'})
        base['preprocess_experiment_id']=self.completed_preprocess()['id']
        draft=self.post('experiment/create',{**base,'config':{'max_window_events':1,
            'overlap_events':0,'max_previous_summary_tokens':0,'max_future_summary_tokens':0}})
        self.assertEqual(draft['windows'],[])
        root,_=self.workspace.paths(draft['id'])
        self.assertFalse((root/'output/windows').exists())
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create',{'title':'Incomplete','source_experiment_id':draft['id']})
        with self.assertRaises(urllib.error.HTTPError):
            self.get('windows?dataset=fixture-v1')

    def test_split_parameters_change_windows_and_preserve_event_coverage(self):
        a=self.split(max_window_events=1)
        b=self.split(max_window_events=2,overlap_events=1)
        self.assertEqual((a['produced_windows'],b['produced_windows']),(3,2))
        self.assertEqual(a['input_hash'],b['input_hash'])
        windows=[self.get('window?experiment='+b['id']+'&id='+w['id'])['window'] for w in b['windows']]
        self.assertEqual([ev['event_id'] for w in windows for ev in w['core']['events']],['event-1','event-2','event-3'])
        self.assertEqual(windows[1]['overlap']['event_ids'],['event-2'])
        self.assertEqual(b['statistics']['core_events'],3)
        record=self.workspace.records('fixture-v1')[0]
        original=read(record.path)
        original['events'][0]['thought']='Long observation ' * 20000
        write(record.path, original)
        long=self.split(max_window_events=2)
        self.assertEqual(long['produced_windows'],2)
        self.assertGreater(long['statistics']['max_core_tokens'],6000)

    def test_split_summary_failure_resume_reuses_completed_windows(self):
        config={'max_window_events':1,'overlap_events':0,
                'max_previous_summary_tokens':0,'max_future_summary_tokens':32}
        e=self.post('experiment/create',{'kind':'split','title':'Resume summaries','dataset_id':'fixture-v1',
            'preprocess_experiment_id':self.completed_preprocess()['id'],'config':config})
        root,output=self.workspace.paths(e['id'])
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/start',{'id':e['id']})
        calls=[]
        def transport(payload):
            calls.append(payload)
            if len(calls)==2: raise RuntimeError('Synthetic summary failure')
            return {'choices':[{'finish_reason':'stop','message':{'content':'The agent verifies the result.'}}]}
        with self.assertRaisesRegex(RuntimeError,'Synthetic'):
            splitting.run(root,transport)
        saved=output/'windows/test-trajectory__window_0001.json'
        old=saved.read_bytes()
        splitting.run(root,transport)
        self.assertEqual(saved.read_bytes(),old)
        self.assertEqual(len(calls),3)
        self.assertEqual(read(output/'execution_state.json')['status'],'completed')
        self.assertEqual(self.workspace.experiment(e['id'])['produced_windows'],3)

    def test_preview_matches_execution_without_creating_outputs(self):
        body={'dataset_id':'fixture-v1','trajectory_ids':['test-trajectory'],
              'preprocess_experiment_id':self.completed_preprocess()['id'],
              'config':{'max_window_events':2,'overlap_events':1}}
        before={str(p):p.read_bytes() for p in self.workspace.data.rglob('*') if p.is_file()}
        preview=self.post('experiment/split-preview',body)
        after={str(p):p.read_bytes() for p in self.workspace.data.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
        self.assertEqual(self.workspace.processes,{})
        self.assertEqual(preview['event_histogram'],[{'events':1,'windows':1},{'events':2,'windows':1}])
        self.assertEqual(sum(b['core_count'] for b in preview['token_histogram']),2)
        self.assertEqual(sum(b['context_count'] for b in preview['token_histogram']),2)
        core_lengths = [w['core_tokens'] for w in preview['longest_windows']]
        self.assertEqual(preview['core_tokens']['median'],sum(core_lengths)/2)
        complete=self.split(max_window_events=2,overlap_events=1)
        self.assertEqual(complete['algorithm'],'event-count/v2')
        self.assertNotIn('max_window_tokens',complete['config'])
        self.assertEqual(preview['window_count'],complete['produced_windows'])
        self.assertEqual(preview['input_hash'],complete['input_hash'])
        self.assertEqual(preview['context_tokens']['max'],complete['statistics']['max_context_tokens'])
        windows=[self.get('window?experiment='+complete['id']+'&id='+w['id'])['window'] for w in complete['windows']]
        for item in preview['longest_windows']:
            window=next(w for w in windows if w['window_id']==item['window_id'])
            self.assertEqual(item['core_tokens'],window['metadata']['core_tokens'])
            self.assertEqual(item['context_tokens'],window['metadata']['context_tokens'])

    def test_preview_tracks_selection_overlap_and_validates_parameters(self):
        body={'dataset_id':'fixture-v1','trajectory_ids':['test-trajectory'],
              'preprocess_experiment_id':self.completed_preprocess()['id'],
              'config':{'max_window_events':2,'overlap_events':0}}
        baseline=self.post('experiment/split-preview',body)
        body['config']['overlap_events']=2
        overlap=self.post('experiment/split-preview',body)
        self.assertEqual(baseline['core_tokens'],overlap['core_tokens'])
        self.assertEqual(baseline['event_histogram'],overlap['event_histogram'])
        self.assertGreater(overlap['context_tokens']['max'],baseline['context_tokens']['max'])
        body['config']['max_window_events']=1
        self.assertEqual(self.post('experiment/split-preview',body)['window_count'],3)
        source=self.workspace.records('fixture-v1')[0]
        second=copy.deepcopy(source.data); second['metadata']['attempt_index']=2
        write(source.path.with_name('second.json'),second)
        body['preprocess_experiment_id']=self.completed_preprocess()['id']
        body['trajectory_ids'].append('second')
        self.assertEqual(self.post('experiment/split-preview',body)['window_count'],6)
        for config in ({'max_window_events':0,'overlap_events':0},
                       {'max_window_events':True,'overlap_events':0},
                       {'max_window_events':2,'overlap_events':-1},
                       {'max_window_events':2,'overlap_events':0,'max_window_tokens':6000}):
            with self.assertRaises(urllib.error.HTTPError):
                self.post('experiment/split-preview',{**body,'config':config})
        for ids in ([],['unknown']):
            with self.assertRaises(urllib.error.HTTPError):
                self.post('experiment/split-preview',{**body,'trajectory_ids':ids})
        self.assertTrue(all(e['kind']=='preprocess' for e in self.get('experiments')))
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create',{'kind':'split','title':'Removed parameter','dataset_id':'fixture-v1',
                'config':{'max_window_events':2,'overlap_events':0,'max_previous_summary_tokens':0,
                          'max_future_summary_tokens':0,'max_window_tokens':6000}})

    def test_legacy_snapshots_retain_original_boundaries(self):
        draft=self.post('experiment/create',{'kind':'split','title':'Historical snapshot','dataset_id':'fixture-v1',
            'preprocess_experiment_id':self.completed_preprocess()['id'],
            'config':{'max_window_events':2,'overlap_events':0,'max_previous_summary_tokens':0,'max_future_summary_tokens':0}})
        root,output=self.workspace.paths(draft['id'])
        meta=read(root/'experiment.json')
        for key in list(meta):
            if key.startswith('preprocess_'): meta.pop(key)
        meta['algorithm']='event-greedy/v1'
        meta['config']['max_window_tokens']=1
        write(root/'experiment.json',meta)
        splitting.run(root)
        self.assertEqual(read(output/'statistics.json')['window_count'],3)
        self.assertTrue(all(read(p)['metadata']['oversized'] for p in (output/'windows').glob('*.json')))

    def test_split_input_snapshot_and_downstream_hash_guard(self):
        source=self.split()
        record=self.workspace.records('fixture-v1')[0]
        record.path.write_text('{}')
        e=self.post('experiment/create',{'title':'Independent snapshot','source_experiment_id':source['id']})
        self.assertEqual(e['window_count'],3)
        _,output=self.workspace.paths(source['id'])
        window=next((output/'windows').glob('*.json'))
        value=read(window);value['user_query']['title']='Edited';write(window,value)
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create',{'title':'Changed output','source_experiment_id':source['id']})

    def test_catalog_path_guard_and_no_legacy_experiment_import(self):
        legacy = self.source / 'runs/old/build_edges'
        write(legacy / 'edge_type_registry.json', [{'name': 'OLD_RELATION'}])
        self.assertEqual(self.get('experiments'), [])
        with self.assertRaises(urllib.error.HTTPError):
            self.get('experiment?id=history-old')
        catalog = read(self.catalog_path)
        catalog['datasets'][0]['normalized_path'] = '../outside'
        write(self.catalog_path, catalog)
        with self.assertRaises(urllib.error.HTTPError):
            self.get('trajectories?dataset=fixture-v1')

    def test_snapshots_are_isolated_and_settings_display_saved_key(self):
        saved = self.post('settings', {'api_key': 'workbench-test-key', 'model': 'test-model', 'base_url': 'https://api.deepseek.com'})
        self.assertEqual(saved['api_key'], 'workbench-test-key')
        self.assertTrue(saved['key_configured'])
        e = self.create()
        root, _ = self.workspace.paths(e['id'])
        self.assertEqual(len(list((root / 'inputs').glob('*.json'))), 3)
        self.assertEqual(len(list((root / 'prompts').glob('*/*.txt'))), len(PROMPT_FILES))
        old = (root / 'prompts/discovery/system.txt').read_text()
        prompts = self.get('prompts')['files']
        prompts['discovery/system.txt'] += '\nA controlled test change.'
        self.post('prompts', {'files': prompts})
        self.assertEqual((root / 'prompts/discovery/system.txt').read_text(), old)
        self.assertEqual(self.get('bootstrap')['settings']['api_key'], 'workbench-test-key')
        self.assertNotIn('workbench-test-key', (root / 'experiment.json').read_text())
        self.assertEqual(os.stat(self.workspace.data / 'settings.json').st_mode & 0o777, 0o600)

    def test_real_subprocess_pipeline_feedback_and_resume_after_stop(self):
        model = self.model()
        e = self.create()
        identity = e['id']
        self.post('experiment/start', {'id': identity})
        waiting = self.wait_status(identity, 'waiting')
        self.assertEqual(waiting['completed'], 2)
        self.assertEqual(waiting['registry_count'], 4)
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/start', {'id': identity})
        self.post('review', {'id': identity, 'name': 'USES', 'decision': 'revise', 'notes': 'Rename to USES_INFORMATION'})
        old_token = waiting['pending']['token']
        self.post('experiment/stop', {'id': identity})
        self.wait_status(identity, 'stopped')
        self.post('experiment/start', {'id': identity})
        waiting = self.wait_status(identity, 'waiting')
        self.assertNotEqual(old_token, waiting['pending']['token'])
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/feedback', {'id': identity, 'token': old_token, 'feedback': ''})
        self.post('experiment/feedback', {'id': identity, 'token': waiting['pending']['token'],
                                          'feedback': 'Rename USES to USES_INFORMATION.'})
        done = self.wait_status(identity, 'completed')
        self.assertEqual(done['completed'], 3)
        self.assertIn('USES_INFORMATION', {p['name'] for p in done['registry']})
        self.assertEqual(model.stages.count('discovery'), 3)
        self.assertEqual(model.stages.count('registry_revision'), 1)
        self.assertNotIn('workbench-test-key', json.dumps(done))
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/feedback', {'id': identity, 'token': waiting['pending']['token'], 'feedback': ''})

    def test_background_run_completes_after_last_page_closes(self):
        model = self.model(delay=.15)
        identity = self.create(batch_size_override=100)['id']
        self.server.shutdown()
        self.server.server_close()
        self.server = make_server(0, self.workspace.data, self.workspace, idle_timeout=.05, startup_timeout=10)
        def serve_until_idle():
            try:
                self.server.serve_forever(.02)
            finally:
                with self.workspace.lock:
                    self.workspace.shutdown()
        self.thread = threading.Thread(target=serve_until_idle, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.get('bootstrap')['token']
        with self.opener.open(self.base + '/api/session/events?id=page&token=' + self.token) as page:
            self.post('experiment/start', {'id': identity})
            self.post('session/close', {'id': 'page'})
        time.sleep(.25)
        self.assertTrue(self.thread.is_alive())
        self.assertIsNone(self.workspace.processes[identity].poll())
        self.thread.join(10)
        self.assertFalse(self.thread.is_alive())
        completed = self.workspace.experiment(identity)
        self.assertEqual(completed['status'], 'completed')
        self.assertEqual(completed['completed'], 3)
        self.assertEqual(self.workspace.processes[identity].poll(), 0)
        self.assertEqual(model.stages.count('discovery'), 3)

    def test_service_shutdown_stops_workers_and_keeps_saved_progress(self):
        model = self.model()
        identity = self.create()['id']
        self.post('experiment/start', {'id': identity})
        waiting = self.wait_status(identity, 'waiting')
        worker = self.workspace.processes[identity]
        with self.workspace.lock:
            self.workspace.shutdown()
        self.assertIsNotNone(worker.poll())
        stopped = self.get('experiment?id=' + identity)
        self.assertEqual(stopped['status'], 'stopped')
        self.assertEqual(stopped['completed'], waiting['completed'])
        self.assertEqual(stopped['registry'], waiting['registry'])
        self.post('experiment/start', {'id': identity})
        resumed = self.wait_status(identity, 'waiting')
        self.post('experiment/feedback', {'id': identity, 'token': resumed['pending']['token'], 'feedback': ''})
        self.wait_status(identity, 'completed')
        self.assertEqual(model.stages.count('discovery'), 3)

    def test_closing_server_rejects_new_experiment_starts(self):
        identity = self.create()['id']
        self.workspace.closing = True
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post('experiment/start', {'id': identity})
        self.assertEqual(error.exception.code, 400)
        self.assertIn('工作台正在停止', json.load(error.exception)['error'])
        self.assertNotIn(identity, self.workspace.processes)
        self.assertEqual(self.get('experiment?id=' + identity)['status'], 'draft')

    def test_failure_resume_does_not_repeat_completed_stage(self):
        model = self.model(fail=True)
        identity = self.create()['id']
        self.post('experiment/start', {'id': identity})
        failed = self.wait_status(identity, 'failed')
        self.assertEqual(failed['state']['next_stage'], 'comparison')
        self.post('experiment/start', {'id': identity})
        waiting = self.wait_status(identity, 'waiting')
        self.post('experiment/feedback', {'id': identity, 'token': waiting['pending']['token'], 'feedback': ''})
        self.wait_status(identity, 'completed')
        self.assertEqual(model.stages.count('discovery'), 3)

    def test_multiple_feedback_batches_and_stale_review(self):
        self.model()
        identity = self.create(batch_size_override=1)['id']
        self.post('experiment/start', {'id': identity})
        first = self.wait_status(identity, 'waiting')
        self.post('review', {'id': identity, 'name': 'USES', 'decision': 'keep', 'notes': 'First version'})
        self.post('experiment/feedback', {'id': identity, 'token': first['pending']['token'], 'feedback': ''})
        deadline = time.monotonic() + 10
        second = first
        while time.monotonic() < deadline:
            second = self.get('experiment?id=' + identity)
            if second['status'] == 'waiting' and second['batch'] == 2:
                break
            time.sleep(.05)
        self.assertEqual(second['batch'], 2)
        self.assertTrue(second['reviews']['USES']['stale'])
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/feedback', {'id': identity, 'token': first['pending']['token'], 'feedback': ''})
        self.post('experiment/feedback', {'id': identity, 'token': second['pending']['token'], 'feedback': ''})
        self.wait_status(identity, 'completed')

    def test_workspace_server_lock(self):
        with self.assertRaisesRegex(ValueError, '已经有运行中的工作台'):
            make_server(0, self.workspace.data)

    def test_queued_feedback_survives_restart_before_pipeline_commit(self):
        root = self.root / 'queued'
        write(root / 'output/execution_state.json', {'current_batch_index': 1})
        write(root / 'pending_feedback.json', {'token': 'one', 'batch': 1})
        write(root / 'feedback.json', {'token': 'one', 'text': 'Keep the mechanism explicit.'})
        self.assertEqual(WebFeedback(root)(), 'Keep the mechanism explicit.')
        restarted = WebFeedback(root)
        self.assertEqual(restarted(), 'Keep the mechanism explicit.')
        self.assertEqual(restarted(), 'END')

    def test_host_origin_token_and_path_guards(self):
        for kwargs in ({'token': 'bad'}, {'origin': 'https://example.org'}):
            with self.assertRaises(urllib.error.HTTPError) as caught:
                self.post('task', {'title': 'Bad request'}, **kwargs)
            self.assertEqual(caught.exception.code, 403)
        req = urllib.request.Request(self.base + '/api/bootstrap', headers={'Host': 'evil.example'})
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.opener.open(req)
        self.assertEqual(caught.exception.code, 403)
        with self.assertRaises(urllib.error.HTTPError):
            self.get('experiment?id=../../settings.json')
        with self.assertRaises(urllib.error.HTTPError):
            self.post('experiment/create', {'title': 'Bad', 'dataset_id': '../fixture'})

    def test_task_persistence_and_prompt_validation(self):
        tasks = self.post('task', {'title': '<script>research</script>', 'notes': 'Evidence', 'status': 'doing'})
        task = tasks[0]
        self.post('task', {'id': task['id'], 'status': 'review'})
        reopened = Workspace(self.workspace.data, discovery=self.source, catalog_path=self.catalog_path)
        self.assertEqual(read(reopened.data / 'tasks.json')[0]['status'], 'review')
        prompts = self.get('prompts')['files']
        prompts['discovery/user.txt'] = 'Missing the required variable'
        with self.assertRaises(urllib.error.HTTPError):
            self.post('prompts', {'files': prompts})
        self.assertIn('{{context_window}}', self.get('prompts')['files']['discovery/user.txt'])


if __name__ == '__main__':
    unittest.main()
