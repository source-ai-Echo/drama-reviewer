#!/bin/zsh
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "未找到 Python 3。请先安装 Python 3.10 或更高版本。"
  read -r "?按回车关闭窗口。"
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --quiet -e .
(sleep 2; open http://127.0.0.1:8765) &
echo "Drama Reviewer 已启动。关闭此窗口即可停止。"
exec .venv/bin/python main.py serve
