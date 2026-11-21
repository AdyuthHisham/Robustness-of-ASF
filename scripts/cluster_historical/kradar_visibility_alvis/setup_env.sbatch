#!/bin/bash
# scripts/alvis/setup_env.sbatch — one-time environment build, module-based.
#
# Alvis is a shared cluster: no host-level package installs are permitted
# (no pip/uv/conda against the system Python or a $HOME-wide location).
# `uv` itself is a C3SE-provided module (uv/0.7.13-GCCcore-14.2.0), which
# pulls in Python/3.13.1-GCCcore-14.2.0 as its toolchain dependency —
# `requires-python = ">=3.11"` in pyproject.toml is satisfied by that, so no
# separate Python module or download is needed. `uv sync` then only writes
# to this project's local .venv/, which lives on Cephyr NOBACKUP project
# storage (not system-wide) — the explicitly-permitted case.
#
# UV_PYTHON_DOWNLOADS=never + UV_PYTHON pinned to the module's interpreter
# stop uv from trying to fetch its own Python to satisfy the project's
# ".python-version" (pinned to "3.11" for local dev) — that pin is
# advisory-only here; we deliberately override it to the module-provided
# 3.13.1 rather than let uv reach out to python-build-standalone over the
# network.
#
#SBATCH -A naiss2026-4-494
#SBATCH -p alvis
#SBATCH --gpus-per-node=A40:1
#SBATCH -c 4
#SBATCH -t 00:30:00
#SBATCH -o slurm_logs/setup_env_%j.out
#SBATCH -J kradar_vis_setup_env

set -euo pipefail

BASE_DIR="${BASE_DIR:-/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth/AMSCUP}"
KRADAR_DIR="$BASE_DIR/test-bed/src/Modules/robust_testing/kradar"

mkdir -p "$KRADAR_DIR/slurm_logs"
cd "$KRADAR_DIR"

module load uv/0.7.13-GCCcore-14.2.0

export UV_PYTHON_DOWNLOADS=never
export UV_PYTHON="$(command -v python3)"

uv --version
"$UV_PYTHON" --version

echo "Locking + syncing dependencies (from $(pwd)) ..."
uv lock
uv sync

# kradar is a uv workspace member of test-bed (see test-bed/pyproject.toml),
# so `uv sync` resolves the shared venv at the workspace root, not here.
echo ""
echo "Environment ready at $BASE_DIR/test-bed/.venv"
uv run python -c "import kradar_visibility, polars, numpy, cv2; print('imports OK')"
