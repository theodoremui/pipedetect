"""Tests for result exporters."""

import pytest
import json
import csv
import tempfile
from pathlib import Path
from datetime import datetime

from pipedetect.io.exporters import JSONExporter, CSVExporter, ExporterFactory
from pipedetect.core.models import PoseResult, LandmarkPoint, ProcessingStats


@pytest.fixture
def sample_landmarks():
    """Create sample landmarks for testing."""
    return [
        LandmarkPoint(x=0.5, y=0.3, z=0.1, visibility=0.9, presence=0.8),
        LandmarkPoint(x=0.6, y=0.4, z=0.2, visibility=0.8, presence=0.9)
    ]


@pytest.fixture
def sample_pose_result(sample_landmarks):
    """Create sample pose result for testing."""
    return PoseResult(
        frame_id=1,
        timestamp=1.5,
        landmarks=sample_landmarks,
        confidence=0.95,
        source_file="test.jpg"
    )


@pytest.fixture
def sample_stats():
    """Create sample processing stats for testing."""
    now = datetime.now()
    return ProcessingStats(
        total_frames=10,
        processed_frames=8,
        failed_frames=2,
        processing_time=5.0,
        fps=2.0,
        start_time=now,
        end_time=now
    )


class TestJSONExporter:
    """Test JSON exporter functionality."""
    
    def test_export_json(self, sample_pose_result, sample_stats):
        """Test JSON export functionality."""
        exporter = JSONExporter()
        results = [sample_pose_result]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output.json"
            
            exporter.export(results, output_path, sample_stats)
            
            # Verify file was created
            assert output_path.exists()
            
            # Verify content
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert "metadata" in data
            assert "results" in data
            assert len(data["results"]) == 1
            
            # Check metadata
            metadata = data["metadata"]
            assert metadata["total_frames"] == 10
            assert metadata["processed_frames"] == 8
            assert metadata["success_rate"] == 0.8
            
            # Check result data
            result = data["results"][0]
            assert result["frame_id"] == 1
            assert result["timestamp"] == 1.5
            assert result["confidence"] == 0.95
            assert result["source_file"] == "test.jpg"
            assert len(result["landmarks"]) == 2
            
            # Check landmark data
            landmark = result["landmarks"][0]
            assert landmark["x"] == 0.5
            assert landmark["y"] == 0.3
            assert landmark["visibility"] == 0.9
    
    def test_export_empty_results(self, sample_stats):
        """Test exporting empty results."""
        exporter = JSONExporter()
        results = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "empty_output.json"
            
            exporter.export(results, output_path, sample_stats)
            
            # Verify file was created
            assert output_path.exists()
            
            # Verify content
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert len(data["results"]) == 0


class TestCSVExporter:
    """Test CSV exporter functionality."""
    
    def test_export_csv(self, sample_pose_result, sample_stats):
        """Test CSV export functionality."""
        exporter = CSVExporter()
        results = [sample_pose_result]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output.csv"
            
            exporter.export(results, output_path, sample_stats)
            
            # Verify file was created
            assert output_path.exists()
            
            # Verify content
            with open(output_path, 'r', newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Should have header + 1 data row
            assert len(rows) == 2
            
            # Check header
            header = rows[0]
            assert 'frame_id' in header
            assert 'timestamp' in header
            assert 'confidence' in header
            assert 'source_file' in header
            assert 'landmark_0_x' in header
            assert 'landmark_0_y' in header
            
            # Check data row
            data_row = rows[1]
            assert data_row[0] == '1'  # frame_id
            assert data_row[1] == '1.5'  # timestamp
            assert data_row[2] == '0.95'  # confidence
            assert data_row[3] == 'test.jpg'  # source_file
    
    def test_export_empty_csv(self, sample_stats):
        """Test exporting empty CSV results."""
        exporter = CSVExporter()
        results = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "empty_output.csv"
            
            # Should not create file for empty results
            exporter.export(results, output_path, sample_stats)
            # The method returns early for empty results, so no file should be created
    
    def test_csv_landmark_padding(self, sample_stats):
        """Test CSV export with fewer than 33 landmarks."""
        # Create result with only 1 landmark
        landmark = LandmarkPoint(x=0.5, y=0.3, z=0.1, visibility=0.9, presence=0.8)
        pose_result = PoseResult(
            frame_id=1, timestamp=1.0, landmarks=[landmark],
            confidence=0.9, source_file="test.jpg"
        )
        
        exporter = CSVExporter()
        results = [pose_result]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "padded_output.csv"
            
            exporter.export(results, output_path, sample_stats)
            
            # Verify content
            with open(output_path, 'r', newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Check that we have the right number of columns
            header = rows[0]
            expected_columns = 4 + (33 * 5)  # 4 basic + 33 landmarks * 5 values each
            assert len(header) == expected_columns
            
            # Check data row has right number of values
            data_row = rows[1]
            assert len(data_row) == expected_columns
            
            # First landmark should have real values
            assert data_row[4] == '0.5'  # landmark_0_x
            # Later landmarks should be padded with zeros
            assert data_row[4 + 5] == '0.0'  # landmark_1_x (padded)


class TestExporterFactory:
    """Test exporter factory."""
    
    def test_create_json_exporter(self):
        """Test creating JSON exporter."""
        exporter = ExporterFactory.create_exporter('json')
        assert isinstance(exporter, JSONExporter)
        
        exporter = ExporterFactory.create_exporter('JSON')
        assert isinstance(exporter, JSONExporter)
    
    def test_create_csv_exporter(self):
        """Test creating CSV exporter."""
        exporter = ExporterFactory.create_exporter('csv')
        assert isinstance(exporter, CSVExporter)
        
        exporter = ExporterFactory.create_exporter('CSV')
        assert isinstance(exporter, CSVExporter)
    
    def test_unsupported_format(self):
        """Test creating exporter with unsupported format."""
        with pytest.raises(ValueError, match="Unsupported export format"):
            ExporterFactory.create_exporter('xml') 