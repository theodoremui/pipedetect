"""Tests for core data models."""

import pytest
from datetime import datetime
from pathlib import Path

from pipedetect.core.models import (
    LandmarkPoint, PoseResult, DetectionConfig, 
    ProcessingStats, OutputPaths
)


class TestLandmarkPoint:
    """Test LandmarkPoint model."""
    
    def test_landmark_point_creation(self):
        """Test creating a valid landmark point."""
        point = LandmarkPoint(
            x=0.5, y=0.3, z=0.1,
            visibility=0.9, presence=0.8
        )
        
        assert point.x == 0.5
        assert point.y == 0.3
        assert point.z == 0.1
        assert point.visibility == 0.9
        assert point.presence == 0.8


class TestPoseResult:
    """Test PoseResult model."""
    
    def test_pose_result_creation(self):
        """Test creating a valid pose result."""
        landmarks = [
            LandmarkPoint(x=0.5, y=0.3, z=0.1, visibility=0.9, presence=0.8)
        ]
        
        result = PoseResult(
            frame_id=1,
            timestamp=1.5,
            landmarks=landmarks,
            confidence=0.95,
            source_file="test.jpg"
        )
        
        assert result.frame_id == 1
        assert result.timestamp == 1.5
        assert len(result.landmarks) == 1
        assert result.confidence == 0.95
        assert result.source_file == "test.jpg"
    
    def test_confidence_validation(self):
        """Test confidence validation."""
        landmarks = [
            LandmarkPoint(x=0.5, y=0.3, z=0.1, visibility=0.9, presence=0.8)
        ]
        
        # Valid confidence
        result = PoseResult(
            frame_id=1, timestamp=1.5, landmarks=landmarks,
            confidence=0.5, source_file="test.jpg"
        )
        assert result.confidence == 0.5
        
        # Invalid confidence - too high
        with pytest.raises(ValueError):
            PoseResult(
                frame_id=1, timestamp=1.5, landmarks=landmarks,
                confidence=1.5, source_file="test.jpg"
            )
        
        # Invalid confidence - too low
        with pytest.raises(ValueError):
            PoseResult(
                frame_id=1, timestamp=1.5, landmarks=landmarks,
                confidence=-0.1, source_file="test.jpg"
            )


class TestDetectionConfig:
    """Test DetectionConfig model."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = DetectionConfig()
        
        assert config.min_detection_confidence == 0.5
        assert config.min_tracking_confidence == 0.5
        assert config.model_complexity == 1
        assert config.enable_segmentation is False
        assert config.smooth_landmarks is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = DetectionConfig(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.8,
            model_complexity=2,
            enable_segmentation=True,
            smooth_landmarks=False
        )
        
        assert config.min_detection_confidence == 0.7
        assert config.min_tracking_confidence == 0.8
        assert config.model_complexity == 2
        assert config.enable_segmentation is True
        assert config.smooth_landmarks is False
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid values
        config = DetectionConfig(
            min_detection_confidence=0.0,
            min_tracking_confidence=1.0,
            model_complexity=0
        )
        assert config.min_detection_confidence == 0.0
        assert config.min_tracking_confidence == 1.0
        assert config.model_complexity == 0
        
        # Invalid confidence values
        with pytest.raises(ValueError):
            DetectionConfig(min_detection_confidence=-0.1)
        
        with pytest.raises(ValueError):
            DetectionConfig(min_detection_confidence=1.1)
        
        with pytest.raises(ValueError):
            DetectionConfig(min_tracking_confidence=-0.1)
        
        with pytest.raises(ValueError):
            DetectionConfig(min_tracking_confidence=1.1)
        
        # Invalid model complexity
        with pytest.raises(ValueError):
            DetectionConfig(model_complexity=-1)
        
        with pytest.raises(ValueError):
            DetectionConfig(model_complexity=3)


class TestProcessingStats:
    """Test ProcessingStats model."""
    
    def test_processing_stats_creation(self):
        """Test creating processing stats."""
        start_time = datetime.now()
        end_time = datetime.now()
        
        stats = ProcessingStats(
            total_frames=100,
            processed_frames=90,
            failed_frames=10,
            processing_time=30.5,
            fps=25.0,
            start_time=start_time,
            end_time=end_time
        )
        
        assert stats.total_frames == 100
        assert stats.processed_frames == 90
        assert stats.failed_frames == 10
        assert stats.processing_time == 30.5
        assert stats.fps == 25.0
        assert stats.start_time == start_time
        assert stats.end_time == end_time
    
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        stats = ProcessingStats(
            total_frames=100, processed_frames=80, failed_frames=20,
            processing_time=10.0, fps=10.0,
            start_time=datetime.now(), end_time=datetime.now()
        )
        
        assert stats.success_rate == 0.8
        
        # Test zero total frames
        stats_zero = ProcessingStats(
            total_frames=0, processed_frames=0, failed_frames=0,
            processing_time=0.0, fps=0.0,
            start_time=datetime.now(), end_time=datetime.now()
        )
        
        assert stats_zero.success_rate == 0.0


class TestOutputPaths:
    """Test OutputPaths model."""
    
    def test_output_paths_creation(self):
        """Test creating output paths."""
        paths = OutputPaths(
            json_file=Path("output.json"),
            csv_file=Path("output.csv"),
            frames_dir=Path("frames"),
            overlay_dir=Path("overlays")
        )
        
        assert paths.json_file == Path("output.json")
        assert paths.csv_file == Path("output.csv")
        assert paths.frames_dir == Path("frames")
        assert paths.overlay_dir == Path("overlays") 