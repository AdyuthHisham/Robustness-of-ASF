# Two follow-ups on flagged-but-unresolved items in crossproduct_trends_and_anomalies

Deeper dig into two items `docs/crossproduct_trends_and_anomalies.md` explicitly
left as "flagged, not investigated further" (A.4) or asserted without checking the
confound (A.1's D4 fog interaction). Companion to [[asf-availability-told-not-aware]]
— same style of "look past the aggregate metric at the mechanism" investigation.

## 1. "Suspicious recovery" (A.4) is mostly a rate-denominator artifact

`q5_suspicious_recovery.csv` flags 13/21 conditions where
`corruption_induced_recovery_rate >= corruption_induced_miss_rate`. Pulling the raw
2x2 counts behind the rates (not just the rates) shows why, and it isn't "the model
gets better under corruption":

- `miss_rate = n_miss / (n_stable + n_miss)` — denominator is the clean-*detected*
  population (~27,000-35,000 objects for a typical condition).
- `recovery_rate = n_recover / (n_recover + n_fail)` — denominator is the
  clean-*missed* population, much smaller (~7,000-8,300, since baseline already
  misses ~23% of all GT objects overall).

Dividing a small recovery count by a small denominator routinely produces a rate
comparable to or larger than the miss rate even when the **absolute object count
moved against the model**. Checked all 13 flagged rows:

| Condition | n_miss | n_recover | net (recover−miss) |
|---|---|---|---|
| `camera_gaussian_noise_high` | 749 | 243 | −506 |
| `radar_loss_complete_zero` | 2481 | 775 | −1706 |
| `lidar_loss_partial_high` | 2431 | 1286 | −1145 |
| `lidar_loss_partial_medium` | 713 | 1164 | **+451** |
| `lidar_loss_partial_low` | 300 | 611 | **+311** |
| `radar_gaussian_noise_low` | 241 | 239 | ≈0 |
| (7 more, all camera/radar-medium-or-worse) | — | — | negative |

**9 of 13 flagged conditions are net-negative in absolute detected-object count**
despite tripping the rate-based flag — the flag compares two differently-scaled
rates, not like with like. Only **4 of 13** (`lidar_loss_partial_{low,medium}`,
`radar_gaussian_noise_low`, `radar_loss_partial_low`) are genuinely net-positive,
and all four are the *mildest* severity in the sweep — consistent with sub-voxel
perturbation acting as jitter that occasionally nudges a borderline-score box over
the greedy matcher's threshold, not evidence the network "sees better." This matches
`net_retention` (correctly bounded/interpretable, unlike the raw rate comparison)
being >1.0 for exactly these four and only these four.

**Correction to A.4's framing**: don't cite "13/21 conditions show suspicious
recovery" as a network-behavior anomaly — it's a metric-definition artifact from
asymmetric denominators (small clean-miss population vs. large clean-detected
population). The real, mechanistically sound "mild corruption occasionally helps"
signal is the 4-condition net_retention>1.0 cluster, a narrower and much more
mundane claim.

## 2. The "fog protects against LiDAR noise" (D4) finding is confounded with fog being the easiest baseline bucket

Pulled `summary_cond_cls_weather.parquet` directly (sed class):

| Weather | baseline sed AP | n | `lidar_gaussian_noise_high` AP | retention |
|---|---|---|---|---|
| fog | **94.91** | 2,035 | 53.26 | 56.1% |
| overcast | 89.40 | 1,186 | 26.10 | 29.2% |
| sleet | 76.10 | 1,928 | 30.53 | 40.1% |
| normal | 77.21 | 21,712 | 11.00 | 14.3% |
| rain | 69.13 | 6,505 | 11.33 | 16.4% |

Fog isn't just the best-retaining bucket under LiDAR noise (as D4 reports) — it's
also, by a wide margin, the easiest baseline weather bucket overall (94.9 vs.
69-89 everywhere else), on the smallest sample (6/58 sequences carry fog at all,
per B.5's own sequence-confound caveat). High-baseline + tiny-N is the signature
of a couple of unusually easy sequences (well-separated, favorable-geometry
objects), not necessarily a real physical "fog helps the network resist LiDAR
corruption" effect.

Not fully resolved either way — the ordering isn't a clean monotonic
"easier-baseline-survives-better" relationship (sleet retains noise better than
overcast despite a lower baseline AP, so baseline difficulty alone doesn't explain
everything) — but fog specifically, which is doing most of the work in D4's
"genuine weather interaction" claim, is confounded enough with baseline difficulty
and sequence count that it should not be reported as a clean architectural finding
without first controlling for per-stratum baseline difficulty (e.g. residualizing
against baseline AP, not just the additive condition+weather model D4 already
subtracts).

## Follow-up not done

- D4's median-polish residual could be recomputed with baseline AP as an added
  covariate to see if the fog effect survives controlling for it — not done here,
  flagged as the natural next step.
- Recovery-rate metric itself could be redefined as a rate over a shared
  denominator (e.g. all GT objects) to avoid the asymmetric-population issue
  going forward — a design fix to `gt_transition_analysis.py`'s
  `aggregate_transition_rates`, not applied here (would change historical
  numbers, needs a decision).
