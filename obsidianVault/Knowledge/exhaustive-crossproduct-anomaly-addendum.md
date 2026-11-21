---
name: exhaustive-crossproduct-anomaly-addendum
description: Phase-1-style audit and resolved decisions for the peer-group anomaly-detection addendum (Q7 replacement) on full_denormalized_table.parquet
metadata:
  type: project
---

# Peer-group anomaly detection addendum — audit and decisions (2026-08-31)

Extends [[exhaustive-crossproduct-phase1-audit]] and
[[exhaustive-crossproduct-phase2-progress]]. The addendum reframes Q7: every
other deliverable in this analysis measures a cell against `original`
(baseline-relative); this measures a cell against its PEERS — the other
cells expected to behave alike (peer-relative). Distance from the peer
cluster is the signal, not distance from baseline.

## A1 — peer-group viability (N≥100 reliability floor)

| Peer group | Fix | Vary | Groups w/ ≥1 member | Median members | Groups meeting min-members |
|---|---|---|---|---|---|
| Sibling conditions | (cls, weather, tod) | condition (22) | 15/18 | 22.0 | 15/18 (83%) ≥4 |
| Sibling, modality-fixed | (modality, cls, weather, tod) | condition within modality | 60/72 | 7.0 | 45/72 (63%) ≥4 |
| Modality parity | (effect, severity, cls, weather, tod) | modality (3) | 120/144 | 3.0 | 103/144 (72%) all 3 |
| Severity ladder | (modality, effect, cls, weather, tod) | severity (3) | 149/180 | 3.0 | 89/180 (49%) all 3 |
| Stratum sweep | (condition, cls) | weather×env×dist×density×tod | 44/44 | 41.5 | 44/44 (100%) ≥4 |
| Cross-stratum, hold-all-but-tod | everything but tod | tod (2) | 1586/4971 | 1.0 | 255/4971 (5%) both |
| Cross-stratum, hold-all-but-weather | everything but weather | weather (5) | 1664/4699 | 1.0 | **0/4699 (0%)** ≥4 |

The last row was structurally dead as originally specified — weather,
environment, and time_of_day are fixed per-sequence (established in the
original Phase 1 audit), so pinning environment+distance+density+tod before
asking for weather variety collapses almost everything.

## A2 — frame_density binning (BLOCKING, resolved)

`n_objs` ranges 1–16 (mean 4.07), heavily right-skewed per-frame (5,773
frames at n_objs=1, single digits by n_objs≥12). **Decision: keep the
existing 3-bin `{1, 2-3, 4+}` scheme** (already used everywhere else in this
project, already gives 100% peer-group viability for stratum-sweep) rather
than move to quantile bins.

## A3 — natural dispersion baseline

Computed on sibling-conditions (15 groups, the only well-populated type at
audit time): median scaled-MAD ≈3.28 for AP, ≈0.019 for F1, ≈0.011 for mATE.
**Caveat, never fully resolved**: correlation between MAD and group size was
weak/inconsistent-sign at n=15 groups — too small a sample to confirm or
rule out the expected MAD-vs-N confound. Re-check if this becomes
load-bearing for interpreting any specific flag.

## A4 — CI-detectability (drove the gate decision)

Using precision/recall against sibling-conditions' typical MAD: **78% of
reliable precision cells and 52% of reliable recall cells have a CI wider
than 2x the group's typical natural spread** — meaning a CI-non-overlap
requirement would almost never fire regardless of whether a real deviation
exists, and doesn't exist at all as a criterion for F1/AP/error metrics (no
CI implemented for those).

## Resolved decisions

1. **Detection gate: SINGLE-GATE.** Robust z (|z|>3.5, Iglewicz & Hoaglin's
   conventional modified-z cutoff) is the actual filter. CI-overlap is
   computed and recorded (precision/recall only) but never filters — direct
   consequence of A4.
2. **`cross_stratum_weather` (A1.5b) redefined looser**: pools over
   frame_density too (fix condition+cls+environment+distance_bucket+tod,
   vary weather) rather than the original all-6-fixed spec. Empirically
   still caps at 3 co-occurring weather values even after loosening — never
   4 or 5 — so `min_members=3` for this group, documented as the real
   ceiling rather than an arbitrary relaxation.
3. **Severity ladder (49% viable) and cross-stratum-by-tod (5% viable) both
   run anyway**, exclusions reported via the coverage statement — maximal
   inclusion per the addendum's own convention, not silently narrowed.

## Structural finding not anticipated in the audit

`cross_stratum_tod` (2-member groups by construction) can **never** produce
a robust-z flag: with exactly 2 points, the median equals the mean and MAD
is symmetric around it, so z = ±1/1.4826 ≈ 0.674 for every possible pair of
values, always below any real threshold. This wasn't caught during A1/A4 —
it only surfaced when the scored output came back with zero flags across
every metric tested for this group. Its absence of flags is a property of
the math, not evidence of no anomaly; documented prominently in
`run_analysis.py`'s findings report rather than left to be misread as a
clean result.

## Implementation

See [[exhaustive-crossproduct-phase2-progress]]'s "Anomaly-addendum session"
section for what was built (`anomaly.py`, `detectors.py`,
`anomaly_plots.py`), the three real bugs caught during the build, and the
verified output (1,421 flags: 389 real / 1,032 small-N / 0 suspected-bug;
top flag is `bus+sleet+day+lidar_gaussian_noise_high` precision collapsing
to 0.50 against a 0.90 sibling-conditions peer median).
