"""Readiness, port ownership and safe project-entry behavior."""
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from workbench.macos_service import LaunchError, WorkbenchService, install_shortcut


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve() / '带空格 工作台'
        self.root.mkdir()
        self.service = WorkbenchService(self.root, self.root / 'runs', 8765)
        self.health = {'app': 'agentcm-workbench', 'status': 'ready', 'pid': os.getpid(),
                       'source': str(self.root), 'workspace': str(self.service.data)}
        case = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_GET(self):
                raw = json.dumps(case.health).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(raw)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.service.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.temp.cleanup()

    def test_health_bypasses_proxy_and_reuses_existing_process(self):
        with patch.dict(os.environ, {'http_proxy': 'http://127.0.0.1:1', 'no_proxy': ''}), \
             patch('sys.platform', 'darwin'), patch.object(self.service, 'launchctl') as launchctl:
            self.assertEqual(self.service.ensure_ready()['pid'], os.getpid())
            launchctl.assert_not_called()

    def test_other_apps_and_workspaces_are_rejected(self):
        for change in ({'app': 'another-app'}, {'workspace': '/different/workspace'},
                       {'source': '/different/code'}, {'status': 'starting'}):
            original = self.health.copy()
            self.health.update(change)
            with self.assertRaises(LaunchError):
                self.service.probe()
            self.health = original

    def test_service_starts_only_when_launched_and_does_not_restart_itself(self):
        specification = self.service.specification()
        self.assertFalse(specification['KeepAlive'])
        self.assertTrue(specification['RunAtLoad'])

    def test_busy_non_http_port_does_not_start_another_server(self):
        with socket.socket() as occupied:
            occupied.bind(('127.0.0.1', 0))
            occupied.listen()
            self.service.port = occupied.getsockname()[1]
            with patch('sys.platform', 'darwin'), patch.object(self.service, 'probe', return_value=None), \
                 patch.object(self.service, 'loaded', return_value=False), \
                 patch.object(self.service, 'launchctl') as launchctl:
                with self.assertRaisesRegex(LaunchError, '已占用'):
                    self.service.ensure_ready()
                launchctl.assert_not_called()

    def test_shortcut_is_idempotent_and_preserves_existing_files(self):
        project = self.root / '研究 项目'
        workbench = project / '代码仓库' / 'graph-construction' / 'workbench'
        workbench.mkdir(parents=True)
        entry = workbench / 'open-workbench.command'
        entry.write_text('#!/bin/bash\nexit 0\n')
        shortcut = install_shortcut(workbench)
        self.assertEqual(shortcut.parent, project)
        self.assertFalse(shortcut.readlink().is_absolute())
        self.assertTrue(os.access(shortcut, os.X_OK))
        self.assertEqual(shortcut.resolve(), entry)
        self.assertEqual(install_shortcut(workbench), shortcut)
        moved_project = project.rename(self.root / '移动后的 项目')
        workbench = moved_project / workbench.relative_to(project)
        shortcut = moved_project / shortcut.name
        self.assertEqual(shortcut.resolve(), workbench / entry.name)
        self.assertEqual(install_shortcut(workbench), shortcut)
        shortcut.unlink()
        shortcut.write_text('User document')
        with self.assertRaises(LaunchError):
            install_shortcut(workbench)
        self.assertEqual(shortcut.read_text(), 'User document')


if __name__ == '__main__':
    unittest.main()
