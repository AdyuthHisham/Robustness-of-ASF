#!/usr/bin/env bash
# scripts/alvis/submit_all.sh — run ON Alvis, from inside the deployed
# kradar_visibility directory. Submits the array job, then the merge job
# with a dependency on it, and prints both job IDs.

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."

ARRAY_JOB=$(sbatch --parsable scripts/alvis/array_job.sbatch)
echo "Array job submitted: ${ARRAY_JOB}"

MERGE_JOB=$(sbatch --parsable --dependency=afterok:"${ARRAY_JOB}" scripts/alvis/merge_job.sbatch)
echo "Merge job submitted: ${MERGE_JOB} (runs after ${ARRAY_JOB} completes ok)"

echo ""
echo "Monitor with: squeue -u \$USER"
echo "Or:           sacct -j ${ARRAY_JOB},${MERGE_JOB} --format=JobID,JobName,State,Elapsed,ExitCode"
