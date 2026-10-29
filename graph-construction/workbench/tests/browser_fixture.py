"""Disposable UI sandbox: synthetic inputs and a local deterministic model."""
import importlib.util
import json
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workbench.common import DISCOVERY, write
from workbench.server import make_server
from workbench.store import Workspace
from dataset_fixture import create_catalog, add_official_fixture

spec = importlib.util.spec_from_file_location('fixture', DISCOVERY / 'tests/test_predicate_discovery.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
model = fixture.Model(fail_comparison='--progress' in sys.argv)


class ModelHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if '--progress' in sys.argv:
            time.sleep(1.4)
        try:
            answer = model(data)
            response = json.dumps(answer).encode()
            self.send_response(200)
        except Exception as exc:
            response = json.dumps({'error': str(exc)}).encode()
            self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)


with tempfile.TemporaryDirectory(prefix='agentcm-ui-test-') as temporary:
    root = Path(temporary)
    discovery = root / 'discovery'
    catalog_path = create_catalog(root / 'datasets', fixture.window)
    add_official_fixture(catalog_path)
    if '--preprocess' in sys.argv or '--selection' in sys.argv:
        from test_preprocessing import enrich
        for path in (root / 'datasets').glob('*/normalized/*.json'):
            write(path, enrich(json.loads(path.read_text())))
    if '--selection' in sys.argv:
        import copy
        directory = root / 'datasets/fixture-v1/normalized'
        original = json.loads((directory/'test-trajectory.json').read_text())
        original['metadata']['attempt_index'] = 1
        write(directory/'test-trajectory.json', original)
        for name, passed, scored, index in [('success-retry', True, True, 2),
                ('failed-last', False, True, 3), ('unscored', False, False, 4),
                ('failed-no-tools', False, True, 5), ('empty-content', False, True, 6)]:
            value = copy.deepcopy(original)
            value['metadata'].update(attempt_index=index, result={'pass': passed, 'scored': scored})
            if name == 'unscored':
                value['metadata']['result']['errorCode'] = 'command_exec_failed'
            if name in ('unscored', 'failed-no-tools', 'empty-content'):
                for event in value['events']:
                    event['tool_calls'] = []
                    if name == 'empty-content':
                        event['thought'] = ' \n '
            write(directory/(name+'.json'), value)
        write(directory/'zz-duplicate-import.json', original)
    model_server = ThreadingHTTPServer(('127.0.0.1', 0), ModelHandler)
    threading.Thread(target=model_server.serve_forever, daemon=True).start()
    workspace = Workspace(root / 'workspace', discovery=discovery, catalog_path=catalog_path)
    workspace.save_settings({'model': 'local-test-model', 'api_key': 'test-key-local-only',
                             'base_url': f'http://127.0.0.1:{model_server.server_port}'})
    session_options = {'idle_timeout': 1, 'startup_timeout': 30} if '--on-demand' in sys.argv else {}
    server = make_server(0, workspace.data, workspace, **session_options)
    print(json.dumps({'url': f'http://127.0.0.1:{server.server_port}', 'catalog_path': str(catalog_path)}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        workspace.shutdown()
        server.server_close()
        model_server.shutdown()
        model_server.server_close()
