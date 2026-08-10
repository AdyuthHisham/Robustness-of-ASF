# Noise Visual Inspection Report — v2

Supersedes `noise-visual-inspection-report.md` (stale on two fronts: generated
against the pre-AI-MSF-Benchmark `loss_partial` mechanism, and using the
default `render_bev` style that cannot show zero-out corruption at all —
see `loss-partial-zeroout-visibility-diagnostic.md`). Same 3 non-consecutive
frames as the original, for direct comparability.

## Frames (unchanged from v1)

| # | Label | Seq | RDR idx | LiDAR idx | Cam idx | Objects | Scene |
|---|-------|-----|---------|-----------|---------|---------|-------|
| 1 | seq001_rdr033 | 1 | 33 | 1 | 2 | Sedan ~24m | Highway |
| 2 | seq021_rdr015 | 21 | 15 | 11 | 34 | Sedans ~2-5m | Urban |
| 3 | seq048_rdr035 | 48 | 35 | 30 | 89 | Bus/Truck 14-58m | Mixed |

## What changed vs. v1, per effect

**Re-confirmed unchanged (original `render_bev` style, current code, all 3 frames):**

- radar: `frame_deletion`, `noise_induced_shifts`, `loss_complete`
- lidar: `frame_deletion`, `gaussian_noise`, `loss_complete`
- camera: `frame_deletion`, `gaussian_noise`, `loss_complete`

These 9 effects' underlying functions are untouched by both the loss_partial
AI-MSF swap (`loss-partial-aimsf-replacement-report.md` §7: "Files NOT
Modified... frame_deletion, loss_complete, gaussian_noise,
noise_induced_shifts") and the frame_deletion RNG-desync fix
(`frame-deletion-rng-desync-fix-report.md`: that fix touched only the
`NoiseInjector` class's `should_skip`/`__call__`/cache plumbing, not the
standalone `radar_frame_deletion`/`lidar_frame_deletion`/`camera_frame_deletion`
functions this inspection calls directly). Visual re-inspection of all 27
renders (9 effects × 3 frames) confirms output consistent with the v1
report's descriptions — diffuse Gaussian point clouds for `noise_induced_shifts`/
`gaussian_noise`, correct blackout/`NO DATA` canvas for `frame_deletion`/
`loss_complete`.

**Caveat on the confirmation method:** a byte-for-byte diff against the
original v1 PNGs was intended but not achievable — the regeneration script's
first (buggy) run overwrote the v1 files in place before the bug was caught,
so no pristine v1 baseline survives on disk for these effects. Confirmation
instead rests on (a) source-level verification that the relevant functions in
`noise_injection.py` are byte-identical to what they were when v1 was
generated (per the two reports cited above, which enumerate exactly what was
and wasn't touched), and (b) visual inspection of the regenerated images
against the v1 report's written descriptions and parameter table. All 9
effects are self-consistent across repeat runs of the v2 script (48/48
non-loss_partial renders byte-identical across two consecutive runs), so the
regeneration itself is deterministic even though the true v1 originals are
gone.

**Fixed rendering (radar/lidar `loss_partial`):** now use the zero-out-aware
`render_bev_zeroout()` established in `loss-partial-zeroout-visibility-diagnostic.md`
— zeroed rows drawn as a distinct magenta marker (vs. orange survivors),
zoomed ±3m origin inset with crosshair, and a legend panel reporting exact
surviving/zeroed counts and actual fraction. The old `render_bev` style is
confirmed incapable of showing this corruption (collapsed points render as
one invisible pixel at the origin); replacing it was the point of this
regeneration. Spot-checked at fraction=0.5: e.g. `seq021_rdr015` lidar shows
36,784/73,569 rows (0.500 exact) zeroed and collapsed at the origin, clearly
visible in both the full-scene magenta cluster and the zoomed inset.

**Re-confirmed correct under current code (new mechanism, not stale):**
camera `loss_partial` — the flatten-permute-zero salt-and-pepper mechanism
(replacing the old rectangular block-occlusion) renders as dense per-pixel
speckle/grain across the full frame, structurally distinct from both `clean`
and `loss_complete` (full blackout) in all 3 frames. No rendering fix needed
here (already established in the zero-out diagnostic); this run just confirms
it still looks right under the current `noise_injection.py` at fraction=0.3.

**`frame_deletion` — included, and a random-mode spot-check added:**
frame_deletion (deterministic mode, `index_list=[0]`) was in the original v1
effect list and is in this one too. v1 only exercised deterministic mode; v2
adds a `frame_deletion_random` (p=0.5) render per modality per frame,
seeded per-frame (not just per-effect) so the coin-flip decision actually
varies across the 3 frames rather than repeating the same draw. Result: radar
and lidar fired (deleted) on all 3 frames at this seed, camera fired on 2/3
(deleted → near-black `frame_deletion_random.png` for `seq001_rdr033` and
`seq021_rdr015`, intact frame for `seq048_rdr035`) — both outcomes (deleted /
kept) are represented, confirming random mode behaves as a real per-frame
coin flip and not a frozen decision. The RNG-desync fix
(`frame-deletion-rng-desync-fix-report.md`) is scoped to `NoiseInjector`'s
`should_skip()`/`__call__()` interaction, which this script never invokes
(it calls `radar_frame_deletion`/etc. directly with a single `rng` draw per
call) — so that fix has no bearing on these renders, consistent with the fix
report's own stated scope.

## Known limitation introduced during regeneration (fixed, documented for transparency)

The first version of the v2 script had two bugs, both caught before the final
run:

1. Imported `noise_injection.py` from the git worktree used to isolate this
   work, which — being freshly branched from the last commit — held the
   *stale* pre-AI-MSF-swap version (the swap is currently uncommitted in the
   working tree). This produced `radar_loss_partial` output that shrank the
   array (Bernoulli-deletion semantics) instead of preserving row count
   (zero-out semantics). Fixed by importing `noise_injection.py` from the
   original checkout path explicitly.
2. Built `dict_item['meta']['idx']` from each frame's real rdr/ldr/cam index
   instead of all-zero (as the original v1 script did), which silently
   disabled deterministic `frame_deletion` (index_list=[0] no longer matched
   a real index like 33). Fixed by reverting to all-zero idx, matching v1.

Both are visible as inline comments in `visualize_effects_v2.py` at the
fixed call sites.

## Output location

**Consolidated in place** at the original location — no `v2/` subfolder.
Rationale: only 6 of 39 non-clean effect images (loss_partial × 3 modalities
× radar/lidar fixed-render, camera re-confirmed) actually needed new pixels;
the other 27 are re-renders of unchanged effects. A parallel `v2/` directory
would duplicate ~33 identical-content images for no benefit and invite the
two directories drifting out of sync. `index.html` and `v2_regeneration_confirmation.md`
were regenerated in place and now carry v2 badges (`FIXED RENDER` /
`RE-CONFIRMED`) per effect, so anyone opening the index sees explicitly which
effects are new-style vs. re-confirmed — there is no ambiguous prior version
left in the directory to confuse with.

- Root: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/noise_visual_inspection/`
- Index: `outputs/noise_visual_inspection/index.html`
- Confirmation log: `outputs/noise_visual_inspection/v2_regeneration_confirmation.md`
- Params: `outputs/noise_visual_inspection/effect_parameters.yaml`
- Script: `repos/K-Radar/datasets/effects/visualize_effects_v2.py` (new; does not modify `visualize_effects.py`, `noise_injection.py`, or `diagnose_loss_partial_zeroout.py`)
- This report: `docs/vAIlt/noise-visual-inspection-report-v2.md`

## Not touched

`noise_injection.py`, training code paths, `visualize_effects.py` (v1 script,
left in place for history), `diagnose_loss_partial_zeroout.py`.
