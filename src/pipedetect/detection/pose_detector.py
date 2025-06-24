"""High-level pose detector interface."""

from typing import List, Optional, Iterator, Tuple
from pathlib import Path
import time

import cv2
import numpy as np
from loguru import logger

from ..core.models import PoseResult, DetectionConfig, ProcessingStats
from ..core.exceptions import DetectionError, FileProcessingError
from .mediapipe_wrapper import MediaPipeWrapper


class PoseDetector:
    """High-level pose detector with batch processing capabilities."""
    
    def __init__(self, config: DetectionConfig):
        """Initialize pose detector.
        
        Args:
            config: Detection configuration
        """
        self.config = config
        self._mediapipe = MediaPipeWrapper(config)
        logger.info("PoseDetector initialized")
    
    def detect_single_image(self, image_path: Path, frame_id: int = 0) -> Optional[PoseResult]:
        """Detect pose in a single image file.
        
        Args:
            image_path: Path to image file
            frame_id: Frame identifier
            
        Returns:
            PoseResult or None if no pose detected
            
        Raises:
            FileProcessingError: If image cannot be loaded
            DetectionError: If detection fails
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise FileProcessingError(f"Cannot load image: {image_path}")
            
            # Detect pose
            landmarks = self._mediapipe.detect_pose(image)
            if landmarks is None:
                logger.debug(f"No pose detected in {image_path}")
                return None
            
            # Calculate confidence (simplified - use average visibility)
            confidence = sum(lm.visibility for lm in landmarks) / len(landmarks)
            
            result = PoseResult(
                frame_id=frame_id,
                timestamp=0.0,  # Static image
                landmarks=landmarks,
                confidence=confidence,
                source_file=str(image_path)
            )
            
            logger.debug(f"Pose detected in {image_path} with confidence {confidence:.3f}")
            return result
            
        except Exception as e:
            if isinstance(e, (FileProcessingError, DetectionError)):
                raise
            raise DetectionError(f"Failed to process image {image_path}: {str(e)}")
    
    def detect_video(self, video_path: Path) -> Iterator[Tuple[PoseResult, np.ndarray]]:
        """Detect poses in video file.
        
        Args:
            video_path: Path to video file
            
        Yields:
            Tuple of (PoseResult, frame) for each frame with detected pose
            
        Raises:
            FileProcessingError: If video cannot be loaded
            DetectionError: If detection fails
        """
        cap = None
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise FileProcessingError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            actual_frame_number = 0
            
            logger.info(f"Processing video {video_path} at {fps:.2f} FPS")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect pose
                landmarks = self._mediapipe.detect_pose(frame)
                if landmarks is not None:
                    confidence = sum(lm.visibility for lm in landmarks) / len(landmarks)
                    
                    # Use the ACTUAL frame number from the video, not a sequential counter
                    result = PoseResult(
                        frame_id=actual_frame_number,  # This is the real frame number in the video
                        timestamp=actual_frame_number / fps,
                        landmarks=landmarks,
                        confidence=confidence,
                        source_file=str(video_path)
                    )
                    
                    # Yield both result and the actual frame that was processed
                    yield result, frame.copy()
                
                actual_frame_number += 1
                
        except Exception as e:
            if isinstance(e, (FileProcessingError, DetectionError)):
                raise
            raise DetectionError(f"Failed to process video {video_path}: {str(e)}")
        finally:
            if cap is not None:
                cap.release()
    
    def detect_batch_images(self, image_dir: Path) -> Iterator[PoseResult]:
        """Detect poses in a directory of images.
        
        Args:
            image_dir: Directory containing images
            
        Yields:
            PoseResult for each image with detected pose
        """
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        image_files = []
        for ext in supported_extensions:
            image_files.extend(image_dir.glob(f"*{ext}"))
            image_files.extend(image_dir.glob(f"*{ext.upper()}"))
        
        image_files.sort()  # Process in alphabetical order
        
        logger.info(f"Found {len(image_files)} images in {image_dir}")
        
        for frame_id, image_path in enumerate(image_files):
            result = self.detect_single_image(image_path, frame_id)
            if result is not None:
                yield result
    
    def get_frame_from_video(self, video_path: Path, frame_id: int) -> Optional[np.ndarray]:
        """Extract a specific frame from video.
        
        Args:
            video_path: Path to video file
            frame_id: Frame number to extract
            
        Returns:
            Frame as numpy array or None if frame not found
        """
        cap = None
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return None
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
            ret, frame = cap.read()
            
            return frame if ret else None
            
        except Exception as e:
            logger.warning(f"Failed to extract frame {frame_id} from {video_path}: {e}")
            return None
        finally:
            if cap is not None:
                cap.release()
    
    def close(self) -> None:
        """Clean up resources."""
        self._mediapipe.close()
        logger.info("PoseDetector closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 