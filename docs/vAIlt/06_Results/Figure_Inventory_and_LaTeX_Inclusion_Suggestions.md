---
title: Figure Inventory and LaTeX Inclusion Suggestions
type: concept
source: home/adhish/Productivity/AMSCUP/docs/Latex_Report/figure_inventory.md
date: 2026-07-02
tags: [06 Results]
---
# Figure Inventory and LaTeX Inclusion Suggestions

## Images Available in Obsidian Vault (`/home/adhish/Productivity/AMSCUP/obsidianVault/Images/`)

### Sensor/Dataset Visualizations
| Filename | Description | Suggested Chapter | LaTeX Code |
|---|---|---|---|
| `Pasted image 20260211134012.png` | Sensor comparison table (LiDAR/Radar/Camera specs) | Theory / Introduction | `\includegraphics[width=0.9\linewidth]{figure/sensor_comparison.png}` |
| `Pasted image 20260211135031.png` | Fusion types diagram (data/feature/decision level) | Theory | `\includegraphics[width=0.9\linewidth]{figure/fusion_types.png}` |
| `Pasted image 20260211131611.png` | Fusion algorithms overview | Theory | `\includegraphics[width=0.9\linewidth]{figure/fusion_algorithms.png}` |
| `Pasted image 20260211134634.png` | Fusion architecture diagram | Theory | `\includegraphics[width=0.9\linewidth]{figure/fusion_architecture.png}` |
| `Pasted image 20260211140836.png` | Fusion architecture detailed | Theory | `\includegraphics[width=0.9\linewidth]{figure/fusion_architecture_detailed.png}` |
| `Pasted image 20260211141910.png` | Early fusion diagram | Theory | `\includegraphics[width=0.45\linewidth]{figure/early_fusion.png}` |
| `Pasted image 20260211141928.png` | Mid-level fusion diagram | Theory | `\includegraphics[width=0.45\linewidth]{figure/mid_fusion.png}` |
| `Pasted image 20260211142104.png` | Late fusion diagram | Theory | `\includegraphics[width=0.45\linewidth]{figure/late_fusion.png}` |
| `Pasted image 20260211142110.png` | Hybrid fusion diagram | Theory | `\includegraphics[width=0.45\linewidth]{figure/hybrid_fusion.png}` |

### Weather/Adverse Conditions
| Filename | Description | Suggested Chapter | LaTeX Code |
|---|---|---|---|
| `Pasted image 20260303153441.png` | Weather effects on sensors table | Theory / Results | `\includegraphics[width=0.9\linewidth]{figure/weather_effects.png}` |
| `Pasted image 20260303160943.png` | Adverse weather dataset comparison | Theory / Results | `\includegraphics[width=0.9\linewidth]{figure/adverse_weather_datasets.png}` |
| `screenshot-2026-02-09-163152.png` | LiDAR/Radar-Camera comparison | Theory | `\includegraphics[width=0.9\linewidth]{figure/lidar_radar_camera_comparison.png}` |
| `screenshot-2026-02-11-114027.png` | Sensor theory table | Theory | `\includegraphics[width=0.9\linewidth]{figure/sensor_theory_table.png}` |
| `screenshot-2026-02-11-121219.png` | Fusion types illustration | Theory | `\includegraphics[width=0.9\linewidth]{figure/fusion_types_illustration.png}` |

### Calibration/Methodology
| Filename | Description | Suggested Chapter | LaTeX Code |
|---|---|---|---|
| `Pasted image 20260504133839.png` | Calibration pipeline / methodology | Methods | `\includegraphics[width=0.9\linewidth]{figure/calibration_pipeline.png}` |
| `Pasted image 20260504133918.png` | Sensor setup / experimental config | Methods / Results | `\includegraphics[width=0.9\linewidth]{figure/experimental_setup.png}` |

### Excalidraw Diagrams
| Filename | Description | Suggested Chapter | LaTeX Code |
|---|---|---|---|
| `Excalidraw/Drawing 2026-04-13 14.45.35.excalidraw.md` | NuScenes vs K-Radar sensor diagram | Introduction / Methods | Convert to PDF/PNG first, then include |

### Photos
| Filename | Description | Suggested Chapter | LaTeX Code |
|---|---|---|---|
| `IMG_20260220_163239570_AE.jpg` | Planning report / whiteboard photo | Introduction / Appendix | `\includegraphics[width=0.7\linewidth]{figure/planning_whiteboard.jpg}` |
| `IMG_20260223_162122895_AE.jpg` | Planning report / whiteboard photo | Introduction / Appendix | `\includegraphics[width=0.7\linewidth]{figure/planning_whiteboard2.jpg}` |

## Images Already in LaTeX Report (`/home/adhish/Productivity/AMSCUP/docs/Latex_Report/`)

### Thesis Report Figures
| Path | Description | Status |
|---|---|---|
| `thesis_report/figure/X.pdf` | Surface/contour plot example (template) | Template - replace |
| `thesis_report/figure/Y.pdf` | Surface/contour plot example (template) | Template - replace |
| `thesis_report/figure/Z.pdf` | Surface/contour plot example (template) | Template - replace |
| `thesis_report/figure/Wind.png` | Wind visualization (template) | Template - replace |
| `thesis_report/figure/auxiliary/` | Chalmers logos (EPS/PDF) | Keep for title page |

### Planning Report Images
| Path | Description | Status |
|---|---|---|
| `images/basic_sensors.png` | Sensor comparison diagram | Use in Introduction |
| `images/basic_datasets.png` | Dataset sensor configurations | Use in Introduction/Methods |

## Figures to Generate (Not Yet Available)

### System Architecture Diagrams (Need Creation)
| Figure | Description | Chapter | Priority |
|---|---|---|---|
| `figure/system_architecture.pdf` | Overall pipeline: sensors → sync → preprocess → feature extract → fusion → detection → tracking | Methods | High |
| `figure/fusion_pipeline.pdf` | Availability-aware fusion detail: reliability estimation → weight computation → feature fusion | Methods | High |
| `figure/calibration_pipeline.pdf` | Two-stage calibration: target-based init → online ego-motion refinement | Methods | Medium |

### Results Figures (Need Generation from Data)
| Figure | Description | Chapter | Priority |
|---|---|---|---|
| `figure/kradar_weather_mAP.pdf` | Bar chart: mAP across weather conditions (Clear, Overcast, Fog, Rain, Sleet, Light Snow, Heavy Snow, Night) | Results | High |
| `figure/ablation_nuscenes.pdf` | Waterfall chart: cumulative NDS improvement from ablations | Results | High |
| `figure/noise_sensitivity.pdf` | Line plot: NDS vs noise level for each modality + proposed | Results | Medium |
| `figure/qualitative.pdf` | 2x2 grid: detection results in Clear, Fog, Rain, Night | Results | High |
| `figure/availability_weights.pdf` | Stacked bar: modality weights across conditions | Results/Discussion | Medium |

### Theory Figures (Can Use Obsidian Images)
| Figure | Source | Chapter |
|---|---|---|
| `figure/sensor_principles.pdf` | `Pasted image 20260211134012.png` | Theory |
| `figure/calibration_taxonomy.pdf` | Combine from Li et al. / Lyu et al. tables | Theory |
| `figure/fusion_levels.pdf` | `Pasted image 20260211135031.png` | Theory |
| `figure/adverse_weather_effects.pdf` | `Pasted image 20260303153441.png` | Theory |

## LaTeX Figure Inclusion Template

```latex
\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\linewidth]{figure/filename.pdf}
    \caption{Descriptive caption explaining what the figure shows and its relevance.}
    \label{fig:label_for_referencing}
\end{figure}
```

For side-by-side figures:
```latex
\begin{figure}[H]
    \centering
    \begin{subfigure}{0.45\linewidth}
        \includegraphics[width=\linewidth]{figure/fig1.pdf}
        \caption{Subcaption A}
        \label{fig:sub_a}
    \end{subfigure}
    \hfill
    \begin{subfigure}{0.45\linewidth}
        \includegraphics[width=\linewidth]{figure/fig2.pdf}
        \caption{Subcaption B}
        \label{fig:sub_b}
    \end{subfigure}
    \caption{Overall caption}
    \label{fig:combined}
\end{figure}
```

## Action Items

1. **Copy Obsidian images to thesis report figure directory**:
   ```bash
   cp /home/adhish/Productivity/AMSCUP/obsidianVault/Images/*.png /home/adhish/Productivity/AMSCUP/docs/Latex_Report/thesis_report/figure/
   cp /home/adhish/Productivity/AMSCUP/obsidianVault/Images/*.jpg /home/adhish/Productivity/AMSCUP/docs/Latex_Report/thesis_report/figure/
   ```

2. **Convert Excalidraw to PDF/PNG**:
   - Open in Obsidian with Excalidraw plugin
   - Export as PNG/PDF
   - Save to figure directory

3. **Generate missing figures from experimental data** (Python/Matplotlib)

4. **Replace template figures** (X.pdf, Y.pdf, Z.pdf, Wind.png) with actual content

5. **Update all figure references** in .tex files to match actual filenames