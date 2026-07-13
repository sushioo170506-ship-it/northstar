#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR"
while [[ "$ROOT" != "/" ]]; do
  if [[ -f "$ROOT/pyproject.toml" ]] && \
     command grep -q "northstar-research-workflow" "$ROOT/pyproject.toml"; then
    break
  fi
  ROOT="$(dirname "$ROOT")"
done

if [[ "$ROOT" == "/" ]]; then
  echo "找不到 northstar-research-workflow 仓库" >&2
  exit 2
fi

python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install -e "${ROOT}[office]"
echo "环境已安装：$ROOT/.venv"
