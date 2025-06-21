import mediapipe as mp
import cv2
import numpy as np
import argparse
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Detect pose landmarks in an image')
    parser.add_argument('image_path', help='Path to the input image file')
    args = parser.parse_args()
    
    # Initialize MediaPipe Pose Landmarker
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    model_path = os.path.join(project_root, 'notebooks', 'pose_landmarker_lite.task')
    
    # Create pose landmarker options
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE)
    
    # Use the image path from command line arguments
    image_path = args.image_path
    
    try:
        # Create pose landmarker
        with vision.PoseLandmarker.create_from_options(options) as landmarker:
            # Load image
            mp_image = mp.Image.create_from_file(image_path)
            
            # Detect pose landmarks
            pose_landmarker_result = landmarker.detect(mp_image)
            
            # Convert MediaPipe image to OpenCV format
            image_cv2 = cv2.imread(image_path)
            annotated_image = image_cv2.copy()
            
            # Define pose connections (main body connections)
            POSE_CONNECTIONS = [
                # Face
                (0, 1), (1, 2), (2, 3), (3, 7),
                (0, 4), (4, 5), (5, 6), (6, 8),
                # Torso
                (9, 10), (11, 12), (11, 13), (13, 15),
                (12, 14), (14, 16), (11, 23), (12, 24),
                (23, 24),
                # Arms
                (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
                (16, 18), (16, 20), (16, 22), (12, 14), (14, 16),
                # Legs
                (23, 25), (25, 27), (27, 29), (27, 31),
                (24, 26), (26, 28), (28, 30), (28, 32)
            ]
            
            # Draw pose landmarks
            if pose_landmarker_result.pose_landmarks:
                for pose_landmarks in pose_landmarker_result.pose_landmarks:
                    # Convert landmarks to pixel coordinates
                    landmark_points = []
                    for landmark in pose_landmarks:
                        x = int(landmark.x * image_cv2.shape[1])
                        y = int(landmark.y * image_cv2.shape[0])
                        landmark_points.append((x, y))
                        # Draw landmark points
                        cv2.circle(annotated_image, (x, y), 5, (0, 255, 0), -1)
                    
                    # Draw connections
                    for connection in POSE_CONNECTIONS:
                        start_idx, end_idx = connection
                        if start_idx < len(landmark_points) and end_idx < len(landmark_points):
                            start_point = landmark_points[start_idx]
                            end_point = landmark_points[end_idx]
                            cv2.line(annotated_image, start_point, end_point, (0, 0, 255), 2)
                
                print(f"Detected {len(pose_landmarker_result.pose_landmarks)} pose(s)")
                print(f"Each pose has {len(pose_landmarker_result.pose_landmarks[0])} landmarks")
            else:
                print("No poses detected in the image")
            
            # Save the result
            # Create output filename based on input image name
            input_filename = os.path.basename(image_path)
            name_without_ext, ext = os.path.splitext(input_filename)
            output_filename = f"{name_without_ext}_pose{ext}"
            output_path = os.path.join(project_root, 'output', output_filename)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cv2.imwrite(output_path, annotated_image)
            print(f"Result saved to: {output_path}")
            
            # Display image info
            print(f"Input image: {image_path}")
            print(f"Image size: {image_cv2.shape[1]}x{image_cv2.shape[0]}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the model file exists and the image path is correct")

if __name__ == "__main__":
    main()