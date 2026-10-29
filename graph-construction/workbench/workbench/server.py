"""Loopback-only JSON API and static application server."""
import json
import fcntl
import mimetypes
import os
import re
import select
import secrets
import signal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .common import PROMPTS, ROOT, PromptManager, read, write
from .store import Workspace
from . import splitting, preprocessing, experiment_lifecycle
from .split_preview import preview as split_preview
from .browser_sessions import BrowserSessions


def make_server(port, data_dir, workspace=None, *, idle_timeout=None, startup_timeout=120, session_mode='manual'):
    workspace = workspace or Workspace(data_dir)
    token = secrets.token_urlsafe(32)
    sessions = BrowserSessions(idle_timeout, startup_timeout) if idle_timeout is not None else None
    mode = 'on-demand' if sessions else session_mode

    def session_id(value):
        if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9-]{1,100}', value):
            raise ValueError('页面标识无效')
        return value

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, data, status=200, kind='application/json; charset=utf-8'):
            raw = json.dumps(data, ensure_ascii=False).encode() if kind.startswith('application/json') else data
            self.send_response(status)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(raw)

        def check_host(self):
            host = self.headers.get('Host', '')
            valid = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            if host not in valid:
                raise PermissionError('仅接受本机访问')
            origin = self.headers.get('Origin')
            if origin and origin not in {'http://' + item for item in valid}:
                raise PermissionError('请求来源无效')

        def session_events(self, query):
            if not secrets.compare_digest(query.get('token', ''), token):
                raise PermissionError('请刷新页面后重试')
            if sessions is None:
                return self.send({'error': '当前使用手动启动模式'}, 400)
            identity = session_id(query.get('id'))
            connection = sessions.open(identity)
            try:
                self.connection.settimeout(5)
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(b'retry: 1000\ndata: connected\n\n')
                self.wfile.flush()
                while not connection.is_set():
                    # Socket closure also covers browser crashes and missing pagehide events.
                    readable, _, _ = select.select([self.connection], [], [], 15)
                    if readable:
                        break
                    self.wfile.write(b': page connection\n\n')
                    self.wfile.flush()
            except (OSError, ValueError):
                pass
            finally:
                sessions.close(identity, connection)
                self.close_connection = True

        def do_GET(self):
            try:
                self.check_host()
                parsed = urlparse(self.path)
                query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
                path = parsed.path
                if path == '/api/session/events':
                    return self.session_events(query)
                if path == '/api/health':
                    return self.send({'app': 'agentcm-workbench', 'status': 'ready',
                                      'source': str(ROOT), 'workspace': str(workspace.data),
                                      'pid': os.getpid(), 'session_mode': mode,
                                      'open_pages': sessions.count() if sessions else None})
                with workspace.lock:
                    if path == '/api/bootstrap':
                        value = {'token': token, 'datasets': workspace.datasets(),
                                 'experiments': workspace.experiments(), 'settings': workspace.settings(),
                                 'tasks': read(workspace.data / 'tasks.json', []),
                                 'session_mode': mode}
                    elif path == '/api/experiments':
                        value = workspace.experiments()
                    elif path == '/api/experiments/deleted':
                        value = experiment_lifecycle.deleted_experiments(workspace)
                    elif path == '/api/experiment':
                        value = workspace.experiment(query['id'], detail=True)
                    elif path == '/api/dataset-tasks':
                        value = workspace.dataset_tasks(query['dataset'])
                    elif path == '/api/dataset-task':
                        value = workspace.dataset_task(query['dataset'], query['id'])
                    elif path == '/api/preprocess-comparison':
                        value = preprocessing.compare(workspace, query['id'], query['trajectory'], query.get('event'))
                    elif path == '/api/trajectories':
                        value = workspace.trajectories(query['dataset'])
                    elif path == '/api/trajectory':
                        value = workspace.trajectory(query['dataset'], query['id'])
                    elif path == '/api/windows':
                        value = workspace.window_list(query.get('dataset'), query.get('experiment'))
                    elif path == '/api/window':
                        value = workspace.window(query.get('dataset'), query['id'], query.get('experiment'))
                    elif path == '/api/evidence':
                        value = workspace.evidence(query['experiment'], query['name'])
                    elif path == '/api/batch':
                        value = workspace.batch(query['id'], int(query['index']))
                    elif path == '/api/prompts':
                        value = workspace.prompts()
                    elif path == '/api/export':
                        value = workspace.experiment(query['id'], detail=True)['registry']
                    else:
                        assets = {'/': 'index.html', **{'/' + name: name for name in (
                            'predicate-selection.js', 'browser-session.js', 'experiment-management.js', 'preprocessing.js', 'preprocess-selection.js', 'app.js', 'core.js', 'views.js', 'forms.js', 'datasets.js', 'splitting.js', 'split-preview.js', 'style.css')}}
                        if path not in assets:
                            return self.send({'error': '页面不存在'}, 404)
                        file = ROOT / 'web' / assets[path]
                        return self.send(file.read_bytes(), kind=(mimetypes.guess_type(str(file))[0] or 'text/plain') + '; charset=utf-8')
                self.send(value)
            except PermissionError as exc:
                self.send({'error': str(exc)}, 403)
            except (ValueError, KeyError, OSError) as exc:
                self.send({'error': str(exc)}, 400)

        def do_POST(self):
            try:
                self.check_host()
                if not secrets.compare_digest(self.headers.get('X-Workspace-Token', ''), token):
                    raise PermissionError('请刷新页面后重试')
                length = int(self.headers.get('Content-Length', '0'))
                if length < 0 or length > 2_000_000:
                    raise ValueError('请求过大')
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ValueError('请求需要 JSON 对象')
                if self.path == '/api/session/close':
                    if sessions:
                        sessions.close(session_id(body.get('id')))
                    return self.send({'closed': True})
                with workspace.lock:
                    if workspace.closing or (sessions and sessions.stopping):
                        raise ValueError('工作台正在停止，请从项目入口重新打开')
                    if self.path == '/api/experiment/create':
                        value = workspace.create(body)
                    elif self.path == '/api/experiment/split-preview':
                        value = split_preview(workspace, body)
                    elif self.path == '/api/experiment/preprocess-preview':
                        value = preprocessing.preview_selection(workspace, body)
                    elif self.path == '/api/experiment/input-attach':
                        value = splitting.attach(workspace, body)
                    elif self.path == '/api/experiment/start':
                        value = workspace.start(body['id'])
                    elif self.path == '/api/experiment/stop':
                        value = workspace.stop(body['id'])
                    elif self.path == '/api/experiment/delete':
                        value = experiment_lifecycle.delete(workspace, body['id'])
                    elif self.path == '/api/experiment/restore':
                        value = experiment_lifecycle.restore(workspace, body['id'])
                    elif self.path == '/api/experiment/feedback':
                        value = workspace.feedback(body['id'], body)
                    elif self.path == '/api/review':
                        value = workspace.review(body['id'], body)
                    elif self.path == '/api/task':
                        value = workspace.task(body)
                    elif self.path == '/api/settings':
                        value = workspace.save_settings(body)
                    elif self.path == '/api/prompts':
                        files = body.get('files', {})
                        PromptManager(PROMPTS, workspace.data).validate(files)
                        write(workspace.data / 'prompts.json', files)
                        value = workspace.prompts()
                    else:
                        return self.send({'error': '操作不存在'}, 404)
                self.send(value)
            except PermissionError as exc:
                self.send({'error': str(exc)}, 403)
            except (ValueError, KeyError, OSError) as exc:
                self.send({'error': str(exc)}, 400)

    lockfile = (workspace.data / '.server.lock').open('a')
    try:
        fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lockfile.close()
        raise ValueError('这个工作目录已经有运行中的工作台，请打开原来的地址')

    class NoOpenPages(Exception):
        pass

    class LocalServer(ThreadingHTTPServer):
        def service_actions(self):
            if sessions is None or not workspace.lock.acquire(blocking=False):
                return
            try:
                # Take the same lock as experiment/start so exit cannot interrupt a new worker.
                busy = any(process.poll() is None for process in workspace.processes.values())
                if sessions.should_stop(busy=busy):
                    raise NoOpenPages
            finally:
                workspace.lock.release()

        def serve_forever(self, poll_interval=1):
            try:
                super().serve_forever(poll_interval)
            except NoOpenPages:
                print('工作台页面已关闭，实验均已结束，停止服务。', flush=True)

        def server_close(self):
            if sessions:
                sessions.close_all()
            super().server_close()
            if not lockfile.closed:
                fcntl.flock(lockfile, fcntl.LOCK_UN)
                lockfile.close()

    server = LocalServer(('127.0.0.1', port), Handler)
    server.workspace = workspace
    return server


def serve(port, data_dir, *, idle_timeout=None, startup_timeout=120, on_ready=None):
    server = make_server(port, data_dir, idle_timeout=idle_timeout,
                         startup_timeout=startup_timeout, session_mode='terminal')
    signals = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
    previous = {s: signal.getsignal(s) for s in signals}
    stopping = False
    def shutdown(signum, frame):
        nonlocal stopping
        if not stopping:
            stopping = True
            raise KeyboardInterrupt
    for sig in signals:
        signal.signal(sig, shutdown)
    try:
        if on_ready:
            on_ready(server)
        else:
            print(f'AgentCM Workbench → http://127.0.0.1:{server.server_port}\n'
                  '保持这个终端打开；按 Ctrl+C 或关闭终端停止工作台。', flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # A second close/interrupt must not interrupt worker cleanup.
        stopping = True
        try:
            with server.workspace.lock:
                server.workspace.closing = True
                server.workspace.shutdown()
        finally:
            server.server_close()
            for sig, handler in previous.items():
                signal.signal(sig, handler)
