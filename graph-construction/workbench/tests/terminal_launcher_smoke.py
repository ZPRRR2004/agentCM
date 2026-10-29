"""Real terminal close, page-close independence and resumable local-model work."""
import json
import os
from pathlib import Path
import pty
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from test_workbench import fixture
from dataset_fixture import create_catalog
from workbench.common import read
from workbench.store import Workspace
from workbench import preprocessing, splitting


def main():
    with tempfile.TemporaryDirectory(prefix='agentcm-terminal-test-') as directory:
        base = Path(directory)
        data = base / 'workspace'
        catalog = create_catalog(base / 'datasets', fixture.window)
        workspace = Workspace(data, discovery=base/'discovery', catalog_path=catalog)
        pre = workspace.create({'kind': 'preprocess', 'title': 'Prepared', 'dataset_id': 'fixture-v1',
                                'config': {'deduplicate_observation': False, 'remove_source_lines': False}})
        preprocessing.run(workspace.paths(pre['id'])[0])
        split = workspace.create({'kind': 'split', 'title': 'Split', 'dataset_id': 'fixture-v1',
            'preprocess_experiment_id': pre['id'], 'config': {'max_window_events': 1,
                'overlap_events': 0, 'max_previous_summary_tokens': 0, 'max_future_summary_tokens': 0}})
        splitting.run(workspace.paths(split['id'])[0])
        model = fixture.Model()
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                raw = json.dumps(model(payload)).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(raw)
        model_server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        workspace.save_settings({'model': 'local-test-model', 'api_key': 'test-key-local-only',
                                'base_url': f'http://127.0.0.1:{model_server.server_port}'})
        experiment = workspace.create({'title': 'Terminal close and resume',
                                       'source_experiment_id': split['id'], 'batch_size': 2})
        with socket.socket() as candidate:
            candidate.bind(('127.0.0.1', 0))
            port = candidate.getsockname()[1]
        url = f'http://127.0.0.1:{port}/api/'
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        def get(route):
            with opener.open(url + route, timeout=2) as response:
                return json.load(response)
        token = ''
        def post(route, payload):
            request = urllib.request.Request(url + route, json.dumps(payload).encode(),
                {'Content-Type': 'application/json', 'X-Workspace-Token': token})
            with opener.open(request, timeout=5) as response:
                return json.load(response)
        def until(check, timeout=15):
            end = time.monotonic() + timeout
            while time.monotonic() < end:
                try:
                    result = check()
                    if result:
                        return result
                except (OSError, ValueError):
                    pass
                time.sleep(.1)
            raise AssertionError('Timed out waiting for terminal lifecycle')
        def stopped():
            try:
                get('health')
                return False
            except OSError:
                return True
        # Fork before starting any threads. The child immediately execs the real Finder entry.
        child, terminal = pty.fork()
        if child == 0:
            os.execv('/bin/bash', ['/bin/bash', str(ROOT/'open-workbench.command'),
                '--no-open', '--port', str(port), '--data-dir', str(data)])
        threading.Thread(target=model_server.serve_forever, daemon=True).start()
        restarted = None
        try:
            health = until(lambda: get('health'))
            assert health['pid'] == child and health['session_mode'] == 'terminal'
            token = get('bootstrap')['token']
            post('session/close', {'id': 'closed-test-page'})
            # Cross the old 30-second page-close deadline with no experiment running.
            time.sleep(31)
            assert get('health')['pid'] == child
            duplicate = subprocess.run([sys.executable, str(ROOT/'launch.py'), '--no-open',
                '--port', str(port), '--data-dir', str(data)], capture_output=True, text=True, timeout=10)
            assert duplicate.returncode == 0 and '原来的启动终端' in duplicate.stdout
            assert get('health')['pid'] == child
            print('PASS: terminal owns service; closing page and duplicate launch preserve it', flush=True)

            post('experiment/start', {'id': experiment['id']})
            waiting = until(lambda: (value if (value := get('experiment?id='+experiment['id']))['status'] == 'waiting' else None))
            assert waiting['completed'] == 2
            workers = subprocess.check_output(['/bin/ps', '-axo', 'pid=,args='], text=True)
            worker_ids = [int(line.split()[0]) for line in workers.splitlines()
                          if 'workbench.worker' in line and str(data/'experiments'/experiment['id']) in line]
            assert len(worker_ids) == 1
            os.close(terminal)
            terminal = None
            ended = until(lambda: (result if (result := os.waitpid(child, os.WNOHANG))[0] else None))
            assert os.waitstatus_to_exitcode(ended[1]) == 0
            child = None
            until(stopped)
            for pid in worker_ids:
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    continue
                raise AssertionError('Worker outlived its terminal')
            state = read(data/'experiments'/experiment['id']/'lifecycle.json')
            assert state['status'] == 'stopped'
            assert read(data/'experiments'/experiment['id']/'output/execution_state.json')['completed_windows'] == 2
            print('PASS: closing the actual terminal stops server and worker, preserving two windows', flush=True)

            with (base/'restart.log').open('wb') as log:
                restarted = subprocess.Popen([sys.executable, str(ROOT/'run.py'), '--port', str(port),
                    '--data-dir', str(data), '--startup-timeout', '.1'],
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
            until(lambda: get('health'))
            time.sleep(.3)
            assert get('health')['session_mode'] == 'terminal'
            token = get('bootstrap')['token']
            post('experiment/start', {'id': experiment['id']})
            resumed = until(lambda: (value if (value := get('experiment?id='+experiment['id']))['status'] == 'waiting' else None))
            post('experiment/feedback', {'id': experiment['id'], 'token': resumed['pending']['token'], 'feedback': ''})
            until(lambda: get('experiment?id='+experiment['id'])['status'] == 'completed')
            assert model.stages.count('discovery') == 3
            restarted.send_signal(signal.SIGINT)
            assert restarted.wait(timeout=10) == 0
            until(stopped)
            print('PASS: direct command stays open without pages; resume finishes once; Ctrl+C stops service', flush=True)
        finally:
            if terminal is not None:
                os.close(terminal)
            if child:
                try:
                    os.kill(child, signal.SIGTERM)
                    os.waitpid(child, 0)
                except ProcessLookupError:
                    pass
            if restarted and restarted.poll() is None:
                restarted.terminate()
                restarted.wait(timeout=15)
            model_server.shutdown()
            model_server.server_close()


if __name__ == '__main__':
    main()
