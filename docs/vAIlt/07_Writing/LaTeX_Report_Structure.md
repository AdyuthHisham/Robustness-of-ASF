# LaTeX Report Structure

Structural analysis of `docs/Latex_Report/` (git submodule, **read-only** — nothing in this note is a request to edit it; breakages are documented for the user to fix in the submodule directly). Every claim below was verified against the actual files, not assumed from the task-inventory brief.

## Entry point and build

`thesis_report/Main.tex`, `\documentclass[12pt,a4paper,twoside,openright]{report}` — Chalmers M2 template (David Frisk 2018, updates through Krister Wolff Dec 2023). `\input{include/settings/Settings}` immediately after `\documentclass`. **No build system** — no Makefile, no `.latexmkrc`, no CI; manual `pdflatex Main.tex` only.

`\input` order (confirmed against `Main.tex`): frontmatter (Titlepage → Abstract → Preface → Acknowledgements → Acronyms → Nomenclature) → `\tableofcontents` / `\listoffigures` / `\listoftables` → **Introduction → Theory → Methods** → Results/Discussion/Conclusion (all three `\input` lines commented out — chapters fully written but hidden, commit `41f2e2c` "Hid results as it doesnt reflect the current status right now") → `\appendix` → `backmatter/Appendix_1` → `Lastpage`.

## Settings (`include/settings/Settings.tex`)

No custom `.cls`/`.sty` — everything lives in this one file. Confirmed: `geometry` with `inner=3cm, outer=3cm` margins; `hyperref` (all-black links per the template convention); `fancyhdr`; `\numberwithin` applied to equation/figure/table per chapter; `\setcounter{tocdepth}{5}` / `\setcounter{secnumdepth}{5}`; macros `\backgroundpic{x}{y}{img}` and `\tagtemp`; flags `\def\ThesisType{M}` (master-only) and `\def\InstitutionLocation{C}` (Chalmers-only), `\def\layout{2}` (two-sided). See `docs/Latex_Report/FLAGS_REVIEW.md` for the full flag-combination review.

## Other products in the same submodule

Root-level standalone documents (separate from `thesis_report/`): `planning_report.tex`, `planning_report_draft.tex`, `thesis_proposal.tex` — sharing a root `references.bib` and root `images/` (distinct from `thesis_report/figure/`). A Beamer slide deck under `PPT/` (`loadslides.tex`, `template.tex`) with its own `styles/*.sty` theme files (`beamerinnerthemeelegant.sty` etc.).

## Known breakages — confirmed, not fixed (submodule is read-only)

| Issue | Detail | Verified |
|---|---|---|
| Acronyms case mismatch | `Main.tex` does `\input{include/frontmatter/Acronyms}` but the file on disk is `include/frontmatter/acronyms.tex` (lowercase) | Confirmed — `ls include/frontmatter/` shows `acronyms.tex`; will fail `\input` on a case-sensitive filesystem |
| Bibliography disabled | `\usepackage[backend=bibtex,style=ieee,sorting=none]{biblatex}`, `\addbibresource{references.bib}`, `\printbibliography` all commented out in `Main.tex` — every `\cite{...}` renders `[?]` | Confirmed both lines commented; `include/backmatter/References.tex` exists on disk but is never `\input` anywhere |
| `.gitignore` inert | `docs/Latex_Report/.gitignore` is a single line: `*.aux *.log *.out *.toc *.lof *.lot *.pdf *.bak *.backup*` — space-separated on one line is one literal (non-matching) gitignore pattern, not 9 separate patterns | Confirmed via `cat -A` — one line, no newlines between extensions. Consequence confirmed: `tmpskbquucd.{aux,log,pdf}` are committed at the repo root |
| Fragile figure filenames | Colons in filenames break `graphicx`/`includegraphics` on some filesystems/tools | Confirmed **two** such files: `figure/2026-07-01-11:35:55-screenshot.png`, `figure/2026-07-01-11:38:58-screenshot.png` — both are the project's only two *live* (uncommented) figures, i.e. the fragile filenames are actually load-bearing, not dead weight |
| Backup clutter in `include/` | Stray editor/backup files alongside the real chapter files | Confirmed: `Introduction.tex.bak`, `Methods.tex.{backup,backup2,bak,before_clean}`, `Theory.tex.current_backup`, `test.tex`, `test_minimal.tex`, plus `test.log`/`test_minimal.log` |

## Figures — only two live, six commented-out placeholders

No `\graphicspath`; paths are relative to `thesis_report/` as `figure/...`.

| Label | File | Status |
|---|---|---|
| `fig:thesis_work_plan` | `Introduction.tex:74` | **Live** — `\includegraphics` active |
| `fig:test_suite_data_flow` | `Methods.tex:527` | **Live** — `\includegraphics` active |
| `fig:system_architecture` | `Methods.tex:22` | Commented out (`figure/system_architecture.pdf` doesn't exist yet) |
| `fig:fusion_pipeline` | `Methods.tex:375` | Commented out |
| `fig:kradar_weather` | `Results.tex:57` | Commented out — points at `figure/kradar_weather_mAP.pdf` |
| `fig:ablation_nuscenes` | `Results.tex:167` | Commented out |
| `fig:noise_sensitivity` | `Results.tex:243` | Commented out — points at `figure/noise_sensitivity.pdf` |
| `fig:qualitative` | `Results.tex:294` | Commented out — 4 sub-figures (`qual_clear/fog/rain/night.pdf`) |

All 8 labels exist with active `\caption`/`\label`, confirming the chapters were fully drafted before Results/Discussion/Conclusion were hidden — the commented figures aren't missing content, they're waiting on generated plots. Prior art: `docs/Latex_Report/figure_inventory.md`.

## Source

- `docs/Latex_Report/thesis_report/Main.tex`, `include/settings/Settings.tex`, `include/Introduction.tex`, `include/Methods.tex`, `include/Results.tex`
- `docs/Latex_Report/.gitignore`, `docs/Latex_Report/FLAGS_REVIEW.md`, `docs/Latex_Report/figure_inventory.md`
- `docs/Latex_Report` git log (commit `41f2e2c`)
