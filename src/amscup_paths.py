"""Single source of truth for filesystem locations. Every script imports from here.

Override the data location with AMSCUP_DATA_DIR and the K-Radar dataset root with
KRADAR_DATASET_ROOT (the dataset is not part of this repo; see data/DATA.md).
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = Path(os.environ.get("AMSCUP_DATA_DIR", ROOT / "data"))

# K-Radar dataset root (sequences, info_label_rev2, resources/cam_calib). Not tracked.
KRADAR_ROOT: Path = Path(os.environ.get("KRADAR_DATASET_ROOT", DATA_DIR / "KRadar"))

# Raw model outputs and derived tables (formerly repos/K-Radar/outputs). Not tracked.
OUTPUTS_DIR: Path = DATA_DIR / "results"
REPORTS_DIR: Path = OUTPUTS_DIR / "robustness_reports"
# Visibility-pipeline parquet tables. Not tracked.
VISIBILITY_DIR: Path = DATA_DIR / "visibility"
# Generated figures (charts written by scripts/analysis). Not tracked; curated finals live in results/.
FIGURES_DIR: Path = DATA_DIR / "figures"

# Tracked inputs
CONFIGS_DIR: Path = ROOT / "configs"
SPLIT_DIR: Path = CONFIGS_DIR / "split"
# Tracked curated results (small tables, final figures)
RESULTS_DIR: Path = ROOT / "results"
