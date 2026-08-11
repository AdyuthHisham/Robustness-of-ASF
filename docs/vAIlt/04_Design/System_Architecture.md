# System Architecture

`kradar_visibility` — CPU-only visibility analysis pipeline for K-Radar. Reads `info_label_rev2/*.txt` annotations plus raw sensor data (radar `zyx_cube`, OS2-64/OS1-128 LiDAR PCDs, 4-camera stereo images), computes per-object visibility metrics for 7 sensors, emits one Parquet table. Runs on toy-scale subsets (1–2 sequences, ≤20 annotated frames) in seconds on CPU; full-dataset and GPU-accelerated modes are explicitly out of scope for this build.

## Module layout

```
kradar_visibility/
├── config.py                # paths, sensor specs, schema, constants — no logic
├── parser.py                 # info_label_rev2/*.txt parser
├── calibration.py             # camera calibration loading (T_params_seq pickles)
├── data_loader.py             # lazy sensor data loading (radar/lidar/camera), returns None on missing files
├── radar_visibility.py        # SNR-weighted power density score
├── lidar_visibility.py        # CPU point-in-box count → expected-density ratio
├── camera_visibility.py       # 8-corner projection → area × centrality score
└── pipeline.py                 # orchestration: parse → compute → output
```

## Data flow

```
sequence_ids
  → parser.get_sequence_label_files()          List[Path]
  → parser.parse_label_file()                   (HeaderInfo, List[ObjectAnnotation])   [per file]
  → data_loader.load_radar_cube/load_lidar_points/calibration.get_camera_params()       [per frame]
  → radar_visibility / lidar_visibility / camera_visibility                              [per object]
  → pipeline.compute_visibility_for_frame()      List[dict]
  → polars.DataFrame → parquet write
```

Full formula-level detail for each visibility computation is in [[03_Theory/Visibility_Formulas]]; the coordinate convention all of this operates in is [[03_Theory/Coordinate_Frames]].

## Error handling strategy

| Failure | Handling |
|---|---|
| Missing sensor file | `data_loader` returns `None` → `visible=False, score=0.0` — logged, never raises |
| Calibration load failure | log warning, `calib_available=False` → camera metrics zeroed |
| Empty result set | log warning, return empty `pl.DataFrame()` |
| Per-frame exception | log warning, skip frame, continue |

This "degrade, don't crash" contract is a hard project rule (see `AGENTS.md`), not just an implementation convenience — a partial-dataset run should never abort on one bad frame.

## CLI configuration

All tunables live in `config.py` (module constants, no external config file loaded at runtime). The CLI entry point (`scripts/run_pipeline.py`) exposes: `--sequences` (default `1, 2`), `--frame-limit` (default 20 annotated frames, not raw file count — empty-object frames are skipped), `--output` (Parquet path), `--dataset-root`, `--no-report`.

## Web viewer — architecture addendum

A FastAPI + static HTML/JS viewer reuses `config.py`, `data_loader.py`, `calibration.py`, and `pipeline.compute_visibility_for_frame()` to serve sensor data and annotations for visual inspection. **Chosen over Flask/Jinja2** because: (1) clean API/frontend separation mirrors the existing `pipeline.py`/viewer module boundary, (2) FastAPI's Pydantic models give automatic request/response validation as a canonical frontend contract, (3) uvicorn/ASGI is production-viable without a later rewrite, (4) zero duplication of file-loading logic — the viewer imports the pipeline's own modules rather than reimplementing them.

```
src/kradar_visibility/viewer/
├── server.py        # FastAPI app + endpoints
└── static/{index.html, style.css, app.js}   # single-page vanilla JS, no build step
```

**Endpoints:** `GET /api/sequences`, `/api/frames/{seq_id}`, `/api/frame/{seq_id}/{frame_idx}` (full frame: annotations + visibility + box corners), `/api/image/{seq_id}/{cam}/{frame_idx}` (JPEG), `/api/lidar/{seq_id}/{sensor}/{frame_idx}` (JSON points), `/api/radar/{seq_id}/{frame_idx}` (PNG top-down heatmap).

**Frontend layout:** sequence/frame selector → camera view (image + SVG box overlay) and radar heatmap (canvas, top-down max-projection) side by side; LiDAR top-down scatter and a per-object visibility-scores table below. Toy-scale (2 seq × 20 frames) means everything fits in RAM — no caching layer, no pagination.

Full endpoint request/response schemas (Pydantic models, exact function signatures for every module) are in [[API_Contracts]] — this note covers the shape of the system, that one is the literal interface spec.

## Source

- `test-bed/src/Modules/robust_testing/kradar/architecture.md` (421 L, canonical — full module responsibilities with function-level detail, dependency list, test-structure mapping)
