#!/usr/bin/env python3
"""
quick_check.py — One-off diagnostic for your actual data
Run this first to verify the mapping works before full pipeline.
"""

from pathlib import Path
import pandas as pd

# CONFIGURE THESE PATHS
XLSX_FILE = "/home/adhish/Downloads/sync_files_list_and_analysis_12345.xlsx"
BASE_DIR = "/mnt/expansion/k-radar/1"  # Your actual path


def main():
    radar_dir = Path(BASE_DIR) / "radar_zyx_cube"

    # 1. Show what radar files actually exist
    print("=" * 50)
    print("ACTUAL RADAR FILES")
    print("=" * 50)
    radar_files = sorted(radar_dir.glob("*.mat"))
    print(f"Total: {len(radar_files)}")
    print(f"First 10: {[f.name for f in radar_files[:10]]}")
    print(f"Last 10:  {[f.name for f in radar_files[-10:]]}")

    # 2. Read Excel and show tesseract references
    print("\n" + "=" * 50)
    print("EXCEL TESSERACT REFERENCES")
    print("=" * 50)
    xl = pd.ExcelFile(XLSX_FILE)
    print(f"Sheets: {xl.sheet_names}")

    df = pd.read_excel(xl, sheet_name=xl.sheet_names[0])
    print(f"\nSheet '{xl.sheet_names[0]}' columns: {list(df.columns)}")
    print("\nFirst 5 tesseract paths:")
    for i, path in enumerate(df["f_address_tesseract"].head(5)):
        print(f"  Row {i}: {path}")

    # 3. Test the conversion
    print("\n" + "=" * 50)
    print("CONVERSION TEST")
    print("=" * 50)

    sample_tesseract = df["f_address_tesseract"].iloc[0]
    # Extract stem and convert
    stem = Path(str(sample_tesseract).replace("\\", "/")).stem
    expected_cube = stem.replace("tesseract", "cube")

    print(f"Sample tesseract: {sample_tesseract}")
    print(f"Extracted stem:   {stem}")
    print(f"Expected cube:    {expected_cube}")

    # Check if it exists
    expected_path = radar_dir / f"{expected_cube}.mat"
    print(f"File exists:      {expected_path.exists()}")

    if expected_path.exists():
        print("\n✓ CONVERSION WORKS! Your data uses tesseract → cube mapping.")
    else:
        print("\n✗ CONVERSION FAILED")
        print(f"  Looked for: {expected_path}")
        print("  Try finding the actual file with same number:")

        # Try to find by number
        import re

        match = re.search(r"(\d+)", stem)
        if match:
            number = match.group(1)
            matches = list(radar_dir.glob(f"*_{number}.mat"))
            if matches:
                print(f"  Found by number: {matches[0].name}")
                print(
                    f"  Your prefix map should be: tesseract → {matches[0].stem.split('_')[0]}"
                )
            else:
                print(f"  No file with number {number} found in radar_zyx_cube")


if __name__ == "__main__":
    main()
