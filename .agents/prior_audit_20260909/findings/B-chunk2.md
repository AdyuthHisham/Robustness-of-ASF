# Chunk 2 — Reviewer B (Claims integrity) — kradar_visibility tests

## Findings

### B-2-01: SMK-16 test doesn't test the comparison its docstring/spec claims

- Doc/spec: `docs/vAIlt/05_Implementation/6_Smoke_Test_Scaffold.md:147-149` — "SMK-16: center-of-frame object score > edge-of-FOV object score. Tests method B from §4.3." Test function is even named `test_smk16_camera_score_center_gt_edge`.
- Code: `test-bed/src/Modules/robust_testing/kradar/tests/test_smoke.py:195-205`
- Mechanism: the test body only constructs `center_corners` (a single object in front of the vehicle) and asserts `scores['front'] > 0`. No edge-of-FOV object is ever constructed, scored, or compared. There is no `>` comparison anywhere in the function — the ">" in both the spec's claim and the function name is untested.
- Contradiction: both the spec doc and the function name assert a center-vs-edge score comparison exists; the actual assertion only checks the center object's score is positive, which a completely broken centrality term (e.g. constant score) would still pass.
- Severity: doc-drift.

### B-2-02: VER-32 "distortion correction applied when coefficients provided" test calls the function identically both times — no comparison is possible or made

- Doc/spec: `test-bed/src/Modules/robust_testing/kradar/tests/test_verify.py:322-323` (docstring) — "VER-32: distortion correction applied when coefficients provided."
- Code: `test-bed/src/Modules/robust_testing/kradar/tests/test_verify.py:352-356`
- Mechanism: `score_no_dist = calculate_visibility_score(obj_corners, cam_params)` and `score_with_dist = calculate_visibility_score(obj_corners, cam_params)` — both calls pass the exact same `cam_params` dict, which already has `dist_coeffs` set (line 344-349). There is no second `cam_params` variant with `dist_coeffs=None` to compare against. The only assertions are `0.0 <= score_no_dist <= 1.0` and `0.0 <= score_with_dist <= 1.0` (range checks on what are, by construction, the same computation run twice). The trailing comment even concedes this: "The scores should be computable (distortion correction doesn't break anything)" — a materially weaker claim than the docstring's "distortion correction applied."
- Contradiction: the docstring claims distortion correction is verified to apply; the code verifies nothing about distortion at all — it can't, since both branches are identical calls.
- Severity: doc-drift.

### B-2-03: VER-30 and VER-31 assert only score range validity, not the comparative behavior their docstrings claim

- Doc/spec: `test-bed/src/Modules/robust_testing/kradar/tests/test_verify.py:240-241` — "VER-30: radar score adapts to local noise variations when noise floor map provided." And `tests/test_verify.py:277-278` — "VER-31: calculate_visibility_score applies depth-buffer occlusion discount when depth map provided."
- Code: `tests/test_verify.py:266-272` (VER-30) and `tests/test_verify.py:315-320` (VER-31)
- Mechanism: VER-30 computes `score_low_noise` and `score_high_noise` from a cube with a deliberately weaker signal in the noisier region, then only asserts both are within `[0,1]`; the file's own comment admits "Note: Exact comparison depends on the specific values, but we can check they're computed" — no comparison between the two scores is asserted. VER-31 computes `score_no_depth` and `score_with_depth`, asserts both are within `[0,1]`, and its trailing comment says "With occlusion indication, score should be reduced (Note: actual projection math needed to confirm, but principle tested)" — again, no assertion that `score_with_depth < score_no_depth` (or any inequality) exists.
- Contradiction: both docstrings claim the noise-floor-map / depth-map mechanism is being verified to change behavior in a specific direction; the actual test bodies verify only that scores stay in the valid `[0,1]` range regardless of whether the mechanism does anything at all — a no-op implementation of either feature would pass both tests.
- Severity: doc-drift.

## Unverified / Suspicion

- `TestGhostFlag` docstring (`tests/test_verify.py:657`) cites "ghost_flag formula (pipeline.py:481)" — did not cross-check this line number against the current `pipeline.py` in this pass (chunk 1's B-1-03 noted `ghost_flag` is populated around pipeline.py:515 in one finding's citation, which doesn't match 481 — worth a follow-up line-number reconciliation, but not asserted as a finding here since exact current line numbers for ghost_flag computation weren't independently re-verified in this chunk).
- `TestWeatherImpact` (VER-25/VER-26, `tests/test_verify.py:753-761`) are both unconditional `pytest.skip(...)` — always skipped, never actually run. This is visible in the code (not hidden), so it's a weaker case for a "claims" finding than B-2-01/02/03, but flagged here in case chunk 5/6 vault docs claim VER-25/26 as implemented/passing checks — that would be a real doc-drift finding in those chunks, not this one.
- Did not statically audit every SMK-*/VER-* docstring line-by-line against its assertion (large file); focused on the ones graphify's initial query surfaced as distinct test classes (TestLidarWithRangeImage, TestRadarWithNoiseFloorMap, TestCameraWithDepthMap, TestGhostFlag, TestCameraProjectionSanity, TestDataQuality, TestPrimarySensorLogic) plus SMK-*. A few individual VER-0X in TestSensorIdentifyConsistency/TestDistanceCorrelation were spot-checked and matched their docstrings.
