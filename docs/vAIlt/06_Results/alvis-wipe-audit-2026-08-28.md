# Alvis Wipe Audit — 2026-08-28

Read-only audit ahead of cluster wipe (2026-08-29). No files copied, synced, or modified — this is a report only.

**Revision 2 (verification pass):** the original pass under-counted orphans because its SLURM search only looked for `.out`/`.err` files under `test-bed/.../slurm_logs/` and never scanned `repos/K-Radar/` root, where a second, larger ASF corruption-sweep job set logs to `.log` files. A full-tree path diff (remote listing vs. local disk, git-history-aware) plus targeted spot-checks caught this and two smaller misses. Corrections are marked **[REV2]** below; nothing in the original findings was wrong, they were just incomplete.

## Summary

| Path | Files | Total size | >100MB files | Files modified since 2026-07-29 |
|---|---|---|---|---|
| `/cephyr/users/adyuth/Alvis` | 47,558 | 23.5 GB | 25 | 38,294 |
| `/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth` | 569,475 | 4.2 GB | 4 | 567,575 |
| `/mimer/NOBACKUP/groups/naiss2025-22-321/users/adyuth` | 2,010,567 | 26.3 GB | 27 | 0 |

**Full-enumeration check (rev2):** re-ran `find -type f` fresh against all three paths — counts matched the original run exactly (47,558 / 569,475 / 2,010,567), 0 stderr lines, 0 "Permission denied" entries on any path. No timeouts, no truncation, no sampling — every file was walked both times.

**Key finding:** `/cephyr/NOBACKUP/.../adyuth/AMSCUP` is a near-complete mirror of the local git repo (same directory structure, `.venv`s, `.git` packs and all) — the huge "recent" count there is mostly rsync'd copies of files you already have locally, not new work. `/mimer/.../adyuth` (training outputs/containers) has zero files touched in 30 days — everything there is from an April–June 2026 training campaign, already stale.

**Orphaned / no local counterpart:** 6 flagged groups (see SLURM section) — **[REV2] up from 3**: added the `repos/K-Radar/asf*.log` job-log set, the `repos/K-Radar/outputs/alvis_seq*` raw per-frame output tree, and `repos/K-Radar/scripts/alvis/recon_seq32.sbatch`.
**Failed/incomplete jobs:** 2 groups — **[REV2] up from 1**: the already-noted superseded `array_6929473` (no action needed), plus a genuinely-unaddressed one — **144 ASF `camera_frame_deletion_new` runs crashed mid-run** (container exit=134) and need rerunning before the wipe if that condition/sequence combination matters to the sweep.

### Verification methodology (rev2)

1. **Full re-enumeration:** fresh `find -type f -printf '%s\t%TY-%Tm-%Td\t%p\n'` against all three paths, diffed file counts against the original report — exact match, all three paths, 0 errors.
2. **Sample verification of "has local counterpart" claims:** 8 direct file-existence/size checks (prediction batches, merged parquet/txt outputs) — **8/8 passed**, except `random_sample_gallery.html` where remote (427,613,003 bytes, 2026-08-18) and local (378,308,613 bytes, 2026-08-17) sizes **do not match** — reclassified below from implicit-skip to SYNC. A 6-file random sample of `.sbatch`/`.sh` scripts — **5/6 passed** (found on disk); 1 failure (`recon_seq32.sbatch`, not on disk and not in `git log --all`) — added to orphan list.
3. **Full-tree orphan re-scan:** built a complete remote relative-path list (554k candidate paths after excluding `.venv`/`.git`/`.cache`/`__pycache__`) and diffed against a complete local disk listing (761k paths, excluding the same junk plus the read-only `repos/K-Radar/data` and `resources` dataset mirrors which are identical on both sides and not "work product"). Most of the ~554k raw diff lines are false positives from two sources that a naive path diff can't see: (a) the K-Radar dataset tree itself, excluded explicitly; (b) **git-tracked reorganizations** — e.g. `docs/vAIlt/*.md` flat files that the remote checkout still has at old paths, but which were moved into the PARA folder structure locally via commits `43ce859`/`c341a50` (verified via `git log --all --diff-filter=AD`) — these are not orphans, just a stale remote checkout. After excluding the dataset mirror and manually confirming the vault-reorg pattern accounts for the vAIlt hits, the diff surfaced three genuine, non-false-positive orphan groups (below) that the original pass missed entirely.

---

## SLURM / Prediction Outputs (time-sensitive)

Job arrays found under `/cephyr/NOBACKUP/.../AMSCUP/test-bed/src/Modules/robust_testing/kradar/slurm_logs/`:

- [ ] **`array_6929473` (21 tasks, 2026-08-11)** — 12/21 tasks show `CANCELLED` in `.out` logs (`_9`–`_21` excluding `_13`). **SKIP** — superseded by `array_6929609` (58 tasks, same day range, completed) and the later `regen_sedan_bus_6951648` (58 tasks, 2026-08-20, all completed, confirmed via tail: `COMPLETE: ... 0 errors`). No rerun needed before wipe.
- [ ] **`array_6929609` (58 tasks, 2026-08-11)** — all completed. Outputs land in `outputs/shards/output_seq*.parquet`. **SKIP** (see shards note below — partially orphaned as raw shards, but content is already folded into local merged outputs).
- [ ] **`array_6929605` (3 tasks)**, **`verify_lidar_vec_*` (3 single jobs)** — small verification jobs, `.out` sizes ~500B–16KB, no errors found. **SKIP**.
- [ ] **`regen_sedan_bus_6951648` (58 tasks, 2026-08-20)** — all completed successfully, output dir `outputs/shards_sedan_bus/`. **See orphan below — SYNC.**
- [ ] **`test_single_6951647`** — single validation run preceding the array above. **SKIP**, trivial.
- [ ] **[REV2] `asf*_<condition>_<jobid>.log` (1,498 files, 65.1 MB, most recent 2026-08-27)** at `repos/K-Radar/` root (not under `slurm_logs/` — missed in the original pass because it only searched `.out`/`.err` under `test-bed/.../slurm_logs/`). This is the **ASF corruption-sweep job set** — each log embeds a full run manifest (sequence, noise condition, seed, `checkpoint` path, `git_sha`, `slurm_job_id`), matching the project's established per-run reproducibility logging pattern. **1,354/1,498 completed OK** ("ASF run OK" + full prediction count). **144/1,498 CRASHED** — see failed-tasks entry below. **Recommendation: SYNC the logs (65 MB, cheap) for provenance before they're gone; the crashed 144 need a rerun decision, not just a sync.**
- [ ] **[REV2] `outputs/alvis_seq*/` full tree (552,024 files, 267 MB, spans all 58 sequences)** at `repos/K-Radar/outputs/`. This is the raw per-frame prediction/sensor-dump output of the ASF sweep the logs above describe. **Local has only 12 of the 58 `alvis_seq*` sequence directories** (`alvis_seq{1,2,7,8,9,10,16,18,41,46,48,55}`), and those may themselves be partial subsets rather than full copies — not independently verified given the file count. **Recommendation: UNSURE, but high-priority to decide** — if `all_preds_batch*.txt`/`all_gts_batch*.txt` (dated 2026-08-27, same day these jobs finished) were built from this tree, the aggregate may already be safe locally and the raw dump is disposable; if the per-condition/per-frame granularity is needed later (e.g. to redo a merge or investigate one of the 144 crashes), this is the only copy and pulling all 267 MB is cheap relative to losing it. Recommend at minimum syncing the 46 sequence dirs missing locally before deciding to discard.
- [ ] **[REV2] `scripts/alvis/recon_seq32.sbatch`** at `repos/K-Radar/scripts/alvis/` — confirmed missing from local disk and absent from `git log --all --diff-filter=A` (never committed). Sibling scripts (`ingest_original_all_iou.sbatch`, `run_metrics.sbatch`, etc.) in the same directory all verified present locally. **Recommendation: SYNC — single small script file, otherwise permanently lost.**

### Failed/incomplete job tasks needing a rerun decision (rev2 addition)

- [ ] **[REV2] 144 ASF `camera_frame_deletion_new_{low,medium,high}` runs crashed** (container exit=134, mid-run Python exception, verified via log tail e.g. `asf11_camera_frame_deletion_new_high_6967810.log`: "ASF run CRASHED ... only 1 partial prediction files written before abort -- NOT a complete sequence, do not treat as OK"). All 144 failures are confined to the `camera_frame_deletion_new_*` condition across multiple sequences (verified via `grep -L 'ASF run OK'` returning exactly 144 matches, all under that condition family) — every other ASF condition in the sweep completed cleanly. **Recommendation: decide whether `camera_frame_deletion_new` is still a condition you need in the final sweep; if yes, this needs to be rerun before the wipe since the checkpoint (`ASF_v2_0_final_10.pt`) and exact config are still resolvable from the log manifests.**

### Orphaned outputs — no local counterpart (highest priority)

- [ ] **`outputs/shards_sedan_bus/`** (58× `seq_*.parquet` + `.progress.log`/`.errors.log`, ~174 files, **8.8 MB total**, last modified 2026-08-20) — path: `/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth/AMSCUP/test-bed/src/Modules/robust_testing/kradar/outputs/shards_sedan_bus/`. Local repo has **only the sbatch script** (`scripts/alvis/regen_sedan_bus.sbatch`), no output data at all. This is the "sedan/bus" regen job output referenced by the frame-identifier-bug fix work and has never been pulled down. **Recommendation: SYNC — small, cheap, and otherwise lost.**
- [ ] **`outputs/shards/output_seq*.parquet`** (58 files present remotely, only 3 present locally: `output_seq{1,2,3}.parquet`, all dated 2026-08-11) — path: `.../AMSCUP/test-bed/src/Modules/robust_testing/kradar/outputs/shards/`. These are the raw per-sequence shards behind the original visibility pipeline run; local repo is missing 55 of 58. However, local `all_preds.txt`/`all_gts.txt`/batches are dated 2026-08-27 (post-dating this run), so the aggregate is very likely already folded into current merged outputs. **Recommendation: UNSURE — pull only if you need the raw per-seq shards for a future re-derivation; otherwise the merged product already supersedes them.**
- [ ] **`output_regen/output_with_env_density.parquet`** (56 KB, 2026-08-13) — path: `.../AMSCUP/test-bed/src/Modules/robust_testing/kradar/output_regen/`. Local has no `output_regen/` dir, but does have a larger, newer version at `outputs/output_with_env_density.parquet` (7.5 MB, 2026-08-20) — same filename, clearly a later regeneration. **Recommendation: SKIP — superseded by the local/synced 2026-08-20 version.**

### Cross-check vs `all_preds_enriched.parquet` / `all_gts.txt` / `all_preds.txt`

Local `outputs/batches/` (11 batches each of `all_gts_batch*.txt` / `all_preds_batch*.txt`, all dated 2026-08-27) matches the remote batch files under `.../AMSCUP/repos/K-Radar/outputs/batches/` byte-for-byte in filenames present (both have batches 1–11, `all_preds_original_refresh.txt`, `all_gts_original_refresh.txt`). **This set is already synced — no action.** Remote also retains three `.bak_*` snapshots (`all_preds.txt.bak_pre_merge_20260825`, `.pre_shift_removal.bak`, etc., 20–100 MB each) which are pre-merge safety copies; local has its own equivalent `.bak` files under the same names with different suffixes (`bak_pre_pull_20260825`, `pre_original_refresh.bak`) — **these look like independent backup snapshots taken at different pipeline stages, not exact duplicates.** Flagged individually below.

---

## `/cephyr/users/adyuth/Alvis` (23.5 GB, 47,558 files)

Mostly unrelated legacy work: a `bevfusion`/nuScenes container environment (`Desktop/Containers/`) and a duplicate git checkout (`Desktop/combined-repo/`). Not part of the actively-tracked AMSCUP repo.

### Large files (>100MB)

- [ ] `Desktop/Containers/container/bevfusion_1_L.sif` — 9.4 GB, 2026-04-28. **UNSURE** — Apptainer container image for bevfusion/nuScenes work; expensive to rebuild if needed again, otherwise dead weight. Not referenced by current K-Radar visibility pipeline.
- [ ] `Desktop/Containers/container/dataAnalyzer.sif` — 3.4 GB, 2026-04-20. **UNSURE** — same call as above.
- [ ] `Desktop/Containers/src/bevfusion/nuscenes/nuscenes_infos_train_radar.pkl` — 1.3 GB, 2026-03-30. **SKIP** — derived nuScenes dataset index, regenerable from raw dataset if ever needed again; not part of K-Radar work.
- [ ] `Desktop/Containers/src/bevfusion/.git/objects/pack/tmp_pack_O9UJZj` — 579 MB, 2026-06-04. **SKIP** — git pack object, recoverable from the bevfusion upstream repo.
- [ ] `Desktop/combined-repo/.git/modules/local-project/objects/pack/pack-*.pack` — 410 MB, 2026-08-10. **SKIP** — this is a git pack of a duplicate AMSCUP checkout; local repo already has the real history.
- [ ] `Desktop/Containers/src/bevfusion/nuscenes/nuscenes_infos_val_radar.pkl` — 278 MB, 2026-03-30. **SKIP** — same as train pkl above.
- [ ] `Desktop/Containers/container/nuAnalysis.sif` — 254 MB, 2026-04-13. **UNSURE**.
- [ ] `Desktop/combined-repo/.git/modules/hpc-project/modules/src/K-Radar/objects/pack/pack-*.pack` — 246 MB, 2026-08-10. **SKIP** — duplicate of `repos/K-Radar` submodule history, already present locally.
- [ ] `Desktop/Containers/src/K-Radar/.git/objects/pack/pack-038baf...pack` and `Desktop/Containers/src/kradar/.git/.../pack-038baf...pack` (same pack, two locations) — 246 MB each, 2026-06-04/04-08. **SKIP** — duplicate K-Radar submodule clones.
- [ ] `Desktop/combined-repo/.git/objects/pack/pack-266293...pack` — 245 MB, 2026-06-04. **SKIP** — duplicate repo history.
- [ ] `parquet_venv/lib/.../_polars_runtime.abi3.so` and `.cache/uv/archive-v0/.../_polars_runtime.abi3.so` (×3, 175–216 MB each) — **SKIP** — cached Python wheel binaries, `uv sync` recreates these from lockfile.
- [ ] `Desktop/Containers/src/bevfusion/pretrained/*.pth` (camera-only-seg/det, bevfusion-seg/det/converted, swint-nuimages — 6 files, 110–201 MB each, 2026-04-09/05-05) — **UNSURE** — pretrained bevfusion checkpoints; only useful if you plan to resume nuScenes/bevfusion work, otherwise re-downloadable from upstream model zoo.
- [ ] `.cache/torch/hub/checkpoints/swin_s-5e29d889.pth` (199 MB) and `swin_tiny_patch4_window7_224.pth` (114 MB) — **SKIP** — standard torch-hub pretrained weights, auto-redownloaded on first use.
- [ ] `Desktop/Containers/src/bevfusion/.git/objects/dd/602d09...` — 135 MB, 2026-06-04. **SKIP** — git blob, part of bevfusion history already on GitHub.

### Notable recent (last 30 days) activity

38,294 files touched — almost entirely `.venv`/`.cache`/`uv` package installs (dependency reinstalls, not authored work) and the `Desktop/combined-repo/` duplicate checkout being kept in sync with local commits. No unique authored files beyond what's covered above and the `.sbatch` scripts (149 found; spot-checked several — they mirror the ones already tracked in `test-bed/.../scripts/alvis/` locally). **No action needed beyond the large-file calls above.**

**Not fully enumerated:** none — `find` completed cleanly for this path.

---

## `/cephyr/NOBACKUP/groups/c3se2025-3-18/users/adyuth` (4.2 GB, 569,475 files)

This is `AMSCUP/` — a full rsync mirror of the local repo (code, `.venv_fixed/`, `.git` packs, submodule checkouts). Only genuinely new content vs. local is covered in the SLURM/orphan section above. Everything else (source files, configs, `.venv_fixed` site-packages) is either already present locally or is disposable virtualenv content.

### Large files (>100MB)

- [ ] `repos/K-Radar/outputs/random_sample_gallery.html` — 427,613,003 bytes, 2026-08-18. **[REV2 correction] SYNC, not skip** — spot-check confirmed local copy exists but is a **different, older version**: 378,308,613 bytes, dated 2026-08-17. The remote file is 49 MB larger and a day newer — pull it to replace the local copy before the wipe.
- [ ] `.git/objects/pack/pack-bc7b5677...pack` — 410 MB, 2026-08-10. **SKIP** — remote git pack, local repo already has full history.
- [ ] `.git/modules/repos/K-Radar/objects/pack/pack-d4169ba0...pack` — 246 MB, 2026-08-10. **SKIP** — submodule git pack, already in local `repos/K-Radar/.git`.
- [ ] `test-bed/src/Modules/robust_testing/kradar/.venv_fixed/.../_polars_runtime.abi3.so` — 216 MB, 2026-08-13. **SKIP** — venv artifact, `uv sync` recreates.

### Backup snapshot files worth a manual diff before discard

- [ ] `repos/K-Radar/outputs/all_preds.txt.bak_pre_merge_20260825` — 102 MB, 2026-08-20. **UNSURE** — compare against local `all_preds.txt.bak_pre_pull_20260825` (different suffix/date) — may be a distinct checkpoint in the merge history worth keeping for provenance.
- [ ] `repos/K-Radar/outputs/all_preds.txt.pre_shift_removal.bak` — 84 MB, 2026-08-20. **UNSURE** — no obviously matching local `.bak` by that exact name; check before discarding, it documents a specific correction step (shift removal) in the frame-identifier-bug fix history.
- [ ] `repos/K-Radar/outputs/all_gts.txt` — 2.7 MB, 2026-08-27. Matches local `all_gts.txt` in name/date range. **SKIP** (already synced).

**Not fully enumerated:** none — `find` completed cleanly.

---

## `/mimer/NOBACKUP/groups/naiss2025-22-321/users/adyuth` (26.3 GB, 2,010,567 files)

No SLURM logs, `.out`/`.err`, or `.sh` scripts found here — this NAISS storage allocation holds only training containers and model output artifacts from an A2FUSION/K-Radar training campaign (April–June 2026). **Zero files modified in the last 30 days** — this entire path is stale relative to current work but may still hold irreplaceable trained checkpoints.

### Large files (>100MB)

- [ ] `containers/kradarV0.sif` — 10.3 GB, 2026-05-21. **UNSURE** — Apptainer image for K-Radar training; rebuildable from Dockerfile/recipe if one exists in `repos/K-Radar`, otherwise expensive to recreate.
- [ ] `containers/mmdetBev.sif` — 8.4 GB, 2026-05-07. **UNSURE** — same call.
- [ ] `output/kradar/exp_260506_135737_A2FUSION_.../models/model_{0-10}.pt` — 314 MB each (11 checkpoints across 2 experiment dirs `exp_260505_114109` and `exp_260506_135737`, plus a third partial run `exp_260430_142055` with 2 checkpoints) — **UNSURE, decide per-experiment**: these are trained A2FUSION model checkpoints. If the training results feed into current robustness/visibility work, **SYNC the final-epoch checkpoint of each experiment at minimum** (e.g. `model_10.pt` from `exp_260506_135737`); intermediate epoch checkpoints (0–9) can likely be SKIPped unless you need training-curve reproducibility.
- [ ] `output/kradar/*/utils/util_*.pt` — 330 MB each, same experiment dirs — optimizer/scheduler state. **SKIP unless you intend to resume training** (unlikely post-wipe without the container anyway).
- [ ] `output/kradar/*/train_iter/events.out.tfevents.*` — 130 MB each — TensorBoard logs. **UNSURE** — cheap to keep for a training-curve record if you want it, otherwise safely discarded once final metrics are extracted.
- [ ] `output/bevfusion/bevfusion_lidar-cam_voxel0075_...-5239b1af.pth` — 167 MB, 2023-05-31 (pre-existing pretrained weight, not generated by this project). **SKIP** — standard public bevfusion checkpoint, redownloadable.

**Not fully enumerated:** none — `find` completed cleanly, though the 2M-file count made per-file review infeasible; only the >100MB tier and directory-level structure were reviewed. If there's specific work product you expect under `output/kradar/` beyond the three experiment dirs found, say so and I'll re-query.

---

## Recommended action order before wipe

1. **Now, cheap, unambiguous:** `outputs/shards_sedan_bus/` (8.8 MB), `repos/K-Radar/asf*.log` (65 MB), `repos/K-Radar/scripts/alvis/recon_seq32.sbatch`, and the newer `repos/K-Radar/outputs/random_sample_gallery.html` (427 MB) — all confirmed to have zero or stale local copies, all cheap enough to just pull without further deliberation. **[REV2]**
2. **Decide, high-priority:** the 144 crashed `camera_frame_deletion_new` ASF runs **[REV2]** — determine whether that condition is still needed in the final sweep; if so, it must be rerun before the wipe (checkpoint + config are still resolvable from the surviving log manifests).
3. **Decide, high-priority:** `repos/K-Radar/outputs/alvis_seq*/` (267 MB, 552k files, only 12/58 sequence dirs present locally) **[REV2]** — check whether the raw per-frame dump is still needed given the same-day merged `all_preds_batch*`/`all_gts_batch*` outputs already exist locally; if there's any chance of needing to re-derive or debug at per-frame granularity, sync the 46 missing sequence dirs now.
4. **Decide:** whether any A2FUSION checkpoints on `/mimer/...` matter for ongoing work; if yes, pull at minimum the final-epoch `model_*.pt` per experiment (3 experiments × ~314 MB = <1 GB) before the wipe.
5. **Decide:** whether the two `.bak` prediction-history files on cephyr NOBACKUP (`all_preds.txt.bak_pre_merge_20260825`, `all_preds.txt.pre_shift_removal.bak`) contain a distinct correction stage worth preserving for provenance, or are superseded by local `.bak` files of the same lineage.
6. **Low priority / optional:** the two large `.sif` containers and bevfusion pretrained weights on `/cephyr/users/adyuth/Alvis` and `/mimer/...` — only worth pulling if you expect to resume nuScenes/bevfusion or K-Radar training work without cluster access to rebuild them.
7. Everything else (venvs, git packs, uv/torch caches, duplicate checkouts, and the `docs/vAIlt/*` flat-file paths that a naive diff flags — those were moved into the PARA folder structure locally via commits `43ce859`/`c341a50`, not lost) is safely discardable or already accounted for.
