# Alvis migration plan: kradar_visibility full-dataset run

Status: planning only, no code/scripts written yet.
Scope: `test-bed/src/Modules/robust_testing/kradar` (package `src/kradar_visibility`, entry `scripts/run_full_sequence.py`).

## 0. Facts this plan is built on

- Pipeline is **strictly single-threaded, single-process** — no multiprocessing/joblib/concurrent.futures anywhere in `pipeline.py` or `run_full_sequence.py`. Parallelism must come from job-level sharding, not in-process threads. This is why an array job (§2) is the right shape, not a request for more cores per task.
- `run_full_sequence.py` already operates **one sequence per invocation** and writes **one Parquet + one error log per sequence** (`outputs/output_seq{N}_full.parquet`, `--sequence`/`--dataset-root`/`--output`/`--error-log` all overridable via CLI). This is a de facto shard already — no code changes needed to get per-sequence output, only to point `--dataset-root`/`--output` at cluster paths.
- No merge/concat tooling exists yet (`scripts/summarize_output.py`, `scripts/validate_output.py` both operate on a single file). A merge step is new but trivial (`pl.concat` + `write_parquet`, ~10 lines).
- `uv.lock` does not currently exist in the working tree despite the subproject being uv-managed — regenerate with `uv lock` before shipping to Alvis, don't assume it's there.
- `config.py:DATASET_ROOT` is hardcoded to a local absolute path; must be overridden via `--dataset-root` on Alvis, not edited in place (avoid committing a machine-specific default).
- Architecture doc explicitly states this pipeline was validated at toy scale ("1-2 sequences, ≤20 frames... seconds on CPU") and full-dataset/HPC runs are *out of documented scope* — treat this as a first real stress test, budget contingency accordingly (§4, §5).
- No existing sshfs-stall reports specific to this pipeline were found in-repo; the sshfs-stall concern in the task brief is inferred from general experience with the mount, not a logged incident in this codebase. Direct on-cluster I/O (§5) removes the mechanism regardless.

## 1. Getting repo + environment onto Alvis

**Transfer: `git clone` over `rsync`.** The repo is already a git repo with submodules; `alvis2.c3se.chalmers.se` is a normal SSH target, so `git clone --recurse-submodules <repo-url>` (or clone + `git submodule update --init` if only `K-Radar`/`AMSCUP_PLUS` submodule pointers are needed — they're read-only dataset/tooling refs, not required if reading data directly from Cephyr/Mimer, see §5) is simpler and gives clean version tracking on the cluster side vs. rsync's one-shot copy with no history. rsync is only preferable for iterating on uncommitted local changes before they're pushed; default to clone, use `rsync -av --exclude .git` for a quick throwaway sync during initial debugging if needed.

Only `test-bed/src/Modules/robust_testing/kradar` need be present — it's a workspace member with its own `pyproject.toml`; you don't need to sync all of `repos/K-Radar` or `repos/AMSCUP_PLUS` since data will be read directly from Cephyr/Mimer, not the sshfs-mounted submodule paths.

**Python env: `uv`, not module-based venv.** `uv` is a static, self-contained Rust binary with no system dependency — it does not need to exist as an Alvis environment module. Install once to the user's home (persists across jobs):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This must run from a node with outbound internet — confirm `alvis2` (login/transfer node) has it; compute nodes are typically air-gapped, so **do this once on alvis2, not inside the SLURM job**. If alvis2 has no outbound internet either, fall back to `pip install --user uv` using whatever `module load Python/...` gives you as a bootstrap, then use that `uv` for everything else — a bootstrap escape hatch, not the primary path, since CLAUDE.md mandates uv exclusively for this subproject.

Before first run: `cd kradar && uv lock && uv sync` — regenerates the missing lockfile against Alvis's platform (Icelake x86_64, same arch as local dev, so no cross-compilation surprises expected for numpy/scipy/pyarrow/opencv-python-headless wheels). Run `uv sync` once on alvis2 (or interactively on a NOGPU compute node via `srun`) before the array job — SLURM array tasks should not each independently resolve/install dependencies; they should activate a pre-built `.venv`.

Flag the suspicious `test-bed/pyproject.toml` workspace member entry (`"src/Modules/robust_testing/kradar/kradar_visibility"` — looks like a stale/duplicate path since `kradar_visibility` is a package dir under `src/`, not its own pyproject location) — check `uv sync`/`uv lock` don't choke on it before relying on workspace-wide commands; if it errors, sync from inside the `kradar/` directory specifically rather than fixing the workspace file (out of scope for this task per "no code changes yet").

## 2. Job structure: array job, one task per sequence

**Recommendation: SLURM job array, one task per sequence — not a single looping job.**

Reasoning:
- Per-sequence CPU runtime was informally observed at ~2.5hr locally (sequence 2, 462 frames / 187 annotated / 222 objects). K-Radar has dozens of sequences (confirm exact count/IDs once the dataset path is reachable on Alvis — `ls /cephyr/.../datasets/kradar` or equivalent under whichever of the two listed Cephyr kradar paths holds the raw sequence directories; do this as the first live step before submitting anything). At ~2.5hr/sequence, a single serial loop over all sequences is many-times-10-hours of wall time — this blows past typical walltime limits on shared partitions and wastes the whole allocation on one job that dies if any single sequence hits an edge case (a known risk here — this pipeline's error handling degrades to zeroed scores per-object/per-frame, but an unhandled exception at the *sequence* level, e.g. a corrupt label file crashing `run_full_sequence.py`'s outer loop before its try/except, would kill everything downstream in a single-job design).
- An array job (`--array=0-N%K`) gives independent walltime/failure isolation per sequence: one bad sequence fails one array task, not the whole run, and `sacct`/exit codes tell you exactly which sequence(s) need a rerun. This matches `run_full_sequence.py`'s existing per-sequence CLI/output model with zero code restructuring.
- `%K` throttle (e.g. `%12`) caps concurrent array tasks to be a good cluster citizen and to match how many NOGPU nodes/cores you actually want in flight at once.
- Single-node parallelism is a dead end anyway since the pipeline has no in-process concurrency — running multiple sequences *within* one job would require manually backgrounding multiple `python` invocations and managing their I/O contention yourself, which is just a worse version of what job arrays give for free.

## 3. Output strategy: per-task shard + merge job

- Each array task writes its own shard: `outputs/shards/output_seq${SLURM_ARRAY_TASK_ID}.parquet` + matching `.errors.log`, using `run_full_sequence.py --sequence $ID --dataset-root <cluster-path> --output outputs/shards/output_seq${ID}.parquet --error-log outputs/shards/output_seq${ID}.errors.log`. No code change needed — this is exactly the script's existing per-sequence CLI contract.
- Output location: **Mimer** (`/mimer/NOBACKUP/groups/naiss2025-22-321/...`), not Cephyr scratch or job-local disk, for two reasons: (a) it's already a listed accessible path for this project, (b) Mimer is the InfiniBand-backed fast storage tier at Chalmers — better for the merge job's read-heavy concatenation pass than Cephyr, which is being used here as a slower bulk dataset store. `alvis-cpu1`'s 3.4TB local SSD scratch is an option for *intermediate* per-task scratch (fast local writes during a task, then copy the finished shard to Mimer at task end) if I/O contention on Mimer becomes a bottleneck with many concurrent array tasks — start without this optimization, add it only if observed necessary.
- Merge job: separate small job submitted with `--dependency=afterok:<array_job_id>` so it only runs once every array task has exited 0. It globs `outputs/shards/output_seq*.parquet`, `pl.concat()`s them, writes `outputs/kradar_visibility_full.parquet`. Needs the same `.venv` (polars) but trivial resources (single core, a few GB RAM, minutes of walltime) — do not oversize this job.
- `afterok` (not `afterany`) is deliberate: if any sequence fails, halt before merging a knowingly-incomplete combined table; inspect and rerun failed array indices individually, then merge manually or resubmit the dependency chain.
- Keep shards even after merging (don't have the merge job delete them) — they're the natural unit for re-running a single failed/updated sequence without re-running everything.

## 4. Resource sizing per array task

Local CPU profile is not rigorously logged in-repo (no persisted memory-usage report, no formal walltime log beyond the informal "~2.5hr for seq 2" and the smoke-suite's own timeout note: full-pipeline smoke tests were excluded from CI because they exceed 360s even on toy 1-2-sequence/20-frame subsets — consistent with a genuinely CPU-heavy per-frame cost, not a fluke). Given that:

- **Cores**: 1 core is sufficient per task — the pipeline is single-threaded and won't use more. Request `-c 2` as a small safety margin for OS/I/O overhead and any incidental threading inside numpy/opencv BLAS calls, not more; requesting a full 32/64-core node per sequence would badly under-utilize Alvis NOGPU capacity across a multi-dozen-sequence array.
- **Memory**: the largest per-frame allocation is the radar zyx_cube voxel grid (250×400×150 floats ≈ 15M cells; at float32 that's ~60MB per frame, held one frame at a time per `data_loader.py`'s lazy per-frame loading — not the whole sequence in memory at once per architecture.md's data-flow description). Realistic working set should be well under a few GB; request **8GB** per task as a safe margin (covers numpy/opencv/polars overhead, calibration pickles, and any transient copies) without needlessly starving other jobs on the shared 512-768GB nodes.
- **Walltime**: request `-t` with real margin over the observed 2.5hr — e.g. `08:00:00` — since (a) that timing was for sequence 2 specifically and other sequences may have different frame counts, (b) this is explicitly the first full-scale/HPC run of this pipeline (architecture.md scopes it out), so treat the 2.5hr figure as a lower bound, not a tight estimate, until at least one array task completes on Alvis and its actual wall-clock is observed.
- **Node type**: any NOGPU node works given the light per-task footprint (`alvis-cpu1` or `alvis10-14`); no need to target the local-SSD `alvis-cpu1` specifically unless you adopt the local-scratch-then-copy optimization from §3. Just require `-C NOGPU` and let SLURM schedule to whichever is free — don't pin a specific node name, that only adds queue wait time.
- Confirm sequence count once the dataset path is reachable and set the array range accordingly (`--array=1-N%K` matching actual sequence IDs, which may not be a dense 1..N range — check for gaps before assuming).

## 5. Codebase-specific risks

- **Half-extent vs full-extent bug class**: verification report already confirmed this is guarded against as of the last audit (`pipeline.py` consistently uses `*_half` fields; `lidar_visibility.py` works directly in full-extent world-frame bboxes) — not expected to resurface, but re-run the existing `tests/test_verify.py` correctness suite once on Alvis against real cluster-mounted data before trusting the full-dataset run, since verification was presumably last run against local/sshfs data and this is a different filesystem/mount path.
- **sshfs stalls**: no incident is actually logged for *this* pipeline (the sshfs-stall history found in-repo belongs to the separate ASF/GPU migration in `AMSCUP_PLUS`, a different codebase). Regardless, reading directly from Cephyr/Mimer on-cluster removes sshfs (a FUSE network-filesystem layer with known small-file-latency problems, particularly for workloads like this one that open many small per-frame `.mat`/`.pcd`/label files) from the path entirely — Alvis compute nodes reach Cephyr/Mimer over the cluster's native high-speed fabric, not a re-exported network mount. This alone should resolve the class of problem even without confirmed root-causing of the original stall.
- **Cephyr vs Mimer**: Cephyr is the bulk dataset store here (`kradar_pre/processed`, `kradar_pre/trained`, raw `kradar`, `revise_label` tooling) — fine for read-heavy sequential per-frame access during a task. Mimer (`naiss2025-22-321/.../KRadar_refined_label_by_UWIPL`) is the InfiniBand-backed fast tier — use it for pipeline **output** (shards + merge), and prefer it if any part of the read path turns out to be a bottleneck, but don't move the whole dataset there without checking quota — Mimer allocations are typically much smaller than bulk Cephyr storage.
- **`radar_tesseract` guard**: confirm `--dataset-root` on Alvis actually points at a tree containing `radar_zyx_cube/` (not only raw `radar_tesseract/`) for every sequence — if any sequence's preprocessed zyx_cube is missing on Alvis (e.g. only raw tesseract data was transferred/mounted there), `data_loader.py` will silently degrade every radar score to `visible=False, score=0.0` for that whole sequence rather than error, per its designed missing-file behavior — this would produce a *quietly* incomplete/wrong output rather than a job failure. Worth a `ls`-based sanity check per sequence before running the full array, and worth checking the per-sequence error log + summary stats after each task for suspiciously all-zero radar columns.
- **uv.lock drift**: since the lockfile doesn't currently exist, the exact resolved versions that will run on Alvis are not yet pinned to anything tested. Generate it there, commit it, and don't regenerate mid-campaign (a `uv sync` triggered by a mid-array-job dependency change would be a reproducibility hazard across array tasks running at different times).
- **CFAR noise-floor gap** (pre-existing, unrelated to migration): `pipeline.py` already runs with `noise_floor_db=None`, silently using a per-frame global median fallback instead of the intended spatial CFAR map — not a migration risk per se, but worth noting so an unexpectedly uniform-looking `radar_score` distribution across the full dataset isn't mistaken for a new bug introduced by the cluster run.

## 6. Illustrative directory layout

```
kradar/                              # on Alvis, cloned repo subtree
├── .venv/                           # uv-managed, built once via `uv sync`
├── outputs/
│   ├── shards/
│   │   ├── output_seq1.parquet
│   │   ├── output_seq1.errors.log
│   │   ├── output_seq2.parquet
│   │   ├── output_seq2.errors.log
│   │   └── ...
│   └── kradar_visibility_full.parquet   # merge job output
├── slurm_logs/
│   ├── array_%A_%a.out
│   └── merge_%j.out
└── scripts/
    ├── run_full_sequence.py         # existing, unmodified
    └── merge_shards.py              # new, not yet written
```

## 7. Illustrative sbatch skeletons (NOT final — for shape/review only)

Array job:

```bash
#!/bin/bash
#SBATCH -A <project>
#SBATCH -p alvis
#SBATCH -C NOGPU
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 08:00:00
#SBATCH --array=1-58%12          # placeholder range — confirm real sequence IDs first
#SBATCH -o slurm_logs/array_%A_%a.out
#SBATCH -J kradar_vis

cd $SLURM_SUBMIT_DIR
source .venv/bin/activate        # or: uv run --no-sync ...

SEQ=$SLURM_ARRAY_TASK_ID
python scripts/run_full_sequence.py \
  --sequence "$SEQ" \
  --dataset-root /cephyr/users/adyuth/Alvis/Desktop/cephyr_c3se2025-3-18/datasets/kradar \
  --output outputs/shards/output_seq${SEQ}.parquet \
  --error-log outputs/shards/output_seq${SEQ}.errors.log
```

Merge job (submitted after, with `--dependency=afterok:<array_job_id>`):

```bash
#!/bin/bash
#SBATCH -A <project>
#SBATCH -p alvis
#SBATCH -C NOGPU
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -t 00:30:00
#SBATCH -o slurm_logs/merge_%j.out
#SBATCH -J kradar_vis_merge

cd $SLURM_SUBMIT_DIR
source .venv/bin/activate
python scripts/merge_shards.py \
  --shard-glob "outputs/shards/output_seq*.parquet" \
  --output outputs/kradar_visibility_full.parquet
```

Submission sequence:

```bash
ARRAY_JOB=$(sbatch --parsable array_job.sbatch)
sbatch --dependency=afterok:${ARRAY_JOB} merge_job.sbatch
```

## 8. In-sequence parallelism (implemented)

`scripts/run_full_sequence.py` now takes `--workers N`. Frames within a sequence are independent (each loads its own sensor files and returns its own rows), so `N>1` dispatches them to a `ProcessPoolExecutor` instead of the original serial per-frame loop — processes, not threads, since the work is CPU-bound array/OpenCV math that would contend on the GIL under threading. `--workers 1` (default) is byte-identical to the pre-existing serial behavior.

- BLAS/OpenMP thread pools (`OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`) are pinned to `1` at import time (via `os.environ.setdefault`, so an sbatch-supplied value is respected, not overridden) to prevent numpy/OpenCV's internal threading from oversubscribing cores the process pool is also using.
- Verified on real data (sequence 2, local dev machine): 4 workers over 6 frames gave a ~1.9x wall-clock speedup (135s → 72s), below the naive 4x due to shared I/O contention on this machine — expect a better ratio on Alvis given more cores and, per §5, faster/less-contended storage access than the local sshfs path this was benchmarked over.
- Output is content-identical between worker counts (validated via a full-row `polars` equality check after sorting by `(frame_idx, obj_tracking_id)`), though row order can differ since parallel results are assembled as they complete rather than strictly in frame order.
- Practical effect on §4 sizing: bump `-c` per array task to match the desired `--workers` value (e.g. `-c 16 --workers 16`) rather than leaving it at the placeholder `-c 2`; re-measure per-sequence walltime once run on Alvis before finalizing `-t`.
- New tests: `tests/test_parallel_smoke.py` (SMK-18: thread-env pinning, fast, no dataset; SMK-19: serial vs. parallel output parity on real data, `slow`; SMK-20: one frame failing under a worker pool doesn't crash the pool or lose other frames' rows, `slow`). Run via `uv run pytest tests/test_parallel_smoke.py` (fast) and `-m slow` (real-data tests, ~35s–4min each on this machine).

## 9. Dataset-split runner + bundled split files (implemented)

Added `scripts/run_split.py`: a multi-sequence driver that runs the pipeline over a K-Radar train/test split (e.g. `resources/split/test.txt` — one line per frame, `"<sequence_id>,<label_filename>"`, selecting a subset of frames *within* each sequence, not held-out sequences) rather than every frame. Each sequence writes its own shard (resumable — an existing shard is skipped unless `--overwrite`), and shards are concatenated into one combined Parquet at the end.

- `resources/split/test.txt` and `train.txt` are **bundled inside the kradar_visibility subproject** (`resources/split/`, copied from the K-Radar repo's own `resources/split/`) rather than read from the separate K-Radar git submodule. This means the "only `kradar/` needs to be transferred" claim in §1 now actually holds with no exceptions — the split files would otherwise have been the one thing requiring the K-Radar submodule on Alvis too.
- `run_split.py --sequences <id>` processes one sequence — this is exactly the SLURM array-job unit of work (§2); `array_job.sbatch` (§10) calls it with `--sequences $SLURM_ARRAY_TASK_ID`.
- Validated end-to-end locally: full test-split frames for sequences 1+2 (531 frames) — 1,243 output rows, zero frame errors, correct per-object schema, resumability confirmed (rerun skips existing shards, still merges correctly).
- **Found and fixed a real correctness bug during this validation**: `lidar_visibility.py`'s occlusion computation used horizontal-only (x,y) range where it needed true 3D range (x,y,z), causing `arcsin` domain errors (→ `NaN`, silently misrouted to the wrong LUT channel) and systematically underestimating occlusion for any object with vertical offset from the sensor — corrupting `lidar64/128_sparsity_score` for affected objects. One-line fix (`lidar_visibility.py:266`); confirmed via smoke suite + targeted re-run of the previously-affected frames under `-W error::RuntimeWarning`. This means any output produced before this fix (including the local seq1/seq2 validation shards from the first pass) is stale and must be regenerated.

## 10. Alvis job scripts (implemented, illustrative account string only)

Added under `scripts/alvis/`:

- **`push_to_alvis.sh`** — run locally. `rsync`s the kradar_visibility subproject to Alvis (`~/kradar_visibility` by default), excluding `.venv`/`outputs`/caches.
- **`bootstrap_env.sh`** — run once on `alvis2` (needs outbound internet) after pushing. Installs `uv` if missing, runs `uv lock && uv sync`, sanity-imports the package.
- **`array_job.sbatch`** — `--array=1-58%12`, one task per sequence, calls `run_split.py --sequences $SLURM_ARRAY_TASK_ID --workers 16 --skip-merge`, reading from Cephyr and writing shards to a Mimer output dir.
- **`merge_job.sbatch`** — submitted with `--dependency=afterok:<array_job_id>`; calls `run_split.py` with no `--sequences` (full split), which skips every already-done shard instantly and just concatenates.
- **`submit_all.sh`** — run on Alvis, submits both with the dependency wired up automatically, prints job IDs and a `sacct` command to watch them.

All `#SBATCH -A <NAISS_COMPUTE_PROJECT>` lines are placeholders — see open item #1 below.

## 11. Open items resolved / still open

Resolved via the live sshfs mount to Cephyr (already reachable from local dev — confirmed the mount source paths match the task brief's Cephyr paths exactly):
- ~~Exact sequence count/IDs~~ — **58 sequences (1-58)**, matching both split files exactly.
- ~~Confirm `radar_zyx_cube/` presence~~ — **confirmed present for all 58 sequences** (not just raw `radar_tesseract/`).

Still open (need Alvis-side access I don't have — direct SSH from this machine gets `Permission denied`; only the pre-established read-only sshfs mounts are reachable):
1. **NAISS/C3SE compute project account string** for `#SBATCH -A` — required before any script here can actually submit.
2. Confirm `alvis2` has outbound internet for the `uv` installer (`bootstrap_env.sh` needs this once), or provide the module-based Python fallback if not.
3. Whether `test-bed/pyproject.toml`'s workspace member list needs fixing before `uv sync` works cleanly from inside `kradar/`, or whether it's a non-issue when syncing from that directory directly (untested on Alvis; local `uv sync` from within `kradar/` has not hit this).
4. Real per-sequence wall-clock at `--workers 16` on actual Alvis NOGPU cores — only benchmarked up to 4 workers locally (§8, memory-constrained dev box); use the first few array tasks' actual runtime to tune `-c`/`--workers`/`-t` before letting the full array run unattended.
5. Confirm the chosen Mimer output subdirectory (`/mimer/NOBACKUP/groups/naiss2025-22-321/projects/AMSCUP/kradar_visibility/`) is fine to create, or provide a preferred path.
