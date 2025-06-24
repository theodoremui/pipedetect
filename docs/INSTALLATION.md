# Installation Guide

This guide provides detailed instructions for installing PipeDetect on various platforms and environments.

## Prerequisites

### System Requirements

- **Python**: 3.12 or higher
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+, CentOS 7+)
- **Memory**: Minimum 4GB RAM (8GB+ recommended for video processing)
- **Storage**: At least 2GB free space for dependencies and models

### Hardware Recommendations

- **CPU**: Multi-core processor (4+ cores recommended)
- **GPU**: Optional but improves performance for video processing
- **Webcam**: For real-time pose detection (future feature)

## Installation Methods

### Method 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that provides better dependency resolution and faster installation.

#### Step 1: Install uv

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative installation methods:**
```bash
# Using pip
pip install uv

# Using pipx
pipx install uv

# Using Homebrew (macOS)
brew install uv

# Using conda
conda install -c conda-forge uv
```

#### Step 2: Clone and Install PipeDetect

```bash
# Clone the repository
git clone https://github.com/your-username/pipedetect.git
cd pipedetect

# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
# On Unix/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

#### Step 3: Verify Installation

```bash
# Test the installation
python detect.py --help

# Run a quick test (requires test data)
python detect.py --version
```

### Method 2: Using pip

If you prefer using pip or cannot install uv:

#### Step 1: Create Virtual Environment

```bash
# Clone the repository
git clone https://github.com/your-username/pipedetect.git
cd pipedetect

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Unix/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

#### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install PipeDetect in development mode
pip install -e .

# Or install specific dependencies
pip install -r requirements.txt  # If available
```

### Method 3: Using Poetry

If you're using Poetry for dependency management:

```bash
# Clone the repository
git clone https://github.com/your-username/pipedetect.git
cd pipedetect

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Method 4: Using conda/mamba

For conda/mamba users:

```bash
# Create conda environment
conda create -n pipedetect python=3.12
conda activate pipedetect

# Clone and install
git clone https://github.com/your-username/pipedetect.git
cd pipedetect
pip install -e .
```

## Platform-Specific Instructions

### Windows

#### Prerequisites
- Windows 10 or Windows 11
- Python 3.12+ from [python.org](https://python.org) or Microsoft Store
- Git for Windows (optional but recommended)

#### Visual C++ Redistributable
Some dependencies may require Visual C++ Redistributable:
```bash
# Download and install Visual C++ Redistributable from Microsoft
# Or install via winget:
winget install Microsoft.VCRedist.2015+.x64
```

#### Installation
```bash
# Using PowerShell or Command Prompt
git clone https://github.com/your-username/pipedetect.git
cd pipedetect

# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install PipeDetect
uv sync

# Activate environment
.venv\Scripts\activate
```

### macOS

#### Prerequisites
- macOS 10.15 (Catalina) or later
- Xcode Command Line Tools: `xcode-select --install`
- Homebrew (recommended): `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

#### Installation
```bash
# Install dependencies
brew install python@3.12 git

# Install uv
brew install uv

# Clone and install PipeDetect
git clone https://github.com/your-username/pipedetect.git
cd pipedetect
uv sync
source .venv/bin/activate
```

### Linux (Ubuntu/Debian)

#### Prerequisites
```bash
# Update package list
sudo apt update

# Install Python and development tools
sudo apt install python3.12 python3.12-venv python3.12-dev
sudo apt install git build-essential

# Install additional system dependencies
sudo apt install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
```

#### Installation
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal

# Clone and install PipeDetect
git clone https://github.com/your-username/pipedetect.git
cd pipedetect
uv sync
source .venv/bin/activate
```

### Linux (CentOS/RHEL/Fedora)

#### Prerequisites
```bash
# CentOS/RHEL
sudo yum update
sudo yum install python3.12 python3.12-devel git gcc gcc-c++
sudo yum install mesa-libGL glib2 libSM libXext libXrender

# Fedora
sudo dnf install python3.12 python3.12-devel git gcc gcc-c++
sudo dnf install mesa-libGL glib2 libSM libXext libXrender
```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.12 -m venv .venv
```

#### 2. MediaPipe Installation Fails
```bash
# Install system dependencies first (Linux)
sudo apt install libprotobuf-dev protobuf-compiler

# Try installing MediaPipe separately
pip install --upgrade pip
pip install mediapipe==0.10.21
```

#### 3. OpenCV Issues
```bash
# Linux: Install OpenCV system dependencies
sudo apt install libopencv-dev python3-opencv

# macOS: Use Homebrew
brew install opencv

# Windows: Usually works out of the box with pip installation
```

#### 4. Permission Issues
```bash
# Linux/macOS: Use user installation
pip install --user -e .

# Or fix permissions
sudo chown -R $USER:$USER .venv/
```

#### 5. SSL Certificate Issues
```bash
# Upgrade certificates
pip install --upgrade certifi

# Or use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org -e .
```

### Platform-Specific Issues

#### Windows
- **Long Path Names**: Enable long path support in Windows 10/11
- **Antivirus**: Exclude the project directory from real-time scanning
- **PowerShell Execution Policy**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

#### macOS
- **Xcode License**: Accept Xcode license with `sudo xcodebuild -license accept`
- **Homebrew Permissions**: Fix with `sudo chown -R $(whoami) $(brew --prefix)/*`

#### Linux
- **Missing Libraries**: Install development packages (`-dev` or `-devel`)
- **CUDA Support**: Install NVIDIA drivers and CUDA toolkit for GPU acceleration

## Development Installation

For contributors and developers:

```bash
# Clone with development extras
git clone https://github.com/your-username/pipedetect.git
cd pipedetect

# Install with development dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run tests to verify installation
uv run pytest
```

## Docker Installation

For containerized deployment:

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv and dependencies
RUN pip install uv
RUN uv sync

ENTRYPOINT ["uv", "run", "python", "detect.py"]
```

```bash
# Build and run
docker build -t pipedetect .
docker run -v $(pwd)/data:/app/data -v $(pwd)/outputs:/app/outputs pipedetect /app/data/video.mp4
```

## Verification

After installation, verify everything works:

```bash
# Activate environment
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows

# Check version and help
python detect.py --help

# Run basic tests
uv run pytest tests/test_core_models.py -v

# Test with sample data (if available)
python detect.py sample_data/test_image.jpg --output-dir test_output/
```

## Performance Optimization

### GPU Acceleration
MediaPipe can utilize GPU acceleration on supported systems:

```bash
# Check GPU support
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# For NVIDIA GPUs, install CUDA toolkit
# For AMD GPUs, install ROCm (limited support)
```

### Memory Optimization
For systems with limited memory:

```bash
# Use lighter model complexity
python detect.py video.mp4 --model-complexity 0

# Process smaller batches
python detect.py large_directory/ --no-frames --no-overlays
```

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Search existing [GitHub Issues](https://github.com/your-username/pipedetect/issues)
3. Create a new issue with:
   - Operating system and version
   - Python version
   - Installation method used
   - Complete error message
   - Steps to reproduce the issue

## Next Steps

After successful installation:

1. Read the [Usage Guide](USAGE.md)
2. Check out [Examples](../examples/)
3. Review [API Documentation](API.md)
4. Join the [Community Discussions](https://github.com/your-username/pipedetect/discussions) 