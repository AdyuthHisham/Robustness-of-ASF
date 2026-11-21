# 2026-11-21: single-repo restructure and README

**State on arrival:** branch `restructure/work` already had the submodule removal, vendoring, flatten and docs-regroup commits (made outside this session). Nothing was deleted: former vaults, submodules, backups and legacy layouts are in `Misc/`.

**Integrity check:** of 633 files present in `restructure/pre-snapshot` but absent from `restructure/work`, every one is found by content hash in the tree or `Misc/`, except 4 gitlinks / `.gitmodules` (intentional) and 7 files over 50 MB or with unusual names that I located by name (`data/visibility`, `Misc/...`). `Misc/MANIFEST.txt` (referenced by `.gitignore`) does not exist, so the sha256 manifest planned earlier was never written.

**Done this session:** `README.md` rewritten (workflow figure, thesis numbers with sources), `data/DATA.md`, `results/RESULTS.md`, `scripts/README.md`, `docs/README.md`, `Misc/README.md`, CLAUDE.md layout/commands, `.gitignore` exceptions for tracked figures, thesis figures copied to `docs/figures/thesis/`.

**Findings:**
- Thesis pooled metrics (clean mAP 73.99; LiDAR noise medium/high 18.54 / 17.45) differ from `results/tables/master_metrics_table.md`, which regenerates exactly from the local row table (72.89 / 23.71 / 21.56). Cause not traced.
- `src/kradar_visibility/viewer/server.py` is missing everywhere.
- `tests/test_smoke.py`: 9 passed, 11 failed. 10 failures are the missing K-Radar dataset. SMK-21 is a real regression: passes on numpy 1.26.4 (pre-snapshot nested project, identical `lidar_visibility.py` and test), fails on the locked numpy 2.4.6 in the merged environment. Not fixed; decision pending (pin `numpy<2` vs dtype-explicit binning). This also bears on whether visibility parquets regenerated today would match the existing ones.
- The pre-restructure environment was not otherwise compared; there is no pre-move smoke baseline (the baseline run was taken on the already-restructured tree).
- Which of `crossproduct`, `crossproduct_v2`, `crossproduct_v3_weather_corrected` the thesis uses is not recorded.
