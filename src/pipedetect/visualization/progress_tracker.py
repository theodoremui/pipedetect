"""Progress tracking utilities."""

import time
from typing import Optional
import sys

from rich.progress import Progress, TaskID, BarColumn, TextColumn, TimeRemainingColumn
from rich.console import Console
from loguru import logger


class ProgressTracker:
    """Tracks and displays processing progress."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize progress tracker.
        
        Args:
            console: Rich console instance (optional)
        """
        self.console = console or Console()
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
        self.start_time: Optional[float] = None
        
    def start(self, total: int, description: str = "Processing") -> None:
        """Start progress tracking.
        
        Args:
            total: Total number of items to process
            description: Progress description
        """
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            TimeRemainingColumn(),
            "•",
            "[bold green]{task.completed}/{task.total}",
            console=self.console
        )
        
        self.progress.start()
        self.task_id = self.progress.add_task(description, total=total)
        self.start_time = time.time()
        
        logger.info(f"Started processing {total} items")
    
    def update(self, advance: int = 1, description: Optional[str] = None) -> None:
        """Update progress.
        
        Args:
            advance: Number of items completed
            description: Updated description (optional)
        """
        if self.progress and self.task_id is not None:
            if description:
                self.progress.update(self.task_id, description=description)
            self.progress.update(self.task_id, advance=advance)
    
    def set_status(self, status: str) -> None:
        """Set current status message.
        
        Args:
            status: Status message
        """
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, description=status)
    
    def finish(self) -> float:
        """Finish progress tracking.
        
        Returns:
            Total processing time in seconds
        """
        processing_time = 0.0
        
        if self.start_time:
            processing_time = time.time() - self.start_time
        
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.task_id = None
        
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        return processing_time
    
    def is_active(self) -> bool:
        """Check if progress tracking is active.
        
        Returns:
            True if progress tracking is active
        """
        return self.progress is not None and self.task_id is not None
    
    def get_current_progress(self) -> dict:
        """Get current progress information.
        
        Returns:
            Dictionary with progress information
        """
        if not self.is_active():
            return {}
        
        task = self.progress.tasks[self.task_id]
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        return {
            'completed': task.completed,
            'total': task.total,
            'percentage': task.percentage,
            'elapsed_time': elapsed_time,
            'remaining_time': task.time_remaining or 0
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.finish() 