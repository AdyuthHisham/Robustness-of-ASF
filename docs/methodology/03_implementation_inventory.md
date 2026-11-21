## Directory Structure

```
.python-version (Other)
AGENTS.md (Documentation)
PHASE1_ANALYSIS.md (Documentation)
PHASE2_ROADMAP.md (Documentation)
README.md (Documentation)
README_projection.md (Documentation)
api_contracts.md (Documentation)
architecture.md (Documentation)
check_output.py (Python)
check_parquet.py (Python)
get_columns.py (Python)
kanban_create_commands.sh (Script)
lidar_visibility.py (Python)
output.parquet (Data)
parser.py (Python)
project_bbox_to_camera.py (Python)
pyproject.toml (Configuration)
    run_pipeline.py (Python)
        __init__.py (Python)
        calibration.py (Python)
        camera_visibility.py (Python)
        config.py (Python)
        config.py.backup (Other)
        config.py.backup2 (Other)
        data_loader.py (Python)
        lidar_visibility.py (Python)
        lidar_visibility.py.backup (Other)
        parser.py (Python)
        pipeline.py (Python)
        pipeline.py.backup (Other)
        radar_visibility.py (Python)
task_conditioned_normalization_strategy.md (Documentation)
    conftest.py (Python)
    test_smoke.py (Python)
    test_verify.py (Python)
```

## File Inventory

| File | Type | Purpose | Aligned To | Status |
|------|------|---------|------------|--------|
| .python-version | Other | 3.11 | General | Not Started |
| AGENTS.md | Documentation | AGENTS.md — kradar_visibility | General | Implemented |
| PHASE1_ANALYSIS.md | Documentation | Phase 1: Comprehensive Analysis | General | Implemented |
| PHASE2_ROADMAP.md | Documentation | Phase 2: Upgrade Strategy | General | Implemented |
| README.md | Documentation | No content | General | Not Started |
| README_projection.md | Documentation | K-Radar 3D Bounding Box to Camera Projection | General | Implemented |
| api_contracts.md | Documentation | kradar_visibility — API Contracts | General | Implemented |
| architecture.md | Documentation | kradar_visibility — Architecture | General | Implemented |
| check_output.py | Python | Python module | General | Implemented |
| check_parquet.py | Python | Python module | General | Implemented |
| get_columns.py | Python | Python module | General | Implemented |
| kanban_create_commands.sh | Script | WORKDIR="/home/adhish/Productivity/AMSCUP/test-... | General | Implemented |
| lidar_visibility.py | Python | Function to calculate point count | General | Implemented |
| output.parquet | Data | Unable to read file | General | Unknown |
| parser.py | Python | Define a function to parse the sensor data | General | Implemented |
| project_bbox_to_camera.py | Python | K-Radar 3D Bounding Box to Camera Image Projection | General | Implemented |
| pyproject.toml | Configuration | [project] | 08_readme_spec.md | Implemented |
| scripts/run_pipeline.py | Python | scripts/run_pipeline.py — CLI entry point for t... | 08_readme_spec.md | Implemented |
| src/kradar_visibility/__init__.py | Python | Python module | General | Implemented |
| src/kradar_visibility/calibration.py | Python | Load T_params_seq pickle for a given sequence. ... | kradar_visibility_analysis_prompt.md | Implemented |
| src/kradar_visibility/camera_visibility.py | Python | Camera visibility metrics for all four cameras ... | 04_visibility_methodology.md | Implemented |
| src/kradar_visibility/config.py | Python | Configuration for K-Radar visibility analysis. | 04_visibility_methodology.md | Implemented |
| src/kradar_visibility/config.py.backup | Other | """Configuration for K-Radar visibility analysis. | General | Implemented |
| src/kradar_visibility/config.py.backup2 | Other | """Configuration for K-Radar visibility analysis. | General | Implemented |
| src/kradar_visibility/data_loader.py | Python | Lazy data loaders for all sensor types. | kradar_visibility_analysis_prompt.md | Implemented |
| src/kradar_visibility/lidar_visibility.py | Python | LiDAR visibility metrics for OS2-64 and OS1-128. | 04_visibility_methodology.md | Implemented |
| src/kradar_visibility/lidar_visibility.py.backup | Other | """LiDAR visibility metrics for OS2-64 and OS1-... | General | Implemented |
| src/kradar_visibility/parser.py | Python | Parser for info_label_rev2/*.txt annotation files. | kradar_visibility_analysis_prompt.md | Implemented |
| src/kradar_visibility/pipeline.py | Python | Pipeline: parse labels -> compute visibility ->... | kradar_visibility_analysis_prompt.md | Implemented |
| src/kradar_visibility/pipeline.py.backup | Other | """Pipeline: parse labels -> compute visibility... | General | Implemented |
| src/kradar_visibility/radar_visibility.py | Python | Radar visibility metrics. | 04_visibility_methodology.md | Implemented |
| task_conditioned_normalization_strategy.md | Documentation | Task-Conditioned Normalization for Cross-Modal ... | General | Implemented |
| tests/conftest.py | Python | Load the toy-scale visibility parquet table (2 ... | General | Implemented |
| tests/test_smoke.py | Python | SMK-01: parse one file, header count==1, object... | 06_smoke_tests_scaffold.md | Implemented |
| tests/test_verify.py | Python | Verification tests for K-Radar visibility analy... | 07_verification_tests_scaffold.md | Implemented |

## Implementation Summary

- Total Files: 35
- Fully Implemented: 32 (91.4%)
- Partially Implemented: 0 (0.0%)
- Not Started: 2 (5.7%)
- Status Unknown: 1 (2.9%)