# Thesis Writing Bible — Chalmers MSc Thesis Rules & Boundaries

*Synthesized from: Bärgman & Mayberry, "Improving academic writing skills" seminar series (4 parts, Chalmers Vehicle Safety); the Personal Scientific Writing Checklist workbook; and the Literature Review Documentation workbook.*

*Purpose: this is the canonical reference against which drafts of the AMSCUP thesis (and any Claude Code prompt for chapter drafting) should be checked. Treat it as a hard-boundary checklist, not inspirational advice — every item below should be independently verifiable in the text.*

---

## 0. Scope and how to use this document

- Use this as a **pre-submission / pre-draft gate**, not just a style guide. Each numbered rule below maps 1:1 to an item in the source checklist.
- Rules are grouped by tier:
  - **[HARD]** — violating this is a defect that should block sign-off (plagiarism, citation integrity, reproducibility gaps).
  - **[STRONG]** — apply unless there's a documented, deliberate reason not to (organization, parallelism, tense).
  - **[STYLE]** — personal/domain preference; confirm with supervisor/examiner before treating as fixed.
- When Claude (or an LLM) is used to check drafts against this bible, it should flag violations **explicitly**, not silently rewrite — consistent with the citation-integrity and "absence of findings requires a coverage statement" conventions already used in this project.

---

## 1. What a Chalmers MSc thesis must demonstrate

**[HARD] Formal requirement.** The thesis is an independent degree project (≥30 HEC) in which the student completes autonomous work and demonstrates the knowledge and ability required for autonomous work as a Master of Science in Engineering.

**[HARD] To pass, the student needs:**
1. Approved planning report
2. Approved presentation and defense
3. Approved opposition to another thesis
4. Attendance at two other presentations
5. Approved essay (the thesis itself)
6. Evidence of having worked actively and autonomously, contributing to an extent corresponding to 30 HEC
7. An up-to-date, examiner-signed work-card throughout

**Assessment weighting (guideline only):**

| Criterion | Weight |
|---|---|
| Content | 50% |
| Holistic impression | 20% |
| Information structure | 30% |

**[STRONG] The 11 MSc learning objectives** the thesis should evidence (abbreviated): apply specialized knowledge and relate it to current R&D; choose and justify method; contribute to R&D and relate to scientific/technical context; identify, formulate, and deal with complex issues holistically, critically, autonomously, creatively; plan and perform qualified tasks and critically evaluate the work; create, analyze, and critically evaluate technical solutions; integrate knowledge critically and systematically; present and discuss solutions clearly in English; identify questions needed to address societal/ethical/ecological aspects; discuss ethical aspects of both *how* the work is done and *what* is investigated; identify and discuss the need for further clarification before decisions/implementation.

---

## 2. The Story — content comes before structure

**[HARD] All scientific writing must have a "story."** The story is the flow of the document: parts early in the document support what comes later, and *every* part must serve the story. If a section doesn't advance the main message, cut it or move it to an appendix.

**[HARD] Know your main message(s) before you write.** A reader must be able to state your main point(s) after reading. The aim/objectives are necessary but not sufficient — the Discussion and Conclusion must explicitly return to and address the stated objectives.

**[STRONG] Reader analysis exercise** (do this before drafting): write ~1/3–1/2 page answering —
- Who are my readers?
- What should they understand after reading?
- What should they be able to do after reading?
- What is my (intended) contribution?

*Applied to AMSCUP*: the narrative arc (radar underused in AV perception → K-Radar as diverse dataset → ASF's robustness claims → what the corruption sweep actually shows, headlined by ASF's failure under medium/high LiDAR Gaussian noise) **is** the story. Every section, figure, and appendix decision should be tested against whether it serves this arc.

**[STRONG] Only include what's relevant.** Students routinely over-include. Test: "What would I want to read as a reader of this thesis?" Not everything you did needs to go in "in full" — secondary material belongs in an appendix.

---

## 3. Structural organization

**[STRONG] There is no single correct order to write in.** Common patterns:
- Intro → Method → Results → Discussion → Conclusion (final reading order, but *typically not the best drafting order*)
- Results → Method → Discussion → Introduction → Conclusion (draft order, "with some cheating") — often the most practical
- Main figures first, then supporting text, then the rest

**[STRONG] The "funneling"/hourglass approach** for overall structure:
- **Introduction**: start wide (ecological concepts / big-picture motivation) → narrow through empirical background → application to your study system → research questions → hypotheses/predictions.
- **Methods**: data collection methods → analysis methods → summary of what was collected.
- **Results**: let figures/tables carry the results; text should not restate everything in the figure, only the most important patterns.
- **Discussion**: widen back out — interpret hypothesis tests and answer research questions → explain meaning for your study system → explain meaning for other/similar research → explain meaning for the wider concepts → discuss assumptions and caveats.

**[HARD] General rule for what belongs in each section:**
| Section | Answers |
|---|---|
| Introduction | What question was studied, and why? |
| Methods | How was the problem studied? |
| Results | What were the findings? |
| Discussion | What do these findings mean? |

**[STRONG] One main point per paragraph.** Do not let a paragraph drift from concept A into concept B into concept C. Split into new paragraphs instead.

**[STRONG] Topic sentences.** Every paragraph should open with a sentence that tells the reader what's coming (a "summary" sentence). Trick: draft the paragraph, then take its *last* sentence — which often already summarizes it — reword it, and move it to the front.

**[STRONG] Transitions/segues between paragraphs.** Each paragraph should end (or the next should begin) with a sentence that smoothly connects to what follows — no jarring jumps.

**[STRONG] Use signposts** to guide the reader:
- Structure/navigation: "In this section, we…", "Section 3 presents…"
- Transitions/connections: "However…", "In contrast…", "Building on this…"
- Argument signals: "This suggests that…", "A limitation is…"
- Purpose statements: "To test this, we…", "To address this gap, we…"

**[STYLE] Formatting is mechanics — do it last.** Content and ideas come first; wait to polish formatting until late in the writing process. Use the institution's or journal's template.

---

## 4. Content rules

**[HARD] Justify every choice ("Why?").** If a reader could reasonably ask "why?" of a sentence, it should be answered — method choices, model choices, parameter settings, inclusion/exclusion criteria for data. These justifications typically belong in the Introduction (or Methods, where domain-specific).

**[HARD] Research should be reproducible.** An MSc thesis has "plenty of space" (no strict page limit like a journal), so ask: *does a reader have everything needed to replicate this work?* If not, either add it or explicitly document the limitation (see AMSCUP's Alvis-HPC-gone constraint as a model case of an honestly documented, permanent reproducibility limitation).

**[HARD] Inclusion/exclusion criteria for data must be described thoroughly**, preferably:
- All criteria ("reasons") for exclusion stated explicitly
- The *amount* of data excluded per criterion stated explicitly
- If exclusion happened in steps, each step documented (a funnel/flow diagram is often appropriate)

**[HARD] Describe data and data sources completely.** A reader should know, after reading: where the data came from; who collected it; where and why it was collected (purpose-built vs. reused); whether your data is a subset of a larger dataset (and what your subset was, cross-referencing the inclusion/exclusion criteria); if human-subject data, participant recruitment, demographics (age mean/SD, gender counts), and other study-relevant covariates.

**[STRONG] Use appendices deliberately.** Move to an appendix: redundant figures that don't add new information beyond one or two representative ones; results not central to the "story"; anything included mainly for completeness/reproducibility rather than argument.

**[HARD] Literature must appear in the Discussion, not just the Introduction.** The Introduction "sets the stage"; the Discussion must relate your *results and method choices* back to existing literature. Expect some citation overlap between Introduction and Discussion, but new references are typically needed in the Discussion specifically to interpret results.

**[HARD] Limitations must be described and reflected on in the Discussion.** All research has limitations — be transparent. Include: assumptions made; study-design limitations (e.g., amount/representativeness of data); how these compare to limitations in prior work (citing similar-methodology studies strengthens credibility). A limitations section is a credibility-building device, not an admission of failure.

**[HARD] Others' work is not "THE truth."** Very little in science is definitive. Never state a finding from prior literature as unconditional fact. Use qualified language:
- "provide strong evidence for…"
- "most research shows…"
- "X et al. report…", not "X et al. proved…"

---

## 5. Citations, references, and plagiarism

**[HARD] Plagiarism is a serious, centrally reportable offense.** Copying text or ideas from any source — including your own previously published work — without proper citation is plagiarism. This applies to text, figures, and images equally.

**[HARD] You cannot include a figure or image from literature/internet without an explicit right to reuse it.**
- Many journals have online forms for permission to reuse content.
- For an MSc thesis this is often free, but an **explicit OK is still required** — do not assume implicit permission.
- Consider copyright before including *any* externally sourced figure.

**[HARD] Citation style must be chosen once and applied consistently** across the entire document (e.g., APA or IEEE-style). The "best" style is often dictated by institution/journal/supervisor — check first, then never mix styles within one document.

**[HARD] Bibliography must be complete and correctly formatted.**
- Preferably use a reference management system (e.g., Zotero via `graphify` for AMSCUP) — but **do not trust it blindly**; manually verify every entry.
- Choose one established citation format and comply with its rules exactly.
- Every reference must be checked for completeness (author, year, title, venue, etc.).

**[HARD] Direct-quote conventions**: when quoting text verbatim, use quotation marks and a precise citation (author, year, page number for APA-style). Never present a close paraphrase of someone's specific wording as if it were fully independent prose.

**Literature-review documentation discipline** (from the lit-review workbook, applicable to AMSCUP's `docs/lit_survey/`):
- For every source reviewed, record: how it was found (structured search / snowball / Google / by chance / experience / other), the exact search terms or SCOPUS query used, full bibliographic metadata, and — **mandatory** — at least a few sentences of analysis in the context of your own work. An entry with no analysis is treated as incomplete.
- Record who did the review if multiple people share the work.
- Record a relevance rating (High/Medium/Low) per relevant sub-topic; leave blank if not relevant at all — don't force a rating where none applies.
- When to write up the literature review: if unfamiliar with the field, do it early (you need to build the survey before you can write meaningfully); if already expert in the field, it can be deferred until later in the writing process.

---

## 6. Language and grammar

**[HARD] Correct tense usage** (this is treated as a hard, checkable rule, not a style preference):
- **Past tense** — what happened: what you did, what someone reported, what happened in an experiment. Most of the thesis should be past tense.
- **Present tense** — general truths: conclusions (yours or others'), atemporal facts, and statements about what the document itself does/covers ("This section describes…").
- **Future tense** — reserved almost exclusively for perspectives / future work sections (what will be done in coming months or years). Very few sentences, if any, should be future tense.

**[STRONG] Simplify wordy constructions.** Prefer the verb form:

| Instead of | Write |
|---|---|
| Make an examination of… | examine |
| Present a comparison of… | compare |
| Be in agreement… | agree |
| Perform an analysis of… | analyze |
| Produce an improvement in… | improve |

**[HARD] Terminology consistency.** Choose one term per concept for the entire document and never switch. Define/describe each term at first use — be generous ("better to describe 'too much' than too few"). If using an abbreviation/acronym, spell it out at first use *in every major section that could stand alone* (main text and the Abstract both need the first-use spellout). Watch especially for students unintentionally using multiple different terms for the same underlying concept — check this deliberately and, if working with co-authors, agree on terminology up front.

**[HARD] No colloquial/slang language.** Avoid casual spoken register (e.g., never open a sentence with "So, let's look at XYZ") and avoid common contractions ("it's", "don't").

**[STRONG] Passive vs. active voice.** Scientific convention (as taught in this seminar) strongly encourages mostly **passive voice** — minimize "we" and "I". Active voice can be included but should be limited. **Flag**: conventions differ substantially by domain and by supervisor/venue — confirm actual expectation before enforcing this as a hard rule in any specific chapter.

**[HARD] Do not overstate findings.** Avoid absolute claims. Prefer:
- "…indicate that…"
- "…can be interpreted as…"
- "…provide further evidence for…"

**[HARD] Reserve "significant/significantly/significance" for statistical meaning only.** Use "substantially" or similar for non-statistical emphasis. This is directly relevant to AMSCUP's ASF robustness-failure claims — never describe a corruption effect as "significant" unless backed by the appropriate statistical test (consistent with the project's existing Wilson-CI/bootstrap-CI discipline).

**[STRONG] Avoid weak intensifiers** ("very", "extremely") — use more specific, descriptive language instead.

**[STRONG] Resolve ambiguous referents.** Never use "this"/"that"/"it" where it's not immediately obvious what is being referred to — repeat the specific noun instead.

**[HARD] Singular/plural correctness**, checked explicitly, including for mass/uncountable nouns (information, advice, research, knowledge, etc. have no plural and cannot take "a/an").

**[STRONG] Short sentences.** If a sentence spans multiple lines, consider splitting it. Don't try to cram everything into one sentence.

**[STRONG] Hyphenation rules and consistency:**
1. Hyphen is **obligatory** for a compound noun formed of a noun + participle acting as a modifier: "garden-filled city", "cutting-edge methods" (but not when used predicatively: "His methods are cutting edge").
2. Hyphen is **strongly recommended** when a compound noun would otherwise be ambiguous: "driving-research statistics" (statistics from driving research) vs. "driving research-statistics" (a different, likely meaningless, reading).
3. Hyphen is required when a multi-word phrase functions as an adjective before a noun: "an out-of-the-box solution" (but "used out of the box").
Beyond the rules, be **internally consistent** in hyphenation choices across the whole document.

**[STRONG] Watch for dangling modifiers/participles.** A modifying phrase (often "-ing") must sit next to the noun it modifies. E.g., wrong: *"Analyzing the results, older participants were slower to react."* Right: *"Analyzing the results, we found that older participants were slower to react."*

**[STYLE] Preposition correctness** — memorize case-by-case; no shortcut rule. Flag uncertain prepositions for review.

**[STRONG] Early verb placement.** Where possible, put the main verb early in a sentence so the reader isn't kept waiting to understand the clause.

**[STYLE] Watch nominalization.** Nouns ending in "-tion" aren't inherently wrong, but excessive nominalization can obscure the actor and action — check for balance.

**Numbers and comparison words:**
- **[HARD]** Numbers zero through twelve are written out in words; 13 and above use numerals.
- **[HARD]** "Between" is used only for exactly two items; "across" for more than two.
- **[HARD]** "Several" conventionally implies three or four — not two.

**[STYLE] Variable naming.** Balance brevity and clarity — avoid opaque short names ("Var1") and avoid unwieldy long ones; aim for something like "Eyes Off-Road" / "EOF" rather than either extreme.

**[STYLE] Personal checklist.** Beyond these general rules, keep a running list of your own recurring language issues (mother-tongue interference, dialect habits, recurring errors flagged by supervisors/reviewers) and check the draft against that personal list too.

---

## 7. Figures

**[HARD] Axes must always be labelled and carry units.**

**[STRONG] Do not use titles on figures/plots** (exceptions rare — check with supervisor/venue guide).

**[STRONG] Avoid frames around figures** — design guidelines generally discourage them; simpler is better.

**[HARD] Figure text font size must be consistent across all figures and comparable to the main-text font.** Rule of thumb from the checklist: no figure text should be smaller than ~70% of the main body text size. Since exact sizing depends on final figure scaling, this typically must be checked visually after layout.

**[STYLE] Consider grayscale/colorblind-safe rendering** — noted as "not super important nowadays" but still worth a sanity check for accessibility.

**[HARD] Keep figures as simple as possible** — include only what's needed to make the point; consider alternative visualization forms if the current one is cluttered.

**[HARD] Be consistent across all figures** in color palette, line styles, marker styles, and general figure style — ideally throughout the entire document. (AMSCUP's shared reusable plotting module in `robust_testing/kradar/` should be the single source of truth for this.)

**[HARD] Copyright.** Never assume you can reuse a figure/image just because you used it before (even in your own prior publication) — an explicit right/license check is required every time.

**[STRONG] Don't repeat the figure's full content in prose.** Figures and tables should be self-contained via their captions; the surrounding text should highlight patterns/trends/important findings rather than re-describe every value.

---

## 8. Tables

**[HARD] Be internally consistent** in style, fonts, acronym use, and units across all tables.

**[HARD] Limit significant digits.** Don't over-report precision — the checklist suggests ~2–3 significant digits as a reasonable default unless the domain demands more.

**[STRONG] Keep tables as simple and concise as possible.**

**[HARD] Captions must make the table self-contained.** A reader should be able to understand the table from its caption alone, without needing to read the surrounding text. (Table captions are conventionally placed *above* the table.)

---

## 9. Data and code sharing

**[STRONG] Default toward openness where possible.** There is a strong disciplinary push to share both data and code so others can replicate and build on the work.

**[HARD] Always check with supervisors and any industry stakeholders before sharing anything.** This is a hard gate, not a courtesy — do not share data/code publicly without explicit clearance, regardless of how "obviously fine" it seems.

**[STYLE] Plan sharing format early**, not as an afterthought — if you intend to eventually share data/code (e.g., via GitHub/GitLab with a chosen license), design your data/code organization with that in mind from the start.

*Applied to AMSCUP*: this rule interacts directly with the hard project constraint that ASF training pipelines/configs/data loaders must never be modified, and that the K-Radar raw dataset lived only on the now-gone Alvis HPC with no local mirror — any sharing decision here needs explicit supervisor/stakeholder sign-off given these constraints.

---

## 10. Personal writing checklist mechanism (process, not content)

The seminar recommends keeping a literal, living checklist document (this is the origin of the source spreadsheet):
- One row per rule/topic (organization, content, citations, language, figures, tables, sharing, personal issues).
- For each item, track: importance (as judged by you and by your supervisor — high items always get checked), your comments, supervisor's comments, and dated check-in status across multiple passes (Check 1 → Check 2 → … → Final).
- High-importance items (as flagged by a supervisor) should always be checked, even late in the process; as skill improves, the number of "high importance" items should shrink over successive drafts/theses.
- A personal section at the bottom exists specifically for idiosyncratic, recurring issues (e.g., specific grammar habits tied to mother tongue) that don't fit the general checklist.

**Recommendation for AMSCUP**: maintain this as a literal tracked file in the repo (e.g., `docs/writing_checklist.md` or as a companion to `CLAUDE.md`), checked against each chapter draft before it's considered submission-ready, mirroring the two-phase gated workflow (audit → explicit approval) already used for Claude Code prompts.

---

## 11. Interaction with AMSCUP-specific hard rules

These items from the project's existing hard constraints reinforce or specialize the general rules above and should be treated as non-negotiable in any thesis draft:

- **Citation integrity is absolute** — no invented or approximated numbers; every numeric claim needs verbatim sourcing with exact field names and page/section citations. This is a stricter version of §5's citation-consistency rule and directly explains why the three verified errors in `Introduction.tex` §1.2 (nuScenes metadata overstatement, wrong 35–58% range, incorrect Waymo weather-annotation claim) must be corrected explicitly and documented as corrections, not silently patched.
- **Absence of findings requires a coverage statement**, never silence — this is the AMSCUP-specific instantiation of "reproducibility" and "why?" (§4): if a reader would expect an analysis and doesn't find one, the gap itself must be stated.
- **Never overstate exploratory/uncorrected results** (RCE sign inversion, mASE denominator error, CRI formula status) as validated findings in the thesis text — apply §4's and §6's "don't overstate findings" rule with extra force to any metric flagged as buggy/unverified.
- **Statistical rigor conventions** (dual N reporting, N≥30 floor, Wilson/bootstrap CI, low-N flagging) are the project's concrete implementation of the "significantly" rule in §6 — never let prose imply statistical significance without the corresponding CI/test being reported alongside it.

---

## Quick pre-submission checklist (condensed)

- [ ] Does every section serve the stated story/main message?
- [ ] Is every choice (method, model, parameter, inclusion/exclusion) justified?
- [ ] Are inclusion/exclusion criteria and excluded-data counts fully documented?
- [ ] Does the Discussion cite literature to interpret results (not just repeat the Introduction's citations)?
- [ ] Are limitations explicitly stated in the Discussion?
- [ ] Is every claim about prior work hedged ("indicates", "provides evidence for"), never asserted as THE truth?
- [ ] Is citation style consistent, and is the bibliography manually verified for completeness?
- [ ] Is every figure/image confirmed to have explicit reuse rights?
- [ ] Do all figures share consistent fonts, colors, and line styles at readable relative size?
- [ ] Are tables captioned so they're understandable standalone?
- [ ] Is tense usage correct (past for what was done, present for general truths, future rare)?
- [ ] Is "significant/significantly" used only in the statistical sense?
- [ ] Are terms/abbreviations defined once at first use and used consistently thereafter?
- [ ] Is data/code sharing cleared with supervisors/stakeholders before any public release?
- [ ] Has the draft been checked against your own personal recurring-error list?
