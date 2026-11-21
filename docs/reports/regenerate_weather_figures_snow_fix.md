# Standalone task: regenerate weather figures with corrected snow labels

## Context (self-contained — no prior conversation needed)

K-Radar's official per-sequence weather taxonomy (paper's Table 5, and confirmed
verbatim in `repos/K-Radar/tools/tag_generator/tag_generation.py` /
`repos/K-Radar/scripts/main_fusion_eval_0.py`) includes `lightsnow` and `heavysnow`
as raw weather tokens for sequences:

- `lightsnow`: 42, 43, 48, 49
- `heavysnow`: 46, 47, 54, 55, 56, 57, 58

Two allowlists in this repo were missing those exact tokens and silently fell back
to `"normal"` for any sequence carrying them:

- `repos/K-Radar/scripts/alvis/ingest.py` (`_ALLOWED_WEATHER`, ~line 57)
- `test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py`
  (`ALLOWED_WEATHER` / `WEATHER_LABELS`, ~line 59/172)

**Both have already been fixed** (both sets now include `"lightsnow"`,
`"heavysnow"`). This means all 11 of the above sequences were pooled into the
`normal` weather bucket in every existing output, contaminating every
per-weather AP figure/table derived from it — most materially, Bus or Truck's
baseline BEV AP in "Normal" weather: **70.98 (contaminated) → 57.43 (correct)**,
a 13.55-point difference. Sedan barely moves (77.21 → 76.93).

The dataset itself is not available locally to re-run `ingest.py` end-to-end
(compute cluster access for this project is permanently gone). Instead, a
weather-corrected copy of the row-level table was already produced by relabeling
by sequence ID (bypassing re-ingestion, since only the `weather` column needs
fixing):

```
repos/K-Radar/outputs/robustness_reports/row_table_iou03_weather_corrected.parquet
```

This file is row-identical to `row_table_iou03.parquet` (1,109,616 rows, 29
columns) except `weather` is corrected via:

```python
LIGHT_SNOW = ["42", "43", "48", "49"]
HEAVY_SNOW = ["46", "47", "54", "55", "56", "57", "58"]
# else: keep existing weather value unchanged
```

Verified AP (via `repos/K-Radar/scripts/alvis/ap_metrics.py:compute_ap`,
`condition == "original"`):

| Class | Normal | Overcast | Fog | Rain | Sleet | LightSnow | HeavySnow |
|---|---|---|---|---|---|---|---|
| Sedan | 76.93 | 89.40 | 94.91 | 69.13 | 76.10 | 90.78 | 66.20 |
| Bus or Truck | 57.43 | 81.67 | N/A | 7.89 | 63.18 | 94.46 | 87.53 |

N_gt-backing sequence counts: Normal 19, Overcast 2, Fog 6, Rain 8, Sleet 12,
LightSnow 4, HeavySnow 7 (sums to 58). Overcast (n=2) and LightSnow (n=4) rest on
very few sequences — flag as low-confidence in any figure/caption, same caution
the thesis already applies to other thin categories.

## Task

Regenerate every figure in `docs/Latex_Report/thesis_report/` that depends on the
per-weather baseline AP or per-weather corruption robustness, using the
corrected weather labels. **Do not edit any `.tex` file or any prose** — the
user is fixing all text and numbers by hand. Your job ends at: (a) regenerated
images in place, (b) a checklist (final section below) telling the user exactly
where in the `.tex` sources the numbers now disagree with the regenerated
figures, so they know what to go fix themselves.

### Step 1 — also correct `full_denormalized_table_22cond.parquet`

`docs/crossproduct_figures/generate_corruption_radar.py` reads
`repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond.parquet`
(NOT `row_table_iou03.parquet`), so the same sequence-based weather relabel
needs applying to that file too before that figure can be regenerated. Same
mapping as above, write a new file (do not overwrite the original), e.g.
`full_denormalized_table_22cond_weather_corrected.parquet`.

### Step 2 — regenerate `baseline_ap_coxcomb_weather.png`

Source: `docs/crossproduct_figures/generate_baseline_ap_coxcomb.py`. Its
`AXES["weather"]` dict (~line 32) is hardcoded, not read live from any parquet —
edit it directly:

```python
"weather": ("baseline_ap_coxcomb_weather",
            ["Normal", "Rain", "Overcast", "Sleet", "Fog", "LightSnow", "HeavySnow"],
            {"sed": {"Normal": (76.93, 15988), "Rain": (69.13, 5978), "Overcast": (89.40, 1107),
                     "Sleet": (76.10, 1622), "Fog": (94.91, 1947),
                     "LightSnow": (90.78, <N_gt>), "HeavySnow": (66.20, <N_gt>)},
             "bus": {"Normal": (57.43, 2763), "Rain": (7.89, 120), "Overcast": (81.67, 151),
                     "Sleet": (63.18, 1132), "Fog": None,
                     "LightSnow": (94.46, <N_gt>), "HeavySnow": (87.53, <N_gt>)}}),
```

`<N_gt>` placeholders: pull exact ground-truth counts for LightSnow/HeavySnow
per class from `row_table_iou03_weather_corrected.parquet`
(`is_tp.sum() + is_fn.sum()`, filtered to `condition == "original"`, per class,
per corrected weather) — not yet computed in this task's context, compute
before editing. Decide with the user whether to add LightSnow/HeavySnow as two
new wedges (recommended, since they're now real, non-trivial categories) or
keep the figure at 5 categories and only fix Normal's numbers — ask if unclear.

Also update `CATEGORY_PALETTE` in `docs/crossproduct_figures/palette.py` if 7
categories now exceeds its current color count for this axis.

Run: `uv run --project test-bed python docs/crossproduct_figures/generate_baseline_ap_coxcomb.py`

### Step 3 — regenerate `weather_corruption_radar_{sedan_part1,sedan_part2,bus}.png`

Source: `docs/crossproduct_figures/generate_corruption_radar.py`.

- Line ~78: `DATA = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond.parquet"` — point this at the Step-1 corrected file instead.
- Line ~77: `"weather": ("weather", ["normal", "rain", "overcast", "sleet", "fog"], ...)` — hardcoded stratum list omits snow entirely (unsurprising, since it was invisible before this fix). Add `"lightsnow"`, `"heavysnow"` if they should appear as their own radar polygons.
- Line 41: `N_FLOOR = 30` — this floors on GT count per cell, not sequence count. Given LightSnow/HeavySnow N_gt is in the thousands per the coxcomb data, both should clear this floor easily, but confirm the exact `bn`/`cn` values for the two new categories before trusting the panel isn't silently NaN'd out.

Run: `uv run --project test-bed python docs/crossproduct_figures/generate_corruption_radar.py`

### Step 4 — copy regenerated PNGs into the thesis figure directory

`docs/crossproduct_figures/*.png` and `docs/Latex_Report/thesis_report/figure/*.png`
are currently byte-identical copies (confirmed via md5sum), not symlinks — copy
each regenerated file over manually:

```bash
cp docs/crossproduct_figures/baseline_ap_coxcomb_weather.png docs/Latex_Report/thesis_report/figure/
cp docs/crossproduct_figures/weather_corruption_radar_sedan_part1.png docs/Latex_Report/thesis_report/figure/
cp docs/crossproduct_figures/weather_corruption_radar_sedan_part2.png docs/Latex_Report/thesis_report/figure/
cp docs/crossproduct_figures/weather_corruption_radar_bus.png docs/Latex_Report/thesis_report/figure/
```

### Step 5 — produce the number-change checklist (do not edit `.tex` files)

Recompute, from `row_table_iou03_weather_corrected.parquet` /
`full_denormalized_table_22cond_weather_corrected.parquet`, whatever exact
figures are needed to fill in the checklist below (per-class N_gt for
LightSnow/HeavySnow, per-class sequence count for corrected Normal, etc.), then
emit a checklist in this exact shape — one row per place in the `.tex` sources
where a number or claim now disagrees with the regenerated figures. Do not
guess at line numbers beyond what's listed here if the file has since changed;
re-grep for the quoted text first.

Known candidates to check (confirm exact current wording/line before listing,
`Results.tex` may have shifted since this doc was written):

- `Results.tex` ~line 61: `Weather & Normal & 18{,}959 & 4{,}440 \\` (N_gt table) — old contaminated N_gt vs. corrected (15,988 / 2,763); note whether LightSnow/HeavySnow rows should be added.
- `Results.tex` ~line 122 and ~line 126: prose citing "Normal (77.2)" and "the only large-sample, reliable weather category" — flag old value (77.2) and flag that the reliability claim itself may no longer hold once LightSnow (n=4)/HeavySnow (n=7) exist as visible categories.
- `Results.tex` ~line 284: "the normal-weather divergence rests on 29--30 sequences per class" — flag old sequence count vs. corrected count (report the actual corrected per-class number computed in this task, expect ~19).
- `Results.tex` ~line 479: repeats the same "Normal is the only large-sample, reliable category" claim as line 122 — flag same as above.
- `Discussion.tex` ~lines 218–260: stale, currently `%`-commented-out draft table/discussion citing the old contaminated numbers and an "unexplained +12.7 anomaly." Flag that this fix resolves the anomaly (rectified Bus/Truck-Normal gap vs. ASF's paper becomes −0.9, consistent with every other cell) — if this section is ever reinstated it needs full renumbering, not just a note.
- Any other `\includegraphics` caption or inline number in `Results.tex`/`Discussion.tex` referencing Normal-weather AP, N_gt, or sequence counts that a re-grep for `77.2`, `70.98`, `77.21`, `18,959`, `18959`, `4,440`, `4440`, `29--30`, or `12.7` turns up — list each with file:line and old vs. new value.

Explicitly out of scope, do not flag: `ASF.tex:34` and `ASF.tex:164` — those cite
ASF's own published paper numbers verbatim, unaffected by this repo's ingestion
bug.

Present the checklist as a plain markdown table: `File:line | Old text/number |
What it should become | Why`. That table is the deliverable for this step —
no `.tex` edits.

## List of all regenerated images (once this task is run)

| File | Generator |
|---|---|
| `docs/crossproduct_figures/baseline_ap_coxcomb_weather.png` | `generate_baseline_ap_coxcomb.py` |
| `docs/Latex_Report/thesis_report/figure/baseline_ap_coxcomb_weather.png` | copy of above |
| `docs/crossproduct_figures/weather_corruption_radar_sedan_part1.png` | `generate_corruption_radar.py` |
| `docs/Latex_Report/thesis_report/figure/weather_corruption_radar_sedan_part1.png` | copy of above |
| `docs/crossproduct_figures/weather_corruption_radar_sedan_part2.png` | `generate_corruption_radar.py` |
| `docs/Latex_Report/thesis_report/figure/weather_corruption_radar_sedan_part2.png` | copy of above |
| `docs/crossproduct_figures/weather_corruption_radar_bus.png` | `generate_corruption_radar.py` |
| `docs/Latex_Report/thesis_report/figure/weather_corruption_radar_bus.png` | copy of above |

No other figure in the live thesis (`Results.tex`, `Discussion.tex`, `ASF.tex`)
depends on the weather column — confirmed by grepping every `\includegraphics`
in `thesis_report/include/*.tex` for weather-related filenames; only the four
generators above produce the four figures actually `\includegraphics`'d.
`baseline_ap_coxcomb_{environment,density,distance,tod}.png` and
`weather_corruption_lines_*.svg` / `8b/8d/8e_*.svg` in `docs/crossproduct_figures/`
either don't depend on the `weather` column at all or aren't referenced by the
live thesis — out of scope for this fix.
