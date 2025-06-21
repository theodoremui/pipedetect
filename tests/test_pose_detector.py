"""
Tests for pose detector functionality.

This module contains comprehensive tests for the PoseDetector class,
including configuration validation, detection accuracy, and error handling.
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pipedetect.core.pose_detector import (
    PoseDetector, 
    PoseDetectorConfig, 
    PoseDetectionResult
)


class TestPoseDetectorConfig:
    """Test cases for PoseDetectorConfig."""
    
    def test_valid_config_creation(self):
        """Test creating a valid configuration."""
        with patch('pathlib.Path.exists', return_value=True):
            config = PoseDetectorConfig(
                model_path="test_model.task",
                num_poses=3,
                min_pose_detection_confidence=0.7
            )
            
            assert config.model_path == "test_model.task"
            assert config.num_poses == 3
            assert config.min_pose_detection_confidence == 0.7
    
    def test_invalid_model_path(self):
        """Test validation of model path."""
        with pytest.raises(ValueError, match="Model file not found"):
            PoseDetectorConfig(model_path="nonexistent_model.task")
    
    def test_num_poses_validation(self):
        """Test validation of num_poses parameter."""
        with patch('pathlib.Path.exists', return_value=True):
            # Valid range
            config = PoseDetectorConfig(model_path="test.task", num_poses=5)
            assert config.num_poses == 5
            
            # Invalid ranges
            with pytest.raises(ValueError):
                PoseDetectorConfig(model_path="test.task", num_poses=0)
            
            with pytest.raises(ValueError):
                PoseDetectorConfig(model_path="test.task", num_poses=11)
    
    def test_confidence_validation(self):
        """Test validation of confidence parameters."""
        with patch('pathlib.Path.exists', return_value=True):
            # Valid confidence values
            config = PoseDetectorConfig(
                model_path="test.task",
                min_pose_detection_confidence=0.8,
                min_pose_presence_confidence=0.6,
                min_tracking_confidence=0.9
            )
            
            assert config.min_pose_detection_confidence == 0.8
            assert config.min_pose_presence_confidence == 0.6
            assert config.min_tracking_confidence == 0.9
            
            # Invalid confidence values
            with pytest.raises(ValueError):
                PoseDetectorConfig(
                    model_path="test.task",
                    min_pose_detection_confidence=1.5
                )
            
            with pytest.raises(ValueError):
                PoseDetectorConfig(
                    model_path="test.task",
                    min_pose_presence_confidence=-0.1
                )


class TestPoseDetectionResult:
    """Test cases for PoseDetectionResult."""
    
    def test_empty_result_creation(self):
        """Test creating an empty detection result."""
        result = PoseDetectionResult()
        
        assert result.pose_landmarks == []
        assert result.pose_world_landmarks == []
        assert result.segmentation_masks is None
        assert result.num_poses == 0
        assert result.processing_time_ms == 0.0
    
    def test_result_with_poses(self):
        """Test creating a result with pose data."""
        landmarks = [
            [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9}]
        ]
        
        result = PoseDetectionResult(
            pose_landmarks=landmarks,
            num_poses=1,
            processing_time_ms=50.0
        )
        
        assert len(result.pose_landmarks) == 1
        assert result.num_poses == 1
        assert result.processing_time_ms == 50.0


class TestPoseDetector:
    """Test cases for PoseDetector class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        with patch('pathlib.Path.exists', return_value=True):
            return PoseDetectorConfig(
                model_path="test_model.task",
                num_poses=2,
                min_pose_detection_confidence=0.5
            )
    
    @pytest.fixture
    def mock_mediapipe(self):
        """Mock MediaPipe components."""
        with patch('pipedetect.core.pose_detector.python') as mock_python, \
             patch('pipedetect.core.pose_detector.vision') as mock_vision:
            
            # Mock the pose landmarker
            mock_landmarker = Mock()
            mock_vision.PoseLandmarker.create_from_options.return_value = mock_landmarker
            
            yield {
                'python': mock_python,
                'vision': mock_vision,
                'landmarker': mock_landmarker
            }
    
    def test_detector_initialization(self, mock_config, mock_mediapipe):
        """Test successful detector initialization."""
        detector = PoseDetector(mock_config)
        
        assert detector.is_initialized()
        assert detector.get_config() == mock_config
        
        # Verify MediaPipe was called correctly
        mock_mediapipe['vision'].PoseLandmarker.create_from_options.assert_called_once()
    
    def test_detector_initialization_failure(self, mock_config):
        """Test detector initialization failure."""
        with patch('pipedetect.core.pose_detector.vision.PoseLandmarker.create_from_options') as mock_create:
            mock_create.side_effect = Exception("MediaPipe initialization failed")
            
            with pytest.raises(RuntimeError, match="MediaPipe initialization failed"):
                PoseDetector(mock_config)
    
    def test_detect_with_valid_image(self, mock_config, mock_mediapipe):
        """Test pose detection with valid image."""
        detector = PoseDetector(mock_config)
        
        # Create test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Mock detection result
        mock_detection = Mock()
        mock_detection.pose_landmarks = [
            [Mock(x=0.5, y=0.5, z=0.0, visibility=0.9)]
        ]
        mock_detection.pose_world_landmarks = []
        mock_detection.segmentation_masks = None
        
        mock_mediapipe['landmarker'].detect.return_value = mock_detection
        
        # Perform detection
        result = detector.detect(test_image)
        
        assert isinstance(result, PoseDetectionResult)
        assert result.num_poses == 1
        assert result.processing_time_ms > 0
        assert len(result.pose_landmarks) == 1
    
    def test_detect_with_invalid_image(self, mock_config, mock_mediapipe):
        """Test pose detection with invalid image."""
        detector = PoseDetector(mock_config)
        
        # Test with None image
        with pytest.raises(ValueError, match="Invalid image provided"):
            detector.detect(None)
        
        # Test with empty image
        empty_image = np.array([])
        with pytest.raises(ValueError, match="Invalid image provided"):
            detector.detect(empty_image)
    
    def test_detect_without_initialization(self, mock_config):
        """Test detection without proper initialization."""
        with patch('pipedetect.core.pose_detector.vision.PoseLandmarker.create_from_options') as mock_create:
            mock_create.side_effect = Exception("Failed to initialize")
            
            try:
                detector = PoseDetector(mock_config)
            except:
                pass  # Expected to fail
            
            detector._is_initialized = False
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            with pytest.raises(RuntimeError, match="Detector is not initialized"):
                detector.detect(test_image)
    
    def test_detect_with_mediapipe_failure(self, mock_config, mock_mediapipe):
        """Test handling of MediaPipe detection failure."""
        detector = PoseDetector(mock_config)
        
        # Mock MediaPipe failure
        mock_mediapipe['landmarker'].detect.side_effect = Exception("MediaPipe detection failed")
        
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        with pytest.raises(RuntimeError, match="Detection failed"):
            detector.detect(test_image)
    
    def test_context_manager(self, mock_config, mock_mediapipe):
        """Test detector as context manager."""
        with PoseDetector(mock_config) as detector:
            assert detector.is_initialized()
        
        # Verify cleanup was called
        mock_mediapipe['landmarker'].close.assert_called_once()
    
    def test_convert_detection_result(self, mock_config, mock_mediapipe):
        """Test conversion of MediaPipe result to our format."""
        detector = PoseDetector(mock_config)
        
        # Create mock MediaPipe result
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.6
        mock_landmark.z = 0.1
        mock_landmark.visibility = 0.8
        
        mock_detection = Mock()
        mock_detection.pose_landmarks = [[mock_landmark]]
        mock_detection.pose_world_landmarks = [[mock_landmark]]
        mock_detection.segmentation_masks = None
        
        # Test conversion
        result = detector._convert_detection_result(
            mock_detection, 
            (480, 640, 3), 
            25.5
        )
        
        assert result.num_poses == 1
        assert result.processing_time_ms == 25.5
        assert result.image_shape == (480, 640, 3)
        assert len(result.pose_landmarks) == 1
        assert result.pose_landmarks[0][0]["x"] == 0.5
        assert result.pose_landmarks[0][0]["visibility"] == 0.8
    
    def test_multiple_poses_detection(self, mock_config, mock_mediapipe):
        """Test detection of multiple poses."""
        detector = PoseDetector(mock_config)
        
        # Create test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Mock detection result with multiple poses
        mock_detection = Mock()
        mock_detection.pose_landmarks = [
            [Mock(x=0.3, y=0.4, z=0.0, visibility=0.9)],  # First pose
            [Mock(x=0.7, y=0.6, z=0.0, visibility=0.8)]   # Second pose
        ]
        mock_detection.pose_world_landmarks = []
        mock_detection.segmentation_masks = None
        
        mock_mediapipe['landmarker'].detect.return_value = mock_detection
        
        # Perform detection
        result = detector.detect(test_image)
        
        assert result.num_poses == 2
        assert len(result.pose_landmarks) == 2
        assert result.pose_landmarks[0][0]["x"] == 0.3
        assert result.pose_landmarks[1][0]["x"] == 0.7


class TestPoseDetectorIntegration:
    """Integration tests for PoseDetector."""
    
    @pytest.mark.skipif(
        not Path("notebooks/pose_landmarker_lite.task").exists(),
        reason="MediaPipe model file not available"
    )
    def test_real_model_initialization(self):
        """Test initialization with real MediaPipe model."""
        config = PoseDetectorConfig(
            model_path="notebooks/pose_landmarker_lite.task"
        )
        
        detector = PoseDetector(config)
        assert detector.is_initialized()
    
    @pytest.mark.skipif(
        not Path("notebooks/pose_landmarker_lite.task").exists(),
        reason="MediaPipe model file not available"
    )
    def test_real_image_detection(self):
        """Test pose detection on a real image."""
        config = PoseDetectorConfig(
            model_path="notebooks/pose_landmarker_lite.task"
        )
        
        detector = PoseDetector(config)
        
        # Create a simple test image (solid color)
        # In real usage, this would be a photo with people
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        result = detector.detect(test_image)
        
        # Even with a blank image, the detector should return a valid result
        assert isinstance(result, PoseDetectionResult)
        assert result.processing_time_ms > 0
        assert result.image_shape == (480, 640, 3)


if __name__ == "__main__":
    pytest.main([__file__]) 