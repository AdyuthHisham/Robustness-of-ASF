Starter: Read /home/adhish/Downloads/00_orchestrator_kickoff_prompt.md first, then /home/adhish/Downloads/kradar_visibility_analysis_prompt.md, /home/adhish/Downloads/04_visibility_methodology.md, /home/adhish/Downloads/06_smoke_tests_scaffold.md, and /home/adhish/Downloads/07_verification_tests_scaffold.md.

/goal Build the kradar_visibility package in /home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar against /home/adhish/Productivity/AMSCUP/repos/K-Radar using uv exclusively, outputting a Parquet table matching the §3.1 schema.

/subgoal Implement all §8 modules: config.py, parser.py, calibration.py, data_loader.py, radar_visibility.py (§4.1 method B), lidar_visibility.py (§4.2 method A+B, reusing the existing points_in_boxes_gpu pipeline elsewhere in the test-bed repo, not reimplementing it), camera_visibility.py (§4.3 method B), pipeline.py.

/subgoal Every radar_*, lidar64_*, lidar128_*, and cam_*_* column in the output Parquet must hold real computed values, not placeholders or constants.

/subgoal Not complete until a response pastes the raw, unedited output of uv run pytest tests/test_smoke.py -v showing all 17 SMK tests passing.

/subgoal Not complete until a response pastes the raw output of a uv run python one-liner that reads the output Parquet with polars and prints its shape and column list.

/subgoal Not complete until a response pastes the raw output of a one-liner printing min/max/mean of radar_sparsity_score, lidar64_points_count, and cam_front_visibility_score, proving computed variance rather than constants/nulls.

/subgoal A prose claim of completion without that pasted output does not satisfy the goal — judge "continue" if the evidence is missing, regardless of what the response claims was built.

/subgoal Write kradar_visibility/README.md per /home/adhish/Downloads/08_readme_spec.md, after the pipeline runs end-to-end and smoke tests pass — covering architecture, per-module reference pulled from actual code, methodology summary, schema reference, uv-based setup/usage, testing instructions, known limitations, and at least 2 of §10's analysis queries as real Polars one-liners.

/subgoal Parse all info_label_rev2/*.txt files (header + object lines) correctly, including the shared cam-lrr index for left/right/rear cameras, per §2 and SMK-01/SMK-02 in 06_smoke_tests_scaffold.md.

/subgoal Load calibration for all 7 active sensors (R, L1, L2, CF, CL, CR, CRE) from info_calib/, per SMK-03.

/subgoal Implement lazy-loading data_loader.py for radar_zyx_cube, OS2-64, OS1-128, and all 4 camera streams — never load full radar_tesseract by default.

/subgoal Implement radar_sparsity_score using the SNR-weighted power density method on radar_zyx_cube, per §4.1 method B in 04_visibility_methodology.md, with radar_fov_in/radar_range_in as pure geometry checks.

/subgoal Implement lidar64/lidar128 point counts by reusing the existing points_in_boxes_gpu (OpenPCDet) pipeline found elsewhere in the test-bed repo, and derive lidar*_sparsity_score via the expected-density normalization, per §4.2 method A+B in 04_visibility_methodology.md.

/subgoal Implement cam_*_visibility_score via 8-corner bbox projection → clipped area + centrality, per §4.3 method B in 04_visibility_methodology.md, for all 4 cameras; leave the LiDAR depth-buffer occlusion discount (method C) behind a config flag, off by default.

/subgoal Assemble the full output table with every column from §3.1 in kradar_visibility_analysis_prompt.md, correct dtypes, and write to Parquet via pipeline.py.

/subgoal Fill in and pass every test in tests/test_smoke.py (SMK-01 through SMK-17, from 06_smoke_tests_scaffold.md) on a 2-sequence, 20-frame sample before proceeding further.

/subgoal Fill in and pass every test in tests/test_verify.py (VER-01 through VER-26, from 07_verification_tests_scaffold.md) on the full dataset, marking §7.6 weather tests optional if weather labels aren't wired in yet.

/subgoal Manage all dependencies via uv add and run all commands via uv run — no pip, conda, or manual venv activation.
