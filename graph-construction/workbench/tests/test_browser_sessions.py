"""Page lifetimes, refresh grace, disconnect fallback and idle service exit."""
import json
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from workbench.browser_sessions import BrowserSessions
from workbench.server import make_server


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.sessions = BrowserSessions(30, 120, lambda: self.now)

    def test_startup_expires_without_opening_a_page(self):
        self.now = 119
        self.assertFalse(self.sessions.should_stop())
        self.now = 120
        self.assertTrue(self.sessions.should_stop())
        with self.assertRaises(ValueError):
            self.sessions.open('late')

    def test_last_page_closes_and_refresh_cancels_exit(self):
        a = self.sessions.open('a')
        self.sessions.open('b')
        self.sessions.close('a', a)
        self.now = 1000
        self.assertFalse(self.sessions.should_stop())
        self.sessions.close('b')
        self.now = 1020
        refreshed = self.sessions.open('new-page')
        self.now = 2000
        self.assertFalse(self.sessions.should_stop())
        self.sessions.close('new-page', refreshed)
        self.now = 2029
        self.assertFalse(self.sessions.should_stop())
        self.now = 2030
        self.assertTrue(self.sessions.should_stop())

    def test_reconnect_and_duplicate_close_do_not_remove_a_live_page(self):
        old = self.sessions.open('a')
        current = self.sessions.open('a')
        self.assertTrue(old.is_set())
        self.sessions.close('a', old)
        self.assertEqual(self.sessions.count(), 1)
        self.sessions.close('missing')
        self.assertEqual(self.sessions.count(), 1)
        self.sessions.close('a', current)
        self.now = 20
        self.sessions.close('a')
        self.now = 30
        self.assertTrue(self.sessions.should_stop())

    def test_running_work_survives_idle_deadline_then_allows_exit(self):
        self.sessions.open('a')
        self.sessions.close('a')
        self.now = 300
        self.assertFalse(self.sessions.should_stop(busy=True))
        self.assertFalse(self.sessions.stopping)
        self.assertTrue(self.sessions.should_stop(busy=False))


class SessionHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.server = make_server(0, Path(self.temp.name), idle_timeout=.2, startup_timeout=10)
        self.thread = threading.Thread(target=lambda: self.server.serve_forever(.02), daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with self.opener.open(self.base + '/api/bootstrap') as response:
            self.token = json.load(response)['token']
        self.sockets = []

    def tearDown(self):
        for stream in self.sockets:
            stream.close()
        self.server.shutdown()
        self.server.server_close()
        self.temp.cleanup()

    def health(self):
        with self.opener.open(self.base + '/api/health') as response:
            return json.load(response)

    def stream(self, identity):
        stream = socket.create_connection(('127.0.0.1', self.server.server_port), timeout=2)
        self.sockets.append(stream)
        stream.sendall((f'GET /api/session/events?id={identity}&token={self.token} HTTP/1.1\r\n'
                        f'Host: 127.0.0.1:{self.server.server_port}\r\n\r\n').encode())
        data = b''
        while b'data: connected\n\n' not in data:
            data += stream.recv(4096)
        return stream

    def close_page(self, identity, token=None):
        request = urllib.request.Request(self.base + '/api/session/close',
            data=json.dumps({'id': identity}).encode(),
            headers={'X-Workspace-Token': token or self.token, 'Content-Type': 'application/json'})
        with self.opener.open(request) as response:
            return json.load(response)

    def test_pages_keep_service_alive_then_socket_disconnect_exits(self):
        first, second = self.stream('a'), self.stream('b')
        self.assertEqual(self.health()['open_pages'], 2)
        first.close()
        time.sleep(.3)
        self.assertEqual(self.health()['open_pages'], 1)
        self.assertTrue(self.thread.is_alive())
        second.close()
        self.thread.join(2)
        self.assertFalse(self.thread.is_alive())

    def test_explicit_close_is_authenticated_and_refresh_is_safe(self):
        self.stream('old')
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.close_page('old', 'wrong')
        self.assertEqual(error.exception.code, 403)
        self.assertEqual(self.health()['open_pages'], 1)
        self.close_page('old')
        self.stream('new')
        self.close_page('old')
        time.sleep(.3)
        self.assertEqual(self.health()['open_pages'], 1)
        self.close_page('new')
        self.thread.join(2)
        self.assertFalse(self.thread.is_alive())

    def test_all_workers_finish_before_service_exits(self):
        self.stream('page')
        workers = []
        try:
            for index, exit_code in enumerate((0, 7)):
                release = Path(self.temp.name) / f'release-{index}'
                script = 'import pathlib,sys,time\np=pathlib.Path(sys.argv[1])\nwhile not p.exists(): time.sleep(.01)\nsys.exit(int(sys.argv[2]))'
                process = subprocess.Popen([sys.executable, '-c', script, str(release), str(exit_code)])
                workers.append((process, release))
                with self.server.workspace.lock:
                    self.server.workspace.processes[str(index)] = process
            self.close_page('page')
            time.sleep(.35)
            self.assertEqual(self.health()['open_pages'], 0)
            self.assertTrue(all(process.poll() is None for process, _ in workers))
            workers[0][1].touch()
            self.assertEqual(workers[0][0].wait(timeout=2), 0)
            time.sleep(.3)
            self.assertTrue(self.thread.is_alive())
            workers[1][1].touch()
            self.assertEqual(workers[1][0].wait(timeout=2), 7)
            self.thread.join(2)
            self.assertFalse(self.thread.is_alive())
        finally:
            for process, release in workers:
                release.touch()
                process.wait(timeout=2)


if __name__ == '__main__':
    unittest.main()
