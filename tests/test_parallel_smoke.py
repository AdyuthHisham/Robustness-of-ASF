"""Smoke tests for scripts/run_full_sequence.py's --workers process-pool parallelism.

scripts/ is not a package (no __init__.py) so the module under test is loaded
via importlib from its file path rather than a normal import.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import polars as pl
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts" / "visibility"
RUN_FULL_SEQUENCE_PATH = SCRIPTS_DIR / "run_full_sequence.py"


def _load_run_full_sequence():
    """Load scripts/run_full_sequence.py as a module.

    Must register in sys.modules under its own name before exec: --workers>1
    submits `_process_one_frame` to a ProcessPoolExecutor, and even under
    fork (the Linux default start method) the callable is pickled by
    module-qualified reference — unpickling in the worker does
    `getattr(sys.modules['run_full_sequence'], qualname)`, which fails unless
    the module is registered under that exact name.
    """
    spec = importlib.util.spec_from_file_location("run_full_sequence", RUN_FULL_SEQUENCE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestThreadPinning:
    def test_smk18_blas_thread_env_pinned_by_default(self):
        """SMK-18: importing run_full_sequence pins OMP/OPENBLAS/MKL thread envs to
        1 by default (prevents BLAS/OpenMP oversubscription fighting a --workers>1
        process pool), but does not clobber a value already set by the caller
        (e.g. an sbatch script pinning to a specific core count).

        Run in a subprocess so the pinning doesn't leak into this test process's
        environment or affect other tests.
        """
        result = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, sys.argv[1]); import run_full_sequence, os; "
             "print(os.environ['OMP_NUM_THREADS'], os.environ['OPENBLAS_NUM_THREADS'], os.environ['MKL_NUM_THREADS'])",
             str(SCRIPTS_DIR)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.split() == ["1", "1", "1"]

        result_preset = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, sys.argv[1]); import run_full_sequence, os; "
             "print(os.environ['OMP_NUM_THREADS'])",
             str(SCRIPTS_DIR)],
            capture_output=True, text=True, timeout=30,
            env={**__import__("os").environ, "OMP_NUM_THREADS": "4"},
        )
        assert result_preset.returncode == 0, result_preset.stderr
        assert result_preset.stdout.strip() == "4", "caller-supplied thread count must not be overridden"


class TestParallelParity:
    @pytest.mark.slow
    @pytest.mark.timeout(300)
    def test_smk19_parallel_output_matches_serial(self, dataset_root, tmp_path, monkeypatch):
        """SMK-19: --workers 1 (serial) and --workers 3 (process pool) produce
        row-identical output (content, not just shape) for the same frames.
        Guards against the parallel path silently reordering/dropping/duplicating
        rows or diverging in computed values from the original serial baseline.
        """
        m = _load_run_full_sequence()
        # run_sequence() reads output/error-log paths from module globals
        # (mirrors main()'s CLI-override pattern) — point them at tmp_path so
        # this test doesn't clobber real outputs/ files or collide with
        # concurrently-running tests.
        monkeypatch.setattr(m, "OUTPUT_PATH", tmp_path / "serial.parquet")
        monkeypatch.setattr(m, "ERROR_LOG", tmp_path / "serial.errors.log")
        df_serial = m.run_sequence(
            sequence_id="2", dataset_root=dataset_root,
            max_frames=4, annotated_first=True, workers=1,
        )
        monkeypatch.setattr(m, "OUTPUT_PATH", tmp_path / "parallel.parquet")
        monkeypatch.setattr(m, "ERROR_LOG", tmp_path / "parallel.errors.log")
        df_parallel = m.run_sequence(
            sequence_id="2", dataset_root=dataset_root,
            max_frames=4, annotated_first=True, workers=3,
        )

        assert df_serial.height > 0, "serial run produced no rows"
        sort_cols = ["frame_idx", "obj_tracking_id"]
        a = df_serial.sort(sort_cols)
        b = df_parallel.sort(sort_cols)
        assert a.shape == b.shape
        assert a.columns == b.columns
        assert a.equals(b), "parallel output diverges from serial output for identical input frames"

    @pytest.mark.slow
    @pytest.mark.timeout(300)
    def test_smk20_one_bad_frame_does_not_crash_parallel_pool(self, dataset_root, tmp_path, monkeypatch):
        """SMK-20: under --workers>1, a single frame raising an exception is
        captured into the per-frame error (matching the serial loop's existing
        per-frame try/except behaviour) without crashing the process pool or
        losing rows from the other, successful frames in the same batch.
        """
        m = _load_run_full_sequence()
        from kradar_visibility.parser import get_sequence_label_files, parse_label_file as real_parse_label_file

        label_files = get_sequence_label_files("2", dataset_root)
        annotated = []
        for f in label_files:
            _, objects = real_parse_label_file(f)
            if objects:
                annotated.append(f)
            if len(annotated) >= 4:
                break
        assert len(annotated) >= 2, "need at least 2 annotated frames for this test"
        bad_header, _ = real_parse_label_file(annotated[1])
        bad_tesseract_idx = bad_header.tesseract_idx

        # Patch compute_visibility_for_frame (the per-frame compute step
        # inside _process_one_frame), not parse_label_file: run_sequence's
        # own annotated_first pre-scan also calls parse_label_file, so
        # patching that would silently exclude the target frame from the
        # selected set instead of exercising a mid-run failure.
        real_compute = m.compute_visibility_for_frame

        def flaky_compute(sequence_id, header, objects, dataset_root, **kwargs):
            if header.tesseract_idx == bad_tesseract_idx:
                raise RuntimeError("SMK-20 injected failure")
            return real_compute(sequence_id, header, objects, dataset_root, **kwargs)

        monkeypatch.setattr(m, "compute_visibility_for_frame", flaky_compute)
        monkeypatch.setattr(m, "OUTPUT_PATH", tmp_path / "flaky.parquet")
        monkeypatch.setattr(m, "ERROR_LOG", tmp_path / "flaky.errors.log")

        df = m.run_sequence(
            sequence_id="2", dataset_root=dataset_root,
            max_frames=4, annotated_first=True, workers=3,
        )

        assert m.ERROR_LOG.exists()
        error_text = m.ERROR_LOG.read_text()
        assert annotated[1].stem in error_text
        assert "SMK-20 injected failure" in error_text
        # the other 3 annotated frames must still have produced rows despite
        # the pool having one worker task fail
        assert df.height > 0
        assert df.filter(pl.col("frame_idx") == int(bad_tesseract_idx)).height == 0
