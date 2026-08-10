#!/usr/bin/env bash
# scripts/alvis/push_to_alvis.sh — run LOCALLY (this dev machine), not on Alvis.
#
# Pushes just the kradar_visibility subproject to Alvis via rsync. Only this
# directory is needed on the cluster: data is read directly from
# Cephyr/Mimer on-cluster (see docs/ALVIS_MIGRATION_PLAN.md §1), and the
# dataset split files are bundled at resources/split/ rather than pulled
# from the separate K-Radar git submodule.
#
# Usage:
#   scripts/alvis/push_to_alvis.sh [remote_dir]
#
# remote_dir defaults to ~/kradar_visibility on Alvis.

set -euo pipefail

# Uses the "alvis" alias from ~/.ssh/config (HostName/User/IdentityFile
# already set up there) rather than a raw hostname, so it picks up the
# correct key automatically. Override ALVIS_SSH_TARGET if your config uses
# a different alias.
ALVIS_SSH_TARGET="${ALVIS_SSH_TARGET:-alvis}"
REMOTE_DIR="${1:-~/kradar_visibility}"

LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Pushing ${LOCAL_DIR} -> ${ALVIS_SSH_TARGET}:${REMOTE_DIR}"

rsync -avz --progress \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'outputs/' \
  --exclude '.pytest_cache' \
  -e ssh \
  "${LOCAL_DIR}/" "${ALVIS_SSH_TARGET}:${REMOTE_DIR}/"

echo "Done. Next: ssh ${ALVIS_SSH_TARGET}, cd ${REMOTE_DIR}, then run scripts/alvis/bootstrap_env.sh"
