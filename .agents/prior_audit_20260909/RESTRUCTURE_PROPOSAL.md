# AMSCUP Restructure Proposal

Based on `.agents/MASTER_AUDIT.md` (7 chunks, 15 findings, 2 reviewer lenses). This document proposes how the repo should be organized going forward. It does not recap findings except by ID reference — see MASTER_AUDIT.md for full detail. No files moved, no code edited, as instructed.

## 1. The core problem: hand-maintained copies with no single owner

The single strongest pattern across all 7 chunks isn't a directory-layout problem, it's an ownership problem: several facts about `kradar_visibility` are duplicated by hand in 2-4 places with no mechanism forcing them to stay in sync, and every duplicate found is stale in a different way.

**The OUTPUT_SCHEMA copy problem** (B-1-03, B-3-01, B-5-02): the real schema is 50 columns (`config.py:110-161`). At least **four** separate hand-written descriptions of it exist, and all four are wrong in different ways:
- `architecture.md`'s Output Schema table — missing 8 columns (or was thought to be missing 4, until the chunk-5 spot-check corrected the count to 8; see MASTER_AUDIT.md chunk 1/5 notes for the reconciliation)
- `validate_output.py`'s `expected_cols` list — missing 3 columns, so the schema *validator itself* can't catch a broken output in those fields
- `docs/vAIlt/05_Implementation/KRadar_configpy_Reference.md` — same 8 columns missing, "total 42 shown here" undercounting the real 50
- `docs/vAIlt/05_Implementation/Config_Reference.md` — same 8 columns missing, presented with no "excerpt" caveat as if complete

**Proposal**: make `config.OUTPUT_SCHEMA` the only place the column list is ever typed out. Everywhere else that needs the list — architecture.md, the two vault docs, `validate_output.py`'s `expected_cols` — should either (a) import/read it programmatically (`validate_output.py` already imports `config`, this is a one-line fix there), or (b) if a doc must contain prose describing what a column means (which architecture.md legitimately should — a raw column list isn't self-documenting), the doc should state explicitly "column list generated from config.OUTPUT_SCHEMA as of <date>, see config.py for the current authoritative list" rather than reproducing a static count. A doc that says "N columns" invites exactly this drift the moment N changes.

**The output-path copy problem** (A-7-01): `crossproduct.py:32`'s `SUMMARY_OUT_DIR` and `plots.py:26` each independently hardcode `repos/K-Radar/outputs/robustness_reports/crossproduct/` — the stale pre-correction directory — while every current doc cites `crossproduct_v2/` as authoritative. This is the most consequential finding in the audit: it means the "confirmed clean" number-matches in chunks 3 and 5 (RELIABILITY_FLOOR, D3=209, 2 suspected_bug flags) were validated against a directory the code, if rerun today, would not reproduce.

**Proposal**: define `SUMMARY_OUT_DIR` (or whatever the corrected path should be) in exactly one place — a shared `crossproduct/config.py` or similar — and have every consumer (`run_analysis.py`, `queries.py`, `plots.py`) import it, rather than each file hardcoding its own copy. Whether the correct fix is repointing at `crossproduct_v2/` or something else is a decision for whoever owns this pipeline (possibly "rename `crossproduct_v2/` back to `crossproduct/` once it's confirmed authoritative and delete the old one" is simpler than propagating `_v2` forever) — that decision is out of scope for this document, but the current state (two full copies on disk, code pointing at the wrong one, no error) needs a decision, not a workaround.

**The validator-reimplements-the-bug problem** (A-3-01, chunk-2's A-2-01/A-2-02): `validate_precomputation.py` recomputes `radar_visible` using the exact same buggy formula as `pipeline.py` (A-1-01) instead of importing `pipeline`'s logic or diffing against its actual output row-by-row. Because it reimplements rather than reuses, a bug in the shared formula is invisible to the validator by construction — it will always agree with itself. Similarly, `TestLidarWithRangeImage` (VER-27/28/29) tests the channel-LUT threshold logic with `expected_density=10.0`, a value chosen specifically to avoid exercising the real production values (8000/32000) that trigger A-1-02.

**Proposal**: this is a testing/validation-architecture issue, not a file-layout issue. The general rule going forward: a "verification" or "validation" script's job is to catch drift *between* two independently-arrived-at computations (recomputed vs. pipeline output) or to check a real invariant against real inputs — not to re-derive the same formula from the same source and declare agreement with itself. Concretely: `validate_precomputation.py` should call `pipeline.compute_visibility_for_frame()` (or the specific function under test) directly rather than reimplementing its logic inline, so a future formula change only needs to happen in one place and validators stay honest against it automatically.

## 2. Dead infrastructure — archive candidates

Alvis is permanently gone (2026-09-01, ground truth). The following are now dead weight with no live interface into the active codebase (confirmed via chunk 7's call-site trace):

- **`repos/AMSCUP_PLUS`** (submodule) — confirmed zero functional call sites from `test-bed/`; the only reference found is a comment in `array_job.sbatch:24` citing it as a prior pattern, not a functional dependency.
- **`test-bed/src/Modules/robust_testing/kradar/scripts/alvis/*`** (`array_job.sbatch`, `submit_all.sh`, `merge_shards.py`, `setup_env.sbatch`, `push_to_alvis.sh`, `regen_sedan_bus.sbatch`, `bootstrap_env.sh`, `merge_job.sbatch`) — targets a cluster that no longer exists; self-consistent internally but has no runtime target.
- **`docs/ALVIS_MIGRATION_PLAN.md`** — confirmed (chunk-7 follow-up read) to be a "how to get code/data *onto* Alvis" plan, not a migration-*off* record. Entirely retrospective now — useful only as a historical record of the pipeline's HPC-scale run design (chunking strategy, walltime/core sizing, the `radar_tesseract`-vs-`radar_zyx_cube` sanity-check callout), not as an actionable plan.
- **`alvis_archive_2026-08-28/`** (working-tree, untracked) — per its own name, an archive of Alvis-era data. Already user-created as an archive; likely just needs a decision on retention/location, not a restructure.

**Proposal**: move `repos/AMSCUP_PLUS`'s submodule pointer removal, `scripts/alvis/*`, and `docs/ALVIS_MIGRATION_PLAN.md` into a single top-level `archive/alvis/` (or similar) directory rather than deleting them — they document a real, completed engineering effort and the design decisions in `ALVIS_MIGRATION_PLAN.md` (walltime sizing, the `radar_zyx_cube` vs `radar_tesseract` presence check, the missing-`description.txt` risk it correctly flagged in advance) have value if this project ever gets HPC access again under a different cluster. Don't delete; relabel as archived so nobody mistakes it for a live target. `repos/AI-MSF-Benchmark` was found to have zero references anywhere under `test-bed/` — this needs a decision, not a recommendation (see §4): is it unused, or referenced only from inside the `repos/K-Radar` submodule? If the latter, it stays; if the former, it's a second archive candidate.

## 3. A permanent, not transient, data limitation

B-7-01 found that `weather`/`environment`/`time_of_day` columns can never be populated locally again: their source `description.txt` files "only ever lived on Alvis" (per `obsidianVault/Daily/2026-09-07.md`) and don't exist anywhere in the local `repos/K-Radar` checkout. This directly explains why VER-25/VER-26 (`TestWeatherImpact`) are permanently `pytest.skip`ped (chunk 2) — not a temporary gap, a structural one now that Alvis is gone.

**Proposal**: `architecture.md`'s Output Schema table currently frames `weather`'s "normal" fallback as an edge case. It should instead state plainly that these three columns are permanently fallback-only in this environment, and that VER-25/26 are permanently un-runnable rather than "currently skipped." This isn't a restructure of code — it's a correction of what "done" means for this feature going forward, so a future contributor doesn't spend time trying to source real weather data that structurally cannot exist locally.

## 4. Decisions needed from the user (not recommendations)

These are working-tree items and open questions the audit surfaced that require a call only the user can make — listed here per the task's explicit instruction not to recommend a disposition:

- **`docs/delete_/`** — name suggests staged-for-deletion content; needs confirmation before treating as safe to remove.
- **`backups/`** — contents and retention policy unknown from this audit; needs a decision on what it's backing up and for how long.
- **`alvis_archive_2026-08-28/`** — likely fine as-is once archived per §2, but needs confirmation it's not still needed as a live reference.
- **Several modified-but-uncommitted tracked files** (`docs/Latex_Report`, `docs/vAIlt/.obsidian/workspace.json`, `obsidianVault/.obsidian/workspace.json`, `obsidianVault/Knowledge/asf-training-inputs.md`, `obsidianVault/Knowledge/robustness-metric-selection.md`, `obsidianVault/Projects/K-Radar/asf-corruption-study-alvis.md`, `obsidianVault/Projects/K-Radar/robustness-radar-charts.md`, `repos/K-Radar` submodule pointer, `test-bed/.../radar_charts.py`) — probable intentional in-progress work per ground truth; needs a decision on whether to commit, and in what grouping (the two `robustness-metric-selection.md`/`robustness-radar-charts.md` vault docs are also B-6-01/B-6-02 doc-drift targets — fixing the doc-drift and committing could be the same pass).
- **`repos/AI-MSF-Benchmark`** — zero references found under `test-bed/`; needs the user (or someone with submodule-internal knowledge) to confirm whether it's referenced from inside `repos/K-Radar` before deciding whether it's an archive candidate.
- **Whether `crossproduct/` or `crossproduct_v2/` is the directory to keep** (§1) — a data-provenance decision, not a code-structure one; whoever last ran the corrected analysis should confirm which directory's contents are actually trustworthy before either is deleted or renamed.

## 5. What this document deliberately does not propose

Per ground truth: no restructuring of `repos/K-Radar`, `repos/AMSCUP_PLUS`, or `repos/AI-MSF-Benchmark` internals; no merging `docs/vAIlt/` and `obsidianVault/`; no proposal to add a top-level build/test/lint command (the monorepo's lack of one is by design). The two-vault split, the submodule boundaries, and the lack of a unified build system are treated as settled architecture, not audit findings.
