# §11 README Requirements

> **Execution Mode: CPU-Only / Validation-Only**
>
> The README must reflect the **current** CPU-only, toy-scale build.  It
> should state explicitly that the package is for validation and debugging
> on small subsets, and that full-dataset / GPU processing is future scope.


> Companion doc. Defines the required `README.md` for the
> `kradar_visibility` package, to be written after the pipeline (§5
> Sub-Goal 5) is working and smoke tests (§6) pass — it should document
> what was actually built, not what was planned.

## Required sections

1. **Overview** — 2-3 sentences: what the package does, what it outputs
   (Parquet table, schema reference to §3.1), who/what consumes it.

2. **Architecture** — one diagram or ordered list showing data flow:
   `info_label_rev2/*.txt` → `parser.py` → `calibration.py` transforms →
   `data_loader.py` per-sensor loads → `{radar,lidar,camera}_visibility.py`
   scoring → `pipeline.py` assembly → Parquet output. State which modules
   run per-frame vs. per-object vs. per-sequence.

3. **Module reference** — one subsection per file in `kradar_visibility/`
   (per §8's layout): purpose, key public functions/classes with
   signatures, and what it depends on. Pull this from actual code, not
   from the original spec doc — if implementation diverged from §8/§4
   during the build, the README reflects what's real.

4. **Methodology summary** — one paragraph per sensor (radar/LiDAR/camera)
   stating which method was implemented (cross-reference
   `04_visibility_methodology.md` by section, e.g. "§4.1 method B"), with
   the actual formula used and any deviations or simplifications made
   during implementation that the methodology doc didn't anticipate.

5. **Schema reference** — either reproduce or link to the §3.1 table, with
   a note on which columns are guaranteed non-null vs. nullable
   (e.g. `cam_*_proj_x/y` null when not visible per VER-11).

6. **Setup & usage** — exact `uv` commands for a **minimal CPU run**:
   `uv sync`, point `config.py` at a dataset root, then run the default
   toy-scale pipeline (2 sequences, 20 frames) first.  Document the
   full-dataset command only as a future-scope note.

7. **Testing** — smoke and verification commands for the **toy subset**;
   note expected runtimes on CPU (<5 min for smoke, <2 min for verify).
   Full-dataset testing is future scope.

8. **Known limitations / deviations** — explicitly list:
   - CPU-only execution (GPU kernels not used).
   - Toy-scale validation only; no full-dataset benchmarks.
   - Any verification tests that are skipped or have caveats at small scale.
   - TODOs for future GPU/full-dataset upgrades (full-tesseract radar,
     camera occlusion discount, `points_in_boxes_gpu`).

9. **Downstream usage examples** — at least 2 of the §10 analysis queries
   (Q1-Q9) written as actual Polars one-liners against the output Parquet,
   not just restated as prose questions.

## Constraints

- Written **after** the pipeline runs end-to-end and smoke tests pass —
  not drafted speculatively from the spec docs before code exists.
- Module reference (§3 above) must be regenerated/checked against actual
  function signatures in the codebase, not copied from `00_orchestrator_
  kickoff_prompt.md` or `kradar_visibility_analysis_prompt.md` verbatim.
- Lives at the package root: `kradar_visibility/README.md` (or repo root
  if the package is the whole repo).
- No marketing language, no restating this spec doc's section headers
  word-for-word as filler — each section needs real content pulled from
  the actual implementation.
