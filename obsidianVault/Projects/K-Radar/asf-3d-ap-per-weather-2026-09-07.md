# Per-weather 3D AP for the `original` baseline (2026-09-07)

Extends the pooled 3D AP already established in [[official-checkpoint-rerun-2026-08-26]]
(sedan 74.99, bus 58.15 at IoU 0.3) down to a per-weather breakdown, to sit alongside the
thesis's existing per-weather **BEV** table (`tab:baseline_distance_weather` in Results.tex)
and ASF's own published per-weather 3D AP. New script:
`repos/K-Radar/scripts/alvis/compute_3d_ap_per_weather.py`.

## Two real bugs found and fixed before the numbers could be trusted

1. **Dummy 2D bbox = zeros silently zeroed the whole eval.** `all_preds.txt`/`all_gts.txt`
   (via `ingest.py`'s `_parse_kitti_line`) never carried a 2D image bbox at all — only
   h/w/l/x/y/z/rotation_y. The first version of the adapter filled the required `bbox` field
   with `np.zeros((n,4))`, reasoning it was "unused by bev/3d metrics." It isn't used by the
   IoU math, but K-Radar's own `clean_data()` (`eval_revised.py`) computes
   `height = bbox[3]-bbox[1]` **before** any BEV/3D geometry is touched, and drops any
   object below `MIN_HEIGHT` (40/25/25px per difficulty). Zero height fails every tier, so
   every GT object and every detection got silently excluded — pooled AP came back as an
   exact `0.00` for both classes despite correct GT counts (29,613 sedan / 5,843 bus).
   Root-caused via `sudo env "PATH=$PATH" uvx py-spy dump --pid <pid>` (ptrace_scope=1
   blocked a plain attach) confirming it was genuinely inside `rotate_iou_cpu.py`'s
   Sutherland-Hodgman clip, not stuck — the *pooled* AP result was the tell, not a hang.
   **Fix:** synthetic non-zero placeholder bbox (`[0,0,100,200]`, height=200) for every row.
2. **Weather-per-sequence join silently defaulted everything to "normal."** The adapter
   originally called `ingest.py`'s `_sequence_metadata()`, which reads
   `data/<seq>/description.txt` from the raw K-Radar dataset. That raw dataset does not
   exist anywhere in this local checkout (`repos/K-Radar/data/` is empty, confirmed via
   filesystem-wide search) — it only ever lived on Alvis. `_parse_description_txt`'s
   missing-file fallback returns `{}`, and `_sequence_metadata` then defaults every
   sequence's weather to `"normal"` — so the first (bbox-fixed) run put all 13,727 frames
   in the `normal` bucket and reported `NO FRAMES` for overcast/fog/rain/sleet.
   **Fix:** pull the sequence→weather mapping from
   `outputs/robustness_reports/full_denormalized_table_22cond.parquet`'s own
   `sequence`/`weather` columns instead (already-verified data, computed back when Alvis
   access still existed) — confirmed 58/58 sequences map cleanly, one weather each, no
   conflicts, and the resulting frame-level distribution (8238/2206/1445/1424/414) matches
   Methods.tex's `tab:kradar_distribution` exactly before trusting the AP numbers.

## Validation

Every BEV-AP value the (fixed) script produced as a byproduct of computing 3D AP was
cross-checked against the thesis's already-verified per-weather BEV table and matched to two
decimals in every cell (including the bus/fog `N=0` → not-reported case) — strong evidence the
new 3D figures alongside them are correct, not just plausible-looking.

## Final table (IoU 0.3, `original`/baseline condition)

| Class | Total (pooled) | Normal | Overcast | Fog | Rain | Sleet |
|---|---|---|---|---|---|---|
| Sedan 3D AP | 74.99 | 74.46 | 82.41 | 92.28 | 66.36 | 70.59 |
| Sedan BEV AP | 77.86 | 77.21 | 89.40 | 94.91 | 69.13 | 76.10 |
| Bus/Truck 3D AP | 58.15 | 60.30 | 74.38 | N/A ($N{=}0$) | 7.89 | 59.84 |
| Bus/Truck BEV AP | 67.93 | 70.98 | 81.67 | N/A ($N<30$) | 7.89 | 63.18 |

GT counts (sedan/bus): normal 18959/4440, overcast 1107/151, fog 1947/0, rain 5978/120,
sleet 1622/1132.

## Runtime notes (not a data issue, but worth knowing for next time)

K-Radar's own rotated-BEV-IoU fallback (`rotate_iou_cpu.py`) is deliberately pure-Python/
unvectorized (its own docstring: the real numba/CUDA kernel segfaults on a driver mismatch),
so a pooled 13,727-frame pass took ~2.5–3h on this machine even before the per-weather splits
— largely worsened by concurrent system memory pressure (swap nearly full from unrelated
browser/app load) during one run; killing a few processes measurably helped. Budget for this
when re-running rather than assuming a "few minutes" estimate.
