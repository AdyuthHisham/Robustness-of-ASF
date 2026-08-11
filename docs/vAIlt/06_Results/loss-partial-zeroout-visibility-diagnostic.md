# Loss-Partial Zero-Out Visibility Diagnostic

Companion to `loss-partial-aimsf-replacement-report.md` (mechanism change) and
`loss-partial-aimsf-replacement-verification.md` (correctness verification, which
left an open caveat on visual legibility). Supersedes the *diagnosis* — not the
frames or plotting conventions — of `noise-visual-inspection-report.md`, which
was written against the old Bernoulli-deletion mechanism and is now stale for
`loss_partial` specifically (still valid for the other 9 effects it covered).

Script: `repos/K-Radar/datasets/effects/diagnose_loss_partial_zeroout.py` (new,
standalone, does not modify `noise_injection.py`). Run via
`.smoke_venv/bin/python datasets/effects/diagnose_loss_partial_zeroout.py`.

Frames (same 3 non-consecutive frames as the old report, for comparability):

| Label | Seq | RDR idx | LiDAR idx | Cam idx |
|---|---|---|---|---|
| seq001_rdr033 | 1 | 33 | 1 | 2 |
| seq021_rdr015 | 21 | 15 | 11 | 34 |
| seq048_rdr035 | 48 | 35 | 30 | 89 |

Fraction used: 0.30 for radar/lidar/camera `loss_partial` (matches the current
`radar_loss_partial`/`lidar_loss_partial` default of 0.3 in
`noise_injection.py`; camera's own default is 0.2 but 0.3 was used here to
match the old report's camera value for direct visual comparability — see
re-tuning recommendation below).

## 1. Confirmed current mechanism

Read `radar_loss_partial`, `lidar_loss_partial`, `camera_loss_partial` in full
(`repos/K-Radar/datasets/effects/noise_injection.py:176-203, 272-297, 385-429`).

- Radar/LiDAR: `loss_num = int(n * fraction)`; `index = rng.permutation(n)[:loss_num]`;
  `arr[index] = 0` (exact zero, all columns, not jittered — literally `(0,0,0,...)`).
  Row count unchanged.
- Camera: same permutation-zero-out but on the **flattened** `(H*W*3,)` uint8
  array — individual R/G/B scalars are zeroed independently, not whole pixels.

Empirical verification (all 3 frames, fraction=0.30), from
`outputs/noise_visual_inspection/loss_partial_zeroout_diagnostic/before_after_counts.md`:

| Frame/Modality | n_before | n_after | Preserved | Zeroed | Expected | Actual frac |
|---|---|---|---|---|---|---|
| seq001_rdr033/radar | 150000 | 150000 | True | 45000 | 45000 | 0.3000 |
| seq001_rdr033/lidar | 60601 | 60601 | True | 18180 | 18180 | 0.3000 |
| seq001_rdr033/camera | 5,529,600 | 5,529,600 | True | 1,671,600 | 1,658,880 | 0.3023 |
| seq021_rdr015/radar | 150000 | 150000 | True | 45000 | 45000 | 0.3000 |
| seq021_rdr015/lidar | 73569 | 73569 | True | 22070 | 22070 | 0.3000 |
| seq021_rdr015/camera | 5,529,600 | 5,529,600 | True | 1,659,009 | 1,658,880 | 0.3000 |
| seq048_rdr035/radar | 150000 | 150000 | True | 45000 | 45000 | 0.3000 |
| seq048_rdr035/lidar | 48209 | 48209 | True | 14462 | 14462 | 0.3000 |
| seq048_rdr035/camera | 5,529,600 | 5,529,600 | True | 1,659,679 | 1,658,880 | 0.3001 |

Radar/LiDAR: zeroed count == expected exactly (integer permutation count).
Camera: observed zero-scalar count is slightly *above* expected because the
clean image already contains some pre-existing black (0,0,0) pixel channels
(deep shadow in a night scene) — this is the correct comparison (`>=`, not
`==`) and does not indicate a mechanism bug.

## 2. Zero-out clustering artifact: confirmed present

Yes — the artifact occurs, and it is severe under default plotting conventions.

Radar/LiDAR: all zeroed rows land at exactly world-origin `(0,0,0)`. In the BEV
scatter these 45,000 (radar) or up to 22,070 (LiDAR) collapsed rows render as
literally **one overlapping marker** at the origin pixel — indistinguishable
from a single stray point. Compare:

- `frame_seq021_rdr015/lidar_loss_partial_DEFAULT_before.png` — 73,569 pts
  rendered with the original plotting style; no visual indication that 22,070
  of them (30%) were just zeroed. The corruption is **completely invisible**.
- `frame_seq021_rdr015/lidar_loss_partial_FIXED_after.png` — same data, fixed
  rendering: a single magenta marker at the origin, legend reads "zeroed
  (near-origin): 22070", and a zoomed ±3m origin inset with a crosshair
  confirms the marker sits exactly at (0,0). Confirms 22,070 rows are really
  there, not a rendering artifact of the annotation itself — the inset is
  drawn from the same underlying point array with a tighter axis range.

Same pattern holds for all 3 frames × radar and lidar (6 image pairs total,
under `outputs/noise_visual_inspection/loss_partial_zeroout_diagnostic/frame_*/`).

This is a **different failure mode** from the old report's diagnosis. The old
report (pre-mechanism-change) found that *sparse point deletion* was
imperceptible because removing points from an already-dense point cloud barely
changes the visual density — a density problem. The new problem is not about
density: it's that removed information doesn't vanish, it **piles up at a
single coordinate**, and any plot that doesn't special-case the origin will
render 14k–45k corrupted points as 1 pixel. These require different fixes (the
old report's fix would have been about point size/opacity/subsampling
comparison; this one is about coordinate-collapse detection) — do not treat
the old report's conclusions as still applicable to `loss_partial`.

## 3. Visualization fix applied

Option (a) combined with a zoomed origin inset, per the task's suggested
preference: zeroed rows are drawn in distinct magenta (vs. surviving points in
orange), given a larger marker radius (5px vs 2px) plus a white outline ring so
the stacked cluster reads as a single deliberate marker rather than noise, a
legend panel reports exact surviving/zeroed counts and actual zeroed fraction,
and a bottom-right ±3m zoomed inset around the origin (with crosshair) proves
the cluster is real and at the expected location. This was chosen over (b)
exclude-and-badge because keeping the corrupted points positionally visible
(even if collapsed) is more informative for debugging pipelines than hiding
them — and over pure (c) table-only because the geometric collapse itself
(everything going to exactly one point) is the finding worth seeing, not just
a count.

Implementation: `render_bev_zeroout()` in
`repos/K-Radar/datasets/effects/diagnose_loss_partial_zeroout.py` (lines
~152-240). Does not modify `noise_injection.py` or `visualize_effects.py`.

## 4. Camera loss_partial: visual confirmation

`frame_*/camera_clean_vs_loss_partial_vs_loss_complete.png` (3-panel composite,
one per frame) confirms:

- CLEAN vs LOSS_PARTIAL (frac=0.3): dense, uniform speckle/grain across the
  entire frame — classic salt-and-pepper, structurally different from the old
  rectangular block-occlusion mechanism (no rectangular patches, no clean
  edges) and clearly *not* full blackout.
- LOSS_COMPLETE: fully black, trivially distinguishable from both.

All three states are visually distinguishable from each other in every frame
inspected; no further action needed for camera legibility at fraction=0.3.

## 5. Config fraction re-tuning recommendation

**Radar/LiDAR loss_partial (default fraction=0.3): re-tuning is not required
for correctness, but IS required if the intent is for a human eyeballing a
default-style BEV plot to notice the corruption without dedicated tooling.**
At fraction=0.3, up to 45,000 radar rows or 22,070 lidar rows are corrupted per
frame, but under the *original* `visualize_effects.py` plotting style they are
invisible — indistinguishable from an intact frame with a single stray origin
point (see §2). This is not a magnitude problem (0.3 is a substantial
fraction of the data being altered) but a **rendering** problem: any
Bernoulli-deletion-era plot that assumes "corruption = fewer points" will miss
zero-out entirely regardless of what fraction is configured, because ALL
zeroed points overlap at exactly one coordinate no matter how many there are.
Raising the fraction would not fix this — even fraction=1.0 collapses to the
same single origin pixel under the old plot style. Recommendation: **do not
re-tune the fraction; instead adopt the zero-out-aware rendering style
(§3) as the default going forward for any human-in-the-loop visual QA
involving `loss_partial`.** This directly closes the open caveat left by
`loss-partial-aimsf-replacement-verification.md` — the corruption IS applied
correctly and at the configured strength; it was a visualization gap, not a
config-tuning gap.

Camera loss_partial (fraction=0.3 as tested here, default 0.2 in code):
already clearly visible as salt-and-pepper noise at both values without any
visualization fix — no re-tuning needed.

## 6. Proposed code change (NOT implemented, awaiting approval)

None required. The task anticipated a possible near-origin jitter parameter in
`noise_injection.py` to visually separate collapsed points, but the zoomed
inset + distinct-marker approach in `render_bev_zeroout()` fully resolves
legibility without touching the corruption semantics or the output schema of
`noise_injection.py`, so no change to that file is proposed.

## Output files

Root: `repos/K-Radar/outputs/noise_visual_inspection/loss_partial_zeroout_diagnostic/`

- `before_after_counts.md` — full row-count table (reproduced in §1)
- `frame_seq001_rdr033/`, `frame_seq021_rdr015/`, `frame_seq048_rdr035/` — each contains:
  - `radar_clean.png`, `lidar_clean.png`
  - `radar_loss_partial_DEFAULT_before.png`, `lidar_loss_partial_DEFAULT_before.png` — old plotting style, artifact invisible
  - `radar_loss_partial_FIXED_after.png`, `lidar_loss_partial_FIXED_after.png` — new style, artifact clearly visible with counts + origin inset
  - `camera_clean_vs_loss_partial_vs_loss_complete.png` — 3-panel comparison
