"""LiDAR-relabeled CRI table. Reuses compute_cri from compute_robustness.py
unmodified (see that function's docstring for the RoHOI Eq.2 formula and the
"requires >=2 severity tiers, else returns None" rule) rather than
reimplementing it -- consistent with how Results.tex's tab:cri_results was
computed. lidar_gaussian_noise has only one surviving tier (high, relabeled
from low) in this dataset, so compute_cri returns None for it and it is
dropped from the table, exactly like loss_complete_zero already is for all
three modalities in the live thesis table.

Per-condition mAP is recomputed from summary_full_density_lidar_relabel.
parquet the same way generate_metrics_table_relabel.py does (pooled over
both diversity-axis strata, weighted by num_gt).

Run: uv run --project test-bed python docs/crossproduct_figures/lidar_relabel/generate_cri_relabel.py
"""

import sys
from pathlib import Path

import polars as pl

REPO_ROOT = Path("/home/adhish/Productivity/AMSCUP")
sys.path.insert(0, str(REPO_ROOT / "repos/K-Radar/scripts/alvis"))
from compute_robustness import compute_cri  # noqa: E402

BASE = REPO_ROOT / "repos/K-Radar/outputs/robustness_reports/crossproduct_v2"
OUT = REPO_ROOT / "docs/crossproduct_figures/lidar_relabel"
OUT.mkdir(parents=True, exist_ok=True)

df = pl.read_parquet(BASE / "summary_full_density_lidar_relabel.parquet")

agg = df.group_by(["condition", "cls"]).agg(
    (pl.col("ap_restricted_range") * pl.col("num_gt")).sum().alias("_ap_w"),
    pl.col("num_gt").sum().alias("_gt_w"),
)
agg = agg.with_columns((pl.col("_ap_w") / pl.col("_gt_w")).alias("mAP"))


def ap_by_severity(modality: str, effect: str, cls: str) -> dict[str, float]:
    out = {}
    for sev in ("low", "medium", "high"):
        row = agg.filter((pl.col("condition") == f"{modality}_{effect}_{sev}") & (pl.col("cls") == cls))
        if row.height:
            out[sev] = row["mAP"][0]
    return out


EFFECTS = [
    ("camera", "loss_partial"), ("camera", "gaussian_noise"),
    ("lidar", "loss_partial"), ("radar", "loss_partial"),
    ("radar", "gaussian_noise"), ("lidar", "gaussian_noise"),
]

rows = []
for modality, effect in EFFECTS:
    row = {"effect": f"{modality}_{effect}"}
    for cls, key in (("sed", "cri_sed"), ("bus", "cri_bus")):
        clean_ap = agg.filter((pl.col("condition") == "original") & (pl.col("cls") == cls))["mAP"][0]
        cri = compute_cri(ap_by_severity(modality, effect, cls), clean_ap)
        row[key] = cri
    rows.append(row)

print(f"{'effect':<24} {'CRI (sedan)':>12} {'CRI (bus/truck)':>16}")
tex_lines = []
for row in rows:
    sed = "n/a (1 tier)" if row["cri_sed"] is None else f"{row['cri_sed']:.3f}"
    bus = "n/a (1 tier)" if row["cri_bus"] is None else f"{row['cri_bus']:.3f}"
    print(f"{row['effect']:<24} {sed:>12} {bus:>16}")
    if row["cri_sed"] is not None:
        tex_lines.append(
            r"\texttt{" + row["effect"].replace("_", r"\_") + "} & "
            f"{row['cri_sed']:.3f} & {row['cri_bus']:.3f} \\\\"
        )

(OUT / "cri_table_rows.tex").write_text("\n".join(tex_lines) + "\n")
print("\nexcluded (single tier):", [r["effect"] for r in rows if r["cri_sed"] is None])
print("saved ->", OUT / "cri_table_rows.tex")
