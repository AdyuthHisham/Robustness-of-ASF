#!/usr/bin/env bash
# scripts/alvis/bootstrap_env.sh — run ON Alvis (alvis2 login/transfer node),
# from inside the pushed kradar_visibility directory, with outbound internet
# available (needed once, to install uv and resolve dependencies).
#
# Do NOT run this inside a SLURM job — compute nodes are expected to be
# air-gapped. Run it once here, then jobs activate the resulting .venv.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found — installing to \$HOME/.local/bin"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

uv --version

echo "Locking + syncing dependencies (from $(pwd))..."
uv lock
uv sync

echo ""
echo "Environment ready at $(pwd)/.venv"
echo "Sanity check:"
uv run python -c "import kradar_visibility, polars, numpy, cv2; print('imports OK')"
