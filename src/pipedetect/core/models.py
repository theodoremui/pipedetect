"""Core data models for pose detection."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field, field_validator


class OutputFormat(str, Enum):
    """Supported output formats."""
    JSON = "json"
    CSV = "csv"


class LandmarkPoint(BaseModel):
    """Represents a single pose landmark point."""
    x: float = Field(..., description="X coordinate (normalized)")
    y: float = Field(..., description="Y coordinate (normalized)")
    z: float = Field(..., description="Z coordinate (normalized)")
    visibility: float = Field(..., description="Visibility score")
    presence: float = Field(..., description="Presence score")


class PoseResult(BaseModel):
    """Complete pose detection result for a single frame."""
    frame_id: int = Field(..., description="Frame number")
    timestamp: float = Field(..., description="Timestamp in seconds")
    landmarks: List[LandmarkPoint] = Field(..., description="Pose landmarks")
    confidence: float = Field(..., description="Overall pose confidence")
    source_file: str = Field(..., description="Source file path")
    
    model_config = {"arbitrary_types_allowed": True}
        
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Ensure confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0 and 1')
        return v


class DetectionConfig(BaseModel):
    """Configuration for pose detection."""
    min_detection_confidence: float = Field(
        default=0.5, 
        ge=0.0, 
        le=1.0,
        description="Minimum confidence for pose detection"
    )
    min_tracking_confidence: float = Field(
        default=0.5, 
        ge=0.0, 
        le=1.0,
        description="Minimum confidence for pose tracking"
    )
    model_complexity: int = Field(
        default=1, 
        ge=0, 
        le=2,
        description="Model complexity (0=light, 1=full, 2=heavy)"
    )
    enable_segmentation: bool = Field(
        default=False,
        description="Enable pose segmentation"
    )
    smooth_landmarks: bool = Field(
        default=True,
        description="Apply landmark smoothing"
    )


@dataclass
class ProcessingStats:
    """Statistics from processing session."""
    total_frames: int
    processed_frames: int
    failed_frames: int
    processing_time: float
    fps: float
    start_time: datetime
    end_time: datetime
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_frames == 0:
            return 0.0
        return self.processed_frames / self.total_frames


@dataclass 
class OutputPaths:
    """Container for all output file paths."""
    json_file: Path
    csv_file: Path
    frames_dir: Path
    overlay_dir: Path
    
    def create_directories(self) -> None:
        """Create all necessary output directories."""
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.overlay_dir.mkdir(parents=True, exist_ok=True)
        self.json_file.parent.mkdir(parents=True, exist_ok=True)
        self.csv_file.parent.mkdir(parents=True, exist_ok=True) 