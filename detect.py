#!/usr/bin/env python3
"""
PipeDetect - Professional Pose Estimation using MediaPipe

A modern command-line tool for detecting human poses in videos and images.
This script serves as the main entry point for the PipeDetect pose detection system.

Usage:
    python detect.py input_video.mp4
    python detect.py image.jpg --output-dir results/
    python detect.py images_folder/ --json poses.json --csv poses.csv

For more options, run: python detect.py --help
"""

import sys
from pathlib import Path

# Add src directory to Python path to enable imports
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    from pipedetect.cli.main import app
    
    if __name__ == "__main__":
        app()
        
except ImportError as e:
    print(f"Error importing PipeDetect modules: {e}")
    print("Please ensure you have installed the dependencies:")
    print("  uv sync")
    print("  uv run python detect.py --help")
    sys.exit(1)
except Exception as e:
    print(f"Error running PipeDetect: {e}")
    sys.exit(1) 