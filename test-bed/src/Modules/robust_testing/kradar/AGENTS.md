# AGENTS.md — kradar_visibility

## Project context

- Python package computing per-object multi-sensor visibility metrics
  (radar, LiDAR ×2, camera ×4) from the K-Radar dataset, output as a
  single Parquet table.
- Dataset (read-only): `/home/adhish/Productivity/AMSCUP/repos/K-Radar`
- Project root: `/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar`
- Specs live in this repo's `docs/` (or wherever the 5 md files were
  copied): `kradar_visibility_analysis_prompt.md`,
  `04_visibility_methodology.md`, `06_smoke_tests_scaffold.md`,
  `07_verification_tests_scaffold.md`, `00_orchestrator_kickoff_prompt.md`.
  Read these before writing code that touches schema, metrics, or tests.

## Package management — uv, exclusively

This project uses **[uv](https://docs.astral.sh/uv/)** for everything.
Never use `pip install`, `python -m venv`, `conda`, `poetry`, or a manually
activated virtualenv — if a command needs a `python` invocation, it's
`uv run <command>`, full stop.

- **Init**: `uv init` was already run if `pyproject.toml` exists — don't
  re-init. If starting fresh, `uv init --package kradar_visibility`.
- **Add a dependency**: `uv add <package>` (e.g. `uv add polars pyarrow numpy opencv-python`).
  Never hand-edit `pyproject.toml`'s dependency list and never write a
  `requirements.txt` by hand — `uv export` if one is ever needed for an
  external consumer.
- **Add a dev-only dependency**: `uv add --dev pytest pytest-cov pytest-json-report tqdm`.
- **Run anything**: `uv run python script.py`, `uv run pytest`,
  `uv run kradar-pipeline` (if an entry point is defined). Never invoke
  `python` or `pytest` directly — the project's interpreter and locked
  deps only exist inside `uv run`.
- **Sync the environment**: `uv sync` after pulling changes that touch
  `pyproject.toml` / `uv.lock`. Don't manually `pip install -e .`.
- **Lockfile**: `uv.lock` is committed and authoritative. Don't delete or
  hand-edit it — regenerate via `uv lock` if it's genuinely stale.
- **Python version pinning**: if a specific interpreter is needed, use
  `uv python pin 3.11` (or whichever version the GPU stack requires) rather
  than relying on whatever `python3` resolves to on the system.
- **CLI entry points / scripts**: define console scripts in
  `pyproject.toml` `[project.scripts]` and invoke them as `uv run <name>`,
  not via a bare path to `scripts/run_pipeline.py`.

## Coding conventions

- **Polars, not pandas**, for all tabular work — consistent with the
  existing `headers_df`/`objects_df` pattern already used in this codebase.
- Type-hint all public functions; prefer dataclasses for structured
  records (calibration objects, parsed headers) over raw dicts/tuples.
- Reuse existing GPU primitives before writing new ones — in particular,
  the existing `points_in_boxes_gpu` (OpenPCDet)-based LiDAR point-in-box
  pipeline elsewhere in this repo. Don't reimplement it.
- Vectorize per-frame, per-object computation where the methodology doc
  specifies it (radar/LiDAR/camera scores must scale across all objects
  in a frame, not loop per-object in pure Python).
- Never load `radar_tesseract/` (full 4DRT) by default — `radar_zyx_cube/`
  is the default radar input; full-tensor mode is an explicit opt-in flag.
- Missing sensor files degrade to `visible=False, score=0.0` — never raise
  on a missing frame; log a warning and continue.

## Tests

- All tests in `tests/`, run via `uv run pytest`.
- `tests/test_smoke.py` — fast sanity checks (SMK-01..17), must complete
  in under 5 minutes on 1–2 sequences. Run these before anything else.
- `tests/test_verify.py` — full-dataset correctness checks (VER-01..26).
  Only run after smoke tests pass: `uv run pytest tests/test_verify.py`.
- Test IDs in docstrings must match the spec doc IDs (`SMK-01`, `VER-12`,
  etc.) so failures map directly back to the methodology/scaffold docs.

## Hard rules

- Never commit `.env` files, dataset paths outside the documented roots,
  or any K-Radar raw sensor data into the repo.
- Never use `pip`, `conda`, or a bare `python`/`pytest` invocation — `uv`
  only, every time.
- Don't change the schema in §3.1 of `kradar_visibility_analysis_prompt.md`
  without flagging it — downstream analysis queries (§10) depend on exact
  column names.
