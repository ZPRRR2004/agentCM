#!/bin/bash
# Finder entrypoint. Resolve the entrypoint symlink before locating the project.
set -eu
entry_path="${BASH_SOURCE[0]}"
while [ -L "$entry_path" ]; do
  entry_dir="$(cd -P "$(dirname "$entry_path")" && pwd)"
  entry_path="$(readlink "$entry_path")"
  case "$entry_path" in /*) ;; *) entry_path="$entry_dir/$entry_path" ;; esac
done
workbench_dir="$(cd -P "$(dirname "$entry_path")" && pwd)"

for candidate in \
  "$workbench_dir/.venv/bin/python3" \
  "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" \
  /opt/homebrew/bin/python3 /usr/local/bin/python3 \
  "$(command -v python3 || true)"; do
  if [ -x "$candidate" ] && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
    # The server owns this terminal session and receives its close/interrupt signals.
    exec "$candidate" "$workbench_dir/launch.py" "$@"
  fi
done
printf '%s\n' '需要 Python 3.11 或更新版本。请安装后再次双击工作台入口。' >&2
if [ -t 0 ]; then read -r -p '按回车关闭此窗口…' _; fi
exit 1
