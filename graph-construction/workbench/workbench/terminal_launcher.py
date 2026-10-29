"""Keep the workbench in its launching terminal; retire the old launchd entry."""
import json
import os
import signal
import sys
import time

from .macos_service import LaunchError
from .server import serve


def retire_background_service(service):
    """Remove only this workspace's previous launchd job, preserving active runs."""
    if sys.platform != 'darwin' or not service.loaded():
        return
    if service.probe():
        with service.opener.open(f'http://127.0.0.1:{service.port}/api/experiments', timeout=10) as response:
            experiments = json.load(response)
        if any(e['status'] in ('running', 'waiting') for e in experiments):
            raise LaunchError('旧的后台工作台还有实验在运行。等实验结束，或在网页中停止实验后，再打开这个入口。')
    service.stop()


def stop_workbench(service):
    if sys.platform == 'darwin' and service.loaded():
        service.stop()
    health = service.probe()
    if not health:
        return
    try:
        os.kill(health['pid'], signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        current = service.probe()
        if not current or current['pid'] != health['pid']:
            return
        time.sleep(.1)
    raise LaunchError('停止服务超时，请检查启动工作台的终端。')


def run_in_terminal(service, *, open_browser=True):
    retire_background_service(service)
    health = service.probe()
    if health:
        print(f'工作台已在运行：{service.url}\n请保持原来的启动终端打开；这个窗口可以关闭。', flush=True)
        if open_browser:
            service.open_browser()
        return

    def ready(server):
        print(f'工作台已就绪：{service.url}\n'
              '保持这个终端打开，网站就会一直运行。关闭网页不影响实验。\n'
              '关闭这个终端或按 Ctrl+C 会停止服务和运行中的实验，已保存的进度可以继续。', flush=True)
        if open_browser:
            service.open_browser()

    serve(service.port, service.data, on_ready=ready)
