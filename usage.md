# Image2Pose Usage Guide

## Overview

`image2pose.py` is a Python script that uses MediaPipe to detect and visualize human pose landmarks in images. The script processes an input image and outputs a new image with pose landmarks and connections drawn on it.

## Prerequisites

- Python 3.7 or higher
- Required Python packages:
  - mediapipe
  - opencv-python (cv2)
  - numpy

## Installation

Make sure you have the required dependencies installed:

```bash
pip install mediapipe opencv-python numpy
```

## Required Files

The script requires the MediaPipe pose detection model file:
- `notebooks/pose_landmarker_lite.task` - MediaPipe pose landmarker model

## Usage

### Basic Usage

```bash
python src/image2pose.py <image_path>
```

### Examples

```bash
# Process an image in the data directory
python src/image2pose.py data/person.jpg

# Process an image with absolute path
python src/image2pose.py /path/to/your/image.jpg

# Process an image with relative path
python src/image2pose.py ../images/photo.png
```

### Help

To see usage information:

```bash
python src/image2pose.py --help
```

## Output

The script will:
1. Detect pose landmarks in the input image
2. Draw green circles at each landmark point
3. Draw red lines connecting related landmarks (pose connections)
4. Save the annotated image in the `output/` folder with a filename based on the original image
5. Print detection results to the console

### Output File Naming

The output files are saved in the `output/` directory with the following naming convention:
- Input: `person.jpg` → Output: `output/person_pose.jpg`
- Input: `data/family.png` → Output: `output/family_pose.png`
- Input: `/path/to/image.jpeg` → Output: `output/image_pose.jpeg`

### Console Output Example

```
Detected 1 pose(s)
Each pose has 33 landmarks
Result saved to: /path/to/project/output/person_pose.jpg
Input image: data/person.jpg
Image size: 640x480
```

## Pose Landmarks and Connections

The script detects 33 pose landmarks including:
- Face landmarks (nose, eyes, ears, mouth)
- Upper body (shoulders, elbows, wrists, hands)
- Lower body (hips, knees, ankles, feet)

### What are Pose Connections?

Pose connections are the red lines drawn between specific landmark points to create a skeletal representation of the human pose. These connections help visualize the body structure and movement by linking anatomically related points.

The script draws the following types of connections:

#### Face Connections (8 connections)
- Connect facial landmarks like nose, eyes, ears, and mouth
- Create the basic facial structure outline
- Landmarks 0-10 represent facial features

#### Torso Connections (9 connections)  
- Connect shoulders, hips, and core body points
- Form the main body trunk structure
- Include shoulder-to-shoulder, hip-to-hip, and shoulder-to-hip connections
- Landmarks 11-12 (shoulders), 23-24 (hips)

#### Arm Connections (10 connections)
- Connect shoulder → elbow → wrist → hand landmarks
- Draw both left and right arm skeletal structure
- Include hand finger connections
- Left arm: landmarks 11→13→15→17,19,21
- Right arm: landmarks 12→14→16→18,20,22

#### Leg Connections (8 connections)
- Connect hip → knee → ankle → foot landmarks  
- Draw both left and right leg skeletal structure
- Include foot toe connections
- Left leg: landmarks 23→25→27→29,31
- Right leg: landmarks 24→26→28→30,32

### Landmark Numbering System

MediaPipe uses a standardized 33-point landmark system:
- **0-10**: Face (nose, eyes, ears, mouth)
- **11-12**: Shoulders (left, right)
- **13-16**: Elbows and wrists (left elbow, right elbow, left wrist, right wrist)
- **17-22**: Hand landmarks (thumb, pinky, hand tips)
- **23-24**: Hips (left, right)
- **25-28**: Knees and ankles (left knee, right knee, left ankle, right ankle)
- **29-32**: Foot landmarks (heel, foot index)

## Supported Image Formats

The script supports common image formats including:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## Error Handling

If the script encounters errors, it will display helpful error messages:
- Missing or invalid image file
- Missing model file
- Unsupported image format
- No poses detected in the image

## Troubleshooting

1. **Model file not found**: Ensure `notebooks/pose_landmarker_lite.task` exists
2. **Image not found**: Check that the image path is correct and the file exists
3. **No poses detected**: Try with a clearer image where the person is fully visible
4. **Permission errors**: Make sure you have write permissions in the project directory

## Technical Details

- **Detection Model**: MediaPipe Pose Landmarker Lite
- **Running Mode**: Static image processing
- **Landmark Count**: 33 points per detected person
- **Output Format**: JPEG image with pose annotations 