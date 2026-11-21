# AMSCUP Deep Audit + Restructure Prompt

Paste this whole file as a prompt to Claude Code in the AMSCUP repo root.

---

## What you are doing

Two things, kept as two separate deliverables:

1. **Findings log** — an append-only, evidence-only record of bugs, broken invariants,
   and documentation/code mismatches ("false information" in docs/vault/report vs.
   what the code actually does).
2. **Restructure document** — proposals for how the repo should be organized, based
   on what chunk 1 finds. No file moves, no edits to code or docs. Proposals only.

Nothing in this repo gets modified, moved, or deleted as part of this task. Read-only
investigation. No destructive git commands.

## Ground truth (read this before finding "bugs")

Read `/home/adhish/Productivity/AMSCUP/CLAUDE.md` in full first. Key facts already
established — do not re-report these as findings:

- This is a monorepo of loosely-coupled parts. There is **no single top-level
  build/test/lint command** by design. Do not flag this as a fault.
- `repos/K-Radar`, `repos/AMSCUP_PLUS`, `docs/Latex_Report` are **git submodules**.
  `repos/AI-MSF-Benchmark` is **vendored**. You may document their interface with
  the rest of the repo (what calls into them, what data they produce/consume) but
  you may **never** propose restructuring their internals — that's a separate repo.
- `docs/vAIlt/` and `obsidianVault/` are two deliberately separate vaults (project
  docs vs. personal research knowledge base). This split is a settled decision —
  do not propose merging them.
- Alvis (the HPC cluster this project used) is **permanently gone** as of
  2026-09-01. `repos/AMSCUP_PLUS` (Slurm job scripts) is now dead infrastructure.
  This is a legitimate *restructure* observation (candidate for archiving), not a
  bug.
- The actively-developed piece is `test-bed/src/Modules/robust_testing/kradar/`
  (`kradar_visibility`) — its own `pyproject.toml`/`uv.lock`/git repo nested inside
  `test-bed/`, with its own `AGENTS.md` and `architecture.md`. Read both before
  auditing it.
- Known, already-tracked issues (don't rediscover these as new findings, but you
  may cite them if you find something adjacent): the 2026-08-26 frame-identifier
  bug (fixed), the row_table_iou03 camera_frame_deletion gap (expected, tracked),
  mFR excluded from the metrics stack by user decision.
- The working tree currently has real uncommitted state: `docs/delete_/`,
  `backups/`, `alvis_archive_2026-08-28/`, and several modified tracked files.
  Treat these as probable intentional in-progress user state, not garbage to flag
  for deletion — you may note them in the restructure doc as "needs a decision"
  items, not as bugs.

## Anti-confabulation rule (hard constraint)

Every entry in the findings log must have:
- `file:line` (or file + clear location if line numbers don't apply, e.g. a vault doc)
- the actual mechanism — quote or closely paraphrase the real code/text, don't summarize from memory
- either a **repro** (a command or a concrete input) or a **failure scenario**
  (specific inputs/state → specific wrong output/crash/contradiction)

If you cannot produce that, the item does not go in the findings log. It goes in a
separate `## Unverified / Suspicion` section, clearly labeled, with a one-line
reason it's flagged but unconfirmed. Never invent APIs, function names, benchmark
numbers, or paper citations to support a finding. If you're not sure whether
something exists, grep for it before claiming it does or doesn't.

## Graphify

Check if `graphify-out/graph.json` exists (it does, as of this writing). Use
`graphify query`, `graphify path`, and `graphify explain` to navigate
`test-bed/src/Modules/robust_testing/kradar/` — this is the highest-value place
to spend graph queries. Don't bother graphing submodules/vendored code; treat
those as black boxes with a known interface.

## The two reviewers

Spawn two subagents, run **in parallel per chunk**, each reading this whole file
plus `MASTER_AUDIT.md` (below) before starting. They split by lens, not by
personality — keep their tone matter-of-fact, adversarial in *effort* only:

- **Reviewer A — Correctness & data integrity.** Assume every number this
  pipeline has ever produced could be wrong until proven otherwise. Focus on:
  visibility scoring math (`radar_visibility.py`, `lidar_visibility.py`,
  `camera_visibility.py`), corruption injection scripts, metrics computation,
  `config.OUTPUT_SCHEMA` drift between what's declared and what's written,
  missing-sensor degradation (must produce `visible=False, score=0.0`, never
  raise — verify every code path that touches this actually does that), and
  whether `SMK-*`/`VER-*` test IDs actually assert what their docstrings and the
  spec docs claim they assert.

- **Reviewer B — Claims integrity.** Assume every doc is lying about the code
  until proven otherwise. Cross-check `architecture.md`, `AGENTS.md`,
  `docs/vAIlt/*`, `obsidianVault/Projects/K-Radar/*`, and any report/results
  claims (including `docs/Latex_Report` at the interface level — cite specific
  numeric or methodological claims, don't rewrite the submodule) against current
  code and current output files. Enumerate every doc that cites a number, schema,
  or behavior that doesn't match what's on disk right now — memory already flags
  two vault docs citing stale post-camgauss-fix numbers; find the rest
  systematically rather than trusting that those are the only two.

Each subagent works one chunk at a time (see chunk list), appends findings to
`MASTER_AUDIT.md`, updates that chunk's status row, and stops — you (the
orchestrator) launch the next chunk. Do not let either subagent process more
than one chunk per invocation; this is a deliberate pacing constraint to avoid
context overload, not a suggestion.

## Chunks (process in this order, one subagent-pair invocation per chunk)

1. `kradar_visibility` core modules — `config.py`, `parser.py`, `calibration.py`,
   `data_loader.py`, `radar_visibility.py`, `lidar_visibility.py`,
   `camera_visibility.py`, `pipeline.py`
2. `kradar_visibility` tests — `tests/test_smoke.py`, `tests/test_verify.py`, and
   any other test files; check assertions against docstring test IDs and against
   the spec docs those IDs map to
3. Corruption / sweep / analysis scripts — everything under
   `test-bed/src/Modules/robust_testing/kradar/scripts/` (or wherever the
   corruption injection and sweep-runner code lives — locate via graphify first)
4. Outer `test-bed/` — anything outside the `kradar/` subproject:
   `test-bed/src/Modules/robust_testing/{nuscenes,example}/`, `main.py`, root
   `pyproject.toml`/lockfile consistency
5. `docs/vAIlt/` claims vs. code/output reality (Reviewer B leads; Reviewer A
   spot-checks any numeric claim Reviewer B flags)
6. `obsidianVault/Knowledge/` and `obsidianVault/Projects/K-Radar/` claims vs.
   code/output reality (same split as chunk 5)
7. Submodule/vendored interfaces + dead infra — how `repos/K-Radar`,
   `repos/AMSCUP_PLUS`, `repos/AI-MSF-Benchmark` are actually called into from
   `test-bed/`, and what's now dead weight given Alvis is gone

## MASTER_AUDIT.md

Before spawning any subagent, create `.agents/MASTER_AUDIT.md` with this structure
and keep it updated (both subagents read it before their chunk and append after):

```markdown
# AMSCUP Audit — Master Doc

## Scope & boundaries
(copy the "Ground truth" and "Anti-confabulation rule" sections above verbatim)

## Chunk status
| # | Chunk | Reviewer A | Reviewer B | Status |
|---|-------|-----------|-----------|--------|
| 1 | kradar_visibility core | pending | pending | not started |
| 2 | kradar_visibility tests | pending | pending | not started |
| 3 | corruption/sweep/analysis scripts | pending | pending | not started |
| 4 | outer test-bed | pending | pending | not started |
| 5 | docs/vAIlt claims | pending | pending | not started |
| 6 | obsidianVault claims | pending | pending | not started |
| 7 | submodule interfaces + dead infra | pending | pending | not started |

## Finding schema
Each finding:
- id (e.g. A-1-03 = Reviewer A, chunk 1, finding 3)
- file:line
- claim/mechanism (quoted or closely paraphrased)
- failure scenario or repro
- severity (blocks correctness / silent wrong output / doc-drift / cosmetic)

## Findings log (append-only)
(findings go here, grouped by chunk)

## Unverified / Suspicion
(anything that didn't clear the evidence bar)
```

## Final restructure document

Only after all 7 chunks are marked done in `MASTER_AUDIT.md`: write
`.agents/RESTRUCTURE_PROPOSAL.md`. This is proposals, not a findings recap —
reference finding IDs from `MASTER_AUDIT.md` where a proposal is motivated by one,
but the restructure doc's job is "here's how the repo should be organized going
forward," not "here's what's broken." Include a section for the
uncommitted-working-tree items (`docs/delete_/`, `backups/`, `alvis_archive_*`,
etc.) as explicit decisions needed from the user, not recommendations.
