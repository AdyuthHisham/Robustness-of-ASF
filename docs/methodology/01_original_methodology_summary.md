# Original Methodology Summary

## Document: 00_orchestrator_kickoff_prompt.md
- **Purpose:** 1. `kradar_visibility_analysis_prompt.md` — full spec: sensor suite, label
- **Key Concepts:** Execution Mode: CPU-Only / Validation-Only, CPU-only, minimal-data workflow, K-Radar dataset (pruned): `/home/adhish/Productivity/AMSCUP/repos/K-Radar`, Working directory (build here): `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar`, Package manager: **uv**. Use `uv init`, `uv add <dep>`, `uv run pytest`, etc.
- **Architecture:** # Orchestrator Task: Implement K-Radar Visibility Analysis Pipeline

> **Execution Mode: CPU-Only / Validation-Only**
- **Key Patterns:** delegate_task(tasks=[, 1. `kradar_visibility_analysis_prompt.md` — full spec: sensor suite, label, 2. `04_visibility_methodology.md` — selected methodology for each visibility, 3. `06_smoke_tests_scaffold.md` — pytest stubs for SMK-01..17, fill in., 4. `07_verification_tests_scaffold.md` — pytest stubs for VER-01..26, fill in.

## Document: 04_visibility_methodology.md
- **Purpose:** Every method below is selected to satisfy these constraints from §5/§8 before
- **Key Concepts:** Execution Mode: CPU-Only / Validation-Only, future-scope, **Sub-Goal 2 / §8.1 memory efficiency**: never load the full 4DRT, Sub-Goal 2 / §8.1 memory efficiency, **Sub-Goal 3**: all metrics reuse a single oriented-bbox-in-frame primitive
- **Architecture:** 
**A. Raw point count in oriented bbox**
Direct reuse of the existing `points_in_boxes_gpu` (OpenPCDet) pipeline
already built for this codebase.
- Input: `os2-64/`, `os1-128/` point clouds, oriented bbox.
- **Key Patterns:** None

## Document: 06_smoke_tests_scaffold.md
- **Purpose:** ```python
- **Key Concepts:** Execution Mode: CPU-Only / Validation-Only, toy-scale subset
- **Architecture:**         raise NotImplementedError

    def test_smk17_full_pipeline_two_sequences(self, dataset_root, smoke_sequence_ids, smoke_frame_limit, tmp_path):
        """SMK-17: end-to-end pipeline.py run on 2 sequences / 20 frames -> parquet, no crash, all columns present."""
        # TODO: from pipeline import run
- **Key Patterns:** import polars as pl, class TestParsing:, class TestProjection:

## Document: 07_verification_tests_scaffold.md
- **Purpose:** ```python
- **Key Concepts:** Execution Mode: CPU-Only / Validation-Only, toy-scale Parquet output
- **Architecture:** 
> Maps VER-01..26 to pytest stubs that operate on the **output Parquet
> table** (not raw sensor data) — these run after `pipeline.py` produces
> the full table, on the full dataset or a large representative sample.
> Uses Polars throughout for consistency with existing K-Radar pipeline
- **Key Patterns:** import polars as pl, class TestSensorIdentifyConsistency:, DISTANCE_BINS = [0, 20, 40, 60, 80, 120]

## Document: 08_readme_spec.md
- **Purpose:** 1. **Overview** — 2-3 sentences: what the package does, what it outputs
- **Key Concepts:** Execution Mode: CPU-Only / Validation-Only, current, Overview, Architecture, Module reference
- **Architecture:** 
> Companion doc. Defines the required `README.md` for the
> `kradar_visibility` package, to be written after the pipeline (§5
> Sub-Goal 5) is working and smoke tests (§6) pass — it should document
> what was actually built, not what was planned.
- **Key Patterns:** 1. **Overview** — 2-3 sentences: what the package does, what it outputs, 2. **Architecture** — one diagram or ordered list showing data flow:, 3. **Module reference** — one subsection per file in `kradar_visibility/`, 4. **Methodology summary** — one paragraph per sensor (radar/LiDAR/camera), 5. **Schema reference** — either reproduce or link to the §3.1 table, with
