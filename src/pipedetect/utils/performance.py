"""Performance profiling utilities."""

import time
import psutil
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager

from loguru import logger


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    processing_time: float = 0.0
    fps: float = 0.0
    frames_processed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_mb': self.memory_mb,
            'processing_time': self.processing_time,
            'fps': self.fps, 
            'frames_processed': self.frames_processed
        }


class PerformanceProfiler:
    """Profiles performance during pose detection."""
    
    def __init__(self, enable_monitoring: bool = True):
        """Initialize performance profiler.
        
        Args:
            enable_monitoring: Whether to enable system monitoring
        """
        self.enable_monitoring = enable_monitoring
        self.metrics = PerformanceMetrics()
        self._start_time: Optional[float] = None
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        self._cpu_samples = []
        self._memory_samples = []
        
    def start(self) -> None:
        """Start performance monitoring."""
        self._start_time = time.time()
        self._stop_monitoring.clear()
        
        if self.enable_monitoring:
            self._monitoring_thread = threading.Thread(
                target=self._monitor_system_resources,
                daemon=True
            )
            self._monitoring_thread.start()
            
        logger.debug("Performance monitoring started")
    
    def stop(self) -> PerformanceMetrics:
        """Stop performance monitoring and return metrics.
        
        Returns:
            Performance metrics
        """
        if self._start_time:
            self.metrics.processing_time = time.time() - self._start_time
        
        if self.enable_monitoring:
            self._stop_monitoring.set()
            
            if self._monitoring_thread and self._monitoring_thread.is_alive():
                self._monitoring_thread.join(timeout=1.0)
            
            # Calculate averages
            if self._cpu_samples:
                self.metrics.cpu_percent = sum(self._cpu_samples) / len(self._cpu_samples)
            
            if self._memory_samples:
                self.metrics.memory_percent = sum(s[0] for s in self._memory_samples) / len(self._memory_samples)
                self.metrics.memory_mb = sum(s[1] for s in self._memory_samples) / len(self._memory_samples)
        
        # Calculate FPS
        if self.metrics.processing_time > 0:
            self.metrics.fps = self.metrics.frames_processed / self.metrics.processing_time
        
        logger.info(f"Performance monitoring stopped. Processed {self.metrics.frames_processed} frames "
                   f"in {self.metrics.processing_time:.2f}s at {self.metrics.fps:.1f} FPS")
        
        return self.metrics
    
    def update_frame_count(self, frames_processed: int) -> None:
        """Update the number of frames processed.
        
        Args:
            frames_processed: Total frames processed so far
        """
        self.metrics.frames_processed = frames_processed
    
    def increment_frame_count(self) -> None:
        """Increment frame count by 1."""
        self.metrics.frames_processed += 1
    
    def _monitor_system_resources(self) -> None:
        """Monitor system resources in background thread."""
        process = psutil.Process()
        
        while not self._stop_monitoring.is_set():
            try:
                # CPU usage
                cpu_percent = process.cpu_percent()
                self._cpu_samples.append(cpu_percent)
                
                # Memory usage
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                memory_mb = memory_info.rss / (1024 * 1024)
                self._memory_samples.append((memory_percent, memory_mb))
                
                # Sample every 0.5 seconds
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error monitoring system resources: {e}")
                break
    
    @contextmanager
    def profile_operation(self, operation_name: str):
        """Context manager for profiling specific operations.
        
        Args:
            operation_name: Name of the operation being profiled
        """
        start_time = time.time()
        logger.debug(f"Starting operation: {operation_name}")
        
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            logger.debug(f"Operation '{operation_name}' completed in {elapsed:.3f}s")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics.
        
        Returns:
            Dictionary with current metrics
        """
        current_time = time.time()
        if self._start_time:
            elapsed = current_time - self._start_time
            current_fps = self.metrics.frames_processed / elapsed if elapsed > 0 else 0
        else:
            elapsed = 0
            current_fps = 0
        
        return {
            'elapsed_time': elapsed,
            'frames_processed': self.metrics.frames_processed,
            'current_fps': current_fps,
            'cpu_percent': self._cpu_samples[-1] if self._cpu_samples else 0,
            'memory_mb': self._memory_samples[-1][1] if self._memory_samples else 0
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop() 