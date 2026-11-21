# Session transfer: RR/mRR viz — open problem is density/reliability display

For the next agent picking this up. Read this before touching any script in
this directory — the open task is a design decision, not a bug fix.

## User's requirement (verbatim intent, not paraphrased away)

> "I need to show how dense the data / reliability of the data is and I am
> willing to switch away from heatmaps if required."

Primary ask: **one plot, intuitive, showing all information at once** —
the RR value AND the sample density (N) that backs it, in a single figure a
reader can parse without cross-referencing a second image or a legend
lookup. Heatmap is not a requirement, it's the current default that hasn't
solved this — chart type is genuinely open.

## Why the current heatmaps don't satisfy this

All 6 existing heatmaps (`rr_heatmap.png`, `mrr_heatmap.png`,
`mrr_heatmap_marginal.png`, `rr_heatmap_marginal.png`,
`rr_heatmap_sed.png`, `rr_heatmap_bus.png`) encode density as a **binary**
hatch overlay (reliable N≥30 vs. not) plus a row-drop threshold. That's a
pass/fail flag, not a density reading — a cell with N=31 and a cell with
N=3000 render identically (solid, no hatch). The user wants the actual
density visible, continuously, not thresholded away.

## Options already scoped with the user (not yet chosen)

Presented and left open — pick one or propose better, don't default back to
heatmap+hatch without asking:

1. **Continuous alpha by N** on the existing heatmap (`alpha =
   clip(N/N_ref, 0.15, 1)`, keep hatch only for hard N<30 floor). Cheapest
   change, stays a heatmap — likely does NOT fully satisfy "switch away if
   required," listed only as a floor option.
2. **Companion N heatmap**, same axes, separate figure/colormap. Exact info,
   but is explicitly the two-image cross-reference problem the user is
   trying to get away from.
3. **Text-annotated N in cell** — only viable on the 22-row marginal
   heatmaps, unreadable on the 106/160-row full-stratum ones.
4. **Split-triangle dual-channel cell** (color=RR, grayscale=N via Polygon
   patches instead of imshow) — one image, but nonstandard/harder to read
   without a worked example; higher implementation cost.
5. **Marker-size scatter instead of imshow** (dot color=RR, size=sqrt(N)) —
   reads well on the 22-row marginal data, likely too dense/overlapping on
   106+ rows × 21 columns.
6. **Discrete border-weight tiers for N** — coarse compromise, still
   heatmap, still not truly continuous.

None of these were built — this file exists specifically because the user
said "give me a session transfer" instead of picking one, likely wanting a
fresh perspective or explicit non-heatmap proposals (bubble chart? faceted
strip plot? dot-and-whisker with N-scaled marker + RR on y?) before
committing code.

## Concrete next step

Don't re-litigate the RR/mRR formula or reliability rule — those are settled
(see `heatmap_session_summary.md` in this directory, still accurate). The
open question is purely the **visual encoding of (RR, N) jointly**. Suggest
starting by asking the user: is the target audience the report (needs to be
self-explanatory at a glance, one legend) or continued personal analysis
(density of information > polish)? That answer should drive which of the 6
options — or a genuinely different chart family — gets built.

If proposing a non-heatmap alternative, the natural candidates given this
data's shape (RR per stratum/condition cell, N per cell, ~9-21 columns ×
22-160 rows depending on collapse level) are:
- **bubble/scatter grid**: x=condition, y=stratum (categorical), size=N,
  color=RR — literally option 5 above, formalized.
- **strip/dot plot per stratum row**: one row per stratum, dots along x for
  each condition, dot size=N, color=RR, y-jitter removed since rows are
  already categorical — same information as the heatmap, less rigid grid,
  size varies continuously so density reads as texture not just color.
- **small-multiple faceted bars**: one small bar-chart panel per stratum
  (or per marginal dimension value), bar height=RR, bar color/alpha=N-tier
  — trades "one plot" for "one coherent panel of plots," may or may not
  satisfy "in one plot."

## Files in this directory (context, unchanged by this transfer)

- `generate_rr_heatmap.py` / `.png` — full 106-stratum × 21-condition, RR not merged
- `generate_mrr_heatmap.py` / `.png` — full 106-stratum × 9-group, severities merged (mRR)
- `generate_mrr_heatmap_marginal.py` / `.png` — 22 marginal rows × 9 groups, mRR
- `generate_rr_heatmap_marginal.py` / `.png` — 22 marginal rows × 21 conditions, RR
- `generate_rr_heatmap_by_cls.py` → `rr_heatmap_sed.png`, `rr_heatmap_bus.png` — per-class, no cls-weighting
- `heatmap_session_summary.md` — formula, reliability rule, data caveats (still valid, read this too)
- `generate_plots.py` — older 6-figure set (severity lines, damage ranking, etc.), predates this RR work, unrelated axes/questions

All scripts share the verification-against-source-parquet convention
(`assert np.isclose(...)` + printed `verification OK` line) — carry that
forward on whatever gets built next.
