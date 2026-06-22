FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV UV_LINK_MODE=copy
ENV PATH="/root/.local/bin:$PATH"

# Install system dependencies — Ubuntu 22.04 ships Python 3.10 natively
RUN apt-get update && \
    apt-get install -y \
        curl \
        git \
        build-essential \
        cmake \
        python3 \
        python3-pip \
        python3-dev \
        python3-venv \
        libsparsehash-dev \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install CPU-only PyTorch
RUN uv pip install torch torchvision torchaudio --system \
    --index-url https://download.pytorch.org/whl/cpu

# Install build tools
RUN uv pip install setuptools wheel packaging --system

# Install marimo
RUN uv pip install marimo --system

WORKDIR /workspace

EXPOSE 2718

# Project + OpenPCDet installs run at container start since they need the mounted volume
CMD ["/bin/bash", "-c", "\
    rm -rf /workspace/test-bed/.venv && \
    if [ -f /workspace/test-bed/pyproject.toml ]; then \
        uv pip install -e /workspace/test-bed --system; \
    fi && \
    #if [ ! -d /workspace/repos/tools/OpenPCDet ]; then \
    #    git clone https://github.com/open-mmlab/OpenPCDet.git /workspace/repos/tools/OpenPCDet; \
    #fi && \
    #uv pip install -e /workspace/repos/tools/OpenPCDet --system --no-build-isolation && \
    marimo edit /workspace/test-bed/src/Modules/robust_testing --host 0.0.0.0 --port 2718 --no-token"]
