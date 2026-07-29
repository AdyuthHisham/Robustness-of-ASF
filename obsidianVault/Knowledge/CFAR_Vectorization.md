# CFAR Vectorization — Evidence Verification (2026-07-27)

## Summary claims vs verified reality

| Claim | Reported | Verified | Status |
|-------|----------|----------|--------|
| Speedup | 41× (430s → 10.6s) | **46×** (430s → mean 9.41s) | Close — actual faster than claimed |
| Numerical equivalence | 0.00e+00 max abs diff | 0.00e+00 max abs diff on 2 real frames | ✓ Verified |
| r = -1.0 NF→score correlation | "genuine local adaptivity confirmed" | **Meaningless — artifact of 2-point correlation** | ✗ Claim overinterpreted |
| 400-frame viability | ~70 min | **~63 min CFAR only; ~400 min with cold I/O** | Understates I/O cost |

## Per-frame benchmarks (vectorized, real K-Radar frames)

| Frame | Time (s) | Valid cells |
|-------|----------|-------------|
| 00135 | 8.08 | 7,732,075/15,000,000 |
| 00140 | 8.19 | 7,732,075/15,000,000 |
| 00152 | 11.97 | 7,732,075/15,000,000 |
| **Mean** | **9.41** | |
| **Std** | **1.81** | |

Cube loading (scipy.io.loadmat) adds ~100-170s cold, ~5s cached per frame.

## Numerical equivalence

Bit-identical on sub-cubes (20×40×40) of frames 00135 and 00140. Max abs diff = 0.000000e+00 on both.

## Per-object scores

35 frames in seq 2 have ≥2 objects (all exactly 2 — no frame has 3+). Scored 7 frames:

- Scores all in [0, 1]
- Range across all objects: [0.0036, 0.0382] — very low (high dB noise floor ~110 dB results in near-zero SNR)
- Within-frame spread: 3-8× ratio between objects (Bus/Truck > Sedan), driven by object size/distance
- Local noise floor variation within frame: <0.4 dB — CFAR adaptivity acts at frame-region level, not object-discrimination level
- **r=-1.0 is a 2-point artifact** — with exactly 2 objects/frame, Pearson correlation is always ±1.0

## Key finding

The CFAR vectorization is correct and fast (46× speedup, bit-identical), but the summary's "local adaptivity confirmed" claim is overstated. The r=-1.0 correlation is a mathematical artifact. The actual evidence for adaptivity is the per-object score spread (3-8× within same frame), which is genuine but driven by object signal differences, not noise-floor discrimination.

## Further optimization headroom

- **~3-5s/frame** achievable via `np.partition` instead of `np.median` (2-3×) + multi-threaded Z-plane parallelism
- **<1s/frame** requires GPU offloading (maps well to GPU — 15M × 24-element medians is ~100ms on CUDA)
- Z-loop elimination via 3D sliding window is **not viable** (~38 GB memory for view of (150,400,250,13,13,13))