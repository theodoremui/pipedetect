"""Main pose processing orchestrator."""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Iterator, Optional

import cv2
from loguru import logger

from ..core.models import (
    DetectionConfig, PoseResult, ProcessingStats, OutputPaths
)
from ..core.exceptions import PipeDetectError, ValidationError, FileProcessingError
from ..detection.pose_detector import PoseDetector
from ..io.validators import InputValidator
from ..io.exporters import JSONExporter, CSVExporter
from ..io.file_manager import FileManager
from ..visualization.overlay_renderer import OverlayRenderer
from ..visualization.progress_tracker import ProgressTracker
from ..utils.performance import PerformanceProfiler


class PoseProcessor:
    """Main processor for pose detection pipeline."""
    
    def __init__(self, 
                 config: DetectionConfig,
                 output_dir: Path,
                 save_frames: bool = True,
                 save_overlays: bool = True,
                 show_progress: bool = True):
        """Initialize pose processor.
        
        Args:
            config: Detection configuration
            output_dir: Output directory
            save_frames: Whether to save individual frames
            save_overlays: Whether to save overlay frames
            show_progress: Whether to show progress bar
        """
        self.config = config
        self.output_dir = output_dir
        self.save_frames = save_frames
        self.save_overlays = save_overlays
        self.show_progress = show_progress
        
        # Initialize components
        self.pose_detector = PoseDetector(config)
        self.overlay_renderer = OverlayRenderer()
        self.json_exporter = JSONExporter()
        self.csv_exporter = CSVExporter()
        self.progress_tracker = ProgressTracker() if show_progress else None
        self.profiler = PerformanceProfiler()
        
        logger.info("PoseProcessor initialized")
    
    def process_input(self, 
                     input_path: Path,
                     json_output: Optional[str] = None,
                     csv_output: Optional[str] = None) -> ProcessingStats:
        """Process input file or directory.
        
        Args:
            input_path: Input file or directory path
            json_output: Custom JSON output filename
            csv_output: Custom CSV output filename
            
        Returns:
            Processing statistics
            
        Raises:
            PipeDetectError: If processing fails
        """
        try:
            # Validate input
            input_path = InputValidator.validate_input_path(input_path)
            input_type = InputValidator.get_input_type(input_path)
            
            # Create output paths
            output_paths = FileManager.create_output_paths(
                self.output_dir,
                input_path.name,
                json_output,
                csv_output
            )
            
            logger.info(f"Processing {input_type}: {input_path}")
            logger.info(f"Output directory: {self.output_dir}")
            
            # Start profiling
            self.profiler.start()
            start_time = datetime.now()
            
            # Process based on input type
            if input_type == 'video':
                results = list(self._process_video(input_path, output_paths))
            elif input_type == 'image':
                results = list(self._process_single_image(input_path, output_paths))
            elif input_type == 'directory':
                results = list(self._process_image_directory(input_path, output_paths))
            else:
                raise ValidationError(f"Unsupported input type: {input_type}")
            
            # Stop profiling
            performance_metrics = self.profiler.stop()
            end_time = datetime.now()
            
            # Create processing statistics
            stats = ProcessingStats(
                total_frames=performance_metrics.frames_processed,
                processed_frames=len(results),
                failed_frames=performance_metrics.frames_processed - len(results),
                processing_time=performance_metrics.processing_time,
                fps=performance_metrics.fps,
                start_time=start_time,
                end_time=end_time
            )
            
            # Export results
            self._export_results(results, output_paths, stats)
            
            # Cleanup empty directories
            FileManager.cleanup_empty_directories(output_paths)
            
            logger.info(f"Processing completed successfully!")
            logger.info(f"Processed {stats.processed_frames}/{stats.total_frames} frames "
                       f"({stats.success_rate:.1%} success rate)")
            logger.info(f"Average FPS: {stats.fps:.1f}")
            
            return stats
            
        except Exception as e:
            if isinstance(e, PipeDetectError):
                raise
            raise PipeDetectError(f"Processing failed: {str(e)}")
    
    def _process_video(self, video_path: Path, output_paths: OutputPaths) -> Iterator[PoseResult]:
        """Process video file.
        
        Args:
            video_path: Path to video file
            output_paths: Output file paths
            
        Yields:
            PoseResult for each detected pose
        """
        try:
            # Get video info for progress tracking
            cap = cv2.VideoCapture(str(video_path))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if self.progress_tracker:
                self.progress_tracker.start(total_frames, f"Processing {video_path.name}")
            
            # Process ALL video frames starting from frame 0
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise FileProcessingError(f"Cannot open video: {video_path}")
            
            saved_frame_counter = 0
            detected_poses = []
            
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    self.profiler.increment_frame_count()
                    
                    # Save original frame if requested (ALL frames, starting from 0)
                    if self.save_frames:
                        FileManager.save_frame(frame, output_paths.frames_dir, saved_frame_counter)
                    
                    # Try to detect pose in this frame
                    landmarks = self.pose_detector._mediapipe.detect_pose(frame)
                    
                    if landmarks is not None:
                        # Calculate confidence
                        confidence = sum(lm.visibility for lm in landmarks) / len(landmarks)
                        
                        # Create pose result
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        result = PoseResult(
                            frame_id=saved_frame_counter,  # Use sequential frame number
                            timestamp=saved_frame_counter / fps,
                            landmarks=landmarks,
                            confidence=confidence,
                            source_file=str(video_path)
                        )
                        
                        detected_poses.append(result)
                        
                        # Save overlay frame if requested
                        if self.save_overlays:
                            overlay_frame = self.overlay_renderer.render_pose_with_confidence(
                                frame, result
                            )
                            FileManager.save_overlay_frame(
                                overlay_frame, output_paths.overlay_dir, saved_frame_counter
                            )
                    else:
                        # No pose detected, but still save overlay frame with just the original frame
                        if self.save_overlays:
                            FileManager.save_overlay_frame(
                                frame, output_paths.overlay_dir, saved_frame_counter
                            )
                    
                    if self.progress_tracker:
                        self.progress_tracker.update()
                    
                    saved_frame_counter += 1
                    
            finally:
                cap.release()
            
            # Yield all detected poses
            for result in detected_poses:
                yield result
                
        finally:
            if self.progress_tracker:
                self.progress_tracker.finish()
    
    def _process_single_image(self, image_path: Path, output_paths: OutputPaths) -> Iterator[PoseResult]:
        """Process single image file.
        
        Args:
            image_path: Path to image file
            output_paths: Output file paths
            
        Yields:
            PoseResult if pose detected
        """
        if self.progress_tracker:
            self.progress_tracker.start(1, f"Processing {image_path.name}")
        
        try:
            result = self.pose_detector.detect_single_image(image_path)
            self.profiler.increment_frame_count()
            
            if result is not None:
                # Save original image copy if requested (always use 0 for single image)
                if self.save_frames:
                    FileManager.save_image_copy(image_path, output_paths.frames_dir, 0)
                
                # Save overlay image if requested (always use 0 for single image)
                if self.save_overlays:
                    image = cv2.imread(str(image_path))
                    if image is not None:
                        overlay_image = self.overlay_renderer.render_pose_with_confidence(
                            image, result
                        )
                        FileManager.save_overlay_frame(
                            overlay_image, output_paths.overlay_dir, 0
                        )
                
                yield result
            
            if self.progress_tracker:
                self.progress_tracker.update()
                
        finally:
            if self.progress_tracker:
                self.progress_tracker.finish()
    
    def _process_image_directory(self, dir_path: Path, output_paths: OutputPaths) -> Iterator[PoseResult]:
        """Process directory of images.
        
        Args:
            dir_path: Directory path
            output_paths: Output file paths
            
        Yields:
            PoseResult for each detected pose
        """
        # Get list of image files
        image_files = InputValidator.validate_image_directory(dir_path)
        
        if self.progress_tracker:
            self.progress_tracker.start(len(image_files), f"Processing {dir_path.name}")
        
        try:
            saved_frame_counter = 0  # Counter for saved frames starting from 0
            for frame_id, image_path in enumerate(image_files):
                result = self.pose_detector.detect_single_image(image_path, frame_id)
                self.profiler.increment_frame_count()
                
                if result is not None:
                    # Save original image copy if requested (using sequential counter)
                    if self.save_frames:
                        FileManager.save_image_copy(image_path, output_paths.frames_dir, saved_frame_counter)
                    
                    # Save overlay image if requested (using sequential counter)
                    if self.save_overlays:
                        image = cv2.imread(str(image_path))
                        if image is not None:
                            overlay_image = self.overlay_renderer.render_pose_with_confidence(
                                image, result
                            )
                            FileManager.save_overlay_frame(
                                overlay_image, output_paths.overlay_dir, saved_frame_counter
                            )
                    
                    saved_frame_counter += 1  # Increment counter for saved frames
                    yield result
                
                if self.progress_tracker:
                    self.progress_tracker.update()
                
        finally:
            if self.progress_tracker:
                self.progress_tracker.finish()
    
    def _export_results(self, 
                       results: List[PoseResult], 
                       output_paths: OutputPaths,
                       stats: ProcessingStats) -> None:
        """Export processing results.
        
        Args:
            results: List of pose detection results
            output_paths: Output file paths
            stats: Processing statistics
        """
        try:
            # Export JSON
            if results:
                self.json_exporter.export(results, output_paths.json_file, stats)
                self.csv_exporter.export(results, output_paths.csv_file, stats)
                
                logger.info(f"Results exported:")
                logger.info(f"  JSON: {output_paths.json_file}")
                logger.info(f"  CSV: {output_paths.csv_file}")
                
                if self.save_frames:
                    logger.info(f"  Frames: {output_paths.frames_dir}")
                if self.save_overlays:
                    logger.info(f"  Overlays: {output_paths.overlay_dir}")
            else:
                logger.warning("No pose detection results to export")
                
        except Exception as e:
            logger.error(f"Failed to export results: {str(e)}")
            raise
    
    def close(self) -> None:
        """Clean up resources."""
        self.pose_detector.close()
        logger.info("PoseProcessor closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 