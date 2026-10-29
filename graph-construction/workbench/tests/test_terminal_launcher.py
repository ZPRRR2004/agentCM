"""Terminal ownership, migration and safe duplicate launches."""
import io
import json
import signal
import unittest
from unittest.mock import Mock, patch

from workbench.macos_service import LaunchError
from workbench.terminal_launcher import retire_background_service, run_in_terminal, stop_workbench


class TerminalLauncherTests(unittest.TestCase):
    def service(self):
        service = Mock(port=8765, data='/test/workspace', url='http://127.0.0.1:8765/')
        service.loaded.return_value = False
        service.probe.return_value = None
        return service

    def test_new_launch_stays_in_terminal_without_launchd_or_browser(self):
        service = self.service()
        with patch('sys.platform', 'darwin'), patch('workbench.terminal_launcher.serve') as serve:
            run_in_terminal(service, open_browser=False)
            serve.assert_called_once()
            self.assertEqual(serve.call_args.args, (8765, '/test/workspace'))
            self.assertNotIn('idle_timeout', serve.call_args.kwargs)
            with patch('sys.stdout', new_callable=io.StringIO):
                serve.call_args.kwargs['on_ready'](Mock())
        service.ensure_ready.assert_not_called()
        service.open_browser.assert_not_called()

    def test_duplicate_launch_keeps_original_terminal_owner(self):
        service = self.service()
        service.probe.return_value = {'pid': 123, 'session_mode': 'terminal'}
        with patch('sys.platform', 'darwin'), patch('sys.stdout', new_callable=io.StringIO) as output, \
                patch('workbench.terminal_launcher.serve') as serve:
            run_in_terminal(service)
            self.assertIn('原来的启动终端', output.getvalue())
            serve.assert_not_called()
        service.open_browser.assert_called_once()
        service.stop.assert_not_called()

    def test_idle_legacy_job_is_removed_before_terminal_launch(self):
        service = self.service()
        service.loaded.return_value = True
        service.probe.return_value = {'pid': 123}
        service.opener.open.return_value = io.BytesIO(b'[]')
        with patch('sys.platform', 'darwin'):
            retire_background_service(service)
        service.stop.assert_called_once()

    def test_migration_preserves_running_and_waiting_experiments(self):
        for status in ('running', 'waiting'):
            with self.subTest(status=status):
                service = self.service()
                service.loaded.return_value = True
                service.probe.return_value = {'pid': 123}
                service.opener.open.return_value = io.BytesIO(json.dumps([{'status': status}]).encode())
                with patch('sys.platform', 'darwin'), self.assertRaises(LaunchError):
                    retire_background_service(service)
                service.stop.assert_not_called()

    def test_explicit_stop_targets_only_verified_workbench(self):
        service = self.service()
        service.probe.side_effect = [{'pid': 123}, None]
        with patch('sys.platform', 'darwin'), patch('workbench.terminal_launcher.os.kill') as kill:
            stop_workbench(service)
        kill.assert_called_once_with(123, signal.SIGTERM)


if __name__ == '__main__':
    unittest.main()
