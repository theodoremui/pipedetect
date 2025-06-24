"""File management utilities."""

from pathlib import Path
from datetime import datetime
from typing import List
import shutil

import cv2
import numpy as np
from loguru import logger

from ..core.models import OutputPaths
from ..core.exceptions import OutputError, FileProcessingError


class FileManager:
    """Manages file operations for pose detection outputs."""
    
    @staticmethod
    def generate_timestamp() -> str:
        """Generate timestamp string for filenames.
        
        Returns:
            Timestamp string in format YYYYMMDD_HHMMSS
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def create_output_paths(
        output_dir: Path,
        source_name: str,
        json_filename: str = None,
        csv_filename: str = None
    ) -> OutputPaths:
        """Create output paths for all file types.
        
        Args:
            output_dir: Base output directory
            source_name: Name of source file/directory
            json_filename: Custom JSON filename (optional)
            csv_filename: Custom CSV filename (optional)
            
        Returns:
            OutputPaths object with all paths
        """
        timestamp = FileManager.generate_timestamp()
        base_name = Path(source_name).stem
        
        # Generate default filenames if not provided
        if json_filename is None:
            json_filename = f"pose_{base_name}_{timestamp}.json"
        if csv_filename is None:
            csv_filename = f"pose_{base_name}_{timestamp}.csv"
        
        # Create paths
        paths = OutputPaths(
            json_file=output_dir / json_filename,
            csv_file=output_dir / csv_filename,
            frames_dir=output_dir / f"frames_{base_name}_{timestamp}",
            overlay_dir=output_dir / f"overlay_{base_name}_{timestamp}"
        )
        
        # Create directories
        paths.create_directories()
        
        logger.info(f"Created output paths for {source_name}")
        return paths
    
    @staticmethod
    def save_frame(frame: np.ndarray, output_path: Path, frame_id: int) -> None:
        """Save video frame to file.
        
        Args:
            frame: Frame data as numpy array
            output_path: Output directory path
            frame_id: Frame identifier
            
        Raises:
            OutputError: If frame cannot be saved
        """
        try:
            frame_filename = f"frame_{frame_id:06d}.jpg"
            frame_path = output_path / frame_filename
            
            # Ensure directory exists
            frame_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save frame
            success = cv2.imwrite(str(frame_path), frame)
            if not success:
                raise OutputError(f"Failed to save frame {frame_id}")
            
            logger.debug(f"Saved frame {frame_id} to {frame_path}")
            
        except Exception as e:
            if isinstance(e, OutputError):
                raise
            raise OutputError(f"Error saving frame {frame_id}: {str(e)}")
    
    @staticmethod
    def save_overlay_frame(
        overlay_frame: np.ndarray, 
        output_path: Path, 
        frame_id: int
    ) -> None:
        """Save overlay frame to file.
        
        Args:
            overlay_frame: Frame with pose overlay
            output_path: Output directory path
            frame_id: Frame identifier
            
        Raises:
            OutputError: If overlay frame cannot be saved
        """
        try:
            overlay_filename = f"overlay_{frame_id:06d}.jpg"
            overlay_path = output_path / overlay_filename
            
            # Ensure directory exists
            overlay_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save overlay frame
            success = cv2.imwrite(str(overlay_path), overlay_frame)
            if not success:
                raise OutputError(f"Failed to save overlay frame {frame_id}")
            
            logger.debug(f"Saved overlay frame {frame_id} to {overlay_path}")
            
        except Exception as e:
            if isinstance(e, OutputError):
                raise
            raise OutputError(f"Error saving overlay frame {frame_id}: {str(e)}")
    
    @staticmethod
    def save_image_copy(source_path: Path, output_path: Path, frame_id: int) -> None:
        """Save copy of source image to frames directory.
        
        Args:
            source_path: Source image path
            output_path: Output directory path
            frame_id: Frame identifier
            
        Raises:
            FileProcessingError: If image cannot be copied
        """
        try:
            frame_filename = f"frame_{frame_id:06d}{source_path.suffix}"
            frame_path = output_path / frame_filename
            
            # Ensure directory exists
            frame_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, frame_path)
            
            logger.debug(f"Copied image {source_path} to {frame_path}")
            
        except Exception as e:
            raise FileProcessingError(f"Error copying image {source_path}: {str(e)}")
    
    @staticmethod
    def cleanup_empty_directories(output_paths: OutputPaths) -> None:
        """Remove empty output directories.
        
        Args:
            output_paths: Output paths to check and clean
        """
        try:
            # Check and remove empty directories
            for dir_path in [output_paths.frames_dir, output_paths.overlay_dir]:
                if dir_path.exists() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logger.debug(f"Removed empty directory: {dir_path}")
                    
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")
    
    @staticmethod
    def get_file_size_mb(file_path: Path) -> float:
        """Get file size in MB.
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in megabytes
        """
        try:
            if file_path.exists():
                return file_path.stat().st_size / (1024 * 1024)
            return 0.0
        except Exception:
            return 0.0 