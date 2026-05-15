#!/bin/bash
# run_pipeline.sh — Complete K-Radar sync workflow (FIXED)
#
# FIXES:
#   1. Passes output_dir to phase1_mapper
#   2. Passes full manifest path to phase2_rsync
#   3. Proper directory structure for all outputs
#
# Usage: ./run_pipeline.sh <xlsx_file> <data_root> <output_dir> <remote_host> <remote_base>
#
# Arguments:
#   xlsx_file    Path to Excel with 58 sheets (sheet names = sequence numbers)
#   data_root    Read-only source: /mnt/expansion/k-radar
#   output_dir   Writable directory for manifests, batches, logs
#   remote_host  SSH destination (user@hostname)
#   remote_base  Remote path where dataset should be recreated
#
# Example:
#   ./run_pipeline.sh \
#     /mnt/expansion/k-radar/labels.xlsx \
#     /mnt/expansion/k-radar \
#     /home/adhish/k-radar-workflow \
#     user@cluster.hpc.edu \
#     /data/k-radar

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────
# ARGUMENT VALIDATION
# ─────────────────────────────────────────────────────────────────────

XLSX_FILE="${1:-}"
DATA_ROOT="${2:-}"
OUTPUT_DIR="${3:-}"
REMOTE_HOST="${4:-}"
REMOTE_BASE="${5:-}"

if [[ -z "$XLSX_FILE" || -z "$DATA_ROOT" || -z "$OUTPUT_DIR" || -z "$REMOTE_HOST" || -z "$REMOTE_BASE" ]]; then
    cat <<'EOF'
Usage: ./run_pipeline.sh <xlsx> <data_root> <output_dir> <remote_host> <remote_base>

Arguments:
  xlsx_file    Excel file with 58 sheets (sheet names = sequence numbers)
  data_root    Read-only source directory (e.g., /mnt/expansion/k-radar)
  output_dir   Writable directory for generated artifacts
  remote_host  SSH destination (user@hostname)
  remote_base  Remote path where dataset should be recreated

Example:
  ./run_pipeline.sh /mnt/expansion/k-radar/labels.xlsx \
                    /mnt/expansion/k-radar \
                    /home/adhish/k-radar-workflow \
                    user@cluster.hpc.edu \
                    /data/k-radar
EOF
    exit 1
fi

# Validate paths
if [[ ! -f "$XLSX_FILE" ]]; then
    echo "[ERROR] Excel file not found: $XLSX_FILE"
    exit 1
fi

if [[ ! -d "$DATA_ROOT" ]]; then
    echo "[ERROR] Data root not found: $DATA_ROOT"
    exit 1
fi

# Verify at least one sequence exists
if [[ ! -d "$DATA_ROOT/1" ]]; then
    echo "[ERROR] No sequence folders found under $DATA_ROOT"
    echo "  Expected: $DATA_ROOT/1/, $DATA_ROOT/2/, etc."
    exit 1
fi

# Create output directory structure (FIX #2: Create all subdirs upfront)
mkdir -p "$OUTPUT_DIR"/{manifests,logs,rsync_batches}

# Verify SSH connectivity
echo "[CHECK] Testing SSH to $REMOTE_HOST..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$REMOTE_HOST" "echo OK" >/dev/null 2>&1; then
    echo "[ERROR] Cannot SSH to $REMOTE_HOST"
    echo "  Ensure passwordless auth: ssh-copy-id $REMOTE_HOST"
    exit 1
fi
echo "[OK] SSH connection verified"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  K-RADAR SYNC PIPELINE"
echo "═══════════════════════════════════════════════════════════════"
echo "  Excel:      $XLSX_FILE"
echo "  Data root:  $DATA_ROOT (read-only)"
echo "  Output:     $OUTPUT_DIR (writable)"
echo "  Remote:     $REMOTE_HOST:$REMOTE_BASE"
echo "═══════════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────────
# PHASE 1: DISCOVERY & CROSS-REFERENCE (all 58 sequences)
# ─────────────────────────────────────────────────────────────────────

echo ""
echo ">>> PHASE 1: Discovery & Cross-Reference"
echo "    Processing all sequences from Excel sheets..."
echo ""

# FIX #2: Import phase1_mapper from same directory as script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 <<PY
import sys
from pathlib import Path

# Add script directory to path so we can import phase1_mapper
sys.path.insert(0, '$SCRIPT_DIR')

from phase1_mapper import RadarFileMapper

xlsx = Path('$XLSX_FILE')
data_root = Path('$DATA_ROOT')
output_dir = Path('$OUTPUT_DIR/manifests')

print(f"Excel: {xlsx}")
print(f"Data root: {data_root}")
print(f"Output dir: {output_dir}")

# FIX #2: Pass output_dir to mapper
mapper = RadarFileMapper(str(xlsx), str(data_root), str(output_dir))
mapper.process_all_sheets()

# FIX #3: export_manifest() now writes to output_dir automatically
manifest = mapper.export_manifest()

# Print summary
total_sheets = len(mapper.mappings)
successful = sum(1 for r in mapper.mappings.values() if 'error' not in r)
total_files = manifest['metadata']['total_matched_files']

print(f"\n{'='*50}")
print(f"PHASE 1 COMPLETE")
print(f"Sheets: {successful}/{total_sheets} processed successfully")
print(f"Files to sync: {total_files}")
print(f"Manifests: {output_dir}/")
print(f"{'='*50}")
PY

if [[ $? -ne 0 ]]; then
    echo "[ERROR] Phase 1 failed. Check Excel file and data paths."
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────
# PHASE 2: RSYNC BATCH GENERATION
# ─────────────────────────────────────────────────────────────────────

echo ""
echo ">>> PHASE 2: Rsync Batch Generation"
echo ""

MANIFEST_PATH="$OUTPUT_DIR/manifests/radar_sync_manifest.json"

if [[ ! -f "$MANIFEST_PATH" ]]; then
    echo "[ERROR] Manifest not found: $MANIFEST_PATH"
    exit 1
fi

python3 <<PY
import sys
from pathlib import Path

sys.path.insert(0, '$SCRIPT_DIR')

from phase2_rsync import RsyncOrchestrator

# FIX #3: Pass full manifest path
orch = RsyncOrchestrator(
    '$MANIFEST_PATH',
    '$REMOTE_HOST',
    '$REMOTE_BASE',
    '$OUTPUT_DIR/rsync_batches'  # Output dir for batch scripts
)
orch.create_all_batches()
PY

if [[ $? -ne 0 ]]; then
    echo "[ERROR] Phase 2 failed. Check manifest path."
    exit 1
fi

echo ""
echo "Generated batches in: $OUTPUT_DIR/rsync_batches/"
find "$OUTPUT_DIR/rsync_batches" -name "*_sync.sh" -type f | sort -V

# ─────────────────────────────────────────────────────────────────────
# PHASE 3: DRY-RUN GATE (Interactive)
# ─────────────────────────────────────────────────────────────────────

echo ""
echo ">>> PHASE 3: Dry-Run Validation"
echo ""

read -p "Run dry-run for Sequence 1? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running dry-run for Sequence 1..."

    python3 <<PY
import sys
from pathlib import Path

sys.path.insert(0, '$SCRIPT_DIR')

from phase2_rsync import RsyncOrchestrator

orch = RsyncOrchestrator(
    '$MANIFEST_PATH',
    '$REMOTE_HOST',
    '$REMOTE_BASE',
    '$OUTPUT_DIR/rsync_batches'
)
orch.run_dry_run("1")
PY

    echo ""
    read -p "Dry-run looks correct? Proceed with all sequences? [y/N] " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Review and run manually:"
        echo "  cd $OUTPUT_DIR/rsync_batches && ./run_all.sh"
        exit 0
    fi
else
    echo "Skipping dry-run."
fi

# ─────────────────────────────────────────────────────────────────────
# PHASE 4: EXECUTE TRANSFERS
# ─────────────────────────────────────────────────────────────────────

echo ""
echo ">>> PHASE 4: Execute Transfers"
echo ""

read -p "Run all sequence transfers now? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$OUTPUT_DIR/rsync_batches"
    ./run_all.sh
    EXIT_CODE=$?
    cd - >/dev/null
    if [[ $EXIT_CODE -ne 0 ]]; then
        echo "[ERROR] Transfer failed with exit code $EXIT_CODE"
        exit $EXIT_CODE
    fi
else
    echo "To run manually:"
    echo "  cd $OUTPUT_DIR/rsync_batches && ./run_all.sh"
    echo "  # Or parallel:"
    echo "  cd $OUTPUT_DIR/rsync_batches && ./run_parallel.sh"
fi

# ─────────────────────────────────────────────────────────────────────
# PHASE 5: VERIFICATION (if phase3_verify.py available)
# ─────────────────────────────────────────────────────────────────────

echo ""
echo ">>> PHASE 5: Post-Transfer Verification"
echo ""

if [[ -f "$SCRIPT_DIR/phase3_verify.py" ]]; then
    read -p "Run verification now? [y/N] " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 <<PY
import sys
from pathlib import Path

sys.path.insert(0, '$SCRIPT_DIR')

try:
    from phase3_verify import TransferVerifier

    v = TransferVerifier('$MANIFEST_PATH', '$REMOTE_HOST', '$REMOTE_BASE')
    v.verify_all(deep=False)
except ImportError as e:
    print(f"[WARN] phase3_verify not available: {e}")
except Exception as e:
    print(f"[ERROR] Verification failed: {e}")
PY

        read -p "Run deep MD5 verification? [y/N] " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 <<PY
import sys
from pathlib import Path

sys.path.insert(0, '$SCRIPT_DIR')

try:
    from phase3_verify import TransferVerifier
    v = TransferVerifier('$MANIFEST_PATH', '$REMOTE_HOST', '$REMOTE_BASE')
    v.verify_all(deep=True)
except Exception as e:
    print(f"[ERROR] Deep verification failed: {e}")
PY
        fi
    fi
else
    echo "[SKIP] phase3_verify.py not found"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  PIPELINE COMPLETE"
echo "═══════════════════════════════════════════════════════════════"
echo "  Output directory: $OUTPUT_DIR"
echo "  Manifests:        $OUTPUT_DIR/manifests/"
echo "  Batches:          $OUTPUT_DIR/rsync_batches/"
echo "  Logs:             $OUTPUT_DIR/logs/"
echo ""
echo "  To re-verify:"
echo "    python3 phase3_verify.py $MANIFEST_PATH $REMOTE_HOST $REMOTE_BASE"
echo "═══════════════════════════════════════════════════════════════"
