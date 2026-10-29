"""macOS integration check using a disposable workspace and a separate port."""
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from workbench.macos_service import WorkbenchService


def main():
    if sys.platform != 'darwin':
        raise SystemExit('This check requires a logged-in macOS GUI session.')
    with tempfile.TemporaryDirectory(prefix='agentcm-launch-test-') as directory:
        with socket.socket() as candidate:
            candidate.bind(('127.0.0.1', 0))
            port = candidate.getsockname()[1]
        service = WorkbenchService(ROOT, Path(directory), port)
        try:
            first = service.ensure_ready()
            parent = subprocess.check_output(['/bin/ps', '-p', str(first['pid']), '-o', 'ppid='], text=True)
            assert parent.strip() == '1', 'Server must be owned by launchd'
            assert service.ensure_ready()['pid'] == first['pid'], 'Duplicate launch must reuse the process'
            print('PASS: launchd ownership and repeated launch', flush=True)
            # Only the disposable test service is terminated; the user workspace has another label/port.
            os.kill(first['pid'], signal.SIGKILL)
            time.sleep(6)
            assert not service.probe(), 'Closed service must stay stopped'
            recovered = service.ensure_ready()
            assert recovered['pid'] != first['pid'], 'Explicit launch must restart the service'
            print('PASS: no automatic restart; explicit launch starts again', flush=True)
            service.stop()
            assert not service.loaded() and not service.probe(), 'Stop must finish removing the service'
            restarted = service.ensure_ready()
            assert restarted['pid'] != recovered['pid'], 'Cold restart must create a new process'
            print('PASS: stop and immediate cold restart', flush=True)
        except Exception:
            for log in service.log_dir.glob('*.log'):
                print(log.name, log.read_text(), file=sys.stderr)
            raise
        finally:
            service.stop()


if __name__ == '__main__':
    main()
