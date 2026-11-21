# 06 — Consulting angle

**What I know about Cleven:** only what you told me — an engineering consultancy that places permanent consultants on-site at clients in automotive, telecom, energy and finance. I have no further company facts; do not invent any. Research their site/case studies before the interview.

**Industry facts below are GENERAL KNOWLEDGE** (not from your documents): verify before using.

---

## 1. What a consultancy is probably screening for (inference, not a Cleven fact)
1. Technical depth that survives a client technical interview.
2. Fast ramp-up in an unfamiliar domain/codebase.
3. Communication with non-experts; written clarity.
4. Ownership and honesty about limits (clients buy judgement).
5. Willingness to work on-site, embedded in a client team (note: Swedish "Beginner" and English "Intermediate" on the CV, see §5).

## 2. Evidence you already have for each
| Trait | Evidence (source) |
|---|---|
| Embedded at a client | Sysenso → Siemens client site secondment, regular demos, incorporated client feedback (CV:20-23). Your single strongest consulting signal. |
| Ramp-up in unfamiliar area | Hardware+Unity+EMG in 3 months at Chalmers Industriteknik (CV:27-32); ASF/K-Radar from scratch in a master's thesis. |
| Testing a vendor claim | Thesis design: read the paper's actual evidence, find where it stops, design the cheapest experiment beyond it (`Meth:19-26`). |
| Honest reporting of limits | Thesis `Disc:99-118`: single checkpoint, cause not established, no further data possible; CV Myo bullet "fidelity scoped as next stage". |
| Scale/ops | SLURM array jobs, ~1M output files consolidated to Parquet (`Meth:511,526`). |
| Finance-adjacent | First prize LUNAR FINTECH hackathon (CV:86-88). |
| Team/people | CIRC guide, TEDx tech coordinator, Rotary chair (CV:94-97). |

## 3. How the work transfers

### Automotive (direct)
- Perception, sensor fusion, robustness: your thesis is literally a validation exercise on an AV perception stack. Talking points: safety-case evidence (the thesis cites Sun et al. 2024 on perception safety standardisation, `Disc:144`), SOTIF-style "performance limitation under degraded sensors" thinking (**GENERAL KNOWLEDGE**: ISO 21448 SOTIF addresses hazards from functional insufficiencies without faults), scenario-based testing, sensor degradation requirements.
- Localisation (EKF with GNSS/RTK), mapping (LiDAR road features), ROS2.
- Gaps: no AUTOSAR/embedded production C++, no functional-safety (ISO 26262) process experience, no ECU deployment.

### Telecom (no direct experience)
Honest bridge, **GENERAL KNOWLEDGE**: 4D imaging radar shares MIMO array processing, beamforming and detection theory (CFAR) with RF/telecom signal processing; Kalman filtering underlies tracking/positioning; data-pipeline and failure-injection thinking transfers to network testing/QA. Do not claim RF/5G knowledge.

### Energy (no direct experience)
**GENERAL KNOWLEDGE** bridge: state estimation (Kalman-family) is core to power-system state estimation and battery SoC/SoH estimation; sensor-fault detection (bad-data detection via residual/innovation tests — the same gating logic as your EKF outlier rejection); control (LQR/MPC) for converters and storage. Do not claim domain knowledge.

### Finance (limited, hackathon only)
Bridge: robustness testing under perturbation ≈ stress testing / model-risk validation (challenge a model with conditions its developers did not test, quantify damage, report limits); Polars/Parquet data handling for large tabular pipelines (Polars is listed on the CV, not in the thesis text). The hackathon shows you can build a front-end prototype in a time box. Do not claim quantitative-finance knowledge.

## 4. "How would you approach an unfamiliar client problem?" — framework

1. **Clarify the decision.** What decision does the client need to make, what is the cost of being wrong, who owns it, what is the deadline? (The thesis equivalent: "does ASF's claim hold?" — a decision-shaped question.)
2. **Restate in my own words and get it confirmed** (in writing).
3. **Learn the domain fast.** Read the client's own docs/tickets/data first; shadow users; list unknown unknowns; find the one person who knows the history.
4. **Find what exists.** Reuse the client's tooling, data and conventions before introducing mine.
5. **Define success metrics and a baseline** before changing anything (thesis: reproduce baseline first, even though it came out 2–5 pts below the paper).
6. **Smallest experiment that discriminates between hypotheses.** (Thesis lesson: two explanations fit; the one experiment that distinguishes them wasn't run — lesson: *plan the discriminating experiment before the compute disappears*.)
7. **Make it reproducible** (scripts, versions, seeds, containers).
8. **Report with effect sizes and limits.** Separate what was measured from what is hypothesised. Flag decisions you disagree with.
9. **Hand over** documentation and make yourself non-critical.
Worked example to say aloud: "ASF claimed robustness; the evidence was narrow; I scoped a test the paper didn't run; the result was strong for one regime and I labelled the cause unproven."

Typical probes: *What if the client's data is bad? What if the requirement changes mid-way? What if you disagree with the client's architect? What if you have 2 days, not 2 weeks?* Answers: quantify data issues and agree remedy; renegotiate scope against time explicitly; present evidence and trade-offs, then accept the decision and document it; time-box, deliver a ranked partial with stated risk.

## 5. Honest gaps and credible answers

| Gap | Honest statement | Credible mitigation (only things you can show) |
|---|---|---|
| No telecom, energy or finance experience | "My depth is automotive perception and estimation; I haven't worked in those industries." | Method-level transfer (state estimation, fault detection, robustness testing, data pipelines); fast ramp-up evidence (Myo/Quest, thesis); willing to be assigned where my skills transfer first. |
| Limited production deployment | "One year at Sysenso in a client team; my other work is academic/prototype." | Client demos and feedback cycles at Siemens site; reproducible HPC pipeline; honest on limits. Don't pretend to production C++ at scale. |
| Thesis is evaluation, nothing trained | "I evaluated a released checkpoint; no training; the contribution is the test design and analysis." (`Meth:5`) | The method is reusable and cheap; the finding is specific. |
| Causal explanation unproven | "I can show what happened, not fully why." (`Disc:107`) | Name the discriminating experiment; consultants are valued for calibrated confidence. |
| Cannot rerun experiments | "Cluster access ended after the sweep." (`Disc:118`) | Local prediction/GT data retained; follow-ups specified. |
| Language | CV: English *Intermediate*, Swedish *Beginner* (CV:110) | **Decide your honest line now.** If English proficiency is higher than "Intermediate", fix the CV. For Swedish: state current level, a concrete learning plan, and ask which client sites require it. Do not overclaim. |
| CV inconsistencies | ROS2 project dates/location overlap Sysenso (Chennai) and precede Chalmers; `[ROLE TITLE]` placeholder | Fix before submission; have the true answer ready. |
| "SLAM-adjacent", "Docker", "PyTorch" skill lines | Say exactly what you did | Match each to a project or remove. |

## 6. Questions to ask them (shows consultancy-literacy)
- How long is a typical placement, and how is the first 30/60/90 days handled on-site?
- How are consultants matched across industries — can someone with automotive depth be placed in energy/telecom, and how is domain ramp-up supported?
- What technical review does a consultant get from the home company while embedded at a client?
- How is bench time handled?
- What does the progression path look like (senior/lead/architect)?
- Language requirements at client sites?

## 7. Positioning lines
- "I'm strongest where a claim about a sensor-based system has to be tested against reality."
- "At Siemens I learned that the demo cadence is the product: show progress, absorb feedback, repeat."
- "I would rather give you a calibrated 'I don't know yet, and here is the experiment that would tell us' than a confident guess."
