# Docs map

Organised by what you are trying to do. Obsidian vaults, the LaTeX report and the literature survey are **not** in this repo (they are in the gitignored `Misc/`); the thesis numbers used in the root README are cited by section and table name.

## I want to read about the study (reader)
- [`../README.md`](../README.md): brief, key results, limitations.
- `methodology/ASF_pipeline_cheatsheet.md`: how ASF fuses camera, LiDAR and radar.
- `figures/thesis/`: thesis figures (evaluation pipeline, pooled metrics, perception-stack diagram, corruption gallery).
- `presentations/`: defence material and question preparation.

## I want to reproduce or check results (reproducer)
- [`../data/DATA.md`](../data/DATA.md), [`../results/RESULTS.md`](../results/RESULTS.md), [`../scripts/README.md`](../scripts/README.md).
- `methodology/04_visibility_methodology.md`, `methodology/VISIBILITY_FORMULAS_AND_METHODS.md`: how per-object visibility scores are computed.
- `methodology/kradar_config_reference.md`, `config_reference.md`: configuration constants.
- `methodology/verification_report*.md`, `reports/`: verification and cross-product analysis reports.
- `logs/`: historical logs, including the Alvis migration plan (reference only; Alvis is unavailable).

## I want to change the code (contributor)
- [`../CLAUDE.md`](../CLAUDE.md): conventions and commands.
- `methodology/07_phase*_implementation_log.md`, `06_upgrade_roadmap.md`, `04_gap_analysis.md`: design history of the visibility pipeline.
- `methodology/pipeline_issues.md`: known issues.
- `methodology/kradar_visibility/`: the visibility package's own `AGENTS.md`, `architecture.md`, `api_contracts.md`, test notes and verification reports.

## Layout

| Folder | Contents |
|---|---|
| `methodology/` | specs, design notes, implementation logs, verification reports |
| `reports/` | cross-product trends, anomaly reports, adversarial review |
| `presentations/` | defence notes and question banks (`.odp` decks stay local and are gitignored) |
| `figures/` | diagrams and figure sources; `figures/thesis/` holds the tracked thesis figures |
| `logs/` | dated work logs |
