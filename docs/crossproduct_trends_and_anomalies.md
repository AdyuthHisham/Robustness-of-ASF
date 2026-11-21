# Cross-Product Robustness Analysis — Trends & Anomalies

Synthesis document for the exhaustive cross-product analysis of
`repos/K-Radar/outputs/robustness_reports/full_denormalized_table.parquet`
(1,109,616 rows / 22-condition scope used here, 58 sequences).

> **Fully re-derived 2026-09-01** against `crossproduct_v2/`, following a second
> frame-key fix (see `docs/vAIlt/06_Results/exhaustive-crossproduct-frame-key-fix-20260901.md`)
> and correction of two silently-drifted pipeline constants: the reliability floor
> (`RELIABILITY_FLOOR`, had drifted from its documented value of 30 to 100 with no
> git history to explain it — reverted to 30) and the small-N soft ceiling
> (`SMALL_N_CEILING`, rescaled 300→90 to preserve the original 3x-floor ratio now
> that the floor itself is 30, not 100). Full detail:
> `docs/vAIlt/06_Results/crossproduct-rebuild-20260901.md`.
>
> **Every number below was re-pulled directly from `crossproduct_v2/`, not
> patched from the prior version.** Most of the underlying condition-level
> metrics (AP, F1, mATE/mASE/mAOE per condition) are effectively unchanged from
> the prior `crossproduct/` build — the frame-key/floor fixes mainly change
> *which cells are reliable* and *which peer-group members are eligible for
> comparison*, not the raw per-condition numbers. But several derived numbers
> **did move substantially, including a few that flip the specific claim (not
> just its magnitude)** — these are flagged explicitly inline as **CORRECTED**
> rather than silently overwritten, so a reader comparing against an older
> version of this doc can see exactly what changed and why.

Methodology, resolved blockers, and the Phase-1/addendum audits are in
`obsidianVault/Knowledge/exhaustive-crossproduct-phase1-audit.md` and
`obsidianVault/Knowledge/exhaustive-crossproduct-anomaly-addendum.md` — not
re-derived here.

---

## Section A: Trends & Anomalies

### A.1 The dominant, well-triangulated story: LiDAR Gaussian noise is catastrophic, non-gradual, and disproportionately worse in fog

Four independent methods converge on the same finding — **this headline is
unchanged**, only the exact supporting numbers moved:

1. **Severity monotonicity** (`figures/severity_monotonicity.png`): AP for
   `lidar_gaussian_noise` is a step function, not a gradient — low severity
   (68.4 AP) is nearly harmless relative to `original` (72.9), but medium
   (23.7) and high (21.6) both collapse to roughly the same catastrophic
   floor (`q2_ap_restricted_range_worst_condition.csv`). Unchanged to 2
   decimal places.
2. **Churn** (`q5_max_churn.csv`): `lidar_gaussian_noise_high` has the
   highest churn rate in the entire sweep, 60.9% (N=35,455 GT objects,
   pooled across classes — per-class churn not computed, see limitations).
   Unchanged — churn is computed from a cached matcher JSON the frame-key
   fix never touches.
3. **Peer-group robust-z — CORRECTED magnitudes, N unchanged**: in the
   (sedan, fog, day) peer group, `lidar_gaussian_noise_medium` and `_high`
   score AP 52.95 and 53.26 against a 22-condition peer median of 94.89 —
   robust z of **−1,222 and −1,213** (previously reported as −1,130/−1,122;
   the corrected reliability floor changed which peer members are eligible
   for the median/MAD baseline, shifting the exact z though not the
   conclusion), by far the two most extreme deviations in the whole dataset
   (N=1,979 and 1,963 rows, 6 sequences each — clears the sequence-confound
   check). The same pattern repeats independently in (sedan, sleet, day) at
   smaller magnitude — **z≈−129** (previously ≈−118), N=955–960, 5–6
   sequences — two different weather buckets, same two conditions breaking
   away, not a one-off.
4. **D4 interaction residual** (`figures/anomaly/d4_residual_heatmap_ap_restricted_range_sed.png`,
   median polish on condition×weather, fit quality **0.844**, confirmed
   unchanged): lidar-corruption residuals are **positive in fog** (e.g.
   `lidar_gaussian_noise_high`: +15.4, `_medium`: +13.3 — better than the
   additive condition-effect + weather-effect model predicts) and
   **negative in normal/overcast** (`_high`: −6.8/−5.5) — a real
   interaction, not just "fog is hard" and "lidar noise is bad" adding up
   independently. Caveat: D4 is a proxy for the compounding-vs-inherited-
   difficulty question, not the literal corrupted-minus-clean double-
   difference (out of scope for this read-and-synthesize pass, see
   limitations).

**Mechanism, from D5** (`d5_cross_metric_inconsistency.csv`, 7/7 flagged
cells match the "precision up while recall falls" pattern, concentrated in
`lidar_gaussian_noise_medium/high` — unchanged from prior build): the model
isn't uniformly worse at everything — it becomes more conservative,
predicting far fewer objects but staying relatively precise on the ones it
still calls (e.g. `lidar_gaussian_noise_high`+sed: recall delta −0.637,
precision delta +0.025, N=30,151 — unchanged, this cell was already
well above any floor). This is corroborated independently from the
baseline-relative side by Q1 (`q1_significant.csv`): 7 of 7
statistically-significant (CI-excluded) precision improvements under
corruption occur in exactly this condition family — the model suppressing
false positives while missing more true positives, not a genuine accuracy
gain.

### A.2 Corruption degrades mostly by missing detections, not by hallucinating

Across the sweep, FP rate stays flat or drops under heavy corruption
(`q3_fp_by_count.csv` vs. `q3_fp_by_rate.csv` — the two rankings diverge
sharply: `lidar_gaussian_noise_low`/sed has the highest raw FP count (376,
N=2,444, unchanged) but the highest FP *rate* cells are all rare-class `bus`
predictions at fp_rate=1.0. **CORRECTED**: previously reported at "N=130–140";
at the corrected N≥30 floor, smaller-N perfect-rate cells now clear the
reliability bar and dominate the top of the ranking — the actual range
backing the current top-15 `fp_rate=1.0` cells is **N=31–47** (e.g.
`original`+bus: N=31; `camera_gaussian_noise_low`+bus: N=33/35). This is a
real shift in what "the smallest reliable cell" means, not noise — a lower
floor mechanically surfaces smaller-N cells into the ranking. TP-only error
metrics do NOT "barely move" at the worst-AP conditions — mATE actually
rises meaningfully, from 0.326 at `original` to 0.466–0.485 at
`lidar_gaussian_noise_high/medium` (`summary_condition.parquet`, unchanged,
a ~43–49% relative increase), nowhere near AP's ~70% relative collapse but
not negligible either. The more striking finding, also unchanged, is that
**mASE and mAOE both *improve* (get lower) at those same worst-AP
conditions** — mASE 0.239→0.203, mAOE 0.207→0.137 at
`lidar_gaussian_noise_high` — the opposite of what "everything gets worse
under corruption" would predict. This is consistent with A.1's
FP-suppression mechanism: if the surviving true positives under heavy
corruption are disproportionately the easy, confident, well-aligned
detections (the ones the model doesn't give up on), their better-than-average
box/orientation accuracy would show up exactly as a selection-effect
improvement in mASE/mAOE, not as evidence that corruption improves
localization.

### A.3 Modality importance for total sensor loss: camera-invisible, lidar-critical

`q6_zero_ablation_rank.csv`: `camera_loss_complete_zero` retains 98.8% of
baseline AP (mean_f1_delta −0.010, **N=16 reliable cells**, previously N=15
— one more cell cleared the floor, metric values unchanged to 3 decimals) —
camera loss is nearly invisible to this fused model. `radar_loss_complete_zero`
retains 89.8% (N=17, previously 15). `lidar_loss_complete_zero` retains only
50.0% (mean_f1_delta −0.264, N=16, previously 15) — catastrophic. **Caveat
carried in every output**: zeroing a BEV branch is off-distribution for a
model never trained with modality dropout — conv biases and BatchNorm map
zeros to nonzero constants, not "no signal." Frame this as retention relative
to the full-sensor baseline, not unqualified sensor-failure robustness.

### A.4 Suspicious recovery — flagged, not celebrated

13 of 21 corrupted conditions show `corruption_induced_recovery_rate ≥
corruption_induced_miss_rate` (`q5_suspicious_recovery.csv`, count
unchanged). The most extreme: `lidar_loss_partial_high` (miss rate 8.9%,
recovery rate 15.5%, unchanged) — more GT objects flip from
missed-in-clean to detected-in-corrupted than the reverse. Per the task's own
framing, high recovery is a red flag for a matching/pipeline artifact or a
genuinely bizarre model interaction, not evidence the model gets *better*
under corruption — not investigated further this pass.

### A.5 Modality-ordering flips (D3) — CORRECTED: 209 cases (was 187), still diffuse rather than singular

`d3_modality_divergence.csv`: in most (effect, severity, class, weather,
tod) combinations the camera/lidar/radar ranking is stable, but it inverts
**209 times** across the three metrics tested (precision 86, AP 63, recall
60 — previously 187 total: precision 77, recall 54, AP 56). The corrected
floor admits more peer-group comparisons, surfacing more flip instances; the
qualitative claim — diffuse flips across many strata, not a singular
reordering — still holds; direction/magnitude of the increase is consistent
with more cells overall clearing the reliability floor.

### A.6 What did NOT show up, and why that itself is informative

- **D2 (flat-except-one) found zero qualifying groups.** Unchanged. No case
  exists in this dataset of an otherwise-tight, consistent peer group with a
  single cell breaking away — every real anomaly instead comes from groups
  that were already scattered.
- **CORRECTED — anomaly counts, same peer-group-type story**: after applying
  the sequence-confound and small-N checks, **438 "real" anomalies** (was
  348) come from the same **2 of the 6 peer-group types**:
  `sibling_conditions` (352, was 310) and `stratum_sweep` (86, was 38) —
  `modality_parity`, `severity_ladder`, `cross_stratum_tod`, and
  `cross_stratum_weather` still produce **zero** robust "real" findings. The
  count increase reflects the corrected N≥30 floor (more cells clear the bar
  → more comparisons scored) and the corrected N≥90 small-N ceiling (fewer
  clearing cells get the soft artifact caveat, so more graduate to "real") —
  the qualitative pattern (only these 2 peer-group types ever produce robust
  findings) is unchanged.
- **`cross_stratum_tod` cannot ever flag anything, structurally** (2-member
  groups: median=mean, MAD is symmetric, so robust z is mathematically a
  constant ≈0.674 regardless of the data). Unchanged, still true regardless
  of floor.
- **New this pass**: 2 `suspected_bug` anomaly flags (0 previously, since
  they only surface with the corrected N≥30 floor). Both root-caused to a
  single-sequence `lidar_gaussian_noise_{low,high}` × sleet × precision=1.0
  cell where a sequence's only two baseline FPs (low-confidence, boundary-
  distance) vanish under noise — a real, mechanistically explained value
  that happens to rest on n_sequences=1. Not a data bug; flagged for
  completeness since the pipeline's own classifier labels near-perfect
  scores `suspected_bug` unconditionally regardless of cause (a deliberate
  design choice, not a defect — see
  `docs/vAIlt/06_Results/crossproduct-rebuild-20260901.md`).

---

## Section B: Answers to the 7 Questions

### B.1 Sensor robustness

**This measures fused-model degradation under single-modality corruption,
not raw per-sensor detection accuracy** — no `primary_sensor`-attributed
ground truth exists in this table to isolate a sensor's standalone
performance. With that framing: LiDAR corruption is by far the most
damaging (AP retention as low as **0.296** at `gaussian_noise_high`,
unchanged, ranging up to slightly above 1.0 at the mildest severities — see
B.3 for why a retention >1.0 is not a genuine improvement), radar corruption
is moderate (AP retention **0.741–1.001**, unchanged), camera corruption is
the mildest — **CORRECTED range: 0.976–0.981** (previously reported as
0.964–0.980; the wider, lower-bound-0.964 range does not match any measured
camera-condition value in the current or prior build — likely a stale
citation carried forward from an earlier draft; the corrected, directly-
measured range is narrower and higher) — no camera condition appears in the
worst-10 list at all. Total-loss ranking (Q6/A.3) confirms the same
ordering: lidar >> radar > camera in importance to this fused detector.

### B.2 Condition impact (severity/effect ranking)

Worst-to-best by AP (`q2_ap_restricted_range_worst_condition.csv`, values
unchanged to 2 decimal places): `lidar_gaussian_noise_high` (21.6) <
`_medium` (23.7) < `lidar_loss_complete_zero` (42.2) <
`radar_gaussian_noise_high` (54.0) < `radar_gaussian_noise_medium` (61.8) <
`radar_loss_partial_high` (64.3) < `radar_loss_complete_zero` (66.8) <
`lidar_loss_partial_high` (67.9) < `lidar_gaussian_noise_low` (68.4) <
`camera_gaussian_noise_high` (71.2, first camera condition to appear).
`gaussian_noise` is the most damaging effect family at high severity;
`loss_partial` is consistently milder than `gaussian_noise` at matched
severity for the same modality.

### B.3 Where corruption beats baseline

41 statistically-significant improvements found (`q1_significant.csv`,
unchanged count and values), **5** within-noise (`q1_noise.csv`, was 6).
Breaking down the 41 by metric — **unchanged**: 7 precision, 2 recall (both
CI-excluded, the rigorous standard), plus 10 mATE / 8 mASE / 6 mAOE / 4 F1 /
4 AP (weaker "both cells reliable" bar, not CI-based — see `ci_based`
column). **None of these represent a genuine detector improvement.** Every
precision improvement is explained by A.1's mechanism (FP suppression via
reduced recall, confirmed independently by D5) — see the `mechanism_note`
column in `q1_significant.csv` for the per-row diagnostic.

### B.4 FP / FN patterns — CORRECTED: sequence-confound share dropped from 60% to 33%

FP count and FP rate rankings diverge sharply (A.2): raw count is dominated
by high-N common cells, rate is dominated by rare `bus`-class cells with
fp_rate=1.0. **The most extreme FP/FN joint offenders list changed
substantially, not just its confound fraction**:
`q4_joint_worst_offenders.csv` (still 15 rows) is now dominated by
`camera_gaussian_noise_*`/`camera_loss_partial_*` + bus + normal weather
cells (fp_rate=1.0, fn_rate=1.0, N=33–47, 8–9 sequences, not
sequence-confounded) — these did not appear in the top-15 under the old
N≥100 floor because their N (33–47) was below that bar. **5 of 15 (33%)**
carry `sequence_confound_risk=true` (previously "9 of 15 (60%)") — a real
drop, not floor noise: the corrected floor lets genuinely well-backed
(8–9-sequence) cells into the ranking, displacing some of the
single/double-sequence rows that dominated the old, stricter-floor list.
Only the `weather=normal` rows (4+ sequences backing them) and the
non-confounded `sleet`/`bus` rows should be read as generalizable; the 5
flagged rows (mostly `lidar_gaussian_noise_*` + sleet or single-sequence
normal) are single/double-sequence anecdotes that happen to clear the
row-count reliability floor.

### B.5 Weather / time-of-day / environment robustness

**N_rows/N_sequences caveat (load-bearing for every claim in this
subsection, unchanged — these counts are per-sequence properties,
independent of the reliability floor)**: weather, environment, and
time_of_day are fixed properties *per sequence*, confirmed across all 58
sequences. Sequence counts: weather — normal=30, sleet=12, rain=8, fog=6,
overcast=2; environment — urban=18, highway=16, countryside=7, mountain=6,
alleyway=3, university=3, parkinglots=3, shoulder=2; time_of_day — day=35,
night=23. **`fog` and `overcast` weather, and every environment other than
urban/highway/countryside/mountain, generalize from single digits of
sequences.** Any row-count-based "reliable" tag in these strata (**N≥30**
rows, corrected from an erroneous N≥100 this session found in the code) does
not imply independent evidence at the level the row count suggests — a cell
can clear N≥30 rows while resting on 1 sequence (see B.4, and
`sequence_confound_risk` column).

**CORRECTED — the worst-weather claim itself changed, not just its
magnitude.** The retention heatmap (`figures/retention_heatmap_condition_weather.png`)
and the underlying per-condition per-weather deltas (recomputed directly
from `summary_cond_cls_weather.parquet`, sed class) show, for
`lidar_gaussian_noise_high`: retention 0.143 (normal) < 0.164 (rain) < 0.292
(overcast) < 0.401 (sleet) < 0.561 (fog). **`normal` weather is now the
numerically worst bucket, narrowly below `rain`** (0.143 vs. 0.164) —
previously this document claimed `rain` was worst (retention 0.08–0.29) with
`sleet` second-worst (0.23–0.42); those specific ranges don't match any
directly-measured value in either the prior or corrected build and were
likely computed at a different marginalization level (possibly pooled over
both classes or restricted to a narrower stratum) that wasn't re-derivable
from the files checked this pass. What *does* hold, confirmed directly: fog
is consistently the mildest weather for LiDAR-noise conditions (retention
0.56–0.87 across `lidar_gaussian_noise_high/medium`/`lidar_loss_complete_zero`),
consistent with A.1's D4 finding of a genuine positive fog interaction
residual. `radar_gaussian_noise_high` shows the same fog-is-mildest,
sleet-is-worst pattern more cleanly (retention 0.85 in fog down to 0.60 in
sleet) — radar's ordering did not flip. Camera stays closest to
weather-uniform (`camera_gaussian_noise_high`: 0.965–1.000 across all five
weather buckets, essentially unchanged from the prior 0.92–1.00 claim's
upper end, though the corrected lower bound is 0.965 not 0.92). Time-of-day
parity could not be tested for anomalies at all (A.6 — `cross_stratum_tod`'s
2-member groups are mathematically undetectable); no claim is made about
day/night robustness beyond what the baseline-relative deltas show.

### B.6 Distance / density robustness — CORRECTED on both sub-claims

Both distance_bucket and frame_density are **not** fixed per sequence (they
vary within a sequence, frame to frame) — the sequence-confound caveat above
does not apply here in the same way; N_rows is a much better proxy for
independent evidence in this subsection.

- **Distance** (`summary_full.parquet`, `original` vs.
  `lidar_gaussian_noise_high`, pooled over class — **baseline AP values
  themselves differ from the prior citation**, likely because that citation
  was computed at a narrower stratum than the pooled full-grain numbers
  re-derived here): baseline AP is near_0_20=55.4, mid_20_40=54.9,
  far_40_60=48.7, very_far_60_75=41.8 (N=10,618–12,760 per bucket).
  Under `lidar_gaussian_noise_high`: near_0_20→11.0 (80.1% relative drop),
  mid_20_40→17.5 (68.1% drop), far_40_60→12.5 (74.3% drop),
  very_far_60_75→7.7 (81.7% drop). **The largest relative drop is now at
  very-far range (81.7%), narrowly ahead of near-field (80.1%)** — both are
  clearly hit harder than the mid/far-mid buckets (68–74%). This
  partially, not fully, confirms the prior claim that "corruption hurts
  close-range detection disproportionately" — near-field is indeed hit hard,
  but very-far range is hit at least as hard, which the prior version of
  this document did not report (it only contrasted near vs. far, omitting
  very_far entirely from the comparison).
- **Density** (`summary_full_density.parquet`, pooled over class):
  baseline AP is **not monotonically decreasing with density** as the prior
  version claimed — density=1: 42.9, density=2-3: **58.5 (highest)**,
  density=4+: 41.2 (N=7,001–21,014). Under `lidar_gaussian_noise_high`:
  14.0→16.1→5.2 across the same bins. Relative AP loss: 67.4% at density=1,
  72.5% at density=2-3, **87.5% at density=4+** — the densest-scene bucket is
  still by far the most fragile to this corruption in relative terms
  (consistent with the prior claim's direction), but the baseline-difficulty
  story (busier scenes intrinsically harder) does **not** hold in the
  pooled numbers — density=2-3 is the easiest baseline bucket, not the
  hardest. This may be a genuine non-monotonicity in the data (e.g.
  interacting with which weather/environment combinations happen to produce
  each density bin) rather than an error — not investigated further this
  pass; flagged as a correction to the prior "monotonic baseline
  degradation" claim, not confirmed as either right or wrong beyond what's
  directly measured here.

### B.7 Churn

Highest: `lidar_gaussian_noise_high` at 60.9% (35,455 GT objects, pooled
across classes, unchanged). Lowest: `radar_loss_partial_low` at **1.05%**
(`q5_min_churn.csv`, previously reported as 1.1% — same condition, same
order of magnitude, decimal-level difference only) — consistent with A.2's
finding that low-severity conditions are nearly harmless. Churn ranking
matches the AP-based condition-impact ranking (B.2) independently — two
different measurement approaches (detection-outcome flips vs. aggregate AP)
agree on which conditions are damaging. Suspicious-recovery flag (A.4)
applies to 13/21 conditions, unchanged; treat any "condition X improves
detection of some objects" claim with skepticism rather than as a robustness
finding.

### B.8 Per-class best/worst sensor and condition (new question, added 2026-09-01)

For each class, across all 21 corrupted conditions at `reliable` cells (N≥30,
`summary_cond_cls.parquet`), which condition/modality gives the highest and
lowest value per metric. **Primary metric is AP (restricted-range)**, matching
this document's convention elsewhere; other metrics reported for completeness
with the same caveat A.2 already established: mASE/mAOE "improving" under heavy
corruption is a survivorship artifact (the surviving TPs are the easiest,
best-aligned detections), not evidence corruption improves localization — do
not read the mASE/mAOE "best" rows below as a robustness finding.

**Sedan (sed)**:

| Metric | Best condition (modality) | Best value | Worst condition (modality) | Worst value |
|---|---|---|---|---|
| AP (restricted-range) | `lidar_loss_partial_medium` (lidar) | 78.19 | `lidar_gaussian_noise_high` (lidar) | 16.06 |
| F1 | `lidar_loss_partial_medium` (lidar) | 0.829 | `lidar_gaussian_noise_high` (lidar) | 0.242 |
| Precision | `radar_gaussian_noise_high` (radar) | 0.919 | `lidar_loss_complete_zero` (lidar) | 0.829 |
| Recall | `lidar_loss_partial_medium` (lidar) | 0.795 | `lidar_gaussian_noise_high` (lidar) | 0.140 |
| mATE (lower better) | `radar_loss_complete_zero` (radar) | 0.265 | `lidar_gaussian_noise_medium` (lidar) | 0.396 |
| mASE (lower better)† | `lidar_gaussian_noise_high` (lidar) | 0.189 | `camera_gaussian_noise_high` (camera) | 0.262 |
| mAOE (lower better)† | `lidar_gaussian_noise_high` (lidar) | 0.177 | `radar_loss_complete_zero` (radar) | 0.231 |

**Bus (bus)**:

| Metric | Best condition (modality) | Best value | Worst condition (modality) | Worst value |
|---|---|---|---|---|
| AP (restricted-range) | `radar_gaussian_noise_low` (radar) | 68.12 | `lidar_gaussian_noise_high` (lidar) | 27.07 |
| F1 | `lidar_loss_partial_medium` (lidar) | 0.752 | `lidar_gaussian_noise_high` (lidar) | 0.388 |
| Precision | `lidar_gaussian_noise_medium` (lidar) | 0.830 | `radar_gaussian_noise_medium` (radar) | 0.665 |
| Recall | `camera_loss_complete_zero` (camera) | 0.719 | `lidar_gaussian_noise_high` (lidar) | 0.253 |
| mATE (lower better) | `radar_loss_complete_zero` (radar) | 0.556 | `lidar_gaussian_noise_medium` (lidar) | 0.717 |
| mASE (lower better)† | `lidar_gaussian_noise_medium` (lidar) | 0.233 | `radar_gaussian_noise_medium` (radar) | 0.275 |
| mAOE (lower better)† | `lidar_gaussian_noise_high` (lidar) | 0.025 | `radar_gaussian_noise_high` (radar) | 0.195 |

† mASE/mAOE "best" landing on `lidar_gaussian_noise_high/medium` — the same
conditions that are AP/F1/recall's *worst* — is exactly the survivorship
selection effect from A.2: heavy lidar noise kills most detections, and the
handful that survive happen to be well-aligned ones. Not a genuine robustness
result.

**Consistent with A.1/A.2/B.1/B.2 throughout**: `lidar_gaussian_noise_high` is
the worst condition on every accuracy metric (AP, F1, recall) for **both**
classes — the single dominant failure mode in this dataset holds at the
per-class level, not just pooled. On the "best" side, no single condition wins
across every metric; `lidar_loss_partial_medium` is the best AP/F1 condition for
both classes (mild corruption, lidar is otherwise the most informative
modality when it isn't being corrupted heavily), while radar and camera
conditions occasionally edge out precision/recall on individual metrics.
All cells above are N=6,147–33,434 (well above the N≥30 floor and the N≥90
small-N ceiling); none carry a sequence-confound flag in `summary_cond_cls.parquet`'s
own reliability tagging beyond the row-count floor already applied.

---

## Limitations

- **Restricted-range AP, not true AP**: predictions are already
  post-NMS-score-filtered at inference (observed floor 0.30, not the
  configured 0.10 — cause not identified, low-priority). This matches
  K-Radar's own official-benchmark protocol exactly, not a gap specific to
  this analysis.
- **`distance_from_ego` mixed provenance** (pred-based for TP/FP,
  GT-backfilled for FN) — never used for mATE/mASE/mAOE here; those use
  TP-only loc/dims/rotation directly.
- **Sequence-level pseudo-replication for weather/environment/time_of_day**
  (B.5, B.4) — the dominant limitation of this entire analysis. Any
  finding keyed on these three strata is only as generalizable as its
  `n_sequences` count; distance_bucket and frame_density do not share this
  problem.
- **Reliability floor is N≥30 rows** (corrected this session from a silently
  drifted N≥100 with no explanatory git history), with a soft N≥90 "still
  could be small-N artifact" caveat tier above that (corrected from 300,
  rescaled to preserve the original 3x-floor ratio). Every "reliable" tag
  in this document uses these corrected values, not the erroneous ones a
  prior version of the underlying pipeline briefly used.
- **D4's median-polish residual is a proxy, not the literal
  corrupted-minus-clean-vs-clean-baseline-gap double-difference** — a
  future task could compute that exact decomposition if a specific
  headline claim needs it; out of scope for this read-and-synthesize pass.
- **Per-class churn not computed** — the cached matcher output (reused to
  avoid a documented 7.6GB-RAM/7.7GB-swap blowup) is pooled over sed+bus.
- **`frame_deletion` conditions (9 of 31) excluded entirely** —
  expected/by-design crash-coverage, confirmed by user, not a data gap.
- **Class imbalance** (sed 82.6% / bus 17.4%) — every table cited above
  carries `cls` where relevant; pooled-only condition-level numbers
  (B.1/B.2/A.1–A.4) average over both classes and should not be read as
  sedan-only or bus-only performance.
- **Sensor-robustness framing (B.1)**: measures fused-model sensitivity to
  single-modality corruption, not standalone per-sensor accuracy.
- **AP is computable from this table** (reversal of an earlier Phase 1
  audit item that concluded otherwise) via `ap_metrics.compute_ap_grouped()`,
  restricted-range, from per-row `score`/`iou`. **CRI is not** — it needs
  raw (non-restricted-range) AP across severity tiers from the separate
  `ap_robustness_local.json` source, a standing cross-source dependency not
  resolved in this document. See
  `docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md`'s
  2026-09-01 addendum.