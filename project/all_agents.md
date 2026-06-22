# Multi-Agent Architecture for Thesis Project

## Overview

This architecture compresses the original list of specialized agents into **five high-value agents**, each with clear ownership and responsibilities.

The goal is to minimize overlap, reduce coordination overhead, and create measurable outputs that are useful for both software development and thesis evaluation.

---

# Agent 1: Project Steward

**Owns all project knowledge**

### Combines

* Project Historian
* Knowledge Base Curator
* Decision Record Agent
* Product Manager
* Scope Control Agent
* Literature Review Agent
* README Maintenance

### Responsibilities

Maintains:

```text
/docs/
    journal/
    research/
    decisions/
    roadmap.md
    architecture.md
```

Updates:

* `AGENTS.md`
* `README.md`
* Module-level READMEs
* Project roadmap
* Research notes
* Progress summaries

### Key Questions

* What are we building?
* Why are we building it?
* What changed?
* What should happen next?

### Rules

The Builder cannot change project scope.

Only the Project Steward can approve:

* New features
* Major architectural changes
* New dependencies
* Changes to project goals

### Outputs

* Project journal
* Research summaries
* Architecture Decision Records (ADRs)
* Roadmaps and milestones
* Documentation

---

# Agent 2: Architect

**Owns technical design**

### Combines

* System Architect
* Consistency Agent

### Responsibilities

Maintains:

```text
architecture.md
api_contracts.md
data_model.md
```

Reviews:

* Module boundaries
* Dependency direction
* API design
* Data flow
* Architectural consistency

Checks:

* Documentation matches implementation
* Architecture remains coherent
* New code follows established patterns

### Example

Builder proposes:

```text
Added Redis
```

Architect evaluates:

```text
Why is Redis needed?
Is it documented?
Does it fit the architecture?
What alternatives were considered?
```

### Outputs

* Technical designs
* Architecture documents
* Implementation plans
* Design reviews

### Rules

Builder should implement from Architect-approved plans whenever possible.

---

# Agent 3: Builder

**Owns implementation**

### Combines

* Builder Agent
* Formatting / Pre-commit Agent

### Responsibilities

Creates:

* Application code
* Configuration files
* Migrations
* Scripts
* Infrastructure definitions

Runs validation tools before claiming completion:

```bash
ruff check .
black .
mypy .
pre-commit run --all-files
```

### Rules

Builder cannot declare work complete until:

* Code is written
* Formatting succeeds
* Linting succeeds
* Static analysis succeeds

### Outputs

* Source code
* Tests requested by QA
* Refactors
* Build artifacts

---

# Agent 4: Verification & Security

**Owns reality**

### Combines

* Verification Agent
* Agent Auditor
* Exposed Key Scanner

### Responsibilities

Verifies every Builder claim.

Examples:

Builder says:

```text
Created auth.py
```

Verifier checks:

```bash
ls
cat auth.py
```

Builder says:

```text
Tests passed
```

Verifier checks:

```bash
pytest
```

Builder says:

```text
Dependency added
```

Verifier checks:

```bash
uv tree
```

### Security Checks

Scans for:

* Hardcoded API keys
* Secrets
* Credentials
* Misconfigured environment files
* Sensitive data leaks

### Rules

Nothing is considered complete until verified.

The Verifier trusts evidence, not agent statements.

### Outputs

* Verification reports
* Audit reports
* Security findings
* Hallucination detection metrics

---

# Agent 5: Quality Assurance

**Owns breaking the system**

### Combines

* Adversarial Reviewer
* Test Writer
* Test Executor
* Bug Hunter
* Fuzz Tester

### Responsibilities

Creates:

* Unit tests
* Integration tests
* Regression tests
* End-to-end tests
* Fuzz tests

Attempts to break assumptions.

### Example

Builder says:

```text
Input validation implemented
```

QA evaluates:

```text
What happens with:
- Empty strings
- Invalid JSON
- Extremely large payloads
- Unicode edge cases
- Concurrent requests
- Missing fields
```

### Rules

QA assumes the implementation is flawed until proven otherwise.

### Outputs

* Test suites
* Coverage reports
* Bug reports
* Failure analysis
* Fuzzing results

---

# Workflow

```text
Project Steward
        ↓
    Architect
        ↓
     Builder
        ↓
 Verification
        ↓
        QA
```

## Failure Loop

If QA discovers problems:

```text
QA
 ↓
Builder
 ↓
Verification
 ↓
QA
```

This loop continues until the implementation passes verification and quality checks.

---

# Thesis Evaluation Metrics

## Project Steward

Measures:

* Documentation quality
* Context retention
* Knowledge organization
* Scope stability

## Architect

Measures:

* Architectural consistency
* Number of design violations
* Documentation-to-code alignment

## Builder

Measures:

* Development throughput
* Feature completion rate
* Time-to-implementation

## Verification & Security

Measures:

* Hallucination detection rate
* Verification success rate
* Security findings
* Claim-to-reality accuracy

## Quality Assurance

Measures:

* Bugs discovered
* Test coverage
* Failure detection rate
* Fuzzing effectiveness

---

# Why This Architecture

Many agentic coding systems fail because they assume actions succeeded.

This architecture introduces a dedicated Verification & Security agent that independently confirms:

* Files actually exist
* Commands actually ran
* Tests actually passed
* Dependencies were actually installed
* Security issues are not introduced

The most interesting research area for a thesis is often the interaction between:

```text
Builder ↔ Verification
```

This relationship creates measurable data about:

* Hallucinations
* Self-correction
* Reliability
* Autonomous software engineering effectiveness

while keeping the overall system simple enough to manage and evaluate.

