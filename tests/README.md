# tests/

| File | What | Needs |
|---|---|---|
| `test_smoke.py` | SMK-01 to SMK-21 plus a few unnumbered checks. Fast checks on parsing, loading and metrics. Run first. | Mostly the K-Radar dataset under `KRADAR_DATASET_ROOT` |
| `test_verify.py` | VER-* correctness checks on full-dataset output. Run only after smoke passes. | Dataset and `data/visibility/output.parquet` |
| `test_parallel_smoke.py` | Parallel-run smoke test. | Dataset |

```bash
uv run pytest tests/test_smoke.py
```

Status on the restructured tree: 9 passed, 11 failed. Ten failures are the missing dataset; SMK-21 is an unexplained failure (see `docs/logs/2026-11-21_restructure_summary.md`). Test IDs map to specs in `docs/methodology/`.
