# Migration Changelog
Generated: 2026-07-02 13:20:46

## 2026-08-11 — Dedup pass (Phase 1 of `docs/vault_ingestion_prompt.md`)

Executed `docs/vAIlt/00_Inbox/Dedup_Map.md` Groups A/B (import-echo `_N` files), confirmed by the user.
Verified via diff (frontmatter-stripped) that every archived pair is byte-identical in body content before moving.

**Archived to `10_Archive/` (26 files, content-identical to their canonical, confirmed by diff):**
`05_Implementation/`: `11_README_Requirements_1`, `4_Visibility_Metric_Methodology__Recommendations_1`, `6_Smoke_Test_Scaffold_1`, `7_Verification_Test_Scaffold_1`, `Config_Reference_1`, `Goals_And_Subgoals_1`, `Hermes_Multi-Agent_Workplan_1`, `KRadar_configpy_Reference_1`, `K-Radar_Configuration_Reference_1`, `K-Radar_Coordinate_Frame_Analysis_Report_1`, `K-Radar_Multi-Sensor_Visibility_Calculation_Formulas_and_Methodologies_1`, `K-Radar_Sensor_Visibility_Pipeline__Recommended_Methods_Theory__Implementation_{1,2,3}`, `K-Radar_Visibility_Analysis__Master_Task_Brief_1`, `K-Radar_Visibility_Pipeline__Debug_Data_Gathering__Web_Viewer_1`, `K-Radar_Visibility_Pipeline__Issue_Summary_1`, `K-Radar_Visibility_Visual_Verification__Web_UI_Specification_1`, `Orchestrator_Task_Implement_K-Radar_Visibility_Analysis_Pipeline_1`, `Prompt_K-Radar_Multi-Sensor_Visibility_Analysis_Table_Generator_1`, `Refined_SOULmd_Files__Unified_Perception_Framework_Dev_Team_1`, `Sensor_Noise_Modeling_for_Object_Detection_Sensor_Fusion_Test_Suites_1`, `Visibility_Metrics_Comparison_ELI15_1`.
`02_Literature/`: `Sensor_Visibility__Identification_Metrics_for_K-Radar_{1,2,3}`, `Visibility_Calculation_Methods_Literature_Review_and_Analysis_1`.
`07_Writing/`: `Aggregated_Data__AMSCUP_1`.

**Also archived (misfiled, not a dedup — per user decision):** `03_Theory/BSD_3-Clause_License.md` and `_1.md` — third-party license text unrelated to the thesis project, moved wholesale to `10_Archive/03_Theory/`.

**Left in place (per user decision):** `05_Implementation/LibCrypt_Patcher.md`, `LibCrypt_Patcher_1.md`, `LibCrypt_Patcherreadmemd_-_Changelog.md`, `_1.md` — content unrelated to AMSCUP, user chose to leave rather than archive.

**False positive caught and reverted:** `03_Theory/Annotations_1.md` was initially archived on the assumption it was an import-echo of `Annotations.md`, matching the general `_N` pattern. Diff against the changelog's original source paths showed it is genuinely different content — Zotero annotations on `lyuCameraLiDARIMU2025` vs `Annotations.md`'s `liAutomaticTargetlessLiDAR2023`. Restored to `03_Theory/`.

**Deferred to Phase 2 (not resolved in this pass):** the 8-file verification-report cluster (`docs/verification_report.md`, `docs/verification_report_partial1.md`, and 6 files under `test-bed/.../kradar/docs/` and `.../outputs/`) needs a real diff-and-fold merge, not a pick-longest — different "part_" suffixes suggest different phases/sections, not simple re-saves. See `Dedup_Map.md` Group C.

## Summary
- Processed: 44 files
- Skipped (duplicates): 0 files
- Conflicts (renamed): 33 files

## Details

PROCESSED: /home/adhish/Downloads/07_verification_tests_scaffold.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/7_Verification_Test_Scaffold.md
PROCESSED: /home/adhish/Downloads/08_readme_spec.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/11_README_Requirements.md
PROCESSED: /home/adhish/Downloads/kradar_visibility_analysis_prompt.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Prompt_K-Radar_Multi-Sensor_Visibility_Analysis_Table_Generator.md
PROCESSED: /home/adhish/Downloads/kradar_visual_verification_spec.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Visual_Verification__Web_UI_Specification.md
PROCESSED: /home/adhish/Downloads/00_orchestrator_kickoff_prompt.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Orchestrator_Task_Implement_K-Radar_Visibility_Analysis_Pipeline.md
PROCESSED: /home/adhish/Downloads/visibility_methods_literature_review.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Visibility_Calculation_Methods_Literature_Review_and_Analysis.md
PROCESSED: /home/adhish/Downloads/hermes_multiagent_workplan.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Hermes_Multi-Agent_Workplan.md
PROCESSED: /home/adhish/Downloads/kradar_task_brief.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Analysis__Master_Task_Brief.md
PROCESSED: /home/adhish/Downloads/k-radar-recommended-pipeline-summary.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Sensor_Visibility_Pipeline__Recommended_Methods_Theory__Implementation.md
PROCESSED: /home/adhish/Downloads/pipeline_issues.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Pipeline__Issue_Summary.md
PROCESSED: /home/adhish/Downloads/k-radar-sensor-visibility-metrics.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Sensor_Visibility__Identification_Metrics_for_K-Radar.md
PROCESSED: /home/adhish/Downloads/kradar_task_full_spec.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Pipeline__Debug_Data_Gathering__Web_Viewer.md
PROCESSED: /home/adhish/Downloads/goals_and_subgoals.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Goals_And_Subgoals.md
PROCESSED: /home/adhish/Downloads/04_visibility_methodology.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/4_Visibility_Metric_Methodology__Recommendations.md
PROCESSED: /home/adhish/Downloads/refined_souls.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Refined_SOULmd_Files__Unified_Perception_Framework_Dev_Team.md
PROCESSED: /home/adhish/Downloads/06_smoke_tests_scaffold.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/6_Smoke_Test_Scaffold.md
PROCESSED: /home/adhish/Downloads/libcrypt-patcher-v1.1.0-linux-x86_64-static/license.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/03_Theory/BSD_3-Clause_License.md
PROCESSED: /home/adhish/Downloads/libcrypt-patcher-v1.1.0-linux-x86_64-static/changelog.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/LibCrypt_Patcherreadmemd_-_Changelog.md
PROCESSED: /home/adhish/Downloads/libcrypt-patcher-v1.1.0-linux-x86_64-static/readme.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/LibCrypt_Patcher.md
PROCESSED: /home/adhish/Downloads/libcrypt-patcher-v1.1.0-linux-x86_64-static/build.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/10_Archive/Building_From_Source.md
CONFLICT (renamed): /home/adhish/Downloads/bak/k-radar-recommended-pipeline-summary.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Sensor_Visibility_Pipeline__Recommended_Methods_Theory__Implementation_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Downloads/bak/k-radar-sensor-visibility-metrics.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Sensor_Visibility__Identification_Metrics_for_K-Radar_1.md (original target existed with different content)
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/sensor_noise_modeling_research.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Sensor_Noise_Modeling_for_Object_Detection_Sensor_Fusion_Test_Suites.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/kradar_config_reference.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Configuration_Reference.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/kradar_config.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/KRadar_configpy_Reference.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/aggregated_data.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/07_Writing/Aggregated_Data__AMSCUP.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/COORDINATE_FRAME_ANALYSIS.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Coordinate_Frame_Analysis_Report.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/VISIBILITY_FORMULAS_AND_METHODS.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Multi-Sensor_Visibility_Calculation_Formulas_and_Methodologies.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/config_reference.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Config_Reference.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/visibility_comparison.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Visibility_Metrics_Comparison_ELI15.md
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Pipeline__Issue_Summary.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Pipeline__Issue_Summary_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Configuration_Reference.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Configuration_Reference_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/LibCrypt_Patcherreadmemd_-_Changelog.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/LibCrypt_Patcherreadmemd_-_Changelog_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Config_Reference.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Config_Reference_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Multi-Sensor_Visibility_Calculation_Formulas_and_Methodologies.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Multi-Sensor_Visibility_Calculation_Formulas_and_Methodologies_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/7_Verification_Test_Scaffold.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/7_Verification_Test_Scaffold_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Prompt_K-Radar_Multi-Sensor_Visibility_Analysis_Table_Generator.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Prompt_K-Radar_Multi-Sensor_Visibility_Analysis_Table_Generator_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/11_README_Requirements.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/11_README_Requirements_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/LibCrypt_Patcher.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/LibCrypt_Patcher_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Hermes_Multi-Agent_Workplan.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Hermes_Multi-Agent_Workplan_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Visibility_Metrics_Comparison_ELI15.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Visibility_Metrics_Comparison_ELI15_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/KRadar_configpy_Reference.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/KRadar_configpy_Reference_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Visual_Verification__Web_UI_Specification.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Visual_Verification__Web_UI_Specification_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Sensor_Visibility_Pipeline__Recommended_Methods_Theory__Implementation_1.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Sensor_Visibility_Pipeline__Recommended_Methods_Theory__Implementation_2.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Coordinate_Frame_Analysis_Report.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Coordinate_Frame_Analysis_Report_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Orchestrator_Task_Implement_K-Radar_Visibility_Analysis_Pipeline.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Orchestrator_Task_Implement_K-Radar_Visibility_Analysis_Pipeline_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/4_Visibility_Metric_Methodology__Recommendations.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/4_Visibility_Metric_Methodology__Recommendations_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Pipeline__Debug_Data_Gathering__Web_Viewer.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Pipeline__Debug_Data_Gathering__Web_Viewer_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Refined_SOULmd_Files__Unified_Perception_Framework_Dev_Team.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Refined_SOULmd_Files__Unified_Perception_Framework_Dev_Team_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Sensor_Noise_Modeling_for_Object_Detection_Sensor_Fusion_Test_Suites.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Sensor_Noise_Modeling_for_Object_Detection_Sensor_Fusion_Test_Suites_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Analysis__Master_Task_Brief.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Visibility_Analysis__Master_Task_Brief_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Goals_And_Subgoals.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/Goals_And_Subgoals_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/6_Smoke_Test_Scaffold.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/6_Smoke_Test_Scaffold_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Sensor_Visibility_Pipeline__Recommended_Methods_Theory__Implementation.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/K-Radar_Sensor_Visibility_Pipeline__Recommended_Methods_Theory__Implementation_3.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/10_Archive/Building_From_Source.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/10_Archive/Building_From_Source_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/07_Writing/Aggregated_Data__AMSCUP.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/07_Writing/Aggregated_Data__AMSCUP_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Sensor_Visibility__Identification_Metrics_for_K-Radar_1.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Sensor_Visibility__Identification_Metrics_for_K-Radar_2.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Sensor_Visibility__Identification_Metrics_for_K-Radar.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Sensor_Visibility__Identification_Metrics_for_K-Radar_3.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Visibility_Calculation_Methods_Literature_Review_and_Analysis.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Visibility_Calculation_Methods_Literature_Review_and_Analysis_1.md (original target existed with different content)
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/docs/vAIlt/03_Theory/BSD_3-Clause_License.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/03_Theory/BSD_3-Clause_License_1.md (original target existed with different content)
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/Latex_Report/FLAGS_REVIEW.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Missing_Citations_Results_and_Conflicts_-_Human_Review_Required.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/Latex_Report/figure_inventory.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/06_Results/Figure_Inventory_and_LaTeX_Inclusion_Suggestions.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/qa/qa_report_t_c872701f.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/QA_Report_for_task_t_c872701f_QA_review_aggregated_datamd_completeness.md
PROCESSED: /home/adhish/Productivity/AMSCUP/docs/qa/qa_report_t_fa484955.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/05_Implementation/QA_Report_for_t_fa484955_aggregated_datamd_completeness.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/Methodology - Automatic Multi-Sensor Calibration and Unified Perception.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Usual_Questions.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/Meeting Notes.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/01_Project_Management/March_23.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/Literature Review - Automatic Multi-Sensor Calibration and Unified Perception.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/03_Theory/0_Problem_Statement.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/Canvas Notes.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/00_Inbox/KRADAR.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/Untitled.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/03_Theory/phase_2.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/Admin-ish/Daily Notes.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/tasks.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/Admin-ish/General.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/General.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/Excalidraw/Drawing 2026-04-13 14.45.35.excalidraw.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/00_Inbox/Excalidraw_Data.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/LitSurvey/liAutomaticTargetlessLiDAR2023.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/03_Theory/Annotations.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/LitSurvey/shiRadarCameraFusion2024.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Annotations.md
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/LitSurvey/LitSurvey.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/02_Literature/Notes.md
CONFLICT (renamed): /home/adhish/Productivity/AMSCUP/obsidianVault/LitSurvey/lyuCameraLiDARIMU2025.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/03_Theory/Annotations_1.md (original target existed with different content)
PROCESSED: /home/adhish/Productivity/AMSCUP/obsidianVault/LitSurvey/weiOnlineLiDARcameraExtrinsic2024.md -> /home/adhish/Productivity/AMSCUP/docs/vAIlt/03_Theory/Weionlinelidarcameraextrinsic2024.md