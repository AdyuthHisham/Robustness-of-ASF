# Chunk 1 — Reviewer B (Claims integrity) — kradar_visibility core modules

## Findings

### B-1-01
- Doc: `test-bed/src/Modules/robust_testing/kradar/architecture.md:153-166` (§ `lidar_visibility.py` responsibilities)
- Code: `test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/lidar_visibility.py:116-320`
- Mechanism: architecture.md describes the module as "Implements §4.2 method A+B: CPU point-in-box count → expected-density ratio," with the score formula stated as `score = count / expected_density` and no mention of occlusion. The actual `calculate_lidar_visibility()` accepts optional `range_image`/`sensor_origin` args and, when provided, computes `final_score = density_ratio * (1.0 - occluded_fraction * confidence)` via a range-image-based occlusion model (`_compute_occlusion_fraction_from_range_image`, `_validate_range_image_dimensions`) — an entirely different, more complex algorithm than what the doc describes. Docstring in the code itself even says "NEW: Added support for precomputed range image to compute occlusion fraction," confirming this was added after the doc was last accurate.
- Contradiction: a reader relying on architecture.md would believe LiDAR visibility is a simple point-count ratio; the code's default caller (per pipeline.py, see B-1-02) actually applies an occlusion discount driven by a separately-built range image, changing scores for any object with `occluded_fraction > 0`.
- Severity: doc-drift (the underlying occlusion logic itself is not verified wrong here — only the doc mismatch is being reported by this lens).

### B-1-02
- Doc: `test-bed/src/Modules/robust_testing/kradar/architecture.md:169-189` (§ `camera_visibility.py` responsibilities)
- Code: `test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/camera_visibility.py:18, 405-424`
- Mechanism: architecture.md describes camera visibility purely as "8-corner projection → 2D bbox → area/centrality score" with `Score = W1 * (clipped_area / image_area) + W2 * (1 - normalised_center_dist)` and lists only `W1`, `W2`, `HALF_WIDTH`, `HALF_HEIGHT` as constants. The code imports `DEPTH_MARGIN, DEPTH_SAMPLE_RADIUS` from config.py and implements a depth-buffer occlusion pass (`occluded_count`, `if d_local < z_obj - DEPTH_MARGIN: occluded_count += 1`, `occlusion_discount = 1.0 - (occluded_count / valid_count)`) that architecture.md never mentions.
- Contradiction: the doc's formula omits an entire occlusion-discount term that the code applies to the final camera score.
- Severity: doc-drift.

### B-1-03
- Doc: `test-bed/src/Modules/robust_testing/kradar/architecture.md:235-269` (§ Output Schema table)
- Code: `test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py:110-161` (`OUTPUT_SCHEMA`)
- Mechanism: architecture.md's Output Schema table lists 33 columns and does not include `lidar64_visible_confirmed`, `lidar128_visible_confirmed`, `ghost_flag`, or `occluded`. The actual `config.OUTPUT_SCHEMA` list (config.py:110-161) has 46 entries and includes all four of those columns, which are populated by `pipeline.py` (`lidar64_visible_confirmed` at pipeline.py:370/486, `lidar128_visible_confirmed` at pipeline.py:371/490, `ghost_flag` at pipeline.py:515, `occluded` at pipeline.py:521).
- Contradiction: architecture.md's schema table is not a superset/match of the real output — four real output columns are entirely undocumented there, so anyone using architecture.md as "the reference" (as CLAUDE.md instructs) to understand the Parquet schema will miss these fields and their semantics (`ghost_flag` = radar-visible but no other sensor sees it; `occluded` = in radar FOV/range but zero sensors visible).
- Severity: doc-drift.

### B-1-04
- Doc: `test-bed/src/Modules/robust_testing/kradar/config.py:108-109` (comment, in-file doc)
- Code: `test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py:110-161`
- Mechanism: comment says "Harmless in practice since polars.DataFrame(list[dict]) keys columns by name, not list position, but keep these in sync so this list stays trustworthy as documentation" — i.e. config.py itself flags that OUTPUT_SCHEMA's job is to be trustworthy documentation of the real row-dict shape. Given B-1-03, that self-imposed contract (constants file only, "no logic," "single source of truth" per architecture.md:59-62) already holds for the config.py list vs. pipeline.py's row dict — the drift is specifically between config.py (accurate) and architecture.md's separate hand-written table (stale). Noting this only to make clear B-1-03 is a doc/doc drift, not a config/code bug — config.py's list itself was NOT found to be missing any pipeline.py-emitted column in this pass.
- Severity: cosmetic (context note, not a new independent finding — folded under B-1-03).

## Unverified / Suspicion

- `lidar_visibility.py:263-264` code comment claims a specific confirmed numeric discrepancy ("occluded_fraction 0.0 (buggy, wrong bins) vs. 0.167 (correct) for the same range image") from a prior bug fix. This reads as a real prior finding already fixed in code, not a currently-live doc/code mismatch — did not independently reproduce the 0.0-vs-0.167 numbers, so not asserting them as a current finding; flagged only because it's the kind of specific claim Reviewer A's lens should check whether it's still true post-fix.
- Did not check whether `docs/vAIlt/04_Design/API_Contracts.md`'s `CAMERA_INTRINSICS`/`CAMERA_EXTRINSICS` placeholder-zero description (config.py:82-100, explicitly commented "placeholder values ... In a real system, these would be loaded from calibration files") is itself accurately described elsewhere as dead/unused in favor of `calibration.py`'s pickle-loaded real values — out of scope for chunk 1 core-module cross-check as specified, but likely relevant to chunk 3/4 doc-claims about calibration accuracy. Flagging for later chunks, not asserting a finding here.
