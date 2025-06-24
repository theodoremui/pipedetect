"""Input validation utilities."""

from pathlib import Path
from typing import List, Union
import mimetypes

from loguru import logger

from ..core.exceptions import ValidationError


class InputValidator:
    """Validates input files and directories."""
    
    SUPPORTED_IMAGE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'
    }
    
    SUPPORTED_VIDEO_EXTENSIONS = {
        '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'
    }
    
    @classmethod
    def validate_input_path(cls, input_path: Union[str, Path]) -> Path:
        """Validate and convert input path.
        
        Args:
            input_path: Input file or directory path
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If path is invalid
        """
        try:
            path = Path(input_path)
            
            if not path.exists():
                raise ValidationError(f"Input path does not exist: {path}")
            
            return path
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Invalid input path '{input_path}': {str(e)}")
    
    @classmethod
    def validate_output_path(cls, output_path: Union[str, Path]) -> Path:
        """Validate output path and create parent directories.
        
        Args:
            output_path: Output file path
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If path is invalid
        """
        try:
            path = Path(output_path)
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            return path
            
        except Exception as e:
            raise ValidationError(f"Invalid output path '{output_path}': {str(e)}")
    
    @classmethod
    def is_image_file(cls, file_path: Path) -> bool:
        """Check if file is a supported image format.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is a supported image
        """
        if not file_path.is_file():
            return False
        
        return file_path.suffix.lower() in cls.SUPPORTED_IMAGE_EXTENSIONS
    
    @classmethod
    def is_video_file(cls, file_path: Path) -> bool:
        """Check if file is a supported video format.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is a supported video
        """
        if not file_path.is_file():
            return False
        
        return file_path.suffix.lower() in cls.SUPPORTED_VIDEO_EXTENSIONS
    
    @classmethod
    def get_input_type(cls, input_path: Path) -> str:
        """Determine input type (image, video, or directory).
        
        Args:
            input_path: Input path to analyze
            
        Returns:
            Input type: 'image', 'video', or 'directory'
            
        Raises:
            ValidationError: If input type cannot be determined
        """
        if input_path.is_file():
            if cls.is_image_file(input_path):
                return 'image'
            elif cls.is_video_file(input_path):
                return 'video'
            else:
                raise ValidationError(f"Unsupported file format: {input_path}")
        
        elif input_path.is_dir():
            return 'directory'
        
        else:
            raise ValidationError(f"Input is neither file nor directory: {input_path}")
    
    @classmethod
    def validate_image_directory(cls, dir_path: Path) -> List[Path]:
        """Validate directory contains image files.
        
        Args:
            dir_path: Directory path to validate
            
        Returns:
            List of valid image files
            
        Raises:
            ValidationError: If directory contains no valid images
        """
        if not dir_path.is_dir():
            raise ValidationError(f"Not a directory: {dir_path}")
        
        image_files = []
        for file_path in dir_path.iterdir():
            if cls.is_image_file(file_path):
                image_files.append(file_path)
        
        if not image_files:
            raise ValidationError(f"No supported image files found in: {dir_path}")
        
        logger.info(f"Found {len(image_files)} image files in {dir_path}")
        return sorted(image_files)
    
    @classmethod
    def validate_confidence_threshold(cls, confidence: float) -> float:
        """Validate confidence threshold value.
        
        Args:
            confidence: Confidence threshold to validate
            
        Returns:
            Validated confidence value
            
        Raises:
            ValidationError: If confidence is invalid
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValidationError(f"Confidence must be between 0.0 and 1.0, got: {confidence}")
        
        return confidence 