# Dedup Map

Phase-1 deliverable per `docs/vault_ingestion_prompt.md` §5.

**Status: Groups A/B executed 2026-08-11**, confirmed by user. See `Migration_Changelog.md` for the executed list. Group C (verification-report cluster) deferred to Phase 2. `LibCrypt_Patcher*` left in place per user decision; `BSD_3-Clause_License.md`/`_1.md` archived as misfiled (not a true dedup) per user decision.

**Correction found during execution:** `03_Theory/Annotations_1.md` was initially included in Group B by filename-pattern match but is genuinely distinct content (different paper's annotations) — caught by diffing against the changelog's original source paths, reverted before commit. All other Group A/B pairs were verified content-identical (frontmatter-stripped diff) before archiving. This is a reminder that the `_N` suffix pattern is necessary but not sufficient evidence of duplication — always diff, never assume from the name.

Two duplicate mechanisms found in the vault, verified by diff, not assumed from filename similarity:

1. **Import-echo duplicates** (`_1`/`_2`/`_3` suffix): same body content, re-imported into Obsidian multiple times, each pass wrapping the previous file's content in a new YAML frontmatter block (`source:`, `date:`, `tags:`) on top of the old one. Confirmed via diff on `Config_Reference.md` vs `_1` and `Sensor_Visibility...md` vs `_2`: bodies are byte-identical, only frontmatter nesting differs. The **unsuffixed / least-nested file is canonical** (cleanest single frontmatter block); suffixed copies are pure frontmatter-accumulation noise.
2. **Cross-location duplicates**: same canonical source under `docs/*.md`, independently imported once into `docs/vAIlt/05_Implementation/` (via Obsidian import, `_`-normalized filename) and possibly again as a flat file under `docs/vAIlt/*.md`.

**Explicitly checked and ruled OUT as false positives** (similar names, diffed, confirmed distinct documents — do NOT merge):
- `docs/config_reference.md` / `docs/kradar_config.md` / `docs/kradar_config_reference.md` — three different write-ups of `config.py` from different working sessions (different structure, different emphasis). Each maps to its own vault import (`Config_Reference.md`, `KRadar_configpy_Reference.md`, `K-Radar_Configuration_Reference.md` respectively) — keep all three lineages separate in `05_Implementation`.
- `docs/noise_addition_analysis.md` (277 L) vs `docs/noise_addition_analysis_clean.md` (196 L) — diffed: not a formatting cleanup of the same content, the "clean" version restructures/re-summarizes the same ~12 papers differently (different section headers, condensed per-paper entries). Both carry unique information; treat as **complementary sources for `02_Literature/Literature_Survey.md`**, not a dedup pair. Cite both.

## Group A — Import-echo pairs in `05_Implementation/` (canonical = unsuffixed, archive the `_N`)

| Canonical (keep, path relative to `05_Implementation/`) | Archive (`_N` echoes) |
|---|---|
| `11_README_Requirements.md` | `11_README_Requirements_1.md` |
| `4_Visibility_Metric_Methodology__Recommendations.md` | `..._1.md` |
| `6_Smoke_Test_Scaffold.md` | `..._1.md` |
| `7_Verification_Test_Scaffold.md` | `..._1.md` |
| `Config_Reference.md` | `Config_Reference_1.md` |
| `Goals_And_Subgoals.md` | `Goals_And_Subgoals_1.md` |
| `Hermes_Multi-Agent_Workplan.md` | `Hermes_Multi-Agent_Workplan_1.md` |
| `KRadar_configpy_Reference.md` | `KRadar_configpy_Reference_1.md` |
| `K-Radar_Configuration_Reference.md` | `K-Radar_Configuration_Reference_1.md` |
| `K-Radar_Coordinate_Frame_Analysis_Report.md` | `..._1.md` |
| `K-Radar_Multi-Sensor_Visibility_Calculation_Formulas_and_Methodologies.md` | `..._1.md` |
| `K-Radar_Sensor_Visibility_Pipeline__Recommended_Methods_Theory__Implementation.md` | `..._1.md`, `..._2.md`, `..._3.md` |
| `K-Radar_Visibility_Analysis__Master_Task_Brief.md` | `..._1.md` |
| `K-Radar_Visibility_Pipeline__Debug_Data_Gathering__Web_Viewer.md` | `..._1.md` |
| `K-Radar_Visibility_Pipeline__Issue_Summary.md` | `..._1.md` |
| `K-Radar_Visibility_Visual_Verification__Web_UI_Specification.md` | `..._1.md` |
| `LibCrypt_Patcher.md` | `LibCrypt_Patcher_1.md` |
| `LibCrypt_Patcherreadmemd_-_Changelog.md` | `..._1.md` |
| `Orchestrator_Task_Implement_K-Radar_Visibility_Analysis_Pipeline.md` | `..._1.md` |
| `Prompt_K-Radar_Multi-Sensor_Visibility_Analysis_Table_Generator.md` | `..._1.md` |
| `Refined_SOULmd_Files__Unified_Perception_Framework_Dev_Team.md` | `..._1.md` |
| `Sensor_Noise_Modeling_for_Object_Detection_Sensor_Fusion_Test_Suites.md` | `..._1.md` |
| `Visibility_Metrics_Comparison_ELI15.md` | `..._1.md` |

**Note on `LibCrypt_Patcher*`**: content is unrelated to AMSCUP/K-Radar (appears to be a stray import from an unrelated project). Out of scope for the thesis-shaped restructure — recommend archiving both canonical and echo to `10_Archive/` rather than promoting into the new PARA structure, unless the user wants it kept for other reasons. **Flagging for user decision, not deciding unilaterally.**

## Group B — Import-echo pairs elsewhere

| Folder | Canonical | Archive |
|---|---|---|
| `02_Literature/` | `Sensor_Visibility__Identification_Metrics_for_K-Radar.md` | `_1`, `_2`, `_3` (three echoes — heaviest accumulation found) |
| `02_Literature/` | `Visibility_Calculation_Methods_Literature_Review_and_Analysis.md` | `_1.md` |
| `03_Theory/` | `Annotations.md` | `Annotations_1.md` |
| `03_Theory/` | `BSD_3-Clause_License.md` | `BSD_3-Clause_License_1.md` |
| `07_Writing/` | `Aggregated_Data__AMSCUP.md` | `Aggregated_Data__AMSCUP_1.md` |
| `10_Archive/` | `Building_From_Source.md` | `Building_From_Source_1.md` (already in Archive — no move needed, just note as resolved) |

`03_Theory/BSD_3-Clause_License.md`: a software license text, not a theory note — flag as **misfiled**, candidate for `10_Archive/` or deletion-from-vault-only (source untouched) rather than kept in `03_Theory`. User decision.

## Group C — Verification report cluster (6 copies, genuinely overlapping content, largest cluster)

| Path | Lines | Note |
|---|---|---|
| `test-bed/.../kradar/docs/verification_report.md` | 180 | **Longest — proposed canonical** |
| `test-bed/.../kradar/docs/verification/verification_report_t_9383e63a.md` | 170 | Near-duplicate, timestamped variant |
| `docs/verification_report_partial1.md` | 144 | Partial — check for unique content before archiving |
| `test-bed/.../kradar/docs/verification_report_part_testsdocs.md` | 126 | Partial, tests-focused |
| `docs/verification_report.md` | 127 | Repo-root-adjacent copy |
| `test-bed/.../kradar/docs/verification_report_part_ghostflag.md` | 119 | Also duplicated at `docs/vAIlt/verification_report_part_ghostflag.md` (byte-identical filename in both places — same file, confirm before archiving) |
| `test-bed/.../kradar/outputs/verification_report.md` | 60 | Shortest — likely an early/partial run log |
| `test-bed/.../kradar/docs/verification_report_partial1.md` | 17 | Near-empty stub |

**Not yet diffed pairwise** — six files with overlapping but not identical content (different lengths, different "part_" suffixes suggest they cover different sections/phases of verification, not simple re-saves). Per §5 rule this needs a real diff-and-fold pass (not a blind pick-longest) before merging into one `06_Results/Verification_Report.md`, since shorter files may hold unique phase-specific findings. Proposing this as a **Phase-2 task**, not resolved here — flagging the cluster, not yet producing a merge plan for it.

QA reports (`docs/qa/qa_report_t_c872701f.md` ↔ `02_Literature/QA_Report_for_task_t_c872701f_...md`, and `docs/qa/qa_report_t_fa484955.md` ↔ `05_Implementation/QA_Report_for_t_fa484955_...md`) are 1:1 already-imported pairs — same content, no dedup action needed beyond confirming byte-match, which is straightforward.

## Non-duplicate, needs no action

- `docs/config_reference.md`, `docs/kradar_config.md`, `docs/kradar_config_reference.md` — three distinct docs (see above).
- `docs/noise_addition_analysis.md`, `docs/noise_addition_analysis_clean.md` — complementary, not duplicate.

## Open questions for user before executing any `git mv`

1. **`LibCrypt_Patcher*` in `05_Implementation`** — unrelated content. Archive out of the thesis tree, or leave alone?
2. **`BSD_3-Clause_License.md` in `03_Theory`** — misfiled license text. Archive, or leave?
3. **Verification report 6-way cluster** — approve doing a full diff-and-fold merge in Phase 2 (into `06_Results/Verification_Report.md`, listing all 8 source paths under `## Source`), rather than a naive pick-longest?
4. Confirm scope: should Group A/B import-echo archiving (the clear-cut cases, ~28 files) proceed now, or bundled with Phase 2 work on `03_Theory`/`04_Design`/`05_Implementation`?

## Source

- `docs/vault_ingestion_prompt.md` §5
- Directory listings of `docs/vAIlt/*`, `docs/*.md`, `test-bed/src/Modules/robust_testing/kradar/**/*.md`
- `diff` verification on: `Config_Reference.md`/`_1`, `Sensor_Visibility...md`/`_2`, `docs/config_reference.md`/`kradar_config.md`/`kradar_config_reference.md`, `docs/noise_addition_analysis.md`/`_clean.md`
