"""Run the workbench in the launching terminal and open its website."""
import argparse
from pathlib import Path
import sys
import subprocess

from workbench.macos_service import LaunchError, WorkbenchService, install_shortcut
from workbench.terminal_launcher import run_in_terminal, stop_workbench


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-open', action='store_true', help='Run in this terminal without opening a browser')
    parser.add_argument('--install-shortcut', action='store_true', help='Add the project-root entrypoint')
    parser.add_argument('--stop', action='store_true', help='Stop the workbench and its active experiments')
    parser.add_argument('--status', action='store_true', help='Check readiness without starting')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--data-dir', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    try:
        service = WorkbenchService(root, args.data_dir or root / 'runs', args.port)
        if args.install_shortcut:
            print(f'项目入口：{install_shortcut(root)}', flush=True)
        if args.stop:
            stop_workbench(service)
            print('工作台已停止。')
            return 0
        if args.status:
            ready = service.probe()
            print('工作台运行中。' if ready else '工作台已停止，双击项目目录中的入口即可启动。')
            return 0 if ready else 1
        print('正在检查并启动 AgentCM 工作台…', flush=True)
        run_in_terminal(service, open_browser=not args.no_open)
        return 0
    except (LaunchError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f'启动失败：{exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
