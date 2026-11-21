
---
### FIG-20260924-193343-claudeidx-toc-chapter-figure
**Status:** FINAL
**Supersedes:** N/A — first log entry for this figure (figure was created and iterated across several prior turns in this session before this logging system existed)
**Logged:** 2026-09-24T17:33:43Z by claudeidx
**Intended slide(s):** Slide 2, "Index" (table of contents) in Thesis_Presentation_Claude.odp
**Story-arc step served:** N/A — this is a navigational table-of-contents graphic, not a results/data figure. It does not serve a story-arc/finding step.

#### What the figure shows
- One-sentence takeaway: this is a visual table of contents — a two-column chain of 14 numbered circles (01-14), each linked to a short slide title, replacing a plain bulleted text list.
- Not a data plot: no axes, no series, no conditions/severities. Purely navigational/decorative.
- Content: left column = items 01-07 (Context: Reality Gap, Aim, Dataset: K-Radar, Availability-aware Sensor Fusion, Corruptions, Metrics, Experimental Setup); right column = items 08-14 (Results table, Findings, Discussion, Limitation/Open Questions, Future Work, ASF Robustness Study Summary, Conclusions). These 14 labels were given explicitly by the user (a deliberate subset of the deck's 24 slides, not auto-derived from slide titles this time).
- Nothing "excluded" in the data sense — N/A, no dataset involved.

#### Output files
- Embedded copy (the one actually used): internal ODF path `Pictures/1000000100000924000003E8E5BE7C0D.png` inside `/home/adhish/Productivity/AMSCUP/docs/Thesis_Presentation_Claude.odp`. Note: this file was originally written into the package as `Pictures/index_fig_2col.png`; LibreOffice's own save/convert path renamed it internally to the hash-style filename above at some point — content (pixel bytes) is unchanged, confirmed by matching sha256.
- Standalone copy (for reproducibility/inspection outside the odp): `/home/adhish/Productivity/AMSCUP/docs/images/index_toc_figure.png`
- Both files: PNG, RGBA, 2340×1000 px, no DPI metadata embedded (placed into the slide at 20.5cm × 8.761cm, i.e. ~289 px/cm ≈ 733 DPI effective at that placement size).
- sha256 (identical for both copies): `1877ea41f5f306f67a2c350a20d61038dc98ff4c0465ddcbdfa012b4caffb4be`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/figure_scripts/make_index_toc.py` — created by me (this agent) from scratch this session; not copied from an existing repo script. sha256 of script: `ee4e0037ea4d89226bd2dda2892fbe837a2aef8490ac5d09fcdf1b2fc4832509`.
- The script went through 3 in-place edits during this session (bottom-row clipping fix; connector-protrusion tangency fix; font-size increase 46→50pt / 34→40pt). Each edit was applied directly to the script and it was re-run; no separate versioned copies were kept of the intermediate states, only the final script state is preserved at the path above. This is a documentation gap for full step-by-step reproducibility — noted under Open issues.
- Exact command run (from repo root, no special env vars):
  ```
  python3 /home/adhish/Productivity/AMSCUP/docs/figure_scripts/make_index_toc.py
  ```
  (script writes its output to a hardcoded absolute path in its current form — a scratch path from this session, not the repo path above; anyone re-running it verbatim needs to edit the output path at the bottom of the script first. Flagged under Open issues.)
- Git commit hash of repo at generation time: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree was DIRTY — see `git status --porcelain` output captured at logging time (many unrelated unstaged/untracked files across the repo; notably `docs/Thesis_Presentation_Claude.odp` itself is untracked (`??`), so this figure's container file is not under version control at all yet).
- Python 3.14.7; Pillow (PIL) 12.3.0. No matplotlib/pandas/numpy/pyarrow/seaborn involved — pure PIL raster drawing.
- No random seeds/bootstrap/iteration counts — the figure is fully deterministic (fixed geometry, fixed text).

#### Data provenance
- N/A — no input dataset. This figure has no data source; all content (item numbers, labels, colors, layout) is hand-specified in the script per the user's explicit instruction, not derived from any parquet/CSV/table.
- No IoU threshold, classes, sequences, conditions, or severities apply.
- Every number shown on the figure is a slide-index ordinal (01-14), not a measurement — sourced directly from the user's message listing the 14 slide names in order.

#### Statistical reporting
- N/A — no statistics, no CIs, no grouped data, no N_rows/N_sequences. Not applicable to a navigational graphic.
- Figure/caption does not use the word "significant" anywhere.

#### Styling
- Shared plotting module used? No — this is not a data plot, so the `robust_testing/kradar/` shared plotting module does not apply. Built with raw PIL drawing (circles, tapered polygon connectors, text) to match the visual style of a user-supplied reference image.
- Colors used are the deck's own canonical palette established earlier in this session: accent blue `#2a6099`, dark navy `#194461`, white. Not the generic dataviz colorblind-safe palette from the dataviz skill — deliberately matched to the existing deck instead. Not independently checked for colorblind-safety as a foreground/background pair beyond the fact it's already used as body/title text color elsewhere in the deck.
- Font: Noto Sans Bold (matches deck-wide font choice), sizes 50pt-equivalent for numbers / 40pt-equivalent for labels (rasterized at script-internal pixel sizes 50px/40px, not literal pt — this is a raster image, not native ODF text, so "pt" doesn't directly apply; sizing was tuned by eye against the slide's other 11pt/32pt text via rendered PDF inspection, not computed from a shared scale).
- No title baked into the image itself (the slide's own "Index" title frame, native ODF text, sits above it and was left untouched).

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown — N/A, figure contains no metric values at all.
- [x] No camera `frame_deletion` conditions included — N/A, no corruption-condition data of any kind in this figure.
- [ ] No external/paper figures or images reused — PARTIAL CAVEAT: the *visual style/layout concept* (two-column chain of numbered circles with tapered connectors) was deliberately modeled on a stock PowerPoint template image the user provided: `/home/adhish/Downloads/61048-01-creative-table-of-contents-slide-template-16x9-1.webp`. No pixels, files, or assets from that image were copied or embedded — the figure was redrawn from scratch in code with the deck's own colors/fonts/text. Reuse-rights status of that source template = UNCONFIRMED (I did not check its license), but since none of its actual asset bytes are reused, only a generic "numbered circles in two columns with tapered connectors" layout idea, I believe this is not a reuse-rights concern — flagging per the checklist's instruction to always disclose this explicitly rather than assume.
- [x] Every number traced to a source file above — the 14 ordinals/labels trace directly to the user's chat message, not a data file (no data file exists for this figure).
- [x] Figure visually inspected after rendering — viewed the rendered PNG directly, and separately viewed it embedded in the actual slide via a 150 DPI PDF export/render at each of the three iterations (initial layout, protrusion fix, font-size increase).

#### Verification
- No numeric verification applicable (no data-derived numbers). Verified instead that: (a) all 14 requested labels appear, in the requested order, split 7/7 into the requested columns; (b) rendering inside the actual ODP slide (not just the standalone PNG) matches the standalone PNG, confirmed by re-exporting the slide to PDF and visually comparing after each edit; (c) no clipping/overflow at the final font size by full-slide render inspection.
- No comparison against `findings.md`, Q1-Q6 CSVs, or LaTeX thesis text applicable — this figure carries no findings/claims.

#### Open issues / caveats
- Script's hardcoded output path currently points into a session-scratch directory (`/tmp/claude-.../scratchpad/index_fig/index_fig.png`), not into the repo. To regenerate cleanly from the repo copy of the script, the output path at the bottom of `make_index_toc.py` should be edited to point at `docs/images/index_toc_figure.png` (or wherever it should canonically live) before running. I did not fix this because I was not asked to generalize the script, only to produce the figure — flagging as a decision the user may want made.
- Intermediate script states (before the protrusion fix and before the font-size increase) were not preserved as separate files, only edited in place — so the log's "how it was created" reflects the FINAL script only, not a literal replay of the 3 iterations. If exact iteration-by-iteration reproduction is needed, it is not possible from what's preserved.
- `docs/Thesis_Presentation_Claude.odp` is untracked in git (shows as `??` in `git status`) — there is no commit history to pin this figure's container file to; the sha256 values above are the only integrity anchor.
- The embedded picture's internal filename inside the ODF package silently changed from the name I originally gave it (`index_fig_2col.png`) to a LibreOffice-generated hash name (`1000000100000924000003E8E5BE7C0D.png`) at some point between edits, most likely when the file was processed by `soffice --headless --convert-to pdf` for a render check. Content is verified identical by sha256, but I flag this as a small surprise worth knowing about if anyone scripts around expected filenames inside this odp in future.
- I have not checked for any other agent's entries in this log file yet as of this write (first time I've touched this file this session) — no conflicting entries observed, but I only wrote one entry and did not exhaustively review the full file history.

---
### FIG-20260924-193126-claude-mainsession-metrics-primer-table
**Status:** DRAFT
**Supersedes:** N/A
**Logged:** 2026-09-24T19:31:26+02:00 by claude-mainsession
**Intended slide(s):** unassigned — general metrics-primer slide (candidate for a "how to read the results" slide)
**Story-arc step served:** corruption-sweep results (metric definitions primer, not a specific finding)

#### What the figure shows
- One-sentence takeaway: reference table defining AP, mATE, mASE, mAOE, Retention $R_b^c$, and CRI, what each measures, what an ideal value means, and whether higher or lower is better.
- Table image, 4 columns (Metric / What it measures / Ideal value meaning / Ideal: higher or lower), 6 rows. No axes, no data series, no class breakdown, no corruption conditions — this is a definitional glossary, not a results plot.
- Deliberately excludes: F1, churn rate, net retention (removed from an earlier draft at user's request); no numeric/empirical values shown at all, purely definitional text.

#### Output files
- /home/adhish/Productivity/AMSCUP/docs/images/metrics_summary_table.png, 1242x496 px, PNG (no explicit DPI metadata set by PIL; rendered at 1x from a 1242x496 canvas)
- sha256: 05fdf0ff8092435f533ddaca1450fd23df4c7bb11e399b5860c81a36608b86f1

#### How it was created
- Generating script: created fresh this session at /tmp/claude-1000/-home-adhish-Productivity-AMSCUP/1fca3503-63e7-4dc1-a294-88ee127365e5/scratchpad/make_table.py (scratchpad, not committed to repo). Not copied from an existing repo script.
- Iterated in-session: initial version had manual `\n` line breaks causing early wrapping; rewritten to auto-wrap text to each column's pixel width via PIL textbbox measurement; padding/margins subsequently tightened per user request.
- Command: `python3 /tmp/.../scratchpad/make_table.py` (system python3, not the uv-managed test-bed env — this script has no project dependency, uses only Pillow which is present in the system Python).
- Git commit at generation time: 9ca85c28928ac23012b89e4dd3816502b4a82236 (HEAD). Tree was dirty (see `git status --porcelain`); dirty files unrelated to this figure (CLAUDE.md, obsidianVault/*, docs/vAIlt/*, repos/K-Radar submodule pointer, test-bed radar_charts.py/config.py — none touched by this script). docs/images/ itself is untracked (new directory).
- Python 3.14.7 (system), Pillow 12.3.0. No matplotlib/numpy/polars involved — pure PIL drawing.
- No random seeds / no bootstrap — deterministic layout code.

#### Data provenance
- Not derived from any dataset. All cell text is hand-authored definitional content, cross-checked by the agent against `docs/Latex_Report/thesis_report/include/Methods.tex` lines 441-499 (§5, "Evaluation Metrics") for AP/mATE/mASE/mAOE/Retention/CRI formulas and "what it reveals" language.
- No filters/joins/aggregations — no tabular data pipeline involved.
- No numeric values are displayed on this figure (it is text-only), so there is nothing here requiring value-to-source tracing beyond the Methods.tex citations above.

#### Statistical reporting
- N/A — no data, no statistics, no CIs. Definitional table only.

#### Styling
- No shared plotting module used (Pillow direct-draw script, not matplotlib, not the `robust_testing/kradar` plotting module). Reason: this is a static reference table, not a data plot — no existing shared table-rendering utility exists in the repo, and the user asked to match a specific external reference image's visual style (Noto Sans font, navy/light-blue-gray palette) via a bespoke PIL script.
- Fonts: Noto Sans (Bold for labels/metric names, Regular for body), sourced from system fonts at /usr/share/fonts/noto/. Font sizes 17-21px in a 1242px-wide canvas — not evaluated against actual slide text size since this has not yet been placed into the .odp deck.
- Colorblind-safe palette: not formally checked; palette is navy-on-white/light-gray (no color-coded data series to distinguish), so colorblind-safety is largely moot for a text table.
- No title on the image itself (table has no embedded title/caption baked into the PNG; caption given separately in chat).

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown as validated results — mASE and CRI appear only as *definitions* ("what it measures" / "ideal value meaning"), never as computed numeric results, on this figure.
- [x] No camera `frame_deletion` conditions included — N/A, no conditions shown at all.
- [x] No external/paper figures or images reused — built from scratch; visual style modeled after a user-supplied reference image (an unrelated third-party AV-incident table screenshot, not a K-Radar/ASF figure), style only, no content/data reused.
- [x] Every number traced to a source — N/A, no numbers on this figure.
- [x] Figure visually inspected after rendering — yes, viewed via Read tool after each iteration.

#### Verification
- Verified metric formulas/definitions against `Methods.tex` §5 directly (quoted line ranges above) before drafting cell text. No numeric spot-check needed (no numbers shown).
- No discrepancy check needed against findings.md/CSVs — this figure carries no empirical values.

#### Open issues / caveats
- This is a DRAFT: not yet assigned to a specific slide number in `Thesis_Presentation_Claude.odp` — needs user placement decision.
- "Retention Rc_b" label is plain-text (no LaTeX-style subscript/superscript rendering) since PIL doesn't do math typesetting; user was told this in-session and did not request a fix. Flagging again here in case it matters for a defense slide.
- Table content (which metrics to include: AP/mATE/mASE/mAOE/Retention/CRI) reflects several rounds of ad hoc user edits in chat (add/remove F1, churn, net retention) — not a fixed methodology deliverable, just whatever the user last asked for. If this is meant to be the canonical metrics-primer slide, confirm this is the final intended metric set.

---
### FIG-20260924-193127-claude-mainsession-cri-by-effect-table
**Status:** DRAFT
**Supersedes:** N/A
**Logged:** 2026-09-24T19:31:27+02:00 by claude-mainsession
**Intended slide(s):** unassigned — candidate for CRI-results slide, corresponds to thesis Table 5.5
**Story-arc step served:** corruption-sweep results — CRI ranking of effects (§5.5/`sec:cri_results` of the thesis)

#### What the figure shows
- One-sentence takeaway: LiDAR Gaussian noise has by far the lowest CRI (least robust) of any effect for both classes; camera corruptions have the highest CRI (most robust).
- Table image, 3 columns (Effect / CRI sedan / CRI bus-truck), 6 rows, one per three-tier effect family (camera/lidar/radar x gaussian_noise/loss_partial). No axes — this is a direct visual transcription of thesis Table 5.5, not a new plot.
- Deliberately excludes: `loss_complete_zero` (single-tier, CRI undefined under the formula — per thesis text, not scored as spuriously stable) and `frame_deletion` for all three modalities (pipeline-crashing, not a usable corruption metric) — both consistent with the thesis's own exclusions for this table.

#### Output files
- /home/adhish/Productivity/AMSCUP/docs/images/cri_by_effect_table.png, 772x327 px, PNG
- sha256: 3dbd4b7ed5294d6ef295e93c4a7794997159cc6a6df750e79795f27fbea505d6

#### How it was created
- Generating script: /tmp/claude-1000/-home-adhish-Productivity-AMSCUP/1fca3503-63e7-4dc1-a294-88ee127365e5/scratchpad/make_cri_table.py — copied from make_table.py (FIG-...-metrics-primer-table) and modified: 3-column numeric layout instead of 4-column definitional layout, header/body alignment changed to center for numeric columns.
- Command: `python3 /tmp/.../scratchpad/make_cri_table.py` (system python3, Pillow only).
- Git commit at generation time: 9ca85c28928ac23012b89e4dd3816502b4a82236 (HEAD), tree dirty (see FIG-...-metrics-primer-table entry for the same dirty-file list; unrelated to this script).
- Python 3.14.7 (system), Pillow 12.3.0.
- No random seeds / deterministic layout code.

#### Data provenance
- NOT computed from source data by this agent in this session. All 6 CRI values (sedan/bus-truck for camera/lidar/radar x gaussian_noise/loss_partial) were transcribed verbatim from the already-finalized thesis table at `docs/Latex_Report/thesis_report/include/Results.tex` lines 444-459 (`\label{tab:cri_results}`), which the thesis text (line 442) states was itself computed "directly from the per-condition, per-class AP table" — that underlying computation is NOT re-verified in this session; this agent only reproduces the already-published table for a presentation slide.
- No filters/joins/aggregations performed in this session — transcription only.
- All 6 numeric values on the figure trace to Results.tex lines 451-456 (verbatim):
  camera_loss_partial: 0.936 / 0.929; camera_gaussian_noise: 0.915 / 0.842; lidar_loss_partial: 0.546 / 0.383; radar_loss_partial: 0.399 / 0.348; radar_gaussian_noise: 0.272 / 0.272; lidar_gaussian_noise: 0.106 / 0.153.

#### Statistical reporting
- N/A in this session — no CI recomputation performed; this agent did not re-touch the underlying per-condition AP table or its N/sequence counts. Whatever N-floor/reliability flagging the thesis applied when this table was originally produced is not reproduced or re-verified here.

#### Styling
- No shared plotting module used (same bespoke PIL script pattern as the metrics-primer table; see that entry for rationale).
- Fonts: Noto Sans (Bold/Regular), same as metrics-primer table. Not yet checked against actual slide font size.
- No title baked into the image; caption given separately in chat as: "Table: CRI by effect and class... (see thesis Table 5.5 caption)."

#### Integrity checks (HARD)
- [ ] No RCE, mASE, or CRI values shown as validated results — **FAILS AS STATED**: this figure's entire content IS CRI values, shown without any "exploratory/unvalidated" labeling on the image itself. Per the hard integrity rule referenced in the logging instructions ("CRI has known bugs" — asserted by the user's own logging-prompt template, not independently confirmed by this agent in this session), these values need explicit exploratory labeling or the user's explicit sign-off that this specific already-published Table 5.5 CRI computation is validated/exempt. **Flagging this as an open issue below rather than resolving it silently.**
- [x] No camera `frame_deletion` conditions included — confirmed excluded (see "What the figure shows").
- [x] No external/paper figures or images reused — built from scratch, transcribing this thesis's own already-published table only.
- [x] Every number traced to a source — yes, to Results.tex lines 451-456 (see Data provenance).
- [x] Figure visually inspected after rendering — yes.

#### Verification
- Verified by direct transcription cross-check: each of the 6 (effect, class) CRI values in the rendered image was compared side-by-side against Results.tex lines 451-456 during authoring. No independent recomputation from raw AP data was performed.
- No discrepancy vs. findings.md/CSVs checked in this session — out of scope of the chat request, which was "create a table image from this thesis table."

#### Open issues / caveats
- **OPEN QUESTION FOR USER:** the figure-provenance logging instructions state CRI has "known bugs" and that CRI values must not appear as validated results unless explicitly labeled exploratory. This figure reproduces the thesis's own already-finalized, already-defended Table 5.5 CRI values verbatim — it does not run any new CRI computation. Please confirm whether: (a) this already-published table is exempt from that rule since it's the thesis's own accepted result, not new exploratory output, or (b) this figure needs an "exploratory" label/caveat added before use in the defense deck, or (c) it should not be used at all pending the CRI bug being resolved. Not resolved silently — needs your decision.
- DRAFT status: not yet assigned to a slide number.

---
### FIG-20260924-193128-claude-mainsession-worst-cell-by-axis-table
**Status:** DRAFT
**Supersedes:** N/A
**Logged:** 2026-09-24T19:31:28+02:00 by claude-mainsession
**Intended slide(s):** unassigned — candidate for diversity-axis worst-case slide, corresponds to thesis Table 5.4
**Story-arc step served:** corruption-sweep results — single worst cell per diversity axis and class (`sec:diversity_axes_robustness` / Table 5.4 of the thesis)

#### What the figure shows
- One-sentence takeaway: LiDAR Gaussian noise is the single worst condition in nearly every diversity axis (weather, environment, time of day, distance, density) for both classes, except one bus/truck weather cell where `loss_complete_zero` (rain) is worst instead.
- Table image, 5 columns (Axis / Class / R_b^c / Drop / Worst condition (stratum)), 10 rows (5 axes x 2 classes). No plot axes — direct transcription of thesis Table 5.4.
- Deliberately excludes nothing extra beyond what the source table itself scopes: restricted to cells clearing the N>30 reliability floor, per the thesis table's own caption/methodology.

#### Output files
- /home/adhish/Productivity/AMSCUP/docs/images/worst_cell_by_axis_table.png, 1007x523 px, PNG
- sha256: c5ac4cf80f6d5487b101bd86d05a083c59cb1e23ee99ba2b3d31a876f74f89a8

#### How it was created
- Generating script: /tmp/claude-1000/-home-adhish-Productivity-AMSCUP/1fca3503-63e7-4dc1-a294-88ee127365e5/scratchpad/make_worst_cell_table.py — copied from make_cri_table.py (FIG-...-cri-by-effect-table) and modified: 5-column layout, mixed alignment (col 0/1/4 left, col 2/3 center-bold), wider rightmost column for the free-text "worst condition (stratum)" cells.
- Command: `python3 /tmp/.../scratchpad/make_worst_cell_table.py` (system python3, Pillow only).
- Git commit at generation time: 9ca85c28928ac23012b89e4dd3816502b4a82236 (HEAD), tree dirty — same unrelated dirty-file set as prior entries in this batch.
- Python 3.14.7 (system), Pillow 12.3.0. Deterministic, no seeds.

#### Data provenance
- NOT computed from source data by this agent. All 10 rows transcribed verbatim from `docs/Latex_Report/thesis_report/include/Results.tex` lines 420-429 (`\label{tab:max_drop_by_axis}`, Table 5.4), which the thesis text (line 408) states summarizes "the single most damaging cell (any modality, effect, and severity, including `loss_complete_zero`) identified within each diversity axis, for each class, restricted to cells clearing the N>30 reliability floor" — that underlying per-cell R_b^c computation and the N>30 filtering are NOT re-run or re-verified in this session.
- No filters/joins/aggregations performed in this session — transcription only.
- All 10 (axis, class) rows and their R_b^c / drop% / worst-condition-stratum values trace verbatim to Results.tex lines 420-429:
  Weather/Sedan 0.143/85.7%/lidar_gaussian_noise_high(normal); Weather/Bus-truck 0.000/100.0%/lidar_loss_complete_zero(rain,N=120);
  Environment/Sedan 0.003/99.7%/lidar_gaussian_noise_medium(parking lots); Environment/Bus-truck 0.000/100.0%/lidar_gaussian_noise_high(alleyway,N=164);
  Time of day/Sedan 0.202/79.8%/lidar_gaussian_noise_high(day); Time of day/Bus-truck 0.357/64.3%/lidar_gaussian_noise_high(night);
  Distance/Sedan 0.154/84.6%/lidar_gaussian_noise_medium(0-20m); Distance/Bus-truck 0.199/80.1%/lidar_gaussian_noise_high(60-75m);
  Density/Sedan 0.114/88.6%/lidar_gaussian_noise_high(bin 4+); Density/Bus-truck 0.281/71.9%/lidar_gaussian_noise_medium(bin 4+).

#### Statistical reporting
- N/A in this session for the N>30 floor / N_sequences check — inherited as-is from the thesis's own table (which per its own caption already restricts to N>30 cells); two rows explicitly carry their own N in the "worst condition" text (N=120, N=164) as given in the source table. No independent recomputation or CI method applied by this agent.

#### Styling
- No shared plotting module used (same bespoke PIL script family; see FIG-...-metrics-primer-table for rationale).
- Fonts: Noto Sans (Bold/Regular). Not yet checked against actual slide font size.
- No title baked into the image; caption given separately in chat.

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown as validated results — this table shows R_b^c (retention), not RCE/mASE/CRI.
- [x] No camera `frame_deletion` conditions included — none of the 10 rows reference `frame_deletion`.
- [x] No external/paper figures or images reused — built from scratch, transcribing this thesis's own already-published table only.
- [x] Every number traced to a source — yes, to Results.tex lines 420-429 (see Data provenance).
- [x] Figure visually inspected after rendering — yes.

#### Verification
- Verified by direct transcription cross-check: each of the 10 rows compared against Results.tex lines 420-429 during authoring. No independent recomputation from raw per-cell AP/R_b^c data performed in this session.
- No discrepancy vs. findings.md/CSVs checked in this session.

#### Open issues / caveats
- Same category of caveat as FIG-...-cri-by-effect-table: this is a verbatim reproduction of an already-finalized thesis table, not new analysis. R_b^c (unlike CRI) was not flagged as having known bugs in the logging instructions, so no exploratory-labeling conflict is raised here — but flagging for completeness that this agent did not independently re-derive the N>30 filtering or the underlying AP values behind these 10 cells.
- DRAFT status: not yet assigned to a slide number.

---
### FIG-20260924-193129-claude-mainsession-sedan-modality-retention-trend
**Status:** DRAFT
**Supersedes:** N/A
**Logged:** 2026-09-24T19:31:29+02:00 by claude-mainsession
**Intended slide(s):** unassigned — candidate replacement/companion for the pooled (both-class) version already in the thesis as `figure/modality_map_trend_single.pdf`
**Story-arc step served:** corruption-sweep results — modality-importance ordering (LiDAR most fragile, camera near-flat, radar intermediate), sedan class only

#### What the figure shows
- One-sentence takeaway: for sedan alone, LiDAR Gaussian noise causes a severity-laddered collapse in retention while camera stays near-flat and radar degrades gradually — same qualitative pattern as the pooled (both-class) thesis figure, now isolated to sedan.
- Line/scatter plot. X-axis: 7 flattened conditions (gaussian noise low/medium/high, partial loss low/medium/high, complete loss), grouped and shaded by corruption family. Y-axis: $R_b^c$ = corrupted mAP / sedan clean-baseline mAP (1.0 = no change), range 0-1.5. Three series (camera green circle, lidar blue square, radar red triangle), marker size proportional to sqrt(N), marker edge colored red if N <= 30 (reliability floor) else series color. Sedan class only (`cls == "sed"`) — bus/truck excluded by design (per this request).
- Deliberately excludes: `frame_deletion` (not a condition in this CONDITIONS list at all — matches upstream script's own exclusion), bus/truck class, and the plot title (removed per explicit user request this turn).

#### Output files
- /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/modality_map_trend_single_sedan.png — sha256: 0d38426d6f541d6d2a9929a307acf813bdf1f5b824f6db44b9bf8a3c90721167 — 989x540 px (matplotlib default 100 DPI-equivalent via `bbox_inches="tight"`, figsize 10x5.5in before tight-crop)
- /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/modality_map_trend_single_sedan.svg — sha256: 26f8de7461ee3b7c4ae154f887099c33bd1b7e77d309c121612f0c80b29a6d13 — vector, dimensions N/A (SVG)

#### How it was created
- Generating script: /tmp/claude-1000/-home-adhish-Productivity-AMSCUP/1fca3503-63e7-4dc1-a294-88ee127365e5/scratchpad/generate_modality_map_trend_sedan.py — copied from the existing repo script `docs/crossproduct_figures/generate_modality_map_trend_single.py` (this agent did NOT modify the original repo script in place; wrote a derivative copy instead) and modified:
  - Added `df = df.filter(pl.col("cls") == "sed")` immediately after the existing `ap_restricted_range.is_not_null()` filter, before computing the clean baseline or the per-condition aggregation.
  - Removed the `ax.set_title(...)` call (and its associated f-string) entirely, per explicit user request ("remove the title").
  - Changed print statements and output filenames/paths to `..._sedan.png/.svg` and updated the print label to "sedan clean baseline mAP" for clarity; no other logic changed.
  - Everything else (color/marker maps, CONDITIONS list, N_FLOOR=30, group-shading logic, line-break-at-family-boundary logic, marker sizing formula, verification assert block) is unchanged from the original script.
- Exact command run (from repo root `/home/adhish/Productivity/AMSCUP`):
  `uv run --project test-bed/src/Modules/robust_testing/kradar python3 /tmp/claude-1000/-home-adhish-Productivity-AMSCUP/1fca3503-63e7-4dc1-a294-88ee127365e5/scratchpad/generate_modality_map_trend_sedan.py`
- Git commit at generation time: 9ca85c28928ac23012b89e4dd3816502b4a82236 (HEAD). Tree dirty — `git status --porcelain` shows unrelated modified files (CLAUDE.md, obsidianVault/*, docs/vAIlt/.obsidian/workspace.json, obsidianVault/.obsidian/workspace.json, repos/K-Radar submodule pointer, docs/Latex_Report submodule pointer, test-bed/.../radar_charts.py, test-bed/.../kradar_visibility/src/kradar_visibility/config.py) plus untracked docs/images/ and docs/crossproduct_figures/ (this session's own outputs) — none of the dirty tracked files were read or used by this script.
- Environment (uv-managed `test-bed/src/Modules/robust_testing/kradar` project): Python 3.12.13, matplotlib 3.10.8, numpy 1.26.4, polars 1.39.3.
- No random seeds / no bootstrap in this script — it computes point estimates only (weighted mean AP per group), no CI resampling.

#### Data provenance
- Input: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/robustness_reports/crossproduct_v2/summary_full_density.parquet`
  sha256: 32ddb09ed69e8be29ec4e524ca1f5fd6c648598f4658a4284a5bac39efadfca5
  last-modified: 2026-09-01 11:21:32 +0200
- **DEVIATION FROM STATED CANONICAL SOURCE:** the logging instructions name `repos/K-Radar/scripts/alvis/outputs/row_table_iou03.parquet` as canonical. That exact file does not exist on this machine (`ls` confirms no such path under `repos/K-Radar/scripts/alvis/outputs/`) — consistent with prior project context that Alvis compute/outputs are permanently gone. This script therefore used `summary_full_density.parquet`, which is the same pre-aggregated source file the *original, already-published* `generate_modality_map_trend_single.py` reads from (its own header comment names this exact path) — i.e., this is the same input the pooled thesis figure itself was built from, not a new/different data source chosen by this agent.
- Pipeline (exactly as in the unmodified upstream script, with the one added `cls == "sed"` filter noted above):
  1. Read summary_full_density.parquet: 5347 rows total (all classes, all conditions).
  2. Filter `ap_restricted_range.is_not_null()`.
  3. Filter `cls == "sed"` (new, this session): 3615 rows remain (sedan only).
  4. Split into `clean` (condition == "original", 164 rows, n_total sum = 33177) and `corrupted` (condition != "original").
  5. Clean baseline mAP computed as GT-count-weighted mean of `ap_restricted_range` over the 164 clean rows = 75.754 (printed: "sedan clean baseline mAP = 75.754 (N=33177)").
  6. `corrupted` grouped by (modality, effect, severity), GT-weighted mean AP and summed n_total per group (21 groups: 3 modalities x 7 conditions).
  7. Per group, R_b^c = group mAP / clean baseline mAP; reliability flag = n_total_sum > 30 (all 21 sedan groups have n_total_sum in the ~31,500-33,300 range, i.e. all far above the N=30 floor — no group in this sedan-only plot is reliability-flagged).
- Every number on the figure (7 x-axis groups x 3 modality series = 21 plotted points) traces to the group-by output above; spot values queried directly this session, e.g. camera/gaussian_noise/high mAP=74.32 (n=33215), radar/gaussian_noise/medium mAP=64.27 (n=31529) — full 21-row table was queried and inspected, not just these two.
- In-script self-check: the script asserts its aggregated value for (lidar, gaussian_noise, low) matches an independently-filtered manual computation from the same source rows before plotting; this assert passed (printed "verification OK: lidar/gaussian_noise/low mAP=71.190").

#### Statistical reporting
- N_rows per plotted group: 21 groups (3 modalities x 7 flattened conditions), n_total_sum per group ranges roughly 31,500-33,300 (all comfortably above the N=30 floor; see Data provenance step 7). Exact per-group N not individually re-stated for all 21 here — full table was printed and inspected in-session but not saved to a persistent file; if exact per-point N is needed for the slide/appendix, re-run the query in this log's "Data provenance" step 6-7 SQL-equivalent.
- N_sequences per group: also queried (`n_sequences` summed per group) — ranged ~360-393 across the 21 groups, all far above the N_sequences>=10 sequence-confound floor mentioned in thesis methodology (§5, Evaluation Metrics, stratified-breakdown note). No group required flagging.
- CI method: **none applied** — this figure plots point-estimate R_b^c only (GT-weighted mean AP ratio), no bootstrap or Wilson interval, matching the unmodified upstream script's own behavior (it does not compute or plot CIs either). If the thesis defense requires CI bands on this figure, that is a further modification not made in this session.
- No groups fell below N=30 or N_sequences=10 in this sedan-only view, so no group required the red-reliability-outline styling to actually trigger (the styling logic is present in the script and would apply if a future rerun on a smaller data slice produced a low-N group).
- No use of the word "significant"/"significance" anywhere on the figure or its caption.

#### Styling
- No dedicated shared plotting module from `robust_testing/kradar` was used (no such module exists for this specific plot type in that project, per inspection of the upstream script's own imports — it uses matplotlib directly, this derivative does the same for consistency with the original).
- Colors: camera #1b7837 (green), lidar #2166ac (blue), radar #b2182b (red) — matplotlib hex codes, unchanged from upstream script. Not independently re-verified for colorblind-safety in this session (inherited as-is from the original, already-published figure's palette).
- Font sizes: matplotlib defaults except explicit fontsize=9 (group-family labels), fontsize=10-11 (series end-labels, "original" label) — unchanged from upstream, not evaluated against actual slide text size.
- Title: **removed** per this session's explicit user request (the one substantive change beyond the sedan filter).

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown as validated results — figure shows only mAP-derived $R_b^c$, no RCE/mASE/CRI.
- [x] No camera `frame_deletion` conditions included — `frame_deletion` is not in the CONDITIONS list (matches upstream script; confirmed by reading the CONDITIONS list, which only contains gaussian_noise/loss_partial/loss_complete_zero).
- [x] No external/paper figures or images reused — generated fresh from local parquet data this session.
- [x] Every number traced to a source — yes, all 21 plotted points trace to the summary_full_density.parquet group-by described under Data provenance; verified via the script's own built-in assert plus a follow-up interactive query in this session.
- [x] Figure visually inspected after rendering — yes, viewed via Read tool; confirmed title absent, sedan-only data (clean baseline printed as 75.754 vs. the pooled original's 73.99), same visual style as the reference pooled PDF otherwise.

#### Verification
- In-script assert (lidar/gaussian_noise/low manual-vs-aggregated match) passed: printed "verification OK: lidar/gaussian_noise/low mAP=71.190".
- Cross-checked the sedan clean-baseline mAP (75.754, N=33177) is higher than the pooled clean baseline shown in the existing thesis PDF (73.99, N=39977) and that 33177 + (implied bus/truck clean N) is consistent with a class split of the pooled N=39977 — not exactly re-derived bus/truck N in this session to confirm the arithmetic closes exactly (open item below).
- No discrepancy vs. findings.md/Q1-Q6 CSVs/LaTeX thesis text checked in this session beyond the pooled-vs-sedan baseline mAP sanity comparison above.

#### Open issues / caveats
- **Canonical-source deviation** (see Data provenance): used `summary_full_density.parquet` under `repos/K-Radar/outputs/...`, not the instructed canonical `repos/K-Radar/scripts/alvis/outputs/row_table_iou03.parquet`, because the latter does not exist locally. This matches what the *original, already-published* pooled figure's own script uses, so it is not a new/inconsistent choice — but flagging per the hard rule to say so explicitly rather than silently substituting.
- Did not independently re-derive bus/truck-only N to confirm 33177 (sedan) + bus/truck-clean-N == 39977 (pooled, from the existing PDF) exactly — a quick arithmetic sanity check, not done in this session. Low risk (both numbers come from the same parquet/pipeline) but not formally closed out.
- Exact per-group (modality x condition) N/n_sequences values were printed and inspected interactively but not saved to a durable file — if per-point N annotations are wanted on the slide itself (the pooled version doesn't show per-point N as text either, only via marker size), that would be a further script change.
- DRAFT status: not yet assigned to a slide number; no companion bus/truck-only version was requested or created in this session.

---
### FIG-20260924-193130-claude-mainsession-branch-exclusion-vs-zerofill-table
**Status:** DRAFT
**Supersedes:** N/A
**Logged:** 2026-09-24T19:31:30+02:00 by claude-mainsession
**Intended slide(s):** unassigned — candidate for the discussion/comparison-with-ASF-own-ablation slide, corresponds to thesis Table 6.1
**Story-arc step served:** ASF robustness claims — comparing this thesis's zero-fill complete-loss mechanism against ASF's own clean branch-exclusion ablation (`sec:` discussion around Table 6.1, Discussion.tex)

#### What the figure shows
- One-sentence takeaway: zero-filling a missing sensor (this thesis's `loss_complete_zero`) costs substantially more AP than ASF's own clean branch-exclusion for LiDAR specifically (6-13 percentage points worse), while radar and camera show small/inconsistent gaps between the two absence mechanisms.
- Table image with a 2-row grouped header (top: "ASF: branch exclusion" / "This thesis: zero-fill" each spanning 2 sub-columns; bottom: Sedan/Bus-truck under each group) x left label column "Sensor lost", 3 data rows (Radar, LiDAR, Camera). No plot axes — direct transcription of thesis Table 6.1.
- Deliberately excludes: nothing beyond the table's own 3-sensor, 2-class, 2-mechanism scope as published.

#### Output files
- /home/adhish/Productivity/AMSCUP/docs/images/branch_exclusion_vs_zerofill_table.png, 932x330 px, PNG
- sha256: 3e64d3e4b8ab614038b5c1b72e4a2cfb850787bce9bc333645335ad9d3a6d08b

#### How it was created
- Generating script: /tmp/claude-1000/-home-adhish-Productivity-AMSCUP/1fca3503-63e7-4dc1-a294-88ee127365e5/scratchpad/make_branch_exclusion_table.py — written fresh this session (not a copy of the prior 4-entry table scripts, though it follows the same visual-style conventions/color constants established in make_table.py). Needed a bespoke 2-row merged-header layout not supported by the simpler single-header-row scripts used for the other three table figures.
- One in-session bugfix: initial render had a stray vertical divider line cutting through the merged "ASF: BRANCH EXCLUSION" header text (divider was drawn full-height instead of stopping at the merged-cell boundary); fixed by only drawing the internal sedan/bus-truck divider (x-index 2 and 4) starting below the merged group-header row, not from the top of the table.
- Command: `python3 /tmp/.../scratchpad/make_branch_exclusion_table.py` (system python3, Pillow only).
- Git commit at generation time: 9ca85c28928ac23012b89e4dd3816502b4a82236 (HEAD), tree dirty — same unrelated dirty-file set as prior entries in this batch.
- Python 3.14.7 (system), Pillow 12.3.0. Deterministic, no seeds.

#### Data provenance
- NOT computed from source data by this agent. All 12 numeric cells (3 sensors x 2 mechanisms x 2 classes) transcribed verbatim from `docs/Latex_Report/thesis_report/include/Discussion.tex` lines 74-80 (`\label{tab:complete_loss_mechanism_comparison}`, Table 6.1). The ASF-side columns originate from ASF's own published Table 10 (`\cite{paek2025availability}`, per Discussion.tex line 68/72); the "this thesis: zero-fill" columns originate from this thesis's own `loss_complete_zero` results — neither side's underlying computation is re-run or re-verified in this session.
- No filters/joins/aggregations performed in this session — transcription only.
- All 12 values trace verbatim to Discussion.tex line 78-80:
  Radar: -3.9% / -12.0% (ASF sedan/bus-truck), -6.67% / -10.36% (this thesis sedan/bus-truck)
  LiDAR: -28.8% / -36.5% (ASF), -41.37% / -43.06% (this thesis)
  Camera: -0.8% / -1.0% (ASF), -3.06% / -0.81% (this thesis)

#### Statistical reporting
- N/A in this session — no CI recomputation performed on either side's numbers; this agent did not re-touch the underlying AP values or run counts behind either ASF's Table 10 or this thesis's own `loss_complete_zero` result.

#### Styling
- No shared plotting module used (bespoke PIL script, following the visual-style constants shared with the other table figures in this batch — same NAVY/LABEL_BG/Noto Sans choices).
- Fonts: Noto Sans (Bold for headers/labels/data cells — all data cells rendered bold in this table, unlike the metrics-primer table which mixed bold/regular). Not yet checked against actual slide font size.
- No title baked into the image; caption given separately in chat: "Table: Relative AP_BEV drop from full sensor availability (C+L+R) when one sensor is lost entirely — ASF's own clean branch-exclusion (Table 10) vs. this thesis's zero-filled loss_complete_zero, each relative to its own study's C+L+R baseline."

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown as validated results — this table shows relative AP_BEV percentage drops only.
- [x] No camera `frame_deletion` conditions included — this table concerns `loss_complete_zero` only, not `frame_deletion`.
- [ ] No external/paper figures or images reused — **PARTIAL:** the ASF-side two columns ("ASF: branch exclusion") are numeric values sourced from ASF's own published paper (Table 10, \cite{paek2025availability}), reproduced here as transcribed numbers (not a reused image/figure asset). Reuse-rights status for republishing ASF's own reported ablation numbers in a table alongside this thesis's own numbers = **UNCONFIRMED** — flagging per the hard integrity rule rather than assuming fair-use/citation is sufficient for a defense-deck slide.
- [x] Every number traced to a source — yes, to Discussion.tex lines 78-80 (see Data provenance).
- [x] Figure visually inspected after rendering — yes, including a re-check after the merged-header divider-line bugfix.

#### Verification
- Verified by direct transcription cross-check: all 12 cells compared against Discussion.tex lines 78-80 during authoring, both before and after the divider-line bugfix (bugfix was visual/layout only, did not touch data values).
- No discrepancy vs. findings.md/CSVs checked in this session.

#### Open issues / caveats
- **OPEN QUESTION FOR USER:** the ASF-side numbers are the competing paper's own reported ablation results (cited as \cite{paek2025availability} in the thesis), not this thesis's own data. Confirm this is fine to reproduce on a defense slide as a citation-backed comparison table (standard academic practice, and the thesis itself already does exactly this) — flagged per the logging template's reuse-rights checkbox rather than assumed.
- Same category of caveat as the other transcribed tables in this batch (FIG-...-cri-by-effect-table, FIG-...-worst-cell-by-axis-table): verbatim reproduction of an already-finalized thesis table, not new analysis in this session.
- DRAFT status: not yet assigned to a slide number.

---
### FIG-20260924-193406-claude-slidefigs-sedan-weather-normal
**Status:** FINAL
**Supersedes:** N/A — first logged entry for this figure (earlier un-logged transparent-bg / legend-removal / text-edit iterations in this same conversation were overwritten in place before this log existed; only the final state is logged, per no-retroactive-fabrication)
**Logged:** 2026-09-24T19:34:06+02:00 by claude-slidefigs
**Intended slide(s):** Findings slide 1 — "general trends" (unassigned slide number in .odp; user assembling this slide now)
**Story-arc step served:** corruption-sweep results — per-diversity-axis robustness (^c$), individual stratum panel cropped for slide use

#### What the figure shows
- Sedan robustness under all 21 corruption conditions, Weather=Normal stratum (individual panel cropped from the thesis's diversity-axes weather radar-chart family, Fig. 5.8).
- Plot type: polar/radar chart, one spoke per (modality, effect, severity) condition (21 spokes: camera/LiDAR/radar × {gaussian_noise low/med/high, loss_partial low/med/high, loss_complete_zero}). Radial axis = ^c$ = AP(corrupted)/AP(clean), range 0-1.15, gridlines at 0/.25/.5/.75/1. Class: Sedan (cls=sed). Spoke color = modality (camera green / LiDAR blue / radar red, from `docs/crossproduct_figures/palette.py::MODALITY_COLORS`). Per-modality mean-^c$ shown as a shaded arc across that modality's 7 spokes. Worst and second-worst robustness spokes ringed with dashed circles (`palette.py::RANK_COLORS`).
- Deliberately excluded: camera `frame_deletion` (excluded thesis-wide per 2026-08-25 decision, baked into `RADAR_AXIS_EFFECTS`/`SPOKES` in the source script — never in the 21-spoke set). No RCE/mASE/CRI shown.

#### Output files
- `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/sedan_weather_normal.png`
- 1716x1780 px, 200 DPI, transparent background (fig+axes patch alpha=0, `savefig(transparent=True)`)
- sha256: `82c3fa65da2bc8f610a0d24c67c6b036c2e48bcad3070340a7f629b3ceae4789`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py`, requesting stem `sedan_weather_normal` — **new script written this session**, not pre-existing. It is a single-panel adaptation of the thesis's actual multi-panel generator `docs/crossproduct_figures/generate_corruption_radar.py` (confirmed as the true source of thesis Figs. 5.8-5.21 via `docs/Latex_Report/thesis_report/include/Results.tex`).
- Adaptation method: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/_lib.py` is a byte-identical copy of `generate_corruption_radar.py` lines 1-259 (verified via `diff`) -- every function/constant (`compute_axis`, `AXES`, `SPOKES`, `MOD_RANGES`, `CIRCLE_STYLES`, color palette imports) unchanged, with only the trailing top-level `for axis_key ...` batch-generation loop (original lines 260-265) removed, since that loop unconditionally regenerates every thesis figure on import. `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/palette.py` is byte-identical to `docs/crossproduct_figures/palette.py` (sha256 `acfb5f38dbe4c5b923e3edf409c6cf2ff8787fef5dd95672bcacaaa573a626c2` matches both).
- `make_single.py`'s `make_single_panel()` reproduces `generate_corruption_radar.py::make_figure()`'s per-panel plotting logic (same mean-arc computation, same worst/second-worst ring logic, same tick/color logic) for exactly one (class, category) pair instead of a 2x2 grid. Per user instructions this session: per-panel title changed to "Axis - Category (Class)"; shared bottom legend removed entirely (logged separately as `radar_chart_legend.png`); background made transparent.
- Exact command (from `/home/adhish/Productivity/AMSCUP/test-bed`, no special env vars):
```
uv run --project . python /home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py
```
  (generates all 6 individual-panel figures in one run, including this one)
- Git commit at generation time: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree was DIRTY. Dirty/untracked files (abbreviated; full list was captured via `git status --porcelain` at generation time and is stable across all entries in this batch):
     M CLAUDE.md
     D docs/Adyuth_Hisham_resume_PartTime.docx.md
     M docs/Latex_Report
     M docs/vAIlt/.obsidian/workspace.json
     M obsidianVault/.obsidian/workspace.json
     M obsidianVault/Knowledge/asf-training-inputs.md
     M obsidianVault/Knowledge/robustness-metric-selection.md
     M obsidianVault/Projects/K-Radar/asf-corruption-study-alvis.md
     M obsidianVault/Projects/K-Radar/robustness-radar-charts.md
     M repos/K-Radar
     M test-bed/src/Modules/robust_testing/kradar/scripts/analysis/radar_charts.py
     M test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py
    ?? .agents/
    ?? FinalTerm_Presentation_Claude.odp
    ?? alvis_archive_2026-08-28/
    ?? backups/
    ?? docs/.master_presentation_figures.lock
    ?? docs/.~lock.Thesis_Presentation_Claude.odp#
    ?? docs/ASF_KRadar_Adversarial_Review.md
    ?? docs/ASF_Pipeline.backup.svg
    ?? docs/ASF_Pipeline.svg
    ?? docs/ASF_Pipeline_slide.svg
    ?? docs/ASF_Pipeline_v2.svg
    ?? docs/ASF_pipeline_cheatsheet.md
    ?? docs/FINAL_CHECK_LOG.md
    ?? docs/HUMANIZE_LOG.md
    ?? docs/Thesis_Presentation.odp
    ?? docs/Thesis_Presentation_Claude.odp
    ?? docs/crossproduct_figures/
    ?? docs/crossproduct_trends_and_anomalies.md
    ?? docs/crossproduct_trends_and_anomalies_metrics_coverage.md
    ?? docs/delete_/
    ?? docs/figure_scripts/
    ?? docs/images/
    ?? docs/lit_survey/ALVIS_URLs.txt
    ?? docs/lit_survey/asf.txt
    ?? docs/lit_survey/dataset/
    ?? docs/lit_survey/irl_corruptions/
    ?? docs/lit_survey/models/
    ?? docs/lit_survey/motivations/
    ?? docs/lit_survey/robust_benchmarks/
    ?? docs/master_presentation_figures.md
    ?? docs/regenerate_weather_figures_snow_fix.md
    ?? docs/slide_figures_findings1/
    ?? docs/thesis_defense_questions.md
    ?? docs/thesis_defense_questions_draft.md
    ?? docs/thesis_writing_bible.md
    ?? docs/trend_candidates.md
    ?? docs/vAIlt/06_Results/alvis-wipe-audit-2026-08-28.md
    ?? docs/vAIlt/06_Results/crossproduct-rebuild-20260901.md
    ?? docs/vAIlt/06_Results/distance-band-ap-and-churn-recompute-2026-09-04.md
    ?? docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md
    ?? docs/vAIlt/06_Results/frame-identifier-bug-fix-report.md
    ?? docs/vAIlt/06_Results/lidar-gaussian-noise-mechanism-phase1-audit-20260902.md
    ?? docs/vAIlt/06_Results/manual-code-vetting-checklist.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-audit-phase1-2026-08-31.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-bug-audit-2026-08-31.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31-corrected.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31.md
    ?? "docs/vAIlt/3-D LiDAR and Monocular Camera Calibration A Review.md"
    ?? "docs/vAIlt/3D Uncertainty Perspective-N-Points (PnP).md"
    ?? "docs/vAIlt/4D Radar-Camera Calibration and Auto-Labeling.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion_1.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving_1.md"
    ?? "docs/vAIlt/A 4D Radar-Camera Extrinsic Calibration Tool Based on 3D Uncertainty Perspective-N-Points.md"
    ?? "docs/vAIlt/A Continuous-Time Approach for 3D Radar-to-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/A Joint Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/A Low-Cost Temporal-Spatial Calibration Method for Radar and Camera Systems.md"
    ?? "docs/vAIlt/A Review of Environmental Perception Technology Based on Multi-Sensor Information Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A Review of Multi-Sensor Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A low-cost temporal-spatial calibration method for radar and camera systems_1.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and Robust 3D Object Detection in Adverse Conditions through Knowledge Distillation.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and robust 3D object detection in adverse conditions through knowledge distillation_1.md"
    ?? docs/vAIlt/AWARDistill.md
    ?? "docs/vAIlt/AdaptiveFusion LiDAR-Camera Adaptive Fusion for 3D Object Detection.md"
    ?? "docs/vAIlt/AdaptiveFusion Model.md"
    ?? "docs/vAIlt/Adverse Weather Perception.md"
    ?? "docs/vAIlt/Adverse-Weather Perception Robustness.md"
    ?? "docs/vAIlt/An Autonomous Extrinsic Calibration Method for 4D Millimeter-Wave Radar Point Clouds and Visual Images.md"
    ?? "docs/vAIlt/An Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/Anchor-Based 3D Detection.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion_1.md"
    ?? "docs/vAIlt/Automatic Targetless LiDAR-Camera Calibration A Survey.md"
    ?? "docs/vAIlt/Autonomous Driving Perception Safety Standardization.md"
    ?? "docs/vAIlt/Autonomous-Driving Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/Availability-aware Sensor Fusion via Unified Canonical Space.md"
    ?? "docs/vAIlt/BEVFormer (v1).md"
    ?? "docs/vAIlt/BEVFormer v2 Adapting Modern Image Backbones to Bird's-Eye-View Recognition via Perspective Supervision.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation_1.md"
    ?? "docs/vAIlt/Bird's-Eye View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View  3D Object Detection Architectures.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Recognition.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation_1.md"
    ?? "docs/vAIlt/Camera, LiDAR, and IMU Spatiotemporal Calibration Methodological Review and Research Perspectives.md"
    ?? "docs/vAIlt/Camera-Radar Fusion (HVDetFusion).md"
    ?? "docs/vAIlt/Center-Based Object Representation (points, not boxes).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking (CenterPoint).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking.md"
    ?? "docs/vAIlt/Continuous-Time Trajectory Representation.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey_1.md"
    ?? "docs/vAIlt/Deep (Feature-Level) Fusion.md"
    ?? "docs/vAIlt/Deep-Learning-Based Calibration Challenges.md"
    ?? "docs/vAIlt/Delving Into the Secrets of BEV 3D Object Detection in Autonomous Driving A Comprehensive Survey.md"
    ?? "docs/vAIlt/Doppler-Optical Flow Fusion Calibration.md"
    ?? "docs/vAIlt/EA-LSS Edge-Aware Lift-Splat-Shot Framework for 3D BEV Object Detection.md"
    ?? "docs/vAIlt/EA-LSS Edge-aware Lift-splat-shot Framework for 3D BEV Object Detection_1.md"
    ?? "docs/vAIlt/EPSM (Environmental Perception Safety Metric).md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/Early Fusion.md"
    ?? "docs/vAIlt/Echoes Beyond Points Unleashing the Power of Raw Radar Data in Multi-modality Fusion.md"
    ?? "docs/vAIlt/Exploring Radar-Camera Extrinsic Calibration A Deep Learning Perspective and Challenges.md"
    ?? "docs/vAIlt/External Multi-Modal Imaging Sensor Calibration for Sensor Fusion A Review_1.md"
    ?? "docs/vAIlt/External multi-modal imaging sensor calibration for sensor fusion A review.md"
    ?? "docs/vAIlt/Extrinsic 6DoF Calibration of a Radar-LiDAR-Camera System Enhanced by Radar Cross Section Estimates.md"
    ?? "docs/vAIlt/Extrinsic Calibration.md"
    ?? "docs/vAIlt/Extrinsic Sensor Calibration.md"
    ?? "docs/vAIlt/FUTR3D A Unified Sensor Fusion Framework for 3D Detection.md"
    ?? "docs/vAIlt/False Negative  False Positive Error Analysis.md"
    ?? "docs/vAIlt/Fast 3D Object Detection for 4D Imaging Radar Integrating Image Map Features Using Semi-Supervised Learning.md"
    ?? "docs/vAIlt/Fully Connected Pose Estimation (FCPE).md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework.md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework_1.md"
    ?? "docs/vAIlt/Image (Zotero item 6MQUAGUR).md"
    ?? "docs/vAIlt/Intrinsic Calibration.md"
    ?? "docs/vAIlt/Joint Extrinsic Calibration Tool (Radar-Camera-Lidar).md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions.md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions_1.md"
    ?? "docs/vAIlt/K-Radar Dataset.md"
    ?? "docs/vAIlt/Knowledge Distillation.md"
    ?? "docs/vAIlt/Late (Decision-Level) Fusion.md"
    ?? "docs/vAIlt/LiDAR-4D Radar Fusion.md"
    ?? "docs/vAIlt/LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Lift-Splat-Shoot Framework.md"
    ?? "docs/vAIlt/Linear Group RNN.md"
    ?? "docs/vAIlt/Low-Cost Temporal-Spatial Calibration.md"
    ?? "docs/vAIlt/MSAFusion Object Detection Based on Multisensor Adaptive Fusion Under BEV.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection_1.md"
    ?? "docs/vAIlt/MV2DFusion Model.md"
    ?? "docs/vAIlt/Meta-Information-Based Detection Error Analysis (univariate + Random ForestSHAP).md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance.md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance_1.md"
    ?? "docs/vAIlt/Millimeter-Wave Radar-Camera Fusion.md"
    ?? "docs/vAIlt/Minimally Connected Pose Estimation (MCPE).md"
    ?? "docs/vAIlt/Motion-Based Radar-to-Camera Extrinsic Calibration (velocity-based, targetless).md"
    ?? "docs/vAIlt/Multi-Modal Fusion Technology Based on Vehicle Information A Survey.md"
    ?? "docs/vAIlt/Multi-Sensor ExtrinsicTemporal Calibration.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (CameraLiDARRadar).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (Review Taxonomy).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception for Autonomous Driving A Review.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion in Automated Driving A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey_1.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection_1.md"
    ?? "docs/vAIlt/Object Detection in Autonomous Vehicles under Adverse Weather A Review of Traditional and Deep Learning Approaches.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online LiDAR-Camera Extrinsic Parameters Self-Checking and Recalibration.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_2.md"
    ?? "docs/vAIlt/OpenCalib A Multi-Sensor Calibration Toolbox for Autonomous Driving.md"
    ?? "docs/vAIlt/OpenCalib A Multi-sensor Calibration Toolbox for Autonomous Driving_1.md"
    ?? "docs/vAIlt/OpenCalib Toolbox.md"
    ?? "docs/vAIlt/Perception Methods for Adverse Weather Based on Vehicle Infrastructure Cooperation System A Review.md"
    ?? "docs/vAIlt/Perception and Sensing for Autonomous Vehicles Under Adverse Weather Conditions A Survey.md"
    ?? "docs/vAIlt/Perspective Supervision (auxiliary perspective-view detection loss).md"
    ?? docs/vAIlt/PointPillars.md
    ?? "docs/vAIlt/Pose and Structure Estimation (PSE).md"
    ?? "docs/vAIlt/Query-Based Multi-Modal Fusion (FUTR3D).md"
    ?? "docs/vAIlt/RADIATE A Radar Dataset for Automotive Perception in Bad Weather.md"
    ?? "docs/vAIlt/RADIATE Dataset.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network_1.md"
    ?? "docs/vAIlt/RLCNet An End-to-End Deep Learning Framework for Simultaneous Online Calibration of LiDAR, RADAR, and Camera_1.md"
    ?? "docs/vAIlt/RLCNet An end-to-end deep learning framework for simultaneous online calibration of LiDAR, RADAR, and Camera.md"
    ?? "docs/vAIlt/RLCNet Model.md"
    ?? "docs/vAIlt/Radar Cross Section-Enhanced Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey_1.md"
    ?? "docs/vAIlt/Radar-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar-Camera Fusion Taxonomy (whywhatwherewhenhow to fuse).md"
    ?? "docs/vAIlt/Radar-Camera Fusion for Object Detection and Semantic Segmentation in Autonomous Driving A Comprehensive Review.md"
    ?? "docs/vAIlt/Random Forest + Shapley Value Feature Importance.md"
    ?? "docs/vAIlt/Reprojection-Error-Based Extrinsic Calibration.md"
    ?? "docs/vAIlt/Resilient Object Detection for Autonomous Vehicles Integrating Deep Learning and Sensor Fusion.md"
    ?? "docs/vAIlt/Resilient object detection for autonomous vehicles Integrating deep learning and sensor fusion in adverse conditions.md"
    ?? "docs/vAIlt/Review on Millimeter-Wave Radar and Camera Fusion Technology.md"
    ?? "docs/vAIlt/Robustness of Perception under AdverseCorrupted Conditions.md"
    ?? "docs/vAIlt/Robustness-Aware 3D Object Detection in Autonomous Driving A Review and Outlook.md"
    ?? "docs/vAIlt/SACM Dialectical Safety Assurance Case.md"
    ?? "docs/vAIlt/Safe Autonomous Driving in Adverse Weather Sensor Evaluation and Performance Monitoring.md"
    ?? "docs/vAIlt/Safety Assurance for Perception Systems (standardization, metrics, safety cases).md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset.md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset_1.md"
    ?? "docs/vAIlt/Semi-Supervised 4D Radar Object Detection with Image-Map Features.md"
    ?? "docs/vAIlt/Sensor Evaluation and Performance Monitoring in Adverse Weather.md"
    ?? "docs/vAIlt/Simultaneous Online Multi-Sensor Calibration.md"
    ?? "docs/vAIlt/Single Joint Calibration Target Design (radar+camera+lidar).md"
    ?? "docs/vAIlt/Static Multitarget-Based Autocalibration of RGB Cameras, 3-D Radar, and 3-D Lidar Sensors.md"
    ?? "docs/vAIlt/Strong-Fusion  Weak-Fusion Taxonomy (earlydeeplateasymmetry-fusion).md"
    ?? "docs/vAIlt/Systematic Multi-Modal Sensor Calibration.md"
    ?? "docs/vAIlt/Target-Based Calibration.md"
    ?? "docs/vAIlt/Targetless (Target-Free) Calibration.md"
    ?? "docs/vAIlt/Targetless LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar\342\200\223Camera Calibration via Trajectory Alignment.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration of Radar and Camera for Intelligent Transportation Systems.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System_1.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization Progress, Research Advances, and Perspectives.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization, Progress, Research Advances.md"
    ?? "docs/vAIlt/Towards Robust 3D Object Detection with LiDAR and 4D Radar Fusion in Various Weather Conditions.md"
    ?? "docs/vAIlt/Towards Serious Perception Sensor Simulation for Safety Validation of Automated Driving A Collaborative Approach.md"
    ?? "docs/vAIlt/Two-Stage BEV Detector (perspective proposals + BEV head).md"
    ?? "docs/vAIlt/Two-Stage Point-Feature Refinement.md"
    ?? "docs/vAIlt/UniLION Model.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs_1.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation_1.md"
    ?? "docs/vAIlt/UniTR Model.md"
    ?? "docs/vAIlt/V2X-Enabled Cooperative Safety Intelligence.md"
    ?? "docs/vAIlt/Vehicle-Infrastructure Cooperation System.md"
    ?? "docs/vAIlt/Virtual Points (Radar-to-LiDAR Densification).md"
    ?? docs/vAIlt/VoxelNet.md
    ?? "docs/vAIlt/Waymo Open Dataset.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/ZFusion Model.md"
    ?? "docs/vAIlt/_COMMUNITY_3D Detection Performance Influencing-Factor Analysis.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Calibration & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Fusion Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_AV Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather Perception Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather V2I Perception Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV  Center-Based 3D Detection Architectures.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV Fusion Frameworks Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_Cooperative & Query-Based BEV Fusion.md"
    ?? "docs/vAIlt/_COMMUNITY_Deep-Learning-Based Radar-Camera Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Extrinsic Calibration Methods (Targetless  Continuous-Time).md"
    ?? "docs/vAIlt/_COMMUNITY_General Multi-Sensor Fusion Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_LiDAR-Camera Calibration Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_Miscellaneous Image.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Modal Detection Benchmarks & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Sensor Extrinsic Calibration Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Object-Tracking-Based Online Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety & Robustness Assurance.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety Metrics & Evaluation.md"
    ?? "docs/vAIlt/_COMMUNITY_Robust 4D Radar-Camera Fusion under Adverse Weather.md"
    ?? "docs/vAIlt/_COMMUNITY_Safety Assurance Case (SACM) Methodology.md"
    ?? "docs/vAIlt/_COMMUNITY_Sensor Calibration Toolboxes & Reviews (duplicate snapshots).md"
    ?? "docs/vAIlt/_COMMUNITY_UniLION Model (isolated).md"
    ?? "docs/vAIlt/_COMMUNITY_Unified BEV Transformer & Adaptive Fusion Models.md"
    ?? docs/vAIlt/graph.canvas
    ?? docs/vAIlt/noise-injection-smoke-test-report.md
    ?? "docs/vAIlt/nuScenes A Multimodal Dataset for Autonomous Driving.md"
    ?? "docs/vAIlt/nuScenes A multimodal dataset for autonomous driving_1.md"
    ?? "docs/vAIlt/nuScenes Dataset.md"
    ?? graphify-out/
    ?? obsidianVault/Daily/2026-08-26.md
    ?? obsidianVault/Daily/2026-08-27.md
    ?? obsidianVault/Daily/2026-08-28.md
    ?? obsidianVault/Daily/2026-08-31.md
    ?? obsidianVault/Daily/2026-09-01.md
    ?? obsidianVault/Daily/2026-09-02.md
    ?? obsidianVault/Daily/2026-09-03.md
    ?? obsidianVault/Daily/2026-09-07.md
    ?? obsidianVault/Knowledge/asf-availability-told-not-aware.md
    ?? obsidianVault/Knowledge/asf-map-eval-mechanics.md
    ?? obsidianVault/Knowledge/asf-recovery-rate-and-fog-confound.md
    ?? obsidianVault/Knowledge/cri-computed-from-row-table.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-anomaly-addendum.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-frame-key-fix-20260901.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-phase1-audit.md
    ?? obsidianVault/Knowledge/frame-key-derivation-kradar.md
    ?? obsidianVault/Projects/K-Radar/asf-3d-ap-per-weather-2026-09-07.md
    ?? obsidianVault/Projects/K-Radar/context-radar-charts.md
    ?? obsidianVault/Projects/K-Radar/corruption-visual-gallery.md
    ?? obsidianVault/Projects/K-Radar/dataset-distribution-histograms.md
    ?? obsidianVault/Projects/K-Radar/exhaustive-crossproduct-phase2-progress.md
    ?? obsidianVault/Projects/K-Radar/frame-identifier-bug.md
    ?? obsidianVault/Projects/K-Radar/full-denormalized-exploratory-pass.md
    ?? obsidianVault/Projects/K-Radar/official-checkpoint-rerun-2026-08-26.md
    ?? obsidianVault/Projects/K-Radar/results-context-figures-session.md
    ?? obsidianVault/Projects/K-Radar/robustness-bar-charts.md
    ?? obsidianVault/Projects/K-Radar/robustness-metrics-tables.md
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/bar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/box_plots.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/build_denormalized_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/context_radar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct/
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/dataset_distributions.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/density_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_dumbbell_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts_by_modality.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_robustness_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/exploratory_passes.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/fpfn_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/heatmaps.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/merge_churn.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/pass4_stratifier_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/robustness_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_context.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_pass4.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_robustness_line_charts.py
- Python 3.12.13; matplotlib 3.10.8; numpy 1.26.4; polars 1.39.3 (via `uv run --project test-bed`)
- No bootstrap/random seed: ^c$ is a deterministic AP ratio, using K-Radar's unmodified 41-point interpolated AP evaluator (`ap_metrics.py::compute_ap_grouped`)

#### Data provenance
- Input: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond_weather_corrected.parquet`
  sha256: `d911e93691f2fae1b46d3782d408ea26f72629573f859cb56f07ea146bc6098d`, last modified 2026-09-23 16:44:37 +0200, 872,745 rows, 22 distinct conditions, classes {sed, bus}.
  **Canonical-path note:** the logging template names `repos/K-Radar/scripts/alvis/outputs/row_table_iou03.parquet` as canonical; that exact path doesn't exist (a deeper variant `repos/K-Radar/scripts/alvis/outputs/robustness_reports/row_table_iou03.parquet` does). Regardless it is not the correct input for this figure family: it's a per-detection row table consumed by an unrelated script (`test-bed/.../scripts/analysis/radar_charts.py`, severity-tier condition charts, not diversity-axis charts). The diversity-axis radar charts (Figs. 5.8-5.21 and this panel) come exclusively from the pre-aggregated `full_denormalized_table_22cond_weather_corrected.parquet` via `generate_corruption_radar.py` -- confirmed against `Results.tex`'s own figure references.
- Filter/agg chain (inside `compute_axis`, unchanged from `generate_corruption_radar.py`): (1) `df.filter(condition in {original} ∪ {spoke_condition(*s) for s in SPOKES})` -> subset to the 22 needed conditions; (2) `compute_ap_grouped(dff_all, group_by=["condition","cls","weather"])` -> AP + num_gt per (condition, class, category) cell; (3) per spoke, ^c$ = corrupted-AP / baseline-AP if both baseline num_gt >=30 and corrupted num_gt >=30, else NaN (gap in plotted line).
- IoU threshold: 0.3. Class: Sedan (cls=sed). Diversity-axis column: `weather`. Category plotted: `normal`. Severities: low/medium/high for gaussian_noise and loss_partial; single tier for loss_complete_zero.
- Baseline (`original` condition) for this panel: AP=76.93, num_gt=15988 (well above the N>=30 floor -- independently recomputed this session, see Verification)

#### Statistical reporting
- Baseline N reported above; per-corrupted-spoke N not individually enumerated in this session beyond the floor-check already performed inside `compute_axis` (sub-floor spokes become NaN gaps, never plotted as solid values).
- N_sequences: not computed separately this session -- `compute_ap_grouped` pools across all sequences present for this (condition, cls, category) cell in the parquet; sequence-level breakdown is UNVERIFIABLE from this session alone.
- CI method: none -- ^c$ is a point-estimate ratio; no bootstrap/CI shown, consistent with the original thesis figure.
- No sub-floor (N<30) group is plotted as a solid/trusted value on this panel.
- "Significant" is not used on this figure or its caption.

#### Styling
- Shared plotting module: `docs/crossproduct_figures/palette.py` (`MODALITY_COLORS`, `RANK_COLORS`) -- identical to every thesis radar chart.
- Font sizes tuned for a full single-panel chart (title 18pt, tick labels 15pt, y-tick 11pt); not yet checked against actual slide-deck text scale.
- Colorblind safety: not independently re-verified this session -- palette inherited unchanged from the thesis's own module.
- Title on plot: **yes** -- "Sedan robustness under all 21 corruption conditions, Weather=Normal stratum (individual panel cropped from the thesis's diversity-axes weather radar-chart family, Fig. 5.8)." -- deviates from the template's "default is no" convention; kept per explicit user instruction this session, since each panel is being cropped out of its original multi-panel context and needs its own label.

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown -- only ^c$ (AP ratio)
- [x] No camera `frame_deletion` conditions included -- confirmed absent from `RADAR_AXIS_EFFECTS`/`SPOKES` in `_lib.py`
- [x] No external/paper figures or images reused -- generated fresh from local parquet this session
- [x] Every number traced to source file above (baseline AP/num_gt independently recomputed, see Verification)
- [ ] Figure visually inspected after rendering -- **NOT satisfied.** Only file existence, PNG dimensions (via `identify`/PIL) and sha256 were checked this session; the rendered image was not opened/viewed. Flagging honestly rather than claiming a check that didn't happen.

#### Verification
- Independently recomputed the baseline (`original`, Sedan (cls=sed), `weather`=`normal`) AP/num_gt cell via a fresh `compute_ap_grouped` call in this session, separate from re-running the plotting script: AP=76.93, num_gt=15988.
- Not diffed against `findings.md`, Q1-Q6 CSVs, or the compiled LaTeX thesis PDF in this session -- this panel is a re-crop of the same underlying computation behind the corresponding published thesis figure (Fig. 5.8/5.9/5.10 family depending on axis), not a new number, but that equivalence has not been explicitly re-verified against the PDF this session.

#### Open issues / caveats
- Visual inspection of the rendered PNG was not performed this session (see unchecked Integrity item above) -- user should open the file before placing it on a slide.
- Canonical-path discrepancy noted above under Data provenance.
- Per-spoke N/coverage beyond the single baseline cell reported here was not enumerated for this panel in this session.

---
### FIG-20260924-193406-claude-slidefigs-sedan-time-day
**Status:** FINAL
**Supersedes:** N/A — first logged entry for this figure (earlier un-logged transparent-bg / legend-removal / text-edit iterations in this same conversation were overwritten in place before this log existed; only the final state is logged, per no-retroactive-fabrication)
**Logged:** 2026-09-24T19:34:06+02:00 by claude-slidefigs
**Intended slide(s):** Findings slide 1 — "general trends" (unassigned slide number in .odp; user assembling this slide now)
**Story-arc step served:** corruption-sweep results — per-diversity-axis robustness (^c$), individual stratum panel cropped for slide use

#### What the figure shows
- Sedan robustness under all 21 corruption conditions, Time-of-Day=Day stratum (individual panel cropped from the thesis's diversity-axes time-of-day radar-chart family, Fig. 5.10 area).
- Plot type: polar/radar chart, one spoke per (modality, effect, severity) condition (21 spokes: camera/LiDAR/radar × {gaussian_noise low/med/high, loss_partial low/med/high, loss_complete_zero}). Radial axis = ^c$ = AP(corrupted)/AP(clean), range 0-1.15, gridlines at 0/.25/.5/.75/1. Class: Sedan (cls=sed). Spoke color = modality (camera green / LiDAR blue / radar red, from `docs/crossproduct_figures/palette.py::MODALITY_COLORS`). Per-modality mean-^c$ shown as a shaded arc across that modality's 7 spokes. Worst and second-worst robustness spokes ringed with dashed circles (`palette.py::RANK_COLORS`).
- Deliberately excluded: camera `frame_deletion` (excluded thesis-wide per 2026-08-25 decision, baked into `RADAR_AXIS_EFFECTS`/`SPOKES` in the source script — never in the 21-spoke set). No RCE/mASE/CRI shown.

#### Output files
- `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/sedan_time_day.png`
- 1716x1780 px, 200 DPI, transparent background (fig+axes patch alpha=0, `savefig(transparent=True)`)
- sha256: `66ef521abc48e5037d96f0c2adac0dcd629797cc41b6a381bc74cf6361b2d4f6`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py`, requesting stem `sedan_time_day` — **new script written this session**, not pre-existing. It is a single-panel adaptation of the thesis's actual multi-panel generator `docs/crossproduct_figures/generate_corruption_radar.py` (confirmed as the true source of thesis Figs. 5.8-5.21 via `docs/Latex_Report/thesis_report/include/Results.tex`).
- Adaptation method: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/_lib.py` is a byte-identical copy of `generate_corruption_radar.py` lines 1-259 (verified via `diff`) -- every function/constant (`compute_axis`, `AXES`, `SPOKES`, `MOD_RANGES`, `CIRCLE_STYLES`, color palette imports) unchanged, with only the trailing top-level `for axis_key ...` batch-generation loop (original lines 260-265) removed, since that loop unconditionally regenerates every thesis figure on import. `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/palette.py` is byte-identical to `docs/crossproduct_figures/palette.py` (sha256 `acfb5f38dbe4c5b923e3edf409c6cf2ff8787fef5dd95672bcacaaa573a626c2` matches both).
- `make_single.py`'s `make_single_panel()` reproduces `generate_corruption_radar.py::make_figure()`'s per-panel plotting logic (same mean-arc computation, same worst/second-worst ring logic, same tick/color logic) for exactly one (class, category) pair instead of a 2x2 grid. Per user instructions this session: per-panel title changed to "Axis - Category (Class)"; shared bottom legend removed entirely (logged separately as `radar_chart_legend.png`); background made transparent.
- Exact command (from `/home/adhish/Productivity/AMSCUP/test-bed`, no special env vars):
```
uv run --project . python /home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py
```
  (generates all 6 individual-panel figures in one run, including this one)
- Git commit at generation time: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree was DIRTY. Dirty/untracked files (abbreviated; full list was captured via `git status --porcelain` at generation time and is stable across all entries in this batch):
     M CLAUDE.md
     D docs/Adyuth_Hisham_resume_PartTime.docx.md
     M docs/Latex_Report
     M docs/vAIlt/.obsidian/workspace.json
     M obsidianVault/.obsidian/workspace.json
     M obsidianVault/Knowledge/asf-training-inputs.md
     M obsidianVault/Knowledge/robustness-metric-selection.md
     M obsidianVault/Projects/K-Radar/asf-corruption-study-alvis.md
     M obsidianVault/Projects/K-Radar/robustness-radar-charts.md
     M repos/K-Radar
     M test-bed/src/Modules/robust_testing/kradar/scripts/analysis/radar_charts.py
     M test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py
    ?? .agents/
    ?? FinalTerm_Presentation_Claude.odp
    ?? alvis_archive_2026-08-28/
    ?? backups/
    ?? docs/.master_presentation_figures.lock
    ?? docs/.~lock.Thesis_Presentation_Claude.odp#
    ?? docs/ASF_KRadar_Adversarial_Review.md
    ?? docs/ASF_Pipeline.backup.svg
    ?? docs/ASF_Pipeline.svg
    ?? docs/ASF_Pipeline_slide.svg
    ?? docs/ASF_Pipeline_v2.svg
    ?? docs/ASF_pipeline_cheatsheet.md
    ?? docs/FINAL_CHECK_LOG.md
    ?? docs/HUMANIZE_LOG.md
    ?? docs/Thesis_Presentation.odp
    ?? docs/Thesis_Presentation_Claude.odp
    ?? docs/crossproduct_figures/
    ?? docs/crossproduct_trends_and_anomalies.md
    ?? docs/crossproduct_trends_and_anomalies_metrics_coverage.md
    ?? docs/delete_/
    ?? docs/figure_scripts/
    ?? docs/images/
    ?? docs/lit_survey/ALVIS_URLs.txt
    ?? docs/lit_survey/asf.txt
    ?? docs/lit_survey/dataset/
    ?? docs/lit_survey/irl_corruptions/
    ?? docs/lit_survey/models/
    ?? docs/lit_survey/motivations/
    ?? docs/lit_survey/robust_benchmarks/
    ?? docs/master_presentation_figures.md
    ?? docs/regenerate_weather_figures_snow_fix.md
    ?? docs/slide_figures_findings1/
    ?? docs/thesis_defense_questions.md
    ?? docs/thesis_defense_questions_draft.md
    ?? docs/thesis_writing_bible.md
    ?? docs/trend_candidates.md
    ?? docs/vAIlt/06_Results/alvis-wipe-audit-2026-08-28.md
    ?? docs/vAIlt/06_Results/crossproduct-rebuild-20260901.md
    ?? docs/vAIlt/06_Results/distance-band-ap-and-churn-recompute-2026-09-04.md
    ?? docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md
    ?? docs/vAIlt/06_Results/frame-identifier-bug-fix-report.md
    ?? docs/vAIlt/06_Results/lidar-gaussian-noise-mechanism-phase1-audit-20260902.md
    ?? docs/vAIlt/06_Results/manual-code-vetting-checklist.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-audit-phase1-2026-08-31.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-bug-audit-2026-08-31.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31-corrected.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31.md
    ?? "docs/vAIlt/3-D LiDAR and Monocular Camera Calibration A Review.md"
    ?? "docs/vAIlt/3D Uncertainty Perspective-N-Points (PnP).md"
    ?? "docs/vAIlt/4D Radar-Camera Calibration and Auto-Labeling.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion_1.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving_1.md"
    ?? "docs/vAIlt/A 4D Radar-Camera Extrinsic Calibration Tool Based on 3D Uncertainty Perspective-N-Points.md"
    ?? "docs/vAIlt/A Continuous-Time Approach for 3D Radar-to-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/A Joint Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/A Low-Cost Temporal-Spatial Calibration Method for Radar and Camera Systems.md"
    ?? "docs/vAIlt/A Review of Environmental Perception Technology Based on Multi-Sensor Information Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A Review of Multi-Sensor Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A low-cost temporal-spatial calibration method for radar and camera systems_1.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and Robust 3D Object Detection in Adverse Conditions through Knowledge Distillation.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and robust 3D object detection in adverse conditions through knowledge distillation_1.md"
    ?? docs/vAIlt/AWARDistill.md
    ?? "docs/vAIlt/AdaptiveFusion LiDAR-Camera Adaptive Fusion for 3D Object Detection.md"
    ?? "docs/vAIlt/AdaptiveFusion Model.md"
    ?? "docs/vAIlt/Adverse Weather Perception.md"
    ?? "docs/vAIlt/Adverse-Weather Perception Robustness.md"
    ?? "docs/vAIlt/An Autonomous Extrinsic Calibration Method for 4D Millimeter-Wave Radar Point Clouds and Visual Images.md"
    ?? "docs/vAIlt/An Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/Anchor-Based 3D Detection.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion_1.md"
    ?? "docs/vAIlt/Automatic Targetless LiDAR-Camera Calibration A Survey.md"
    ?? "docs/vAIlt/Autonomous Driving Perception Safety Standardization.md"
    ?? "docs/vAIlt/Autonomous-Driving Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/Availability-aware Sensor Fusion via Unified Canonical Space.md"
    ?? "docs/vAIlt/BEVFormer (v1).md"
    ?? "docs/vAIlt/BEVFormer v2 Adapting Modern Image Backbones to Bird's-Eye-View Recognition via Perspective Supervision.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation_1.md"
    ?? "docs/vAIlt/Bird's-Eye View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View  3D Object Detection Architectures.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Recognition.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation_1.md"
    ?? "docs/vAIlt/Camera, LiDAR, and IMU Spatiotemporal Calibration Methodological Review and Research Perspectives.md"
    ?? "docs/vAIlt/Camera-Radar Fusion (HVDetFusion).md"
    ?? "docs/vAIlt/Center-Based Object Representation (points, not boxes).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking (CenterPoint).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking.md"
    ?? "docs/vAIlt/Continuous-Time Trajectory Representation.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey_1.md"
    ?? "docs/vAIlt/Deep (Feature-Level) Fusion.md"
    ?? "docs/vAIlt/Deep-Learning-Based Calibration Challenges.md"
    ?? "docs/vAIlt/Delving Into the Secrets of BEV 3D Object Detection in Autonomous Driving A Comprehensive Survey.md"
    ?? "docs/vAIlt/Doppler-Optical Flow Fusion Calibration.md"
    ?? "docs/vAIlt/EA-LSS Edge-Aware Lift-Splat-Shot Framework for 3D BEV Object Detection.md"
    ?? "docs/vAIlt/EA-LSS Edge-aware Lift-splat-shot Framework for 3D BEV Object Detection_1.md"
    ?? "docs/vAIlt/EPSM (Environmental Perception Safety Metric).md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/Early Fusion.md"
    ?? "docs/vAIlt/Echoes Beyond Points Unleashing the Power of Raw Radar Data in Multi-modality Fusion.md"
    ?? "docs/vAIlt/Exploring Radar-Camera Extrinsic Calibration A Deep Learning Perspective and Challenges.md"
    ?? "docs/vAIlt/External Multi-Modal Imaging Sensor Calibration for Sensor Fusion A Review_1.md"
    ?? "docs/vAIlt/External multi-modal imaging sensor calibration for sensor fusion A review.md"
    ?? "docs/vAIlt/Extrinsic 6DoF Calibration of a Radar-LiDAR-Camera System Enhanced by Radar Cross Section Estimates.md"
    ?? "docs/vAIlt/Extrinsic Calibration.md"
    ?? "docs/vAIlt/Extrinsic Sensor Calibration.md"
    ?? "docs/vAIlt/FUTR3D A Unified Sensor Fusion Framework for 3D Detection.md"
    ?? "docs/vAIlt/False Negative  False Positive Error Analysis.md"
    ?? "docs/vAIlt/Fast 3D Object Detection for 4D Imaging Radar Integrating Image Map Features Using Semi-Supervised Learning.md"
    ?? "docs/vAIlt/Fully Connected Pose Estimation (FCPE).md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework.md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework_1.md"
    ?? "docs/vAIlt/Image (Zotero item 6MQUAGUR).md"
    ?? "docs/vAIlt/Intrinsic Calibration.md"
    ?? "docs/vAIlt/Joint Extrinsic Calibration Tool (Radar-Camera-Lidar).md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions.md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions_1.md"
    ?? "docs/vAIlt/K-Radar Dataset.md"
    ?? "docs/vAIlt/Knowledge Distillation.md"
    ?? "docs/vAIlt/Late (Decision-Level) Fusion.md"
    ?? "docs/vAIlt/LiDAR-4D Radar Fusion.md"
    ?? "docs/vAIlt/LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Lift-Splat-Shoot Framework.md"
    ?? "docs/vAIlt/Linear Group RNN.md"
    ?? "docs/vAIlt/Low-Cost Temporal-Spatial Calibration.md"
    ?? "docs/vAIlt/MSAFusion Object Detection Based on Multisensor Adaptive Fusion Under BEV.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection_1.md"
    ?? "docs/vAIlt/MV2DFusion Model.md"
    ?? "docs/vAIlt/Meta-Information-Based Detection Error Analysis (univariate + Random ForestSHAP).md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance.md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance_1.md"
    ?? "docs/vAIlt/Millimeter-Wave Radar-Camera Fusion.md"
    ?? "docs/vAIlt/Minimally Connected Pose Estimation (MCPE).md"
    ?? "docs/vAIlt/Motion-Based Radar-to-Camera Extrinsic Calibration (velocity-based, targetless).md"
    ?? "docs/vAIlt/Multi-Modal Fusion Technology Based on Vehicle Information A Survey.md"
    ?? "docs/vAIlt/Multi-Sensor ExtrinsicTemporal Calibration.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (CameraLiDARRadar).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (Review Taxonomy).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception for Autonomous Driving A Review.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion in Automated Driving A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey_1.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection_1.md"
    ?? "docs/vAIlt/Object Detection in Autonomous Vehicles under Adverse Weather A Review of Traditional and Deep Learning Approaches.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online LiDAR-Camera Extrinsic Parameters Self-Checking and Recalibration.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_2.md"
    ?? "docs/vAIlt/OpenCalib A Multi-Sensor Calibration Toolbox for Autonomous Driving.md"
    ?? "docs/vAIlt/OpenCalib A Multi-sensor Calibration Toolbox for Autonomous Driving_1.md"
    ?? "docs/vAIlt/OpenCalib Toolbox.md"
    ?? "docs/vAIlt/Perception Methods for Adverse Weather Based on Vehicle Infrastructure Cooperation System A Review.md"
    ?? "docs/vAIlt/Perception and Sensing for Autonomous Vehicles Under Adverse Weather Conditions A Survey.md"
    ?? "docs/vAIlt/Perspective Supervision (auxiliary perspective-view detection loss).md"
    ?? docs/vAIlt/PointPillars.md
    ?? "docs/vAIlt/Pose and Structure Estimation (PSE).md"
    ?? "docs/vAIlt/Query-Based Multi-Modal Fusion (FUTR3D).md"
    ?? "docs/vAIlt/RADIATE A Radar Dataset for Automotive Perception in Bad Weather.md"
    ?? "docs/vAIlt/RADIATE Dataset.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network_1.md"
    ?? "docs/vAIlt/RLCNet An End-to-End Deep Learning Framework for Simultaneous Online Calibration of LiDAR, RADAR, and Camera_1.md"
    ?? "docs/vAIlt/RLCNet An end-to-end deep learning framework for simultaneous online calibration of LiDAR, RADAR, and Camera.md"
    ?? "docs/vAIlt/RLCNet Model.md"
    ?? "docs/vAIlt/Radar Cross Section-Enhanced Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey_1.md"
    ?? "docs/vAIlt/Radar-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar-Camera Fusion Taxonomy (whywhatwherewhenhow to fuse).md"
    ?? "docs/vAIlt/Radar-Camera Fusion for Object Detection and Semantic Segmentation in Autonomous Driving A Comprehensive Review.md"
    ?? "docs/vAIlt/Random Forest + Shapley Value Feature Importance.md"
    ?? "docs/vAIlt/Reprojection-Error-Based Extrinsic Calibration.md"
    ?? "docs/vAIlt/Resilient Object Detection for Autonomous Vehicles Integrating Deep Learning and Sensor Fusion.md"
    ?? "docs/vAIlt/Resilient object detection for autonomous vehicles Integrating deep learning and sensor fusion in adverse conditions.md"
    ?? "docs/vAIlt/Review on Millimeter-Wave Radar and Camera Fusion Technology.md"
    ?? "docs/vAIlt/Robustness of Perception under AdverseCorrupted Conditions.md"
    ?? "docs/vAIlt/Robustness-Aware 3D Object Detection in Autonomous Driving A Review and Outlook.md"
    ?? "docs/vAIlt/SACM Dialectical Safety Assurance Case.md"
    ?? "docs/vAIlt/Safe Autonomous Driving in Adverse Weather Sensor Evaluation and Performance Monitoring.md"
    ?? "docs/vAIlt/Safety Assurance for Perception Systems (standardization, metrics, safety cases).md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset.md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset_1.md"
    ?? "docs/vAIlt/Semi-Supervised 4D Radar Object Detection with Image-Map Features.md"
    ?? "docs/vAIlt/Sensor Evaluation and Performance Monitoring in Adverse Weather.md"
    ?? "docs/vAIlt/Simultaneous Online Multi-Sensor Calibration.md"
    ?? "docs/vAIlt/Single Joint Calibration Target Design (radar+camera+lidar).md"
    ?? "docs/vAIlt/Static Multitarget-Based Autocalibration of RGB Cameras, 3-D Radar, and 3-D Lidar Sensors.md"
    ?? "docs/vAIlt/Strong-Fusion  Weak-Fusion Taxonomy (earlydeeplateasymmetry-fusion).md"
    ?? "docs/vAIlt/Systematic Multi-Modal Sensor Calibration.md"
    ?? "docs/vAIlt/Target-Based Calibration.md"
    ?? "docs/vAIlt/Targetless (Target-Free) Calibration.md"
    ?? "docs/vAIlt/Targetless LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar\342\200\223Camera Calibration via Trajectory Alignment.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration of Radar and Camera for Intelligent Transportation Systems.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System_1.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization Progress, Research Advances, and Perspectives.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization, Progress, Research Advances.md"
    ?? "docs/vAIlt/Towards Robust 3D Object Detection with LiDAR and 4D Radar Fusion in Various Weather Conditions.md"
    ?? "docs/vAIlt/Towards Serious Perception Sensor Simulation for Safety Validation of Automated Driving A Collaborative Approach.md"
    ?? "docs/vAIlt/Two-Stage BEV Detector (perspective proposals + BEV head).md"
    ?? "docs/vAIlt/Two-Stage Point-Feature Refinement.md"
    ?? "docs/vAIlt/UniLION Model.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs_1.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation_1.md"
    ?? "docs/vAIlt/UniTR Model.md"
    ?? "docs/vAIlt/V2X-Enabled Cooperative Safety Intelligence.md"
    ?? "docs/vAIlt/Vehicle-Infrastructure Cooperation System.md"
    ?? "docs/vAIlt/Virtual Points (Radar-to-LiDAR Densification).md"
    ?? docs/vAIlt/VoxelNet.md
    ?? "docs/vAIlt/Waymo Open Dataset.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/ZFusion Model.md"
    ?? "docs/vAIlt/_COMMUNITY_3D Detection Performance Influencing-Factor Analysis.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Calibration & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Fusion Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_AV Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather Perception Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather V2I Perception Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV  Center-Based 3D Detection Architectures.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV Fusion Frameworks Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_Cooperative & Query-Based BEV Fusion.md"
    ?? "docs/vAIlt/_COMMUNITY_Deep-Learning-Based Radar-Camera Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Extrinsic Calibration Methods (Targetless  Continuous-Time).md"
    ?? "docs/vAIlt/_COMMUNITY_General Multi-Sensor Fusion Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_LiDAR-Camera Calibration Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_Miscellaneous Image.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Modal Detection Benchmarks & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Sensor Extrinsic Calibration Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Object-Tracking-Based Online Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety & Robustness Assurance.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety Metrics & Evaluation.md"
    ?? "docs/vAIlt/_COMMUNITY_Robust 4D Radar-Camera Fusion under Adverse Weather.md"
    ?? "docs/vAIlt/_COMMUNITY_Safety Assurance Case (SACM) Methodology.md"
    ?? "docs/vAIlt/_COMMUNITY_Sensor Calibration Toolboxes & Reviews (duplicate snapshots).md"
    ?? "docs/vAIlt/_COMMUNITY_UniLION Model (isolated).md"
    ?? "docs/vAIlt/_COMMUNITY_Unified BEV Transformer & Adaptive Fusion Models.md"
    ?? docs/vAIlt/graph.canvas
    ?? docs/vAIlt/noise-injection-smoke-test-report.md
    ?? "docs/vAIlt/nuScenes A Multimodal Dataset for Autonomous Driving.md"
    ?? "docs/vAIlt/nuScenes A multimodal dataset for autonomous driving_1.md"
    ?? "docs/vAIlt/nuScenes Dataset.md"
    ?? graphify-out/
    ?? obsidianVault/Daily/2026-08-26.md
    ?? obsidianVault/Daily/2026-08-27.md
    ?? obsidianVault/Daily/2026-08-28.md
    ?? obsidianVault/Daily/2026-08-31.md
    ?? obsidianVault/Daily/2026-09-01.md
    ?? obsidianVault/Daily/2026-09-02.md
    ?? obsidianVault/Daily/2026-09-03.md
    ?? obsidianVault/Daily/2026-09-07.md
    ?? obsidianVault/Knowledge/asf-availability-told-not-aware.md
    ?? obsidianVault/Knowledge/asf-map-eval-mechanics.md
    ?? obsidianVault/Knowledge/asf-recovery-rate-and-fog-confound.md
    ?? obsidianVault/Knowledge/cri-computed-from-row-table.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-anomaly-addendum.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-frame-key-fix-20260901.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-phase1-audit.md
    ?? obsidianVault/Knowledge/frame-key-derivation-kradar.md
    ?? obsidianVault/Projects/K-Radar/asf-3d-ap-per-weather-2026-09-07.md
    ?? obsidianVault/Projects/K-Radar/context-radar-charts.md
    ?? obsidianVault/Projects/K-Radar/corruption-visual-gallery.md
    ?? obsidianVault/Projects/K-Radar/dataset-distribution-histograms.md
    ?? obsidianVault/Projects/K-Radar/exhaustive-crossproduct-phase2-progress.md
    ?? obsidianVault/Projects/K-Radar/frame-identifier-bug.md
    ?? obsidianVault/Projects/K-Radar/full-denormalized-exploratory-pass.md
    ?? obsidianVault/Projects/K-Radar/official-checkpoint-rerun-2026-08-26.md
    ?? obsidianVault/Projects/K-Radar/results-context-figures-session.md
    ?? obsidianVault/Projects/K-Radar/robustness-bar-charts.md
    ?? obsidianVault/Projects/K-Radar/robustness-metrics-tables.md
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/bar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/box_plots.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/build_denormalized_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/context_radar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct/
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/dataset_distributions.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/density_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_dumbbell_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts_by_modality.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_robustness_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/exploratory_passes.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/fpfn_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/heatmaps.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/merge_churn.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/pass4_stratifier_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/robustness_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_context.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_pass4.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_robustness_line_charts.py
- Python 3.12.13; matplotlib 3.10.8; numpy 1.26.4; polars 1.39.3 (via `uv run --project test-bed`)
- No bootstrap/random seed: ^c$ is a deterministic AP ratio, using K-Radar's unmodified 41-point interpolated AP evaluator (`ap_metrics.py::compute_ap_grouped`)

#### Data provenance
- Input: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond_weather_corrected.parquet`
  sha256: `d911e93691f2fae1b46d3782d408ea26f72629573f859cb56f07ea146bc6098d`, last modified 2026-09-23 16:44:37 +0200, 872,745 rows, 22 distinct conditions, classes {sed, bus}.
  **Canonical-path note:** the logging template names `repos/K-Radar/scripts/alvis/outputs/row_table_iou03.parquet` as canonical; that exact path doesn't exist (a deeper variant `repos/K-Radar/scripts/alvis/outputs/robustness_reports/row_table_iou03.parquet` does). Regardless it is not the correct input for this figure family: it's a per-detection row table consumed by an unrelated script (`test-bed/.../scripts/analysis/radar_charts.py`, severity-tier condition charts, not diversity-axis charts). The diversity-axis radar charts (Figs. 5.8-5.21 and this panel) come exclusively from the pre-aggregated `full_denormalized_table_22cond_weather_corrected.parquet` via `generate_corruption_radar.py` -- confirmed against `Results.tex`'s own figure references.
- Filter/agg chain (inside `compute_axis`, unchanged from `generate_corruption_radar.py`): (1) `df.filter(condition in {original} ∪ {spoke_condition(*s) for s in SPOKES})` -> subset to the 22 needed conditions; (2) `compute_ap_grouped(dff_all, group_by=["condition","cls","time_of_day"])` -> AP + num_gt per (condition, class, category) cell; (3) per spoke, ^c$ = corrupted-AP / baseline-AP if both baseline num_gt >=30 and corrupted num_gt >=30, else NaN (gap in plotted line).
- IoU threshold: 0.3. Class: Sedan (cls=sed). Diversity-axis column: `time_of_day`. Category plotted: `day`. Severities: low/medium/high for gaussian_noise and loss_partial; single tier for loss_complete_zero.
- Baseline (`original` condition) for this panel: AP=79.85, num_gt=19961 (well above the N>=30 floor -- independently recomputed this session, see Verification)

#### Statistical reporting
- Baseline N reported above; per-corrupted-spoke N not individually enumerated in this session beyond the floor-check already performed inside `compute_axis` (sub-floor spokes become NaN gaps, never plotted as solid values).
- N_sequences: not computed separately this session -- `compute_ap_grouped` pools across all sequences present for this (condition, cls, category) cell in the parquet; sequence-level breakdown is UNVERIFIABLE from this session alone.
- CI method: none -- ^c$ is a point-estimate ratio; no bootstrap/CI shown, consistent with the original thesis figure.
- No sub-floor (N<30) group is plotted as a solid/trusted value on this panel.
- "Significant" is not used on this figure or its caption.

#### Styling
- Shared plotting module: `docs/crossproduct_figures/palette.py` (`MODALITY_COLORS`, `RANK_COLORS`) -- identical to every thesis radar chart.
- Font sizes tuned for a full single-panel chart (title 18pt, tick labels 15pt, y-tick 11pt); not yet checked against actual slide-deck text scale.
- Colorblind safety: not independently re-verified this session -- palette inherited unchanged from the thesis's own module.
- Title on plot: **yes** -- "Sedan robustness under all 21 corruption conditions, Time-of-Day=Day stratum (individual panel cropped from the thesis's diversity-axes time-of-day radar-chart family, Fig. 5.10 area)." -- deviates from the template's "default is no" convention; kept per explicit user instruction this session, since each panel is being cropped out of its original multi-panel context and needs its own label.

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown -- only ^c$ (AP ratio)
- [x] No camera `frame_deletion` conditions included -- confirmed absent from `RADAR_AXIS_EFFECTS`/`SPOKES` in `_lib.py`
- [x] No external/paper figures or images reused -- generated fresh from local parquet this session
- [x] Every number traced to source file above (baseline AP/num_gt independently recomputed, see Verification)
- [ ] Figure visually inspected after rendering -- **NOT satisfied.** Only file existence, PNG dimensions (via `identify`/PIL) and sha256 were checked this session; the rendered image was not opened/viewed. Flagging honestly rather than claiming a check that didn't happen.

#### Verification
- Independently recomputed the baseline (`original`, Sedan (cls=sed), `time_of_day`=`day`) AP/num_gt cell via a fresh `compute_ap_grouped` call in this session, separate from re-running the plotting script: AP=79.85, num_gt=19961.
- Not diffed against `findings.md`, Q1-Q6 CSVs, or the compiled LaTeX thesis PDF in this session -- this panel is a re-crop of the same underlying computation behind the corresponding published thesis figure (Fig. 5.8/5.9/5.10 family depending on axis), not a new number, but that equivalence has not been explicitly re-verified against the PDF this session.

#### Open issues / caveats
- Visual inspection of the rendered PNG was not performed this session (see unchecked Integrity item above) -- user should open the file before placing it on a slide.
- Canonical-path discrepancy noted above under Data provenance.
- Per-spoke N/coverage beyond the single baseline cell reported here was not enumerated for this panel in this session.

---
### FIG-20260924-193406-claude-slidefigs-sedan-time-night
**Status:** FINAL
**Supersedes:** N/A — first logged entry for this figure (earlier un-logged transparent-bg / legend-removal / text-edit iterations in this same conversation were overwritten in place before this log existed; only the final state is logged, per no-retroactive-fabrication)
**Logged:** 2026-09-24T19:34:06+02:00 by claude-slidefigs
**Intended slide(s):** Findings slide 1 — "general trends" (unassigned slide number in .odp; user assembling this slide now)
**Story-arc step served:** corruption-sweep results — per-diversity-axis robustness (^c$), individual stratum panel cropped for slide use

#### What the figure shows
- Sedan robustness under all 21 corruption conditions, Time-of-Day=Night stratum (individual panel cropped from the thesis's diversity-axes time-of-day radar-chart family, Fig. 5.10 area).
- Plot type: polar/radar chart, one spoke per (modality, effect, severity) condition (21 spokes: camera/LiDAR/radar × {gaussian_noise low/med/high, loss_partial low/med/high, loss_complete_zero}). Radial axis = ^c$ = AP(corrupted)/AP(clean), range 0-1.15, gridlines at 0/.25/.5/.75/1. Class: Sedan (cls=sed). Spoke color = modality (camera green / LiDAR blue / radar red, from `docs/crossproduct_figures/palette.py::MODALITY_COLORS`). Per-modality mean-^c$ shown as a shaded arc across that modality's 7 spokes. Worst and second-worst robustness spokes ringed with dashed circles (`palette.py::RANK_COLORS`).
- Deliberately excluded: camera `frame_deletion` (excluded thesis-wide per 2026-08-25 decision, baked into `RADAR_AXIS_EFFECTS`/`SPOKES` in the source script — never in the 21-spoke set). No RCE/mASE/CRI shown.

#### Output files
- `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/sedan_time_night.png`
- 1716x1780 px, 200 DPI, transparent background (fig+axes patch alpha=0, `savefig(transparent=True)`)
- sha256: `40ef250cde51eba0d147243299ce12def8ba9ff538f04b3383d1e0791e145e0d`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py`, requesting stem `sedan_time_night` — **new script written this session**, not pre-existing. It is a single-panel adaptation of the thesis's actual multi-panel generator `docs/crossproduct_figures/generate_corruption_radar.py` (confirmed as the true source of thesis Figs. 5.8-5.21 via `docs/Latex_Report/thesis_report/include/Results.tex`).
- Adaptation method: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/_lib.py` is a byte-identical copy of `generate_corruption_radar.py` lines 1-259 (verified via `diff`) -- every function/constant (`compute_axis`, `AXES`, `SPOKES`, `MOD_RANGES`, `CIRCLE_STYLES`, color palette imports) unchanged, with only the trailing top-level `for axis_key ...` batch-generation loop (original lines 260-265) removed, since that loop unconditionally regenerates every thesis figure on import. `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/palette.py` is byte-identical to `docs/crossproduct_figures/palette.py` (sha256 `acfb5f38dbe4c5b923e3edf409c6cf2ff8787fef5dd95672bcacaaa573a626c2` matches both).
- `make_single.py`'s `make_single_panel()` reproduces `generate_corruption_radar.py::make_figure()`'s per-panel plotting logic (same mean-arc computation, same worst/second-worst ring logic, same tick/color logic) for exactly one (class, category) pair instead of a 2x2 grid. Per user instructions this session: per-panel title changed to "Axis - Category (Class)"; shared bottom legend removed entirely (logged separately as `radar_chart_legend.png`); background made transparent.
- Exact command (from `/home/adhish/Productivity/AMSCUP/test-bed`, no special env vars):
```
uv run --project . python /home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py
```
  (generates all 6 individual-panel figures in one run, including this one)
- Git commit at generation time: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree was DIRTY. Dirty/untracked files (abbreviated; full list was captured via `git status --porcelain` at generation time and is stable across all entries in this batch):
     M CLAUDE.md
     D docs/Adyuth_Hisham_resume_PartTime.docx.md
     M docs/Latex_Report
     M docs/vAIlt/.obsidian/workspace.json
     M obsidianVault/.obsidian/workspace.json
     M obsidianVault/Knowledge/asf-training-inputs.md
     M obsidianVault/Knowledge/robustness-metric-selection.md
     M obsidianVault/Projects/K-Radar/asf-corruption-study-alvis.md
     M obsidianVault/Projects/K-Radar/robustness-radar-charts.md
     M repos/K-Radar
     M test-bed/src/Modules/robust_testing/kradar/scripts/analysis/radar_charts.py
     M test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py
    ?? .agents/
    ?? FinalTerm_Presentation_Claude.odp
    ?? alvis_archive_2026-08-28/
    ?? backups/
    ?? docs/.master_presentation_figures.lock
    ?? docs/.~lock.Thesis_Presentation_Claude.odp#
    ?? docs/ASF_KRadar_Adversarial_Review.md
    ?? docs/ASF_Pipeline.backup.svg
    ?? docs/ASF_Pipeline.svg
    ?? docs/ASF_Pipeline_slide.svg
    ?? docs/ASF_Pipeline_v2.svg
    ?? docs/ASF_pipeline_cheatsheet.md
    ?? docs/FINAL_CHECK_LOG.md
    ?? docs/HUMANIZE_LOG.md
    ?? docs/Thesis_Presentation.odp
    ?? docs/Thesis_Presentation_Claude.odp
    ?? docs/crossproduct_figures/
    ?? docs/crossproduct_trends_and_anomalies.md
    ?? docs/crossproduct_trends_and_anomalies_metrics_coverage.md
    ?? docs/delete_/
    ?? docs/figure_scripts/
    ?? docs/images/
    ?? docs/lit_survey/ALVIS_URLs.txt
    ?? docs/lit_survey/asf.txt
    ?? docs/lit_survey/dataset/
    ?? docs/lit_survey/irl_corruptions/
    ?? docs/lit_survey/models/
    ?? docs/lit_survey/motivations/
    ?? docs/lit_survey/robust_benchmarks/
    ?? docs/master_presentation_figures.md
    ?? docs/regenerate_weather_figures_snow_fix.md
    ?? docs/slide_figures_findings1/
    ?? docs/thesis_defense_questions.md
    ?? docs/thesis_defense_questions_draft.md
    ?? docs/thesis_writing_bible.md
    ?? docs/trend_candidates.md
    ?? docs/vAIlt/06_Results/alvis-wipe-audit-2026-08-28.md
    ?? docs/vAIlt/06_Results/crossproduct-rebuild-20260901.md
    ?? docs/vAIlt/06_Results/distance-band-ap-and-churn-recompute-2026-09-04.md
    ?? docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md
    ?? docs/vAIlt/06_Results/frame-identifier-bug-fix-report.md
    ?? docs/vAIlt/06_Results/lidar-gaussian-noise-mechanism-phase1-audit-20260902.md
    ?? docs/vAIlt/06_Results/manual-code-vetting-checklist.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-audit-phase1-2026-08-31.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-bug-audit-2026-08-31.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31-corrected.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31.md
    ?? "docs/vAIlt/3-D LiDAR and Monocular Camera Calibration A Review.md"
    ?? "docs/vAIlt/3D Uncertainty Perspective-N-Points (PnP).md"
    ?? "docs/vAIlt/4D Radar-Camera Calibration and Auto-Labeling.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion_1.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving_1.md"
    ?? "docs/vAIlt/A 4D Radar-Camera Extrinsic Calibration Tool Based on 3D Uncertainty Perspective-N-Points.md"
    ?? "docs/vAIlt/A Continuous-Time Approach for 3D Radar-to-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/A Joint Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/A Low-Cost Temporal-Spatial Calibration Method for Radar and Camera Systems.md"
    ?? "docs/vAIlt/A Review of Environmental Perception Technology Based on Multi-Sensor Information Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A Review of Multi-Sensor Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A low-cost temporal-spatial calibration method for radar and camera systems_1.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and Robust 3D Object Detection in Adverse Conditions through Knowledge Distillation.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and robust 3D object detection in adverse conditions through knowledge distillation_1.md"
    ?? docs/vAIlt/AWARDistill.md
    ?? "docs/vAIlt/AdaptiveFusion LiDAR-Camera Adaptive Fusion for 3D Object Detection.md"
    ?? "docs/vAIlt/AdaptiveFusion Model.md"
    ?? "docs/vAIlt/Adverse Weather Perception.md"
    ?? "docs/vAIlt/Adverse-Weather Perception Robustness.md"
    ?? "docs/vAIlt/An Autonomous Extrinsic Calibration Method for 4D Millimeter-Wave Radar Point Clouds and Visual Images.md"
    ?? "docs/vAIlt/An Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/Anchor-Based 3D Detection.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion_1.md"
    ?? "docs/vAIlt/Automatic Targetless LiDAR-Camera Calibration A Survey.md"
    ?? "docs/vAIlt/Autonomous Driving Perception Safety Standardization.md"
    ?? "docs/vAIlt/Autonomous-Driving Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/Availability-aware Sensor Fusion via Unified Canonical Space.md"
    ?? "docs/vAIlt/BEVFormer (v1).md"
    ?? "docs/vAIlt/BEVFormer v2 Adapting Modern Image Backbones to Bird's-Eye-View Recognition via Perspective Supervision.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation_1.md"
    ?? "docs/vAIlt/Bird's-Eye View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View  3D Object Detection Architectures.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Recognition.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation_1.md"
    ?? "docs/vAIlt/Camera, LiDAR, and IMU Spatiotemporal Calibration Methodological Review and Research Perspectives.md"
    ?? "docs/vAIlt/Camera-Radar Fusion (HVDetFusion).md"
    ?? "docs/vAIlt/Center-Based Object Representation (points, not boxes).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking (CenterPoint).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking.md"
    ?? "docs/vAIlt/Continuous-Time Trajectory Representation.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey_1.md"
    ?? "docs/vAIlt/Deep (Feature-Level) Fusion.md"
    ?? "docs/vAIlt/Deep-Learning-Based Calibration Challenges.md"
    ?? "docs/vAIlt/Delving Into the Secrets of BEV 3D Object Detection in Autonomous Driving A Comprehensive Survey.md"
    ?? "docs/vAIlt/Doppler-Optical Flow Fusion Calibration.md"
    ?? "docs/vAIlt/EA-LSS Edge-Aware Lift-Splat-Shot Framework for 3D BEV Object Detection.md"
    ?? "docs/vAIlt/EA-LSS Edge-aware Lift-splat-shot Framework for 3D BEV Object Detection_1.md"
    ?? "docs/vAIlt/EPSM (Environmental Perception Safety Metric).md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/Early Fusion.md"
    ?? "docs/vAIlt/Echoes Beyond Points Unleashing the Power of Raw Radar Data in Multi-modality Fusion.md"
    ?? "docs/vAIlt/Exploring Radar-Camera Extrinsic Calibration A Deep Learning Perspective and Challenges.md"
    ?? "docs/vAIlt/External Multi-Modal Imaging Sensor Calibration for Sensor Fusion A Review_1.md"
    ?? "docs/vAIlt/External multi-modal imaging sensor calibration for sensor fusion A review.md"
    ?? "docs/vAIlt/Extrinsic 6DoF Calibration of a Radar-LiDAR-Camera System Enhanced by Radar Cross Section Estimates.md"
    ?? "docs/vAIlt/Extrinsic Calibration.md"
    ?? "docs/vAIlt/Extrinsic Sensor Calibration.md"
    ?? "docs/vAIlt/FUTR3D A Unified Sensor Fusion Framework for 3D Detection.md"
    ?? "docs/vAIlt/False Negative  False Positive Error Analysis.md"
    ?? "docs/vAIlt/Fast 3D Object Detection for 4D Imaging Radar Integrating Image Map Features Using Semi-Supervised Learning.md"
    ?? "docs/vAIlt/Fully Connected Pose Estimation (FCPE).md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework.md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework_1.md"
    ?? "docs/vAIlt/Image (Zotero item 6MQUAGUR).md"
    ?? "docs/vAIlt/Intrinsic Calibration.md"
    ?? "docs/vAIlt/Joint Extrinsic Calibration Tool (Radar-Camera-Lidar).md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions.md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions_1.md"
    ?? "docs/vAIlt/K-Radar Dataset.md"
    ?? "docs/vAIlt/Knowledge Distillation.md"
    ?? "docs/vAIlt/Late (Decision-Level) Fusion.md"
    ?? "docs/vAIlt/LiDAR-4D Radar Fusion.md"
    ?? "docs/vAIlt/LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Lift-Splat-Shoot Framework.md"
    ?? "docs/vAIlt/Linear Group RNN.md"
    ?? "docs/vAIlt/Low-Cost Temporal-Spatial Calibration.md"
    ?? "docs/vAIlt/MSAFusion Object Detection Based on Multisensor Adaptive Fusion Under BEV.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection_1.md"
    ?? "docs/vAIlt/MV2DFusion Model.md"
    ?? "docs/vAIlt/Meta-Information-Based Detection Error Analysis (univariate + Random ForestSHAP).md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance.md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance_1.md"
    ?? "docs/vAIlt/Millimeter-Wave Radar-Camera Fusion.md"
    ?? "docs/vAIlt/Minimally Connected Pose Estimation (MCPE).md"
    ?? "docs/vAIlt/Motion-Based Radar-to-Camera Extrinsic Calibration (velocity-based, targetless).md"
    ?? "docs/vAIlt/Multi-Modal Fusion Technology Based on Vehicle Information A Survey.md"
    ?? "docs/vAIlt/Multi-Sensor ExtrinsicTemporal Calibration.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (CameraLiDARRadar).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (Review Taxonomy).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception for Autonomous Driving A Review.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion in Automated Driving A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey_1.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection_1.md"
    ?? "docs/vAIlt/Object Detection in Autonomous Vehicles under Adverse Weather A Review of Traditional and Deep Learning Approaches.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online LiDAR-Camera Extrinsic Parameters Self-Checking and Recalibration.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_2.md"
    ?? "docs/vAIlt/OpenCalib A Multi-Sensor Calibration Toolbox for Autonomous Driving.md"
    ?? "docs/vAIlt/OpenCalib A Multi-sensor Calibration Toolbox for Autonomous Driving_1.md"
    ?? "docs/vAIlt/OpenCalib Toolbox.md"
    ?? "docs/vAIlt/Perception Methods for Adverse Weather Based on Vehicle Infrastructure Cooperation System A Review.md"
    ?? "docs/vAIlt/Perception and Sensing for Autonomous Vehicles Under Adverse Weather Conditions A Survey.md"
    ?? "docs/vAIlt/Perspective Supervision (auxiliary perspective-view detection loss).md"
    ?? docs/vAIlt/PointPillars.md
    ?? "docs/vAIlt/Pose and Structure Estimation (PSE).md"
    ?? "docs/vAIlt/Query-Based Multi-Modal Fusion (FUTR3D).md"
    ?? "docs/vAIlt/RADIATE A Radar Dataset for Automotive Perception in Bad Weather.md"
    ?? "docs/vAIlt/RADIATE Dataset.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network_1.md"
    ?? "docs/vAIlt/RLCNet An End-to-End Deep Learning Framework for Simultaneous Online Calibration of LiDAR, RADAR, and Camera_1.md"
    ?? "docs/vAIlt/RLCNet An end-to-end deep learning framework for simultaneous online calibration of LiDAR, RADAR, and Camera.md"
    ?? "docs/vAIlt/RLCNet Model.md"
    ?? "docs/vAIlt/Radar Cross Section-Enhanced Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey_1.md"
    ?? "docs/vAIlt/Radar-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar-Camera Fusion Taxonomy (whywhatwherewhenhow to fuse).md"
    ?? "docs/vAIlt/Radar-Camera Fusion for Object Detection and Semantic Segmentation in Autonomous Driving A Comprehensive Review.md"
    ?? "docs/vAIlt/Random Forest + Shapley Value Feature Importance.md"
    ?? "docs/vAIlt/Reprojection-Error-Based Extrinsic Calibration.md"
    ?? "docs/vAIlt/Resilient Object Detection for Autonomous Vehicles Integrating Deep Learning and Sensor Fusion.md"
    ?? "docs/vAIlt/Resilient object detection for autonomous vehicles Integrating deep learning and sensor fusion in adverse conditions.md"
    ?? "docs/vAIlt/Review on Millimeter-Wave Radar and Camera Fusion Technology.md"
    ?? "docs/vAIlt/Robustness of Perception under AdverseCorrupted Conditions.md"
    ?? "docs/vAIlt/Robustness-Aware 3D Object Detection in Autonomous Driving A Review and Outlook.md"
    ?? "docs/vAIlt/SACM Dialectical Safety Assurance Case.md"
    ?? "docs/vAIlt/Safe Autonomous Driving in Adverse Weather Sensor Evaluation and Performance Monitoring.md"
    ?? "docs/vAIlt/Safety Assurance for Perception Systems (standardization, metrics, safety cases).md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset.md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset_1.md"
    ?? "docs/vAIlt/Semi-Supervised 4D Radar Object Detection with Image-Map Features.md"
    ?? "docs/vAIlt/Sensor Evaluation and Performance Monitoring in Adverse Weather.md"
    ?? "docs/vAIlt/Simultaneous Online Multi-Sensor Calibration.md"
    ?? "docs/vAIlt/Single Joint Calibration Target Design (radar+camera+lidar).md"
    ?? "docs/vAIlt/Static Multitarget-Based Autocalibration of RGB Cameras, 3-D Radar, and 3-D Lidar Sensors.md"
    ?? "docs/vAIlt/Strong-Fusion  Weak-Fusion Taxonomy (earlydeeplateasymmetry-fusion).md"
    ?? "docs/vAIlt/Systematic Multi-Modal Sensor Calibration.md"
    ?? "docs/vAIlt/Target-Based Calibration.md"
    ?? "docs/vAIlt/Targetless (Target-Free) Calibration.md"
    ?? "docs/vAIlt/Targetless LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar\342\200\223Camera Calibration via Trajectory Alignment.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration of Radar and Camera for Intelligent Transportation Systems.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System_1.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization Progress, Research Advances, and Perspectives.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization, Progress, Research Advances.md"
    ?? "docs/vAIlt/Towards Robust 3D Object Detection with LiDAR and 4D Radar Fusion in Various Weather Conditions.md"
    ?? "docs/vAIlt/Towards Serious Perception Sensor Simulation for Safety Validation of Automated Driving A Collaborative Approach.md"
    ?? "docs/vAIlt/Two-Stage BEV Detector (perspective proposals + BEV head).md"
    ?? "docs/vAIlt/Two-Stage Point-Feature Refinement.md"
    ?? "docs/vAIlt/UniLION Model.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs_1.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation_1.md"
    ?? "docs/vAIlt/UniTR Model.md"
    ?? "docs/vAIlt/V2X-Enabled Cooperative Safety Intelligence.md"
    ?? "docs/vAIlt/Vehicle-Infrastructure Cooperation System.md"
    ?? "docs/vAIlt/Virtual Points (Radar-to-LiDAR Densification).md"
    ?? docs/vAIlt/VoxelNet.md
    ?? "docs/vAIlt/Waymo Open Dataset.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/ZFusion Model.md"
    ?? "docs/vAIlt/_COMMUNITY_3D Detection Performance Influencing-Factor Analysis.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Calibration & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Fusion Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_AV Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather Perception Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather V2I Perception Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV  Center-Based 3D Detection Architectures.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV Fusion Frameworks Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_Cooperative & Query-Based BEV Fusion.md"
    ?? "docs/vAIlt/_COMMUNITY_Deep-Learning-Based Radar-Camera Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Extrinsic Calibration Methods (Targetless  Continuous-Time).md"
    ?? "docs/vAIlt/_COMMUNITY_General Multi-Sensor Fusion Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_LiDAR-Camera Calibration Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_Miscellaneous Image.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Modal Detection Benchmarks & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Sensor Extrinsic Calibration Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Object-Tracking-Based Online Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety & Robustness Assurance.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety Metrics & Evaluation.md"
    ?? "docs/vAIlt/_COMMUNITY_Robust 4D Radar-Camera Fusion under Adverse Weather.md"
    ?? "docs/vAIlt/_COMMUNITY_Safety Assurance Case (SACM) Methodology.md"
    ?? "docs/vAIlt/_COMMUNITY_Sensor Calibration Toolboxes & Reviews (duplicate snapshots).md"
    ?? "docs/vAIlt/_COMMUNITY_UniLION Model (isolated).md"
    ?? "docs/vAIlt/_COMMUNITY_Unified BEV Transformer & Adaptive Fusion Models.md"
    ?? docs/vAIlt/graph.canvas
    ?? docs/vAIlt/noise-injection-smoke-test-report.md
    ?? "docs/vAIlt/nuScenes A Multimodal Dataset for Autonomous Driving.md"
    ?? "docs/vAIlt/nuScenes A multimodal dataset for autonomous driving_1.md"
    ?? "docs/vAIlt/nuScenes Dataset.md"
    ?? graphify-out/
    ?? obsidianVault/Daily/2026-08-26.md
    ?? obsidianVault/Daily/2026-08-27.md
    ?? obsidianVault/Daily/2026-08-28.md
    ?? obsidianVault/Daily/2026-08-31.md
    ?? obsidianVault/Daily/2026-09-01.md
    ?? obsidianVault/Daily/2026-09-02.md
    ?? obsidianVault/Daily/2026-09-03.md
    ?? obsidianVault/Daily/2026-09-07.md
    ?? obsidianVault/Knowledge/asf-availability-told-not-aware.md
    ?? obsidianVault/Knowledge/asf-map-eval-mechanics.md
    ?? obsidianVault/Knowledge/asf-recovery-rate-and-fog-confound.md
    ?? obsidianVault/Knowledge/cri-computed-from-row-table.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-anomaly-addendum.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-frame-key-fix-20260901.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-phase1-audit.md
    ?? obsidianVault/Knowledge/frame-key-derivation-kradar.md
    ?? obsidianVault/Projects/K-Radar/asf-3d-ap-per-weather-2026-09-07.md
    ?? obsidianVault/Projects/K-Radar/context-radar-charts.md
    ?? obsidianVault/Projects/K-Radar/corruption-visual-gallery.md
    ?? obsidianVault/Projects/K-Radar/dataset-distribution-histograms.md
    ?? obsidianVault/Projects/K-Radar/exhaustive-crossproduct-phase2-progress.md
    ?? obsidianVault/Projects/K-Radar/frame-identifier-bug.md
    ?? obsidianVault/Projects/K-Radar/full-denormalized-exploratory-pass.md
    ?? obsidianVault/Projects/K-Radar/official-checkpoint-rerun-2026-08-26.md
    ?? obsidianVault/Projects/K-Radar/results-context-figures-session.md
    ?? obsidianVault/Projects/K-Radar/robustness-bar-charts.md
    ?? obsidianVault/Projects/K-Radar/robustness-metrics-tables.md
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/bar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/box_plots.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/build_denormalized_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/context_radar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct/
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/dataset_distributions.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/density_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_dumbbell_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts_by_modality.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_robustness_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/exploratory_passes.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/fpfn_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/heatmaps.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/merge_churn.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/pass4_stratifier_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/robustness_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_context.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_pass4.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_robustness_line_charts.py
- Python 3.12.13; matplotlib 3.10.8; numpy 1.26.4; polars 1.39.3 (via `uv run --project test-bed`)
- No bootstrap/random seed: ^c$ is a deterministic AP ratio, using K-Radar's unmodified 41-point interpolated AP evaluator (`ap_metrics.py::compute_ap_grouped`)

#### Data provenance
- Input: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond_weather_corrected.parquet`
  sha256: `d911e93691f2fae1b46d3782d408ea26f72629573f859cb56f07ea146bc6098d`, last modified 2026-09-23 16:44:37 +0200, 872,745 rows, 22 distinct conditions, classes {sed, bus}.
  **Canonical-path note:** the logging template names `repos/K-Radar/scripts/alvis/outputs/row_table_iou03.parquet` as canonical; that exact path doesn't exist (a deeper variant `repos/K-Radar/scripts/alvis/outputs/robustness_reports/row_table_iou03.parquet` does). Regardless it is not the correct input for this figure family: it's a per-detection row table consumed by an unrelated script (`test-bed/.../scripts/analysis/radar_charts.py`, severity-tier condition charts, not diversity-axis charts). The diversity-axis radar charts (Figs. 5.8-5.21 and this panel) come exclusively from the pre-aggregated `full_denormalized_table_22cond_weather_corrected.parquet` via `generate_corruption_radar.py` -- confirmed against `Results.tex`'s own figure references.
- Filter/agg chain (inside `compute_axis`, unchanged from `generate_corruption_radar.py`): (1) `df.filter(condition in {original} ∪ {spoke_condition(*s) for s in SPOKES})` -> subset to the 22 needed conditions; (2) `compute_ap_grouped(dff_all, group_by=["condition","cls","time_of_day"])` -> AP + num_gt per (condition, class, category) cell; (3) per spoke, ^c$ = corrupted-AP / baseline-AP if both baseline num_gt >=30 and corrupted num_gt >=30, else NaN (gap in plotted line).
- IoU threshold: 0.3. Class: Sedan (cls=sed). Diversity-axis column: `time_of_day`. Category plotted: `night`. Severities: low/medium/high for gaussian_noise and loss_partial; single tier for loss_complete_zero.
- Baseline (`original` condition) for this panel: AP=73.91, num_gt=9652 (well above the N>=30 floor -- independently recomputed this session, see Verification)

#### Statistical reporting
- Baseline N reported above; per-corrupted-spoke N not individually enumerated in this session beyond the floor-check already performed inside `compute_axis` (sub-floor spokes become NaN gaps, never plotted as solid values).
- N_sequences: not computed separately this session -- `compute_ap_grouped` pools across all sequences present for this (condition, cls, category) cell in the parquet; sequence-level breakdown is UNVERIFIABLE from this session alone.
- CI method: none -- ^c$ is a point-estimate ratio; no bootstrap/CI shown, consistent with the original thesis figure.
- No sub-floor (N<30) group is plotted as a solid/trusted value on this panel.
- "Significant" is not used on this figure or its caption.

#### Styling
- Shared plotting module: `docs/crossproduct_figures/palette.py` (`MODALITY_COLORS`, `RANK_COLORS`) -- identical to every thesis radar chart.
- Font sizes tuned for a full single-panel chart (title 18pt, tick labels 15pt, y-tick 11pt); not yet checked against actual slide-deck text scale.
- Colorblind safety: not independently re-verified this session -- palette inherited unchanged from the thesis's own module.
- Title on plot: **yes** -- "Sedan robustness under all 21 corruption conditions, Time-of-Day=Night stratum (individual panel cropped from the thesis's diversity-axes time-of-day radar-chart family, Fig. 5.10 area)." -- deviates from the template's "default is no" convention; kept per explicit user instruction this session, since each panel is being cropped out of its original multi-panel context and needs its own label.

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown -- only ^c$ (AP ratio)
- [x] No camera `frame_deletion` conditions included -- confirmed absent from `RADAR_AXIS_EFFECTS`/`SPOKES` in `_lib.py`
- [x] No external/paper figures or images reused -- generated fresh from local parquet this session
- [x] Every number traced to source file above (baseline AP/num_gt independently recomputed, see Verification)
- [ ] Figure visually inspected after rendering -- **NOT satisfied.** Only file existence, PNG dimensions (via `identify`/PIL) and sha256 were checked this session; the rendered image was not opened/viewed. Flagging honestly rather than claiming a check that didn't happen.

#### Verification
- Independently recomputed the baseline (`original`, Sedan (cls=sed), `time_of_day`=`night`) AP/num_gt cell via a fresh `compute_ap_grouped` call in this session, separate from re-running the plotting script: AP=73.91, num_gt=9652.
- Not diffed against `findings.md`, Q1-Q6 CSVs, or the compiled LaTeX thesis PDF in this session -- this panel is a re-crop of the same underlying computation behind the corresponding published thesis figure (Fig. 5.8/5.9/5.10 family depending on axis), not a new number, but that equivalence has not been explicitly re-verified against the PDF this session.

#### Open issues / caveats
- Visual inspection of the rendered PNG was not performed this session (see unchecked Integrity item above) -- user should open the file before placing it on a slide.
- Canonical-path discrepancy noted above under Data provenance.
- Per-spoke N/coverage beyond the single baseline cell reported here was not enumerated for this panel in this session.

---
### FIG-20260924-193406-claude-slidefigs-sedan-env-highway
**Status:** FINAL
**Supersedes:** N/A — first logged entry for this figure (earlier un-logged transparent-bg / legend-removal / text-edit iterations in this same conversation were overwritten in place before this log existed; only the final state is logged, per no-retroactive-fabrication)
**Logged:** 2026-09-24T19:34:06+02:00 by claude-slidefigs
**Intended slide(s):** Findings slide 1 — "general trends" (unassigned slide number in .odp; user assembling this slide now)
**Story-arc step served:** corruption-sweep results — per-diversity-axis robustness (^c$), individual stratum panel cropped for slide use

#### What the figure shows
- Sedan robustness under all 21 corruption conditions, Environment=Highway stratum (individual panel cropped from the thesis's diversity-axes environment radar-chart family, Fig. 5.9 area).
- Plot type: polar/radar chart, one spoke per (modality, effect, severity) condition (21 spokes: camera/LiDAR/radar × {gaussian_noise low/med/high, loss_partial low/med/high, loss_complete_zero}). Radial axis = ^c$ = AP(corrupted)/AP(clean), range 0-1.15, gridlines at 0/.25/.5/.75/1. Class: Sedan (cls=sed). Spoke color = modality (camera green / LiDAR blue / radar red, from `docs/crossproduct_figures/palette.py::MODALITY_COLORS`). Per-modality mean-^c$ shown as a shaded arc across that modality's 7 spokes. Worst and second-worst robustness spokes ringed with dashed circles (`palette.py::RANK_COLORS`).
- Deliberately excluded: camera `frame_deletion` (excluded thesis-wide per 2026-08-25 decision, baked into `RADAR_AXIS_EFFECTS`/`SPOKES` in the source script — never in the 21-spoke set). No RCE/mASE/CRI shown.

#### Output files
- `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/sedan_env_highway.png`
- 1716x1780 px, 200 DPI, transparent background (fig+axes patch alpha=0, `savefig(transparent=True)`)
- sha256: `48275b22baecf7ccf8746a4b35d1429015507c7322bd1898d92cb5faa14d3bc8`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py`, requesting stem `sedan_env_highway` — **new script written this session**, not pre-existing. It is a single-panel adaptation of the thesis's actual multi-panel generator `docs/crossproduct_figures/generate_corruption_radar.py` (confirmed as the true source of thesis Figs. 5.8-5.21 via `docs/Latex_Report/thesis_report/include/Results.tex`).
- Adaptation method: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/_lib.py` is a byte-identical copy of `generate_corruption_radar.py` lines 1-259 (verified via `diff`) -- every function/constant (`compute_axis`, `AXES`, `SPOKES`, `MOD_RANGES`, `CIRCLE_STYLES`, color palette imports) unchanged, with only the trailing top-level `for axis_key ...` batch-generation loop (original lines 260-265) removed, since that loop unconditionally regenerates every thesis figure on import. `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/palette.py` is byte-identical to `docs/crossproduct_figures/palette.py` (sha256 `acfb5f38dbe4c5b923e3edf409c6cf2ff8787fef5dd95672bcacaaa573a626c2` matches both).
- `make_single.py`'s `make_single_panel()` reproduces `generate_corruption_radar.py::make_figure()`'s per-panel plotting logic (same mean-arc computation, same worst/second-worst ring logic, same tick/color logic) for exactly one (class, category) pair instead of a 2x2 grid. Per user instructions this session: per-panel title changed to "Axis - Category (Class)"; shared bottom legend removed entirely (logged separately as `radar_chart_legend.png`); background made transparent.
- Exact command (from `/home/adhish/Productivity/AMSCUP/test-bed`, no special env vars):
```
uv run --project . python /home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py
```
  (generates all 6 individual-panel figures in one run, including this one)
- Git commit at generation time: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree was DIRTY. Dirty/untracked files (abbreviated; full list was captured via `git status --porcelain` at generation time and is stable across all entries in this batch):
     M CLAUDE.md
     D docs/Adyuth_Hisham_resume_PartTime.docx.md
     M docs/Latex_Report
     M docs/vAIlt/.obsidian/workspace.json
     M obsidianVault/.obsidian/workspace.json
     M obsidianVault/Knowledge/asf-training-inputs.md
     M obsidianVault/Knowledge/robustness-metric-selection.md
     M obsidianVault/Projects/K-Radar/asf-corruption-study-alvis.md
     M obsidianVault/Projects/K-Radar/robustness-radar-charts.md
     M repos/K-Radar
     M test-bed/src/Modules/robust_testing/kradar/scripts/analysis/radar_charts.py
     M test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py
    ?? .agents/
    ?? FinalTerm_Presentation_Claude.odp
    ?? alvis_archive_2026-08-28/
    ?? backups/
    ?? docs/.master_presentation_figures.lock
    ?? docs/.~lock.Thesis_Presentation_Claude.odp#
    ?? docs/ASF_KRadar_Adversarial_Review.md
    ?? docs/ASF_Pipeline.backup.svg
    ?? docs/ASF_Pipeline.svg
    ?? docs/ASF_Pipeline_slide.svg
    ?? docs/ASF_Pipeline_v2.svg
    ?? docs/ASF_pipeline_cheatsheet.md
    ?? docs/FINAL_CHECK_LOG.md
    ?? docs/HUMANIZE_LOG.md
    ?? docs/Thesis_Presentation.odp
    ?? docs/Thesis_Presentation_Claude.odp
    ?? docs/crossproduct_figures/
    ?? docs/crossproduct_trends_and_anomalies.md
    ?? docs/crossproduct_trends_and_anomalies_metrics_coverage.md
    ?? docs/delete_/
    ?? docs/figure_scripts/
    ?? docs/images/
    ?? docs/lit_survey/ALVIS_URLs.txt
    ?? docs/lit_survey/asf.txt
    ?? docs/lit_survey/dataset/
    ?? docs/lit_survey/irl_corruptions/
    ?? docs/lit_survey/models/
    ?? docs/lit_survey/motivations/
    ?? docs/lit_survey/robust_benchmarks/
    ?? docs/master_presentation_figures.md
    ?? docs/regenerate_weather_figures_snow_fix.md
    ?? docs/slide_figures_findings1/
    ?? docs/thesis_defense_questions.md
    ?? docs/thesis_defense_questions_draft.md
    ?? docs/thesis_writing_bible.md
    ?? docs/trend_candidates.md
    ?? docs/vAIlt/06_Results/alvis-wipe-audit-2026-08-28.md
    ?? docs/vAIlt/06_Results/crossproduct-rebuild-20260901.md
    ?? docs/vAIlt/06_Results/distance-band-ap-and-churn-recompute-2026-09-04.md
    ?? docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md
    ?? docs/vAIlt/06_Results/frame-identifier-bug-fix-report.md
    ?? docs/vAIlt/06_Results/lidar-gaussian-noise-mechanism-phase1-audit-20260902.md
    ?? docs/vAIlt/06_Results/manual-code-vetting-checklist.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-audit-phase1-2026-08-31.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-bug-audit-2026-08-31.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31-corrected.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31.md
    ?? "docs/vAIlt/3-D LiDAR and Monocular Camera Calibration A Review.md"
    ?? "docs/vAIlt/3D Uncertainty Perspective-N-Points (PnP).md"
    ?? "docs/vAIlt/4D Radar-Camera Calibration and Auto-Labeling.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion_1.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving_1.md"
    ?? "docs/vAIlt/A 4D Radar-Camera Extrinsic Calibration Tool Based on 3D Uncertainty Perspective-N-Points.md"
    ?? "docs/vAIlt/A Continuous-Time Approach for 3D Radar-to-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/A Joint Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/A Low-Cost Temporal-Spatial Calibration Method for Radar and Camera Systems.md"
    ?? "docs/vAIlt/A Review of Environmental Perception Technology Based on Multi-Sensor Information Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A Review of Multi-Sensor Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A low-cost temporal-spatial calibration method for radar and camera systems_1.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and Robust 3D Object Detection in Adverse Conditions through Knowledge Distillation.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and robust 3D object detection in adverse conditions through knowledge distillation_1.md"
    ?? docs/vAIlt/AWARDistill.md
    ?? "docs/vAIlt/AdaptiveFusion LiDAR-Camera Adaptive Fusion for 3D Object Detection.md"
    ?? "docs/vAIlt/AdaptiveFusion Model.md"
    ?? "docs/vAIlt/Adverse Weather Perception.md"
    ?? "docs/vAIlt/Adverse-Weather Perception Robustness.md"
    ?? "docs/vAIlt/An Autonomous Extrinsic Calibration Method for 4D Millimeter-Wave Radar Point Clouds and Visual Images.md"
    ?? "docs/vAIlt/An Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/Anchor-Based 3D Detection.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion_1.md"
    ?? "docs/vAIlt/Automatic Targetless LiDAR-Camera Calibration A Survey.md"
    ?? "docs/vAIlt/Autonomous Driving Perception Safety Standardization.md"
    ?? "docs/vAIlt/Autonomous-Driving Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/Availability-aware Sensor Fusion via Unified Canonical Space.md"
    ?? "docs/vAIlt/BEVFormer (v1).md"
    ?? "docs/vAIlt/BEVFormer v2 Adapting Modern Image Backbones to Bird's-Eye-View Recognition via Perspective Supervision.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation_1.md"
    ?? "docs/vAIlt/Bird's-Eye View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View  3D Object Detection Architectures.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Recognition.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation_1.md"
    ?? "docs/vAIlt/Camera, LiDAR, and IMU Spatiotemporal Calibration Methodological Review and Research Perspectives.md"
    ?? "docs/vAIlt/Camera-Radar Fusion (HVDetFusion).md"
    ?? "docs/vAIlt/Center-Based Object Representation (points, not boxes).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking (CenterPoint).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking.md"
    ?? "docs/vAIlt/Continuous-Time Trajectory Representation.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey_1.md"
    ?? "docs/vAIlt/Deep (Feature-Level) Fusion.md"
    ?? "docs/vAIlt/Deep-Learning-Based Calibration Challenges.md"
    ?? "docs/vAIlt/Delving Into the Secrets of BEV 3D Object Detection in Autonomous Driving A Comprehensive Survey.md"
    ?? "docs/vAIlt/Doppler-Optical Flow Fusion Calibration.md"
    ?? "docs/vAIlt/EA-LSS Edge-Aware Lift-Splat-Shot Framework for 3D BEV Object Detection.md"
    ?? "docs/vAIlt/EA-LSS Edge-aware Lift-splat-shot Framework for 3D BEV Object Detection_1.md"
    ?? "docs/vAIlt/EPSM (Environmental Perception Safety Metric).md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/Early Fusion.md"
    ?? "docs/vAIlt/Echoes Beyond Points Unleashing the Power of Raw Radar Data in Multi-modality Fusion.md"
    ?? "docs/vAIlt/Exploring Radar-Camera Extrinsic Calibration A Deep Learning Perspective and Challenges.md"
    ?? "docs/vAIlt/External Multi-Modal Imaging Sensor Calibration for Sensor Fusion A Review_1.md"
    ?? "docs/vAIlt/External multi-modal imaging sensor calibration for sensor fusion A review.md"
    ?? "docs/vAIlt/Extrinsic 6DoF Calibration of a Radar-LiDAR-Camera System Enhanced by Radar Cross Section Estimates.md"
    ?? "docs/vAIlt/Extrinsic Calibration.md"
    ?? "docs/vAIlt/Extrinsic Sensor Calibration.md"
    ?? "docs/vAIlt/FUTR3D A Unified Sensor Fusion Framework for 3D Detection.md"
    ?? "docs/vAIlt/False Negative  False Positive Error Analysis.md"
    ?? "docs/vAIlt/Fast 3D Object Detection for 4D Imaging Radar Integrating Image Map Features Using Semi-Supervised Learning.md"
    ?? "docs/vAIlt/Fully Connected Pose Estimation (FCPE).md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework.md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework_1.md"
    ?? "docs/vAIlt/Image (Zotero item 6MQUAGUR).md"
    ?? "docs/vAIlt/Intrinsic Calibration.md"
    ?? "docs/vAIlt/Joint Extrinsic Calibration Tool (Radar-Camera-Lidar).md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions.md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions_1.md"
    ?? "docs/vAIlt/K-Radar Dataset.md"
    ?? "docs/vAIlt/Knowledge Distillation.md"
    ?? "docs/vAIlt/Late (Decision-Level) Fusion.md"
    ?? "docs/vAIlt/LiDAR-4D Radar Fusion.md"
    ?? "docs/vAIlt/LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Lift-Splat-Shoot Framework.md"
    ?? "docs/vAIlt/Linear Group RNN.md"
    ?? "docs/vAIlt/Low-Cost Temporal-Spatial Calibration.md"
    ?? "docs/vAIlt/MSAFusion Object Detection Based on Multisensor Adaptive Fusion Under BEV.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection_1.md"
    ?? "docs/vAIlt/MV2DFusion Model.md"
    ?? "docs/vAIlt/Meta-Information-Based Detection Error Analysis (univariate + Random ForestSHAP).md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance.md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance_1.md"
    ?? "docs/vAIlt/Millimeter-Wave Radar-Camera Fusion.md"
    ?? "docs/vAIlt/Minimally Connected Pose Estimation (MCPE).md"
    ?? "docs/vAIlt/Motion-Based Radar-to-Camera Extrinsic Calibration (velocity-based, targetless).md"
    ?? "docs/vAIlt/Multi-Modal Fusion Technology Based on Vehicle Information A Survey.md"
    ?? "docs/vAIlt/Multi-Sensor ExtrinsicTemporal Calibration.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (CameraLiDARRadar).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (Review Taxonomy).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception for Autonomous Driving A Review.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion in Automated Driving A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey_1.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection_1.md"
    ?? "docs/vAIlt/Object Detection in Autonomous Vehicles under Adverse Weather A Review of Traditional and Deep Learning Approaches.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online LiDAR-Camera Extrinsic Parameters Self-Checking and Recalibration.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_2.md"
    ?? "docs/vAIlt/OpenCalib A Multi-Sensor Calibration Toolbox for Autonomous Driving.md"
    ?? "docs/vAIlt/OpenCalib A Multi-sensor Calibration Toolbox for Autonomous Driving_1.md"
    ?? "docs/vAIlt/OpenCalib Toolbox.md"
    ?? "docs/vAIlt/Perception Methods for Adverse Weather Based on Vehicle Infrastructure Cooperation System A Review.md"
    ?? "docs/vAIlt/Perception and Sensing for Autonomous Vehicles Under Adverse Weather Conditions A Survey.md"
    ?? "docs/vAIlt/Perspective Supervision (auxiliary perspective-view detection loss).md"
    ?? docs/vAIlt/PointPillars.md
    ?? "docs/vAIlt/Pose and Structure Estimation (PSE).md"
    ?? "docs/vAIlt/Query-Based Multi-Modal Fusion (FUTR3D).md"
    ?? "docs/vAIlt/RADIATE A Radar Dataset for Automotive Perception in Bad Weather.md"
    ?? "docs/vAIlt/RADIATE Dataset.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network_1.md"
    ?? "docs/vAIlt/RLCNet An End-to-End Deep Learning Framework for Simultaneous Online Calibration of LiDAR, RADAR, and Camera_1.md"
    ?? "docs/vAIlt/RLCNet An end-to-end deep learning framework for simultaneous online calibration of LiDAR, RADAR, and Camera.md"
    ?? "docs/vAIlt/RLCNet Model.md"
    ?? "docs/vAIlt/Radar Cross Section-Enhanced Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey_1.md"
    ?? "docs/vAIlt/Radar-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar-Camera Fusion Taxonomy (whywhatwherewhenhow to fuse).md"
    ?? "docs/vAIlt/Radar-Camera Fusion for Object Detection and Semantic Segmentation in Autonomous Driving A Comprehensive Review.md"
    ?? "docs/vAIlt/Random Forest + Shapley Value Feature Importance.md"
    ?? "docs/vAIlt/Reprojection-Error-Based Extrinsic Calibration.md"
    ?? "docs/vAIlt/Resilient Object Detection for Autonomous Vehicles Integrating Deep Learning and Sensor Fusion.md"
    ?? "docs/vAIlt/Resilient object detection for autonomous vehicles Integrating deep learning and sensor fusion in adverse conditions.md"
    ?? "docs/vAIlt/Review on Millimeter-Wave Radar and Camera Fusion Technology.md"
    ?? "docs/vAIlt/Robustness of Perception under AdverseCorrupted Conditions.md"
    ?? "docs/vAIlt/Robustness-Aware 3D Object Detection in Autonomous Driving A Review and Outlook.md"
    ?? "docs/vAIlt/SACM Dialectical Safety Assurance Case.md"
    ?? "docs/vAIlt/Safe Autonomous Driving in Adverse Weather Sensor Evaluation and Performance Monitoring.md"
    ?? "docs/vAIlt/Safety Assurance for Perception Systems (standardization, metrics, safety cases).md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset.md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset_1.md"
    ?? "docs/vAIlt/Semi-Supervised 4D Radar Object Detection with Image-Map Features.md"
    ?? "docs/vAIlt/Sensor Evaluation and Performance Monitoring in Adverse Weather.md"
    ?? "docs/vAIlt/Simultaneous Online Multi-Sensor Calibration.md"
    ?? "docs/vAIlt/Single Joint Calibration Target Design (radar+camera+lidar).md"
    ?? "docs/vAIlt/Static Multitarget-Based Autocalibration of RGB Cameras, 3-D Radar, and 3-D Lidar Sensors.md"
    ?? "docs/vAIlt/Strong-Fusion  Weak-Fusion Taxonomy (earlydeeplateasymmetry-fusion).md"
    ?? "docs/vAIlt/Systematic Multi-Modal Sensor Calibration.md"
    ?? "docs/vAIlt/Target-Based Calibration.md"
    ?? "docs/vAIlt/Targetless (Target-Free) Calibration.md"
    ?? "docs/vAIlt/Targetless LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar\342\200\223Camera Calibration via Trajectory Alignment.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration of Radar and Camera for Intelligent Transportation Systems.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System_1.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization Progress, Research Advances, and Perspectives.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization, Progress, Research Advances.md"
    ?? "docs/vAIlt/Towards Robust 3D Object Detection with LiDAR and 4D Radar Fusion in Various Weather Conditions.md"
    ?? "docs/vAIlt/Towards Serious Perception Sensor Simulation for Safety Validation of Automated Driving A Collaborative Approach.md"
    ?? "docs/vAIlt/Two-Stage BEV Detector (perspective proposals + BEV head).md"
    ?? "docs/vAIlt/Two-Stage Point-Feature Refinement.md"
    ?? "docs/vAIlt/UniLION Model.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs_1.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation_1.md"
    ?? "docs/vAIlt/UniTR Model.md"
    ?? "docs/vAIlt/V2X-Enabled Cooperative Safety Intelligence.md"
    ?? "docs/vAIlt/Vehicle-Infrastructure Cooperation System.md"
    ?? "docs/vAIlt/Virtual Points (Radar-to-LiDAR Densification).md"
    ?? docs/vAIlt/VoxelNet.md
    ?? "docs/vAIlt/Waymo Open Dataset.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/ZFusion Model.md"
    ?? "docs/vAIlt/_COMMUNITY_3D Detection Performance Influencing-Factor Analysis.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Calibration & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Fusion Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_AV Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather Perception Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather V2I Perception Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV  Center-Based 3D Detection Architectures.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV Fusion Frameworks Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_Cooperative & Query-Based BEV Fusion.md"
    ?? "docs/vAIlt/_COMMUNITY_Deep-Learning-Based Radar-Camera Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Extrinsic Calibration Methods (Targetless  Continuous-Time).md"
    ?? "docs/vAIlt/_COMMUNITY_General Multi-Sensor Fusion Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_LiDAR-Camera Calibration Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_Miscellaneous Image.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Modal Detection Benchmarks & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Sensor Extrinsic Calibration Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Object-Tracking-Based Online Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety & Robustness Assurance.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety Metrics & Evaluation.md"
    ?? "docs/vAIlt/_COMMUNITY_Robust 4D Radar-Camera Fusion under Adverse Weather.md"
    ?? "docs/vAIlt/_COMMUNITY_Safety Assurance Case (SACM) Methodology.md"
    ?? "docs/vAIlt/_COMMUNITY_Sensor Calibration Toolboxes & Reviews (duplicate snapshots).md"
    ?? "docs/vAIlt/_COMMUNITY_UniLION Model (isolated).md"
    ?? "docs/vAIlt/_COMMUNITY_Unified BEV Transformer & Adaptive Fusion Models.md"
    ?? docs/vAIlt/graph.canvas
    ?? docs/vAIlt/noise-injection-smoke-test-report.md
    ?? "docs/vAIlt/nuScenes A Multimodal Dataset for Autonomous Driving.md"
    ?? "docs/vAIlt/nuScenes A multimodal dataset for autonomous driving_1.md"
    ?? "docs/vAIlt/nuScenes Dataset.md"
    ?? graphify-out/
    ?? obsidianVault/Daily/2026-08-26.md
    ?? obsidianVault/Daily/2026-08-27.md
    ?? obsidianVault/Daily/2026-08-28.md
    ?? obsidianVault/Daily/2026-08-31.md
    ?? obsidianVault/Daily/2026-09-01.md
    ?? obsidianVault/Daily/2026-09-02.md
    ?? obsidianVault/Daily/2026-09-03.md
    ?? obsidianVault/Daily/2026-09-07.md
    ?? obsidianVault/Knowledge/asf-availability-told-not-aware.md
    ?? obsidianVault/Knowledge/asf-map-eval-mechanics.md
    ?? obsidianVault/Knowledge/asf-recovery-rate-and-fog-confound.md
    ?? obsidianVault/Knowledge/cri-computed-from-row-table.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-anomaly-addendum.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-frame-key-fix-20260901.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-phase1-audit.md
    ?? obsidianVault/Knowledge/frame-key-derivation-kradar.md
    ?? obsidianVault/Projects/K-Radar/asf-3d-ap-per-weather-2026-09-07.md
    ?? obsidianVault/Projects/K-Radar/context-radar-charts.md
    ?? obsidianVault/Projects/K-Radar/corruption-visual-gallery.md
    ?? obsidianVault/Projects/K-Radar/dataset-distribution-histograms.md
    ?? obsidianVault/Projects/K-Radar/exhaustive-crossproduct-phase2-progress.md
    ?? obsidianVault/Projects/K-Radar/frame-identifier-bug.md
    ?? obsidianVault/Projects/K-Radar/full-denormalized-exploratory-pass.md
    ?? obsidianVault/Projects/K-Radar/official-checkpoint-rerun-2026-08-26.md
    ?? obsidianVault/Projects/K-Radar/results-context-figures-session.md
    ?? obsidianVault/Projects/K-Radar/robustness-bar-charts.md
    ?? obsidianVault/Projects/K-Radar/robustness-metrics-tables.md
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/bar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/box_plots.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/build_denormalized_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/context_radar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct/
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/dataset_distributions.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/density_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_dumbbell_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts_by_modality.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_robustness_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/exploratory_passes.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/fpfn_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/heatmaps.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/merge_churn.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/pass4_stratifier_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/robustness_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_context.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_pass4.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_robustness_line_charts.py
- Python 3.12.13; matplotlib 3.10.8; numpy 1.26.4; polars 1.39.3 (via `uv run --project test-bed`)
- No bootstrap/random seed: ^c$ is a deterministic AP ratio, using K-Radar's unmodified 41-point interpolated AP evaluator (`ap_metrics.py::compute_ap_grouped`)

#### Data provenance
- Input: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond_weather_corrected.parquet`
  sha256: `d911e93691f2fae1b46d3782d408ea26f72629573f859cb56f07ea146bc6098d`, last modified 2026-09-23 16:44:37 +0200, 872,745 rows, 22 distinct conditions, classes {sed, bus}.
  **Canonical-path note:** the logging template names `repos/K-Radar/scripts/alvis/outputs/row_table_iou03.parquet` as canonical; that exact path doesn't exist (a deeper variant `repos/K-Radar/scripts/alvis/outputs/robustness_reports/row_table_iou03.parquet` does). Regardless it is not the correct input for this figure family: it's a per-detection row table consumed by an unrelated script (`test-bed/.../scripts/analysis/radar_charts.py`, severity-tier condition charts, not diversity-axis charts). The diversity-axis radar charts (Figs. 5.8-5.21 and this panel) come exclusively from the pre-aggregated `full_denormalized_table_22cond_weather_corrected.parquet` via `generate_corruption_radar.py` -- confirmed against `Results.tex`'s own figure references.
- Filter/agg chain (inside `compute_axis`, unchanged from `generate_corruption_radar.py`): (1) `df.filter(condition in {original} ∪ {spoke_condition(*s) for s in SPOKES})` -> subset to the 22 needed conditions; (2) `compute_ap_grouped(dff_all, group_by=["condition","cls","environment"])` -> AP + num_gt per (condition, class, category) cell; (3) per spoke, ^c$ = corrupted-AP / baseline-AP if both baseline num_gt >=30 and corrupted num_gt >=30, else NaN (gap in plotted line).
- IoU threshold: 0.3. Class: Sedan (cls=sed). Diversity-axis column: `environment`. Category plotted: `highway`. Severities: low/medium/high for gaussian_noise and loss_partial; single tier for loss_complete_zero.
- Baseline (`original` condition) for this panel: AP=84.34, num_gt=8175 (well above the N>=30 floor -- independently recomputed this session, see Verification)

#### Statistical reporting
- Baseline N reported above; per-corrupted-spoke N not individually enumerated in this session beyond the floor-check already performed inside `compute_axis` (sub-floor spokes become NaN gaps, never plotted as solid values).
- N_sequences: not computed separately this session -- `compute_ap_grouped` pools across all sequences present for this (condition, cls, category) cell in the parquet; sequence-level breakdown is UNVERIFIABLE from this session alone.
- CI method: none -- ^c$ is a point-estimate ratio; no bootstrap/CI shown, consistent with the original thesis figure.
- No sub-floor (N<30) group is plotted as a solid/trusted value on this panel.
- "Significant" is not used on this figure or its caption.

#### Styling
- Shared plotting module: `docs/crossproduct_figures/palette.py` (`MODALITY_COLORS`, `RANK_COLORS`) -- identical to every thesis radar chart.
- Font sizes tuned for a full single-panel chart (title 18pt, tick labels 15pt, y-tick 11pt); not yet checked against actual slide-deck text scale.
- Colorblind safety: not independently re-verified this session -- palette inherited unchanged from the thesis's own module.
- Title on plot: **yes** -- "Sedan robustness under all 21 corruption conditions, Environment=Highway stratum (individual panel cropped from the thesis's diversity-axes environment radar-chart family, Fig. 5.9 area)." -- deviates from the template's "default is no" convention; kept per explicit user instruction this session, since each panel is being cropped out of its original multi-panel context and needs its own label.

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown -- only ^c$ (AP ratio)
- [x] No camera `frame_deletion` conditions included -- confirmed absent from `RADAR_AXIS_EFFECTS`/`SPOKES` in `_lib.py`
- [x] No external/paper figures or images reused -- generated fresh from local parquet this session
- [x] Every number traced to source file above (baseline AP/num_gt independently recomputed, see Verification)
- [ ] Figure visually inspected after rendering -- **NOT satisfied.** Only file existence, PNG dimensions (via `identify`/PIL) and sha256 were checked this session; the rendered image was not opened/viewed. Flagging honestly rather than claiming a check that didn't happen.

#### Verification
- Independently recomputed the baseline (`original`, Sedan (cls=sed), `environment`=`highway`) AP/num_gt cell via a fresh `compute_ap_grouped` call in this session, separate from re-running the plotting script: AP=84.34, num_gt=8175.
- Not diffed against `findings.md`, Q1-Q6 CSVs, or the compiled LaTeX thesis PDF in this session -- this panel is a re-crop of the same underlying computation behind the corresponding published thesis figure (Fig. 5.8/5.9/5.10 family depending on axis), not a new number, but that equivalence has not been explicitly re-verified against the PDF this session.

#### Open issues / caveats
- Visual inspection of the rendered PNG was not performed this session (see unchecked Integrity item above) -- user should open the file before placing it on a slide.
- Canonical-path discrepancy noted above under Data provenance.
- Per-spoke N/coverage beyond the single baseline cell reported here was not enumerated for this panel in this session.

---
### FIG-20260924-193406-claude-slidefigs-bus-weather-normal
**Status:** FINAL
**Supersedes:** N/A — first logged entry for this figure (earlier un-logged transparent-bg / legend-removal / text-edit iterations in this same conversation were overwritten in place before this log existed; only the final state is logged, per no-retroactive-fabrication)
**Logged:** 2026-09-24T19:34:06+02:00 by claude-slidefigs
**Intended slide(s):** Findings slide 1 — "general trends" (unassigned slide number in .odp; user assembling this slide now)
**Story-arc step served:** corruption-sweep results — per-diversity-axis robustness (^c$), individual stratum panel cropped for slide use

#### What the figure shows
- Bus/truck robustness under all 21 corruption conditions, Weather=Normal stratum (individual panel cropped from the thesis's diversity-axes weather radar-chart family, Fig. 5.9-family bus version).
- Plot type: polar/radar chart, one spoke per (modality, effect, severity) condition (21 spokes: camera/LiDAR/radar × {gaussian_noise low/med/high, loss_partial low/med/high, loss_complete_zero}). Radial axis = ^c$ = AP(corrupted)/AP(clean), range 0-1.15, gridlines at 0/.25/.5/.75/1. Class: Bus/truck (cls=bus). Spoke color = modality (camera green / LiDAR blue / radar red, from `docs/crossproduct_figures/palette.py::MODALITY_COLORS`). Per-modality mean-^c$ shown as a shaded arc across that modality's 7 spokes. Worst and second-worst robustness spokes ringed with dashed circles (`palette.py::RANK_COLORS`).
- Deliberately excluded: camera `frame_deletion` (excluded thesis-wide per 2026-08-25 decision, baked into `RADAR_AXIS_EFFECTS`/`SPOKES` in the source script — never in the 21-spoke set). No RCE/mASE/CRI shown.

#### Output files
- `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/bus_weather_normal.png`
- 1716x1780 px, 200 DPI, transparent background (fig+axes patch alpha=0, `savefig(transparent=True)`)
- sha256: `01d81e4484b1a5df635e4a976a3355212ff366ff13c549a4ad339b55e1c97073`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py`, requesting stem `bus_weather_normal` — **new script written this session**, not pre-existing. It is a single-panel adaptation of the thesis's actual multi-panel generator `docs/crossproduct_figures/generate_corruption_radar.py` (confirmed as the true source of thesis Figs. 5.8-5.21 via `docs/Latex_Report/thesis_report/include/Results.tex`).
- Adaptation method: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/_lib.py` is a byte-identical copy of `generate_corruption_radar.py` lines 1-259 (verified via `diff`) -- every function/constant (`compute_axis`, `AXES`, `SPOKES`, `MOD_RANGES`, `CIRCLE_STYLES`, color palette imports) unchanged, with only the trailing top-level `for axis_key ...` batch-generation loop (original lines 260-265) removed, since that loop unconditionally regenerates every thesis figure on import. `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/palette.py` is byte-identical to `docs/crossproduct_figures/palette.py` (sha256 `acfb5f38dbe4c5b923e3edf409c6cf2ff8787fef5dd95672bcacaaa573a626c2` matches both).
- `make_single.py`'s `make_single_panel()` reproduces `generate_corruption_radar.py::make_figure()`'s per-panel plotting logic (same mean-arc computation, same worst/second-worst ring logic, same tick/color logic) for exactly one (class, category) pair instead of a 2x2 grid. Per user instructions this session: per-panel title changed to "Axis - Category (Class)"; shared bottom legend removed entirely (logged separately as `radar_chart_legend.png`); background made transparent.
- Exact command (from `/home/adhish/Productivity/AMSCUP/test-bed`, no special env vars):
```
uv run --project . python /home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py
```
  (generates all 6 individual-panel figures in one run, including this one)
- Git commit at generation time: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree was DIRTY. Dirty/untracked files (abbreviated; full list was captured via `git status --porcelain` at generation time and is stable across all entries in this batch):
     M CLAUDE.md
     D docs/Adyuth_Hisham_resume_PartTime.docx.md
     M docs/Latex_Report
     M docs/vAIlt/.obsidian/workspace.json
     M obsidianVault/.obsidian/workspace.json
     M obsidianVault/Knowledge/asf-training-inputs.md
     M obsidianVault/Knowledge/robustness-metric-selection.md
     M obsidianVault/Projects/K-Radar/asf-corruption-study-alvis.md
     M obsidianVault/Projects/K-Radar/robustness-radar-charts.md
     M repos/K-Radar
     M test-bed/src/Modules/robust_testing/kradar/scripts/analysis/radar_charts.py
     M test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py
    ?? .agents/
    ?? FinalTerm_Presentation_Claude.odp
    ?? alvis_archive_2026-08-28/
    ?? backups/
    ?? docs/.master_presentation_figures.lock
    ?? docs/.~lock.Thesis_Presentation_Claude.odp#
    ?? docs/ASF_KRadar_Adversarial_Review.md
    ?? docs/ASF_Pipeline.backup.svg
    ?? docs/ASF_Pipeline.svg
    ?? docs/ASF_Pipeline_slide.svg
    ?? docs/ASF_Pipeline_v2.svg
    ?? docs/ASF_pipeline_cheatsheet.md
    ?? docs/FINAL_CHECK_LOG.md
    ?? docs/HUMANIZE_LOG.md
    ?? docs/Thesis_Presentation.odp
    ?? docs/Thesis_Presentation_Claude.odp
    ?? docs/crossproduct_figures/
    ?? docs/crossproduct_trends_and_anomalies.md
    ?? docs/crossproduct_trends_and_anomalies_metrics_coverage.md
    ?? docs/delete_/
    ?? docs/figure_scripts/
    ?? docs/images/
    ?? docs/lit_survey/ALVIS_URLs.txt
    ?? docs/lit_survey/asf.txt
    ?? docs/lit_survey/dataset/
    ?? docs/lit_survey/irl_corruptions/
    ?? docs/lit_survey/models/
    ?? docs/lit_survey/motivations/
    ?? docs/lit_survey/robust_benchmarks/
    ?? docs/master_presentation_figures.md
    ?? docs/regenerate_weather_figures_snow_fix.md
    ?? docs/slide_figures_findings1/
    ?? docs/thesis_defense_questions.md
    ?? docs/thesis_defense_questions_draft.md
    ?? docs/thesis_writing_bible.md
    ?? docs/trend_candidates.md
    ?? docs/vAIlt/06_Results/alvis-wipe-audit-2026-08-28.md
    ?? docs/vAIlt/06_Results/crossproduct-rebuild-20260901.md
    ?? docs/vAIlt/06_Results/distance-band-ap-and-churn-recompute-2026-09-04.md
    ?? docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md
    ?? docs/vAIlt/06_Results/frame-identifier-bug-fix-report.md
    ?? docs/vAIlt/06_Results/lidar-gaussian-noise-mechanism-phase1-audit-20260902.md
    ?? docs/vAIlt/06_Results/manual-code-vetting-checklist.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-audit-phase1-2026-08-31.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-bug-audit-2026-08-31.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31-corrected.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31.md
    ?? "docs/vAIlt/3-D LiDAR and Monocular Camera Calibration A Review.md"
    ?? "docs/vAIlt/3D Uncertainty Perspective-N-Points (PnP).md"
    ?? "docs/vAIlt/4D Radar-Camera Calibration and Auto-Labeling.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion_1.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving_1.md"
    ?? "docs/vAIlt/A 4D Radar-Camera Extrinsic Calibration Tool Based on 3D Uncertainty Perspective-N-Points.md"
    ?? "docs/vAIlt/A Continuous-Time Approach for 3D Radar-to-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/A Joint Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/A Low-Cost Temporal-Spatial Calibration Method for Radar and Camera Systems.md"
    ?? "docs/vAIlt/A Review of Environmental Perception Technology Based on Multi-Sensor Information Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A Review of Multi-Sensor Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A low-cost temporal-spatial calibration method for radar and camera systems_1.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and Robust 3D Object Detection in Adverse Conditions through Knowledge Distillation.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and robust 3D object detection in adverse conditions through knowledge distillation_1.md"
    ?? docs/vAIlt/AWARDistill.md
    ?? "docs/vAIlt/AdaptiveFusion LiDAR-Camera Adaptive Fusion for 3D Object Detection.md"
    ?? "docs/vAIlt/AdaptiveFusion Model.md"
    ?? "docs/vAIlt/Adverse Weather Perception.md"
    ?? "docs/vAIlt/Adverse-Weather Perception Robustness.md"
    ?? "docs/vAIlt/An Autonomous Extrinsic Calibration Method for 4D Millimeter-Wave Radar Point Clouds and Visual Images.md"
    ?? "docs/vAIlt/An Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/Anchor-Based 3D Detection.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion_1.md"
    ?? "docs/vAIlt/Automatic Targetless LiDAR-Camera Calibration A Survey.md"
    ?? "docs/vAIlt/Autonomous Driving Perception Safety Standardization.md"
    ?? "docs/vAIlt/Autonomous-Driving Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/Availability-aware Sensor Fusion via Unified Canonical Space.md"
    ?? "docs/vAIlt/BEVFormer (v1).md"
    ?? "docs/vAIlt/BEVFormer v2 Adapting Modern Image Backbones to Bird's-Eye-View Recognition via Perspective Supervision.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation_1.md"
    ?? "docs/vAIlt/Bird's-Eye View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View  3D Object Detection Architectures.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Recognition.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation_1.md"
    ?? "docs/vAIlt/Camera, LiDAR, and IMU Spatiotemporal Calibration Methodological Review and Research Perspectives.md"
    ?? "docs/vAIlt/Camera-Radar Fusion (HVDetFusion).md"
    ?? "docs/vAIlt/Center-Based Object Representation (points, not boxes).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking (CenterPoint).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking.md"
    ?? "docs/vAIlt/Continuous-Time Trajectory Representation.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey_1.md"
    ?? "docs/vAIlt/Deep (Feature-Level) Fusion.md"
    ?? "docs/vAIlt/Deep-Learning-Based Calibration Challenges.md"
    ?? "docs/vAIlt/Delving Into the Secrets of BEV 3D Object Detection in Autonomous Driving A Comprehensive Survey.md"
    ?? "docs/vAIlt/Doppler-Optical Flow Fusion Calibration.md"
    ?? "docs/vAIlt/EA-LSS Edge-Aware Lift-Splat-Shot Framework for 3D BEV Object Detection.md"
    ?? "docs/vAIlt/EA-LSS Edge-aware Lift-splat-shot Framework for 3D BEV Object Detection_1.md"
    ?? "docs/vAIlt/EPSM (Environmental Perception Safety Metric).md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/Early Fusion.md"
    ?? "docs/vAIlt/Echoes Beyond Points Unleashing the Power of Raw Radar Data in Multi-modality Fusion.md"
    ?? "docs/vAIlt/Exploring Radar-Camera Extrinsic Calibration A Deep Learning Perspective and Challenges.md"
    ?? "docs/vAIlt/External Multi-Modal Imaging Sensor Calibration for Sensor Fusion A Review_1.md"
    ?? "docs/vAIlt/External multi-modal imaging sensor calibration for sensor fusion A review.md"
    ?? "docs/vAIlt/Extrinsic 6DoF Calibration of a Radar-LiDAR-Camera System Enhanced by Radar Cross Section Estimates.md"
    ?? "docs/vAIlt/Extrinsic Calibration.md"
    ?? "docs/vAIlt/Extrinsic Sensor Calibration.md"
    ?? "docs/vAIlt/FUTR3D A Unified Sensor Fusion Framework for 3D Detection.md"
    ?? "docs/vAIlt/False Negative  False Positive Error Analysis.md"
    ?? "docs/vAIlt/Fast 3D Object Detection for 4D Imaging Radar Integrating Image Map Features Using Semi-Supervised Learning.md"
    ?? "docs/vAIlt/Fully Connected Pose Estimation (FCPE).md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework.md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework_1.md"
    ?? "docs/vAIlt/Image (Zotero item 6MQUAGUR).md"
    ?? "docs/vAIlt/Intrinsic Calibration.md"
    ?? "docs/vAIlt/Joint Extrinsic Calibration Tool (Radar-Camera-Lidar).md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions.md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions_1.md"
    ?? "docs/vAIlt/K-Radar Dataset.md"
    ?? "docs/vAIlt/Knowledge Distillation.md"
    ?? "docs/vAIlt/Late (Decision-Level) Fusion.md"
    ?? "docs/vAIlt/LiDAR-4D Radar Fusion.md"
    ?? "docs/vAIlt/LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Lift-Splat-Shoot Framework.md"
    ?? "docs/vAIlt/Linear Group RNN.md"
    ?? "docs/vAIlt/Low-Cost Temporal-Spatial Calibration.md"
    ?? "docs/vAIlt/MSAFusion Object Detection Based on Multisensor Adaptive Fusion Under BEV.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection_1.md"
    ?? "docs/vAIlt/MV2DFusion Model.md"
    ?? "docs/vAIlt/Meta-Information-Based Detection Error Analysis (univariate + Random ForestSHAP).md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance.md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance_1.md"
    ?? "docs/vAIlt/Millimeter-Wave Radar-Camera Fusion.md"
    ?? "docs/vAIlt/Minimally Connected Pose Estimation (MCPE).md"
    ?? "docs/vAIlt/Motion-Based Radar-to-Camera Extrinsic Calibration (velocity-based, targetless).md"
    ?? "docs/vAIlt/Multi-Modal Fusion Technology Based on Vehicle Information A Survey.md"
    ?? "docs/vAIlt/Multi-Sensor ExtrinsicTemporal Calibration.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (CameraLiDARRadar).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (Review Taxonomy).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception for Autonomous Driving A Review.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion in Automated Driving A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey_1.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection_1.md"
    ?? "docs/vAIlt/Object Detection in Autonomous Vehicles under Adverse Weather A Review of Traditional and Deep Learning Approaches.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online LiDAR-Camera Extrinsic Parameters Self-Checking and Recalibration.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_2.md"
    ?? "docs/vAIlt/OpenCalib A Multi-Sensor Calibration Toolbox for Autonomous Driving.md"
    ?? "docs/vAIlt/OpenCalib A Multi-sensor Calibration Toolbox for Autonomous Driving_1.md"
    ?? "docs/vAIlt/OpenCalib Toolbox.md"
    ?? "docs/vAIlt/Perception Methods for Adverse Weather Based on Vehicle Infrastructure Cooperation System A Review.md"
    ?? "docs/vAIlt/Perception and Sensing for Autonomous Vehicles Under Adverse Weather Conditions A Survey.md"
    ?? "docs/vAIlt/Perspective Supervision (auxiliary perspective-view detection loss).md"
    ?? docs/vAIlt/PointPillars.md
    ?? "docs/vAIlt/Pose and Structure Estimation (PSE).md"
    ?? "docs/vAIlt/Query-Based Multi-Modal Fusion (FUTR3D).md"
    ?? "docs/vAIlt/RADIATE A Radar Dataset for Automotive Perception in Bad Weather.md"
    ?? "docs/vAIlt/RADIATE Dataset.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network_1.md"
    ?? "docs/vAIlt/RLCNet An End-to-End Deep Learning Framework for Simultaneous Online Calibration of LiDAR, RADAR, and Camera_1.md"
    ?? "docs/vAIlt/RLCNet An end-to-end deep learning framework for simultaneous online calibration of LiDAR, RADAR, and Camera.md"
    ?? "docs/vAIlt/RLCNet Model.md"
    ?? "docs/vAIlt/Radar Cross Section-Enhanced Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey_1.md"
    ?? "docs/vAIlt/Radar-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar-Camera Fusion Taxonomy (whywhatwherewhenhow to fuse).md"
    ?? "docs/vAIlt/Radar-Camera Fusion for Object Detection and Semantic Segmentation in Autonomous Driving A Comprehensive Review.md"
    ?? "docs/vAIlt/Random Forest + Shapley Value Feature Importance.md"
    ?? "docs/vAIlt/Reprojection-Error-Based Extrinsic Calibration.md"
    ?? "docs/vAIlt/Resilient Object Detection for Autonomous Vehicles Integrating Deep Learning and Sensor Fusion.md"
    ?? "docs/vAIlt/Resilient object detection for autonomous vehicles Integrating deep learning and sensor fusion in adverse conditions.md"
    ?? "docs/vAIlt/Review on Millimeter-Wave Radar and Camera Fusion Technology.md"
    ?? "docs/vAIlt/Robustness of Perception under AdverseCorrupted Conditions.md"
    ?? "docs/vAIlt/Robustness-Aware 3D Object Detection in Autonomous Driving A Review and Outlook.md"
    ?? "docs/vAIlt/SACM Dialectical Safety Assurance Case.md"
    ?? "docs/vAIlt/Safe Autonomous Driving in Adverse Weather Sensor Evaluation and Performance Monitoring.md"
    ?? "docs/vAIlt/Safety Assurance for Perception Systems (standardization, metrics, safety cases).md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset.md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset_1.md"
    ?? "docs/vAIlt/Semi-Supervised 4D Radar Object Detection with Image-Map Features.md"
    ?? "docs/vAIlt/Sensor Evaluation and Performance Monitoring in Adverse Weather.md"
    ?? "docs/vAIlt/Simultaneous Online Multi-Sensor Calibration.md"
    ?? "docs/vAIlt/Single Joint Calibration Target Design (radar+camera+lidar).md"
    ?? "docs/vAIlt/Static Multitarget-Based Autocalibration of RGB Cameras, 3-D Radar, and 3-D Lidar Sensors.md"
    ?? "docs/vAIlt/Strong-Fusion  Weak-Fusion Taxonomy (earlydeeplateasymmetry-fusion).md"
    ?? "docs/vAIlt/Systematic Multi-Modal Sensor Calibration.md"
    ?? "docs/vAIlt/Target-Based Calibration.md"
    ?? "docs/vAIlt/Targetless (Target-Free) Calibration.md"
    ?? "docs/vAIlt/Targetless LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar\342\200\223Camera Calibration via Trajectory Alignment.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration of Radar and Camera for Intelligent Transportation Systems.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System_1.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization Progress, Research Advances, and Perspectives.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization, Progress, Research Advances.md"
    ?? "docs/vAIlt/Towards Robust 3D Object Detection with LiDAR and 4D Radar Fusion in Various Weather Conditions.md"
    ?? "docs/vAIlt/Towards Serious Perception Sensor Simulation for Safety Validation of Automated Driving A Collaborative Approach.md"
    ?? "docs/vAIlt/Two-Stage BEV Detector (perspective proposals + BEV head).md"
    ?? "docs/vAIlt/Two-Stage Point-Feature Refinement.md"
    ?? "docs/vAIlt/UniLION Model.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs_1.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation_1.md"
    ?? "docs/vAIlt/UniTR Model.md"
    ?? "docs/vAIlt/V2X-Enabled Cooperative Safety Intelligence.md"
    ?? "docs/vAIlt/Vehicle-Infrastructure Cooperation System.md"
    ?? "docs/vAIlt/Virtual Points (Radar-to-LiDAR Densification).md"
    ?? docs/vAIlt/VoxelNet.md
    ?? "docs/vAIlt/Waymo Open Dataset.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/ZFusion Model.md"
    ?? "docs/vAIlt/_COMMUNITY_3D Detection Performance Influencing-Factor Analysis.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Calibration & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Fusion Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_AV Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather Perception Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather V2I Perception Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV  Center-Based 3D Detection Architectures.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV Fusion Frameworks Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_Cooperative & Query-Based BEV Fusion.md"
    ?? "docs/vAIlt/_COMMUNITY_Deep-Learning-Based Radar-Camera Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Extrinsic Calibration Methods (Targetless  Continuous-Time).md"
    ?? "docs/vAIlt/_COMMUNITY_General Multi-Sensor Fusion Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_LiDAR-Camera Calibration Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_Miscellaneous Image.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Modal Detection Benchmarks & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Sensor Extrinsic Calibration Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Object-Tracking-Based Online Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety & Robustness Assurance.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety Metrics & Evaluation.md"
    ?? "docs/vAIlt/_COMMUNITY_Robust 4D Radar-Camera Fusion under Adverse Weather.md"
    ?? "docs/vAIlt/_COMMUNITY_Safety Assurance Case (SACM) Methodology.md"
    ?? "docs/vAIlt/_COMMUNITY_Sensor Calibration Toolboxes & Reviews (duplicate snapshots).md"
    ?? "docs/vAIlt/_COMMUNITY_UniLION Model (isolated).md"
    ?? "docs/vAIlt/_COMMUNITY_Unified BEV Transformer & Adaptive Fusion Models.md"
    ?? docs/vAIlt/graph.canvas
    ?? docs/vAIlt/noise-injection-smoke-test-report.md
    ?? "docs/vAIlt/nuScenes A Multimodal Dataset for Autonomous Driving.md"
    ?? "docs/vAIlt/nuScenes A multimodal dataset for autonomous driving_1.md"
    ?? "docs/vAIlt/nuScenes Dataset.md"
    ?? graphify-out/
    ?? obsidianVault/Daily/2026-08-26.md
    ?? obsidianVault/Daily/2026-08-27.md
    ?? obsidianVault/Daily/2026-08-28.md
    ?? obsidianVault/Daily/2026-08-31.md
    ?? obsidianVault/Daily/2026-09-01.md
    ?? obsidianVault/Daily/2026-09-02.md
    ?? obsidianVault/Daily/2026-09-03.md
    ?? obsidianVault/Daily/2026-09-07.md
    ?? obsidianVault/Knowledge/asf-availability-told-not-aware.md
    ?? obsidianVault/Knowledge/asf-map-eval-mechanics.md
    ?? obsidianVault/Knowledge/asf-recovery-rate-and-fog-confound.md
    ?? obsidianVault/Knowledge/cri-computed-from-row-table.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-anomaly-addendum.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-frame-key-fix-20260901.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-phase1-audit.md
    ?? obsidianVault/Knowledge/frame-key-derivation-kradar.md
    ?? obsidianVault/Projects/K-Radar/asf-3d-ap-per-weather-2026-09-07.md
    ?? obsidianVault/Projects/K-Radar/context-radar-charts.md
    ?? obsidianVault/Projects/K-Radar/corruption-visual-gallery.md
    ?? obsidianVault/Projects/K-Radar/dataset-distribution-histograms.md
    ?? obsidianVault/Projects/K-Radar/exhaustive-crossproduct-phase2-progress.md
    ?? obsidianVault/Projects/K-Radar/frame-identifier-bug.md
    ?? obsidianVault/Projects/K-Radar/full-denormalized-exploratory-pass.md
    ?? obsidianVault/Projects/K-Radar/official-checkpoint-rerun-2026-08-26.md
    ?? obsidianVault/Projects/K-Radar/results-context-figures-session.md
    ?? obsidianVault/Projects/K-Radar/robustness-bar-charts.md
    ?? obsidianVault/Projects/K-Radar/robustness-metrics-tables.md
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/bar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/box_plots.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/build_denormalized_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/context_radar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct/
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/dataset_distributions.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/density_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_dumbbell_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts_by_modality.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_robustness_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/exploratory_passes.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/fpfn_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/heatmaps.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/merge_churn.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/pass4_stratifier_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/robustness_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_context.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_pass4.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_robustness_line_charts.py
- Python 3.12.13; matplotlib 3.10.8; numpy 1.26.4; polars 1.39.3 (via `uv run --project test-bed`)
- No bootstrap/random seed: ^c$ is a deterministic AP ratio, using K-Radar's unmodified 41-point interpolated AP evaluator (`ap_metrics.py::compute_ap_grouped`)

#### Data provenance
- Input: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond_weather_corrected.parquet`
  sha256: `d911e93691f2fae1b46d3782d408ea26f72629573f859cb56f07ea146bc6098d`, last modified 2026-09-23 16:44:37 +0200, 872,745 rows, 22 distinct conditions, classes {sed, bus}.
  **Canonical-path note:** the logging template names `repos/K-Radar/scripts/alvis/outputs/row_table_iou03.parquet` as canonical; that exact path doesn't exist (a deeper variant `repos/K-Radar/scripts/alvis/outputs/robustness_reports/row_table_iou03.parquet` does). Regardless it is not the correct input for this figure family: it's a per-detection row table consumed by an unrelated script (`test-bed/.../scripts/analysis/radar_charts.py`, severity-tier condition charts, not diversity-axis charts). The diversity-axis radar charts (Figs. 5.8-5.21 and this panel) come exclusively from the pre-aggregated `full_denormalized_table_22cond_weather_corrected.parquet` via `generate_corruption_radar.py` -- confirmed against `Results.tex`'s own figure references.
- Filter/agg chain (inside `compute_axis`, unchanged from `generate_corruption_radar.py`): (1) `df.filter(condition in {original} ∪ {spoke_condition(*s) for s in SPOKES})` -> subset to the 22 needed conditions; (2) `compute_ap_grouped(dff_all, group_by=["condition","cls","weather"])` -> AP + num_gt per (condition, class, category) cell; (3) per spoke, ^c$ = corrupted-AP / baseline-AP if both baseline num_gt >=30 and corrupted num_gt >=30, else NaN (gap in plotted line).
- IoU threshold: 0.3. Class: Bus/truck (cls=bus). Diversity-axis column: `weather`. Category plotted: `normal`. Severities: low/medium/high for gaussian_noise and loss_partial; single tier for loss_complete_zero.
- Baseline (`original` condition) for this panel: AP=57.43, num_gt=2763 (well above the N>=30 floor -- independently recomputed this session, see Verification)

#### Statistical reporting
- Baseline N reported above; per-corrupted-spoke N not individually enumerated in this session beyond the floor-check already performed inside `compute_axis` (sub-floor spokes become NaN gaps, never plotted as solid values).
- N_sequences: not computed separately this session -- `compute_ap_grouped` pools across all sequences present for this (condition, cls, category) cell in the parquet; sequence-level breakdown is UNVERIFIABLE from this session alone.
- CI method: none -- ^c$ is a point-estimate ratio; no bootstrap/CI shown, consistent with the original thesis figure.
- No sub-floor (N<30) group is plotted as a solid/trusted value on this panel.
- "Significant" is not used on this figure or its caption.

#### Styling
- Shared plotting module: `docs/crossproduct_figures/palette.py` (`MODALITY_COLORS`, `RANK_COLORS`) -- identical to every thesis radar chart.
- Font sizes tuned for a full single-panel chart (title 18pt, tick labels 15pt, y-tick 11pt); not yet checked against actual slide-deck text scale.
- Colorblind safety: not independently re-verified this session -- palette inherited unchanged from the thesis's own module.
- Title on plot: **yes** -- "Bus/truck robustness under all 21 corruption conditions, Weather=Normal stratum (individual panel cropped from the thesis's diversity-axes weather radar-chart family, Fig. 5.9-family bus version)." -- deviates from the template's "default is no" convention; kept per explicit user instruction this session, since each panel is being cropped out of its original multi-panel context and needs its own label.

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown -- only ^c$ (AP ratio)
- [x] No camera `frame_deletion` conditions included -- confirmed absent from `RADAR_AXIS_EFFECTS`/`SPOKES` in `_lib.py`
- [x] No external/paper figures or images reused -- generated fresh from local parquet this session
- [x] Every number traced to source file above (baseline AP/num_gt independently recomputed, see Verification)
- [ ] Figure visually inspected after rendering -- **NOT satisfied.** Only file existence, PNG dimensions (via `identify`/PIL) and sha256 were checked this session; the rendered image was not opened/viewed. Flagging honestly rather than claiming a check that didn't happen.

#### Verification
- Independently recomputed the baseline (`original`, Bus/truck (cls=bus), `weather`=`normal`) AP/num_gt cell via a fresh `compute_ap_grouped` call in this session, separate from re-running the plotting script: AP=57.43, num_gt=2763.
- Not diffed against `findings.md`, Q1-Q6 CSVs, or the compiled LaTeX thesis PDF in this session -- this panel is a re-crop of the same underlying computation behind the corresponding published thesis figure (Fig. 5.8/5.9/5.10 family depending on axis), not a new number, but that equivalence has not been explicitly re-verified against the PDF this session.

#### Open issues / caveats
- Visual inspection of the rendered PNG was not performed this session (see unchecked Integrity item above) -- user should open the file before placing it on a slide.
- Canonical-path discrepancy noted above under Data provenance.
- Per-spoke N/coverage beyond the single baseline cell reported here was not enumerated for this panel in this session.

---
### FIG-20260924-193406-claude-slidefigs-bus-env-highway
**Status:** FINAL
**Supersedes:** N/A — first logged entry for this figure (earlier un-logged transparent-bg / legend-removal / text-edit iterations in this same conversation were overwritten in place before this log existed; only the final state is logged, per no-retroactive-fabrication)
**Logged:** 2026-09-24T19:34:06+02:00 by claude-slidefigs
**Intended slide(s):** Findings slide 1 — "general trends" (unassigned slide number in .odp; user assembling this slide now)
**Story-arc step served:** corruption-sweep results — per-diversity-axis robustness (^c$), individual stratum panel cropped for slide use

#### What the figure shows
- Bus/truck robustness under all 21 corruption conditions, Environment=Highway stratum (individual panel cropped from the thesis's diversity-axes environment radar-chart family, bus version).
- Plot type: polar/radar chart, one spoke per (modality, effect, severity) condition (21 spokes: camera/LiDAR/radar × {gaussian_noise low/med/high, loss_partial low/med/high, loss_complete_zero}). Radial axis = ^c$ = AP(corrupted)/AP(clean), range 0-1.15, gridlines at 0/.25/.5/.75/1. Class: Bus/truck (cls=bus). Spoke color = modality (camera green / LiDAR blue / radar red, from `docs/crossproduct_figures/palette.py::MODALITY_COLORS`). Per-modality mean-^c$ shown as a shaded arc across that modality's 7 spokes. Worst and second-worst robustness spokes ringed with dashed circles (`palette.py::RANK_COLORS`).
- Deliberately excluded: camera `frame_deletion` (excluded thesis-wide per 2026-08-25 decision, baked into `RADAR_AXIS_EFFECTS`/`SPOKES` in the source script — never in the 21-spoke set). No RCE/mASE/CRI shown.

#### Output files
- `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/bus_env_highway.png`
- 1716x1780 px, 200 DPI, transparent background (fig+axes patch alpha=0, `savefig(transparent=True)`)
- sha256: `b010b10401837f5ede0c62d4aceacfa445cf29e6d8d618765bf887e999e4bfc4`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py`, requesting stem `bus_env_highway` — **new script written this session**, not pre-existing. It is a single-panel adaptation of the thesis's actual multi-panel generator `docs/crossproduct_figures/generate_corruption_radar.py` (confirmed as the true source of thesis Figs. 5.8-5.21 via `docs/Latex_Report/thesis_report/include/Results.tex`).
- Adaptation method: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/_lib.py` is a byte-identical copy of `generate_corruption_radar.py` lines 1-259 (verified via `diff`) -- every function/constant (`compute_axis`, `AXES`, `SPOKES`, `MOD_RANGES`, `CIRCLE_STYLES`, color palette imports) unchanged, with only the trailing top-level `for axis_key ...` batch-generation loop (original lines 260-265) removed, since that loop unconditionally regenerates every thesis figure on import. `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/palette.py` is byte-identical to `docs/crossproduct_figures/palette.py` (sha256 `acfb5f38dbe4c5b923e3edf409c6cf2ff8787fef5dd95672bcacaaa573a626c2` matches both).
- `make_single.py`'s `make_single_panel()` reproduces `generate_corruption_radar.py::make_figure()`'s per-panel plotting logic (same mean-arc computation, same worst/second-worst ring logic, same tick/color logic) for exactly one (class, category) pair instead of a 2x2 grid. Per user instructions this session: per-panel title changed to "Axis - Category (Class)"; shared bottom legend removed entirely (logged separately as `radar_chart_legend.png`); background made transparent.
- Exact command (from `/home/adhish/Productivity/AMSCUP/test-bed`, no special env vars):
```
uv run --project . python /home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_single.py
```
  (generates all 6 individual-panel figures in one run, including this one)
- Git commit at generation time: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree was DIRTY. Dirty/untracked files (abbreviated; full list was captured via `git status --porcelain` at generation time and is stable across all entries in this batch):
     M CLAUDE.md
     D docs/Adyuth_Hisham_resume_PartTime.docx.md
     M docs/Latex_Report
     M docs/vAIlt/.obsidian/workspace.json
     M obsidianVault/.obsidian/workspace.json
     M obsidianVault/Knowledge/asf-training-inputs.md
     M obsidianVault/Knowledge/robustness-metric-selection.md
     M obsidianVault/Projects/K-Radar/asf-corruption-study-alvis.md
     M obsidianVault/Projects/K-Radar/robustness-radar-charts.md
     M repos/K-Radar
     M test-bed/src/Modules/robust_testing/kradar/scripts/analysis/radar_charts.py
     M test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py
    ?? .agents/
    ?? FinalTerm_Presentation_Claude.odp
    ?? alvis_archive_2026-08-28/
    ?? backups/
    ?? docs/.master_presentation_figures.lock
    ?? docs/.~lock.Thesis_Presentation_Claude.odp#
    ?? docs/ASF_KRadar_Adversarial_Review.md
    ?? docs/ASF_Pipeline.backup.svg
    ?? docs/ASF_Pipeline.svg
    ?? docs/ASF_Pipeline_slide.svg
    ?? docs/ASF_Pipeline_v2.svg
    ?? docs/ASF_pipeline_cheatsheet.md
    ?? docs/FINAL_CHECK_LOG.md
    ?? docs/HUMANIZE_LOG.md
    ?? docs/Thesis_Presentation.odp
    ?? docs/Thesis_Presentation_Claude.odp
    ?? docs/crossproduct_figures/
    ?? docs/crossproduct_trends_and_anomalies.md
    ?? docs/crossproduct_trends_and_anomalies_metrics_coverage.md
    ?? docs/delete_/
    ?? docs/figure_scripts/
    ?? docs/images/
    ?? docs/lit_survey/ALVIS_URLs.txt
    ?? docs/lit_survey/asf.txt
    ?? docs/lit_survey/dataset/
    ?? docs/lit_survey/irl_corruptions/
    ?? docs/lit_survey/models/
    ?? docs/lit_survey/motivations/
    ?? docs/lit_survey/robust_benchmarks/
    ?? docs/master_presentation_figures.md
    ?? docs/regenerate_weather_figures_snow_fix.md
    ?? docs/slide_figures_findings1/
    ?? docs/thesis_defense_questions.md
    ?? docs/thesis_defense_questions_draft.md
    ?? docs/thesis_writing_bible.md
    ?? docs/trend_candidates.md
    ?? docs/vAIlt/06_Results/alvis-wipe-audit-2026-08-28.md
    ?? docs/vAIlt/06_Results/crossproduct-rebuild-20260901.md
    ?? docs/vAIlt/06_Results/distance-band-ap-and-churn-recompute-2026-09-04.md
    ?? docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md
    ?? docs/vAIlt/06_Results/frame-identifier-bug-fix-report.md
    ?? docs/vAIlt/06_Results/lidar-gaussian-noise-mechanism-phase1-audit-20260902.md
    ?? docs/vAIlt/06_Results/manual-code-vetting-checklist.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-audit-phase1-2026-08-31.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-bug-audit-2026-08-31.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31-corrected.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31.md
    ?? "docs/vAIlt/3-D LiDAR and Monocular Camera Calibration A Review.md"
    ?? "docs/vAIlt/3D Uncertainty Perspective-N-Points (PnP).md"
    ?? "docs/vAIlt/4D Radar-Camera Calibration and Auto-Labeling.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion_1.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving_1.md"
    ?? "docs/vAIlt/A 4D Radar-Camera Extrinsic Calibration Tool Based on 3D Uncertainty Perspective-N-Points.md"
    ?? "docs/vAIlt/A Continuous-Time Approach for 3D Radar-to-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/A Joint Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/A Low-Cost Temporal-Spatial Calibration Method for Radar and Camera Systems.md"
    ?? "docs/vAIlt/A Review of Environmental Perception Technology Based on Multi-Sensor Information Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A Review of Multi-Sensor Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A low-cost temporal-spatial calibration method for radar and camera systems_1.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and Robust 3D Object Detection in Adverse Conditions through Knowledge Distillation.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and robust 3D object detection in adverse conditions through knowledge distillation_1.md"
    ?? docs/vAIlt/AWARDistill.md
    ?? "docs/vAIlt/AdaptiveFusion LiDAR-Camera Adaptive Fusion for 3D Object Detection.md"
    ?? "docs/vAIlt/AdaptiveFusion Model.md"
    ?? "docs/vAIlt/Adverse Weather Perception.md"
    ?? "docs/vAIlt/Adverse-Weather Perception Robustness.md"
    ?? "docs/vAIlt/An Autonomous Extrinsic Calibration Method for 4D Millimeter-Wave Radar Point Clouds and Visual Images.md"
    ?? "docs/vAIlt/An Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/Anchor-Based 3D Detection.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion_1.md"
    ?? "docs/vAIlt/Automatic Targetless LiDAR-Camera Calibration A Survey.md"
    ?? "docs/vAIlt/Autonomous Driving Perception Safety Standardization.md"
    ?? "docs/vAIlt/Autonomous-Driving Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/Availability-aware Sensor Fusion via Unified Canonical Space.md"
    ?? "docs/vAIlt/BEVFormer (v1).md"
    ?? "docs/vAIlt/BEVFormer v2 Adapting Modern Image Backbones to Bird's-Eye-View Recognition via Perspective Supervision.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation_1.md"
    ?? "docs/vAIlt/Bird's-Eye View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View  3D Object Detection Architectures.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Recognition.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation_1.md"
    ?? "docs/vAIlt/Camera, LiDAR, and IMU Spatiotemporal Calibration Methodological Review and Research Perspectives.md"
    ?? "docs/vAIlt/Camera-Radar Fusion (HVDetFusion).md"
    ?? "docs/vAIlt/Center-Based Object Representation (points, not boxes).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking (CenterPoint).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking.md"
    ?? "docs/vAIlt/Continuous-Time Trajectory Representation.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey_1.md"
    ?? "docs/vAIlt/Deep (Feature-Level) Fusion.md"
    ?? "docs/vAIlt/Deep-Learning-Based Calibration Challenges.md"
    ?? "docs/vAIlt/Delving Into the Secrets of BEV 3D Object Detection in Autonomous Driving A Comprehensive Survey.md"
    ?? "docs/vAIlt/Doppler-Optical Flow Fusion Calibration.md"
    ?? "docs/vAIlt/EA-LSS Edge-Aware Lift-Splat-Shot Framework for 3D BEV Object Detection.md"
    ?? "docs/vAIlt/EA-LSS Edge-aware Lift-splat-shot Framework for 3D BEV Object Detection_1.md"
    ?? "docs/vAIlt/EPSM (Environmental Perception Safety Metric).md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/Early Fusion.md"
    ?? "docs/vAIlt/Echoes Beyond Points Unleashing the Power of Raw Radar Data in Multi-modality Fusion.md"
    ?? "docs/vAIlt/Exploring Radar-Camera Extrinsic Calibration A Deep Learning Perspective and Challenges.md"
    ?? "docs/vAIlt/External Multi-Modal Imaging Sensor Calibration for Sensor Fusion A Review_1.md"
    ?? "docs/vAIlt/External multi-modal imaging sensor calibration for sensor fusion A review.md"
    ?? "docs/vAIlt/Extrinsic 6DoF Calibration of a Radar-LiDAR-Camera System Enhanced by Radar Cross Section Estimates.md"
    ?? "docs/vAIlt/Extrinsic Calibration.md"
    ?? "docs/vAIlt/Extrinsic Sensor Calibration.md"
    ?? "docs/vAIlt/FUTR3D A Unified Sensor Fusion Framework for 3D Detection.md"
    ?? "docs/vAIlt/False Negative  False Positive Error Analysis.md"
    ?? "docs/vAIlt/Fast 3D Object Detection for 4D Imaging Radar Integrating Image Map Features Using Semi-Supervised Learning.md"
    ?? "docs/vAIlt/Fully Connected Pose Estimation (FCPE).md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework.md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework_1.md"
    ?? "docs/vAIlt/Image (Zotero item 6MQUAGUR).md"
    ?? "docs/vAIlt/Intrinsic Calibration.md"
    ?? "docs/vAIlt/Joint Extrinsic Calibration Tool (Radar-Camera-Lidar).md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions.md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions_1.md"
    ?? "docs/vAIlt/K-Radar Dataset.md"
    ?? "docs/vAIlt/Knowledge Distillation.md"
    ?? "docs/vAIlt/Late (Decision-Level) Fusion.md"
    ?? "docs/vAIlt/LiDAR-4D Radar Fusion.md"
    ?? "docs/vAIlt/LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Lift-Splat-Shoot Framework.md"
    ?? "docs/vAIlt/Linear Group RNN.md"
    ?? "docs/vAIlt/Low-Cost Temporal-Spatial Calibration.md"
    ?? "docs/vAIlt/MSAFusion Object Detection Based on Multisensor Adaptive Fusion Under BEV.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection_1.md"
    ?? "docs/vAIlt/MV2DFusion Model.md"
    ?? "docs/vAIlt/Meta-Information-Based Detection Error Analysis (univariate + Random ForestSHAP).md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance.md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance_1.md"
    ?? "docs/vAIlt/Millimeter-Wave Radar-Camera Fusion.md"
    ?? "docs/vAIlt/Minimally Connected Pose Estimation (MCPE).md"
    ?? "docs/vAIlt/Motion-Based Radar-to-Camera Extrinsic Calibration (velocity-based, targetless).md"
    ?? "docs/vAIlt/Multi-Modal Fusion Technology Based on Vehicle Information A Survey.md"
    ?? "docs/vAIlt/Multi-Sensor ExtrinsicTemporal Calibration.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (CameraLiDARRadar).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (Review Taxonomy).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception for Autonomous Driving A Review.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion in Automated Driving A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey_1.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection_1.md"
    ?? "docs/vAIlt/Object Detection in Autonomous Vehicles under Adverse Weather A Review of Traditional and Deep Learning Approaches.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online LiDAR-Camera Extrinsic Parameters Self-Checking and Recalibration.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_2.md"
    ?? "docs/vAIlt/OpenCalib A Multi-Sensor Calibration Toolbox for Autonomous Driving.md"
    ?? "docs/vAIlt/OpenCalib A Multi-sensor Calibration Toolbox for Autonomous Driving_1.md"
    ?? "docs/vAIlt/OpenCalib Toolbox.md"
    ?? "docs/vAIlt/Perception Methods for Adverse Weather Based on Vehicle Infrastructure Cooperation System A Review.md"
    ?? "docs/vAIlt/Perception and Sensing for Autonomous Vehicles Under Adverse Weather Conditions A Survey.md"
    ?? "docs/vAIlt/Perspective Supervision (auxiliary perspective-view detection loss).md"
    ?? docs/vAIlt/PointPillars.md
    ?? "docs/vAIlt/Pose and Structure Estimation (PSE).md"
    ?? "docs/vAIlt/Query-Based Multi-Modal Fusion (FUTR3D).md"
    ?? "docs/vAIlt/RADIATE A Radar Dataset for Automotive Perception in Bad Weather.md"
    ?? "docs/vAIlt/RADIATE Dataset.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network_1.md"
    ?? "docs/vAIlt/RLCNet An End-to-End Deep Learning Framework for Simultaneous Online Calibration of LiDAR, RADAR, and Camera_1.md"
    ?? "docs/vAIlt/RLCNet An end-to-end deep learning framework for simultaneous online calibration of LiDAR, RADAR, and Camera.md"
    ?? "docs/vAIlt/RLCNet Model.md"
    ?? "docs/vAIlt/Radar Cross Section-Enhanced Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey_1.md"
    ?? "docs/vAIlt/Radar-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar-Camera Fusion Taxonomy (whywhatwherewhenhow to fuse).md"
    ?? "docs/vAIlt/Radar-Camera Fusion for Object Detection and Semantic Segmentation in Autonomous Driving A Comprehensive Review.md"
    ?? "docs/vAIlt/Random Forest + Shapley Value Feature Importance.md"
    ?? "docs/vAIlt/Reprojection-Error-Based Extrinsic Calibration.md"
    ?? "docs/vAIlt/Resilient Object Detection for Autonomous Vehicles Integrating Deep Learning and Sensor Fusion.md"
    ?? "docs/vAIlt/Resilient object detection for autonomous vehicles Integrating deep learning and sensor fusion in adverse conditions.md"
    ?? "docs/vAIlt/Review on Millimeter-Wave Radar and Camera Fusion Technology.md"
    ?? "docs/vAIlt/Robustness of Perception under AdverseCorrupted Conditions.md"
    ?? "docs/vAIlt/Robustness-Aware 3D Object Detection in Autonomous Driving A Review and Outlook.md"
    ?? "docs/vAIlt/SACM Dialectical Safety Assurance Case.md"
    ?? "docs/vAIlt/Safe Autonomous Driving in Adverse Weather Sensor Evaluation and Performance Monitoring.md"
    ?? "docs/vAIlt/Safety Assurance for Perception Systems (standardization, metrics, safety cases).md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset.md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset_1.md"
    ?? "docs/vAIlt/Semi-Supervised 4D Radar Object Detection with Image-Map Features.md"
    ?? "docs/vAIlt/Sensor Evaluation and Performance Monitoring in Adverse Weather.md"
    ?? "docs/vAIlt/Simultaneous Online Multi-Sensor Calibration.md"
    ?? "docs/vAIlt/Single Joint Calibration Target Design (radar+camera+lidar).md"
    ?? "docs/vAIlt/Static Multitarget-Based Autocalibration of RGB Cameras, 3-D Radar, and 3-D Lidar Sensors.md"
    ?? "docs/vAIlt/Strong-Fusion  Weak-Fusion Taxonomy (earlydeeplateasymmetry-fusion).md"
    ?? "docs/vAIlt/Systematic Multi-Modal Sensor Calibration.md"
    ?? "docs/vAIlt/Target-Based Calibration.md"
    ?? "docs/vAIlt/Targetless (Target-Free) Calibration.md"
    ?? "docs/vAIlt/Targetless LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar\342\200\223Camera Calibration via Trajectory Alignment.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration of Radar and Camera for Intelligent Transportation Systems.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System_1.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization Progress, Research Advances, and Perspectives.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization, Progress, Research Advances.md"
    ?? "docs/vAIlt/Towards Robust 3D Object Detection with LiDAR and 4D Radar Fusion in Various Weather Conditions.md"
    ?? "docs/vAIlt/Towards Serious Perception Sensor Simulation for Safety Validation of Automated Driving A Collaborative Approach.md"
    ?? "docs/vAIlt/Two-Stage BEV Detector (perspective proposals + BEV head).md"
    ?? "docs/vAIlt/Two-Stage Point-Feature Refinement.md"
    ?? "docs/vAIlt/UniLION Model.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs_1.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation_1.md"
    ?? "docs/vAIlt/UniTR Model.md"
    ?? "docs/vAIlt/V2X-Enabled Cooperative Safety Intelligence.md"
    ?? "docs/vAIlt/Vehicle-Infrastructure Cooperation System.md"
    ?? "docs/vAIlt/Virtual Points (Radar-to-LiDAR Densification).md"
    ?? docs/vAIlt/VoxelNet.md
    ?? "docs/vAIlt/Waymo Open Dataset.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/ZFusion Model.md"
    ?? "docs/vAIlt/_COMMUNITY_3D Detection Performance Influencing-Factor Analysis.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Calibration & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Fusion Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_AV Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather Perception Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather V2I Perception Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV  Center-Based 3D Detection Architectures.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV Fusion Frameworks Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_Cooperative & Query-Based BEV Fusion.md"
    ?? "docs/vAIlt/_COMMUNITY_Deep-Learning-Based Radar-Camera Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Extrinsic Calibration Methods (Targetless  Continuous-Time).md"
    ?? "docs/vAIlt/_COMMUNITY_General Multi-Sensor Fusion Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_LiDAR-Camera Calibration Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_Miscellaneous Image.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Modal Detection Benchmarks & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Sensor Extrinsic Calibration Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Object-Tracking-Based Online Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety & Robustness Assurance.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety Metrics & Evaluation.md"
    ?? "docs/vAIlt/_COMMUNITY_Robust 4D Radar-Camera Fusion under Adverse Weather.md"
    ?? "docs/vAIlt/_COMMUNITY_Safety Assurance Case (SACM) Methodology.md"
    ?? "docs/vAIlt/_COMMUNITY_Sensor Calibration Toolboxes & Reviews (duplicate snapshots).md"
    ?? "docs/vAIlt/_COMMUNITY_UniLION Model (isolated).md"
    ?? "docs/vAIlt/_COMMUNITY_Unified BEV Transformer & Adaptive Fusion Models.md"
    ?? docs/vAIlt/graph.canvas
    ?? docs/vAIlt/noise-injection-smoke-test-report.md
    ?? "docs/vAIlt/nuScenes A Multimodal Dataset for Autonomous Driving.md"
    ?? "docs/vAIlt/nuScenes A multimodal dataset for autonomous driving_1.md"
    ?? "docs/vAIlt/nuScenes Dataset.md"
    ?? graphify-out/
    ?? obsidianVault/Daily/2026-08-26.md
    ?? obsidianVault/Daily/2026-08-27.md
    ?? obsidianVault/Daily/2026-08-28.md
    ?? obsidianVault/Daily/2026-08-31.md
    ?? obsidianVault/Daily/2026-09-01.md
    ?? obsidianVault/Daily/2026-09-02.md
    ?? obsidianVault/Daily/2026-09-03.md
    ?? obsidianVault/Daily/2026-09-07.md
    ?? obsidianVault/Knowledge/asf-availability-told-not-aware.md
    ?? obsidianVault/Knowledge/asf-map-eval-mechanics.md
    ?? obsidianVault/Knowledge/asf-recovery-rate-and-fog-confound.md
    ?? obsidianVault/Knowledge/cri-computed-from-row-table.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-anomaly-addendum.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-frame-key-fix-20260901.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-phase1-audit.md
    ?? obsidianVault/Knowledge/frame-key-derivation-kradar.md
    ?? obsidianVault/Projects/K-Radar/asf-3d-ap-per-weather-2026-09-07.md
    ?? obsidianVault/Projects/K-Radar/context-radar-charts.md
    ?? obsidianVault/Projects/K-Radar/corruption-visual-gallery.md
    ?? obsidianVault/Projects/K-Radar/dataset-distribution-histograms.md
    ?? obsidianVault/Projects/K-Radar/exhaustive-crossproduct-phase2-progress.md
    ?? obsidianVault/Projects/K-Radar/frame-identifier-bug.md
    ?? obsidianVault/Projects/K-Radar/full-denormalized-exploratory-pass.md
    ?? obsidianVault/Projects/K-Radar/official-checkpoint-rerun-2026-08-26.md
    ?? obsidianVault/Projects/K-Radar/results-context-figures-session.md
    ?? obsidianVault/Projects/K-Radar/robustness-bar-charts.md
    ?? obsidianVault/Projects/K-Radar/robustness-metrics-tables.md
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/bar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/box_plots.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/build_denormalized_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/context_radar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct/
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/dataset_distributions.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/density_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_dumbbell_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts_by_modality.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_robustness_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/exploratory_passes.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/fpfn_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/heatmaps.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/merge_churn.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/pass4_stratifier_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/robustness_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_context.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_pass4.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_robustness_line_charts.py
- Python 3.12.13; matplotlib 3.10.8; numpy 1.26.4; polars 1.39.3 (via `uv run --project test-bed`)
- No bootstrap/random seed: ^c$ is a deterministic AP ratio, using K-Radar's unmodified 41-point interpolated AP evaluator (`ap_metrics.py::compute_ap_grouped`)

#### Data provenance
- Input: `/home/adhish/Productivity/AMSCUP/repos/K-Radar/outputs/robustness_reports/full_denormalized_table_22cond_weather_corrected.parquet`
  sha256: `d911e93691f2fae1b46d3782d408ea26f72629573f859cb56f07ea146bc6098d`, last modified 2026-09-23 16:44:37 +0200, 872,745 rows, 22 distinct conditions, classes {sed, bus}.
  **Canonical-path note:** the logging template names `repos/K-Radar/scripts/alvis/outputs/row_table_iou03.parquet` as canonical; that exact path doesn't exist (a deeper variant `repos/K-Radar/scripts/alvis/outputs/robustness_reports/row_table_iou03.parquet` does). Regardless it is not the correct input for this figure family: it's a per-detection row table consumed by an unrelated script (`test-bed/.../scripts/analysis/radar_charts.py`, severity-tier condition charts, not diversity-axis charts). The diversity-axis radar charts (Figs. 5.8-5.21 and this panel) come exclusively from the pre-aggregated `full_denormalized_table_22cond_weather_corrected.parquet` via `generate_corruption_radar.py` -- confirmed against `Results.tex`'s own figure references.
- Filter/agg chain (inside `compute_axis`, unchanged from `generate_corruption_radar.py`): (1) `df.filter(condition in {original} ∪ {spoke_condition(*s) for s in SPOKES})` -> subset to the 22 needed conditions; (2) `compute_ap_grouped(dff_all, group_by=["condition","cls","environment"])` -> AP + num_gt per (condition, class, category) cell; (3) per spoke, ^c$ = corrupted-AP / baseline-AP if both baseline num_gt >=30 and corrupted num_gt >=30, else NaN (gap in plotted line).
- IoU threshold: 0.3. Class: Bus/truck (cls=bus). Diversity-axis column: `environment`. Category plotted: `highway`. Severities: low/medium/high for gaussian_noise and loss_partial; single tier for loss_complete_zero.
- Baseline (`original` condition) for this panel: AP=68.44, num_gt=3774 (well above the N>=30 floor -- independently recomputed this session, see Verification)

#### Statistical reporting
- Baseline N reported above; per-corrupted-spoke N not individually enumerated in this session beyond the floor-check already performed inside `compute_axis` (sub-floor spokes become NaN gaps, never plotted as solid values).
- N_sequences: not computed separately this session -- `compute_ap_grouped` pools across all sequences present for this (condition, cls, category) cell in the parquet; sequence-level breakdown is UNVERIFIABLE from this session alone.
- CI method: none -- ^c$ is a point-estimate ratio; no bootstrap/CI shown, consistent with the original thesis figure.
- No sub-floor (N<30) group is plotted as a solid/trusted value on this panel.
- "Significant" is not used on this figure or its caption.

#### Styling
- Shared plotting module: `docs/crossproduct_figures/palette.py` (`MODALITY_COLORS`, `RANK_COLORS`) -- identical to every thesis radar chart.
- Font sizes tuned for a full single-panel chart (title 18pt, tick labels 15pt, y-tick 11pt); not yet checked against actual slide-deck text scale.
- Colorblind safety: not independently re-verified this session -- palette inherited unchanged from the thesis's own module.
- Title on plot: **yes** -- "Bus/truck robustness under all 21 corruption conditions, Environment=Highway stratum (individual panel cropped from the thesis's diversity-axes environment radar-chart family, bus version)." -- deviates from the template's "default is no" convention; kept per explicit user instruction this session, since each panel is being cropped out of its original multi-panel context and needs its own label.

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown -- only ^c$ (AP ratio)
- [x] No camera `frame_deletion` conditions included -- confirmed absent from `RADAR_AXIS_EFFECTS`/`SPOKES` in `_lib.py`
- [x] No external/paper figures or images reused -- generated fresh from local parquet this session
- [x] Every number traced to source file above (baseline AP/num_gt independently recomputed, see Verification)
- [ ] Figure visually inspected after rendering -- **NOT satisfied.** Only file existence, PNG dimensions (via `identify`/PIL) and sha256 were checked this session; the rendered image was not opened/viewed. Flagging honestly rather than claiming a check that didn't happen.

#### Verification
- Independently recomputed the baseline (`original`, Bus/truck (cls=bus), `environment`=`highway`) AP/num_gt cell via a fresh `compute_ap_grouped` call in this session, separate from re-running the plotting script: AP=68.44, num_gt=3774.
- Not diffed against `findings.md`, Q1-Q6 CSVs, or the compiled LaTeX thesis PDF in this session -- this panel is a re-crop of the same underlying computation behind the corresponding published thesis figure (Fig. 5.8/5.9/5.10 family depending on axis), not a new number, but that equivalence has not been explicitly re-verified against the PDF this session.

#### Open issues / caveats
- Visual inspection of the rendered PNG was not performed this session (see unchecked Integrity item above) -- user should open the file before placing it on a slide.
- Canonical-path discrepancy noted above under Data provenance.
- Per-spoke N/coverage beyond the single baseline cell reported here was not enumerated for this panel in this session.

---
### FIG-20260924-193506-claude-slidefigs-table-5-3-spoke-key
**Status:** FINAL
**Supersedes:** N/A — first logged entry (earlier un-logged iteration had a title and the LC row read "loss_complete_zero (single tier, no severity)"; both removed per user instruction this session; only final state logged)
**Logged:** 2026-09-24T19:35:06+02:00 by claude-slidefigs
**Intended slide(s):** Findings slide 1 — "general trends" (unassigned slide number)
**Story-arc step served:** corruption-sweep results — legend/key material supporting the radar-chart panels (not itself a result)

#### What the figure shows
- A rendered image of thesis Table 5.3: the 7-row key mapping each two-letter spoke code (GL/GM/GH/LL/LM/LH/LC) to its full effect+severity meaning, as used across Figs. 5.8-5.21.
- Plot type: matplotlib table (`ax.table`), 2 columns (Code, Effect), 7 data rows + 1 header row. No axes/data plot — pure text table. No class breakdown (this is a shared key across all classes/charts).
- No title (removed per user instruction). LC row shows only `loss_complete_zero` (the "(single tier, no severity)" qualifier text was removed per user instruction — see thesis `Results.tex` for the original, unabbreviated caption context if that nuance is needed at defense).

#### Output files
- `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/table_5_3_spoke_key.png`
- 1480x623 px, 200 DPI, opaque white background (not transparent — user did not request transparency for this image; only the 6 radar panels were made transparent)
- sha256: `8e682300bb7a0f6c46834a93c39c076bbedaeeef87604384682463a798996d9b`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_table_and_legend.py` (top section) — **new script written this session**. Content is transcribed verbatim from `docs/Latex_Report/thesis_report/include/Results.tex` lines 228-241 (`\label{tab:radar_spoke_key}`), not derived from data.
- Exact command (from `/home/adhish/Productivity/AMSCUP/test-bed`):
```
uv run --project . python /home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_table_and_legend.py
```
  (also generates `fig_5_8_spoke_labels.png` and `radar_chart_legend.png` in the same run)
- Git commit at generation time: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree DIRTY (same dirty-file set as other entries in this batch, captured via `git status --porcelain`):
     M CLAUDE.md
     D docs/Adyuth_Hisham_resume_PartTime.docx.md
     M docs/Latex_Report
     M docs/vAIlt/.obsidian/workspace.json
     M obsidianVault/.obsidian/workspace.json
     M obsidianVault/Knowledge/asf-training-inputs.md
     M obsidianVault/Knowledge/robustness-metric-selection.md
     M obsidianVault/Projects/K-Radar/asf-corruption-study-alvis.md
     M obsidianVault/Projects/K-Radar/robustness-radar-charts.md
     M repos/K-Radar
     M test-bed/src/Modules/robust_testing/kradar/scripts/analysis/radar_charts.py
     M test-bed/src/Modules/robust_testing/kradar/src/kradar_visibility/config.py
    ?? .agents/
    ?? FinalTerm_Presentation_Claude.odp
    ?? alvis_archive_2026-08-28/
    ?? backups/
    ?? docs/.master_presentation_figures.lock
    ?? docs/.~lock.Thesis_Presentation_Claude.odp#
    ?? docs/ASF_KRadar_Adversarial_Review.md
    ?? docs/ASF_Pipeline.backup.svg
    ?? docs/ASF_Pipeline.svg
    ?? docs/ASF_Pipeline_slide.svg
    ?? docs/ASF_Pipeline_v2.svg
    ?? docs/ASF_pipeline_cheatsheet.md
    ?? docs/FINAL_CHECK_LOG.md
    ?? docs/HUMANIZE_LOG.md
    ?? docs/Thesis_Presentation.odp
    ?? docs/Thesis_Presentation_Claude.odp
    ?? docs/crossproduct_figures/
    ?? docs/crossproduct_trends_and_anomalies.md
    ?? docs/crossproduct_trends_and_anomalies_metrics_coverage.md
    ?? docs/delete_/
    ?? docs/figure_scripts/
    ?? docs/images/
    ?? docs/lit_survey/ALVIS_URLs.txt
    ?? docs/lit_survey/asf.txt
    ?? docs/lit_survey/dataset/
    ?? docs/lit_survey/irl_corruptions/
    ?? docs/lit_survey/models/
    ?? docs/lit_survey/motivations/
    ?? docs/lit_survey/robust_benchmarks/
    ?? docs/master_presentation_figures.md
    ?? docs/regenerate_weather_figures_snow_fix.md
    ?? docs/slide_figures_findings1/
    ?? docs/thesis_defense_questions.md
    ?? docs/thesis_defense_questions_draft.md
    ?? docs/thesis_writing_bible.md
    ?? docs/trend_candidates.md
    ?? docs/vAIlt/06_Results/alvis-wipe-audit-2026-08-28.md
    ?? docs/vAIlt/06_Results/crossproduct-rebuild-20260901.md
    ?? docs/vAIlt/06_Results/distance-band-ap-and-churn-recompute-2026-09-04.md
    ?? docs/vAIlt/06_Results/exhaustive-crossproduct-phase1-audit-20260831.md
    ?? docs/vAIlt/06_Results/frame-identifier-bug-fix-report.md
    ?? docs/vAIlt/06_Results/lidar-gaussian-noise-mechanism-phase1-audit-20260902.md
    ?? docs/vAIlt/06_Results/manual-code-vetting-checklist.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-audit-phase1-2026-08-31.md
    ?? docs/vAIlt/06_Results/robustness-pipeline-bug-audit-2026-08-31.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31-corrected.md
    ?? docs/vAIlt/06_Results/row-table-integrity-audit-2026-08-31.md
    ?? "docs/vAIlt/3-D LiDAR and Monocular Camera Calibration A Review.md"
    ?? "docs/vAIlt/3D Uncertainty Perspective-N-Points (PnP).md"
    ?? "docs/vAIlt/4D Radar-Camera Calibration and Auto-Labeling.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion.md"
    ?? "docs/vAIlt/4D Radar-Camera Fusion_1.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving.md"
    ?? "docs/vAIlt/4D-CAAL 4D Radar-Camera Calibration and Auto-Labeling for Autonomous Driving_1.md"
    ?? "docs/vAIlt/A 4D Radar-Camera Extrinsic Calibration Tool Based on 3D Uncertainty Perspective-N-Points.md"
    ?? "docs/vAIlt/A Continuous-Time Approach for 3D Radar-to-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/A Joint Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/A Low-Cost Temporal-Spatial Calibration Method for Radar and Camera Systems.md"
    ?? "docs/vAIlt/A Review of Environmental Perception Technology Based on Multi-Sensor Information Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A Review of Multi-Sensor Fusion in Autonomous Driving.md"
    ?? "docs/vAIlt/A low-cost temporal-spatial calibration method for radar and camera systems_1.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and Robust 3D Object Detection in Adverse Conditions through Knowledge Distillation.md"
    ?? "docs/vAIlt/AWARDistill Adaptive and robust 3D object detection in adverse conditions through knowledge distillation_1.md"
    ?? docs/vAIlt/AWARDistill.md
    ?? "docs/vAIlt/AdaptiveFusion LiDAR-Camera Adaptive Fusion for 3D Object Detection.md"
    ?? "docs/vAIlt/AdaptiveFusion Model.md"
    ?? "docs/vAIlt/Adverse Weather Perception.md"
    ?? "docs/vAIlt/Adverse-Weather Perception Robustness.md"
    ?? "docs/vAIlt/An Autonomous Extrinsic Calibration Method for 4D Millimeter-Wave Radar Point Clouds and Visual Images.md"
    ?? "docs/vAIlt/An Extrinsic Calibration Tool for Radar, Camera and Lidar.md"
    ?? "docs/vAIlt/Anchor-Based 3D Detection.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion.md"
    ?? "docs/vAIlt/Automatic Spatial Radar-Camera Calibration via Geometric Constraints with Doppler-Optical Flow Fusion_1.md"
    ?? "docs/vAIlt/Automatic Targetless LiDAR-Camera Calibration A Survey.md"
    ?? "docs/vAIlt/Autonomous Driving Perception Safety Standardization.md"
    ?? "docs/vAIlt/Autonomous-Driving Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/Availability-aware Sensor Fusion via Unified Canonical Space.md"
    ?? "docs/vAIlt/BEVFormer (v1).md"
    ?? "docs/vAIlt/BEVFormer v2 Adapting Modern Image Backbones to Bird's-Eye-View Recognition via Perspective Supervision.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation.md"
    ?? "docs/vAIlt/BEVFusion Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation_1.md"
    ?? "docs/vAIlt/Bird's-Eye View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View  3D Object Detection Architectures.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Recognition.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation.md"
    ?? "docs/vAIlt/Bird's-Eye-View (BEV) Representation_1.md"
    ?? "docs/vAIlt/Camera, LiDAR, and IMU Spatiotemporal Calibration Methodological Review and Research Perspectives.md"
    ?? "docs/vAIlt/Camera-Radar Fusion (HVDetFusion).md"
    ?? "docs/vAIlt/Center-Based Object Representation (points, not boxes).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking (CenterPoint).md"
    ?? "docs/vAIlt/Center-based 3D Object Detection and Tracking.md"
    ?? "docs/vAIlt/Continuous-Time Trajectory Representation.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey.md"
    ?? "docs/vAIlt/Cooperative Safety Intelligence in V2X-Enabled Transportation A Survey_1.md"
    ?? "docs/vAIlt/Deep (Feature-Level) Fusion.md"
    ?? "docs/vAIlt/Deep-Learning-Based Calibration Challenges.md"
    ?? "docs/vAIlt/Delving Into the Secrets of BEV 3D Object Detection in Autonomous Driving A Comprehensive Survey.md"
    ?? "docs/vAIlt/Doppler-Optical Flow Fusion Calibration.md"
    ?? "docs/vAIlt/EA-LSS Edge-Aware Lift-Splat-Shot Framework for 3D BEV Object Detection.md"
    ?? "docs/vAIlt/EA-LSS Edge-aware Lift-splat-shot Framework for 3D BEV Object Detection_1.md"
    ?? "docs/vAIlt/EPSM (Environmental Perception Safety Metric).md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/EPSM A Novel Metric to Evaluate the Safety of Environmental Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/Early Fusion.md"
    ?? "docs/vAIlt/Echoes Beyond Points Unleashing the Power of Raw Radar Data in Multi-modality Fusion.md"
    ?? "docs/vAIlt/Exploring Radar-Camera Extrinsic Calibration A Deep Learning Perspective and Challenges.md"
    ?? "docs/vAIlt/External Multi-Modal Imaging Sensor Calibration for Sensor Fusion A Review_1.md"
    ?? "docs/vAIlt/External multi-modal imaging sensor calibration for sensor fusion A review.md"
    ?? "docs/vAIlt/Extrinsic 6DoF Calibration of a Radar-LiDAR-Camera System Enhanced by Radar Cross Section Estimates.md"
    ?? "docs/vAIlt/Extrinsic Calibration.md"
    ?? "docs/vAIlt/Extrinsic Sensor Calibration.md"
    ?? "docs/vAIlt/FUTR3D A Unified Sensor Fusion Framework for 3D Detection.md"
    ?? "docs/vAIlt/False Negative  False Positive Error Analysis.md"
    ?? "docs/vAIlt/Fast 3D Object Detection for 4D Imaging Radar Integrating Image Map Features Using Semi-Supervised Learning.md"
    ?? "docs/vAIlt/Fully Connected Pose Estimation (FCPE).md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework.md"
    ?? "docs/vAIlt/HVDetFusion A Simple and Robust Camera-Radar Fusion Framework_1.md"
    ?? "docs/vAIlt/Image (Zotero item 6MQUAGUR).md"
    ?? "docs/vAIlt/Intrinsic Calibration.md"
    ?? "docs/vAIlt/Joint Extrinsic Calibration Tool (Radar-Camera-Lidar).md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions.md"
    ?? "docs/vAIlt/K-Radar 4D Radar Object Detection for Autonomous Driving in Various Weather Conditions_1.md"
    ?? "docs/vAIlt/K-Radar Dataset.md"
    ?? "docs/vAIlt/Knowledge Distillation.md"
    ?? "docs/vAIlt/Late (Decision-Level) Fusion.md"
    ?? "docs/vAIlt/LiDAR-4D Radar Fusion.md"
    ?? "docs/vAIlt/LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Lift-Splat-Shoot Framework.md"
    ?? "docs/vAIlt/Linear Group RNN.md"
    ?? "docs/vAIlt/Low-Cost Temporal-Spatial Calibration.md"
    ?? "docs/vAIlt/MSAFusion Object Detection Based on Multisensor Adaptive Fusion Under BEV.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection.md"
    ?? "docs/vAIlt/MV2DFusion Leveraging Modality-Specific Object Semantics for Multi-Modal 3D Detection_1.md"
    ?? "docs/vAIlt/MV2DFusion Model.md"
    ?? "docs/vAIlt/Meta-Information-Based Detection Error Analysis (univariate + Random ForestSHAP).md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance.md"
    ?? "docs/vAIlt/Methodology for an Analysis of Influencing Factors on 3D Object Detection Performance_1.md"
    ?? "docs/vAIlt/Millimeter-Wave Radar-Camera Fusion.md"
    ?? "docs/vAIlt/Minimally Connected Pose Estimation (MCPE).md"
    ?? "docs/vAIlt/Motion-Based Radar-to-Camera Extrinsic Calibration (velocity-based, targetless).md"
    ?? "docs/vAIlt/Multi-Modal Fusion Technology Based on Vehicle Information A Survey.md"
    ?? "docs/vAIlt/Multi-Sensor ExtrinsicTemporal Calibration.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (CameraLiDARRadar).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion (Review Taxonomy).md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception for Autonomous Driving A Review.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion and Cooperative Perception.md"
    ?? "docs/vAIlt/Multi-Sensor Fusion in Automated Driving A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey.md"
    ?? "docs/vAIlt/Multi-modal Sensor Fusion for Auto Driving Perception A Survey_1.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection.md"
    ?? "docs/vAIlt/Multimodal Virtual Point 3D Detection_1.md"
    ?? "docs/vAIlt/Object Detection in Autonomous Vehicles under Adverse Weather A Review of Traditional and Deep Learning Approaches.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Calibration via Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online LiDAR-Camera Extrinsic Parameters Self-Checking and Recalibration.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_1.md"
    ?? "docs/vAIlt/Online Multi-Sensor Calibration Based on Moving Object Tracking_2.md"
    ?? "docs/vAIlt/OpenCalib A Multi-Sensor Calibration Toolbox for Autonomous Driving.md"
    ?? "docs/vAIlt/OpenCalib A Multi-sensor Calibration Toolbox for Autonomous Driving_1.md"
    ?? "docs/vAIlt/OpenCalib Toolbox.md"
    ?? "docs/vAIlt/Perception Methods for Adverse Weather Based on Vehicle Infrastructure Cooperation System A Review.md"
    ?? "docs/vAIlt/Perception and Sensing for Autonomous Vehicles Under Adverse Weather Conditions A Survey.md"
    ?? "docs/vAIlt/Perspective Supervision (auxiliary perspective-view detection loss).md"
    ?? docs/vAIlt/PointPillars.md
    ?? "docs/vAIlt/Pose and Structure Estimation (PSE).md"
    ?? "docs/vAIlt/Query-Based Multi-Modal Fusion (FUTR3D).md"
    ?? "docs/vAIlt/RADIATE A Radar Dataset for Automotive Perception in Bad Weather.md"
    ?? "docs/vAIlt/RADIATE Dataset.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network.md"
    ?? "docs/vAIlt/RC-AutoCalib An End-to-End Radar-Camera Automatic Calibration Network_1.md"
    ?? "docs/vAIlt/RLCNet An End-to-End Deep Learning Framework for Simultaneous Online Calibration of LiDAR, RADAR, and Camera_1.md"
    ?? "docs/vAIlt/RLCNet An end-to-end deep learning framework for simultaneous online calibration of LiDAR, RADAR, and Camera.md"
    ?? "docs/vAIlt/RLCNet Model.md"
    ?? "docs/vAIlt/Radar Cross Section-Enhanced Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey.md"
    ?? "docs/vAIlt/Radar and Camera Fusion for Object Detection and Tracking A Comprehensive Survey_1.md"
    ?? "docs/vAIlt/Radar-Camera Extrinsic Calibration.md"
    ?? "docs/vAIlt/Radar-Camera Fusion Taxonomy (whywhatwherewhenhow to fuse).md"
    ?? "docs/vAIlt/Radar-Camera Fusion for Object Detection and Semantic Segmentation in Autonomous Driving A Comprehensive Review.md"
    ?? "docs/vAIlt/Random Forest + Shapley Value Feature Importance.md"
    ?? "docs/vAIlt/Reprojection-Error-Based Extrinsic Calibration.md"
    ?? "docs/vAIlt/Resilient Object Detection for Autonomous Vehicles Integrating Deep Learning and Sensor Fusion.md"
    ?? "docs/vAIlt/Resilient object detection for autonomous vehicles Integrating deep learning and sensor fusion in adverse conditions.md"
    ?? "docs/vAIlt/Review on Millimeter-Wave Radar and Camera Fusion Technology.md"
    ?? "docs/vAIlt/Robustness of Perception under AdverseCorrupted Conditions.md"
    ?? "docs/vAIlt/Robustness-Aware 3D Object Detection in Autonomous Driving A Review and Outlook.md"
    ?? "docs/vAIlt/SACM Dialectical Safety Assurance Case.md"
    ?? "docs/vAIlt/Safe Autonomous Driving in Adverse Weather Sensor Evaluation and Performance Monitoring.md"
    ?? "docs/vAIlt/Safety Assurance for Perception Systems (standardization, metrics, safety cases).md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset.md"
    ?? "docs/vAIlt/Scalability in Perception for Autonomous Driving Waymo Open Dataset_1.md"
    ?? "docs/vAIlt/Semi-Supervised 4D Radar Object Detection with Image-Map Features.md"
    ?? "docs/vAIlt/Sensor Evaluation and Performance Monitoring in Adverse Weather.md"
    ?? "docs/vAIlt/Simultaneous Online Multi-Sensor Calibration.md"
    ?? "docs/vAIlt/Single Joint Calibration Target Design (radar+camera+lidar).md"
    ?? "docs/vAIlt/Static Multitarget-Based Autocalibration of RGB Cameras, 3-D Radar, and 3-D Lidar Sensors.md"
    ?? "docs/vAIlt/Strong-Fusion  Weak-Fusion Taxonomy (earlydeeplateasymmetry-fusion).md"
    ?? "docs/vAIlt/Systematic Multi-Modal Sensor Calibration.md"
    ?? "docs/vAIlt/Target-Based Calibration.md"
    ?? "docs/vAIlt/Targetless (Target-Free) Calibration.md"
    ?? "docs/vAIlt/Targetless LiDAR-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar-Camera Calibration.md"
    ?? "docs/vAIlt/Targetless Radar\342\200\223Camera Calibration via Trajectory Alignment.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration of Radar and Camera for Intelligent Transportation Systems.md"
    ?? "docs/vAIlt/Targetless Rotational Auto-Calibration.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System.md"
    ?? "docs/vAIlt/The Adoption of SACM to Support Dialectical Safety Assurance Case of AV Object Recognition System_1.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization Progress, Research Advances, and Perspectives.md"
    ?? "docs/vAIlt/Toward Ensuring Safety for Autonomous Driving Perception Standardization, Progress, Research Advances.md"
    ?? "docs/vAIlt/Towards Robust 3D Object Detection with LiDAR and 4D Radar Fusion in Various Weather Conditions.md"
    ?? "docs/vAIlt/Towards Serious Perception Sensor Simulation for Safety Validation of Automated Driving A Collaborative Approach.md"
    ?? "docs/vAIlt/Two-Stage BEV Detector (perspective proposals + BEV head).md"
    ?? "docs/vAIlt/Two-Stage Point-Feature Refinement.md"
    ?? "docs/vAIlt/UniLION Model.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs.md"
    ?? "docs/vAIlt/UniLION Towards Unified Autonomous Driving Model with Linear Group RNNs_1.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation.md"
    ?? "docs/vAIlt/UniTR A Unified and Efficient Multi-Modal Transformer for Bird's-Eye-View Representation_1.md"
    ?? "docs/vAIlt/UniTR Model.md"
    ?? "docs/vAIlt/V2X-Enabled Cooperative Safety Intelligence.md"
    ?? "docs/vAIlt/Vehicle-Infrastructure Cooperation System.md"
    ?? "docs/vAIlt/Virtual Points (Radar-to-LiDAR Densification).md"
    ?? docs/vAIlt/VoxelNet.md
    ?? "docs/vAIlt/Waymo Open Dataset.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving.md"
    ?? "docs/vAIlt/ZFusion An Effective Fuser of Camera and 4D Radar for 3D Object Perception in Autonomous Driving_1.md"
    ?? "docs/vAIlt/ZFusion Model.md"
    ?? "docs/vAIlt/_COMMUNITY_3D Detection Performance Influencing-Factor Analysis.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Calibration & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_4D Radar-Camera Fusion Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_AV Perception Benchmark Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather Perception Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Adverse-Weather V2I Perception Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV  Center-Based 3D Detection Architectures.md"
    ?? "docs/vAIlt/_COMMUNITY_BEV Fusion Frameworks Survey.md"
    ?? "docs/vAIlt/_COMMUNITY_Cooperative & Query-Based BEV Fusion.md"
    ?? "docs/vAIlt/_COMMUNITY_Deep-Learning-Based Radar-Camera Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Extrinsic Calibration Methods (Targetless  Continuous-Time).md"
    ?? "docs/vAIlt/_COMMUNITY_General Multi-Sensor Fusion Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_LiDAR-Camera Calibration Reviews.md"
    ?? "docs/vAIlt/_COMMUNITY_Miscellaneous Image.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Modal Detection Benchmarks & Datasets.md"
    ?? "docs/vAIlt/_COMMUNITY_Multi-Sensor Extrinsic Calibration Surveys.md"
    ?? "docs/vAIlt/_COMMUNITY_Object-Tracking-Based Online Calibration.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety & Robustness Assurance.md"
    ?? "docs/vAIlt/_COMMUNITY_Perception Safety Metrics & Evaluation.md"
    ?? "docs/vAIlt/_COMMUNITY_Robust 4D Radar-Camera Fusion under Adverse Weather.md"
    ?? "docs/vAIlt/_COMMUNITY_Safety Assurance Case (SACM) Methodology.md"
    ?? "docs/vAIlt/_COMMUNITY_Sensor Calibration Toolboxes & Reviews (duplicate snapshots).md"
    ?? "docs/vAIlt/_COMMUNITY_UniLION Model (isolated).md"
    ?? "docs/vAIlt/_COMMUNITY_Unified BEV Transformer & Adaptive Fusion Models.md"
    ?? docs/vAIlt/graph.canvas
    ?? docs/vAIlt/noise-injection-smoke-test-report.md
    ?? "docs/vAIlt/nuScenes A Multimodal Dataset for Autonomous Driving.md"
    ?? "docs/vAIlt/nuScenes A multimodal dataset for autonomous driving_1.md"
    ?? "docs/vAIlt/nuScenes Dataset.md"
    ?? graphify-out/
    ?? obsidianVault/Daily/2026-08-26.md
    ?? obsidianVault/Daily/2026-08-27.md
    ?? obsidianVault/Daily/2026-08-28.md
    ?? obsidianVault/Daily/2026-08-31.md
    ?? obsidianVault/Daily/2026-09-01.md
    ?? obsidianVault/Daily/2026-09-02.md
    ?? obsidianVault/Daily/2026-09-03.md
    ?? obsidianVault/Daily/2026-09-07.md
    ?? obsidianVault/Knowledge/asf-availability-told-not-aware.md
    ?? obsidianVault/Knowledge/asf-map-eval-mechanics.md
    ?? obsidianVault/Knowledge/asf-recovery-rate-and-fog-confound.md
    ?? obsidianVault/Knowledge/cri-computed-from-row-table.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-anomaly-addendum.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-frame-key-fix-20260901.md
    ?? obsidianVault/Knowledge/exhaustive-crossproduct-phase1-audit.md
    ?? obsidianVault/Knowledge/frame-key-derivation-kradar.md
    ?? obsidianVault/Projects/K-Radar/asf-3d-ap-per-weather-2026-09-07.md
    ?? obsidianVault/Projects/K-Radar/context-radar-charts.md
    ?? obsidianVault/Projects/K-Radar/corruption-visual-gallery.md
    ?? obsidianVault/Projects/K-Radar/dataset-distribution-histograms.md
    ?? obsidianVault/Projects/K-Radar/exhaustive-crossproduct-phase2-progress.md
    ?? obsidianVault/Projects/K-Radar/frame-identifier-bug.md
    ?? obsidianVault/Projects/K-Radar/full-denormalized-exploratory-pass.md
    ?? obsidianVault/Projects/K-Radar/official-checkpoint-rerun-2026-08-26.md
    ?? obsidianVault/Projects/K-Radar/results-context-figures-session.md
    ?? obsidianVault/Projects/K-Radar/robustness-bar-charts.md
    ?? obsidianVault/Projects/K-Radar/robustness-metrics-tables.md
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/bar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/box_plots.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/build_denormalized_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/context_radar_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/crossproduct/
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/dataset_distributions.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/density_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_dumbbell_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_line_charts_by_modality.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/distance_robustness_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/exploratory_passes.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/fpfn_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/heatmaps.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/master_metrics_table.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/merge_churn.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/pass4_stratifier_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/robustness_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_context.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/run_churn_pass4.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_line_charts.py
    ?? test-bed/src/Modules/robust_testing/kradar/scripts/analysis/zero_ablation_robustness_line_charts.py
- Python 3.12.13; matplotlib 3.10.8 (via `uv run --project test-bed`). No numpy/polars/pandas involved — static text only.
- No randomness/seeds involved.

#### Data provenance
- Source: `docs/Latex_Report/thesis_report/include/Results.tex` (sha256 `107e01cefb39288cc06220af3cb16c9b8defab00e0404d0e25887894357dc5ae` as of this session), specifically the `tab:radar_spoke_key` environment (lines 228-241). This is LaTeX source text, not experimental data — the 7 code→meaning mappings were copied by hand (verified against the file's `\texttt{}` rows) into the Python `rows` list in `make_table_and_legend.py`.
- Cross-check: the same 7 codes also appear as `_EFFECT_SEV_CODE` in `docs/crossproduct_figures/generate_corruption_radar.py` (the actual chart generator) — both sources agree (GL/GM/GH/LL/LM/LH/LC map to the same gaussian_noise/loss_partial/loss_complete_zero + severity meanings in both places).
- No parquet/row-level data involved in this figure.

#### Statistical reporting
- N/A — no data, aggregation, or statistics — this is a static reference table transcribed from LaTeX source text.

#### Styling
- No shared plotting module (not applicable — text table, not a data chart). Palette: plain black text, light-gray (#e8e8e8) header row fill, gray (#888888) cell borders — not the modality color palette (this table doesn't carry modality-specific info, only effect+severity codes).
- Font size 13pt, table scaled 1x/2.0x (row height).
- Title: removed per user instruction (was present in an earlier un-logged iteration).

#### Integrity checks (HARD)
- [x] No RCE, mASE, or CRI values shown — no data at all, just code definitions
- [x] No camera `frame_deletion` conditions included — not applicable, no conditions plotted; and `frame_deletion` legitimately has no code in this key since it's excluded from the radar-chart spoke set entirely
- [x] No external/paper figures reused — original crop/transcription of this thesis's own Table 5.3 text
- [x] Every value traced to source file above (`Results.tex`)
- [ ] Figure visually inspected after rendering — **NOT satisfied**, same caveat as other entries this batch: only file existence/dimensions/sha256 checked, image not opened/viewed this session

#### Verification
- Table text cross-checked against two independent in-repo sources (`Results.tex` LaTeX table and `generate_corruption_radar.py`'s `_EFFECT_SEV_CODE` dict) — both agree on all 7 rows.
- Not compared against a rendered/compiled thesis PDF page image in this session (no PDF page-image diff performed).

#### Open issues / caveats
- The removed "(single tier, no severity)" qualifier for LC is informative context missing from this cropped table — if a defense question asks specifically why LC has no severity variants, that context lives only in the full `Results.tex` caption/table now, not on this slide image.
- Visual inspection of the rendered PNG not performed this session (see unchecked Integrity item).

---
### FIG-20260924-193506-claude-slidefigs-fig-5-8-spoke-labels
**Status:** FINAL
**Supersedes:** N/A — first logged entry (earlier un-logged iteration showed 21 codes with modality labels + a title; both removed per user instruction, replaced with plain colored modality names only)
**Logged:** 2026-09-24T19:35:06+02:00 by claude-slidefigs
**Intended slide(s):** Findings slide 1 — "general trends" (unassigned slide number)
**Story-arc step served:** corruption-sweep results — modality-color legend supporting the radar-chart panels (not itself a result)

#### What the figure shows
- Three words — "Camera", "LiDAR", "Radar" — each rendered in that modality's exact spoke color as used on every radar chart in the thesis's diversity-axes figures (Fig. 5.8-5.21) and on this session's 6 individual panels.
- Plot type: plain text labels on a blank axis, no plot/data. No title, no codes, no legend box.

#### Output files
- `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/fig_5_8_spoke_labels.png`
- 780x419 px, 200 DPI, opaque white background
- sha256: `f4d849d3b020f02982e0903278c0c4615e364bffe07049f411243e2ce6920e91`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_table_and_legend.py` (middle section, `fig2`) — new script this session.
- Colors: `COLORS[mod]` pulled directly from `docs/crossproduct_figures/palette.py::MODALITY_COLORS`, unmodified — same import used by `generate_corruption_radar.py` for the actual thesis charts, so these colors are guaranteed identical to what appears on Fig. 5.8 itself.
- Exact command:
```
uv run --project . python /home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_table_and_legend.py
```
- Git commit: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree DIRTY (same dirty-file set noted in sibling entries this batch).
- Python 3.12.13; matplotlib 3.10.8. No randomness.

#### Data provenance
- `docs/crossproduct_figures/palette.py` sha256 `acfb5f38dbe4c5b923e3edf409c6cf2ff8787fef5dd95672bcacaaa573a626c2` — the single source for the 3 hex colors used. No experimental/parquet data involved.

#### Statistical reporting
- N/A — no data or statistics, pure color-key legend.

#### Styling
- Colors sourced from the shared `palette.py` module (same as every other radar-chart figure this batch and the thesis originals) — not a separate palette.
- Font size 22pt bold, centered.
- Title: removed per user instruction. Codes (GL/GM/GH/etc.): removed per user instruction — this image now shows only the 3 modality-color associations, not the full spoke-code key (that content lives in the separate `table_5_3_spoke_key.png` entry above).

#### Integrity checks (HARD)
- [x] No RCE/mASE/CRI shown — no data
- [x] No camera `frame_deletion` — not applicable, no conditions shown
- [x] No external figures reused
- [x] Every value (the 3 colors) traced to `palette.py` above
- [ ] Figure visually inspected after rendering — **NOT satisfied**, same caveat as sibling entries this batch

#### Verification
- Colors imported directly from `palette.py` at generation time (not manually retyped/approximated) — so correctness is guaranteed by construction as long as `palette.py` itself matches what `generate_corruption_radar.py` uses, which was confirmed via identical sha256 on both copies.

#### Open issues / caveats
- Visual inspection of the rendered PNG not performed this session.
- This image intentionally no longer names which 2-letter codes exist — pair it with `table_5_3_spoke_key.png` on the slide if the audience needs both modality color AND code meaning.

---
### FIG-20260924-193506-claude-slidefigs-radar-chart-legend
**Status:** FINAL
**Supersedes:** N/A — first logged entry
**Logged:** 2026-09-24T19:35:06+02:00 by claude-slidefigs
**Intended slide(s):** Findings slide 1 — "general trends" (unassigned slide number)
**Story-arc step served:** corruption-sweep results — standalone legend for the "worst/second-worst robustness" ring markers and per-modality mean-arc shading used on every radar-chart panel

#### What the figure shows
- A standalone legend, extracted verbatim from the bottom-of-figure legend that `generate_corruption_radar.py::make_figure()` draws on every thesis radar chart: 2 dashed-ring entries ("Worst robustness (lowest $R_b^c$)", "Second-worst robustness") plus 3 color-swatch entries ("Camera/LiDAR/Radar mean $R_b^c$ (arc)"), 5 entries total, 2 columns, no frame/border.
- No title, no plot/data — pure legend, matching exactly what was removed from the 6 individual radar panels this session (per user request to drop the per-panel legend) so it can be placed once on the slide instead of repeated on every panel.

#### Output files
- `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/radar_chart_legend.png`
- 1408x238 px, 200 DPI, opaque white background (NOT transparent — user's transparency request applied only to the 6 individual radar-panel charts, not to this legend or the table/label images; confirm with user if transparency is wanted here too before using on a dark-background slide)
- sha256: `62adcfe104216ec8882249434d34dd9fa928fabffdeb60aefc41a886c423ef73`

#### How it was created
- Generating script: `/home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_table_and_legend.py` (bottom section, `fig3`) — new script this session.
- `CIRCLE_STYLES` and `MOD_RANGES` imported unmodified from `_lib.py` (itself byte-identical to `generate_corruption_radar.py` lines 1-259) and `COLORS` from `palette.py` — the legend's handle definitions are copy-pasted verbatim from `generate_corruption_radar.py::make_figure()`'s own `legend_handles` construction (lines 224-228 of the original script), not re-derived or approximated.
- Exact command:
```
uv run --project . python /home/adhish/Productivity/AMSCUP/docs/slide_figures_findings1/scripts/make_table_and_legend.py
```
- Git commit: `9ca85c28928ac23012b89e4dd3816502b4a82236`. Tree DIRTY (same dirty-file set as sibling entries this batch).
- Python 3.12.13; matplotlib 3.10.8. No randomness.

#### Data provenance
- `docs/crossproduct_figures/generate_corruption_radar.py` sha256 `8ed15012cb558e743931ef027b2821317f63ded5d7e56e0ed42eb5fa0649f27c` (legend text/handle logic source) and `docs/crossproduct_figures/palette.py` sha256 `acfb5f38dbe4c5b923e3edf409c6cf2ff8787fef5dd95672bcacaaa573a626c2` (colors: `RANK_COLORS["worst"]`, `RANK_COLORS["second_worst"]`, `MODALITY_COLORS`). No parquet/experimental data involved — this is a legend key, not a data plot.

#### Statistical reporting
- N/A — legend only, no data plotted.

#### Styling
- Colors/line styles sourced from `palette.py` and `generate_corruption_radar.py::CIRCLE_STYLES`, unmodified — identical to what appears on every actual radar chart.
- Font size 14pt, 2-column layout, no frame.
- Title: none (never had one).

#### Integrity checks (HARD)
- [x] No RCE/mASE/CRI shown — no data
- [x] No camera `frame_deletion` — not applicable
- [x] No external figures reused
- [x] Every element traced to source files above
- [ ] Figure visually inspected after rendering — **NOT satisfied**, same caveat as sibling entries this batch

#### Verification
- Legend handle definitions are a direct copy of `generate_corruption_radar.py`'s own legend-construction code (not retyped from memory or paraphrased), so wording/coloring is guaranteed to match the published thesis chart legends exactly, contingent on the sha256-verified unmodified source files.

#### Open issues / caveats
- Visual inspection of the rendered PNG not performed this session.
- Not made transparent (unlike the 6 radar panels) — flag to user if the slide background requires transparency here too.

---
### FIG-20260924-220100-rework-dataset-model-tables
**Status:** FINAL
**Supersedes:** N/A
**Deck:** Thesis_Presentation_Reworked.odp — slide 8 "Dataset and Model" (previously empty)
**Story-arc step:** dataset/model context, between "Corruptions" methodology and "Results" — establishes what K-Radar/ASF are being compared against
**Takeaway (one sentence):** nuScenes/Waymo/K-Radar and BEVFusion/MV2DFusion/ASF differ in scale, modality composition, diversity axes, and (for models) whether they're designed to handle a missing sensor.
**Output:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/dataset_model_tables.png, PNG, 3200x1427px, no explicit DPI (1x from canvas), sha256=3a978482542fad54326548ae3e8a874bf6676e00abcb221aa76e8e2dfe9c7f7e
**Script:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/scripts/make_dataset_model_tables.py; created fresh this session (new script family for the `thesis_defense/` output dir agreed in Phase 1); iterated in-session (font/padding increase for legibility, then row-height syncing across both tables to eliminate dead space, then fixed one cell's unbreakable slash-joined token that was clipping off the right edge)
**Command:** `cd /home/adhish/Productivity/AMSCUP && python3 docs/crossproduct_figures/thesis_defense/scripts/make_dataset_model_tables.py` (system python3, Pillow only, no project venv needed)
**Repo state:** `git rev-parse HEAD` = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing dirty files unrelated to this figure — CLAUDE.md, obsidianVault/*, docs/vAIlt/*, repos/K-Radar submodule pointer, test-bed radar_charts.py/config.py; docs/crossproduct_figures/thesis_defense/ and docs/Thesis_Presentation_Reworked.odp are new/modified by this entry)
**Environment:** system Python 3.14.7, Pillow 12.3.0 (script), LibreOffice (soffice headless) for render verification. No numpy/pandas/pyarrow involved — no data pipeline, hand-authored cell text. No seeds (deterministic layout).
**Inputs:** No dataset file read. Cell content sourced from: (a) thesis text `docs/Latex_Report/thesis_report/include/{Theory,Methods,Introduction}.tex` for K-Radar/ASF/BEVFusion/MV2DFusion facts already in the thesis; (b) external verification via web search against the original papers for nuScenes (Caesar et al., CVPR 2020, arXiv:1903.11027) and Waymo Open Dataset (Sun et al., CVPR 2020) numbers not stated in the thesis text.
**Processing:** No tabular pipeline — hand-authored table cells, cross-checked against sources listed above, laid out via a bespoke PIL script (row-height sync across the two tables so neither has trailing dead space).
**Scope:** Comparison table only — no IoU threshold, class, sequence, or condition filtering applies (not a results figure). Datasets compared: nuScenes, Waymo Open, K-Radar. Models compared: BEVFusion, MV2DFusion, ASF.
**Numbers shown:**
  - nuScenes: 1.4M 3D boxes, 6 cameras/1 LiDAR/5 radar, 1000 scenes, 360° full-suite redundancy, 11 semantic map layers — source: Caesar et al. CVPR 2020 (verified via web search against paper content, not the thesis text, since Waymo/nuScenes exact box counts/sensor counts/map-layer count are not restated in the thesis at this granularity).
  - Waymo Open: 12M 3D boxes (LiDAR), 76 km² area (40km² Phoenix + 36km² SF/Mountain View) — source: Sun et al. CVPR 2020 (verified via web search). Sensor suite composition (5 LiDAR + 5 cameras) stated at high confidence but not pinned to an exact verbatim quote from the paper in this session — flagged as an open issue below.
  - K-Radar: 93.3K 3D boxes, 4 cameras/2 LiDAR/4D radar, 7 structured weather categories + environment + time-of-day — source: thesis's own `Theory.tex`/`Methods.tex` text, itself citing Paek et al. 2022 (already an established thesis citation, not independently re-verified against the K-Radar paper in this session).
  - BEVFusion/MV2DFusion/ASF modalities, training dataset, fusion approach, main highlight — all sourced verbatim/paraphrased from thesis `Theory.tex` (BEVFusion/MV2DFusion camera+LiDAR/nuScenes; ASF camera+LiDAR+radar/K-Radar; UCP+CASAP architecture description).
**Statistics:** N/A — this is a static reference/comparison table, not a results figure. No N_rows/N_sequences, no CI, no bootstrap; nothing here is a computed statistic over K-Radar evaluation data.
**Style:** No shared plotting module used (same bespoke-PIL-script convention as the deck's other ad hoc table figures — `docs/images/metrics_summary_table.png` etc. — navy `#194461`/accent-blue `#2a6099` palette, Noto Sans Bold/Regular). Slide-specific: sized to the deck's actual master-page dimensions (25.4cm x 14.288cm, confirmed in Phase 1 from `styles.xml` PM1 layout) rather than a generic guess.
**Integrity:** [x] no RCE/mASE/CRI as validated — none shown, this is a dataset/model comparison, not a results figure [x] no camera frame_deletion — N/A, no corruption conditions on this figure [ ] no external images — the *content* of two table cells (nuScenes/Waymo numeric facts) is drawn from external papers, not reused as images/figures; treating this as compliant since no pixels/figures were reused, only textual facts, cited above [x] every number traced — see "Numbers shown" [x] output visually inspected — rendered figure viewed directly, and the final placed slide was rendered via `soffice --headless --convert-to pdf` + `pdftoppm` and visually inspected (see Verification)
**Verification:** Rendered the standalone figure and viewed it directly (2 iterations: fixed title clipping/uneven table heights by syncing row heights across both tables; fixed one overflowing cell caused by an unbreakable slash-joined token, `weather/environment/time-of-day` → `weather, environment, and time-of-day`, and added a wrap() safety check that now raises instead of silently clipping if this recurs). After inserting into the deck, re-rendered the full modified .odp to PDF and rasterized slide 8 specifically (`pdftoppm -f 8 -l 8`) — confirmed title, both tables, no clipping/overlap, and the existing master-page Chalmers logo/page-number frame are all intact. Result: PASS. No discrepancy check needed vs. findings.md/CSVs — this figure carries no K-Radar/ASF empirical results, only dataset/model reference facts.
**Advisor notes:** User asked for board content first (dataset/model comparison focused on radar characteristics for datasets; modality/training/highlight/robustness for models), then iteratively trimmed columns (3D-box-count only instead of full sensor breakdown; separate Modality and Diversity-axes rows instead of a combined Radar row; added a verified Uniqueness row per user-supplied candidate text; removed Robustness facts row from the model table; simplified Fusion approach wording) before approving insertion into slide 8. Chose row-height syncing over independent table heights once the two tables' row counts matched (5 rows each) — keeps both tables visually aligned and eliminates the dead space a naturally-shorter table would otherwise leave.
**Open issues:** (1) Waymo's exact sensor-suite composition (5 LiDAR + 5 cameras) is high-confidence general knowledge but wasn't traced to an exact quoted line from Sun et al. in this session — flag if you want it re-verified against the paper PDF directly before the defense. (2) The nuScenes/Waymo facts on this slide are the only content in the current deck sourced from outside the thesis's own text — worth deciding whether a footnote/citation should appear on the slide itself, or whether this is acceptable as background/context (not a claim of thesis's own finding).
---

---
### FIG-20260924-223000-rework-dataset-model-tables-waymo-reverify
**Status:** FINAL
**Supersedes:** N/A (follow-up verification note on FIG-20260924-220100-rework-dataset-model-tables, not a content change)
**Deck:** Thesis_Presentation_Reworked.odp — slide 8 "Dataset and Model" (no slide change made by this entry)
**Story-arc step:** N/A — provenance/verification note only
**Takeaway (one sentence):** Waymo Open Dataset's "5 LiDAR + 5 cameras" figure (open issue #1 on the prior entry) is now confirmed against the paper's own text, not just general knowledge.
**Output:** N/A — no new figure produced or modified; the existing dataset_model_tables.png is unchanged (sha256 unchanged: 3a978482542fad54326548ae3e8a874bf6676e00abcb221aa76e8e2dfe9c7f7e).
**Script:** N/A
**Command:** WebFetch against https://ar5iv.labs.arxiv.org/html/1912.04838 and https://arxiv.org/html/1912.04838 (two independent renders of the same arXiv source), prompted to quote the sensor-suite sentence verbatim.
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236 (unchanged from prior entry)
**Environment:** N/A (no code run)
**Inputs:** Sun et al., "Scalability in Perception for Autonomous Driving: Waymo Open Dataset," CVPR 2020 (arXiv:1912.04838), fetched via two independent HTML renders of the same source, not a single fetch.
**Processing:** N/A
**Scope:** N/A
**Numbers shown:** No new numbers on the slide. Confirms the existing "Cameras + LiDAR (5 each)" cell for Waymo in the Datasets table.
**Statistics:** N/A
**Style:** N/A
**Integrity:** [x] no RCE/mASE/CRI [x] no camera frame_deletion [x] no external images reused (text-fact verification only) [x] every number traced — quote below [x] visually inspected — N/A, no image change
**Verification:** Two independent WebFetch calls against ar5iv.labs.arxiv.org/html/1912.04838 and arxiv.org/html/1912.04838 (same underlying arXiv source, two different rendering pipelines) both returned the identical verbatim quote: "The data collection was conducted using five LiDAR sensors and five high-resolution pinhole cameras" (§3.1 Sensor Specifications), corroborated by the paper's own Table 1 (Lidars: 5, Cameras: 5, row "Ours"). Direct PDF fetch (arxiv.org/pdf/1912.04838) and the CVPR openaccess PDF/HTML were tried first and failed (PDF text-extraction returned no readable sensor text; CVF openaccess returned HTTP 403) — verification relies on the two arXiv HTML renders, not the original PDF layout, which is a minor caveat on source fidelity even though both renders agree.
**Advisor notes:** User asked specifically to reverify the Waymo sensor-suite claim before the defense (open issue #1 from the prior entry). Confirmed; no slide change was needed since the existing cell text was already correct.
**Open issues:** None remaining for this figure. (Open issue #2 from the prior entry — whether to footnote the external nuScenes/Waymo sourcing on the slide — is still open and un-actioned, pending user decision.)
---

---
### FIG-20260924-224000-rework-metrics-summary-table-slide13
**Status:** FINAL
**Supersedes:** N/A (reuses/places FIG-20260924-193126-claude-mainsession-metrics-primer-table, previously DRAFT/unassigned)
**Deck:** Thesis_Presentation_Reworked.odp — slide 13 (document position; title "Metrics", previously empty)
**Story-arc step:** metrics primer — placed between "Corruptions" (slide 12) and "Corruptions (Visualized)" (slide 14, document order), ahead of the results slides so the audience has metric definitions before seeing results
**Takeaway (one sentence):** Defines AP, mATE, mASE, mAOE, Retention R_b^c, and CRI: what each measures and what an ideal value looks like.
**Output:** Reused existing file, unchanged: /home/adhish/Productivity/AMSCUP/docs/images/metrics_summary_table.png, 1242x496px, PNG, sha256=05fdf0ff8092435f533ddaca1450fd23df4c7bb11e399b5860c81a36608b86f1 (identical to the FIG-...-metrics-primer-table entry; also copied into the deck's own Pictures/ as `Pictures/metrics_summary_table_slide13.png`, same bytes).
**Script:** No new script — reused the already-generated PNG from FIG-...-metrics-primer-table as-is. No regeneration performed.
**Command:** N/A (no regeneration); insertion done via direct ODF XML edit (content.xml frame + manifest.xml entry), not via the Artifact/DesignSync tooling.
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing dirty files, same set as prior entries in this session; docs/Thesis_Presentation_Reworked.odp is the file modified by this entry).
**Environment:** LibreOffice (soffice headless) for render verification; Python 3.14.7 stdlib (zipfile, re) for the ODF XML edit and manifest update. No new figure-generation environment involved.
**Inputs:** docs/images/metrics_summary_table.png (see provenance in FIG-...-metrics-primer-table: content cross-checked against docs/Latex_Report/thesis_report/include/Methods.tex lines 441-499, not re-verified again in this entry).
**Processing:** No new processing — table reused verbatim from its prior generation.
**Scope:** N/A — definitional table, no IoU/class/sequence/condition scope.
**Numbers shown:** No numeric results shown (definitional only) — same as source entry.
**Statistics:** N/A — no data, no CIs (unchanged from source entry).
**Style:** Unchanged from source entry (Noto Sans, navy/light-gray palette, bespoke PIL script, no shared plotting module).
**Integrity:** [x] no RCE/mASE/CRI shown as validated results (mASE, CRI appear only as definitions) [x] no camera frame_deletion — N/A, no conditions shown [x] no external images reused — see source entry (style modeled on a user-supplied reference, no third-party figure content reused) [x] every number traced — N/A, no numeric results [x] output visually inspected — inspected again in this session before insertion.
**Verification:** A significant discovery in this session: the deck's PDF-export page numbers do NOT match its document-order slide numbering (as shown by the on-slide `<text:page-number>` field and LibreOffice's slide panel), because two slides (document positions 9 and 23) carry a `presentation:visibility="hidden"` drawing-page style and are silently skipped by PDF export. An initial verification render checked the wrong PDF page (13) due to this offset and showed unrelated content ("Corruptions (Visualized)"); re-rendering the correct PDF page (12, accounting for the one hidden slide preceding document position 13) confirmed the actual edited slide: title "Metrics," on-slide page-number field reading "13" (matching document position), table correctly placed with no clipping/overlap, Chalmers master-page branding intact. Result: PASS.
**Advisor notes:** User asked to search the figure log for an existing metrics-definitions table before generating a new one; found FIG-...-metrics-primer-table already existed (DRAFT, unassigned). User then asked to place it on slide 13, which was an empty slide inserted into the deck since the Phase 1 audit (deck now has 29 document-order slides vs. 28 at Phase 1, with slide 13 being new/empty). Reused the existing PNG unchanged rather than regenerating.
**Open issues:** (1) A second slide later in the deck (document position 16, "Noisy Inferences (2)") is also titled "Metrics" and shows a different figure ("Fig 8. Evaluation metrics grouped by what each one measures") — now two same-titled slides exist; flagged to user, not resolved. (2) The two hidden slides (document positions 9 "K-Radar and ASF" and 23 "page23"/Discussion) were not created or modified by this session — flagging their existence since they silently disappear from any PDF export/print and from a live presentation, which may or may not be intentional on the user's part. (3) Inherited open issues from the source entry (metric set finality, R_b^c plain-text subscript) still apply unchanged.
---

---
### FIG-20260925-000000-rework-slide26-27-merge-option-a
**Status:** DRAFT (candidate, not yet chosen or inserted)
**Supersedes:** N/A
**Deck:** Thesis_Presentation_Reworked.odp — proposed for slide 26 "ASF Robustness Study Summary" (slide 27 "Conclusion" content merged in; slide 27 itself not yet touched, both currently contain only leftover placeholder boilerplate text, not real content)
**Story-arc step:** closing results synthesis, merges the thesis's RQ1-RQ3 conclusion answers with its "Reinforced/New/Contested claims" summary into one slide
**Takeaway (one sentence):** Verdict stat-strip (17/22 conditions within -8.8%; LiDAR collapses -74.9 to -76.4%; frame deletion fails all 3 modalities) plus a 3-column Reinforced/New/Contested claims table.
**Output:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_a.png, PNG, 3200x570px, sha256=57255117731cb6b44baa485b946b5d36fa9613176b38a9d2f2f2cb13d9ff6396
**Script:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_a.py; new this session
**Command:** `cd /home/adhish/Productivity/AMSCUP && python3 docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_a.py`
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing dirty files, unrelated)
**Environment:** system Python 3.14.7, Pillow. No data pipeline.
**Inputs:** docs/Latex_Report/thesis_report/include/Conclusion.tex (Conclusions/RQ1-3 section and "ASF Robustness Study Summary" subsection, lines 7-54) — all numbers/claims transcribed directly from that source text, no external facts.
**Processing:** Hand-authored content, no data pipeline; numbers copied verbatim from Conclusion.tex (17/22, -8.80%, 14.9-76.4%, -74.9%/-76.4%).
**Scope:** Whole-thesis summary — not scoped to a single IoU/class/sequence/condition.
**Numbers shown:** "17/22 conditions within -8.8% of baseline" (Conclusion.tex L14, RQ1 answer); "-74.9% to -76.4% LiDAR Gaussian-noise collapse" (Conclusion.tex L14/L28, matches Results chapter pooled mAP drop); "3/3 modalities fail under frame deletion" (Conclusion.tex L14/L34). All three traced to Conclusion.tex text, not independently recomputed from parquet in this session (they are the thesis's own already-computed/reported figures).
**Statistics:** N/A — reusing already-reported thesis statistics, no new computation.
**Style:** New composite convention for this slide: stat-callout boxes (navy/warning-red accents) + 3-column table (same navy/accent-blue/Noto Sans table convention as other deck figures).
**Integrity:** [x] no invented numbers — all three headline stats and all three table cells trace to Conclusion.tex quoted above [x] no external images reused [x] output visually inspected (rendered PNG viewed directly) [ ] not yet re-verified against the underlying parquet/CSV — numbers are the thesis's own already-published conclusion figures, treated as authoritative source; flagged as N/A for parquet cross-check since no new computation was done.
**Verification:** Rendered and viewed directly; no clipping, table renders cleanly, stat boxes align. Not yet inserted into the deck — this is a candidate figure only.
**Advisor notes:** One of 3 options generated on user request to showcase slide 26/27 merge content without excess text. Presented alongside Option B (two-panel bullet split) and Option C (icon-row per-sensor verdict + headline). Recommended this option (A) to the user because the slide is a "summary" slide (expected to be information-dense) and because it leads with hard numbers rather than paraphrase.
**Open issues:** (1) Awaiting user's choice of A/B/C (or a mix) before any insertion. (2) If chosen, still need to decide what happens to slide 27 itself (delete/repurpose/leave as a shorter closing slide) — not addressed by this figure. (3) "Contested" cell mentions ASF's broad claim but omits the camera-training-protocol confound (Conclusion.tex L54) for space — flag if that nuance must be retained.
---

---
### FIG-20260925-000000-rework-slide26-27-merge-option-b
**Status:** DRAFT (candidate, not yet chosen or inserted)
**Supersedes:** N/A
**Deck:** Thesis_Presentation_Reworked.odp — proposed for slide 26 "ASF Robustness Study Summary" (same merge target as option A)
**Story-arc step:** closing results synthesis (see option A)
**Takeaway (one sentence):** Two-panel bullet split: left "The Verdict" (RQ1/RQ2 answers, 3 bullets), right "New vs. Contested" (2 new findings + 1 contested claim).
**Output:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_b.png, PNG, 3200x461px, sha256=11fba02915d0488f9789c07ae68e60c7a2d854879c3ebd1e3088b086fefc4fa1
**Script:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py; new this session; iterated once in-session (panel height was fixed to full canvas height initially, leaving large dead space below the bullets; fixed by computing each panel's content height first and sizing both panels to the max of the two, matching the row-height-sync technique used in the slide 8 tables figure)
**Command:** `cd /home/adhish/Productivity/AMSCUP && python3 docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py`
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing dirty files, unrelated)
**Environment:** system Python 3.14.7, Pillow.
**Inputs:** docs/Latex_Report/thesis_report/include/Conclusion.tex (same source as option A).
**Processing:** Hand-authored bullets condensed from Conclusion.tex text; numbers copied verbatim (17/22, -8.8%, 14.9-76.4%, 20/21).
**Scope:** Whole-thesis summary.
**Numbers shown:** "17 of 22 conditions... -8.8%" (L14), "5 conditions collapse by 14.9-76.4%... frame deletion fails all 3" (L14), "missed detections... 20/21 conditions" (L50). All traced to Conclusion.tex.
**Statistics:** N/A — reusing thesis's own reported figures.
**Style:** Two-panel bulleted-card layout (navy/light-gray panel convention, Noto Sans), new for this slide.
**Integrity:** [x] no invented numbers (all trace to Conclusion.tex, quoted above) [x] no external images [x] output visually inspected [ ] not independently re-verified against parquet (same rationale as option A).
**Verification:** Rendered and viewed directly after the panel-height fix; both panels now end at the same baseline, no dead space, no clipping. Not yet inserted into the deck.
**Advisor notes:** Drops the "Reinforced claims" category entirely (least novel content) to keep both panels short. Simpler to read than option A but shows fewer numbers.
**Open issues:** Same as option A (1)-(2). Additionally: (3) omits the "Reinforced" claims (LiDAR costliest/camera least) — confirm this omission is acceptable if this option is chosen.
---

---
### FIG-20260925-000000-rework-slide26-27-merge-option-c
**Status:** DRAFT (candidate, not yet chosen or inserted)
**Supersedes:** N/A
**Deck:** Thesis_Presentation_Reworked.odp — proposed for slide 26 "ASF Robustness Study Summary" (same merge target as options A/B)
**Story-arc step:** closing results synthesis (see option A)
**Takeaway (one sentence):** Three per-sensor icon cards (Camera/Radar/LiDAR) each with a verdict badge and one-line detail, plus a single headline sentence stating the scope boundary.
**Output:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_c.png, PNG, 3200x820px, sha256=0808eba14c513489eda10f8afd0bebe1f4149d07274003676e36526dd5e6f81b
**Script:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_c.py; new this session. Icons are hand-drawn PIL primitives (rectangles/ellipses/arcs/lines) built for this figure specifically, not sourced from any icon library or external asset.
**Command:** `cd /home/adhish/Productivity/AMSCUP && python3 docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_c.py`
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing dirty files, unrelated)
**Environment:** system Python 3.14.7, Pillow.
**Inputs:** docs/Latex_Report/thesis_report/include/Conclusion.tex (same source as options A/B).
**Processing:** Hand-authored badges/details condensed from Conclusion.tex text; numbers copied verbatim (-14.9%/-22.7%, -74.9%/-76.4%).
**Scope:** Whole-thesis summary.
**Numbers shown:** Radar "-14.9% to -22.7% under noise" (L16), LiDAR "-74.9% to -76.4% under Gaussian noise" (L14/L28). Camera card states "negligible impact" with no number (L16/L30 support this qualitatively; no single camera AP-delta number is quoted in Conclusion.tex itself, so none was invented here — flagged below).
**Statistics:** N/A.
**Style:** New icon-card convention (navy line-art icons, colored verdict badges: green=graceful, amber=noisy>absent, red=collapses) — first use of a non-tabular, iconographic figure in this deck; palette kept consistent with the existing navy/accent scheme.
**Integrity:** [x] no invented numbers for radar/LiDAR (traced to Conclusion.tex) [x] camera card intentionally left number-free rather than inventing one — see Open issues [x] no external images/icon libraries reused (icons are original PIL primitives drawn for this figure) [x] output visually inspected.
**Verification:** Rendered and viewed directly; icons render cleanly at this size, badges legible, headline wraps correctly. Not yet inserted into the deck.
**Advisor notes:** Most visually compressed of the three but drops the most content (no Reinforced/Contested claims, no RQ1 "17/22" figure). Best suited as a memorable closer rather than a complete summary.
**Open issues:** Same as option A (1)-(2). Additionally: (3) Camera's card has no supporting number (thesis text describes it qualitatively as "negligible"/"12-13% max deviation" appears elsewhere in Discussion, not in Conclusion.tex itself — if this option is chosen, decide whether to pull that number in from Discussion.tex or keep it qualitative).
---

---
### FIG-20260925-000100-rework-slide26-27-merge-option-b-revised
**Status:** FINAL (chosen option, pending slide 27 disposition decision before insertion)
**Supersedes:** FIG-20260925-000000-rework-slide26-27-merge-option-b (DRAFT)
**Deck:** Thesis_Presentation_Reworked.odp — proposed for slide 26 "ASF Robustness Study Summary" (not yet inserted)
**Story-arc step:** closing results synthesis (see superseded entry)
**Takeaway (one sentence):** Same as superseded entry, minus the availability-flag mechanism bullet: right panel now reads "missed detections drive degradation" + "ASF's broad claim overstates what was tested."
**Output:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_b.png (overwritten in place), PNG, 3200x408px, sha256=0cbe903d8815d45b2f1625d5711e33b2a5b6563edc04a9102cf9440b727c9a42
**Script:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py; edited in place (removed one right_bullets entry)
**Command:** `cd /home/adhish/Productivity/AMSCUP && python3 docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py`
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing dirty files, unrelated)
**Environment:** system Python 3.14.7, Pillow.
**Inputs:** Same as superseded entry (Conclusion.tex).
**Processing:** Removed the bullet "New: noisy-but-present > absent traces to ASF's availability flag never being set" per explicit user instruction; panel heights re-synced automatically via the existing max-of-both-panels logic, no dead space introduced.
**Scope:** Whole-thesis summary.
**Numbers shown:** "20/21 conditions" (Conclusion.tex L50) retained; all other numbers unchanged from superseded entry.
**Statistics:** N/A.
**Style:** Unchanged from superseded entry.
**Integrity:** [x] no invented numbers [x] no external images [x] output visually inspected — re-rendered and viewed, both panels re-synced with no dead space or clipping.
**Verification:** Rendered and viewed directly. Result: PASS. Not yet inserted into the deck — awaiting decision on slide 27's fate before insertion.
**Advisor notes:** User picked option B over A/C, then asked to drop the availability-flag mechanism detail from the first "New" bullet. Interpreted as removing the whole bullet (its entire content was that mechanism claim; the surviving "noisy > absent" finding is already stated in the left panel's third bullet, so nothing distinctive was lost).
**Open issues:** (1) Still need a decision on slide 27 ("Conclusion") — delete it, repurpose it, or leave a shorter version, before this figure is inserted anywhere. (2) Not yet inserted into the deck (no explicit insertion instruction given yet).
---

---
### FIG-20260925-000200-rework-slide26-summary-option-b-inserted
**Status:** FINAL
**Supersedes:** N/A (installs FIG-20260925-000100-rework-slide26-27-merge-option-b-revised)
**Deck:** Thesis_Presentation_Reworked.odp — slide 26 "ASF Robustness Study Summary" (document position 26; NOT the same as PDF page 26 — see Verification)
**Story-arc step:** closing results synthesis
**Takeaway (one sentence):** Replaced the slide's existing hand-drafted body text (an in-progress "ASF had performed a small robustness study..." paragraph with unfilled `<fill this>` placeholders, plus Reinforced Claims/New Findings bullet lists) with the chosen summary_option_b.png figure.
**Output:** Deck-embedded copy: Pictures/summary_option_b_slide26.png inside Thesis_Presentation_Reworked.odp, identical bytes to /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_b.png, sha256=0cbe903d8815d45b2f1625d5711e33b2a5b6563edc04a9102cf9440b727c9a42
**Script:** N/A for this entry (figure itself covered by FIG-20260925-000100); insertion done via direct ODF XML edit.
**Command:** N/A (no regeneration); ODF edit via Python (re.sub on content.xml, manifest.xml append), repack via `zip -X -0 -q "$OUT" mimetype` then `zip -X -rq "$OUT" . -x mimetype -x "Thesis_Presentation_Reworked_new.odp"`.
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing dirty files, unrelated; docs/Thesis_Presentation_Reworked.odp modified by this entry).
**Environment:** LibreOffice (soffice headless) for render verification; Python 3.14.7 stdlib (re, zipfile) for the ODF XML edit.
**Inputs:** The chosen figure (FIG-20260925-000100). Removed content: the slide's own pre-existing draft text (custom-shape "gr57"), not authored by this session.
**Processing:** Replaced the `<draw:custom-shape draw:style-name="gr57">` block (the slide's real body content, 22.46cm x 11.538cm at x=1.67cm, y=2.695cm) with a `<draw:frame>` image frame referencing the new picture, sized to the image's native aspect ratio (3200x408, 7.843:1) at the same width (22.46cm), height 2.864cm, vertically centered within the original body region (y=7.032cm) rather than stretched to fill it (stretching would have distorted the figure). Two other, empty (`draw:fill="none"`, no text) custom-shapes on this slide (gr58, gr59) were left untouched — they render nothing and were not part of the requested edit.
**Scope:** N/A — synthesis/summary slide.
**Numbers shown:** Same as FIG-20260925-000100 (all traced to Conclusion.tex).
**Statistics:** N/A.
**Style:** Unchanged from FIG-20260925-000100.
**Integrity:** [x] no invented content [x] no external images beyond the approved figure [x] output visually inspected (see Verification) [x] every number traced (see FIG-20260925-000100).
**Verification:** A second instance of the hidden-slide/PDF-page-offset issue: rendering PDF page 26 directly showed the deck's closing Chalmers logo slide, not slide 26. Investigation found 3 hidden slides (document positions 9 "K-Radar and ASF", 24 "page24", 25 "page25", all styled `dp4` with `presentation:visibility="hidden"` — defined as an automatic style inside content.xml itself, not in styles.xml, which is why an earlier session's check of styles.xml alone found none) all preceding document position 26, shifting the correct PDF page to 26-3=23. Re-rendered PDF page 23: confirmed title "ASF Robustness Study Summary", on-slide page-number field reading "26" (matching document position), the summary_option_b figure placed cleanly below the title with no clipping/overlap/stretching, Chalmers branding intact. Result: PASS.
**Advisor notes:** Discovered that slide 26 was NOT an empty placeholder slide as previously assumed — it already contained real, hand-drafted body text (an unfinished paragraph with `<fill this>`/`<fill>` gaps, plus Reinforced Claims/New Findings bullets closely paralleling the thesis's own Conclusion.tex structure). This existing text was inside a `<draw:custom-shape>` element, which an earlier session's slide-content survey (which only scanned `<draw:frame>` elements) did not detect — it had reported both slide 26 and 27 as containing only placeholder boilerplate, which was true only of the speaker-notes text, not the slide body. The user's original merge request and the three generated options were based on the thesis text directly, not on this pre-existing draft, but the final content is materially consistent with the pre-existing draft's Reinforced Claims/New Findings framing.
**Open issues:** (1) Slide 27 ("Conclusion") still needs a decision — delete, repurpose, or shorten — this entry only touched slide 26. (2) The full, complete hidden-slide inventory as of now is: document positions 9, 24, 25 (3 total) — supersedes the earlier session's finding of "2 hidden slides at positions 9 and 23," which was based on an incomplete styles.xml-only check; flagging to the user since this affects any future PDF-page verification math and any live-presentation slide count. (3) Two empty, invisible custom-shapes (gr58, gr59) remain on slide 26, inherited from the pre-existing draft — harmless (no fill/stroke/text) but noted in case they were meant to hold additional figures.
---

---
### FIG-20260925-000300-rework-slide26-summary-option-b-rq-reworked
**Status:** FINAL
**Supersedes:** FIG-20260925-000200-rework-slide26-summary-option-b-inserted
**Deck:** Thesis_Presentation_Reworked.odp — slide 26 "ASF Robustness Study Summary" (document position 26; PDF page 23, see prior entry's hidden-slide note)
**Story-arc step:** closing results synthesis
**Takeaway (one sentence):** Reworked the figure: larger font (title 44->54pt, body 32->40pt) and left panel restructured from generic "Verdict" bullets into explicit RQ1/RQ2/RQ3 answers (renamed "Research Questions"), right panel unchanged ("New vs. Contested").
**Output:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_b.png (overwritten in place), PNG, 3200x637px, sha256=b0b52659bc61dc47928d4d6d72f6f1129dd7a9b1a916926f8c550f2fe9af6a97; deck-embedded copy Pictures/summary_option_b_slide26.png, identical bytes.
**Script:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py; edited in place (font sizes, left_bullets content, left panel title)
**Command:** `cd /home/adhish/Productivity/AMSCUP && python3 docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py`
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing dirty files, unrelated; docs/Thesis_Presentation_Reworked.odp modified by this entry)
**Environment:** system Python 3.14.7, Pillow (figure); LibreOffice headless (render verification); Python stdlib re/zipfile (ODF edit).
**Inputs:** docs/Latex_Report/thesis_report/include/Conclusion.tex (RQ1/RQ2/RQ3 answers, lines 14-18) for the left panel; unchanged New/Contested content from the prior entry for the right panel.
**Processing:** Left panel bullets rewritten to explicitly label and answer RQ1 ("Robust to 17/22 conditions... frame deletion fails all 3", Conclusion.tex L14), RQ2 ("noisy-but-present... worse than absent, LiDAR/radar", L16), RQ3 ("camera and radar degrade gracefully; LiDAR collapses abruptly", L18). Panel title changed "The Verdict" -> "Research Questions". Image frame geometry in the deck updated to match the new pixel aspect ratio (3200x637, same as pre-font-increase version, so no re-fit was needed beyond the font-size change already applied in the prior entry's follow-up).
**Scope:** N/A — synthesis/summary slide.
**Numbers shown:** "17/22... -8.8%" (L14), "5 collapse... frame deletion fails all 3" (L14), "20/21 conditions" (L50, right panel, unchanged). All traced to Conclusion.tex.
**Statistics:** N/A.
**Style:** Font sizes increased (title_font 44->54, body_font 32->40) per explicit user request; otherwise unchanged from prior entry.
**Integrity:** [x] no invented numbers — RQ1-3 phrasing condensed directly from Conclusion.tex lines 14-18, quoted above [x] no external images [x] output visually inspected, both before and after deck insertion.
**Verification:** Rendered figure viewed directly (larger fonts, RQ-labeled bullets, both panels re-synced with no dead space). Re-extracted the deck, replaced Pictures/summary_option_b_slide26.png, updated the image frame's svg:height/svg:y to preserve the new aspect ratio and vertical centering (height 2.864cm->4.471cm, y 7.032cm->6.229cm; width/x unchanged), repacked, backed up (Thesis_Presentation_Reworked.backup_20260925_005223.odp), rendered to PDF, rasterized PDF page 23 (= document position 26, accounting for the 3 hidden slides at positions 9/24/25). Confirmed: title, page number "26", both panels legible at the larger font size, no clipping/overlap, Chalmers branding intact. Result: PASS. Installed to docs/Thesis_Presentation_Reworked.odp, sha256=b22492f391a68e938b2463f88c28bb0f7bb7f7d586cbd8611ec2533b9ce089da.
**Advisor notes:** User asked to (1) increase font size, then (2) restructure so the left panel directly answers the Conclusion chapter's RQ1-3 rather than reading as generic bullets, keeping the right panel as New/Contested. Both changes applied together in this entry before reinsertion (font-size-only intermediate version was generated but not installed to the deck, superseded before installation).
**Open issues:** Same as prior entry: (1) slide 27 ("Conclusion") disposition still undecided. (2) 3 hidden slides remain at document positions 9/24/25 (unaffected by this change, flagged previously).
---

---
### FIG-20260925-000400-rework-slide26-summary-option-b-font-larger
**Status:** FINAL
**Supersedes:** FIG-20260925-000300-rework-slide26-summary-option-b-rq-reworked
**Deck:** Thesis_Presentation_Reworked.odp — slide 26 "ASF Robustness Study Summary" (document position 26; PDF page 23)
**Story-arc step:** closing results synthesis
**Takeaway (one sentence):** Same content as prior entry (RQ1-3 left panel, New/Contested right panel), font sizes increased further (title 54->66pt, body 40->50pt) per explicit user request.
**Output:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_b.png (overwritten), PNG, 3200x728px, sha256=a3681c1990dc6e8e338efdaea48df9b8ebc0f8e0dcf4ee831a77da4f25696da9; deck copy Pictures/summary_option_b_slide26.png identical bytes.
**Script:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py; edited in place (title_font 54->66, body_font 40->50)
**Command:** `cd /home/adhish/Productivity/AMSCUP && python3 docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py`
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing, unrelated; docs/Thesis_Presentation_Reworked.odp modified by this entry)
**Environment:** system Python 3.14.7, Pillow; LibreOffice headless render verification; Python stdlib re/zipfile for ODF edit.
**Inputs:** No new source material — text unchanged from prior entry (still traces to Conclusion.tex L14-18, L50).
**Processing:** Font-size-only change to the PIL script; panel heights re-synced automatically (existing max-of-both logic). Deck image frame geometry updated to match new aspect ratio (3200x728, 4.396:1): width unchanged 22.46cm, height 4.471cm->5.11cm, y recentered 6.229cm->5.909cm within the same 2.695-14.233cm body region, x/width unchanged.
**Scope:** N/A.
**Numbers shown:** Unchanged from prior entry.
**Statistics:** N/A.
**Style:** Font sizes increased per user request; palette/layout otherwise unchanged.
**Integrity:** [x] no invented content (text unchanged from prior FINAL entry) [x] no external images [x] output visually inspected before and after deck insertion.
**Verification:** Rendered figure viewed directly — larger text, no overflow, panels still height-synced. Backed up deck (Thesis_Presentation_Reworked.backup_20260925_005536.odp), re-extracted, replaced picture, updated frame geometry, repacked (mimetype-first/stored, verified), rendered to PDF, rasterized PDF page 23 (= document position 26). Confirmed: title, page number "26", both panels legible at larger size, no clipping/overlap, Chalmers branding intact. Result: PASS. Installed, sha256=ba6c8f0773df55afa7b0e81d1213915711b3db3e39d443bccc112b1f8335138e.
**Advisor notes:** Second font-size increase in a row (54/40pt -> 66/50pt) at explicit user request, no content change this round.
**Open issues:** Same as prior entries: (1) slide 27 disposition still undecided. (2) 3 hidden slides at document positions 9/24/25 remain (unrelated to this change).
---

---
### FIG-20260925-000500-rework-slide26-summary-option-b-target-questions
**Status:** FINAL
**Supersedes:** FIG-20260925-000400-rework-slide26-summary-option-b-font-larger
**Deck:** Thesis_Presentation_Reworked.odp — slide 26 "ASF Robustness Study Summary" (document position 26; PDF page 23)
**Story-arc step:** closing results synthesis
**Takeaway (one sentence):** Left panel renamed "Research Questions" -> "Target Questions", bullet labels RQ1/RQ2/RQ3 -> T1/T2/T3; wording and numbers unchanged. Right panel unchanged.
**Output:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/summary_option_b.png (overwritten), PNG, 3200x728px (unchanged dimensions), sha256=c3dbfdb663efee5d541f3d67d887c238a2c608165baebad7f304a0576428864c; deck copy Pictures/summary_option_b_slide26.png identical bytes.
**Script:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py; edited in place (panel title string, "RQ1/RQ2/RQ3" -> "T1/T2/T3" label prefixes in left_bullets)
**Command:** `cd /home/adhish/Productivity/AMSCUP && python3 docs/crossproduct_figures/thesis_defense/scripts/make_summary_option_b.py`
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing, unrelated; docs/Thesis_Presentation_Reworked.odp modified by this entry)
**Environment:** system Python 3.14.7, Pillow; LibreOffice headless render verification; Python stdlib re/zipfile for ODF edit.
**Inputs:** No new source material — content unchanged from prior entry (still traces to Conclusion.tex L14-18, L50); only the label scheme changed per explicit user instruction.
**Processing:** Pure relabeling, no wording/number change beyond the T1/T2/T3 prefixes and panel title. Output image dimensions identical to prior entry (3200x728), so no deck frame-geometry change was needed, only the embedded picture bytes were swapped.
**Scope:** N/A.
**Numbers shown:** Unchanged from prior entry.
**Statistics:** N/A.
**Style:** Unchanged.
**Integrity:** [x] no invented content — pure relabel of already-verified text [x] no external images [x] output visually inspected before and after deck insertion.
**Verification:** Rendered figure viewed directly. Backed up deck (Thesis_Presentation_Reworked.backup_20260925_005832.odp), re-extracted, swapped Pictures/summary_option_b_slide26.png (frame geometry left untouched, confirmed identical dimensions), repacked (mimetype-first/stored, verified), rendered to PDF, rasterized PDF page 23 (= document position 26). Confirmed: title, page number "26", "Target Questions" / T1-T3 labels render correctly, no clipping, Chalmers branding intact. Result: PASS. Installed, sha256=3849f64a34f1157ec33c6495de539653fa1ddbf03f3a8dbc1112c410ea082f8c.
**Advisor notes:** Pure relabeling request (RQ -> T, "Research Questions" -> "Target Questions"), no content change.
**Open issues:** Same as prior entries: (1) slide 27 disposition still undecided. (2) 3 hidden slides at document positions 9/24/25 remain (unrelated to this change).
---

---
### FIG-20260925-020000-rework-slide28-future-work-humanized
**Status:** FINAL
**Supersedes:** N/A (text-only edit to an already-drafted slide, not a new figure)
**Deck:** Thesis_Presentation_Reworked.odp — slide 28 "Future Work" (document position 28)
**Story-arc step:** closing / future work
**Takeaway (one sentence):** Ran a humanizer pass on the slide's existing 4 bullets (2 under "Robustness Analysis", 2 under "Robustness of ASF") to fix a grammar error, a typo, and an AI-pattern gerund, and to match the deck's now-terser tone; subheadings and structure unchanged.
**Output:** N/A — text-only edit, no new image/figure file. No new Pictures/ entry.
**Script:** N/A
**Command:** N/A (direct ODF XML edit via Python re.sub on the `gr61` custom-shape's text content in content.xml)
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing, unrelated; docs/Thesis_Presentation_Reworked.odp modified by this entry)
**Environment:** LibreOffice headless (render verification); Python 3.14.7 stdlib (re, zipfile) for the ODF edit.
**Inputs:** The slide's own pre-existing text (not authored by this session originally): "Cross-architecture and cross-dataset replication and verify if findings from the study stays the same"; "Extending the corruption taxonomy to replicate accurately different real life adverse conditions"; "Deeper analysis of ASF delving into dropping modalities and studying scale of shift propogated by the backbone output"; "Study if the same findings are replicated for models in the same robustness family".
**Processing:** Humanizer-style edit (per /humanizer:humanizer conventions): fixed subject/verb disagreement ("findings...stays"->"hold"), fixed typo "propogated"->"propagated" (implicitly, by rewording the clause), removed the AI-flagged gerund construction "delving into", tightened wording, converted to imperative/direct-verb phrasing matching the rest of the deck's tone (e.g. slide 26's T1-T3 bullets). No new facts or scope added; each bullet's claim/scope preserved exactly (still 2 future-work directions per subheading).
**Scope:** N/A — text-only.
**Numbers shown:** None.
**Statistics:** N/A.
**Style:** No figure/table style involved — text edit only, in the slide's existing custom-shape/list formatting (font/list style names T18/T34/L7 unchanged).
**Integrity:** [x] no invented content — every bullet's underlying claim preserved from the original slide text, only grammar/wording/tone changed [x] no external images [x] output visually inspected after insertion (see Verification) [x] no scope/hedging change — original bullets contained no hedging language to preserve.
**Verification:** Shown to the user as a chat preview first (not applied), per the deck's "no silent design decisions" rule; user confirmed "Add the changes." Backed up deck (Thesis_Presentation_Reworked.backup_20260925_015035.odp), edited content.xml directly, repacked (mimetype-first/stored, verified), rendered to PDF. Note: discovered a 4th hidden slide (document position 5, "Objective", style dp4/hidden) that was NOT present in this session's earlier backups (as of backup_20260925_005832.odp, only 3 hidden slides existed: positions 9/24/25) — it must have been changed outside this session's edits, since no tool call in this session touched slide 5 or its style. Recomputed the correct PDF page for document position 28 accounting for all 4 now-hidden slides (28-4=24) and rasterized PDF page 24: confirmed title "Future Work", on-slide page number "28" (matching document position), both subheadings and all 4 humanized bullets rendered correctly, no clipping, Chalmers branding intact. Result: PASS. Installed, sha256=d214fbc87d13dfc2abb0b20dfea95bec17f08d63820f2983e2a22fff580dd90c.
**Advisor notes:** User asked for a humanizer pass matching the rest of the presentation's tone; showed a preview in chat first (matching the earlier slide-6-humanizer precedent), then applied on explicit "Add the changes" instruction.
**Open issues:** (1) A 4th hidden slide (document position 5, "Objective") now exists in the deck, in addition to the previously-flagged 3 (positions 9/24/25) — total is now 4 hidden slides. This was not introduced by any edit in this session; flagging since it changes the PDF-page/document-position offset math for all subsequent verification and affects the live-presentation slide count. User should confirm this is intentional. (2) Slide 27 ("Conclusion") disposition still undecided (carried over from earlier entries).
---

---
### FIG-20260925-090500-rework-fig11-fig12-av-reasoning-label
**Status:** FINAL
**Supersedes:** N/A (pixel edit of two pre-existing raster images not created by this session and not previously logged with a source script)
**Deck:** Thesis_Presentation_Reworked.odp — slide 2 "Case Study: Reality Gap" (caption "Fig 1.1 Reported real-world autonomous vehicle failures and their consequences") and slides 3/4 "Introduction" (caption "Fig 1.2 Snippet of examples of Autonomous vehicle failure")
**Story-arc step:** motivating case study, opening of the deck
**Takeaway (one sentence):** Changed the row label "AV PERCEPTION REASONING FOR FAILURE" to "AV REASONING FOR FAILURE" in both the full comparison table (Fig 1.1, slide 2) and its cropped/reused row (Fig 1.2, slides 3-4), per explicit user request; no other cell content touched.
**Output:** Two deck-embedded images overwritten in place (no new Pictures/ filenames): `Pictures/10000000000007B000000214B12A1D91.png` (Fig 1.1, full table, 1968x532px, sha256=ad739087dab88356d5090adadd482984472118af203ba1db1fd4b53951641c89) and `Pictures/10000000000007B00000009BD198B90D.png` (Fig 1.2, cropped row reused on slides 3 and 4, 1968x155px, sha256=c8e15b7d695c3a290e82846086b0c15eb2a3ab2c630fcde193cad70d9f839dd5).
**Script:** No source script exists for these two images anywhere in the repo (searched by distinctive on-image text: "untransversable", "3,791 vehicles", "EA26002", "Gannon Storm" — no hits in any .py/.md); they predate this session's figure-log/script convention. Edit performed as a direct pixel-level PIL edit (ad hoc, not saved as a standalone script) rather than a full regeneration, since the underlying data/layout for the rest of the table is unknown/unrecoverable as source.
**Command:** Ad hoc Python (PIL) run interactively; not saved as a reusable script (see note above — flagged as an open issue).
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing, unrelated; docs/Thesis_Presentation_Reworked.odp modified by this entry)
**Environment:** Python 3.14.7, Pillow (pixel edit); Noto Sans Bold (`/usr/share/fonts/noto/NotoSans-Bold.ttf`, matching the deck's established font); LibreOffice headless for render verification.
**Inputs:** The two existing embedded PNGs themselves (extracted from the live .odp). Reference color/font sampled directly from the existing image pixels: label-cell background (221,225,230), text color navy (25,68,97) — this navy is bit-for-bit identical to the deck's established `#194461` palette used throughout this session's other figures, confirming visual consistency even though this image predates the convention.
**Processing:** For each image: measured the exact pixel bounding box of the existing 3-line label text ("AV PERCEPTION"/"REASONING"/"FOR FAILURE") by scanning for navy-colored pixels (line tops at consistent 30px pitch, cap-height ~13px in both images); matched font size (Noto Sans Bold, 20pt) empirically by rendering "AV PERCEPTION" at several sizes and comparing pixel width to the original (155px) until a match (20pt -> 156px); cleared a rectangle covering the old text (with margin, confirmed not to intrude into the "WHAT HAPPENED" text above or "OUTCOME/LOSS" text below) with the sampled background color; drew the new 2-line text ("AV REASONING"/"FOR FAILURE") at the same left margin (x=12) and same overall vertical center as the original 3-line block, using the same 30px line pitch.
**Scope:** N/A — motivating case-study figure, not a results figure.
**Numbers shown:** Unchanged (3,791 vehicles recalled; 9 crashes/1 fatality/1 injury; >$500M farming losses) — these are pre-existing case-study facts from public news/regulatory sources (SF Chronicle, NHTSA ODI, Space.com), not touched by this edit and not independently re-verified in this session (out of scope for this request).
**Statistics:** N/A.
**Style:** Matched exactly to the pre-existing image's own font/color/spacing (Noto Sans Bold, navy #194461, 30px line pitch) rather than the newer PIL-script convention used elsewhere in this session, since this was a surgical edit to an existing asset, not a new figure.
**Integrity:** [x] no invented content — only the label wording was changed per explicit instruction, all other cells/data untouched and unverified-because-out-of-scope [x] no external images newly reused (edited an already-embedded image in place) [x] output visually inspected, both as standalone crops and via full deck render on both affected slides [x] font/color matched empirically to the existing image rather than guessed.
**Verification:** Rendered both fixed images and visually inspected before insertion (label reads cleanly, no artifacts at the edit boundary, background seam invisible). Backed up deck (Thesis_Presentation_Reworked.backup_20260925_090403.odp), swapped both PNGs in place inside the extracted .odp (same filenames, so no content.xml or manifest.xml change was needed), repacked (mimetype-first/stored, verified), rendered to PDF, rasterized PDF pages 2, 3, 4 (document positions 2/3/4, unaffected by the hidden-slide offset since all 4 currently-hidden slides are at document positions 5/9/24/25, all after these). Confirmed on slide 2: "AV REASONING FOR FAILURE" row label, rest of Fig 1.1 table intact, caption "Fig 1.1 Reported real-world autonomous vehicle failures and their consequences" visible below the table (confirming the user's "Fig 1.1" reference). Confirmed on slide 3: same fix in the cropped row, caption "Fig 1.2 Snippet of examples of Autonomous vehicle failure" visible below it (confirming "Fig 1.2"). Slide 4 uses the identical image reference, covered by the same fix. Result: PASS. Installed, sha256=bad66b6f9a26a9ce947e85f06aecf794335b145b7c119fb4b7163540ce6f1cbd.
**Advisor notes:** User referred to "Fig 1.1 and 1.2" by their on-slide captions, which matches exactly: Fig 1.1 = slide 2's full comparison table, Fig 1.2 = slide 3/4's cropped row reuse of the same table. Confirmed via WebFetch-free direct verification (found the paper text locally in docs/lit_survey/asf.txt) in the prior conversation turn that this table itself is unrelated to that ASF-paper question; this label-wording change is a separate, presentation-only edit.
**Open issues:** (1) No source script/generation process exists for this table anywhere in the repo; if further edits to this table's content (not just this one label) are ever needed, a full script would need to be written from scratch reading off the current pixel content, since there's no way to regenerate it from a known source. (2) The rest of this table's content (dates, quotes, outcome figures) was not verified or touched in this entry — flagging since these are real-world case-study facts (Waymo recall, Tesla FSD investigation, solar storm) sourced from external news/regulatory sites, not from the thesis itself, and their accuracy/currency has not been checked by this session. (3) Slide 27 disposition and the newly-hidden slide 5 ("Objective") both remain open from earlier entries.
---

---
### FIG-20260925-092500-rework-abbreviations-slide32
**Status:** FINAL
**Supersedes:** N/A (new slide)
**Deck:** Thesis_Presentation_Reworked.odp — new slide 32 "Abbreviations" (document position 32, inserted after the former last slide, document position 31, a Table 5.2 screenshot)
**Story-arc step:** reference/appendix, deck closer
**Takeaway (one sentence):** A 3-column glossary table (Metrics & Evaluation / Sensors & Hardware / Model & Methodology) covering every abbreviation found across all 31 existing slides, both in editable text and in embedded raster figures.
**Output:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/abbreviations_slide.png, PNG, 3200x780px, sha256=3ef7aaffed872024fc241610855d0fa6a6112c7c40cca9808fc2d7fa95ef5b3c; deck-embedded copy Pictures/abbreviations_slide.png, identical bytes.
**Script:** /home/adhish/Productivity/AMSCUP/docs/crossproduct_figures/thesis_defense/scripts/make_abbreviations_slide.py; new this session, follows the established wrap_table/draw_table row-height-safe convention (same `wrap()` overflow assertion as make_dataset_model_tables.py).
**Command:** `cd /home/adhish/Productivity/AMSCUP && python3 docs/crossproduct_figures/thesis_defense/scripts/make_abbreviations_slide.py`
**Repo state:** git rev-parse HEAD = 9ca85c28928ac23012b89e4dd3816502b4a82236; tree dirty (pre-existing, unrelated; docs/Thesis_Presentation_Reworked.odp modified by this entry)
**Environment:** system Python 3.14.7, Pillow (figure); LibreOffice headless (render verification); Python stdlib re/zipfile for the ODF edit (new `<draw:page>` inserted directly into content.xml, plus a manifest.xml entry).
**Inputs:** Every editable text span across all 31 existing slides (extracted via regex over content.xml, notes excluded) plus every embedded raster figure referenced by those slides, manually reviewed for acronym content: the metrics-definitions table (Fig 7), the pooled-metrics results table (Fig 10.1/10.2, source of mATE/mASE/mAOE/FP/FN column headers), the dataset/model comparison table (slide 8, source of HD), the ASF pipeline diagram (Fig 4, source of UCP/CASAP/PN/SCL/FM/FV/GT/Obj/Cls/SC), and the K-Radar sensor-placement schematic (Fig 2, source of RTK-GPS/IMU). Expansions for UCP/CASAP/PN/SCL cross-checked against `docs/Latex_Report/thesis_report/include/ASF.tex` subsection titles (lines 68, 77, 86, 96: "Unified Canonical Projection (UCP)", "Cross-Attention across Sensors Along Patches (CASAP)", "Post-feature Normalisation (PN)", "Sensor Combination Loss (SCL)") rather than guessed from the diagram alone.
**Processing:** Compiled a 3-category, 25-row glossary (Metrics & Evaluation: 9 rows; Sensors & Hardware: 6 rows; Model & Methodology: 10 rows) from the sources above; rendered as 3 independent two-column (abbreviation/meaning) mini-tables side by side via the standard wrap_table/draw_table helpers.
**Scope:** N/A — reference slide, no IoU/class/sequence/condition scope.
**Numbers shown:** None (definitional only).
**Statistics:** N/A.
**Style:** Same bespoke-PIL-script convention as the deck's other table figures (navy #194461/accent-blue #2a6099 header text, Noto Sans Bold/Regular, alternating light-gray rows); no shared plotting module (none exists in the repo, confirmed in Phase 1).
**Integrity:** [x] no invented expansions — every abbreviation's expansion traced to either explicit on-slide/on-figure text or the thesis's own ASF.tex subsection titles (UCP/CASAP/PN/SCL) [x] one abbreviation pair found in a sensor-schematic legend (HR, LR — LiDAR unit codes in Fig. 2, the K-Radar sensor-placement diagram) was deliberately EXCLUDED from this slide because its expansion (e.g. "High-Resolution/Low-Resolution") could not be confirmed against any source text — flagged as an open issue below rather than guessed [x] no external images reused (new figure, hand-authored) [x] output visually inspected before and after deck insertion.
**Verification:** Rendered the standalone figure and viewed it directly (all 25 rows legible, no clipping, three tables cleanly aligned). Backed up the deck (Thesis_Presentation_Reworked.backup_20260925_092246.odp), inserted a new `<draw:page draw:name="page32">` directly after the last existing `</draw:page>` in content.xml (title frame "Abbreviations" + page-number frame + image frame, same structural pattern as slides 8/13/26), added the corresponding manifest.xml entry, confirmed no `presentation:pages`/custom show-order element exists that would need updating, repacked (mimetype-first/stored, verified), rendered to PDF (32 document pages, 4 hidden -> 28 PDF pages, matching), rasterized PDF page 28 (the new last page): confirmed title "Abbreviations", on-slide page number "32" (matching document position), all three glossary columns rendered correctly, Chalmers branding intact. Also re-rendered PDF page 27 (document position 31, the pre-existing Table 5.2 screenshot slide) to confirm it was undisturbed by the insertion. Result: PASS. Installed, sha256=dfbf48172db511d873a2dfcad2034e895d2c98acb197433d578af48b529d4f22.
**Advisor notes:** This required auditing all 31 slides' text AND embedded images (not just text, since most metric/model abbreviations like mATE/mASE/mAOE/UCP/CASAP/SCL only appear inside raster figures, not as editable slide text) to be complete. Deliberately excluded three diagram-only labels that are self-evident in context and would add noise for a defense-slide reference (individual severity/corruption condition codes like "LC"/"GH" seen in the robustness spoke charts, Fig 11/12 -- these are per-chart condition-code axes explained by their own chart legends, not general-purpose abbreviations).
**Open issues:** (1) "HR"/"LR" appear as LiDAR unit codes in the Fig. 2 sensor-schematic legend ("LiDAR (L; HR, LR)") but no source text in the thesis explicitly defines what HR/LR stand for in that context (Methods.tex's own "HR"/"LR" acronym search only turned up an unrelated, commented-out per-object visibility-tag scheme, not sensor-unit codes) -- excluded from this slide rather than guessed; user should supply the correct expansion if this should be added. (2) Slide 27 disposition and the deck's currently-hidden-slide set (positions 9, 24, 25, 27 as of this entry -- this has changed multiple times across the session, apparently from direct manual edits outside these tool calls) remain open from earlier entries.
---
