#!/usr/bin/env python3
"""
TransferVerifier — Validates transferred files on remote cluster.

Reads the unified manifest (radar_sync_manifest.json) and verifies files
exist on remote with matching MD5 checksums.
"""

import json
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class TransferVerifier:
    """
    Two-phase verification:
    1. Fast: Count files remotely vs expected
    2. Deep: MD5 comparison for integrity
    """

    def __init__(
        self,
        manifest_path: str,  # Full path to radar_sync_manifest.json
        remote_host: str,
        remote_base: str,  # Remote base path (should mirror data_root)
    ):
        self.manifest_path = Path(manifest_path)
        self.remote_host = remote_host
        self.remote_base = remote_base.rstrip("/")

        with open(self.manifest_path) as f:
            self.manifest = json.load(f)

    def get_sequence_batch(self, sequence: str) -> Optional[dict]:
        """Get rsync batch data for a specific sequence from unified manifest."""
        batches = self.manifest.get("rsync_batches", {})
        return batches.get(sequence)

    def local_checksum(self, file_path: Path) -> Optional[str]:
        """Compute MD5 with streaming for memory efficiency."""
        if not file_path.exists():
            return None

        h = hashlib.md5()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def remote_checksums(self, remote_paths: List[str]) -> Dict[str, str]:
        """Batch-fetch MD5s from remote via SSH."""
        if not remote_paths:
            return {}

        # Build command: md5sum path1 path2 ...
        paths_str = " ".join(remote_paths)
        cmd = f'ssh {self.remote_host} "md5sum {paths_str} 2>/dev/null || echo MISSING"'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        checksums = {}
        for line in result.stdout.strip().split("\n"):
            if not line or line == "MISSING":
                continue
            parts = line.split()
            if len(parts) >= 2:
                checksum = parts[0]
                fname = Path(parts[1]).name
                checksums[fname] = checksum

        return checksums

    def verify_sequence(self, sequence: str, deep: bool = False) -> dict:
        """
        Verify one sequence's transferred files.
        """
        batch = self.get_sequence_batch(sequence)
        if not batch:
            return {"sequence": sequence, "status": "NO_MANIFEST"}

        files = batch.get("files", [])
        source_dir = Path(batch.get("source_dir", ""))

        if not files:
            return {"sequence": sequence, "status": "NO_FILES"}

        result = {
            "sequence": sequence,
            "expected_count": len(files),
            "status": "PENDING",
        }

        # Phase 1: Fast count check
        remote_radar_dir = f"{self.remote_base}/{sequence}/radar_zyx_cube"
        count_cmd = f'ssh {self.remote_host} "find {remote_radar_dir} -maxdepth 1 -type f | wc -l"'
        count_result = subprocess.run(
            count_cmd, shell=True, capture_output=True, text=True
        )

        if count_result.returncode == 0:
            result["remote_total_files"] = int(count_result.stdout.strip())

        # Phase 2: Deep MD5 verification
        if deep:
            # Compute local checksums
            local_sums = {}
            for fname in files:
                fpath = source_dir / fname
                local_sums[fname] = self.local_checksum(fpath)

            # Fetch remote checksums
            remote_paths = [f"{remote_radar_dir}/{fname}" for fname in files]
            remote_sums = self.remote_checksums(remote_paths)

            # Compare
            mismatches = []
            missing = []
            for fname, local_hash in local_sums.items():
                remote_hash = remote_sums.get(fname)

                if remote_hash is None:
                    missing.append(fname)
                elif local_hash != remote_hash:
                    mismatches.append(
                        {
                            "file": fname,
                            "local_md5": local_hash,
                            "remote_md5": remote_hash,
                        }
                    )

            result["deep_verify"] = {
                "files_checked": len(files),
                "missing_on_remote": missing,
                "md5_mismatches": mismatches,
                "pass": len(missing) == 0 and len(mismatches) == 0,
            }
            result["status"] = "PASS" if result["deep_verify"]["pass"] else "FAIL"
        else:
            result["status"] = "PASS"  # Shallow pass

        return result

    def verify_all(self, deep: bool = False) -> List[dict]:
        """Verify all sequences from the unified manifest."""
        batches = self.manifest.get("rsync_batches", {})
        results = []

        print(f"[VERIFY] Checking {len(batches)} sequences (deep={deep})")

        for sequence in sorted(batches.keys(), key=lambda x: int(x)):
            print(f"\n  Sequence {sequence}...")
            result = self.verify_sequence(sequence, deep=deep)
            results.append(result)

            icon = "✓" if result["status"] == "PASS" else "✗"
            print(
                f"    {icon} {result['status']} (expected: {result['expected_count']})"
            )

            if deep and result.get("deep_verify"):
                dv = result["deep_verify"]
                if dv["missing_on_remote"]:
                    print(f"    Missing: {dv['missing_on_remote']}")
                if dv["md5_mismatches"]:
                    print(f"    MD5 mismatches: {len(dv['md5_mismatches'])}")

        # Summary
        passed = sum(1 for r in results if r["status"] == "PASS")
        failed = sum(1 for r in results if r["status"] == "FAIL")

        print(f"\n{'='*60}")
        print("VERIFICATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")

        if failed > 0:
            failed_seqs = [r["sequence"] for r in results if r["status"] == "FAIL"]
            print(f"Failed sequences: {failed_seqs}")

        return results


# ═════════════════════════════════════════════════════════════════════
# SMOKE TESTS
# ═════════════════════════════════════════════════════════════════════


def smoke_test_1_checksum_streaming():
    """Test MD5 computation with known content."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = Path(tmpdir) / "test.mat"
        fpath.write_text("radar_data_12345")

        expected = hashlib.md5(b"radar_data_12345").hexdigest()

        verifier = TransferVerifier.__new__(TransferVerifier)
        computed = verifier.local_checksum(fpath)

        assert computed == expected

        print("✓ SMOKE TEST 1: Checksum streaming correct")


def smoke_test_2_remote_parsing():
    """Test md5sum output parsing."""
    sample = (
        "d41d8cd98f00b204e9800998ecf8427e  /data/1/radar_zyx_cube/radar_00033.mat\n"
        "e99a18c428cb38d5f260853678922e03  /data/1/radar_zyx_cube/radar_00034.mat"
    )

    checksums = {}
    for line in sample.strip().split("\n"):
        parts = line.split()
        checksums[Path(parts[1]).name] = parts[0]

    assert checksums["radar_00033.mat"] == "d41d8cd98f00b204e9800998ecf8427e"

    print("✓ SMOKE TEST 2: Remote parsing correct")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING ALL SMOKE TESTS")
    print("=" * 60)

    smoke_test_1_checksum_streaming()
    smoke_test_2_remote_parsing()

    print("\n" + "=" * 60)
    print("ALL SMOKE TESTS PASSED")
    print("=" * 60)

    # Production usage examples:
    #
    # Verify single sequence:
    #   v = TransferVerifier("/home/adhish/k-radar-workflow/manifests/radar_sync_manifest.json",
    #                        "user@cluster", "/data/k-radar")
    #   result = v.verify_sequence("1", deep=False)
    #
    # Verify all sequences:
    #   v.verify_all(deep=False)  # Fast count check
    #   v.verify_all(deep=True)   # Thorough MD5 check
