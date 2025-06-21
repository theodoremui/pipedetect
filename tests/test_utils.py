"""
Tests for utility modules.

This module contains tests for configuration management and file utilities.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open

from pipedetect.utils.config import AppConfig, load_config, save_config
from pipedetect.utils.file_utils import FileUtils


class TestAppConfig:
    """Test cases for AppConfig."""
    
    def test_default_config_creation(self):
        """Test creating default configuration."""
        config = AppConfig()
        
        assert config.num_poses == 2
        assert config.min_pose_detection_confidence == 0.5
        assert config.output_directory == "output"
        assert config.log_level == "INFO"
    
    def test_config_with_custom_values(self):
        """Test creating config with custom values."""
        with patch('pathlib.Path.exists', return_value=True):
            config = AppConfig(
                model_path="custom_model.task",
                num_poses=5,
                min_pose_detection_confidence=0.8,
                log_level="DEBUG"
            )
            
            assert config.model_path == "custom_model.task"
            assert config.num_poses == 5
            assert config.min_pose_detection_confidence == 0.8
            assert config.log_level == "DEBUG"
    
    def test_config_validation(self):
        """Test configuration validation."""
        with patch('pathlib.Path.exists', return_value=True):
            # Valid config
            config = AppConfig(model_path="test.task", num_poses=3)
            assert config.num_poses == 3
            
            # Invalid num_poses
            with pytest.raises(ValueError):
                AppConfig(model_path="test.task", num_poses=0)
            
            with pytest.raises(ValueError):
                AppConfig(model_path="test.task", num_poses=11)
    
    def test_to_pose_detector_config(self):
        """Test conversion to PoseDetectorConfig."""
        with patch('pathlib.Path.exists', return_value=True):
            app_config = AppConfig(
                model_path="test.task",
                num_poses=3,
                min_pose_detection_confidence=0.7
            )
            
            detector_config = app_config.to_pose_detector_config()
            
            assert detector_config.model_path == "test.task"
            assert detector_config.num_poses == 3
            assert detector_config.min_pose_detection_confidence == 0.7
    
    def test_to_visualization_config(self):
        """Test conversion to VisualizationConfig."""
        with patch('pathlib.Path.exists', return_value=True):
            app_config = AppConfig(
                model_path="test.task",
                landmark_radius=5,
                connection_thickness=3
            )
            
            viz_config = app_config.to_visualization_config()
            
            assert viz_config.landmark_radius == 5
            assert viz_config.connection_thickness == 3


class TestConfigManagement:
    """Test cases for configuration file management."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_load_config_default(self):
        """Test loading default configuration."""
        config = load_config()
        
        assert isinstance(config, AppConfig)
        assert config.num_poses == 2  # Default value
    
    def test_load_config_from_json(self, temp_dir):
        """Test loading configuration from JSON file."""
        config_file = temp_dir / "config.json"
        config_data = {
            "model_path": "test_model.task",
            "num_poses": 3,
            "min_pose_detection_confidence": 0.8
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            # Write config file
            with open(config_file, 'w') as f:
                json.dump(config_data, f)
            
            config = load_config(config_file)
            
            assert config.num_poses == 3
            assert config.min_pose_detection_confidence == 0.8
    
    def test_save_config_json(self, temp_dir):
        """Test saving configuration to JSON file."""
        with patch('pathlib.Path.exists', return_value=True):
            config = AppConfig(
                model_path="test.task",
                num_poses=4
            )
            
            config_file = temp_dir / "saved_config.json"
            success = save_config(config, config_file)
            
            assert success
            assert config_file.exists()
            
            # Verify content
            with open(config_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["num_poses"] == 4
    
    def test_load_config_invalid_file(self, temp_dir):
        """Test loading from invalid config file."""
        invalid_file = temp_dir / "invalid.json"
        
        # Create invalid JSON file
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        # Should return default config without error
        config = load_config(invalid_file)
        assert isinstance(config, AppConfig)
        assert config.num_poses == 2  # Default value


class TestFileUtils:
    """Test cases for FileUtils."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_is_image(self):
        """Test image file detection."""
        assert FileUtils.is_image("test.jpg")
        assert FileUtils.is_image("test.png")
        assert FileUtils.is_image("test.JPEG")  # Case insensitive
        assert not FileUtils.is_image("test.mp4")
        assert not FileUtils.is_image("test.txt")
    
    def test_is_video(self):
        """Test video file detection."""
        assert FileUtils.is_video("test.mp4")
        assert FileUtils.is_video("test.avi")
        assert FileUtils.is_video("test.MOV")  # Case insensitive
        assert not FileUtils.is_video("test.jpg")
        assert not FileUtils.is_video("test.txt")
    
    def test_is_media_file(self):
        """Test media file detection."""
        assert FileUtils.is_media_file("test.jpg")
        assert FileUtils.is_media_file("test.mp4")
        assert not FileUtils.is_media_file("test.txt")
        assert not FileUtils.is_media_file("test.doc")
    
    def test_get_file_type(self):
        """Test file type detection."""
        assert FileUtils.get_file_type("test.jpg") == "image"
        assert FileUtils.get_file_type("test.mp4") == "video"
        assert FileUtils.get_file_type("test.txt") == "unknown"
    
    def test_validate_file_path(self, temp_dir):
        """Test file path validation."""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        assert FileUtils.validate_file_path(test_file)
        assert not FileUtils.validate_file_path("nonexistent.txt")
        
        # Test empty file
        empty_file = temp_dir / "empty.txt"
        empty_file.touch()
        assert not FileUtils.validate_file_path(empty_file)
    
    def test_get_file_info(self, temp_dir):
        """Test getting file information."""
        test_file = temp_dir / "test.jpg"
        test_file.write_text("test content")
        
        info = FileUtils.get_file_info(test_file)
        
        assert "error" not in info
        assert info["name"] == "test.jpg"
        assert info["suffix"] == ".jpg"
        assert info["is_image"] is True
        assert info["is_video"] is False
        assert info["media_type"] == "image"
        assert info["size_bytes"] > 0
    
    def test_get_file_info_nonexistent(self):
        """Test getting info for nonexistent file."""
        info = FileUtils.get_file_info("nonexistent.txt")
        
        assert "error" in info
        assert info["error"] == "File does not exist"
    
    def test_clean_filename(self):
        """Test filename cleaning."""
        assert FileUtils.clean_filename("test<>file.txt") == "test__file.txt"
        assert FileUtils.clean_filename("file:with|bad*chars") == "file_with_bad_chars"
        assert FileUtils.clean_filename("") == "untitled"
        assert FileUtils.clean_filename("   ") == "untitled"
        assert FileUtils.clean_filename("normal_file.txt") == "normal_file.txt"
    
    def test_create_unique_filename(self, temp_dir):
        """Test creating unique filenames."""
        # First call should return original name
        unique_path = FileUtils.create_unique_filename(temp_dir, "test", ".txt")
        assert unique_path == temp_dir / "test.txt"
        
        # Create the file and try again
        unique_path.touch()
        unique_path2 = FileUtils.create_unique_filename(temp_dir, "test", ".txt")
        assert unique_path2 == temp_dir / "test_1.txt"
    
    def test_copy_file_with_metadata(self, temp_dir):
        """Test file copying with metadata preservation."""
        source_file = temp_dir / "source.txt"
        source_file.write_text("test content")
        
        dest_file = temp_dir / "destination.txt"
        
        success = FileUtils.copy_file_with_metadata(source_file, dest_file)
        
        assert success
        assert dest_file.exists()
        assert dest_file.read_text() == "test content"
    
    def test_backup_file(self, temp_dir):
        """Test file backup creation."""
        original_file = temp_dir / "original.txt"
        original_file.write_text("original content")
        
        backup_path = FileUtils.backup_file(original_file)
        
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.read_text() == "original content"
        assert backup_path.name.endswith(".bak")
    
    def test_find_media_files(self, temp_dir):
        """Test finding media files in directory."""
        # Create test files
        (temp_dir / "image1.jpg").touch()
        (temp_dir / "image2.png").touch()
        (temp_dir / "video1.mp4").touch()
        (temp_dir / "document.txt").touch()
        
        # Find all media files
        media_files = FileUtils.find_media_files(temp_dir)
        
        assert len(media_files) == 3  # 2 images + 1 video
        
        # Find only images
        image_files = FileUtils.find_media_files(
            temp_dir, include_videos=False
        )
        assert len(image_files) == 2
        
        # Find only videos
        video_files = FileUtils.find_media_files(
            temp_dir, include_images=False
        )
        assert len(video_files) == 1
    
    def test_get_file_checksum(self, temp_dir):
        """Test file checksum calculation."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        checksum = FileUtils.get_file_checksum(test_file)
        
        assert checksum is not None
        assert len(checksum) == 32  # MD5 hex length
        
        # Same content should produce same checksum
        checksum2 = FileUtils.get_file_checksum(test_file)
        assert checksum == checksum2


if __name__ == "__main__":
    pytest.main([__file__]) 