# 2026-11-21: single-repo restructure and README

**State on arrival:** branch `restructure/work` already had the submodule removal, vendoring, flatten and docs-regroup commits (made outside this session). Nothing was intentionally deleted: former vaults, submodules, backups and legacy layouts are in `Misc/`.

**Integrity check:** directory sizes in `Misc/` and `data/` reconcile with the pre-move sizes (backups 1.2 GB, alvis_archive 739 MB, lit_survey 349 MB, LaTeX report 357 MB, 18 presentation backups, K-Radar about 27 GB split between `Misc/repos` and `data/results`), but individual untracked files were not hash-verified. Tracked files: of 633 files present in `restructure/pre-snapshot` but absent from `restructure/work`, every one is found by content hash in the tree or `Misc/`, except 4 gitlinks / `.gitmodules` (intentional) and 7 files over 50 MB or with unusual names that I located by name (`data/visibility`, `Misc/...`). `Misc/MANIFEST.txt` (referenced by `.gitignore`) does not exist, so the sha256 manifest planned earlier was never written.

**Done this session:** `README.md` rewritten (workflow figure, thesis numbers with sources), `data/DATA.md`, `results/RESULTS.md`, `scripts/README.md`, `docs/README.md`, `Misc/README.md`, CLAUDE.md layout/commands, `.gitignore` exceptions for tracked figures, thesis figures copied to `docs/figures/thesis/`.

**Findings:**
- Thesis pooled metrics (clean mAP 73.99; LiDAR noise medium/high 18.54 / 17.45) differ from `results/tables/master_metrics_table.md`, which regenerates exactly from the local row table (72.89 / 23.71 / 21.56). Cause not traced.
- `src/kradar_visibility/viewer/server.py` is missing everywhere.
- Fixed: `scripts/visibility/run_all_sequences.py` wrote its parquet and logs to `data/figures/` (the restructure mapped it to `FIGURES_DIR`); now `data/visibility/`.
- Thesis vs table mAP: FP/FN totals match the row table exactly, 72.89 equals the class mean of the thesis per-class BEV APs; pooled AP not recomputed.
- `camera_frame_deletion`: 102 / 1,674 / 276 rows (high / low / medium) vs about 40,000 per normal condition; lidar and radar frame-deletion have 38,000 to 40,000 rows each.
- `tests/test_smoke.py`: 9 passed, 11 failed. 10 failures read `data/KRadar/` and fail without the dataset. SMK-21 fails in the merged environment but passes in the pre-snapshot nested project, including with numpy 2.4.6 forced in; `lidar_visibility.py`, `pipeline.py` and the test are identical, `conftest.py` differs only in a path. Cause not identified (not numpy alone). The merged `pyproject.toml` did move the visibility code from numpy 1.26.4 to 2.4.6 without the user having been shown that change.
- The pre-restructure environment was not otherwise compared; there is no pre-move smoke baseline (the baseline run was taken on the already-restructured tree).
- Which of `crossproduct`, `crossproduct_v2`, `crossproduct_v3_weather_corrected` the thesis uses is not recorded.
