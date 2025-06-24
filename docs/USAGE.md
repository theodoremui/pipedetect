# Usage Guide

This guide provides comprehensive instructions for using PipeDetect to analyze poses in videos and images.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Command Line Options](#command-line-options)
- [Input Formats](#input-formats)
- [Output Formats](#output-formats)
- [Configuration Examples](#configuration-examples)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Basic Usage

### Processing a Single Video

```bash
# Basic video processing
python detect.py video.mp4

# With custom output directory
python detect.py video.mp4 --output-dir my_results/

# With custom output filenames
python detect.py video.mp4 --json my_poses.json --csv my_poses.csv
```

### Processing a Single Image

```bash
# Basic image processing
python detect.py image.jpg

# Multiple image formats supported
python detect.py photo.png
python detect.py picture.bmp
python detect.py snapshot.webp
```

### Processing Multiple Images

```bash
# Process all images in a directory
python detect.py /path/to/images/

# Process with specific settings
python detect.py ./photos/ --model-complexity 2 --detection-confidence 0.7
```

## Command Line Options

### Required Arguments

- `input_path`: Path to video file, image file, or directory containing images

### Optional Arguments

#### Output Control
```bash
--output-dir, -o         # Output directory (default: "outputs")
--json                   # Custom JSON output filename
--csv                    # Custom CSV output filename
--no-frames             # Don't save individual video frames
--no-overlays           # Don't save pose overlay images
```

#### Model Configuration
```bash
--detection-confidence   # Minimum detection confidence (0.0-1.0, default: 0.5)
--tracking-confidence   # Minimum tracking confidence (0.0-1.0, default: 0.5)  
--model-complexity      # Model complexity: 0=light, 1=full, 2=heavy (default: 1)
--segmentation          # Enable pose segmentation (slower but more detailed)
--no-smooth             # Disable landmark smoothing
```

#### Interface Options
```bash
--verbose, -v           # Increase verbosity (-v for info, -vv for debug)
--quiet, -q             # Suppress console output
--no-progress           # Hide progress bar
--log-file              # Save logs to specified file
```

## Input Formats

### Supported Video Formats
- **MP4** (`.mp4`) - Recommended
- **AVI** (`.avi`)
- **MOV** (`.mov`)
- **MKV** (`.mkv`)
- **WMV** (`.wmv`)
- **WebM** (`.webm`)
- **FLV** (`.flv`)

### Supported Image Formats
- **JPEG** (`.jpg`, `.jpeg`) - Recommended
- **PNG** (`.png`)
- **BMP** (`.bmp`)
- **TIFF** (`.tiff`, `.tif`)
- **WebP** (`.webp`)

### Input Requirements
- **Video**: Any resolution, frame rate should be reasonable (1-60 FPS)
- **Images**: Any resolution, clear human figures for better detection
- **Directory**: Must contain at least one supported image format

## Output Formats

### Directory Structure

When processing `video.mp4`, PipeDetect creates:

```
outputs/
├── pose_video_20231201_143022.json       # Structured pose data
├── pose_video_20231201_143022.csv        # Tabular pose data  
├── frames_video_20231201_143022/          # Original frames (optional)
│   ├── frame_000001.jpg
│   ├── frame_000002.jpg
│   └── ...
└── overlay_video_20231201_143022/         # Pose overlays (optional)
    ├── overlay_000001.jpg
    ├── overlay_000002.jpg
    └── ...
```

### JSON Output Structure

```json
{
  "metadata": {
    "export_timestamp": "2023-12-01T14:30:22.123456",
    "total_frames": 1000,
    "processed_frames": 950,
    "failed_frames": 50,
    "success_rate": 0.95,
    "processing_time_seconds": 45.2,
    "fps": 21.0,
    "start_time": "2023-12-01T14:29:37.123456",
    "end_time": "2023-12-01T14:30:22.323456"
  },
  "results": [
    {
      "frame_id": 0,
      "timestamp": 0.033,
      "confidence": 0.92,
      "source_file": "video.mp4",
      "landmarks": [
        {
          "x": 0.5,        # Normalized x coordinate (0-1)
          "y": 0.3,        # Normalized y coordinate (0-1)  
          "z": 0.1,        # Depth coordinate
          "visibility": 0.9, # How visible the landmark is
          "presence": 0.8   # Confidence that landmark exists
        }
        // ... 32 more landmarks (33 total for full body pose)
      ]
    }
  ]
}
```

### CSV Output Structure

The CSV contains one row per detected pose with columns:

**Basic Information:**
- `frame_id`: Frame number in video (0-based)
- `timestamp`: Time in seconds for video frames
- `confidence`: Overall pose detection confidence
- `source_file`: Original input file name

**Landmark Data (33 landmarks × 5 values each):**
- `landmark_0_x`, `landmark_0_y`, `landmark_0_z`, `landmark_0_visibility`, `landmark_0_presence`
- `landmark_1_x`, `landmark_1_y`, `landmark_1_z`, `landmark_1_visibility`, `landmark_1_presence`
- ... up to `landmark_32_*`

### MediaPipe Pose Landmarks

The 33 pose landmarks represent:

```
0-10:   Face (nose, eyes, ears, mouth)
11-12:  Shoulders  
13-16:  Arms (elbows, wrists)
17-22:  Hands (thumbs, pinky, index, hand centers)
23-24:  Hips
25-28:  Legs (knees, ankles) 
29-32:  Feet (heels, foot centers)
```

## Configuration Examples

### High Precision Detection

For applications requiring maximum accuracy:

```bash
python detect.py video.mp4 \
  --model-complexity 2 \
  --detection-confidence 0.8 \
  --tracking-confidence 0.8 \
  --segmentation
```

**Use cases:** Medical analysis, sports biomechanics, research
**Trade-offs:** Slower processing, higher resource usage

### Fast Processing

For real-time or batch processing where speed is important:

```bash
python detect.py video.mp4 \
  --model-complexity 0 \
  --detection-confidence 0.3 \
  --no-frames \
  --no-overlays
```

**Use cases:** Video indexing, basic motion detection, previews
**Trade-offs:** Lower accuracy, fewer details

### Balanced Performance

Good balance of speed and accuracy:

```bash
python detect.py video.mp4 \
  --model-complexity 1 \
  --detection-confidence 0.5 \
  --tracking-confidence 0.5
```

**Use cases:** General purpose pose detection, content analysis
**Trade-offs:** Default settings work well for most scenarios

### Research/Analysis Setup

Maximum data retention for detailed analysis:

```bash
python detect.py video.mp4 \
  --model-complexity 2 \
  --detection-confidence 0.6 \
  --segmentation \
  --verbose --verbose \
  --log-file analysis.log \
  --json detailed_poses.json
```

## Performance Tuning

### Optimizing for Speed

1. **Use lighter model complexity:**
   ```bash
   --model-complexity 0
   ```

2. **Reduce confidence thresholds:**
   ```bash
   --detection-confidence 0.3 --tracking-confidence 0.3
   ```

3. **Skip unnecessary outputs:**
   ```bash
   --no-frames --no-overlays
   ```

4. **Disable smoothing for real-time:**
   ```bash
   --no-smooth
   ```

### Optimizing for Accuracy

1. **Use heavier model:**
   ```bash
   --model-complexity 2
   ```

2. **Increase confidence thresholds:**
   ```bash
   --detection-confidence 0.7 --tracking-confidence 0.7
   ```

3. **Enable segmentation:**
   ```bash
   --segmentation
   ```

### Memory Optimization

For systems with limited RAM:

```bash
# Process in batches, avoid saving frames
python detect.py large_video.mp4 --no-frames --no-overlays --model-complexity 0
```

## Troubleshooting

### Common Issues

#### 1. No Poses Detected

**Symptoms:** Empty JSON/CSV files, no overlay images generated

**Solutions:**
- Lower detection confidence: `--detection-confidence 0.3`
- Check input quality: ensure clear human figures
- Try different model complexity: `--model-complexity 1`
- Verify input format is supported

#### 2. Low Performance/Slow Processing

**Symptoms:** Very low FPS, long processing times

**Solutions:**
- Use lighter model: `--model-complexity 0`
- Disable segmentation (remove `--segmentation`)
- Skip frame outputs: `--no-frames --no-overlays`
- Check system resources

#### 3. Poor Detection Quality

**Symptoms:** Inaccurate pose landmarks, jittery detection

**Solutions:**
- Increase model complexity: `--model-complexity 2`
- Raise confidence thresholds: `--detection-confidence 0.7`
- Enable segmentation: `--segmentation`
- Ensure good input video quality

#### 4. Memory Issues

**Symptoms:** Out of memory errors, system slowdown

**Solutions:**
- Use lighter model: `--model-complexity 0`
- Process smaller videos/batches
- Skip frame saving: `--no-frames --no-overlays`
- Close other applications

### Error Messages

#### "Input path does not exist"
- Check file/directory path spelling
- Use absolute paths if relative paths fail
- Ensure file permissions are correct

#### "Unsupported file format"
- Check supported formats list above
- Convert to supported format (e.g., MP4 for video)

#### "No supported image files found"
- Ensure directory contains images with supported extensions
- Check file extensions are lowercase or try mixed case

#### "Failed to initialize MediaPipe"
- Reinstall MediaPipe: `pip install --upgrade mediapipe`
- Check system compatibility
- Try different model complexity

## Advanced Usage

### Batch Processing Script

Create a script to process multiple files:

```python
#!/usr/bin/env python3
import subprocess
from pathlib import Path

video_dir = Path("input_videos")
output_base = Path("batch_results")

for video_file in video_dir.glob("*.mp4"):
    output_dir = output_base / video_file.stem
    
    cmd = [
        "python", "detect.py", str(video_file),
        "--output-dir", str(output_dir),
        "--model-complexity", "1",
        "--no-progress"
    ]
    
    print(f"Processing {video_file}...")
    subprocess.run(cmd)
```

### Custom Analysis Pipeline

Process results with custom analysis:

```python
import json
import pandas as pd
from pathlib import Path

# Load results
with open("outputs/pose_video_20231201_143022.json") as f:
    data = json.load(f)

# Convert to DataFrame for analysis
results = []
for result in data["results"]:
    row = {
        "frame_id": result["frame_id"],
        "timestamp": result["timestamp"],
        "confidence": result["confidence"]
    }
    
    # Add landmark coordinates
    for i, landmark in enumerate(result["landmarks"]):
        row[f"landmark_{i}_x"] = landmark["x"]
        row[f"landmark_{i}_y"] = landmark["y"]
        row[f"landmark_{i}_visibility"] = landmark["visibility"]
    
    results.append(row)

df = pd.DataFrame(results)

# Analyze pose data
print(f"Average confidence: {df['confidence'].mean():.3f}")
print(f"Total frames with poses: {len(df)}")

# Calculate motion metrics
df['head_y'] = df['landmark_0_y']  # Nose position
motion = df['head_y'].diff().abs().mean()
print(f"Average head motion: {motion:.4f}")
```

### Integration with Other Tools

Export data for external analysis:

```bash
# Export to CSV for Excel/R/MATLAB
python detect.py video.mp4 --csv analysis_data.csv --no-frames --no-overlays

# Process with specific settings for biomechanics
python detect.py sports_video.mp4 \
  --model-complexity 2 \
  --detection-confidence 0.8 \
  --segmentation \
  --json biomechanics_data.json
```

### Automation and Monitoring

Monitor processing with logs:

```bash
# Detailed logging for troubleshooting
python detect.py video.mp4 \
  --verbose --verbose \
  --log-file processing.log \
  --no-progress

# Check logs
tail -f processing.log
```

## Best Practices

1. **Start with default settings** and adjust based on results
2. **Test on small samples** before processing large datasets  
3. **Monitor system resources** during processing
4. **Keep backups** of important input files
5. **Document your settings** for reproducible results
6. **Validate outputs** with manual spot checks
7. **Use appropriate model complexity** for your use case

## Getting Help

- Check this documentation first
- Search [GitHub Issues](https://github.com/your-username/pipedetect/issues)
- Join [Community Discussions](https://github.com/your-username/pipedetect/discussions)
- Report bugs with detailed error messages and steps to reproduce 