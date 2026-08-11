# Master Map of Contents (MOC) for the AMSCUP/K-Radar Vault

## Overview
This vault contains organized notes from the AMSCUP thesis work and K-Radar project, restructured into a thesis-shaped project (Introduction → Literature Survey → Theory → Design → Implementation → Results → Writing) via the `docs/vault_ingestion_prompt.md` consolidation pass.

## Folder Structure

- [[00 Inbox|00_Inbox/00 Inbox.md]] - Unsorted scraps, TODOs, ideas. See [[Dedup Map|00_Inbox/Dedup_Map.md]] for the duplicate-note audit.
- [[01 Project Management|01_Project_Management/01 Project Management.md]] - Thesis plan, timeline, milestones, research questions, supervisor meetings
- [[02 Literature|02_Literature/02 Literature.md]] - Literature notes, reviews, surveys. [[Literature_Survey|Literature Survey]] synthesizes 12 noise/corruption papers by theme.
- [[03 Theory|03_Theory/03 Theory.md]] - Equations, models, algorithms, derivations, definitions. Visibility formulas, coordinate frames, sensor noise models.
- [[04 Design|04_Design/04 Design.md]] - System architecture, design trade-offs, diagrams, interface definitions, specifications. Noise taxonomy, API contracts, output schema.
- [[05 Implementation|05_Implementation/05 Implementation.md]] - Design decisions in code, module breakdown, bugs/fixes, performance notes, API notes
- [[06 Results|06_Results/06 Results.md]] - Experiment notes, setup, parameters, results, observations, linked plots. [[Verification_Report|Verification Report]] (merged pipeline audit) and [[Noise_Visual_Inspection|Noise Visual Inspection]] (rendered corruption gallery).
- [[07 Writing|07_Writing/07 Writing.md]] - Thesis draft split by section. [[Introduction|Introduction]], [[LaTeX_Report_Structure|LaTeX Report Structure]], [[Vault_to_Thesis_Mapping|Vault to Thesis Mapping]].
- [[08 Resources|08_Resources/08 Resources.md]] - Diagrams, charts, images, exported plots, LaTeX figures
- [[09 References|09_References/09 References.md]] - Key reference clusters, citation notes
- [[10 Archive|10_Archive/10 Archive.md]] - Deprecated/outdated material (never delete, only move). Holds import-echo duplicates resolved in the Phase-1 dedup pass.

## Migration Info
See [[Migration Changelog|00_Inbox/Migration_Changelog.md]] for detailed migration logs, and [[Dedup Map|00_Inbox/Dedup_Map.md]] for the duplicate-resolution audit trail.

## Last Updated
2026-08-11 — vault ingestion / thesis-shaped restructure (Phases 1-5 of `docs/vault_ingestion_prompt.md`)