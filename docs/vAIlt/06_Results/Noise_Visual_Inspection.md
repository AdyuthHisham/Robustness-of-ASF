# Noise Visual Inspection

Rendered gallery and parameter reference for every corruption effect in [[04_Design/Noise_Taxonomy]], across 3 representative frames. Images are referenced in place via a symlink (`_assets/noise_visual_inspection` → `repos/K-Radar/outputs/noise_visual_inspection/`) — never copied, since they regenerate and copies drift.

## Frames

| Dir | seq | rdr idx | lidar idx | cam idx |
|---|---|---|---|---|
| `frame_seq001_rdr033` | 1 | 33 | 1 | 2 |
| `frame_seq021_rdr015` | 21 | 15 | 11 | 34 |
| `frame_seq048_rdr035` | 48 | 35 | 30 | 89 |

Filename grammar: `<modality>_<effect>[_<severity>].png`, severity ∈ `low|medium|high` (bare name = the v2 single-level render). `loss_complete` has no severity variants by design. Global `seed: 42` throughout.

## Parameters — v2 single-level (`effect_parameters.yaml`)

| Modality | Effect | Parameters |
|---|---|---|
| Radar | frame_deletion | deterministic, index_list=[0] |
| Radar | frame_deletion_random | p=0.5 |
| Radar | noise_induced_shifts | shift_std=2.0, gaussian |
| Radar | loss_partial | fraction=0.5 |
| LiDAR | frame_deletion | deterministic, index_list=[0] |
| LiDAR | frame_deletion_random | p=0.5 |
| LiDAR | gaussian_noise | σ_xy=0.5, σ_z=0.2 |
| LiDAR | loss_partial | fraction=0.5 |
| Camera | frame_deletion | deterministic, index_list=[0] |
| Camera | frame_deletion_random | p=0.5 |
| Camera | gaussian_noise | σ=40 |
| Camera | loss_partial | fraction=0.3 |

## Parameters — v3 severity ladder (`severity_parameters.yaml`)

| Modality | Effect | Low | Medium | High |
|---|---|---|---|---|
| Radar/LiDAR/Camera | loss_partial | fraction=0.1 | fraction=0.3 | fraction=0.8 |
| Radar/LiDAR/Camera | frame_deletion | random, p=0.1 | random, p=0.5 | random, p=0.9 |
| Radar | noise_induced_shifts | shift_std=0.01 | shift_std=1.0 | shift_std=5.0 |
| LiDAR | gaussian_noise | σ_xy/σ_z=0.01/0.01 | σ_xy/σ_z=0.5/0.2 | σ_xy/σ_z=1.0/1.0 |
| Camera | gaussian_noise | σ=1.0 | σ=40.0 | σ=50.0 |

Note the v3 severity ladder's `medium` LiDAR/camera Gaussian-noise values exactly match the v2 single-level parameters above — the v2 pass was effectively frozen as the "medium" rung when the severity ladder was built.

## Frame-deletion realized outcomes — methodological caveat

`frame_deletion` (random mode) is a **binary per-frame event**, not a continuous corruption strength — severity is the Bernoulli firing probability `p`, not a graded intensity. A single draw at a given `p` can land on the less-likely outcome (e.g. `p=0.9` *not* firing is a genuine ~10% event). The rendering process **searched up to 25 alternate seeds** for `low` and `high` severities specifically to land on the statistically expected outcome (not-fired for low, fired for high); `medium` (`p=0.5`) took the first draw with no preference, since 50/50 has no "expected" side.

Realized outcomes (all frames, all modalities): every `low` (p=0.1) case correctly landed on **not fired** on the first seed attempt. Every `high` (p=0.9) case landed on **fired**, mostly on the first attempt — one exception: `camera/seq048_rdr035/high` required 2 seed attempts. `medium` (p=0.5) outcomes varied genuinely by frame/modality (no preference applied), e.g. radar stayed *not fired* at medium in all 3 frames while lidar and camera fired at medium in most frames — this is expected variance, not a bug, but **worth flagging explicitly**: a reader comparing the medium-severity gallery image across modalities is not looking at a matched corruption *intensity*, only a matched corruption *probability*, and the two can look very different depending on which side of the coin flip landed.

## `loss_partial` — why it needs a dedicated zero-out-aware renderer

Row counts are **preserved** under `loss_partial` — zeroed points are not removed, they collapse to `(0,0,0)` in place (confirmed via `before_after_counts.md`, fraction=0.30 target):

| Frame/Modality | n_before = n_after | Zeroed fraction (actual) |
|---|---|---|
| radar (all 3 frames) | 150,000 | 0.3000 exactly |
| lidar seq001 / seq021 / seq048 | 60,601 / 73,569 / 48,209 | 0.3000 exactly |
| camera (all 3 frames) | 5,529,600 | 0.3000–0.3023 (per-pixel rounding) |

Because zeroed rows collapse to the origin rather than vanishing, a naive scatter-plot renderer would show them as a dense cluster at `(0,0,0)` rather than as absence — this is why the v2 regeneration introduced a dedicated zero-out-aware BEV renderer specifically for `loss_partial` (radar/lidar), confirmed via `v2_regeneration_confirmation.md`'s SHA-256 byte-identity check: every effect PNG is byte-identical to its pre-regeneration version **except** `loss_partial` (radar/lidar), which is intentionally re-styled; camera's `loss_partial` render was unaffected (2D pixel-array corruption doesn't have the same BEV-scatter ambiguity as a 3D point cloud).

The diagnostic gallery `_assets/noise_visual_inspection/loss_partial_zeroout_diagnostic/` (7 PNGs per frame) shows the before/after difference directly: `*_DEFAULT_before.png` (naive renderer, origin-cluster artifact) vs. `*_FIXED_after.png` (zero-out-aware renderer), plus a 3-panel `camera_clean_vs_loss_partial_vs_loss_complete.png` comparison.

## Byte-identity confirmation (v2 regeneration)

All 51 non-`loss_partial` PNGs across the 3 frames (17 effects × 3 frames, minus the 3 re-styled `loss_partial` radar/lidar renders) were confirmed **SHA-256-identical** before and after the v2 regeneration pass — the regeneration only touched what it intended to touch. See `_assets/noise_visual_inspection/v2_regeneration_confirmation.md` for the full 54-row hash table.

## Effect gallery

Effects per modality — camera/LiDAR: `clean`, `frame_deletion`(+3 severity), `frame_deletion_random`, `gaussian_noise`(+3), `loss_partial`(+3), `loss_complete`. Radar: same, except `noise_induced_shifts`(+3) replaces `gaussian_noise` (radar corruption is modeled as a per-point coordinate shift, not additive intensity noise — see [[04_Design/Noise_Taxonomy]]).

Example embeds (medium severity, `frame_seq001_rdr033`):

```
![[_assets/noise_visual_inspection/frame_seq001_rdr033/radar/radar_loss_partial_medium.png]]
![[_assets/noise_visual_inspection/frame_seq001_rdr033/lidar/lidar_gaussian_noise_medium.png]]
![[_assets/noise_visual_inspection/frame_seq001_rdr033/camera/camera_frame_deletion_random.png]]
```

Full gallery organization mirrors `_assets/noise_visual_inspection/index.html` (the existing v3 gallery) — see that file directly in Obsidian's file browser or via the symlink for the complete 3-frame × 3-modality × ~15-render set, plus `file_manifest.json` for size/sha256_16 per file.

## Cross-links

- Effect definitions and source papers: [[04_Design/Noise_Taxonomy]]
- Parameter justification / sweep rationale: `noise-injection-param-sweep-report.md` (not yet migrated into the PARA tree — flat file at `docs/vAIlt/noise-injection-param-sweep-report.md`, pending sort)

## Source

- `repos/K-Radar/outputs/noise_visual_inspection/effect_parameters.yaml`, `severity_parameters.yaml`, `frame_deletion_severity_log.md`, `v2_regeneration_confirmation.md`, `loss_partial_zeroout_diagnostic/before_after_counts.md`, `file_manifest.json`, `index.html`
