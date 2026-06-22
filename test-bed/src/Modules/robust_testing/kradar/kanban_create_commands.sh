WORKDIR="/home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar"

hermes kanban create "Verify and fix kradar_visibility/radar_visibility.py tests pass" \
  --assignee engineer \
  --workspace "dir:$WORKDIR" \
  --idempotency-key "kradar-radar-visibility-fix-v1" \
  --body "Read /mnt/agents/upload/04_visibility_methodology.md §4.1 and /mnt/agents/upload/kradar_visibility_analysis_prompt.md §3.1 (radar_* columns), §6 (SMK-10, SMK-14), §7 (VER-01/06/08/19/25-26).
Dataset: /home/adhish/Productivity/AMSCUP/repos/K-Radar
numpy and scipy are already installed via uv.

Previous attempt's radar_visibility.py failed tests with ModuleNotFoundError for numpy. This is now fixed.

Your job:
1. Read radar_visibility.py. Verify it uses scipy.io.loadmat() for .mat files, estimates noise_floor from cells OUTSIDE annotated bboxes, and vectorizes point-in-box across all objects per frame.
2. Fix anything missing or broken.
3. Run 'uv run pytest tests/test_smoke.py -k SMK-10 -v' and '-k SMK-14 -v'. Both must pass.
4. If tests don't exist, write them: SMK-10 loads one radar_zyx_cube .mat file and checks valid shape; SMK-14 checks radar_sparsity_score for a close (10m) bbox > far (80m) bbox.
5. IMPORTANT: when finished, you MUST call kanban_complete with a summary of what you did and verified. Do not just answer in plain text — the task stays open until you call kanban_complete (or kanban_block if stuck)." \
  --max-retries 2 \
  --json

hermes kanban create "Verify and fix kradar_visibility/lidar_visibility.py tests pass" \
  --assignee engineer \
  --workspace "dir:$WORKDIR" \
  --idempotency-key "kradar-lidar-visibility-fix-v1" \
  --body "Read /mnt/agents/upload/04_visibility_methodology.md §4.2 and /mnt/agents/upload/kradar_visibility_analysis_prompt.md §3.1 (lidar64_* / lidar128_*), §6 (SMK-11, SMK-12, SMK-15), §7 (VER-02/03/04/06/07/19/20/25-26).
Dataset: /home/adhish/Productivity/AMSCUP/repos/K-Radar
numpy installed; may need 'uv add open3d'.

Previous attempt vectorized point-in-box but failed on ModuleNotFoundError for numpy. Now fixed.

Your job:
1. Read lidar_visibility.py. Verify open3d.io.read_point_cloud() or numpy loads .pcd from os2-64/ and os1-128/, and point-in-box is vectorized (no per-bbox point loops).
2. Fix vectorization if broken/incomplete.
3. Run 'uv run pytest tests/test_smoke.py -k SMK-11/-12/-15 -v'. All must pass.
4. If tests don't exist, write them: SMK-11 loads one os2-64 .pcd, N>0; SMK-12 loads one os1-128 .pcd, N>0 and >= os2-64 count same frame; SMK-15 lidar128 point count >= lidar64 for same object.
5. IMPORTANT: when finished, you MUST call kanban_complete with a summary of what you did and verified. Do not just answer in plain text — the task stays open until you call kanban_complete (or kanban_block if stuck)." \
  --max-retries 2 \
  --json

hermes kanban create "Implement kradar_visibility/calibration.py and fix camera_visibility.py" \
  --assignee engineer \
  --workspace "dir:$WORKDIR" \
  --idempotency-key "kradar-camera-calibration-fix-v1" \
  --body "Read /mnt/agents/upload/04_visibility_methodology.md §4.3 and /mnt/agents/upload/kradar_visibility_analysis_prompt.md §3.1 (cam_* columns), §6 (SMK-05–09, SMK-16), §7 (VER-09–15).
Dataset: /home/adhish/Productivity/AMSCUP/repos/K-Radar
Repo: https://github.com/kaist-avelab/K-Radar
numpy installed; may need 'uv add pyyaml opencv-python-headless'.

CRITICAL ISSUES from previous attempt:
1. Wrong filename: kradar_calibration.py instead of kradar_visibility/calibration.py — delete the wrong one, create the correct one.
2. get_camera_params() returned None instead of real params from .yml files.
3. camera_visibility.py had a TypeError unpacking get_camera_params().

Your job:
1. Delete kradar_calibration.py if present. Create kradar_visibility/calibration.py.
2. Implement load_radar_lidar_calib, load_camera_calib (cam numbers front=1, left=7, right=3, rear=5; parse fx,fy,px,py,k1-k5, roll/pitch/yaw, x/y/z_ldr2cam; build T_lidar2cam), get_radar_lidar_transform, get_camera_params -> (K, dist, T_radar2cam).
3. Fix camera_visibility.py to import from kradar_visibility.calibration, split stitched stereo PNGs into 1280x720 halves (front:1+2, left:7+8, right:3+4, rear:5+6), visible = left OR right, score = max(left,right), proj from winning half.
4. Add behind-camera guard (z_cam>0) and bounds clipping [0,1280)x[0,720) per half.
5. Run 'uv run pytest tests/test_smoke.py -k SMK-05' through SMK-09 and SMK-16. All must pass.
6. If tests don't exist, write SMK-05..09 and SMK-16 as described (projection center checks, behind-camera check, visibility-score check).
7. IMPORTANT: when finished, you MUST call kanban_complete with a summary of what you did and verified. Do not just answer in plain text — the task stays open until you call kanban_complete (or kanban_block if stuck)." \
  --max-retries 2 \
  --json
