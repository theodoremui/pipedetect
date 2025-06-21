"""
Tests for image and video processors.

This module contains tests for the ImageProcessor and VideoProcessor classes,
including file handling, processing workflows, and error conditions.
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from pipedetect.processors.image_processor import ImageProcessor, ImageProcessingResult
from pipedetect.processors.video_processor import VideoProcessor, VideoProcessingResult
from pipedetect.core.pose_detector import PoseDetectionResult


class TestImageProcessor:
    """Test cases for ImageProcessor."""
    
    @pytest.fixture
    def mock_detector(self):
        """Create mock pose detector."""
        detector = Mock()
        detector.detect.return_value = PoseDetectionResult(
            pose_landmarks=[[{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9}]],
            num_poses=1,
            processing_time_ms=25.0
        )
        return detector
    
    @pytest.fixture
    def mock_visualizer(self):
        """Create mock visualizer."""
        visualizer = Mock()
        visualizer.visualize.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        return visualizer
    
    @pytest.fixture
    def processor(self, mock_detector, mock_visualizer):
        """Create ImageProcessor instance."""
        return ImageProcessor(mock_detector, mock_visualizer)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_image_file(self, temp_dir):
        """Create a sample image file."""
        image_path = temp_dir / "test_image.jpg"
        
        # Create a simple test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        with patch('cv2.imread', return_value=test_image):
            with patch('cv2.imwrite', return_value=True):
                # Simulate file creation
                image_path.touch()
                return image_path
    
    def test_processor_initialization(self, mock_detector, mock_visualizer):
        """Test processor initialization."""
        processor = ImageProcessor(mock_detector, mock_visualizer)
        
        assert processor.pose_detector == mock_detector
        assert processor.visualizer == mock_visualizer
        assert processor.SUPPORTED_FORMATS == {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.tif'}
    
    def test_process_image_success(self, processor, sample_image_file, temp_dir):
        """Test successful image processing."""
        output_path = temp_dir / "output.jpg"
        
        with patch('cv2.imread') as mock_imread, \
             patch('cv2.cvtColor') as mock_cvtcolor, \
             patch('cv2.imwrite', return_value=True) as mock_imwrite:
            
            # Mock image loading
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            mock_imread.return_value = test_image
            mock_cvtcolor.return_value = test_image
            
            result = processor.process_image(sample_image_file, output_path)
            
            assert result.success
            assert result.detection_result.num_poses == 1
            assert result.output_path == str(output_path)
            
            # Verify methods were called
            mock_imread.assert_called_once()
            processor.pose_detector.detect.assert_called_once()
            processor.visualizer.visualize.assert_called_once()
            mock_imwrite.assert_called_once()
    
    def test_process_image_nonexistent_file(self, processor):
        """Test processing with non-existent file."""
        result = processor.process_image("nonexistent.jpg")
        
        assert not result.success
        assert "does not exist" in result.error_message
    
    def test_process_image_unsupported_format(self, processor, temp_dir):
        """Test processing with unsupported format."""
        unsupported_file = temp_dir / "test.txt"
        unsupported_file.touch()
        
        result = processor.process_image(unsupported_file)
        
        assert not result.success
        assert "Unsupported image format" in result.error_message
    
    def test_process_image_load_failure(self, processor, sample_image_file):
        """Test handling of image load failure."""
        with patch('cv2.imread', return_value=None):
            result = processor.process_image(sample_image_file)
            
            assert not result.success
            assert "Failed to load image" in result.error_message
    
    def test_process_image_with_display(self, processor, sample_image_file):
        """Test image processing with display option."""
        with patch('cv2.imread') as mock_imread, \
             patch('cv2.cvtColor') as mock_cvtcolor, \
             patch('cv2.imshow') as mock_imshow, \
             patch('cv2.waitKey') as mock_waitkey, \
             patch('cv2.destroyAllWindows') as mock_destroy:
            
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            mock_imread.return_value = test_image
            mock_cvtcolor.return_value = test_image
            
            result = processor.process_image(sample_image_file, display=True)
            
            assert result.success
            mock_imshow.assert_called_once()
            mock_waitkey.assert_called_once()
            mock_destroy.assert_called_once()
    
    def test_process_batch(self, processor, temp_dir):
        """Test batch processing of images."""
        # Create multiple test image files
        for i in range(3):
            image_file = temp_dir / f"test_{i}.jpg"
            image_file.touch()
        
        output_dir = temp_dir / "output"
        
        with patch('cv2.imread') as mock_imread, \
             patch('cv2.cvtColor') as mock_cvtcolor, \
             patch('cv2.imwrite', return_value=True):
            
            test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_imread.return_value = test_image
            mock_cvtcolor.return_value = test_image
            
            results = processor.process_batch(temp_dir, output_dir)
            
            assert results["total_files"] == 3
            assert results["successful"] == 3
            assert results["failed"] == 0
            assert results["total_poses"] == 3  # 1 pose per image
    
    def test_get_supported_formats(self, processor):
        """Test getting supported formats."""
        formats = processor.get_supported_formats()
        
        assert isinstance(formats, set)
        assert '.jpg' in formats
        assert '.png' in formats
        assert len(formats) > 0
    
    def test_estimate_processing_time(self, processor, sample_image_file):
        """Test processing time estimation."""
        with patch('cv2.imread') as mock_imread:
            test_image = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
            mock_imread.return_value = test_image
            
            estimated_time = processor.estimate_processing_time(sample_image_file)
            
            assert estimated_time is not None
            assert estimated_time > 0


class TestVideoProcessor:
    """Test cases for VideoProcessor."""
    
    @pytest.fixture
    def mock_detector(self):
        """Create mock pose detector."""
        detector = Mock()
        detector.detect.return_value = PoseDetectionResult(
            pose_landmarks=[[{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9}]],
            num_poses=1,
            processing_time_ms=25.0
        )
        return detector
    
    @pytest.fixture
    def mock_visualizer(self):
        """Create mock visualizer."""
        visualizer = Mock()
        visualizer.visualize.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        return visualizer
    
    @pytest.fixture
    def processor(self, mock_detector, mock_visualizer):
        """Create VideoProcessor instance."""
        return VideoProcessor(mock_detector, mock_visualizer)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_video_capture(self):
        """Create mock video capture."""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            1: 30.0,    # FPS
            3: 640,     # Width
            4: 480,     # Height
            7: 100      # Frame count
        }.get(prop, 0)
        
        # Mock frame reading
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap.read.side_effect = [(True, test_frame)] * 5 + [(False, None)]
        
        return mock_cap
    
    def test_processor_initialization(self, mock_detector, mock_visualizer):
        """Test processor initialization."""
        processor = VideoProcessor(mock_detector, mock_visualizer)
        
        assert processor.pose_detector == mock_detector
        assert processor.visualizer == mock_visualizer
        assert processor.SUPPORTED_FORMATS == {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
    
    def test_process_video_success(self, processor, temp_dir, mock_video_capture):
        """Test successful video processing."""
        video_file = temp_dir / "test_video.mp4"
        video_file.touch()
        output_file = temp_dir / "output_video.mp4"
        
        with patch('cv2.VideoCapture', return_value=mock_video_capture), \
             patch('cv2.VideoWriter') as mock_writer_class, \
             patch('cv2.cvtColor') as mock_cvtcolor:
            
            mock_writer = Mock()
            mock_writer.isOpened.return_value = True
            mock_writer_class.return_value = mock_writer
            mock_cvtcolor.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
            
            result = processor.process_video(video_file, output_file)
            
            assert result.success
            assert result.total_frames == 100
            assert result.processed_frames == 5  # Based on mock setup
            assert result.fps == 30.0
            assert result.resolution == (640, 480)
    
    def test_process_video_nonexistent_file(self, processor):
        """Test processing with non-existent video file."""
        result = processor.process_video("nonexistent.mp4")
        
        assert not result.success
        assert "Invalid input video" in result.error_message
    
    def test_process_video_unsupported_format(self, processor, temp_dir):
        """Test processing with unsupported format."""
        unsupported_file = temp_dir / "test.txt"
        unsupported_file.touch()
        
        result = processor.process_video(unsupported_file)
        
        assert not result.success
        assert "Invalid input video" in result.error_message
    
    def test_process_video_open_failure(self, processor, temp_dir):
        """Test handling of video open failure."""
        video_file = temp_dir / "test_video.mp4"
        video_file.touch()
        
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        
        with patch('cv2.VideoCapture', return_value=mock_cap):
            result = processor.process_video(video_file)
            
            assert not result.success
            assert "Failed to open video" in result.error_message
    
    def test_process_video_with_display(self, processor, temp_dir, mock_video_capture):
        """Test video processing with display option."""
        video_file = temp_dir / "test_video.mp4"
        video_file.touch()
        
        with patch('cv2.VideoCapture', return_value=mock_video_capture), \
             patch('cv2.cvtColor') as mock_cvtcolor, \
             patch('cv2.imshow') as mock_imshow, \
             patch('cv2.waitKey', return_value=ord('q')) as mock_waitkey, \
             patch('cv2.destroyAllWindows') as mock_destroy:
            
            mock_cvtcolor.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
            
            result = processor.process_video(video_file, display=True)
            
            assert result.success
            # Display methods should be called
            assert mock_imshow.call_count > 0
    
    def test_process_video_stream(self, processor, mock_video_capture):
        """Test processing video stream."""
        with patch('cv2.VideoCapture', return_value=mock_video_capture), \
             patch('cv2.cvtColor') as mock_cvtcolor, \
             patch('cv2.imshow') as mock_imshow, \
             patch('cv2.waitKey', return_value=ord('q')) as mock_waitkey, \
             patch('cv2.destroyAllWindows') as mock_destroy:
            
            mock_cvtcolor.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
            
            result = processor.process_video_stream(source=0, max_frames=5)
            
            assert result.success
            assert result.processed_frames == 5
            assert result.fps == 30.0
    
    def test_get_video_info(self, processor, temp_dir):
        """Test getting video information."""
        video_file = temp_dir / "test_video.mp4"
        video_file.touch()
        
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            1: 30.0,    # FPS
            3: 1920,    # Width
            4: 1080,    # Height
            7: 900,     # Frame count
            6: 875967.0 # FOURCC
        }.get(prop, 0)
        
        with patch('cv2.VideoCapture', return_value=mock_cap):
            info = processor.get_video_info(video_file)
            
            assert info is not None
            assert info["fps"] == 30.0
            assert info["width"] == 1920
            assert info["height"] == 1080
            assert info["total_frames"] == 900
            assert info["duration_seconds"] == 30.0  # 900 frames / 30 fps
    
    def test_extract_pose_data(self, processor, temp_dir, mock_video_capture):
        """Test extracting pose data from video."""
        video_file = temp_dir / "test_video.mp4"
        video_file.touch()
        
        with patch('cv2.VideoCapture', return_value=mock_video_capture), \
             patch('cv2.cvtColor') as mock_cvtcolor, \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_cvtcolor.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
            
            output_path = processor.extract_pose_data(video_file, "json")
            
            assert output_path is not None
            assert output_path.endswith("_poses.json")
    
    def test_get_supported_formats(self, processor):
        """Test getting supported formats."""
        formats = processor.get_supported_formats()
        
        assert isinstance(formats, set)
        assert '.mp4' in formats
        assert '.avi' in formats
        assert len(formats) > 0


def mock_open():
    """Create a mock for file operations."""
    from unittest.mock import mock_open as _mock_open
    return _mock_open()


if __name__ == "__main__":
    pytest.main([__file__]) 