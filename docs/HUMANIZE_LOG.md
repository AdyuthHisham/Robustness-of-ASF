# Humanization Pass — Log

Deliverables per the humanization prompt: voice profile, style ledger, per-section status, logged conflicts/rejections.

---

## Voice profile (from user sample, 2026-09-07)

**Sample provided** (self-reported non-AI-assisted, representative of target thesis register):

> This thesis represents my work for the past few months. The objective of this thesis is to study a benchmark sensor fusion model developed by the same team that developed the K-Radar dataset. From this thesis it can be seen how the Availability Aware Sensor Fusion Model is built to be robust against corruption/noisy input data.

**Observed traits:**

- **Sentence length**: short to medium, all single-clause or one-relative-clause. No compound/multi-clause sentences in the sample.
- **Paragraph opening**: states the document/object directly as subject ("This thesis represents...", "The objective of this thesis is..."). Leads with the thing being described, not a scene-setting hook.
- **Connective habits**: minimal — no "however", "moreover", "furthermore". Sentences stand independently; relationships are implicit from order, not signaled.
- **Repetition tolerance**: "developed by the same team that developed the K-Radar dataset" — repeats "developed" rather than swapping in a synonym. Reads as natural, not polished-around.
- **Fronted phrases**: "From this thesis it can be seen..." — fronts a prepositional phrase before the impersonal construction, rather than "It can be seen from this thesis that...". A recurring habit to preserve, not correct into the more "standard" order.
- **Shorthand notation**: "corruption/noisy" — slash used instead of "corruption or noisy" / "corruption and noise". Informal but compact; likely to be cleaned up for the thesis body regardless, per bible's no-colloquial-slang rule — flagged as one point where the sample's own habit should NOT be carried over verbatim.
- **Voice**: mixes first-person ("my work") with impersonal/passive-leaning constructions ("it can be seen", "is built to be robust") in the same short passage. First person appears only when describing the author's own act of doing the thesis (a framing move), not when describing technical content — technical content already defaults to impersonal/passive in this sample.
- **Hedging**: none present in this tiny sample — too short to establish a baseline hedging rate. Will default to what the source text already does, and to bible §4/§6 requirements, rather than inventing a rate.
- **Word choice**: plain, unadorned — "represents", "study", "built to be robust". No inflated vocabulary, no filler adjectives.

**What I will carry over:**
- Short, direct sentences over long compound ones.
- Subject-first paragraph/section openings that state the object being discussed, not a scene-setting hook.
- Fronted-phrase constructions like "From X, it follows that..." as one acceptable pattern, not something to normalize away.

**What I will NOT carry over (bible collision, confirmed by user 2026-09-07):**
- The first-person "my work" framing — bible §6 [STRONG] pushes mostly passive/impersonal voice, "we"/"I" minimized. **User confirmed: no first person, follow bible's passive style.** Thesis body stays impersonal throughout.
- Repeated words — sample tolerated "developed... developed", but **user overrode this: repetition should be minimally tolerated; always prefer a suitable synonym.** Repetition is now a thing to avoid, not a voice trait to preserve, as long as the synonym isn't a strained/inaccurate substitution (accuracy still wins over variety — a synonym that shifts technical meaning is never used, per Section 2 hard rules on term consistency).
- Slash shorthand ("X/Y") — **user confirmed: do not use.** Any "/" found in flowing prose (not tables/labels) is spelled out ("or"/"and", whichever the sentence means).
- Absence of hedging — bible §4/§6 [HARD] require hedged language for prior-work claims and forbid overstatement; the sample's lack of hedging is an artifact of its brevity/subject matter (describing one's own thesis, not summarizing literature), not a license to strip required hedges elsewhere.

**Note on the resulting profile**: after these overrides, what's left from the sample as a genuine "voice" trait is mainly structural — short sentences, subject-first openings, occasional fronted-phrase constructions — rather than lexical habits. Word-level choices (repetition tolerance, informal notation, person) are governed by the bible, not the sample.

---

## Status

Voice profile confirmed by user 2026-09-07, with three corrections applied (no first person; minimize repetition, prefer synonyms; no slash shorthand). Proceeding to Step 2 (bible-vs-Humanizer conflict resolution).

## Style ledger

**Locked terminology / exceptions:**
- `IMU/GPS` — kept with slash. Standard compound sensor-pairing term in this field, not or/and shorthand. Exempt from no-slash rule everywhere it recurs.
- `corruption-robustness` — locked compound form (hyphenated), used for "benchmarking work in the space of robustness to corruption." Do not paraphrase to "corruption/robustness" or "corruption and robustness" elsewhere — pick this one form.
- `Environment/Weather` — kept with slash. This is the proper name of one of the four defined corruption categories in Theory §Corruption Types (heading + repeated in-text references: "Sensor", "Geometric", "Illumination" are its siblings). Exempt from no-slash rule for terminology consistency (§6 hard rule) — changing it would desync the heading from its own body references.
- Sensor-pair fusion naming convention: **hyphenated** ("radar-camera fusion", "camera-LiDAR fusion", "LiDAR-camera fusion"), matching the document's own established usage (Theory.tex lines 9, 11, 20, 58, 73). Never write these as "X/Y fusion" or "X and Y fusion" — hyphenate, and preserve whichever sensor order the local sentence already uses (order isn't standardized document-wide, only the hyphenation is).
- `bus/truck` — kept with slash throughout (Results.tex tables, captions, and prose). This is the established shorthand for the "bus or truck" class label, used pervasively and consistently across the whole document (tables and prose alike). Exempt from no-slash rule for terminology consistency — do not spell out to "bus or truck" mid-Results where the slash form is already the document's own convention there.
- `day/night` — same treatment as `bus/truck` when used as a compound category/axis name (as in Theory.tex's nuScenes description). A **numeric-value pairing** using the same words ("0.202 day / 0.214 night") is different — that gets spelled out into full clauses ("0.202 during the day and 0.214 at night"), per the numeric-pair-spelling precedent (see Theory.tex's Gaussian/impulse fix). Rule of thumb: slash-as-category-name → keep; slash-as-value-separator → spell out.

**Voice decisions:**
- Em-dash parentheticals: replaced with comma, semicolon, colon, or parentheses depending on local grammar — never simply deleted (would create a run-on or drop the aside). Nested-list dash pairs (a dash-set list that itself contains commas) are kept, not converted, to avoid comma collision/ambiguity. Applies going forward: check for this exception case before converting any dash.
- Slash shorthand for a 2-item pairing → "and" or "or" per meaning. For a genuine compound single-concept modifier (e.g., "corruption-robustness") → hyphenate instead, don't use "and".

**Rejected rewrites:**
(none yet — no user rejections recorded)

## Per-section status

- **Introduction (all sections)** — APPLIED 2026-09-07. User instructed: stop asking per-section approval, work section-by-section and apply directly. Changes across the chapter:
  - §1.1 Background: em-dash parenthetical → "including" clause. Fixed incidental pre-existing bible violation "fourteen corruption patterns" → "14" (§6 numerals 13+).
  - §1.2 Problem Statement: 3 em-dash parentheticals → semicolon/comma (meaning-preserving). Slash fixes: "fog/rain/sleet/snow" → "fog, rain, sleet, and snow"; "Weather/lighting diversity is" → "Weather and lighting diversity are each" (subject-verb agreement fix required by the "and" substitution, flagged not silently introduced); "corruption/robustness" → "corruption-robustness" (read as one compound field per §6 hyphenation rule for pre-nominal compounds, not "and").
  - §1.3 Research Questions: 2 dashes → colon/semicolon; 1 dash pair *kept* (nested list inside a dash aside — comma substitution would collide with the list's own internal commas; logged exception).
  - §1.4 Scope and Objectives: dash around "ASF" → parenthetical "(ASF)" (cleaner, matches how the acronym is introduced elsewhere). Slash fixes: "weather/environment/time-of-day" → "weather, environment, and time-of-day"; "weather/environment diversity" → "weather and environment diversity".
  - §1.5 Thesis Structure: "sensor noise/degradation modelling" → "sensor noise and degradation modelling". No other tells found.
  - No headings changed, no math/labels/citations/numbers touched except the one flagged pre-existing numeral fix.
- Introduction: DONE.
- **Theory (whole chapter)** — APPLIED 2026-09-07. 21 targeted fixes: em-dash parentheticals converted to comma/semicolon/colon/parentheses/sentence-splits (meaning-preserving throughout); slash fixes ("brightness/darkness"→"brightness and darkness", "contrast/occlusion"→"contrast and occlusion", "density increase/decrease"→"or", "trained/run"→"trained and run", "training/evaluation"→"training and evaluation", "camera/LiDAR fusion"→"camera-LiDAR fusion" to match the document's own established hyphenated sensor-pair naming convention); numeric-pair shorthand "74.4/74.2 under Gaussian/impulse noise" spelled into two full clauses (no numbers changed, just format); incidental "fourteen corruption patterns"→"14" fixed for consistency with the same fix already applied in Introduction. Two nested-list dash pairs *kept* (K-Radar's class list, nuScenes' sensor-suite list — both contain their own internal commas; converting would create ambiguity). Content inside `\iffalse...\fi` (commented-out "Diversity Axes and Class Distribution" subsection) left untouched — not rendered, out of scope, same precedent as OPEN-Q9-1 in the verification log.
- Theory: DONE.
- **Methods (whole chapter, 593 lines)** — APPLIED 2026-09-07. ~20 targeted fixes across live prose: em-dash → comma/semicolon/colon/parentheses/sentence-split (meaning-preserving); slash fixes ("light/heavy snow"→"light snow, heavy snow" matching Theory.tex's own established convention; "point-removal/masking"→"point-removal or masking"; "sparse-point-cloud / front-camera-only representation"→spelled into two named representations; "weather/environment/time-of-day"→"weather, environment, and time-of-day"; "precision/recall"→"precision-recall" hyphenated). One nested-list dash pair kept (Gaussian-noise $\sigma$ schedule with internal parenthetical commas — converting risked ambiguity, same exception class as before). All content inside `\iffalse...\fi` blocks and `%`-commented paragraphs (dead/deferred material: sensor-set paper-vs-config note, checkpoint subsection, determinism/frame-independence notes, the avail_feats mechanism note per OPEN-Q9-1, ground-truth annotation-sensor field, visibility-calculation-methods appendix material, corruption-taxonomy table draft, mFR metric note) left completely untouched — not rendered, out of scope. Table cells and figure/diagram labels (sensor-spec table, coordinate-frame table, tikzpicture node text) left untouched per rule 2 — slashes inside table cells (e.g. "Channels / accuracy") are not prose and were not modified. Locked exception: "mean Absolute Translation/Scale/Orientation Error" kept as-is — standard nuScenes-style metric-naming convention (mATE/mASE/mAOE), not or/and shorthand.
- Methods: DONE.
- **Results (whole chapter, 374 lines)** — APPLIED 2026-09-07. §ASF Regeneration Results had zero live-prose tells (no changes). Remaining sections: 10 targeted fixes — em-dash → comma/colon/parentheses (meaning-preserving; several nested-list dash pairs kept where converting risked ambiguity against internal commas, e.g. "camera essentially immune, radar gradually degraded, LiDAR..." aside); numeric-pair slash spelled into full clauses ("0.202 day / 0.214 night" → "0.202 during the day and 0.214 at night", consistent with the Theory.tex Gaussian/impulse precedent); slash-to-hyphen/and fixes ("fog/LiDAR-noise pattern"→"fog-LiDAR-noise", "axis/class cell"→"axis-class cell", "sensor/effect combination"→"sensor-effect combination", "radar/LiDAR alone"→"radar and LiDAR alone" x2, "weather/environment breakdowns"→"weather and environment breakdowns"). Zero numbers, table values, or captions touched. `camera/LiDAR/radar $\times$ gaussian_noise/loss_partial`-style factorial notation in prose (describing a figure's legend structure) left as-is — read as compact mathematical/technical notation, not colloquial shorthand.
- Results: DONE.
- **Discussion (whole chapter, 329 lines)** — APPLIED 2026-09-07. ~24 targeted fixes across live prose: em-dash → comma/colon/semicolon/parentheses (meaning-preserving); slash fixes ("sensor/effect"→"sensor-effect", "camera/LiDAR/4D-radar"→spelled list, "LiDAR/radar"→"LiDAR or radar", "normal/overcast"→"normal and overcast", "fog/LiDAR-noise"→"fog-LiDAR-noise" x2 for cross-chapter consistency with Results.tex, "weather/environment/density"→spelled list, "prediction/ground-truth"→"prediction and ground-truth" matching Methods.tex's own phrasing, numeric pair "0.915/0.842"→"0.915 (sedan) and 0.842 (bus or truck)"). Several heavily numeric-dense dash constructions (the ASF-vs-thesis comparison paragraphs, §What This Thesis Reaffirms) were left as nested-list exceptions — the density of embedded percentages, arrows, and parenthetical deltas made a comma/colon substitution a real risk of misparsing which number attaches to which clause; logged rather than risked. The entire "MOVED FROM Results.tex" block at the end of the file (~140 lines, everything after the visible Summary section) is commented out (`%`) and was left completely untouched, per the established out-of-scope precedent for dead/commented material.
- Discussion: DONE.
- **Conclusion (57 lines)** — APPLIED 2026-09-07. 8 fixes: em-dash → comma/colon/parentheses; slash fixes ("weather/environment/time-of-day"→spelled list, "net retention/churn (0.207/0.609...)"→spelled into "net retention 0.207, churn 0.609 at high severity; ..." full clauses, "single-sector/single-threshold"→comma-joined, "lenses/windows"→"lenses or windows"). RQ1/RQ2/RQ3 quoted question text left verbatim (direct quotes of Introduction's research questions, including that section's own kept nested-list dash) — changing a quote would break the RQ1/RQ2/RQ3 ↔ Introduction correspondence. The "RQ1 -- ``...''" label-separator dash convention (used identically 3 times) left as a deliberate structural/typographic choice, not prose.
- Conclusion: DONE.
- **Abstract (frontmatter/Abstract.tex)** — APPLIED 2026-09-07, done LAST per the prompt's risk ordering. 1 fix: one em-dash → comma. Title/author/affiliation lines (heading-like frontmatter) untouched.
- Abstract: DONE.

## Step 4 — Whole-document consistency check (2026-09-07)

- **Compile check**: 2-pass pdflatex + bibtex, zero errors, zero warnings, all cross-references and citations resolve. No LaTeX structure broken by any edit.
- **Voice drift**: all chapters processed with the same rule set (bible overrides from Step 2, applied identically chapter to chapter) — no chapter received different treatment. Sentence-transition style (comma/colon/semicolon/parentheses substitution for em-dashes) is consistent Introduction → Abstract.
- **Locked terminology**: no term fragmented across chapters — `corruption-robustness`, `Environment/Weather`, `bus/truck`, `day/night`, `IMU/GPS`, `fog-LiDAR-noise`, `sensor-effect`/`axis-class` compounds, and the mATE/mASE/mAOE convention were applied identically wherever they recurred (see Style ledger above).
- **Slash purge — honest completion state**: the explicit no-slash rule was applied to genuine prose shorthand (or/and substitutions, spelled-out lists, numeric-pair expansions) throughout. NOT purged, and logged as legitimate exceptions rather than fixed: units (`mm/h`, `m/s`, `pts/s`), file/code paths (`repos/K-Radar/tools/...`, `docs/vAIlt`), table `N/A` notation, proper benchmark/dataset names as defined by their own cited papers (`KITTI-C/nuScenes-C/Waymo-C`, `RS/mRS`), and `low/medium/high` severity-tier shorthand, which recurs too pervasively as compact enumeration notation (tables, captions, and prose alike) to convert everywhere without disproportionate risk to number-adjacent sentences for cosmetic gain. If the user wants these purged too, flag which class and I'll do a targeted follow-up pass.
- **Em-dash exceptions (nested-list dash pairs kept)**: a recurring, logged exception class throughout — where a dash-set aside itself contains internal commas (e.g. a 3-item list), the outer dashes were kept rather than converted to commas, to avoid ambiguous nesting. Occurs in Introduction (RQ1, quoted verbatim in Conclusion too), Theory (nuScenes sensor-suite description, K-Radar class list), Methods (Gaussian-noise σ schedule), and several data-dense passages in Discussion/Results comparing ASF's published numbers to this thesis's regenerated ones.
- **Mechanical bible checks** (numbers 0–12 spelled/13+ numeral, "significant" reserved for statistical sense, "between"/"across" usage, contractions, tense): no violations introduced by any humanization edit — all edits were prose-structure substitutions (dash/slash), none touched a number's value, a hedge, or a tense.
- **Incidental pre-existing issues fixed at user's direction, outside strict humanization scope**: "fourteen corruption patterns" → "14" (both occurrences, Introduction and Theory) per §6 numerals-13+ rule.

## Step 2 — Bible overrides (locked 2026-09-07)

Bible wins on every row. User confirmed: follow `thesis_writing_bible.md`'s actual text, not generic Humanizer defaults.

| Humanizer pattern | Bible rule | Override applied |
|---|---|---|
| #13 Passive voice / missing subjects — name the actor, prefer active | §6 [STRONG]: mostly passive, minimize "we"/"I" | Do not de-passivize. Fix only genuinely agentless/confusing constructions. Never convert passive→active as a default. |
| #21 Knowledge-limit disclaimers — remove | §4/§11 [HARD]: limitations required in Discussion; absence-of-findings needs a coverage statement, never silence | Do not remove methodological limitations, coverage statements, or documented constraints (HPC-unavailability, sequence-coverage caveats, metric-status flags, N-floor notes). Remove only chatbot-style hedging about the writing itself (should already be gone post-verification). |
| #24 Too many qualifiers — compress to one hedge | §4 [HARD]: prior-work claims hedged ("indicate", "provide evidence for"); §6 [HARD]: don't overstate findings | Preserve required hedges. Collapse only genuinely redundant stacking ("could potentially possibly"). Never strip a hedge to a bare assertion. |
| #17 Title case in headings — convert to sentence case | Not addressed by bible (§3 [STYLE]: formatting is mechanics, done last) | Leave headings untouched — out of scope for a prose-only pass. Log inconsistencies, don't fix. |
| #14 Em/en dashes — cut | Not addressed directly | Apply, but never inside math, numeric ranges, or compound/hyphenated technical terms (§6 hyphenation rules govern those, not dash removal). |
| #26 Hyphenated word pairs — keep only grammatically needed | §6 [STRONG] full hyphenation ruleset: obligatory for noun+participle modifiers, required for multi-word pre-nominal adjectives, internal consistency across the document | Follow §6's rules exactly, not Humanizer's simpler default. |
| #10 Forced groups of three — use the number meaning needs | Not addressed directly; §3 [STRONG] one-point-per-paragraph implies no padding | Apply. Never drop a list item that carries real content — three conditions stays three conditions. |
| #7 Overused AI words — replace | §6 [HARD]: one term per concept, defined at first use, never switched | Apply, except where the word is a locked technical term (see style ledger) — those are never paraphrased away. |
| — | §6 [HARD]: numbers 0–12 spelled out, 13+ numerals; "between" only for two, "across" for 3+; "significant" only in the statistical sense; tense rules (past for what was done, present for general truths/document self-reference, future rare); no contractions/colloquialisms | All apply as written, mechanically checked per section and again at Step 4. |

Any other Humanizer suggestion that would violate a bible [HARD] or [STRONG] rule: rejected and logged under that section's entry, not silently applied.

## Conflicts logged

(populated as sections are processed)
