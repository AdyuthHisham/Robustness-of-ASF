---
title: Hermes Multi-Agent Workplan
type: literature
source: home/adhish/Downloads/hermes_multiagent_workplan.md
date: 2026-07-02
tags: [05 Implementation]
---
# Hermes Multi-Agent Workplan

## Overview

This workplan configures the five-agent system defined in `all_agents.md` inside the Hermes framework. It addresses all four known failure modes: `pip` use, unreliable filesystem navigation, silent error stopping, and unverified action claims.

---

## 1. System Architecture Design

### Profile Layout

Each agent runs as a distinct **Hermes profile** (`~/.hermes/profiles/<name>/`). The Kanban board (`~/.hermes/kanban.db`) is shared across all profiles and is the sole coordination surface between agents. No agent talks to another directly — all handoffs go through the board.

```
~/.hermes/
├── kanban.db                   # shared coordination surface
├── profiles/
│   ├── steward/
│   │   ├── SOUL.md             # Steward personality + rules
│   │   └── memories/
│   ├── architect/
│   │   ├── SOUL.md
│   │   └── memories/
│   ├── builder/
│   │   ├── SOUL.md
│   │   └── memories/
│   ├── verifier/
│   │   ├── SOUL.md
│   │   └── memories/
│   └── qa/
│       ├── SOUL.md
│       └── memories/
└── memories/                   # global fallback (not used)
```

### Project-level Context Files

At the root of the codebase (`/path/to/project/`):

```
project/
├── AGENTS.md          # injected into every agent session automatically
├── all_agents.md      # canonical role spec, referenced by AGENTS.md
├── .hermes.md         # project-level Hermes config (toolsets, constraints)
└── docs/
    ├── architecture.md
    ├── api_contracts.md
    ├── data_model.md
    ├── roadmap.md
    └── decisions/     # ADRs
```

`AGENTS.md` must `@include` or summarise `all_agents.md` so every agent gets role boundaries in every session.

### Delegation vs. Kanban

| Mechanism | When to use |
|---|---|
| `delegate_task` | Steward spawning Architect for design review of a single ticket; Builder spawning a parallel linting sub-task |
| Kanban board | All inter-agent handoffs (the primary coordination path) |

Kanban is the **durable** path. `delegate_task` is for **ephemeral, bounded sub-work** that belongs inside one agent's turn.

---

## 2. Agent Mapping

### Agent 1 — Project Steward

**Hermes profile:** `steward`

**Toolsets:** `file`, `web`, `kanban`, `memory`

**SOUL.md rules (excerpt):**
```
You are the Project Steward. You own project scope and documentation.
You never write application code.
Only you may approve new features, new dependencies, or architectural changes.
After every planning session, update roadmap.md and post a Kanban task.
```

**Memory (MEMORY.md):** Current sprint goal, active dependencies under review, last ADR number issued.

**Responsibilities:**
- Breaks incoming work into Kanban tasks in `Backlog`
- Assigns tasks to Architect or Builder lanes
- Owns `docs/`, `README.md`, `AGENTS.md`, `roadmap.md`
- Issues Architecture Decision Records for any scope change

**Boundaries:** Cannot touch `src/`, cannot run tests, cannot approve its own scope changes.

**Escalation rule:** If a Builder or QA task has been in `Blocked` for more than one cycle, Steward re-scopes it and re-queues.

---

### Agent 2 — Architect

**Hermes profile:** `architect`

**Toolsets:** `file`, `kanban`, `memory`

**SOUL.md rules (excerpt):**
```
You are the Architect. You own technical design and consistency.
You never implement features directly.
Every plan you produce must update architecture.md and api_contracts.md before moving the task to Builder.
Reject any Builder output that violates documented module boundaries.
```

**Memory (MEMORY.md):** Module dependency graph summary, current API contract version, known design violations logged.

**Responsibilities:**
- Reviews Kanban tasks in `Design Review` column
- Produces or updates `architecture.md`, `api_contracts.md`, `data_model.md`
- Delegates point design questions to sub-agents via `delegate_task` with `toolsets: ["file", "web"]`
- Moves approved tasks to `Ready for Build`

**Boundaries:** Cannot merge or deploy; cannot approve its own designs without Steward sign-off on scope.

---

### Agent 3 — Builder

**Hermes profile:** `builder`

**Toolsets:** `terminal`, `file`, `kanban`

**SOUL.md rules (excerpt):**
```
You are the Builder. You implement approved designs only.
NEVER use pip. ALWAYS use `uv` for all Python package operations.
Resolve your working directory with `pwd` before any file operation.
Use absolute paths constructed from `pwd` output.
Never declare a task complete until you have run ruff, black, mypy, and pre-commit.
If any tool fails, fix the error and retry — do not stop.
```

**Memory (MEMORY.md):** Project root path (confirmed via `pwd`), `uv` venv location, last pre-commit run result.

**Responsibilities:**
- Picks up tasks from `Ready for Build`
- Confirms working directory with `pwd` before every file operation
- Runs validation suite before moving any task forward:
  ```bash
  uv run ruff check .
  uv run black .
  uv run mypy .
  uv run pre-commit run --all-files
  ```
- Moves completed tasks to `Verification`

**Hard constraint on `uv`:** Builder's SOUL.md must include a negative example:
```
BAD:  pip install polars
GOOD: uv add polars
BAD:  pip install -r requirements.txt
GOOD: uv sync
```

**Failure recovery:** On tool error, Builder retries up to 3 times with strategy change (e.g., widen import, fix type annotation). On third failure it moves the task to `Blocked` with a failure note and notifies via Kanban comment.

---

### Agent 4 — Verification & Security

**Hermes profile:** `verifier`

**Toolsets:** `terminal`, `file`, `kanban`

**SOUL.md rules (excerpt):**
```
You are the Verifier. You trust evidence, not agent statements.
For every Builder claim, verify it with shell commands before accepting it.
Never move a task to Verified without running the checks yourself.
Scan for secrets on every verification cycle.
```

**Memory (MEMORY.md):** Hallucination count for current sprint, list of patterns that previously produced false-positive completions.

**Verification protocol for every task:**

| Builder claim | Verifier check |
|---|---|
| "Created `auth.py`" | `ls -la src/auth.py && wc -l src/auth.py` |
| "Tests passed" | `uv run pytest --tb=short 2>&1` |
| "Dependency added" | `uv tree \| grep <package>` |
| "Pre-commit passed" | `uv run pre-commit run --all-files 2>&1` |
| "No secrets" | `git secrets --scan` or `trufflehog filesystem .` |

**Output:** Writes a `verification_report_<task_id>.md` to `docs/verification/`. Moves task to `QA` on pass, back to `In Progress` on fail with a `kanban_comment` describing the discrepancy.

**Boundaries:** Never modifies application code. If it must run a fix (e.g., `git rm` a committed secret), it logs the action in the ADR trail.

---

### Agent 5 — Quality Assurance

**Hermes profile:** `qa`

**Toolsets:** `terminal`, `file`, `kanban`

**SOUL.md rules (excerpt):**
```
You are QA. Assume the implementation is wrong until you have evidence otherwise.
Attempt to break every public interface.
Do not move a task to Done unless your adversarial test suite passes.
```

**Memory (MEMORY.md):** Current test coverage %, known fragile subsystems, fuzz patterns that have historically found bugs.

**Responsibilities:**
- Picks tasks from `QA`
- Writes and executes: unit tests, integration tests, regression tests, edge-case fuzz probes
- Adversarial checklist for every feature:
  - Empty / null inputs
  - Boundary values
  - Invalid types / schemas
  - Concurrent access
  - Very large payloads
  - Unicode / encoding edge cases
- Produces `qa_report_<task_id>.md` in `docs/qa/`
- On pass: moves task to `Done`
- On fail: moves task back to `In Progress` with bug report attached as Kanban comment, triggering Builder → Verifier → QA loop

---

## 3. Execution Workflow

### Phase 1 — Planning (Steward + Architect)

```
/goal Plan and break down the next milestone into Kanban tasks

Steward:
  1. Reads roadmap.md and current board state
  2. Creates tasks in Backlog with description, acceptance criteria, and dependencies
  3. Tags tasks: [needs-design] or [ready-for-build]

For [needs-design] tasks → Steward posts to Kanban, Architect picks up:
  Architect:
    1. Reads task + architecture.md
    2. Produces implementation plan
    3. Updates architecture.md / api_contracts.md
    4. Moves task to Ready for Build with plan attached as comment
```

### Phase 2 — Implementation (Builder)

```
Builder polls Ready for Build:
  1. pwd → confirm absolute project root
  2. Read Architect's plan from Kanban comment
  3. Implement
  4. uv run ruff check . && uv run black . && uv run mypy . && uv run pre-commit run --all-files
  5. On all-pass → move task to Verification
  6. On fail → fix and retry (max 3); on 3rd fail → Blocked + comment
```

### Phase 3 — Verification (Verifier)

```
Verifier polls Verification:
  1. Run all checks from verification protocol table above
  2. Scan for secrets
  3. Write verification_report_<task_id>.md
  4. Pass → move to QA
  5. Fail → move to In Progress with failure evidence in comment
```

### Phase 4 — Testing (QA)

```
QA polls QA column:
  1. Run existing test suite
  2. Write adversarial tests for new surface area
  3. Execute fuzz probes
  4. Write qa_report_<task_id>.md
  5. Pass → move to Done
  6. Fail → move to In Progress with bug report
```

### Failure Loop

```
In Progress → (Builder) → Verification → (Verifier) → QA → (QA) → Done
                   ↑                          |               |
                   └──────────────────────────┘               |
                   ↑                                           |
                   └───────────────────────────────────────────┘
```

Steward monitors `Blocked` and `In Progress` cycle counts. If a task exceeds 5 round-trips it is escalated: Steward and Architect re-design the sub-task from scratch.

---

## 4. Hard Constraints

These are enforced via SOUL.md for the Builder profile and checked by the Verifier.

**`uv` only — never `pip`:**
```bash
# Builder must use exclusively:
uv add <package>        # add dependency
uv remove <package>     # remove dependency
uv sync                 # install from lockfile
uv run <command>        # run in venv
uv tree                 # inspect dependency tree
```

The Verifier checks `pyproject.toml` and `uv.lock` after every build. If either is missing or a `pip` invocation appears in shell history, the task fails verification.

**Filesystem navigation:**
Builder's SOUL.md mandates:
```
Before any file operation:
  1. Run `pwd` and store the absolute path
  2. Construct all paths from that absolute root
  3. Never use relative `../` chains to cross module boundaries
  4. Confirm file existence with `ls -la <path>` before reading or editing
```

**No silent stopping:**
Builder's SOUL.md:
```
If a command fails:
  - Log the error
  - Attempt a recovery strategy
  - Retry up to 3 times
  - Only after 3 failures: move task to Blocked and write the failure trace as a Kanban comment
  - Never exit silently
```

**No assumed success:**
Verifier's SOUL.md:
```
A task is not verified because Builder said so.
A task is verified because you ran the check and read the output yourself.
```

---

## 5. Memory & State Design

### Per-agent MEMORY.md (short-term, ~800 tokens)

| Agent | MEMORY.md contents |
|---|---|
| Steward | Active sprint goal, scope decisions, last ADR # |
| Architect | Module boundary summary, current API version, active design patterns |
| Builder | Absolute project root, uv venv path, last validation run result |
| Verifier | Hallucination count this sprint, known false-positive patterns |
| QA | Coverage %, fragile subsystems, effective fuzz payloads |

### Context Files (project-scoped, unlimited)

| File | Owner | Purpose |
|---|---|---|
| `AGENTS.md` | Steward | Role summaries, injected into every session automatically |
| `all_agents.md` | Steward | Canonical full role spec, referenced by AGENTS.md |
| `.hermes.md` | Steward | Project toolsets, model config, default constraints |
| `docs/architecture.md` | Architect | Live system design |
| `docs/api_contracts.md` | Architect | Interface specs |
| `docs/roadmap.md` | Steward | Milestones and priorities |
| `docs/decisions/` | Steward/Architect | ADR trail |
| `docs/verification/` | Verifier | Per-task verification reports |
| `docs/qa/` | QA | Per-task QA reports |

### Long-term vs. short-term

- **Short-term:** In-session Kanban comments and task descriptions. Ephemeral `delegate_task` sub-agent context.
- **Medium-term:** MEMORY.md per profile. Updated each session by the agent via the `memory` tool.
- **Long-term:** `docs/` tree, `AGENTS.md`, `architecture.md`. These survive across all sessions and are the ground truth for the project.

---

## 6. Verification System Design

### Preventing Hallucinated Actions

The core principle: **every claim requires a shell command whose output is quoted in the task comment.**

Builder must post evidence like:
```
Implemented sensor_loader.py.
Evidence:
  $ ls -la src/kradar/sensor_loader.py
  -rw-r--r-- 1 adhish users 4823 Jun 22 11:04 src/kradar/sensor_loader.py
  $ wc -l src/kradar/sensor_loader.py
  142 src/kradar/sensor_loader.py
```

Verifier then reproduces those exact commands independently. If output differs, the task goes back.

### How QA and Verifier Differ

| Dimension | Verifier | QA |
|---|---|---|
| Question | "Did it happen?" | "Does it work?" |
| Tools | `ls`, `cat`, `pytest`, secret scanners | `pytest`, custom harnesses, fuzz tools |
| Produces | Verification report (truth audit) | QA report (quality audit) |
| Failure output | "File does not exist / tests failed" | "Edge case X causes crash / coverage < 80%" |
| Code changes | Never | Writes test files |

### `/goal` for Verification Loop

The Verifier can use `/goal` to keep running until all Verification-column tasks are processed:

```
/goal Verify all tasks currently in the Verification column and move each to QA or back to In Progress with evidence. Do not stop until the Verification column is empty.
```

---

## 7. Kanban Workflow Design

### Columns

```
Backlog → Design Review → Ready for Build → In Progress → Verification → QA → Done
                                                  ↑                           |
                                              Blocked ←──────────────────────┘ (on failure)
```

| Column | Owner | Entry condition | Exit condition |
|---|---|---|---|
| `Backlog` | Steward | Task created | Steward assigns it |
| `Design Review` | Architect | Needs design work | Architect approves, posts plan |
| `Ready for Build` | Builder | Design approved | Builder picks it up |
| `In Progress` | Builder | Builder started | Validation suite passes |
| `Verification` | Verifier | Builder posted evidence | Verifier independently confirms |
| `QA` | QA | Verifier confirmed | QA test suite passes |
| `Done` | QA | All tests pass | — |
| `Blocked` | Any | 3 consecutive failures | Steward re-scopes and re-queues |

### Task Card Schema

Every Kanban task must include:

```markdown
## Task: <title>

**Assigned to:** builder | verifier | qa | architect | steward
**Acceptance criteria:**
- [ ] <concrete, testable criterion>
**Dependencies:** <task IDs>
**Constraints:** uv only; absolute paths; no silent failures
```

### Blocker Handling

If Builder calls `kanban_block`:
1. Verifier is notified (via board poll)
2. Verifier reads the failure trace in the comment
3. If it's a design issue, Verifier re-routes to `Design Review`
4. If it's an environment issue, Steward reviews
5. After re-scoping, Steward calls `kanban_unblock` and moves to `Ready for Build`

---

## 8. AGENTS.md Template

This file is auto-injected into every Hermes session in the project directory.

```markdown
# AGENTS.md — Project Agent Roles

This project uses a five-agent system. See all_agents.md for full spec.

## Hard rules (ALL agents)
- NEVER use pip. ALWAYS use uv.
- NEVER assume a file exists. Run `ls -la <path>` first.
- NEVER declare a task complete without running validation.
- NEVER stop on an error. Log it, retry, or escalate to Blocked.

## Role boundaries
- Steward: docs, scope, roadmap. Cannot touch src/.
- Architect: design docs, api contracts. Cannot merge code.
- Builder: src/ only. Cannot approve scope or design changes.
- Verifier: reads everything, writes nothing except reports in docs/verification/.
- QA: writes tests, reads src/, writes nothing except tests and docs/qa/.

## Coordination
- All handoffs go through the Kanban board.
- Post evidence (shell output) in task comments before moving any task forward.
- See docs/architecture.md for current system design.
- See docs/roadmap.md for active sprint goals.
```

---

## Appendix: Key `delegate_task` Patterns

### Steward spawning design review

```python
delegate_task(
    goal="Review the proposed config.py module and confirm it fits the architecture",
    context="""
    Project root: /home/adhish/Productivity/AMSCUP/test-bed/src/Modules/robust_testing/kradar
    Architecture doc: docs/architecture.md (attached below)
    <paste architecture.md>
    Proposed module: config.py handles sensor config loading for K-Radar dataset.
    Confirm: does this violate any documented module boundaries?
    Produce: a brief design verdict and any required changes.
    """,
    toolsets=["file"]
)
```

### Builder spawning parallel linting

```python
delegate_task(tasks=[
    {
        "goal": "Run ruff on src/ and return the full output",
        "context": "Project root: /absolute/path/to/project. Run: uv run ruff check src/",
        "toolsets": ["terminal"]
    },
    {
        "goal": "Run mypy on src/ and return the full output",
        "context": "Project root: /absolute/path/to/project. Run: uv run mypy src/",
        "toolsets": ["terminal"]
    }
])
```

### Verifier running secret scan

```python
delegate_task(
    goal="Scan the project for hardcoded secrets or credentials",
    context="""
    Project root: /absolute/path/to/project
    Run: git secrets --scan 2>&1 || trufflehog filesystem . --json
    Return the full output including exit code.
    """,
    toolsets=["terminal"]
)
```
