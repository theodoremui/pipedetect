"""MediaPipe wrapper for pose detection."""

from typing import Optional, List
import cv2
import numpy as np
import mediapipe as mp
from loguru import logger

from ..core.models import DetectionConfig, LandmarkPoint
from ..core.exceptions import DetectionError, ConfigurationError


class MediaPipeWrapper:
    """Wrapper around MediaPipe pose detection."""
    
    def __init__(self, config: DetectionConfig):
        """Initialize MediaPipe pose detector.
        
        Args:
            config: Detection configuration
        """
        self.config = config
        self._mp_pose = mp.solutions.pose
        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_drawing_styles = mp.solutions.drawing_styles
        
        try:
            self._pose = self._mp_pose.Pose(
                static_image_mode=False,
                model_complexity=config.model_complexity,
                enable_segmentation=config.enable_segmentation,
                smooth_landmarks=config.smooth_landmarks,
                min_detection_confidence=config.min_detection_confidence,
                min_tracking_confidence=config.min_tracking_confidence
            )
            logger.info(f"MediaPipe pose detector initialized with config: {config}")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize MediaPipe: {str(e)}")
    
    def detect_pose(self, image: np.ndarray) -> Optional[List[LandmarkPoint]]:
        """Detect pose in a single image.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of landmark points or None if no pose detected
            
        Raises:
            DetectionError: If detection fails
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Perform pose detection
            results = self._pose.process(rgb_image)
            
            if not results.pose_landmarks:
                return None
                
            # Convert landmarks to our format
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append(LandmarkPoint(
                    x=landmark.x,
                    y=landmark.y, 
                    z=landmark.z,
                    visibility=landmark.visibility,
                    presence=getattr(landmark, 'presence', 1.0)  # Fallback for older versions
                ))
                
            return landmarks
            
        except Exception as e:
            raise DetectionError(f"Pose detection failed: {str(e)}")
    
    def draw_landmarks(self, image: np.ndarray, landmarks: List[LandmarkPoint]) -> np.ndarray:
        """Draw pose landmarks on image.
        
        Args:
            image: Input image
            landmarks: Pose landmarks
            
        Returns:
            Image with drawn landmarks
        """
        try:
            # Convert our landmarks back to MediaPipe format for drawing
            mp_landmarks = self._mp_pose.PoseLandmark
            landmark_list = []
            
            for lm in landmarks:
                # Create a mock landmark object
                mock_landmark = type('MockLandmark', (), {
                    'x': lm.x, 'y': lm.y, 'z': lm.z, 
                    'visibility': lm.visibility
                })()
                landmark_list.append(mock_landmark)
            
            # Create pose landmarks object
            pose_landmarks = type('PoseLandmarks', (), {
                'landmark': landmark_list
            })()
            
            # Draw landmarks
            annotated_image = image.copy()
            self._mp_drawing.draw_landmarks(
                annotated_image,
                pose_landmarks,
                self._mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self._mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            return annotated_image
            
        except Exception as e:
            logger.warning(f"Failed to draw landmarks: {str(e)}")
            return image
    
    def close(self) -> None:
        """Clean up resources."""
        if hasattr(self, '_pose'):
            self._pose.close()
            logger.debug("MediaPipe pose detector closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 