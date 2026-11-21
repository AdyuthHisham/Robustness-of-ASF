# ASF Pipeline Cheat Sheet (Fig. 4, slide 6)

One-liner: patch → align channels (UCP) → attend across sensors, pick what's usable (CASAP) → normalize so head doesn't care what combo it got (PN) → reshape (Fused FM) → trained to handle any combo (SCL).

## Blocks

- **Feature Maps**: each sensor's own backbone output — camera (BEVDepth), LiDAR (SECOND), 4D radar (RTNH) — all resized to the same BEV height×width, different channel counts.
- **Patchification**: each feature map is chopped into equal-sized spatial patches. Because all three sensors' patches are already spatially aligned (same BEV grid position), ASF skips the expensive positional-embedding step that transformer-based fusion methods need.
- **UCP (Unified Canonical Projection)**: per-sensor learned projection (LayerNorm → MLP → GeLU, repeated twice) that maps each sensor's patch into one shared channel dimension. Makes patches from different sensors directly comparable — "canonical" = same coordinate system for the attention step.
- **CASAP w/ PN**: cross-attention where a trainable reference query attends across the 3 sensors' patches (not across all patches like standard transformer fusion — O(N_sensors) not O(N_sensors×N_patches)). Query ends up dominated by whichever sensor(s) are actually informative. **PN = post-feature normalization**, one more LayerNorm+MLP+GeLU pass after attention, so the detection head sees consistent features regardless of sensor combo used.
- **Fused FM**: normalized patches reshaped back to the original BEV H×W grid — feeds the detection head.
- **SCL (Sensor Combination Loss)**: training-time loss that exposes the model to every sensor-availability combination during training (not just full-sensor), so it doesn't collapse when a sensor is missing/degraded at inference.

## ASF in a few words

Multi-sensor fusion (camera+LiDAR+4D radar) that projects all three sensors into a shared feature space and uses cross-attention to automatically weight whichever sensors are actually available/reliable — designed to keep working when a sensor degrades or drops out, without retraining for each sensor combination.

## Slide 6 claim text (verbatim)

"What makes ASF Robust: Graceful degradation under adverse weather / No retraining needed across sensor combinations / Near-optimal performance under damaged sensors" (labeled on-slide as ASF's claims, not thesis findings)

## Fig. 5 — BEV AP by weather, local inference

Own re-run of the released ASF checkpoint on K-Radar — "local" distinguishes it from ASF's paper-reported numbers. Same table structure as Results.tex baseline table: BEV AP at IoU=0.3, by weather, sedan vs bus/truck. Local reproduction comes in 3.2–5.6 points below ASF's published numbers across the board — this is why the thesis uses its own re-run as reference, not the paper's numbers.

Source: ASF paper (arXiv 2503.07029v2), §3.1–3.2, docs/lit_survey/models/2503.07029v2.pdf.
