# AMSCUP: robustness of camera / LiDAR / 4D-radar fusion under sensor corruption

AMSCUP is the code, configuration and analysis behind a Chalmers MSc thesis that asks how a multi-sensor 3D detector behaves when its sensors are noisy, partly lost or absent. The model under test is Availability-aware Sensor Fusion (ASF, camera + LiDAR + 4D radar). It is run **unmodified, from its officially released checkpoint**, on the 58-sequence K-Radar test split. Twelve synthetic corruption effects (Gaussian noise, partial loss, complete loss, frame deletion; applied to each sensor separately at three severities) are injected, and the detections are compared with the clean run. The repo holds the corruption definitions, the metric and analysis code, a per-object visibility pipeline, and the small result tables and figures. Large data is shared separately (see [Data and reproducibility](#data-and-reproducibility)).

![Evaluation pipeline: dataset, corruption injection and ASF inference run once per condition; the outputs are consolidated into one Parquet table, then metrics and stratified robustness analysis](docs/figures/thesis/eval_pipeline.svg)

*Workflow (thesis Figure "Overview of the evaluation pipeline", Methods chapter). The figure's box says "36 conditions". That is the nominal grid in the thesis Methods chapter (3 modalities x 4 effects x 3 severities); complete loss has a single tier, so 30 corrupted conditions actually exist (clean run not counted): 21 evaluable plus 9 frame-deletion. Verified against `configs/noise/single/` (30 files) and `row_table_iou03.parquet` (30 corrupted conditions plus `original`).*

## Key results

All numbers below are from the thesis (Results chapter). The figure files are tracked copies; the table or figure each number comes from is named. Scope: one model checkpoint, one dataset (K-Radar test split: 58 sequences, 13,727 baseline frames, 35,456 sedan and bus/truck ground-truth objects), 30 corrupted conditions (clean run not counted): 21 evaluable, including the 3 `loss_complete_zero` conditions, and 9 frame-deletion conditions that could not be evaluated. (The thesis text says "22 evaluable"; that count includes the clean run.)

![Pooled robustness metrics per corruption condition](results/figures/metrics_table.png)

*Pooled metrics per condition (thesis Fig. "metrics_table"; same file as [`results/figures/metrics_table.png`](results/figures/metrics_table.png)). R_b^c is corrupted mAP divided by clean mAP.*

1. **LiDAR Gaussian noise causes the largest drop, and it is a step, not a slope.** Pooled mAP goes from 73.99 (clean) to 69.59 at low severity, then 18.54 (medium) and 17.45 (high); R_b^c is 0.251 and 0.236. False negatives rise from 8,287 to 29,214 / 29,829 while false positives fall from 4,900 to 1,175 / 842, so the drop comes from missed detections rather than spurious ones. Source: pooled metrics figure above.
2. **Complete LiDAR loss (zero-filled) is less damaging than medium or high LiDAR noise.** mAP 44.05, R_b^c 0.595. A noisy-but-present LiDAR hurts more than an absent one in this sweep. Source: same figure. Note that the sweep never tells ASF's availability mechanism that a sensor is absent (thesis, discussion of cause); this result describes zero-filled input, not declared exclusion.
3. **Camera corruption barely moves the output.** Every camera condition stays between mAP 72.64 and 73.35 (R_b^c >= 0.982). Source: same figure. Composite Robustness Index (CRI, 1 = AP stays high and stable across severities): camera loss-partial 0.936 / 0.929 (sedan / bus-truck), camera Gaussian noise 0.915 / 0.842, versus LiDAR Gaussian noise 0.106 / 0.153. Source: thesis CRI table.
4. **Radar sits in between.** Radar Gaussian noise gives mAP 62.94 (medium) and 57.18 (high); radar loss-partial at low and medium severity stays close to baseline. CRI for radar Gaussian noise is 0.272 for both classes. Source: pooled metrics figure and CRI table.
5. **LiDAR Gaussian noise is the worst single cell in 9 of the 10 axis-class pairs** (weather, environment, time of day, distance, point density; sedan and bus/truck), always at medium or high severity. The exception is bus/truck in rain, where complete LiDAR loss gives R_b^c = 0.000 (N = 120). Sedan examples: 0.114 in the densest point-density bin, 0.154 at 0 to 20 m. Source: thesis table "single worst cell per diversity axis and class" (cells with N > 30).
6. **Frame deletion crashed the pipeline for all three sensors.** ASF's sparse-convolution backbone raises a `RuntimeError` on the empty input (radar, LiDAR) and the camera case also crashes, so none of the nine frame-deletion conditions has a metric. Source: thesis, frame-deletion section.

![R_b^c by modality across corruption families and severities](results/figures/modality_map_trend_single.png)

*Retention by modality (same data as the table; thesis draft figure). Marker size scales with the sample count N.*

**Limitations.**
- One checkpoint and one dataset; nothing here says how other fusion models behave.
- The re-run baseline sits 3.2 to 5.6% below the numbers in the ASF paper (sedan BEV AP 77.86 vs 82.5; bus/truck BEV AP 67.93 vs 70.2; same checkpoint, IoU 0.3, official evaluation code). The thesis reports the gap but does not explain it.
- Several weather and environment categories rest on 2 to 7 sequences or few objects; the thesis flags them rather than treating them as general findings.
- mATE, mASE and mAOE are computed over true positives only, so at the collapsed conditions they describe a smaller, easier surviving population. Their apparent improvement there is a survivorship artefact.
- The mFR metric is excluded from the metrics stack: no frame-level flip/consistency computation exists in this pipeline (`scripts/analysis/master_metrics_table.py` docstring).
- mAP throughout is the **aggregated** mAP: the num_gt-weighted mean of the cell-level restricted-range AP over both classes and all stratum cells in `crossproduct_v2/summary_full_density.parquet` (clean = 73.99). It is not the mean of the two per-class APs (72.89). `results/tables/master_metrics_table.md` was regenerated on that definition and reproduces every mAP and R_b^c in the thesis figure to the printed precision. mASE differs slightly between the two (clean 0.236 in the table, 0.239 in the thesis figure; LiDAR noise medium 0.201 vs 0.204): the repo has two mASE implementations (an earlier audit found `crossproduct.py` uses a different formula), and which one the thesis figure used was not traced. RCE is still computed per class. Other chart scripts (`heatmaps.py`, `bar_charts.py`, ...) still use the per-class mean mAP. See [`results/RESULTS.md`](results/RESULTS.md).

## Repository map

```
README.md          this file
CLAUDE.md          instructions for the Claude Code agent working in this repo
pyproject.toml     one uv project for everything (Python >= 3.12)
src/               first-party packages (import with `uv run`; paths come from src/amscup_paths.py)
  kradar_visibility/   per-object radar / LiDAR / camera visibility scores -> Parquet;
  robustness/          prediction ingest, AP, retention, CRI, churn (vendored from the K-Radar fork)
  effects/             the corruption (noise) definitions and their visualisation
  amscup_paths.py      single source of truth for every filesystem path
configs/           ASF configs (final run + per-sequence), noise-effect configs, camera calibration, train/test split
scripts/           runnable entry points, by purpose: visibility/, analysis/, data_transfer/, cluster_historical/
tests/             smoke tests (SMK-*) and verification tests (VER-*)
results/           tracked, curated tables and figures (index: results/RESULTS.md)
data/              NOT tracked: datasets and generated tables (catalogue: data/DATA.md)
docs/              methodology, reports, presentation material, figures (index: docs/README.md)
Misc/              everything moved out of the main tree during the restructure (nothing deleted; not tracked)
```

## How to navigate

| I want to... | Go to |
|---|---|
| Understand the method | `docs/methodology/` (start with `ASF_pipeline_cheatsheet.md`, `04_visibility_methodology.md`) |
| See the results | this README, then [`results/RESULTS.md`](results/RESULTS.md) |
| See where every table and figure comes from | [`data/DATA.md`](data/DATA.md) and [`scripts/README.md`](scripts/README.md) |
| Reproduce a table or figure | [Quickstart](#quickstart), then `scripts/analysis/` |
| Run the visibility pipeline | `scripts/visibility/run_pipeline.py` (needs the K-Radar dataset) |
| See how corruptions are defined | `src/effects/noise_injection.py`, `configs/noise/` |
| See how ASF was configured | [`configs/README.md`](configs/README.md) |
| Read the audits and verification reports | `docs/reports/`, `docs/methodology/verification_report.md` |
| Contribute | `CLAUDE.md` (conventions), `tests/`, `scripts/README.md` |

## Quickstart

```bash
git clone <repo-url> && cd AMSCUP          # no submodules; nothing to --recurse
uv sync                                    # installs the single project (Python >= 3.12)
# download the data bundle (link below) and unpack it so that data/results/ exists
uv run python -c "import sys; sys.path.insert(0, 'scripts/analysis'); \
  import master_metrics_table as m; print(m.build_all_tables(out_dir=__import__('pathlib').Path('/tmp/mmt')))"
uv run pytest tests/test_smoke.py          # needs the K-Radar dataset (see below)
```

The regeneration command was run on the full local bundle (about 18 s) and reproduced `results/tables/master_metrics_table.md` exactly. `scripts/analysis/master_metrics_table.py` also runs standalone with `uv run python scripts/analysis/master_metrics_table.py`, but that overwrites the copy in `data/results/robustness_reports/`, so the snippet above writes elsewhere.

**Smoke tests need the K-Radar dataset, which is not in this repo or the bundle.** Without it `tests/test_smoke.py` fails at the first test (file not found under `data/KRadar/`). Point `KRADAR_DATASET_ROOT` at your copy of the dataset to run them. Current state of `tests/test_smoke.py` on the restructured tree: 9 passed, 11 failed. Ten of the failures read files under `data/KRadar/` and fail without the dataset. **SMK-21 (LiDAR range-image float32 bin boundary) fails for another reason**: it passes in the pre-restructure project (numpy 1.26.4, and also with numpy 2.4.6 forced in) but fails in the merged environment, with identical `lidar_visibility.py` and test code. The cause is not identified; see `docs/logs/2026-11-21_restructure_summary.md`.

## Data and reproducibility

- **Tracked:** code, configs, docs, and the small tables and figures in `results/`.
- **Not tracked (`data/`):** generated tables (`row_table_iou03.parquet`, `full_denormalized_table_*.parquet`, `crossproduct*/`), figures and visibility Parquets. About 13 GB in total. Shared through a drive link: **TODO: add link**. Details in [`data/DATA.md`](data/DATA.md).
- **Not included at all:** the K-Radar dataset itself. Obtain it from its authors and set `KRADAR_DATASET_ROOT` (default `data/KRadar`).
- **What can be regenerated:** every downstream table and figure, from the Parquet row tables, with the scripts in `scripts/analysis/`.
- **What cannot be regenerated:** the ASF predictions. They were produced on the Chalmers Alvis cluster (NVIDIA A40 GPUs, SLURM array jobs), and that compute is permanently unavailable. The files in `scripts/cluster_historical/` and the `*_alvis.yml` configs document how the sweep ran; they are for reference, not a current workflow. The local data is the ceiling for any further analysis.
- Known, expected gap: `camera_frame_deletion` is only partly present in `row_table_iou03.parquet` (102 / 1,674 / 276 rows for high / low / medium, against about 40,000 for a normal condition), because that sweep crashed (result 6 above). The lidar and radar frame-deletion conditions have about 38,000 to 40,000 rows each; the thesis excludes all nine frame-deletion conditions from every metric regardless.

## Third-party code (no submodules)

This repo used to carry K-Radar, AMSCUP_PLUS and the LaTeX report as submodules. They are gone. The pieces the results depend on were copied into `src/` and `configs/`: the AP/robustness scripts (`src/robustness/`, from the K-Radar fork), the corruption definitions (`src/effects/`), and the ASF configs (`configs/asf/`). The K-Radar dataset, the ASF model code and the cluster tooling are not included. Upstream: K-Radar (KAIST) and the ASF authors' release; `src/robustness/LICENSE` (MIT) covers the vendored evaluation code.

## Citation, license, contact

- **License:** TODO. No top-level license file exists in this repo.
- **Citation:** TODO. Add the thesis reference once it is published.
- **Contact:** TODO.
