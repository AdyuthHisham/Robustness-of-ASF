# 06 — Consulting angle (Cleeven)

Facts about Cleeven come only from your brief: engineering consultancy, permanent consultants placed on-site at clients in automotive, telecom, energy, finance. **No Cleeven job description, website text or past application is in any folder I read**, so nothing below is specific to their stack; check their site/job ad before the interview.

## 1. What transfers (each tied to evidence)
| Consulting need | Your evidence | Source |
|---|---|---|
| Joining a client's existing system, not building from scratch | Thesis tests someone else's released model unmodified; Sysenso work was client-seconded at Siemens with demos and feedback loops | thesis `Methods.tex:5`; CV:20-23 (CV only) |
| Turning a vague claim into a testable one | "robust to degradation and failure" → taxonomy: absent-and-known / absent-and-unknown / present-but-wrong | `Methods.tex:17-26`, `Discussion.tex:144` |
| Evidence quality and caveats | Reliability floor N>30, sequence-confounding flag, reproduction gap reported not hidden, causal claim withheld | `Methods.tex:446`, `Results.tex:36`, `Discussion.tex:106` |
| Delivering infra at scale | SLURM array sweep, ~10⁶ output files → one Parquet table, one canonical metric loader | `Methods.tex:511-527` |
| Sensor fusion / estimation breadth | EKF (FIDO, SSY345), complementary filter + LQR (SSY191), LiDAR point-cloud work (CV) | `R/` PDFs |
| Team delivery | FIDO: first author of a 5-person system (Go2, LIO, RTK, LLM agent); SSY191 team of 4 | `R/SSY226…pdf`, `R/SSY191…pdf` |
| Failure honesty | Crazyflie hardware failure analysed; FIDO indoor/outdoor not fused — stated in the reports | `R/` PDFs |

## 2. Transfer by sector (frame as analogy, never as experience)
- **Automotive (strongest):** perception robustness validation, sensor-fault injection, SOTIF-style thinking (SOTIF/ISO 26262 details are **NID**; thesis only cites a paper on safety standardisation, `Discussion.tex:144`). Offer: a per-sensor fault-injection test plan and metrics for a supplier's detector.
- **Telecom:** analogous *concepts*: redundant measurement streams, degraded vs dead vs noisy links, KPI baselines vs deviation. You have **no** telecom experience (RAN, 5G, protocols). Say so; offer the method, not domain knowledge.
- **Energy:** state estimation (Kalman filtering) is the same family as grid state estimation; sensor fault detection in SCADA/PMU data is the same shape of problem. **No** energy-system experience; don't claim any.
- **Finance:** the CV lists a first-prize fintech hackathon (Noctis Bank dashboard prototype, 2026) — frontend/product prototype, not quant or risk engineering; **no** finance engineering experience. Robustness-testing mindset (stress scenarios, tail behaviour) transfers conceptually.

## 3. 'How would you approach an unfamiliar client problem?' (answer skeleton)
1. **Clarify the decision** the client needs (ship/no-ship, root cause, cost, safety case) and who owns it; get the failure definition in numbers.
2. **Inventory what exists:** data, logs, existing metrics, owners, constraints (confidentiality, tooling, compute).
3. **Baseline first:** reproduce current performance under their own protocol (your thesis: baseline 2–5 AP points off paper, reported, not buried).
4. **Cheap experiments before builds:** fault injection / ablation on existing artefacts; stratify to find where it fails (your weather/distance/density strata).
5. **Separate measurement from explanation:** state what is measured, what is hypothesised, and the single experiment that discriminates (LiDAR-only vs fused).
6. **Communicate in client's currency:** one-page finding, risk, next experiment, effort; demo early (CV:23).
7. **Hand over:** reproducible script, README, metrics definitions, known limitations.
Example to cite: thesis pipeline (`Methods.tex:520-529`).

## 4. Honest gaps and credible answers
| Gap | Evidence | Credible answer |
|---|---|---|
| No telecom/energy/finance experience | CV, all docs | "My depth is estimation and perception. In an unfamiliar domain I'd pair with the client's domain owner in week one, learn their failure definitions and data, and apply the same measure-then-explain loop. The domain vocabulary is the learning curve, the method transfers." |
| Limited production deployment | thesis scope excludes hardware (`Introduction.tex:79`); Crazyflie hardware failed; FIDO "yet to be validated in real-time deployment"; Sysenso is the only job with delivery (unverified) | "My deployments were research-grade; I know where the gap is: observability, rollback, calibration, and long-run drift. At Sysenso I delivered to a client with demos; I'd want a mentor for release engineering." (Adapt to what is true.) |
| Thesis is single-model, synthetic, seed 42 | `Discussion.tex:103-118` | State as method limits and next steps (multi-seed, bootstrap, LiDAR-only control). |
| Hardware results mixed | `R/SSY191…pdf` | "Sim worked, hardware didn't, I know the likely causes (CoM offset, unmodelled actuators, unfinished code port) and what I'd do first: system-ID the thrust model and add integral trim." |
| Swedish beginner (CV:110) | CV | On-site client placement may need Swedish; state learning plan truthfully (don't claim a course you haven't taken). |
| Permanent consultant = utilisation, travel, client-driven scope | brief | Be ready: "why consulting rather than a product company?" Answer from your real motive; the evidence you can cite for enjoying client-facing work is CV:23 (demos/feedback) and the hackathon (shipped a prototype under time pressure), both unverified in documents. |
| ML depth | thesis evaluates, doesn't train; PyTorch claimed on CV, no evidence | Be able to code a small training loop live or don't lead with PyTorch. |

## 5. Likely consulting-style questions
1. Tell me about a time you disagreed with a supervisor/client. (Use: ASF's claim vs your finding — not adversarial: you measured the boundary, `Conclusion.tex:78`.)
2. How do you estimate effort when requirements are vague?
3. A client wants a number you can't defend. What do you do? (Thesis: pooled vs class-mean mAP, 21.6 vs 17.45 — name the aggregation; refuse to give a bare number.)
4. How do you ramp up on a new codebase in a week? (Your thesis: you traced ASF's inference code to learn how availability is handled.)
5. How do you document and hand over?
6. What happens when the client's data is dirty? (K-Radar label revisions, strata with <10 sequences, flagged.)
7. Why consulting? Why Cleeven? (**NOT IN DOCUMENTS** — prepare from their site.)
