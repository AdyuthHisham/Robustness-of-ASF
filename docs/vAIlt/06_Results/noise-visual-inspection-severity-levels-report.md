# Noise Visual Inspection — Severity Levels (v3)

Extends `noise-visual-inspection-report-v2.md` from one fixed parameter value
per effect to three severity levels (**low / medium / high**) per effect, for
all 11 severity-capable effects in the 12-effect taxonomy (`loss_complete`
excluded — see below). Same 3 non-consecutive frames as v1/v2, for
continuity: `seq001_rdr033`, `seq021_rdr015`, `seq048_rdr035`.

Script: `repos/K-Radar/datasets/effects/visualize_effects_v3_severity.py`
(new; does not modify `noise_injection.py`, `visualize_effects.py`,
`visualize_effects_v2.py`, or `diagnose_loss_partial_zeroout.py`). Reuses
v2's `render_bev`, `render_bev_zeroout`, data loaders, and tensor helpers by
import rather than reimplementing.

## Output location

- Root: `repos/K-Radar/outputs/noise_visual_inspection/` (same directory as
  v2 — consolidated in place, matching v2's own precedent)
- Per-frame, per-modality, per-effect, per-severity:
  `frame_<label>/<modality>/<modality>_<effect>_<low|medium|high>.png`
- `loss_complete` (no severity axis): `frame_<label>/<modality>/<modality>_loss_complete.png`
  (no severity suffix)
- Index: `outputs/noise_visual_inspection/index.html` (updated in place,
  now a 3-column low|medium|high grid per effect)
- Severity params: `outputs/noise_visual_inspection/severity_parameters.yaml`
- `frame_deletion` realized-outcome log: `outputs/noise_visual_inspection/frame_deletion_severity_log.md`
  (see below — `frame_deletion` needed a probabilistic-outcome log that the
  other effects don't)
- This report: `docs/vAIlt/noise-visual-inspection-severity-levels-report.md`

45 PNGs per frame (135 total): 3 severities × 3 effects × 3 modalities (27),
+ 1 `loss_complete` × 3 modalities (3), + the pre-existing `clean` reference
per modality (3) carried over from v2, + v2's original single-value
`frame_deletion_random`/`gaussian_noise`/etc. files left untouched on disk
(not regenerated or referenced by the new index).

## Severity parameter values, per effect, traced to the param sweep

All values below are reused directly from tested points in
`noise-injection-param-sweep-report.md` (Rev 2 taxonomy sweep, 109/109
PASS) — no new untested values were introduced except where noted.

### `loss_partial` (radar / lidar / camera) — fraction

| Severity | fraction | Sweep row |
|---|---|---|
| low | 0.1 | *(interpolated between tested 0.01 and 0.3 — not itself a swept point, but the row-count-exact behavior is confirmed monotonic and formula-exact across the full swept range 0.0–1.5, so any fraction in that range inherits the same guarantee)* |
| medium | 0.3 | R3/L3/C3 `fraction=0.3` — existing v2 default |
| high | 0.8 | R3/L3/C3 `fraction=0.8` |

Note: `fraction=0.1` was not itself one of the sweep's explicit rows (which
tested 0.0, 0.01, 0.3, 0.8, 1.0, 1.5), but the sweep confirms `zeroed ==
floor(N*fraction)` exactly and monotonically across that entire range with no
discontinuities — so 0.1 is safely interpolated, and this script's own
re-verification (below) confirms the exact-count guarantee holds at 0.1 too.

### `noise_induced_shifts` (radar) — shift_std

| Severity | shift_std | Sweep row |
|---|---|---|
| low | 0.01 | R2 `shift_std=0.01` → mean_disp=0.0154 |
| medium | 1.0 | R2 `shift_std=1.0` → mean_disp=1.5417 |
| high | 5.0 | R2 `shift_std=5.0` → mean_disp=7.7084 |

### `gaussian_noise` (lidar) — sigma_xy / sigma_z

| Severity | sigma_xy | sigma_z | Sweep row |
|---|---|---|---|
| low | 0.01 | 0.01 | L2 `sigma=0.01` → observed_std=0.0095 |
| medium | 0.5 | 0.2 | existing v2 default (not a swept row itself, but sigma_xy=0.5 falls inside the swept 0.1–1.0 monotonic range) |
| high | 1.0 | 1.0 | L2 `sigma=1.0` → observed_std=0.9514 |

### `gaussian_noise` (camera) — sigma (pixel-space, 0–255)

| Severity | sigma | Sweep row |
|---|---|---|
| low | 1.0 | C2 `sigma=1.0` → observed_std_pixel≈1.00 |
| medium | 40.0 | existing v2 default (between swept 10.0 and 50.0) |
| high | 50.0 | C2 `sigma=50.0` → observed_std_pixel≈49.85 |

### `frame_deletion` (radar / lidar / camera) — random-mode p

| Severity | p | Sweep row |
|---|---|---|
| low | 0.1 | R1/L1/C1 `p=0.1` |
| medium | 0.5 | R1/L1/C1 `p=0.5` |
| high | 0.9 | R1/L1/C1 `p=0.9` |

**Design choice and why (per task instructions, justify explicitly):**
`frame_deletion` is a genuinely **binary** per-frame effect — a frame is
either fully present or fully absent, with no fractional/partial state in
between. Two designs were considered:

1. **Interval-based determinism** (`interval=N`, delete when `frame_index %
   N == 0`). Rejected: this script (like v1/v2) renders one synthetic frame
   per call with a hardcoded `idx=0` (so that deterministic `index_list=[0]`
   keeps working, matching v1/v2's established convention). Since `0 % N ==
   0` for *every* `N`, interval mode would fire on **every** severity level
   for this single-frame setup — giving three visually identical "always
   deleted" images, not a low/medium/high distinction. Interval mode only
   produces a rate difference across a real multi-frame *sequence*, which
   this single-frame-per-render script doesn't model.
2. **Random-mode p=0.1/0.5/0.9** (chosen). Each severity maps to the actual
   swept probability. The tradeoff: a single Bernoulli draw is a coin flip,
   so `p=0.9` firing (or `p=0.1` not firing) is not *guaranteed* on any one
   frame — a "wrong-side" draw (10% chance for `p=0.9`) is statistically
   real, not a bug (v2's own `frame_deletion_random` spot-check documented
   exactly this kind of outcome as expected). To keep the low/medium/high
   comparison visually monotonic and not misleadingly "flip" the sequence's
   apparent severity, **low and high search up to 25 alternate seeds** (via
   `_draw_frame_deletion` in the v3 script) to land on the statistically
   expected outcome (not-fired for low, fired for high); **medium (p=0.5) is
   left as the first draw with no preference**, since 50/50 genuinely has no
   "expected" side to search for. The realized outcome for every
   (modality, frame, severity) triple is logged verbatim in
   `frame_deletion_severity_log.md`, so nothing is silently hidden — see
   the log excerpt below.

**Bug caught and fixed during this task:** the first version of the seed
search used `tensor.std() < 1e-3` to detect whether camera `frame_deletion`
had fired. This was wrong: `noise_injection._zero_camera_tensor` produces a
per-channel-constant "black" tensor, but the three channels map to three
*different* normalized constants (R≈-2.12, G≈-2.04, B≈-1.80, from
ImageNet mean/std), so the fired tensor's global std is a fixed **≈0.1327**,
not ≈0. The threshold check never matched fired frames, so the seed search
for camera `high` (p=0.9) silently exhausted all 25 attempts and reported
"not fired" on every one of the 3 frames — a real detection bug, not a
probability artifact (the true fire probability at p=0.9 is 90%, not
0%). Fixed by comparing against the known exact zero-tensor per-channel
means/std instead of a std threshold; re-verified afterward — camera `high`
now fires on attempt 1 for 2/3 frames and attempt 2 for the third, matching
the expected ~90% single-draw fire rate.

Realized per-frame outcomes (from `frame_deletion_severity_log.md`, after
the fix):

| Modality | Frame | low fired? | medium fired? | high fired? |
|---|---|---|---|---|
| radar | seq001_rdr033 | False | False | True |
| radar | seq021_rdr015 | False | False | True |
| radar | seq048_rdr035 | False | True | True |
| lidar | seq001_rdr033 | False | True | True |
| lidar | seq021_rdr015 | False | False | True |
| lidar | seq048_rdr035 | False | True | True |
| camera | seq001_rdr033 | False | True | True |
| camera | seq021_rdr015 | False | True | True |
| camera | seq048_rdr035 | False | True | True |

`low` never fires (9/9) and `high` always fires (9/9) as designed; `medium`
splits 6/9 fired — consistent with p=0.5 being a genuine coin flip, not
biased toward either outcome.

### `loss_complete` — no severity axis (rendered once per frame)

Per `noise-injection-param-sweep-report.md` R4/L4/C4: `loss_complete` always
performs a full clear regardless of any params passed (`{}`,
`{'fraction': 0.01}`, `{'fraction': 0.5}`, `{'anything': 'ignored'}` — all
produce identical full-blackout output). There is no parameter that changes
its severity, so rendering three copies of the same image would misleadingly
imply a severity axis exists. Rendered exactly once per frame per modality,
labeled `"loss_complete (N/A - always full clear)"` in-image and tagged
`N/A - no severity axis` in the index.

## Verification: loss_partial zero-out scaling across severities (task 2)

Re-ran `radar_loss_partial`/`lidar_loss_partial` directly (independent of the
render script) against `seq021_rdr015`'s real point counts (radar N=150000,
lidar N=73569) at all three severity fractions:

| Severity | fraction | Radar zeroed | Radar expected | Lidar zeroed | Lidar expected |
|---|---|---|---|---|---|
| low | 0.1 | 15000 | 15000 | 7356 | 7356 |
| medium | 0.3 | 45000 | 45000 | 22070 | 22070 |
| high | 0.8 | 120000 | 120000 | 58855 | 58855 |

Exact `floor(N*fraction)` match at every severity, for both modalities —
confirms the sweep's exact-count guarantee holds at the new severity
fractions, not just the sweep's own tested points.

**Zoomed origin inset legibility at high severity:** inspected
`radar_loss_partial_high.png` for `seq021_rdr015` (120000/150000 = 80%
zeroed). The ±3m origin inset remains legible — individual magenta markers
are still visually distinguishable from each other in the inset even at this
density, because the inset only ever contains as many points as fall within
±3m of the sensor origin (a small fixed subset of the full N), not the full
zeroed count. No inset overcrowding/occlusion observed at any tested
severity.

## Perceptibility check, per effect (task 6)

Numerically-correct-but-visually-subtle is flagged explicitly per the task's
request — this is separate from (and does not contradict) the param sweep's
already-confirmed numerical correctness.

| Effect | Modality | Perceptible low→high? | Note |
|---|---|---|---|
| `loss_partial` | camera | **Yes, strongly** | Clean → light grain (low) → dense speckle (medium) → near-total blackout (high). Clearest progression of any effect. |
| `loss_partial` | radar/lidar | **Partially — flag** | The exact zeroed-count and inset-marker density scale correctly and are confirmed numerically, but in the **main full-scene view** all zeroed points collapse to the *same* origin pixel regardless of how many there are, so the magenta marker's on-screen size is visually near-identical across low/medium/high — severity is only clearly conveyed by the legend text and the zoomed inset's marker density, not by the main plot's silhouette. This is an inherent limit of collapsing all zeroed rows to a single point, not a rendering bug (the zero-out-aware render was specifically built to make the corruption visible *at all*, per the original zeroout diagnostic — it wasn't designed to make severity differences visible in the main view too). |
| `noise_induced_shifts` | radar | **Yes, strongly** | low (shift_std=0.01) preserves sharp object/return silhouettes; high (shift_std=5.0) diffuses them into blurred near-uniform circular point clouds. Clear monotonic spread. |
| `gaussian_noise` | lidar | **No — flag** | At the tested sigma_xy range (0.01 → 1.0 m), the displacement is small relative to the point cloud's own natural spatial extent and the BEV plot's auto-scaled axis range (which spans hundreds of meters when far-range returns are present). Low and high renders look nearly identical at this zoom level; the corruption is real (confirmed numerically in the param sweep — observed_std tracks sigma almost exactly) but not visually obvious without zooming into a small sub-region. |
| `gaussian_noise` | camera | **Yes, strongly** | low (sigma=1.0) is visually near-clean; high (sigma=50.0) shows obvious dense film-grain noise across the frame. Clear progression. |
| `frame_deletion` | radar/lidar/camera | **Yes, where it fires — binary by nature** | Not a "subtle vs strong" question — each severity either shows the full clean frame or full NO DATA/blackout; see the frame_deletion-specific caveats above about it being a probability axis, not a continuous-strength axis. |

## Updated index

`index.html` restructured per effect from v2's flat 6-column grid to a
3-column (low | medium | high) grid per severity-capable effect, with
`loss_complete` shown as a single reference image per modality (labeled
`N/A - no severity axis`) rather than a 3-column row. `clean` reference
carried over from v2, shown once per modality. The `FIXED RENDER` badge is
retained on radar/lidar `loss_partial` to flag the zero-out-aware rendering.

## Not touched

`noise_injection.py`, training code paths, `visualize_effects.py`,
`visualize_effects_v2.py`, `diagnose_loss_partial_zeroout.py`. Only new file:
`visualize_effects_v3_severity.py`.
