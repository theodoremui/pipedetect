"""Pose overlay rendering utilities."""

from typing import List, Tuple, Optional
import cv2
import numpy as np
from loguru import logger

from ..core.models import LandmarkPoint, PoseResult
from ..detection.mediapipe_wrapper import MediaPipeWrapper


class OverlayRenderer:
    """Renders pose overlays on images and video frames."""
    
    # MediaPipe pose landmark connections
    POSE_CONNECTIONS = [
        # Face
        (0, 1), (1, 2), (2, 3), (3, 7),
        (0, 4), (4, 5), (5, 6), (6, 8),
        (9, 10),
        # Body
        (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
        (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
        (11, 23), (12, 24), (23, 24),
        # Legs
        (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
        (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
    ]
    
    def __init__(self, 
                 landmark_color: Tuple[int, int, int] = (0, 255, 0),
                 connection_color: Tuple[int, int, int] = (255, 0, 0),
                 landmark_size: int = 3,
                 connection_thickness: int = 2):
        """Initialize overlay renderer.
        
        Args:
            landmark_color: BGR color for landmarks
            connection_color: BGR color for connections
            landmark_size: Size of landmark circles
            connection_thickness: Thickness of connection lines
        """
        self.landmark_color = landmark_color
        self.connection_color = connection_color
        self.landmark_size = landmark_size
        self.connection_thickness = connection_thickness
    
    def render_pose_overlay(self, 
                          image: np.ndarray, 
                          landmarks: List[LandmarkPoint],
                          draw_landmarks: bool = True,
                          draw_connections: bool = True,
                          min_visibility: float = 0.5) -> np.ndarray:
        """Render pose overlay on image.
        
        Args:
            image: Input image
            landmarks: Pose landmarks
            draw_landmarks: Whether to draw landmark points
            draw_connections: Whether to draw connections
            min_visibility: Minimum visibility threshold for drawing
            
        Returns:
            Image with pose overlay
        """
        if not landmarks:
            return image.copy()
        
        overlay_image = image.copy()
        height, width = image.shape[:2]
        
        # Convert normalized coordinates to pixel coordinates
        pixel_landmarks = []
        for lm in landmarks:
            if lm.visibility >= min_visibility:
                x = int(lm.x * width)
                y = int(lm.y * height)
                pixel_landmarks.append((x, y, lm.visibility))
            else:
                pixel_landmarks.append(None)
        
        # Draw connections
        if draw_connections:
            for connection in self.POSE_CONNECTIONS:
                start_idx, end_idx = connection
                if (start_idx < len(pixel_landmarks) and 
                    end_idx < len(pixel_landmarks) and
                    pixel_landmarks[start_idx] is not None and
                    pixel_landmarks[end_idx] is not None):
                    
                    start_point = pixel_landmarks[start_idx][:2]
                    end_point = pixel_landmarks[end_idx][:2]
                    
                    cv2.line(overlay_image, start_point, end_point, 
                            self.connection_color, self.connection_thickness)
        
        # Draw landmarks
        if draw_landmarks:
            for i, pixel_lm in enumerate(pixel_landmarks):
                if pixel_lm is not None:
                    x, y, visibility = pixel_lm
                    # Adjust color intensity based on visibility
                    color_intensity = int(255 * visibility)
                    adjusted_color = (
                        min(self.landmark_color[0], color_intensity),
                        min(self.landmark_color[1], color_intensity),
                        min(self.landmark_color[2], color_intensity)
                    )
                    
                    cv2.circle(overlay_image, (x, y), self.landmark_size, 
                              adjusted_color, -1)
                    
                    # Optionally draw landmark index
                    if self.landmark_size > 3:
                        cv2.putText(overlay_image, str(i), (x + 5, y - 5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, 
                                   (255, 255, 255), 1)
        
        return overlay_image
    
    def render_pose_with_confidence(self, 
                                  image: np.ndarray,
                                  pose_result: PoseResult,
                                  show_confidence: bool = True) -> np.ndarray:
        """Render pose with confidence information.
        
        Args:
            image: Input image
            pose_result: Pose detection result
            show_confidence: Whether to display confidence text
            
        Returns:
            Image with pose overlay and confidence info
        """
        overlay_image = self.render_pose_overlay(image, pose_result.landmarks)
        
        if show_confidence:
            # Add confidence text
            confidence_text = f"Confidence: {pose_result.confidence:.3f}"
            cv2.putText(overlay_image, confidence_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Add frame info
            frame_text = f"Frame: {pose_result.frame_id}"
            cv2.putText(overlay_image, frame_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Add timestamp for videos
            if pose_result.timestamp > 0:
                time_text = f"Time: {pose_result.timestamp:.2f}s"
                cv2.putText(overlay_image, time_text, (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return overlay_image
    
    def create_pose_comparison(self, 
                             original: np.ndarray,
                             overlay: np.ndarray) -> np.ndarray:
        """Create side-by-side comparison of original and overlay images.
        
        Args:
            original: Original image
            overlay: Image with pose overlay
            
        Returns:
            Combined comparison image
        """
        # Ensure both images have the same height
        if original.shape[0] != overlay.shape[0]:
            target_height = min(original.shape[0], overlay.shape[0])
            original = cv2.resize(original, 
                                (int(original.shape[1] * target_height / original.shape[0]), 
                                 target_height))
            overlay = cv2.resize(overlay,
                               (int(overlay.shape[1] * target_height / overlay.shape[0]),
                                target_height))
        
        # Combine horizontally
        comparison = np.hstack((original, overlay))
        
        # Add labels
        cv2.putText(comparison, "Original", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        overlay_x = original.shape[1] + 10
        cv2.putText(comparison, "Pose Detection", (overlay_x, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return comparison 