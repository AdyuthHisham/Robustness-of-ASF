---
title: Orchestrator Task: Implement K-Radar Visibility Analysis Pipeline
type: literature
source: home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Orchestrator_Task_Implement_K-Radar_Visibility_Analysis_Pipeline.md
date: 2026-07-02
tags: [05 Implementation]
---
---
title: Orchestrator Task: Implement K-Radar Visibility Analysis Pipeline
type: literature
source: home/adhish/Downloads/00_orchestrator_kickoff_prompt.md
date: 2026-07-02
tags: [05 Implementation]
---
# Orchestrator Task: Implement K-Radar Visibility Analysis Pipeline

> **Execution Mode: CPU-Only / Validation-Only**
>
> This implementation targets a **CPU-only, minimal-data workflow** for
> validation and debugging.  All examples use toy-scale subsets (1–2
> sequences, ≤20 frames).  Full-dataset and GPU-accelerated processing are
> explicitly out of scope for the current build and are reserved for
> future scaling work.


## Spec documents (read in this order)

1. `kradar_visibility_analysis_prompt.md` — full spec: sensor suite, label
   format, output schema (§1-§3), goals/sub-goals (§5), package layout (§8).
2. `04_visibility_methodology.md` — selected methodology for each visibility
   score (radar/LiDAR/camera). Implement exactly the recommended method in
   each section; optional upgrades (full-tesseract radar, occlusion
   discount) are flag-gated, not default.
3. `06_smoke_tests_scaffold.md` — pytest stubs for SMK-01..17, fill in.
4. `07_verification_tests_scaffold.md` — pytest stubs for VER-01..26, fill in.

## Environment

- K-Radar dataset (pruned): `/home/adhish/Productivity/AMSCUP/repos/K-Radar`
- Working directory (build here): `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar`
- Package manager: **uv**. Use `uv init`, `uv add <dep>`, `uv run pytest`, etc.
  — no pip/conda/venv directly.
- `AGENTS.md` in the working directory has standing conventions (uv-only,
  Polars over pandas, etc.) — it's auto-injected, don't re-derive these.

## Task

Build the `kradar_visibility/` package per §8's module layout inside the
working directory above.

### Phase 1 — sequential foundation (do not parallelize)

`config.py` → `parser.py` → `calibration.py` → `data_loader.py`
(Sub-Goal 1-2). Everything else depends on these, so build and smoke-test
them (SMK-01..04, SMK-10..13) before moving on.

### Phase 2 — parallel visibility metrics (use `delegate_task`)

Once Phase 1 passes its smoke tests, the three metric modules
(`radar_visibility.py`, `lidar_visibility.py`, `camera_visibility.py`) are
independent of each other — each only depends on the Phase 1 modules, not
on one another. Dispatch them as a single **parallel batch** of subtasks
rather than implementing them one after another:

```python
delegate_task(tasks=[
    {
        "goal": "Implement radar_visibility.py per §4.1 method B",
        "context": "<paste the full §4.1 'Recommendation' section from "
                    "04_visibility_methodology.md, the radar_* schema rows "
                    "from §3.1, SMK-14, VER-01/06/08/19/25-26, the working "
                    "directory path, and the signature data_loader.py "
                    "exposes for radar_zyx_cube — subagents start with zero "
                    "context, so include everything verbatim, not by "
                    "reference.>",
        "toolsets": ["terminal", "file"],
        "note": "CPU-only execution — use CPU-based point-in-box (e.g. NumPy or Open3D), no GPU kernels."
    },
    {
        "goal": "Implement lidar_visibility.py per §4.2 method A+B (CPU-only)",
        "context": "<full §4.2 Recommendation section, lidar_* schema rows, "
                    "SMK-11/12/15, VER-02/03/04/06/07/19/20/25-26, note "
                    "that points_in_boxes_gpu already exists elsewhere in "
                    "the test-bed repo — search for and reuse it, don't "
                    "reimplement, plus the working directory path.>",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "Implement camera_visibility.py per §4.3 method B",
        "context": "<full §4.3 Recommendation section, cam_* schema rows, "
                    "SMK-05-09/16, VER-09-15, the 4-camera calibration "
                    "interface calibration.py exposes, and the working "
                    "directory path.>",
        "toolsets": ["terminal", "file"]
    }
])
```

Each subtask gets its own isolated context and terminal — only the final
summaries return, so this keeps the main session's token usage flat
regardless of how much back-and-forth each module needs. After all three
return, review their summaries before wiring them into `pipeline.py`
yourself (don't delegate the integration step — it needs the full picture).

### Phase 3 — assembly and testing

> **Sanity-first rule:** always run on a 2-sequence / 20-frame subset before
> attempting any larger batch.  The default `run()` entry point should target
> this minimal subset so that CPU execution finishes in seconds.

1. `pipeline.py` (Sub-Goal 5) — done directly, not delegated, since it
   integrates Phase 2's outputs.
2. Fill in `tests/test_smoke.py` and `tests/test_verify.py` from the two
   scaffold docs (Sub-Goal 6-7).

#### Use `execute_code` for batch test/check operations

For any step that's "run N things and aggregate the results" rather than a
single shell command, write a script and execute it in one shot instead of
issuing terminal commands one at a time:

- Running all 17 smoke tests and summarizing pass/fail + durations in one
  call (`terminal("uv run pytest tests/test_smoke.py -v --json-report ...")`
  inside an `execute_code` script, then parse the JSON report and print a
  compact table) — not 17 separate terminal invocations.
- Checking that calibration files exist for all 7 sensors across a batch of
  sequences before running verification, looping with `read_file`/
  `search_files` inside one script rather than one `terminal(ls ...)` per
  sequence.
- Generating the `verification_report.md` artifact from §7's "Report
  generation" section: parse the full `pytest --json-report` output and
  emit the per-VER-ID table in a single script run.

Run smoke tests on 2 sequences first; only run full verification (and the
batch checks above) once smoke passes.

## Constraints

- Memory: never load full 4DRT (`radar_tesseract/`) by default — use
  `radar_zyx_cube/` as specified.
- All dependencies added via `uv add`, tests run via `uv run pytest`.
- Don't delegate Phase 1 (foundation) or the `pipeline.py` integration step
  — only Phase 2's three independent metric modules are parallelizable.
- Stop and report after smoke tests pass on the 2-sequence subset.
  Full verification on all 58 sequences is **future scope** and must not be
  run in the current CPU-only validation build.
