# Prompt: Consolidate all repo markdown into `docs/vAIlt` as a thesis-shaped Obsidian project

> Run this in a fresh Claude Code session from the repo root `/home/adhish/Productivity/AMSCUP`.
> Everything below is the instruction set. The inventory is pre-computed — verify it, don't re-derive it.

---

## Objective

Consolidate the markdown knowledge scattered across this repo into the Obsidian vault at `docs/vAIlt/`,
organised as a **thesis-shaped project structure** (Introduction → Literature Survey → Theory → Design →
Implementation → Results → Writing). Embed the rendered noise-inspection images. Analyse the LaTeX report
and produce a vault↔thesis mapping.

**Three hard constraints:**

1. **Never edit anything under `docs/Latex_Report/`.** It is a git submodule with its own history. Read-only.
2. **Never edit anything under `obsidianVault/`.** That is the user's separate personal research vault. Read-only cross-reference.
3. **Never delete a source `.md`.** Consolidation is additive. Superseded *vault* notes move to `docs/vAIlt/10_Archive/`; source docs under `docs/` stay where they are.

---

## 1. Source inventory

### 1a. `docs/*.md` — the canonical layer (~43 files, ~8,700 lines)

Priority reads:

| Path | What it holds |
|---|---|
| `docs/Black_Book.md` (69 L) | Canonical noise/corruption taxonomy per modality (LiDAR / Camera / Radar), each entry naming the effect and its source paper |
| `docs/Small_Brown_Book.md` (136 L) | The "Battle Plan": 5-step research methodology (baseline SF inference → visibility-based robust test sets → noise injection → comparative inference → metrics) + the 17-point rubric used to screen noise papers |
| `docs/VISIBILITY_FORMULAS_AND_METHODS.md` (514 L) | Per-sensor visibility math and methodology |
| `docs/COORDINATE_FRAME_ANALYSIS.md` (373 L) | K-Radar sensor coordinate frame analysis |
| `docs/aggregated_data.md` (525 L) | Aggregated literature/noise data tables |
| `docs/visibility_methods_literature_review.md` (285 L) | Visibility-metric literature review |
| `docs/sensor_noise_modeling_research.md` (169 L) | Sensor noise modelling research |
| `docs/k-radar-sensor-visibility-metrics.md` (306 L) | Per-sensor visibility metric definitions |
| `docs/k-radar-recommended-pipeline-summary.md` (257 L) | Recommended pipeline summary |
| `docs/kradar_methodology_comparison.md` (218 L) | Methodology comparison |
| `docs/noise_addition_analysis.md` (277 L) + `_clean` variant (196 L) | Noise addition analysis (dedupe these two) |
| `docs/kradar_task_brief.md` (371 L), `docs/kradar_task_full_spec.md` (75 L) | Master task brief + full spec |
| `docs/kradar_visibility_analysis_prompt.md` (499 L), `docs/kradar_visual_verification_spec.md` (477 L) | Analysis prompt spec, viewer verification spec |
| `docs/hermes_multiagent_workplan.md` (540 L), `docs/refined_souls.md` (421 L) | Multi-agent orchestration workplan, agent-persona definitions |
| `docs/00_orchestrator_kickoff_prompt.md` … `docs/08_readme_spec.md` | Staged orchestration series (plan → gap analysis → specs) |
| `docs/07_phase1..4_implementation_log.md` (118–217 L each) | Phase implementation logs |
| `docs/ALVIS_MIGRATION_PLAN.md` (188 L), `docs/pipeline_issues.md` (166 L) | Cluster migration plan, open issues |
| `docs/kradar_config.md`, `docs/kradar_config_reference.md`, `docs/config_reference.md` | Config references (three overlapping — dedupe) |
| `docs/verification_report.md`, `docs/verification_report_partial1.md`, `/verification_report.md` (repo root) | Verification reports (many near-duplicates repo-wide — see §5 dedup rule) |
| `docs/qa/qa_report_t_c872701f.md`, `docs/qa/qa_report_t_fa484955.md` | QA reviews of `aggregated_data.md` completeness |
| `docs/06_upgrade_roadmap.md`, `docs/06_smoke_tests_scaffold.md`, `docs/07_verification_tests_scaffold.md` | Roadmap + test scaffolds |

### 1b. `docs/lit_survey/noise_addition/` — Literature Survey primary source

~12 source PDFs with converted Markdown under `docs/lit_survey/noise_addition/markdown/`
(KITTI, K-Radar, LiRTest, BenchmarkingRobustness, CommonCorruption, 4D mmWave survey, and others).
**These are the primary input for `02_Literature/`.** Read the markdown conversions, not the PDFs.

### 1c. `docs/vAIlt/*.md` — flat working-report layer (~30 files, the active layer)

`noise-injection-design.md`, `noise-injection-implementation-report.md`, `-integration-report.md`,
`-param-sweep-report.md`, `-smoke-test-report.md`, `-taxonomy-revision-report.md`, `-design-verification.md`;
`frame-deletion-rng-desync-fix-report.md`, `frame-deletion-verification-report.md`,
`frame-deletion-vs-loss-complete-explainer.md`;
`loss-partial-aimsf-replacement-report.md`, `-verification.md`, `loss-partial-report-correction-log.md`,
`loss-partial-zeroout-visibility-diagnostic.md`;
`kradar-effects-audit.md`, `kradar-effects-verification.md`, `ldr128-usage-audit.md`,
`asf-training-inputs.md`, `aimsf-benchmark-comparison.md`, `radar-*-report.md`,
`verification_report_part_ghostflag.md`;
explainers: `bev-plot-axes-explainer.md`, `rdr_sparse-vs-pc100p-explainer.md`,
`camera-gaussian-noise-resolution.md`;
`docs/vAIlt/Daily/2026-07-21.md`.

### 1d. `docs/vAIlt/0X_*/` — the existing PARA tree (extend it, don't replace it)

`00_Inbox`, `01_Project_Management`, `02_Literature`, `03_Theory`, `04_Design`, `05_Implementation`,
`06_Results`, `07_Writing`, `08 Resources`, `09_References`, `10_Archive`.
Indexed by `docs/vAIlt/00_MOC.md` (Master Map of Contents), which links folder-index notes via piped
wikilinks: `[[02 Literature|02_Literature/02 Literature.md]]`. Migration history in
`docs/vAIlt/00_Inbox/Migration_Changelog.md`.

**Known problem to fix:** `05_Implementation/` is full of import duplicates with `_1`/`_2`/`_3` suffixes
(e.g. `Config_Reference.md` / `Config_Reference_1.md`). These are copies of `docs/*.md` files. Dedupe per §5.

### 1e. `test-bed/src/Modules/robust_testing/kradar/`

`architecture.md` (421 L), `api_contracts.md` (584 L), `PHASE1_ANALYSIS.md` (308 L),
`PHASE2_ROADMAP.md` (333 L), `README_projection.md` (150 L), `README.md` (110 L), `AGENTS.md` (80 L),
`task_conditioned_normalization_strategy.md` (180 L), `TESTING_NOTES.md` (46 L),
`docs/verification_report.md`, `docs/verification/verification_report_t_9383e63a.md`,
`docs/verification_report_part_testsdocs.md`, `docs/verification_report_part_ghostflag.md`,
`docs/output_schema_fix.md`, `outputs/output_seq2_full_investigation.md` (366 L),
`outputs/verification_report.md`.

### 1f. Read-only cross-reference

`obsidianVault/Knowledge/**` — hand-curated distillations (`CFAR_Vectorization.md`,
`OS1-128-Coverage-Deficit*.md`, `Verification/`). Read them to learn the house writing style and to
check whether a distillation already exists. **Do not write there.**

### 1g. Excluded

`**/venv/`, `**/.pytest_cache/`, `node_modules`, `.git`, all submodule internals except the two
explicit read targets (`docs/Latex_Report/thesis_report/`, `repos/K-Radar/outputs/noise_visual_inspection/`),
`docs/Adyuth_Hisham_resume_PartTime.docx.md`, `test-bed/my_README.md`.

---

## 2. Target structure

Extend the **existing** numbered PARA folders under `docs/vAIlt/`. Do not create a parallel tree.

| Folder | Receives |
|---|---|
| `01_Project_Management` | Battle plan (from `Small_Brown_Book.md`), roadmaps, `ALVIS_MIGRATION_PLAN`, phase implementation logs, orchestration series |
| `02_Literature` | **Literature Survey** — one note per paper from `lit_survey/noise_addition/markdown/`, plus synthesis notes and the 17-point paper-screening rubric |
| `03_Theory` | Sensor principles, noise/degradation models, visibility formulas, coordinate frames |
| `04_Design` | Noise taxonomy (from `Black_Book.md`), system architecture, API contracts, output schema |
| `05_Implementation` | Pipeline modules, config references, effect implementations — **plus dedupe the `_1`/`_2`/`_3` copies already here** |
| `06_Results` | Verification reports, param sweeps, audits, **noise visual inspection gallery** |
| `07_Writing` | **Introduction**, LaTeX structure analysis, vault↔thesis mapping, figure inventory, gaps |
| `09_References` | Bib keys, dataset references |
| `10_Archive` | Superseded vault notes (moved, never deleted) |

**Two notes are explicitly required as real synthesized prose, not link dumps:**

- `docs/vAIlt/07_Writing/Introduction.md` — background, problem statement, research questions, scope,
  document structure. Written from `README.md`, `Small_Brown_Book.md`, `kradar_task_brief.md`, and
  `docs/Latex_Report/thesis_report/include/Introduction.tex`.
- `docs/vAIlt/02_Literature/Literature_Survey.md` — a genuine survey: organise the ~12 papers by theme
  (corruption benchmarks / sensor noise models / visibility metrics / fusion robustness), state what each
  contributes, where they disagree, and what gap this project fills. Link out to the per-paper notes.

---

## 3. Conventions

Match what the vault already does — verify against existing notes before writing:

- **First line is an H1 title.** No YAML frontmatter (neither vault uses it for hand-written notes).
- **Wikilinks use vault-relative paths:** `[[03_Theory/Visibility_Formulas]]`, not bare names.
- **House style is evidence-first.** Bold labels (`**Root cause**:`, `**Evidence**:`, `**Result:**`),
  claim-vs-verified tables with ✓/✗/⚠️ status columns, `file:line` citations, concrete numbers.
  No hedging prose where a number exists.
- **Every derived note ends with a `## Source` section** listing the repo-relative paths it was built from.
  This is the audit trail that makes deduplication safe and reversible.
- Update `docs/vAIlt/00_MOC.md` to index new notes, and append a dated entry to
  `docs/vAIlt/00_Inbox/Migration_Changelog.md` describing what moved where.
- Tags: only `02_Literature/` notes carry tags, following the existing hierarchical scheme
  (`#autocalib/method/...`, `#ReferPaper`, `#important`). Leave other folders untagged.

---

## 4. Images — reference in place

Source: `repos/K-Radar/outputs/noise_visual_inspection/` — 156 PNG, 3 frames × 3 modalities × ~15 renders.
**Do not copy them.** They regenerate; copies drift.

**Obsidian constraint:** the vault root is `docs/vAIlt/`, so `../../repos/...` falls outside the vault and
will not render. Create a symlink first:

```bash
mkdir -p docs/vAIlt/_assets
ln -s ../../../repos/K-Radar/outputs/noise_visual_inspection \
      docs/vAIlt/_assets/noise_visual_inspection
```

Then embed as: `![[_assets/noise_visual_inspection/frame_seq001_rdr033/lidar/lidar_gaussian_noise_high.png]]`

### Image grammar (pre-computed — use it, don't re-list the directory)

Three frame directories:

| Dir | seq | rdr idx | lidar idx | cam idx |
|---|---|---|---|---|
| `frame_seq001_rdr033` | 1 | 33 | 1 | 2 |
| `frame_seq021_rdr015` | 21 | 15 | 11 | 34 |
| `frame_seq048_rdr035` | 48 | 35 | 30 | 89 |

Each contains `camera/`, `lidar/`, `radar/` with 15 PNG apiece.
Filename grammar: `<modality>_<effect>[_<severity>].png`, severity ∈ `low|medium|high`
(bare name = the v2 single-level render).

Effects per modality:
- **camera, lidar:** `clean`, `frame_deletion`(+3), `frame_deletion_random`, `gaussian_noise`(+3), `loss_partial`(+3), `loss_complete`
- **radar:** same, except `noise_induced_shifts`(+3) replaces `gaussian_noise` (radar corruption is a per-point coordinate shift, not additive intensity noise)
- `loss_complete` has **no** severity variants by design

Plus `loss_partial_zeroout_diagnostic/` — 7 PNG per frame (`*_DEFAULT_before.png` / `*_FIXED_after.png`
pairs, and a 3-panel `camera_clean_vs_loss_partial_vs_loss_complete.png`).

### Deliverable: `docs/vAIlt/06_Results/Noise_Visual_Inspection.md`

Per-effect severity ladders (low → medium → high side by side), and for each effect **state the actual
parameter values**, not just the images. Read them from:

- `effect_parameters.yaml` (v2 single-level) and `severity_parameters.yaml` (v3 ladder), global `seed: 42`
- Known values to verify: camera gaussian σ = 1 / 40 / 50; lidar gaussian σ_xy/σ_z = 0.01/0.01, 0.5/0.2, 1.0/1.0;
  radar `noise_induced_shifts` shift_std = 0.01 / 1.0 / 5.0; `loss_partial` zeroed fraction = 0.1 / 0.3 / 0.8;
  `frame_deletion_random` Bernoulli p = 0.1 / 0.5 / 0.9

Fold in these supporting docs from the same directory:
- `frame_deletion_severity_log.md` — realized Bernoulli outcomes; note it searched up to 25 alternate seeds
  for low/high to hit the statistically expected outcome (this is a methodological caveat worth surfacing)
- `v2_regeneration_confirmation.md` — byte-identity table, old vs new hashes
- `loss_partial_zeroout_diagnostic/before_after_counts.md` — row counts preserved (radar 150,000;
  lidar 60,601 / 73,569 / 48,209; camera 5,529,600 px), zeroed fraction ≈ 0.30 exactly for radar/lidar,
  0.3000–0.3023 for camera (per-pixel rounding). This is *why* `loss_partial` needs the zero-out BEV
  renderer: zeroed rows collapse to (0,0,0) rather than being removed.
- `file_manifest.json` — size + sha256_16 per file
- `index.html` — the existing v3 gallery; mirror its organisation

Cross-link every effect to its taxonomy entry in `04_Design/` and its parameter justification in
`06_Results/` (`noise-injection-param-sweep-report.md`).

---

## 5. Deduplication rule

The same content exists in up to four places: `docs/*.md` (canonical) → `docs/vAIlt/05_Implementation/*`
(imported, often `_1`/`_2` suffixed) → `docs/vAIlt/*.md` (flat working layer) → `obsidianVault/`
(hand-curated). Verification reports alone have ~6 near-identical copies.

For each cluster of duplicates:

1. Pick the **longest / most recent** as canonical.
2. Diff the others against it; fold in any unique content (don't drop a paragraph just because it's in a shorter copy).
3. List **all** copies under the canonical note's `## Source` section.
4. Move the non-canonical *vault* notes to `docs/vAIlt/10_Archive/` (git mv). Leave source files under
   `docs/` and `test-bed/` untouched.
5. Record the merge in `00_Inbox/Migration_Changelog.md`.

Produce `docs/vAIlt/00_Inbox/Dedup_Map.md` first — a table of `duplicate group → canonical → archived` —
and confirm it with the user before moving anything.

---

## 6. LaTeX analysis — read-only

Read `docs/Latex_Report/thesis_report/`. **Write nothing there.** Produce two notes in `07_Writing/`.

### 6a. `docs/vAIlt/07_Writing/LaTeX_Report_Structure.md`

Pre-computed facts — **verify each against the files, then document**:

- Entry: `thesis_report/Main.tex`, `\documentclass[12pt,a4paper,twoside,openright]{report}`
  (Chalmers M2 template, David Frisk 2018 / Wolff 2023), `\input{include/settings/Settings}` immediately after.
- `\input` order: frontmatter (Titlepage, Abstract, Preface, Acknowledgements, Acronyms, Nomenclature)
  → `\tableofcontents`/`\listoffigures`/`\listoftables` → Introduction, Theory, Methods →
  **Results, Discussion, Conclusion are commented out** (files fully written but hidden; commit `41f2e2c`
  "Hid results as it doesnt reflect the current status") → `\appendix`, `backmatter/Appendix_1`, `Lastpage`.
- Settings: no custom `.cls`/`.sty`; everything in `include/settings/Settings.tex` — geometry 3 cm margins,
  `hyperref` all-black links, `fancyhdr`, `\numberwithin` per chapter, `tocdepth`/`secnumdepth` = 5,
  macros `\backgroundpic{x}{y}{img}` and `\tagtemp`, flags `\ThesisType{M}` / `\InstitutionLocation{C}` /
  `\layout{2}`. See `FLAGS_REVIEW.md`.
- Other products in the same submodule: standalone `planning_report.tex`, `planning_report_draft.tex`,
  `thesis_proposal.tex` (root `references.bib` + root `images/`), and a Beamer deck under `PPT/`
  with `styles/*.sty`.
- **No build system** — no Makefile, no `.latexmkrc`, no CI. Manual `pdflatex Main.tex`.

**Known breakages — document them, do NOT fix them** (they're in a submodule; report to the user instead):

| Issue | Detail |
|---|---|
| Acronyms case mismatch | `Main.tex` does `\input{include/frontmatter/Acronyms}` but the file on disk is `acronyms.tex` — fails on a case-sensitive filesystem |
| Bibliography disabled | `\usepackage[backend=bibtex,style=ieee,sorting=none]{biblatex}`, `\addbibresource{references.bib}`, and `\printbibliography` are all commented out → every `\cite{...}` renders `[?]`. `include/backmatter/References.tex` exists but is never `\input` |
| `.gitignore` inert | All patterns are on one space-separated line, which git treats as a single literal pattern — it ignores nothing (hence `tmpskbquucd.{aux,log,pdf}` committed at root) |
| Fragile figure filenames | `figure/2026-07-01-11:35:55-screenshot.png` — colons break `graphicx` on some setups |
| Backup clutter in `include/` | `Introduction.tex.bak`, `Methods.tex.{bak,backup,backup2,before_clean}`, `Theory.tex.current_backup`, `test.tex`, `test_minimal.tex` |

**Figures:** no `\graphicspath`; paths relative to `thesis_report/` as `figure/...`. Convention:

```latex
\begin{figure}[H]
  \centering
  \includegraphics[width=0.9\linewidth]{figure/...}
  \caption{...}
  \label{fig:snake_case}
\end{figure}
```

Only **two live figures**: `fig:thesis_work_plan` (`include/Introduction.tex:74`) and
`fig:test_suite_data_flow` (`include/Methods.tex:527`). Placeholders with active `\caption`/`\label`
but commented-out `\includegraphics`: `fig:system_architecture` (Methods:22), `fig:fusion_pipeline`
(Methods:375), `fig:kradar_weather`, `fig:ablation_nuscenes`, `fig:noise_sensitivity`, `fig:qualitative`
(Results). Prior art to reuse and extend: `docs/Latex_Report/figure_inventory.md`.

### 6b. `docs/vAIlt/07_Writing/Vault_to_Thesis_Mapping.md`

A table: **vault note → thesis chapter → section → status (written / partial / gap) → notes**.

Chapter/section outline to map against (verify against the `.tex` files):

- **Ch.1 Introduction** — Background · Problem Statement · Research Questions · Scope and Objectives · Thesis Structure
- **Ch.2 Theory** — Sensor Principles (Camera; LiDAR; LiDAR Weather-Driven Degradation Modeling; Radar; IMU and GPS/RTK) · Sensor Noise and Degradation Models (Camera; LiDAR; Radar; Communication-Layer Modeling; Temporal Characteristics; Environmental Factors Summary; Existing Corruption Benchmarks) · Calibration Theory (Taxonomy; Targetless LiDAR-Camera; IMU-Camera; LiDAR-IMU; Evaluation Metrics) · Sensor Fusion Architectures (Fusion Levels; Advanced Paradigms; Notable Algorithms) · Perception under Adverse Weather (Weather Effects; Mitigation; Relevant Datasets) · Evaluation Metrics (Detection; Tracking; Calibration; Adverse Weather Robustness) · Summary · Visibility Calculation Methods (LiDAR; Camera; Radar; Theoretical Justification) — *note this last section sits after "Summary", which is an ordering bug worth flagging*
- **Ch.3 Methods** — System Architecture Overview · Sensor Specifications and Configuration (K-Radar Sensor Suite; Coordinate Frame Conventions; Visibility Calculation Methods; nuScenes Sensor Suite) · Data Synchronization · Calibration Procedure · Feature Extraction (Image; LiDAR; Radar) · Fusion Strategy · Availability-Aware Detection Head · Handling Adverse Conditions · Implementation Details · Experimental Setup (Datasets; Training Details; Data Flow of the Robust Test Suite) · Summary
- **Ch.4 Results** *(excluded from build)* — Quantitative Results · Ablation Studies · Sensor Degradation Analysis (Controlled Sensor Noise Injection; Complete Sensor Dropout) · Qualitative Analysis · Computational Performance · Summary
- **Ch.5 Discussion** *(excluded)* — Interpretation of Key Findings · Comparison with SOTA (BEVFusion; SAMFusion; ASF) · Limitations · Implications · Open Questions · Summary
- **Ch.6 Conclusion and Future Work** *(excluded)* — Conclusions · Future Work · Final Remarks

Add a column with a **ready-to-paste `\includegraphics` snippet** for the noise images that would fill
`fig:noise_sensitivity` and `fig:kradar_weather`, using paths relative to `thesis_report/` (the user copies
the PNG in themselves — you do not write to the submodule).

Bib keys in use, for `09_References/`: `lyuCameraLiDARIMU2025`, `liAutomaticTargetlessLiDAR2023`,
`multisensor2025`, `mai2022perception`, `paek2025availability`, `planning_report`.

---

## 7. Execution phases

Work in this order. Suggest a commit at each phase boundary.

1. **Inventory + dedup map** — produce `00_Inbox/Dedup_Map.md`; confirm with the user before any `git mv`.
2. **Theory / Design / Implementation** — `03_Theory`, `04_Design`, `05_Implementation`; execute the dedup.
3. **Literature Survey** — `02_Literature/` per-paper notes + `Literature_Survey.md` synthesis.
4. **Introduction + Results** — `07_Writing/Introduction.md`, `06_Results/*` including the image gallery
   (create the `_assets` symlink here).
5. **LaTeX mapping** — `07_Writing/LaTeX_Report_Structure.md` + `Vault_to_Thesis_Mapping.md`.
6. **Index** — update `00_MOC.md`, append to `00_Inbox/Migration_Changelog.md`.

**Working rules:**

- Prefer `Read` over shelling out. Use `Explore` subagents only if context pressure demands it —
  the ~12 lit-survey paper conversions in `docs/lit_survey/noise_addition/markdown/` are the one place
  where fan-out is clearly worth it.
- **Invent nothing.** Every claim must trace to a source file. Where the sources leave a genuine hole,
  record it in `docs/vAIlt/07_Writing/Gaps.md` rather than writing filler prose.
- Where two sources contradict each other, say so explicitly in the note with both citations — do not
  silently pick one.
- Report at the end: notes created, notes archived, duplicates merged, gaps found, and the list of
  LaTeX breakages the user needs to fix in the submodule themselves.
