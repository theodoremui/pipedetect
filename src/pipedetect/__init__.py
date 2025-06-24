"""
PipeDetect: Professional pose estimation using MediaPipe.

A modern, extensible pose detection system with comprehensive 
visualization and analysis capabilities.
"""

__version__ = "0.1.0"
__author__ = "PipeDetect Team"

from .core.models import PoseResult, DetectionConfig
from .detection.pose_detector import PoseDetector

__all__ = ["PoseResult", "DetectionConfig", "PoseDetector"] 