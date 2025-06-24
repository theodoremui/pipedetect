# PipeDetect 🕺

**Professional Pose Estimation using MediaPipe**

A modern, extensible Python application for detecting human poses in videos and images using Google's MediaPipe framework. Built with best software engineering practices including SOLID principles, comprehensive testing, and modular architecture.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package%20manager-blue)](https://github.com/astral-sh/uv)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🚀 Features

- **Multi-format Support**: Process videos, single images, or entire directories of images
- **High-Quality Pose Detection**: Leverages MediaPipe's state-of-the-art pose estimation models
- **Multiple Output Formats**: Export results as JSON and CSV with comprehensive metadata
- **Visual Outputs**: Generate frame-by-frame images and pose overlay visualizations
- **Performance Monitoring**: Built-in profiling and progress tracking
- **Configurable Detection**: Adjustable confidence thresholds and model complexity
- **Modern CLI**: Rich terminal interface with progress bars and colored output
- **Comprehensive Logging**: Structured logging with multiple verbosity levels
- **Robust Error Handling**: Graceful error handling with detailed error messages
- **Extensible Architecture**: Modular design following SOLID principles

## 📋 Requirements

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

## 🔧 Installation

### Using uv (Recommended)

1. **Install uv** if you haven't already:
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/pipedetect.git
   cd pipedetect
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Activate the virtual environment**:
   ```bash
   # On Unix/macOS
   source .venv/bin/activate
   
   # On Windows
   .venv\Scripts\activate
   ```

### Using pip (Alternative)

```bash
git clone https://github.com/your-username/pipedetect.git
cd pipedetect
pip install -e .
```

## 🎯 Quick Start

### Basic Usage

```bash
# Process a video file
python detect.py video.mp4

# Process a single image
python detect.py image.jpg

# Process all images in a directory
python detect.py /path/to/images/

# Specify custom output directory
python detect.py video.mp4 --output-dir results/
```

### Advanced Usage

```bash
# High-precision detection with heavy model
python detect.py video.mp4 \
  --model-complexity 2 \
  --detection-confidence 0.8 \
  --tracking-confidence 0.7

# Custom output filenames
python detect.py video.mp4 \
  --json my_poses.json \
  --csv my_poses.csv

# Enable segmentation and disable frame saving
python detect.py video.mp4 \
  --segmentation \
  --no-frames

# Verbose logging with log file
python detect.py video.mp4 \
  --verbose --verbose \
  --log-file pose_detection.log
```

## 📁 Output Structure

PipeDetect generates comprehensive outputs organized in the `outputs/` directory:

```
outputs/
├── pose_video_20231201_143022.json       # Detailed JSON results
├── pose_video_20231201_143022.csv        # Tabular CSV data
├── frames_video_20231201_143022/          # Original video frames
│   ├── frame_000001.jpg
│   ├── frame_000002.jpg
│   └── ...
└── overlay_video_20231201_143022/         # Frames with pose overlays
    ├── overlay_000001.jpg
    ├── overlay_000002.jpg
    └── ...
```

### Output Formats

#### JSON Output
```json
{
  "metadata": {
    "export_timestamp": "2023-12-01T14:30:22",
    "total_frames": 1000,
    "processed_frames": 950,
    "success_rate": 0.95,
    "processing_time_seconds": 45.2,
    "fps": 21.0
  },
  "results": [
    {
      "frame_id": 0,
      "timestamp": 0.033,
      "confidence": 0.92,
      "source_file": "video.mp4",
      "landmarks": [
        {
          "x": 0.5,
          "y": 0.3,
          "z": 0.1,
          "visibility": 0.9,
          "presence": 0.8
        }
      ]
    }
  ]
}
```

#### CSV Output
Contains frame-by-frame data with columns for each of the 33 pose landmarks:
- Basic info: `frame_id`, `timestamp`, `confidence`, `source_file`
- Landmarks: `landmark_0_x`, `landmark_0_y`, `landmark_0_z`, `landmark_0_visibility`, `landmark_0_presence`, ...

## ⚙️ Configuration Options

### Model Parameters
- `--model-complexity`: 0 (light), 1 (full), 2 (heavy) - Default: 1
- `--detection-confidence`: Minimum detection confidence (0.0-1.0) - Default: 0.5
- `--tracking-confidence`: Minimum tracking confidence (0.0-1.0) - Default: 0.5
- `--segmentation`: Enable pose segmentation (slower but more detailed)
- `--no-smooth`: Disable landmark smoothing

### Output Control
- `--output-dir`: Custom output directory - Default: "outputs"
- `--json`: Custom JSON filename
- `--csv`: Custom CSV filename
- `--no-frames`: Skip saving individual frames
- `--no-overlays`: Skip saving overlay frames

### Interface Options
- `--verbose` / `-v`: Increase verbosity (use -vv for debug)
- `--quiet` / `-q`: Suppress console output
- `--no-progress`: Hide progress bar
- `--log-file`: Save logs to file

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/pipedetect --cov-report=html

# Run specific test files
uv run pytest tests/test_core_models.py
uv run pytest tests/test_validators.py -v
```

## 🏗️ Architecture

PipeDetect follows modern software engineering principles:

### Project Structure
```
pipedetect/
├── src/pipedetect/              # Main package
│   ├── core/                    # Core business logic
│   │   ├── models.py           # Data models (Pydantic)
│   │   └── exceptions.py       # Custom exceptions
│   ├── detection/              # MediaPipe integration
│   │   ├── pose_detector.py    # High-level detector
│   │   └── mediapipe_wrapper.py # MediaPipe wrapper
│   ├── io/                     # Input/Output handling
│   │   ├── exporters.py        # JSON/CSV exporters
│   │   ├── validators.py       # Input validation
│   │   └── file_manager.py     # File operations
│   ├── visualization/          # Rendering and progress
│   │   ├── overlay_renderer.py # Pose visualization
│   │   └── progress_tracker.py # Progress display
│   ├── utils/                  # Utilities
│   │   ├── logging_config.py   # Logging setup
│   │   └── performance.py      # Performance profiling
│   └── cli/                    # Command-line interface
│       ├── main.py            # CLI entry point
│       └── processor.py       # Main orchestrator
├── tests/                      # Comprehensive test suite
├── detect.py                   # Main script
└── pyproject.toml             # Project configuration
```

### Design Principles
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Easy to extend without modifying existing code
- **Dependency Inversion**: Abstractions don't depend on details
- **DRY**: No code duplication
- **Comprehensive Error Handling**: Graceful failure with detailed messages
- **Performance Monitoring**: Built-in profiling and metrics

## 🔧 Development

### Setting up Development Environment

```bash
# Clone and setup
git clone https://github.com/your-username/pipedetect.git
cd pipedetect
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run code formatting
uv run black src/ tests/
uv run isort src/ tests/

# Type checking
uv run mypy src/
```

### Adding New Features

1. **Exporters**: Extend `BaseExporter` in `io/exporters.py`
2. **Validators**: Add methods to `InputValidator` in `io/validators.py`
3. **Visualizations**: Extend `OverlayRenderer` in `visualization/overlay_renderer.py`
4. **CLI Options**: Add to `cli/main.py` and update `processor.py`

## 📊 Performance

PipeDetect is optimized for performance:

- **Efficient Processing**: Streaming video processing with minimal memory usage
- **Parallel Operations**: Multi-threaded resource monitoring
- **Progress Tracking**: Real-time FPS and ETA calculations
- **Memory Management**: Automatic cleanup of temporary resources

### Benchmarks
- **Video Processing**: ~15-30 FPS on modern hardware
- **Image Batch**: ~10-50 images/second depending on size
- **Memory Usage**: ~200-500MB for typical video processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`uv run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://github.com/google-ai-edge/mediapipe) for the excellent pose estimation models
- [uv](https://github.com/astral-sh/uv) for modern Python package management
- [Rich](https://github.com/Textualize/rich) for beautiful terminal interfaces
- [Typer](https://github.com/tiangolo/typer) for the CLI framework

## 🆘 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-username/pipedetect/issues)
- 💬 [Discussions](https://github.com/your-username/pipedetect/discussions)

---

Built with ❤️ for the computer vision community
