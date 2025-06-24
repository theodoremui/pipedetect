"""Tests for input validators."""

import pytest
import tempfile
from pathlib import Path

from pipedetect.io.validators import InputValidator
from pipedetect.core.exceptions import ValidationError


class TestInputValidator:
    """Test InputValidator functionality."""
    
    def test_validate_confidence_threshold(self):
        """Test confidence threshold validation."""
        # Valid values
        assert InputValidator.validate_confidence_threshold(0.0) == 0.0
        assert InputValidator.validate_confidence_threshold(0.5) == 0.5
        assert InputValidator.validate_confidence_threshold(1.0) == 1.0
        
        # Invalid values
        with pytest.raises(ValidationError):
            InputValidator.validate_confidence_threshold(-0.1)
        
        with pytest.raises(ValidationError):
            InputValidator.validate_confidence_threshold(1.1)
    
    def test_validate_input_path_nonexistent(self):
        """Test validation of non-existent paths."""
        with pytest.raises(ValidationError, match="does not exist"):
            InputValidator.validate_input_path("/nonexistent/path")
    
    def test_is_image_file(self):
        """Test image file detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create actual files for testing
            image_files = ["test.jpg", "test.jpeg", "test.png", "test.bmp", "test.tiff", "test.webp"]
            for filename in image_files:
                (temp_path / filename).touch()
                assert InputValidator.is_image_file(temp_path / filename)
            
            # Test case insensitivity
            (temp_path / "test.JPG").touch()
            (temp_path / "test.PNG").touch()
            assert InputValidator.is_image_file(temp_path / "test.JPG")
            assert InputValidator.is_image_file(temp_path / "test.PNG")
            
            # Test unsupported extensions
            (temp_path / "test.txt").touch()
            (temp_path / "test.mp4").touch()
            assert not InputValidator.is_image_file(temp_path / "test.txt")
            assert not InputValidator.is_image_file(temp_path / "test.mp4")
    
    def test_is_video_file(self):
        """Test video file detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create actual files for testing
            video_files = ["test.mp4", "test.avi", "test.mov", "test.mkv", "test.wmv", "test.webm"]
            for filename in video_files:
                (temp_path / filename).touch()
                assert InputValidator.is_video_file(temp_path / filename)
            
            # Test case insensitivity
            (temp_path / "test.MP4").touch()
            (temp_path / "test.AVI").touch()
            assert InputValidator.is_video_file(temp_path / "test.MP4")
            assert InputValidator.is_video_file(temp_path / "test.AVI")
            
            # Test unsupported extensions
            (temp_path / "test.txt").touch()
            (temp_path / "test.jpg").touch()
            assert not InputValidator.is_video_file(temp_path / "test.txt")
            assert not InputValidator.is_video_file(temp_path / "test.jpg")
    
    def test_get_input_type_with_temp_files(self):
        """Test input type detection with temporary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test directory
            assert InputValidator.get_input_type(temp_path) == "directory"
            
            # Test image file
            image_file = temp_path / "test.jpg"
            image_file.touch()
            assert InputValidator.get_input_type(image_file) == "image"
            
            # Test video file
            video_file = temp_path / "test.mp4"
            video_file.touch()
            assert InputValidator.get_input_type(video_file) == "video"
            
            # Test unsupported file
            text_file = temp_path / "test.txt"
            text_file.touch()
            with pytest.raises(ValidationError, match="Unsupported file format"):
                InputValidator.get_input_type(text_file)
    
    def test_validate_image_directory(self):
        """Test image directory validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Empty directory
            with pytest.raises(ValidationError, match="No supported image files"):
                InputValidator.validate_image_directory(temp_path)
            
            # Directory with images
            (temp_path / "image1.jpg").touch()
            (temp_path / "image2.png").touch()
            (temp_path / "text.txt").touch()  # Should be ignored
            
            image_files = InputValidator.validate_image_directory(temp_path)
            assert len(image_files) == 2
            assert all(f.suffix.lower() in {'.jpg', '.png'} for f in image_files)
            
            # Test with non-directory
            file_path = temp_path / "not_a_dir.txt"
            file_path.touch()
            with pytest.raises(ValidationError, match="Not a directory"):
                InputValidator.validate_image_directory(file_path) 