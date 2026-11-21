# src/

First-party packages. Install with `uv sync` at the repo root; import paths are defined once in `amscup_paths.py`.

| Package | What | Notes |
|---|---|---|
| `kradar_visibility/` | Per-object radar / LiDAR / camera visibility scores written to Parquet. Start with `pipeline.py` (`run()`), constants and output schema in `config.py`. | Needs the K-Radar dataset. `viewer/` holds only `static/`; its server is missing. Developer rules: `docs/methodology/kradar_visibility/AGENTS.md` |
| `robustness/` | Prediction/GT ingest, AP (`ap_metrics.py`), retention, CRI (`compute_robustness.py`), churn (`gt_transition_analysis.py`), `run_ap_robustness.py`. | Vendored from the K-Radar fork (commit 48ee57d), MIT license in `LICENSE`. Analysis scripts import it. |
| `effects/` | Corruption definitions (`noise_injection.py`), schema (`config.py`), visualisation. | Reference-only: needs `torch` and K-Radar model code (`uv sync --group effects`). A few scripts carry old absolute paths. |
| `amscup_paths.py` | `ROOT`, `DATA_DIR`, `KRADAR_ROOT`, `REPORTS_DIR`, `VISIBILITY_DIR`, `FIGURES_DIR`, `CONFIGS_DIR`, `RESULTS_DIR`. | Override with `AMSCUP_DATA_DIR`, `KRADAR_DATASET_ROOT`. |
