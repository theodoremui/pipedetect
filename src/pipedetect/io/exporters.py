"""Exporters for pose detection results."""

import json
import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from loguru import logger

from ..core.models import PoseResult, ProcessingStats
from ..core.exceptions import OutputError


class BaseExporter(ABC):
    """Base class for result exporters."""
    
    @abstractmethod
    def export(self, results: List[PoseResult], output_path: Path, stats: ProcessingStats) -> None:
        """Export results to file.
        
        Args:
            results: List of pose detection results
            output_path: Output file path
            stats: Processing statistics
        """
        pass


class JSONExporter(BaseExporter):
    """Export results to JSON format."""
    
    def export(self, results: List[PoseResult], output_path: Path, stats: ProcessingStats) -> None:
        """Export results to JSON file.
        
        Args:
            results: List of pose detection results
            output_path: JSON output file path
            stats: Processing statistics
        """
        try:
            # Convert results to dictionary format
            export_data = {
                "metadata": {
                    "export_timestamp": datetime.now().isoformat(),
                    "total_frames": stats.total_frames,
                    "processed_frames": stats.processed_frames,
                    "failed_frames": stats.failed_frames,
                    "success_rate": stats.success_rate,
                    "processing_time_seconds": stats.processing_time,
                    "fps": stats.fps,
                    "start_time": stats.start_time.isoformat(),
                    "end_time": stats.end_time.isoformat()
                },
                "results": []
            }
            
            # Convert each result to dict
            for result in results:
                result_dict = {
                    "frame_id": result.frame_id,
                    "timestamp": result.timestamp,
                    "confidence": result.confidence,
                    "source_file": result.source_file,
                    "landmarks": []
                }
                
                # Convert landmarks
                for landmark in result.landmarks:
                    result_dict["landmarks"].append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility,
                        "presence": landmark.presence
                    })
                
                export_data["results"].append(result_dict)
            
            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(results)} results to JSON: {output_path}")
            
        except Exception as e:
            raise OutputError(f"Failed to export JSON to {output_path}: {str(e)}")


class CSVExporter(BaseExporter):
    """Export results to CSV format."""
    
    def export(self, results: List[PoseResult], output_path: Path, stats: ProcessingStats) -> None:
        """Export results to CSV file.
        
        Args:
            results: List of pose detection results
            output_path: CSV output file path
            stats: Processing statistics
        """
        if not results:
            logger.warning("No results to export to CSV")
            return
            
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                header = ['frame_id', 'timestamp', 'confidence', 'source_file']
                
                # Add landmark columns (MediaPipe has 33 pose landmarks)
                for i in range(33):
                    header.extend([
                        f'landmark_{i}_x', f'landmark_{i}_y', f'landmark_{i}_z',
                        f'landmark_{i}_visibility', f'landmark_{i}_presence'
                    ])
                
                writer.writerow(header)
                
                # Write results
                for result in results:
                    row = [
                        result.frame_id,
                        result.timestamp,
                        result.confidence,
                        result.source_file
                    ]
                    
                    # Add landmark data (pad with zeros if less than 33 landmarks)
                    for i in range(33):
                        if i < len(result.landmarks):
                            lm = result.landmarks[i]
                            row.extend([lm.x, lm.y, lm.z, lm.visibility, lm.presence])
                        else:
                            row.extend([0.0, 0.0, 0.0, 0.0, 0.0])
                    
                    writer.writerow(row)
            
            logger.info(f"Exported {len(results)} results to CSV: {output_path}")
            
        except Exception as e:
            raise OutputError(f"Failed to export CSV to {output_path}: {str(e)}")


class ExporterFactory:
    """Factory for creating exporters."""
    
    _exporters = {
        'json': JSONExporter,
        'csv': CSVExporter
    }
    
    @classmethod
    def create_exporter(cls, format_type: str) -> BaseExporter:
        """Create exporter for specified format.
        
        Args:
            format_type: Export format ('json' or 'csv')
            
        Returns:
            Exporter instance
            
        Raises:
            ValueError: If format is not supported
        """
        if format_type.lower() not in cls._exporters:
            raise ValueError(f"Unsupported export format: {format_type}")
        
        return cls._exporters[format_type.lower()]() 