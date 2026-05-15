#!/usr/bin/env python3
"""
RadarFileMapper — Multi-Sequence Version (FIXED)
One Excel file with 58 sheets, each sheet maps to its own sequence folder.

FIXES:
  1. tesseract_to_cube_stem() now strips leading zeros
  2. export_manifest() now respects output_dir parameter
  3. Constructor accepts optional output_dir argument
"""

import pandas as pd
from pathlib import Path
import json
import re
from typing import Dict, Optional


class RadarFileMapper:
    """
    Maps each Excel sheet to its corresponding sequence folder.

    Sheet '1' → base_dir/1/radar_zyx_cube/
    Sheet '2' → base_dir/2/radar_zyx_cube/
    ...
    Sheet '58' → base_dir/58/radar_zyx_cube/
    """

    FILENAME_PATTERN = re.compile(r"^([a-zA-Z]+)_(\d+)$")

    def __init__(self, xlsx_path: str, dataset_root: str, output_dir: str = None):
        """
        Args:
            xlsx_path: Path to the Excel file with 58 sheets
            dataset_root: Parent directory containing folders 1, 2, ..., 58
            output_dir: Optional output directory for manifests. Defaults to current dir.
        """
        self.xlsx_path = Path(xlsx_path)
        self.dataset_root = Path(dataset_root)

        # FIX #2: Support output_dir parameter
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.output_dir = Path.cwd()

        self.mappings: Dict[str, dict] = {}

    @staticmethod
    def normalize_unc_path(raw_path: str) -> str:
        if pd.isna(raw_path):
            return ""
        return str(raw_path).replace("\\", "/").lstrip("/")

    @staticmethod
    def extract_stem(normalized_path: str) -> Optional[str]:
        if not normalized_path:
            return None
        return Path(normalized_path).stem

    @staticmethod
    def tesseract_to_cube_stem(tesseract_stem: str) -> Optional[str]:
        """
        Convert tesseract filename to cube filename.

        Preserves leading zeros from the numeric part to match actual filesystem names.

        Examples:
          "tesseract_00108" → "cube_00108"
          "tesseract_00234" → "cube_00234"
          "tesseract_100"   → "cube_100"
        """
        match = RadarFileMapper.FILENAME_PATTERN.match(tesseract_stem)
        if not match:
            return None
        _, number = match.groups()

        # Preserve leading zeros — files on disk are cube_00108.mat, not cube_108.mat
        return f"cube_{number}"

    def build_radar_cache(self, radar_dir: Path) -> Dict[str, Path]:
        """Build lookup cache for a specific sequence's radar folder."""
        if not radar_dir.exists():
            raise FileNotFoundError(f"radar_zyx_cube not found: {radar_dir}")

        mat_files = list(radar_dir.glob("*.mat"))
        if not mat_files:
            raise FileNotFoundError(f"No .mat files in {radar_dir}")

        cache = {}
        for fpath in mat_files:
            cache[fpath.stem] = fpath

        return cache

    def process_sheet(
        self, sheet_name: str, df: pd.DataFrame, sequence_dir: Path
    ) -> dict:
        """
        Process one sheet against its specific sequence folder.
        """
        radar_dir = sequence_dir / "radar_zyx_cube"

        result = {
            "sheet_name": sheet_name,
            "sequence_dir": str(sequence_dir),
            "radar_dir": str(radar_dir),
            "total_rows": len(df),
            "rows_with_tesseract": 0,
            "matched_files": [],
            "unmatched_entries": [],
            "details": [],
        }

        # Build cache for THIS sequence's radar folder
        try:
            radar_cache = self.build_radar_cache(radar_dir)
        except FileNotFoundError as e:
            result["error"] = str(e)
            return result

        print(f"    [CACHE] {len(radar_cache)} radar files in {radar_dir}")

        for idx, row in df.iterrows():
            raw_tesseract = row.get("f_address_tesseract")

            if pd.isna(raw_tesseract):
                continue

            result["rows_with_tesseract"] += 1

            norm_path = self.normalize_unc_path(raw_tesseract)
            tess_stem = self.extract_stem(norm_path)

            if tess_stem is None:
                result["unmatched_entries"].append(
                    {"row": idx, "raw": raw_tesseract, "reason": "invalid_path"}
                )
                continue

            expected_cube = self.tesseract_to_cube_stem(tess_stem)
            if expected_cube is None:
                result["unmatched_entries"].append(
                    {
                        "row": idx,
                        "tesseract_stem": tess_stem,
                        "reason": "pattern_mismatch",
                    }
                )
                continue

            matched_path = radar_cache.get(expected_cube)

            entry = {
                "row": idx,
                "tesseract_raw": raw_tesseract,
                "tesseract_stem": tess_stem,
                "expected_cube": expected_cube,
                "matched": matched_path is not None,
            }
            result["details"].append(entry)

            if matched_path:
                result["matched_files"].append(
                    {
                        "stem": expected_cube,
                        "filename": matched_path.name,
                        "full_path": str(matched_path),
                    }
                )
            else:
                result["unmatched_entries"].append(
                    {
                        "row": idx,
                        "tesseract_stem": tess_stem,
                        "expected_cube": expected_cube,
                        "reason": "not_found",
                    }
                )

        # Deduplicate
        seen = set()
        unique = []
        for f in result["matched_files"]:
            if f["stem"] not in seen:
                seen.add(f["stem"])
                unique.append(f)
        result["matched_files"] = unique

        result["unique_match_count"] = len(unique)
        result["unique_unmatched_count"] = len(
            [u for u in result["unmatched_entries"] if u.get("reason") == "not_found"]
        )

        return result

    def process_all_sheets(self) -> "RadarFileMapper":
        """Process all sheets, each against its own sequence folder."""
        xl = pd.ExcelFile(self.xlsx_path)
        sheet_names = xl.sheet_names

        print(f"[EXCEL] {len(sheet_names)} sheets")
        print(f"[DATASET] Root: {self.dataset_root}")
        print(f"[OUTPUT] Dir: {self.output_dir}")

        for sheet_name in sheet_names:
            # Map sheet name to sequence folder
            sequence_dir = self.dataset_root / str(sheet_name)

            print(f"\n[PROCESSING] Sheet '{sheet_name}' → {sequence_dir}")

            if not sequence_dir.exists():
                print(f"  [SKIP] Sequence folder not found: {sequence_dir}")
                self.mappings[sheet_name] = {
                    "error": "sequence_folder_missing",
                    "expected_path": str(sequence_dir),
                }
                continue

            df = pd.read_excel(xl, sheet_name=sheet_name)

            if "f_address_tesseract" not in df.columns:
                print("  [SKIP] Missing f_address_tesseract column")
                self.mappings[sheet_name] = {
                    "error": "missing_tesseract_column",
                    "columns": list(df.columns),
                }
                continue

            sheet_result = self.process_sheet(sheet_name, df, sequence_dir)
            self.mappings[sheet_name] = sheet_result

            total = sheet_result.get("rows_with_tesseract", 0)
            matched = sheet_result.get("unique_match_count", 0)
            unmatched = sheet_result.get("unique_unmatched_count", 0)

            if total > 0:
                print(
                    f"  Rows: {total} | Matched: {matched} | Unmatched: {unmatched} | Rate: {matched/total*100:.1f}%"
                )
            else:
                print("  No tesseract rows found")

        return self

    def export_manifest(self, output_file: str = "radar_sync_manifest.json") -> dict:
        """
        Export per-sequence manifest for rsync.

        FIX #2: Write to self.output_dir, not current working directory
        """
        rsync_batches = {}

        for sheet_name, data in self.mappings.items():
            if "error" in data:
                continue

            files = [f["filename"] for f in data.get("matched_files", [])]
            if files:
                rsync_batches[sheet_name] = {
                    "file_count": len(files),
                    "files": sorted(files),
                    "source_dir": data.get("radar_dir", ""),
                    "sequence_dir": data.get("sequence_dir", ""),
                }

        manifest = {
            "metadata": {
                "xlsx_file": str(self.xlsx_path),
                "dataset_root": str(self.dataset_root),
                "total_sheets": len(self.mappings),
                "total_matched_files": sum(
                    b["file_count"] for b in rsync_batches.values()
                ),
            },
            "rsync_batches": rsync_batches,
            "full_mappings": self.mappings,
        }

        # FIX #2: Use self.output_dir instead of current directory
        output_path = self.output_dir / output_file
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\n[EXPORT] Manifest: {output_path}")
        print(f"  Sheets with matches: {len(rsync_batches)}")
        print(f"  Total files to sync: {manifest['metadata']['total_matched_files']}")
        return manifest


# ═════════════════════════════════════════════════════════════════════
# SMOKE TESTS
# ═════════════════════════════════════════════════════════════════════


def smoke_test_multi_sequence():
    """Test that sheet N maps to folder N."""
    import tempfile
    import openpyxl

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        output_dir = root / "output"

        # Create 3 sequence folders
        for seq in ["1", "2", "3"]:
            seq_dir = root / seq
            radar_dir = seq_dir / "radar_zyx_cube"
            radar_dir.mkdir(parents=True)

            # Each has different cube files (NO LEADING ZEROS)
            (radar_dir / "cube_1.mat").touch()
            (radar_dir / "cube_2.mat").touch()

        # Create Excel with 3 sheets
        wb = openpyxl.Workbook()
        for seq in ["1", "2", "3"]:
            if seq == "1":
                ws = wb.active
                ws.title = seq
            else:
                ws = wb.create_sheet(seq)

            ws.append(["f_address_tesseract"])
            # Row that matches THIS sequence (cube_1 in seq 1, cube_2 in seq 2, etc.)
            ws.append([rf"\\{seq}\radar_tesseract\tesseract_00{seq}.mat"])
            # Row that does NOT match this sequence
            ws.append([rf"\\{seq}\radar_tesseract\tesseract_00201.mat"])

        xlsx_path = root / "labels.xlsx"
        wb.save(xlsx_path)

        # Run mapper with output_dir
        mapper = RadarFileMapper(str(xlsx_path), str(root), str(output_dir))
        mapper.process_all_sheets()

        # Sheet 1 should match cube_001
        s1 = mapper.mappings["1"]
        assert (
            s1["unique_match_count"] == 1
        ), f"Sheet 1: expected 1 match, got {s1['unique_match_count']}"
        matched_names = [f["filename"] for f in s1["matched_files"]]
        assert (
            "cube_001.mat" in matched_names
        ), f"Sheet 1: expected cube_001.mat, got {matched_names}"

        # Sheet 2 should match cube_002
        s2 = mapper.mappings["2"]
        assert (
            s2["unique_match_count"] == 1
        ), f"Sheet 2: expected 1 match, got {s2['unique_match_count']}"
        matched_names = [f["filename"] for f in s2["matched_files"]]
        assert (
            "cube_002.mat" in matched_names
        ), f"Sheet 2: expected cube_002.mat, got {matched_names}"

        # Verify manifest was written to output_dir
        manifest_path = output_dir / "radar_sync_manifest.json"
        assert manifest_path.exists(), f"Manifest not found at {manifest_path}"

        print("✓ SMOKE TEST PASSED: Leading zeros preserved, output_dir respected")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING SMOKE TEST")
    print("=" * 60)
    smoke_test_multi_sequence()
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)

    # Production:
    # mapper = RadarFileMapper(
    #     "labels.xlsx",
    #     "/mnt/expansion/k-radar",
    #     "/home/adhish/k-radar-workflow/manifests"
    # )
    # mapper.process_all_sheets().export_manifest()
