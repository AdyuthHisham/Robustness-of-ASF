# AMSCUP

A comprehensive research repository for autonomous vehicle perception development, focusing on multi-sensor fusion (camera, LiDAR, and 4D radar) and robust object detection across various weather conditions.

## Overview

AMSCUP serves as a development platform and testbed for evaluating and integrating autonomous vehicle (AV) sensor fusion pipelines. The project emphasizes working with multi-modal autonomous driving datasets (Waymo, nuScenes, K-Radar) and state-of-the-art object detection models to build robust perception systems that perform consistently across diverse environmental conditions.

## Project Purpose

This repository consolidates:
- **Data pipeline development**: Integration and preprocessing of multiple autonomous vehicle datasets
- **Model evaluation**: Testing state-of-the-art scene flow (SF) and 3D object detection models
- **Sensor fusion research**: Camera, LiDAR, and 4D radar integration for improved detection robustness
- **Testbed infrastructure**: Local and distributed testing environments for algorithm validation

## Key Features

- **Multi-dataset support**: Waymo, nuScenes, K-Radar, and NVIDIA autonomous driving datasets
- **Sensor fusion pipelines**: Integration of camera, LiDAR, and 4D radar data
- **4D Radar object detection**: Full support for K-Radar's RAED (Range–Azimuth–Elevation–Doppler) tensor data
- **Scene flow model evaluation**: Testing and validation of SF models on multiple datasets
- **Docker containerization**: Pre-configured environments for K-Radar and other models
- **Robust testing modules**: Modules for evaluating system behavior under degraded sensor conditions and adverse weather

## Directory Structure

```
AMSCUP/
├── test-bed/                          # Main development testbed
│   ├── src/
│   │   ├── Modules/
│   │   │   └── robust_testing/        # Robustness evaluation modules
│   │   │       ├── Dataset_Module.ipynb  # Dataset loading and exploration
│   │   │       ├── nuscenes/          # nuScenes dataset integration
│   │   │       ├── kradar/            # K-Radar dataset integration
│   │   │       └── example/           # Example scripts and configurations
│   │   ├── SFModels/                  # Scene flow models (ignored in git)
│   │   │   └── CenterPoint/           # CenterPoint detection model with Docker
│   │   └── Datasets/                  # Local dataset storage (ignored in git)
│   ├── main.py                        # Testbed entry point
│   ├── pyproject.toml                 # Python project configuration with dependencies
│   ├── uv.lock                        # Dependency lock file (uv package manager)
│   └── .python-version                # Python version specification (3.12)
├── repos/                             # Third-party repositories and integrations
│   ├── K-Radar/                       # K-Radar dataset & benchmark implementation
│   │   ├── configs/                   # Model configurations
│   │   ├── models/                    # Detection and segmentation models
│   │   ├── pipelines/                 # Data processing and training pipelines
│   │   ├── utils/                     # Utility functions and evaluation tools
│   │   ├── scripts/                   # Processing and evaluation scripts
│   │   ├── Dockerfile                 # Docker image for K-Radar environment
│   │   ├── docker-compose.yml         # Docker compose configuration
│   │   ├── requirements.txt           # Python dependencies
│   │   └── readme.md                  # K-Radar specific documentation
│   └── .gitignore                     # Third-party repo ignore patterns
├── tools/                             # Utility tools and helper scripts
│   └── data_transfer_kradar/          # K-Radar data transfer utilities
├── groupL/                            # Group learning materials
│   ├── pdfs/                          # Academic papers and references
│   └── ppts/                          # Presentations and slides
├── obsidianVault/                     # Research notes and documentation vault
├── notes.txt                          # Development status and TODO items
└── .pre-commit-config.yaml            # Pre-commit hooks configuration
```

## Supported Datasets

### Dataset Comparison

| Dataset | Cameras | LiDAR | Radar | Time/Scene | Total Time | Scenes |
|---------|---------|-------|-------|-----------|-----------|--------|
| **Waymo** | 5 | 5 | — | 20s | 333 min | 1000 |
| **nuScenes** | 6 | 1 | 5 | 20s | 330 min | 1000 |
| **K-Radar** | Multiple | Yes | ✓ (4D) | — | — | — |

**K-Radar Uniqueness**: Provides complete 4D radar tensor data (full RAED dimensions) – a world-first for public autonomous driving datasets. Unlike most datasets that provide sparse point clouds, K-Radar offers raw 4D tensor representations for superior object detection performance.

## Installation

### Prerequisites

- **Python 3.10+** (verified with Python 3.12)
- **pip** or **uv** package manager (uv recommended for faster dependency resolution)
- **Git** (for cloning repositories)
- **Docker** (optional, for containerized environments)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AdyuthHisham/AMSCUP.git
   cd AMSCUP
   ```

2. **Navigate to testbed:**
   ```bash
   cd test-bed
   ```

3. **Install dependencies using uv (recommended):**
   ```bash
   uv sync
   ```
   
   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```
   
   For development dependencies:
   ```bash
   uv sync --all-groups
   ```

4. **Verify installation:**
   ```bash
   python main.py
   ```
   Expected output: `"Hello from test-bed!"`

## Dependencies

### Core Dependencies

- **hdbscan** (≥0.8.42) – Hierarchical density-based clustering
- **marimo** (≥0.20.4) – Interactive notebooks and reactive programming
- **numpy** (<2.0.0) – Numerical computing
- **nuscenes-devkit** (≥1.2.0) �� nuScenes dataset SDK
- **pandas** (≥2.3.3) – Data manipulation
- **polars** (≥1.39.3) – High-performance data frames
- **pyarrow** (≥23.0.1) – Arrow data format support
- **sentence-transformers** (≥5.4.1) – Text embeddings and semantic search
- **umap-learn** (≥0.5.12) – Dimensionality reduction
- **visidata** (≥3.3) – Interactive data analysis
- **python-lsp-server** (≥1.14.0) – LSP for code editors
- **ruff** (≥0.15.5) – Fast Python linter

### K-Radar Dependencies

- **open3d** (0.15.1) – 3D data processing
- **torch** with **spconv-cu113** – PyTorch with sparse convolution (CUDA 11.3)
- **opencv-python** (4.2.0.32) – Computer vision
- **tensorboard** – Training visualization
- **PyQt5** – GUI framework
- **scikit-image** – Image processing
- **numba** – JIT compilation for performance
- **einops** – Tensor operations

### Development Dependencies

- **basedpyright** (≥1.38.2) – Static type checker
- **ipykernel** (≥7.2.0) – Jupyter notebook kernel
- **pre-commit** (≥4.5.1) – Git hooks framework
- **uv** (≥0.10.7) – Fast Python package manager

## Usage

### Quick Start

1. **Run the testbed:**
   ```bash
   cd test-bed
   python main.py
   ```

2. **Launch interactive notebooks:**
   ```bash
   # Dataset exploration module
   jupyter notebook src/Modules/robust_testing/Dataset_Module.ipynb
   ```

### Working with Datasets

#### Load nuScenes Dataset
```python
from nuscenes import NuScenes

nusc = NuScenes(version='v1.0-mini', dataroot='/path/to/nuscenes')
# Explore scenes and sensor data
```

#### Load K-Radar Dataset
Navigate to `repos/K-Radar` for dataset-specific code:
```bash
cd repos/K-Radar
python test.py  # Run diagnostic tests
```

### K-Radar Setup

#### Using Docker

1. **Build the Docker image:**
   ```bash
   cd repos/K-Radar
   docker build -f Dockerfile -t kradar:latest .
   ```

2. **Run using Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the container:**
   ```bash
   docker-compose exec kradar bash
   ```

#### Manual Installation (K-Radar)

```bash
cd repos/K-Radar
pip install -r requirements.txt
```

### Model Evaluation

The testbed includes integration with multiple state-of-the-art models:

- **CenterPoint**: 3D object detection model (Docker support provided)
- **Scene Flow Models**: Multiple SF models for motion estimation
- **K-Radar Detection Pipelines**: 4D radar-specific detection models

### Running Model Inference

#### K-Radar 4D Radar Detection
```bash
cd repos/K-Radar
python models/inference.py --config configs/detector.yaml --checkpoint model.pth
```

#### Sensor Fusion Pipeline
Refer to `repos/K-Radar/pipelines/` for sensor fusion integration examples.

## Project Structure Details

### Test-Bed (`test-bed/`)

**Purpose**: Isolated development and testing environment for algorithm validation.

**Key Components**:
- **Dataset_Module.ipynb**: Interactive notebook for dataset loading, exploration, and visualization
- **Robust Testing Modules**: Performance evaluation under adverse conditions
- **pyproject.toml**: Centralized dependency management with uv

### K-Radar Repository (`repos/K-Radar/`)

**Purpose**: Official K-Radar dataset implementation and benchmark models.

**Structure**:
- **models/**: Neural network architectures for detection and segmentation
- **pipelines/**: Data loading, preprocessing, and training pipelines
- **utils/**: Helper functions for data processing and evaluation
- **configs/**: Configuration files for model training
- **docs/**: Dataset documentation and pipeline guides
- **scripts/**: Utility scripts for data processing and analysis

### Tools (`tools/`)

**Purpose**: Utility scripts for dataset manipulation and transfer.

- **data_transfer_kradar/**: Scripts for downloading and transferring K-Radar data

## Configuration

### Python Version

Specified in `test-bed/.python-version`:
```
3.12
```

### Development Tools

#### Pre-commit Hooks
Configuration in `.pre-commit-config.yaml`:
```bash
pre-commit install
pre-commit run --all-files
```

#### Code Formatting
```bash
cd test-bed
uv run black .  # Format code with black
uv run ruff check .  # Lint with ruff
```

## Important Notes

### Current Development Status

As noted in `notes.txt`:
- Docker containerization for CenterPoint is in progress
- Training capability on local devices is limited due to computational requirements
- Full model training recommended on cluster environment
- Data manipulation and sensor calibration are ongoing work areas

### Key Uncertainties

1. **Group Storage**: Documentation needed for group storage access patterns
2. **Full Dataset Integration**: Some dataset features not yet fully integrated
3. **Autocalibration**: Sensor extrinsic calibration tools are under development
4. **Cluster Deployment**: Timeline for full cluster testbed support is in progress

## Dependencies Management

### Using `uv` (Recommended)

```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update lock file
uv sync --refresh
```

### Using pip

```bash
# Standard installation
pip install -e .

# With development dependencies
pip install -e ".[dev]"

# Or from requirements
pip install -r requirements.txt
```

## Troubleshooting

### CUDA/GPU Issues (K-Radar)

The `repos/K-Radar/test.py` provides diagnostic utilities for GPU/CUDA configuration:
```bash
python test.py  # Diagnose libcuda, PTX compiler, and Numba GPU access
```

### Missing Dependencies

If encountering import errors:
```bash
cd test-bed
uv sync --refresh  # Refresh all dependencies
```

### Dataset Access

Datasets are ignored in git (see `.gitignore`). Ensure datasets are placed in:
- `test-bed/src/Datasets/` for local testing
- Refer to dataset documentation for download links

## Related Resources

- **K-Radar Paper**: [arXiv:2206.08171](https://arxiv.org/abs/2206.08171)
- **4D Radar Detection Network**: [arXiv:2303.06342](https://arxiv.org/abs/2303.06342)
- **K-Radar Repository**: [KAIST AVELab K-Radar](https://github.com/kaist-avelab/K-Radar_auto-labeling)
- **nuScenes Dataset**: [nuScenes Official](https://www.nuscenes.org/)
- **Waymo Open Dataset**: [Waymo Official](https://waymo.com/open/)

## Contributing

For development work:

1. Create a feature branch
2. Make changes and run pre-commit hooks
3. Test thoroughly in the testbed environment
4. Submit pull request with detailed description

## License

*To be specified by repository owner*

---

## Quick Reference Commands

```bash
# Setup
cd test-bed && uv sync

# Run testbed
python main.py

# Format code
uv run black .

# Lint code
uv run ruff check .

# Run diagnostics (K-Radar)
cd repos/K-Radar && python test.py

# Build Docker image (K-Radar)
docker build -f Dockerfile -t kradar:latest .
```
