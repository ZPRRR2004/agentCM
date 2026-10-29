"""Workspace health checks, project shortcut and legacy launchd compatibility."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import plistlib
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


class LaunchError(RuntimeError):
    pass


def install_shortcut(root, directory=None):
    root = Path(root).resolve()
    source = root / 'open-workbench.command'
    source.chmod(source.stat().st_mode | 0o111)
    # Project / 代码仓库 / graph-construction / workbench.
    destination = Path(directory).resolve() if directory else root.parents[2]
    shortcut = destination / '打开 AgentCM 工作台.command'
    if shortcut.is_symlink() and shortcut.resolve() == source:
        return shortcut
    if shortcut.exists() or shortcut.is_symlink():
        raise LaunchError(f'该目录已有同名文件，请先重命名：{shortcut}')
    shortcut.symlink_to(os.path.relpath(source, shortcut.parent))
    return shortcut


class WorkbenchService:
    def __init__(self, root, data_dir, port=8765):
        if not 1 <= port <= 65535:
            raise LaunchError('端口需要在 1–65535 之间')
        self.root = Path(root).resolve()
        self.data = Path(data_dir).resolve()
        self.port = port
        identity = hashlib.sha256(f'{self.root}:{self.data}:{port}'.encode()).hexdigest()[:12]
        self.label = f'local.agentcm.workbench.{identity}'
        self.domain = f'gui/{os.getuid()}'
        self.target = f'{self.domain}/{self.label}'
        self.log_dir = self.data / 'service'
        self.plist = self.log_dir / (self.label + '.plist')
        self.url = f'http://127.0.0.1:{port}/#experiments'
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def probe(self):
        """Read a cheap identity check directly, regardless of system proxy settings."""
        try:
            with self.opener.open(f'http://127.0.0.1:{self.port}/api/health', timeout=1) as response:
                value = json.loads(response.read(8192))
        except urllib.error.HTTPError as exc:
            raise LaunchError(f'端口 {self.port} 已有其他服务，请关闭占用者或换一个端口') from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            return None
        except (ValueError, UnicodeError) as exc:
            raise LaunchError(f'端口 {self.port} 返回了其他服务的内容') from exc
        if not isinstance(value, dict) or value.get('app') != 'agentcm-workbench':
            raise LaunchError(f'端口 {self.port} 已被其他应用占用')
        if value.get('source') != str(self.root) or value.get('workspace') != str(self.data):
            raise LaunchError(f'端口 {self.port} 正在使用另一份工作区，请为当前项目选择其他端口')
        if value.get('status') != 'ready' or type(value.get('pid')) is not int:
            raise LaunchError('工作台健康检查响应无效')
        return value

    def launchctl(self, *args):
        return subprocess.run(['/bin/launchctl', *args], capture_output=True, text=True, timeout=15)

    def loaded(self):
        return self.launchctl('print', self.target).returncode == 0

    def specification(self):
        # Only the local service bypasses proxies; external model URLs retain system proxy behavior.
        return {
            'Label': self.label,
            'ProgramArguments': [sys.executable, '-u', str(self.root / 'run.py'),
                                 '--port', str(self.port), '--data-dir', str(self.data), '--idle-timeout', '30'],
            'WorkingDirectory': str(self.root),
            'EnvironmentVariables': {'PYTHONUNBUFFERED': '1',
                                     'NO_PROXY': 'localhost,127.0.0.1,::1',
                                     'no_proxy': 'localhost,127.0.0.1,::1'},
            'KeepAlive': False,
            'RunAtLoad': True,
            'ThrottleInterval': 5,
            'ExitTimeOut': 15,
            'StandardOutPath': str(self.log_dir / 'stdout.log'),
            'StandardErrorPath': str(self.log_dir / 'stderr.log'),
        }

    def ensure_ready(self, timeout=30):
        if sys.platform != 'darwin':
            raise LaunchError('双击入口适用于 macOS；其他系统可运行 python3 run.py')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        with (self.log_dir / 'launcher.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            health = self.probe()
            if health:
                return health
            if not self.loaded():
                # Refuse a busy port even when its occupant does not speak HTTP.
                with socket.socket() as candidate:
                    candidate.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    try:
                        candidate.bind(('127.0.0.1', self.port))
                    except OSError as exc:
                        raise LaunchError(f'端口 {self.port} 已占用，请选择其他端口') from exc
                temporary = self.plist.with_suffix('.tmp')
                temporary.write_bytes(plistlib.dumps(self.specification()))
                temporary.replace(self.plist)
                result = self.launchctl('bootstrap', self.domain, str(self.plist))
                if result.returncode:
                    raise LaunchError(f'macOS 后台服务启动失败：{result.stderr.strip()}')
            else:
                result = self.launchctl('kickstart', self.target)
                if result.returncode:
                    raise LaunchError(f'macOS 后台服务启动失败：{result.stderr.strip()}')
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                health = self.probe()
                if health:
                    return health
                time.sleep(.2)
            raise LaunchError('服务启动超时，请查看运行日志')

    def open_browser(self):
        result = subprocess.run(['/usr/bin/open', '-g', self.url], capture_output=True, text=True, timeout=15)
        if result.returncode:
            raise LaunchError(f'浏览器打开失败，可手动访问 {self.url}')

    def stop(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        with (self.log_dir / 'launcher.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if self.loaded():
                # Wait for launchd to remove the job before allowing another launch.
                result = self.launchctl('bootout', '--wait', self.target)
                if result.returncode:
                    raise LaunchError(f'停止服务失败：{result.stderr.strip()}')
