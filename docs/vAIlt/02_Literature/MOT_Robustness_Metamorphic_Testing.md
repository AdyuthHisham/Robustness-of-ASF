# Towards the Robustness of Multiple Object Tracking Systems

#ReferPaper #corruption/tracking/metamorphic #important

Xie, Duan, Chen, Xuan (Wuhan University). ISSRE 2022.

## Contribution

First metamorphic-testing method for Multiple Object Tracking (MOT) robustness, covering two MOT-specific dynamic scenario classes prior (mostly static-image) work didn't address: **speed variety of tracked objects** and **temporary camera failure**. Five metamorphic relations (MRs) transform frame *sequences*, tested on KITTI tracking (29 videos) against SORT+YOLOv3 (tracking-by-detection), PointTrack (tracking-by-segmentation), CenterTrack (joint detection+tracking).

## Frame Deletion — exact definitions (source paper for this project's own Frame Deletion corruption)

- **MR1-1 (fixed-interval / deterministic deletion)**: retain every k-th frame, `V' = {f_{i·k}}`, discard the rest. Experimentally **k=2** — deletes every other frame, simulating 2× object speed.
- **MR1-2 (random deletion)**: randomly remove **p=1%** of frames; **q=5** independently-sampled follow-up videos per source video to average out randomness.
- **MR2-1 (frame freeze, related but distinct)**: p% of frames *replaced* with the immediately preceding frame (not removed — duplicated), simulating a video-freeze camera failure. Same p=1%, q=5.
- (MR2-2 pixelation, MR2-3 Gaussian blur are separate noise-type MRs, not frame-deletion — implemented via Dart's `pixelate` and Pillow's `GaussianBlur` respectively.)

Consistency oracle: IoU>0.5 detection matching + trajectory-ID consistency across mapped frame pairs between source and follow-up video; any mismatch is a violation, categorized as Missing Detection / Additional Detection / ID Switch (CLEAR MOT taxonomy).

## Key findings

- **All three MOT systems violate MRs in over two-thirds of the 29 test videos**; some combinations (CenterTrack under MR1-1, MR2-2, MR2-3) violate in **29/29 — every single video**.
- **MR1-1 (deterministic, stable 2× deletion) causes substantially more errors than the four "occasional" MRs (1% random perturbation)** — a stable, wholesale change to effective sampling rate is a harder robustness challenge than brief occasional corruption, across all three systems.
- Small, localized corruption events have a **footprint larger than their trigger**: even though MR1-2/MR2-1/MR2-2/MR2-3 modify only 1% of frames, in many tests the resulting tracking inconsistency affects **more than 1%** of frames — errors propagate into subsequent unmodified frames.
- Noise-type MRs (pixelation, blur) cause **more** errors than information-loss MRs (deletion, freeze) across all three systems — these MOT architectures are more vulnerable to noise disturbance than to outright information loss.
- Architecture-dependent robustness groupings: CenterTrack (joint detection+tracking) is best under information-loss MRs but worst under noise MRs (tightly coupled model shares vulnerability across both tasks); SORT+YOLOv3 (loosely coupled detection/association) is the reverse — best under noise, worst under stable speed variety.

## Relevance to AMSCUP

Directly cited as the source for this project's own Frame Deletion (deterministic + random) implementation for LiDAR/camera/radar (see [[04_Design/Noise_Taxonomy]]) — the k=2 fixed-interval and p=1%/q=5 random-deletion parameterization scheme is worth cross-checking against this project's own `frame_deletion_random` Bernoulli p sweep (0.1/0.5/0.9, per [[06_Results/Noise_Visual_Inspection]]) — this project uses a much wider severity range than the source paper's single p=1% setting.

## Limitations acknowledged

Only 29 videos, 3 systems (one per paradigm) — authors note limited generalizability; only 2 scenario categories / 5 MRs studied, with an explicit acknowledgment that "we can never detect all the defects by testing" (no completeness guarantee for MR coverage); explicitly scoped as **natural/common corruption, not adversarial-attack noise** — a framing distinction relevant to how this project should describe its own corruption suite.

## Source

- `docs/lit_survey/noise_addition/markdown/Towards_the_Robustness_of_Multiple_Object_Tracking_Systems.md` (376 L)
