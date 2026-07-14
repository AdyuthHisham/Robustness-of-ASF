# Testing Notes — Errata

## Errata: False Claims from Prior Sessions

### 1. False Claim: Smoke Test Suite Timeout

**False claim (prior report):** The smoke test suite "timed out when run in full" and only `test_smk17_full_pipeline_two_sequences` could be confirmed passing within a time limit.

**Actual result (verified by direct execution):**
```
19 passed in 242.07s (0:04:02)
```

Full, untruncated output of `uv run pytest tests/test_smoke.py -v` completed in **242.07 seconds (4 minutes 2 seconds)** with **all 19 tests passing** and **no timeout**. The timeout claim was false.

---

### 2. False Claim: "Task 3.2" and "Task 3.3" Completion

**False claim (prior ad-hoc task numbering):** "Task 3.2 (Radar Doppler consistency)" and "Task 3.3 (Camera temporal consistency)" were reported as "completed" or "verified."

**Actual code state at time of claim (verified by grep):**
- **Radar Doppler consistency (`radar_score_with_doppler`):** Function existed in `radar_visibility.py` but was **never called from `pipeline.py`** — dead code, not an integrated feature.
- **Camera temporal consistency:** `grep -n "temporal" src/kradar_visibility/camera_visibility.py` returned **zero matches** — no temporal-consistency logic was ever implemented.

**Current project decision (formal, not pending):** Both items have been formally reclassified as **OUT OF SCOPE** by project decision:
- **Radar Doppler consistency:** Out of scope — K-Radar dataset lacks RTK-GPS/INS ground truth required for Doppler consistency validation.
- **Camera temporal consistency:** Out of scope — Pipeline is intentionally stateless / per-frame by design; temporal consistency is out of scope.

These are not "pending work" — they are formally closed as out of scope.

---

## Going Forward: Evidence Requirement for Completion Claims

**All completion claims in this project must be accompanied by raw command output in the same message** — not narrative summary alone.

Required evidence per claim type:
| Claim type | Required evidence (paste raw output) |
|------------|--------------------------------------|
| Test pass  | Full `uv run pytest ... -v` output showing `X passed in Y.Ys` |
| Test failure fix | Full `uv run pytest ... -v` output showing the specific test now passes |
| Code change / diff | `git diff` or unified diff of the exact changes |
| Code existence / absence | `grep -n "pattern" path/to/file.py` output (showing line numbers or zero matches) |
| File existence | `ls -la path/to/file` or `cat path/to/file` |

Narrative summaries without accompanying raw command output will not be accepted as verification.