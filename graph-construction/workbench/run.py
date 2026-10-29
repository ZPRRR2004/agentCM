"""Start the local AgentCM research workbench."""
import argparse
from pathlib import Path

from workbench.server import serve


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).parent / 'runs')
    parser.add_argument('--idle-timeout', type=float, default=None, help='Opt in to page-based shutdown after this many seconds')
    parser.add_argument('--startup-timeout', type=float, default=120, help='Seconds to wait for the first page')
    args = parser.parse_args()
    if (args.idle_timeout is not None and args.idle_timeout <= 0) or args.startup_timeout <= 0:
        parser.error('页面等待时间需要大于 0')
    serve(args.port, args.data_dir, idle_timeout=args.idle_timeout, startup_timeout=args.startup_timeout)
