# AGENTS.md — Project Agent Roles

This project uses a five-agent system. See all_agents.md for full spec.

## Hard rules (ALL agents)
- NEVER use pip. ALWAYS use uv.
- NEVER assume a file exists. Run `ls -la &lt;path&gt;` first.
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
