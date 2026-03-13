# ------------------------------
# Dockerfile for CenterPoint / det3d sensor fusion
# GPU-dependent extensions will be built inside container
# ------------------------------

# Use official NVIDIA CUDA base image with Python 3.7
FROM nvidia/cuda:11.1.1-cudnn8-devel-ubuntu18.04

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    curl \
    cmake \
    ca-certificates \
    python3.7 \
    python3.7-dev \
    python3-pip \
    libboost-all-dev \
    libgl1 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3.7 -m pip install --upgrade pip

# Set python3.7 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Install PyTorch and torchvision (compatible with CUDA 11.1)
RUN pip install torch==1.10.1+cu111 torchvision==0.11.2+cu111 -f https://download.pytorch.org/whl/torch_stable.html

# Clone CenterPoint repository
WORKDIR /workspace
RUN git clone https://github.com/tianweiy/CenterPoint.git
WORKDIR /workspace/CenterPoint

# Install Python dependencies
RUN pip install -r requirements.txt

# Set PYTHONPATH for CenterPoint
ENV PYTHONPATH="${PYTHONPATH}:/workspace/CenterPoint"

# Clone nuScenes devkit and set PYTHONPATH
RUN git clone https://github.com/tianweiy/nuscenes-devkit.git /workspace/nuscenes-devkit
ENV PYTHONPATH="${PYTHONPATH}:/workspace/nuscenes-devkit/python-sdk"

# Skip CUDA extensions (iou3d_nms and DCN) at build time

# Optional: Install NVIDIA APEX
#RUN git clone https://github.com/NVIDIA/apex.git /workspace/apex
#WORKDIR /workspace/apex
#RUN git checkout 5633f6
#RUN pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./

# Clone and install spconv
RUN pip install --upgrade pip setuptools wheel
RUN pip install spconv-cu111
#WORKDIR /workspace
#RUN git clone https://github.com/traveller59/spconv.git --recursive
#WORKDIR /workspace/spconv
#RUN git checkout 7342772
#RUN python setup.py bdist_wheel
#RUN pip install ./dist/*.whl


ENV LD_LIBRARY_PATH=/usr/local/lib/python3.7/dist-packages/torch/lib:$LD_LIBRARY_PATH

# Install Vim
RUN apt-get update && apt-get install -y vim && rm -rf /var/lib/apt/lists/*

# Set working directory for running training scripts
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]
