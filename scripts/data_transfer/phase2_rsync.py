#!/usr/bin/env python3
"""
RsyncOrchestrator — Generates per-sequence rsync commands (FIXED).
Each sheet gets its own source folder and batch.

FIXES:
  1. Manifest path no longer hardcoded to current directory
  2. Constructor validates manifest path exists
  3. batch_dir output location is configurable
"""

import json
import subprocess
from pathlib import Path
from typing import Dict
import shlex


class RsyncOrchestrator:
    """
    Each sheet/sequence is independent:
    - Sheet 1 → rsync from 1/radar_zyx_cube/ to remote:.../1/
    - Sheet 2 → rsync from 2/radar_zyx_cube/ to remote:.../2/
    """

    def __init__(
        self,
        manifest_path: str,
        remote_host: str,
        remote_dataset_root: str,
        batch_output_dir: str = None,
    ):
        """
        Args:
            manifest_path: Full path to radar_sync_manifest.json
            remote_host: SSH destination (user@hostname)
            remote_dataset_root: Remote base path for dataset
            batch_output_dir: Optional output dir for rsync scripts. Defaults to ./rsync_batches
        """
        # FIX #3: Accept full path and validate it exists
        manifest_file = Path(manifest_path)
        if not manifest_file.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_file) as f:
            self.manifest = json.load(f)

        self.remote_host = remote_host
        self.remote_root = remote_dataset_root.rstrip("/")

        # Support optional batch_output_dir
        if batch_output_dir:
            self.batch_dir = Path(batch_output_dir)
        else:
            self.batch_dir = Path("rsync_batches")

        self.batch_dir.mkdir(parents=True, exist_ok=True)

    def generate_file_list(self, sheet_name: str, batch_data: dict) -> Path:
        """Create --files-from list for a sequence."""
        list_path = self.batch_dir / f"{sheet_name}_files.txt"
        source_dir = Path(batch_data["source_dir"])
        files = batch_data["files"]

        with open(list_path, "w") as f:
            for fname in files:
                full_path = source_dir / fname
                if full_path.exists():
                    # Path relative to sequence dir (parent of radar_zyx_cube)
                    f.write(f"radar_zyx_cube/{fname}\n")
                else:
                    print(f"  [WARN] Missing: {full_path}")

        return list_path

    def generate_rsync_command(
        self, sheet_name: str, file_list: Path, batch_data: dict
    ) -> str:
        """Build rsync for one sequence."""
        sequence_dir = Path(batch_data["sequence_dir"])
        # Source is the sequence folder (contains radar_zyx_cube/)
        source = shlex.quote(str(sequence_dir) + "/")
        # Remote destination is the corresponding sequence folder
        dest = shlex.quote(f"{self.remote_host}:{self.remote_root}/{sheet_name}/")

        cmd_parts = [
            "rsync",
            "-avz",
            "--progress",
            "--stats",
            "--files-from",
            shlex.quote(str(file_list)),
            source,
            dest,
        ]

        return " ".join(cmd_parts)

    def create_all_batches(self) -> Dict[str, str]:
        """Generate all batch files and scripts."""
        batches = self.manifest.get("rsync_batches", {})
        commands = {}

        print(f"\n[GENERATING] {len(batches)} batches...")

        for sheet_name, batch_data in batches.items():
            files = batch_data.get("files", [])
            if not files:
                print(f"  [SKIP] Sheet {sheet_name}: empty")
                continue

            file_list = self.generate_file_list(sheet_name, batch_data)
            cmd = self.generate_rsync_command(sheet_name, file_list, batch_data)
            commands[sheet_name] = cmd

            # Write script
            script_path = self.batch_dir / f"{sheet_name}_sync.sh"
            with open(script_path, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"# Sheet {sheet_name}: {len(files)} files\n")
                f.write(f'# Local:  {batch_data["sequence_dir"]}\n')
                f.write(
                    f"# Remote: {self.remote_host}:{self.remote_root}/{sheet_name}/\n"
                )
                f.write("set -euo pipefail\n\n")
                f.write(f'echo "[START] Sheet {sheet_name} ({len(files)} files)"\n')
                f.write(cmd + "\n")
                f.write(f'echo "[DONE] Sheet {sheet_name}"\n')

            script_path.chmod(0o755)
            print(f"  [OK] Sheet {sheet_name}: {len(files)} files")

        # Master scripts
        self._write_master_scripts(commands)

        return commands

    def _write_master_scripts(self, commands: Dict[str, str]):
        """Write sequential and parallel run scripts."""
        # Sequential
        seq_path = self.batch_dir / "run_all.sh"
        with open(seq_path, "w") as f:
            f.write("#!/bin/bash\nset -euo pipefail\n\n")
            for sheet in sorted(commands.keys()):
                f.write(f'echo "\\n=== Sheet {sheet} ==="\n')
                f.write(f"./{sheet}_sync.sh\n")
            f.write('\necho "[ALL DONE]"')
        seq_path.chmod(0o755)

        # Parallel (GNU parallel or fallback)
        par_path = self.batch_dir / "run_parallel.sh"
        with open(par_path, "w") as f:
            f.write("#!/bin/bash\nset -uo pipefail\n\n")
            sheets = sorted(commands.keys())
            f.write("if command -v parallel &>/dev/null; then\n")
            f.write("  parallel --jobs 4 -a <<EOF ./{}_sync.sh\n")
            for s in sheets:
                f.write(f"{s}\n")
            f.write("EOF\nelse\n")
            f.write("  for s in " + " ".join(sheets) + "; do\n")
            f.write("    ./${s}_sync.sh &\n")
            f.write("    [ $(jobs -r | wc -l) -ge 4 ] && wait -n\n")
            f.write("  done\n  wait\nfi\n")
        par_path.chmod(0o755)

        print(f"\n[MASTER] Sequential: {seq_path}")
        print(f"[MASTER] Parallel:   {par_path}")

    def run_dry_run(self, sheet_name: str = None):
        """Execute rsync -n for validation."""
        batches = self.manifest.get("rsync_batches", {})
        targets = (
            [sheet_name] if sheet_name else sorted(batches.keys())[:3]
        )  # First 3 by default

        for sheet in targets:
            batch = batches.get(sheet)
            if not batch:
                continue

            file_list = self.batch_dir / f"{sheet}_files.txt"
            cmd = self.generate_rsync_command(sheet, file_list, batch)
            dry_cmd = cmd.replace("rsync -avz", "rsync -avzn")

            print(f"\n{'='*50}")
            print(f"DRY RUN: Sheet {sheet}")
            print(f"{'='*50}")

            result = subprocess.run(dry_cmd, shell=True, capture_output=True, text=True)
            lines = [lined for lined in result.stdout.split("\n") if lined.strip()]

            # Show summary
            print(
                f"Would transfer: {len([lined  for lined in lines if 'radar_zyx_cube' in lined])} files"
            )
            if result.returncode != 0:
                print(f"[ERROR] {result.stderr[:500]}")


if __name__ == "__main__":
    # Example usage (with fixed path handling)
    orch = RsyncOrchestrator(
        "/home/adhish/k-radar-workflow/manifests/radar_sync_manifest.json",
        "user@cluster.hpc.edu",
        "/data/k-radar",
        "/home/adhish/k-radar-workflow/rsync_batches",
    )
    orch.create_all_batches()
    orch.run_dry_run("1")
