---
title: K-Radar Sensor Visibility Pipeline — Recommended Methods, Theory & Implementation
type: literature
source: home/adhish/Downloads/k-radar-recommended-pipeline-summary.md
date: 2026-07-02
tags: [05 Implementation]
---
# K-Radar Sensor Visibility Pipeline — Recommended Methods, Theory & Implementation

## 1. Recommended Methods per Sensor

| Sensor | Default (production) | Optional add-on | Offline-audit only |
|---|---|---|---|
| **Radar** | 1.2 SNR-weighted power density | 1.3 Doppler-coherence gating (per-object cropped sub-volume) | 1.4 Full 4DRT integration |
| **LiDAR 64 / 128** | 2.2 Expected-density normalization | 2.3 Ray-casting / frustum occupancy (merged into 2.2, see §3) | 2.4 Voxel occupancy (rejected) |
| **Camera ×4** | 4.2 8-corner projection area/centrality | 4.3 LiDAR depth-buffer occlusion discount (default-on, cheap since LiDAR already loaded); 4.5 Stereo consistency (front pair only, if rig overlap confirmed) | 4.4 Instance-segmentation mask overlap |

**Cross-sensor sanity check (free, no extra compute):**
`radar_visible=True ∧ lidar_visible=False ∧ camera_visible=False` → flag as probable radar multipath/ghost artifact (§6.1 in the main document) for review or automatic down-weighting.

---

## 2. Recommended Pipeline (Narrative)

1. **Per-frame precompute (once, shared across all M objects):**
   - Radar: per-frame CFAR noise-floor map over `radar_zyx_cube`.
   - LiDAR (each of 64/128): one range-image rasterization `(channel × azimuth_bin) → nearest range`.
   - Camera: project the full LiDAR point cloud into each of the 4 camera images once (for 4.3).

2. **Per-object scoring (vectorized across all M objects in the frame):**
   - Radar: excess-power sum in box / `V_box` (1.2); optionally refine with Doppler-coherence weighting (1.3) using a small cropped sub-tensor, not the full 4DRT.
   - LiDAR: combined density × occlusion score (2.2 + 2.3 merged, see §3 below), computed identically for OS2-64 and OS1-128 with sensor-specific channel LUTs.
   - Camera: 8-corner projected area/centrality (4.2), discounted by LiDAR depth-buffer occlusion (4.3); stereo consistency (4.5) applied only where a genuine stereo pair covers the object.

3. **Graceful degradation:** any missing/unreadable sensor file → `visible=False, score=0.0`, logged, pipeline continues.

4. **Cross-sensor QA pass:** compute the ghost-flag rule above; optionally sample 1–2% of frames for offline audit against 1.4 (radar) and 4.4 (camera) to validate the cheap defaults aren't drifting.

**Why this is the CPU-optimal combination:** every default-on method has cost that is either O(1) or O(N) per object with the expensive part amortized once per frame (noise-floor map, range image, LiDAR→camera projection) — so total per-frame cost scales as roughly `O(N_points + N_radar_cells + M·const)`, not `O(M × expensive_op)`. The gated/offline methods (1.4, 2.4, 4.4) are exactly the ones whose cost *would* scale badly with M or require a full 4DRT / learned model, so they're reserved for periodic calibration rather than every-frame production use.

---

## 3. Theory Recap: Why 2.2 and 2.3 Merge Into One Score

Every observed point count is theoretically a product of two independent factors:

```
N_actual  ≈  N_expected(geometry)  ×  fraction_actually_reached(occlusion)
```

- **2.2** measures the left-hand ratio (`N_actual / N_expected`) — a geometric, range-normalized sampling-adequacy term. It cannot distinguish "occluded" from "just far away" from "absorptive surface."
- **2.3** measures the right-hand factor directly, by checking — for every ray whose angular direction overlaps the box — whether it terminated at the box's range or stopped short on something nearer. This isolates the occlusion cause specifically.

Both questions are really different queries against the same underlying physical fact: **where did each ray's pulse first terminate**. That fact is exactly what a **range image** (one array per frame: for every `(channel, azimuth_bin)`, the nearest hit range) encodes. So instead of two separate analyses of the point cloud, you build the range image once per frame and ask it two questions per object — the 2.2 question (point-in-box count vs. expected count) and the 2.3 question (do rays aimed at the box actually reach it) — then combine them multiplicatively:

```
score   = density_ratio × (1 − occluded_fraction)
visible = (density_ratio > τ_density) and (occluded_fraction < 1.0)
```

**Distance handling:** distance is already accounted for on both sides —
- `N_expected ∝ A_visible / r²` (solid-angle falloff: a fixed-size object subtends fewer angular bins as range increases, so fewer points are expected, which is exactly why the *ratio* stays range-invariant).
- The angular footprint queried in the range image also shrinks with range (fewer ray indices returned at long range), but `occluded_fraction` is a ratio, so it remains well-formed even with few rays — with one caveat: at very long range, the ray count backing that ratio can become small (a handful of rays, or even a sub-bin footprint), making the ratio noisy/unreliable. The implementation below guards against this with a minimum-ray-count fallback.

---

## 4. Implementation Code

### 4.1 Per-frame precompute

```python
import numpy as np

def prepare_frame_lidar(points, sensor_origin, channel_lut):
    """
    Build a range image once per frame, shared across all objects.
    channel_lut: per-channel elevation angles (differs for OS2-64 vs OS1-128)
    Returns: range_image[channel_idx, azimuth_bin] = nearest hit range (or np.inf if no hit)
    """
    az_bins = channel_lut.n_azimuth_bins
    n_channels = len(channel_lut.elevations)
    range_image = np.full((n_channels, az_bins), np.inf, dtype=np.float32)

    rel = points - sensor_origin
    r = np.linalg.norm(rel, axis=1)
    az = np.arctan2(rel[:, 1], rel[:, 0])
    el = np.arcsin(np.clip(rel[:, 2] / np.maximum(r, 1e-6), -1, 1))

    az_idx = channel_lut.azimuth_to_bin(az)          # vectorized bin lookup
    ch_idx = channel_lut.elevation_to_channel(el)     # nearest-channel lookup

    valid = (ch_idx >= 0) & (ch_idx < n_channels)
    # Keep nearest hit per (channel, az_bin) cell
    order = np.argsort(r[valid])
    ch_v, az_v, r_v = ch_idx[valid][order], az_idx[valid][order], r[valid][order]
    range_image[ch_v, az_v] = np.minimum(range_image[ch_v, az_v], r_v)
    return range_image


def prepare_frame_radar(radar_zyx_cube, guard_cells, training_cells):
    """CFAR-style per-frame noise floor map, computed once."""
    noise_floor = cfar_noise_floor(radar_zyx_cube, guard_cells, training_cells)
    return noise_floor


def prepare_frame_camera(points, lidar_extrinsics, camera_intrinsics_list, camera_extrinsics_list):
    """Project LiDAR points into each of the 4 camera images once per frame."""
    depth_maps = []
    for K, T_cam in zip(camera_intrinsics_list, camera_extrinsics_list):
        pts_cam = transform_points(points, lidar_extrinsics, T_cam)
        uv, z = project_points(pts_cam, K)
        depth_maps.append(build_sparse_depth_map(uv, z))
    return depth_maps  # one sparse depth map per camera
```

### 4.2 Per-object LiDAR score (2.2 + 2.3 merged, with min-ray-count guard)

```python
MIN_RAYS_FOR_OCCLUSION_CHECK = 8   # guard against noisy ratios at long range
EPS = 1e-6

def lidar_score(box_half_extents, points, range_image, sensor_origin, channel_lut,
                 tau_density=0.08):
    """
    box_half_extents: (x, y, z, theta, l, w, h) as stored in K-Radar annotations.
    IMPORTANT: l, w, h are HALF-extents -> convert to full extents before any
    volumetric / area computation.
    """
    x, y, z, theta, l, w, h = box_half_extents
    L, W, H = 2 * l, 2 * w, 2 * h
    box = Box3D(center=(x, y, z), yaw=theta, size=(L, W, H))

    # --- 2.2: expected-density normalization ---
    N_actual = count_points_in_box(points, box)              # vectorizable, AABB-prefiltered
    A_visible = projected_silhouette_area(box, sensor_origin)  # facing-area model
    r = np.linalg.norm(np.array([x, y, z]) - sensor_origin)
    N_expected = (A_visible / max(r ** 2, EPS)) / (channel_lut.d_azimuth * channel_lut.d_elevation)
    density_ratio = min(1.0, N_actual / max(N_expected, EPS))

    # --- 2.3: ray-casting occlusion, reusing the same range_image ---
    ray_channels, ray_az_bins = angular_footprint(box, sensor_origin, channel_lut)
    n_rays = len(ray_channels)

    if n_rays < MIN_RAYS_FOR_OCCLUSION_CHECK:
        # Too few rays to trust an occlusion ratio -> fall back to density term alone
        occluded_fraction = 0.0
        occlusion_reliable = False
    else:
        hits = range_image[ray_channels, ray_az_bins]
        r_near, r_far = box_range_extent(box, sensor_origin)
        reaching = (hits >= r_near - EPS) & (hits <= r_far + EPS)
        occluded_fraction = 1.0 - reaching.sum() / n_rays
        occlusion_reliable = True

    # --- combine ---
    score = density_ratio * (1.0 - occluded_fraction)
    visible = (density_ratio > tau_density) and (occluded_fraction < 1.0)

    return {
        "visible": bool(visible),
        "score": float(score),
        "density_ratio": float(density_ratio),
        "occluded_fraction": float(occluded_fraction),
        "occlusion_reliable": occlusion_reliable,
        "n_rays": n_rays,
    }
```

### 4.3 Per-object radar score (1.2, optional 1.3 refinement)

```python
def radar_score(box_half_extents, radar_zyx_cube, noise_floor, cell_res,
                 doppler_cube=None, ego_velocity=None, epsilon=1e-3):
    x, y, z, theta, l, w, h = box_half_extents
    L, W, H = 2 * l, 2 * w, 2 * h
    box = Box3D(center=(x, y, z), yaw=theta, size=(L, W, H))
    V_box = L * W * H

    cell_idx = cells_in_box(box, cell_res)                 # index set into the collapsed cube
    power = radar_zyx_cube[cell_idx]
    excess = np.maximum(0.0, power - noise_floor[cell_idx])
    score = excess.sum() / max(V_box, epsilon)
    visible = excess.sum() > epsilon

    if doppler_cube is not None and ego_velocity is not None:
        # 1.3: crop only this object's small sub-volume across all Doppler bins
        sub_doppler = doppler_cube[cell_idx, :]             # small, bounded-size read
        v_exp = expected_doppler(box, ego_velocity)
        v_meas = doppler_bin_to_velocity(np.argmax(sub_doppler, axis=-1))
        coherence = np.clip(1.0 - np.abs(v_meas - v_exp) / v_tol, 0.0, 1.0)
        score = (excess * coherence).sum() / max(V_box, epsilon)

    return {"visible": bool(visible), "score": float(score)}
```

### 4.4 Per-object camera score (4.2 + 4.3 depth-buffer discount)

```python
def camera_score(box_half_extents, K, extrinsics, depth_map, image_size):
    x, y, z, theta, l, w, h = box_half_extents
    L, W, H = 2 * l, 2 * w, 2 * h
    corners_3d = box_corners((x, y, z), theta, (L, W, H))

    corners_2d, in_front = project_and_undistort(corners_3d, K, extrinsics)
    if not in_front.any():
        return {"visible": False, "score": 0.0}

    hull = convex_hull_2d(corners_2d)
    clipped = clip_to_image(hull, image_size)
    A_full = polygon_area(hull)
    A_clip = polygon_area(clipped)
    if A_clip <= 0:
        return {"visible": False, "score": 0.0}

    center_2d = polygon_centroid(clipped)
    image_center = np.array(image_size) / 2.0
    centrality = max(0.0, 1.0 - np.linalg.norm(center_2d - image_center) / (np.linalg.norm(image_size) / 2.0))

    base_score = (A_clip / max(A_full, 1e-6)) * centrality

    # 4.3: LiDAR depth-buffer occlusion discount (reuses depth_map from prepare_frame_camera)
    z_obj = expected_surface_depth(corners_3d, extrinsics)
    sample_uv = sample_pixels(clipped, n_samples=64)
    d_local = local_depth_lookup(depth_map, sample_uv, radius=3)  # neighborhood search for sparse depth
    occluded_px = np.sum(d_local < (z_obj(sample_uv) - DEPTH_MARGIN))
    occlusion_discount = 1.0 - occluded_px / max(len(sample_uv), 1)

    score = base_score * occlusion_discount
    return {"visible": True, "score": float(score)}
```

### 4.5 Frame-level orchestration + cross-sensor ghost flag

```python
def score_frame(objects, radar_ctx, lidar64_ctx, lidar128_ctx, camera_ctx):
    results = []
    for obj in objects:
        r = radar_score(obj.box, **radar_ctx) if radar_ctx else {"visible": False, "score": 0.0}
        l64 = lidar_score(obj.box, **lidar64_ctx) if lidar64_ctx else {"visible": False, "score": 0.0}
        l128 = lidar_score(obj.box, **lidar128_ctx) if lidar128_ctx else {"visible": False, "score": 0.0}
        cams = [camera_score(obj.box, **cctx) for cctx in camera_ctx] if camera_ctx else []
        cam_visible = any(c["visible"] for c in cams)

        probable_ghost = r["visible"] and (not l64["visible"]) and (not l128["visible"]) and (not cam_visible)

        results.append({
            "object_id": obj.id,
            "radar": r,
            "lidar_64": l64,
            "lidar_128": l128,
            "cameras": cams,
            "probable_radar_ghost": probable_ghost,
        })
    return results
```

---

## 5. Key Implementation Reminders

- **Half-extent conversion is applied exactly once**, at the top of every per-object scoring function (`L, W, H = 2*l, 2*w, 2*h`), before any area/volume computation — verified with a unit test against a hand-computed canonical box.
- **Nothing per-object re-does the expensive per-frame work** (range image, noise-floor map, LiDAR→camera projection) — those are function arguments (`range_image`, `noise_floor`, `depth_map`), computed once and passed in.
- **Graceful degradation:** every scoring function should be wrapped so a missing/corrupt input (e.g., `radar_zyx_cube is None`) short-circuits to `{"visible": False, "score": 0.0}` rather than raising.
- **Offline-audit hooks** (1.4 full 4DRT, 4.4 segmentation mask overlap) are intentionally *not* included in the default `score_frame` call — wire them in as separate, explicitly-invoked functions gated by a config flag, run on a sampled subset of frames for periodic validation.
