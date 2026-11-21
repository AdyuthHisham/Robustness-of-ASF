#!/usr/bin/env bash
# scripts/alvis/bootstrap_env.sh — interactive equivalent of setup_env.sbatch.
# Prefer submitting setup_env.sbatch instead; this is here for manual/debug
# use only (e.g. inside an `srun --pty` allocation, not the login node).
#
# Alvis is a shared cluster: no host-level package installs. `uv` is a
# C3SE-provided module and pulls in its own Python (>=3.11, satisfies this
# project's requires-python) as a toolchain dependency — nothing is
# installed outside this project's local .venv/, which lives on Cephyr
# NOBACKUP project storage.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."

module load uv/0.7.13-GCCcore-14.2.0

export UV_PYTHON_DOWNLOADS=never
export UV_PYTHON="$(command -v python3)"

uv --version

echo "Locking + syncing dependencies (from $(pwd)) into local .venv/ ..."
uv lock
uv sync

echo ""
echo "Environment ready at $(pwd)/.venv"
echo "Sanity check:"
uv run python -c "import kradar_visibility, polars, numpy, cv2; print('imports OK')"
