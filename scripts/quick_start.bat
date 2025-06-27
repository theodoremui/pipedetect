@echo off
REM ============================================================================
REM PipeDetect - Quick Start Script (Windows)
REM ============================================================================
REM Simple script to get started with pose detection quickly

echo.
echo ============================================================================
echo                         PipeDetect - Quick Start
echo ============================================================================
echo.

REM Activate virtual environment if not already active
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Display help first
echo Showing available options:
echo.
python src/detect.py --help

echo.
echo ============================================================================
echo                         Ready to detect poses!
echo ============================================================================
echo.
echo Basic usage examples:
echo.
echo   Process a video:     python src/detect.py your_video.mp4
echo   Process an image:    python src/detect.py your_image.jpg  
echo   Process a folder:    python src/detect.py your_images_folder/
echo.
echo Advanced examples:
echo.
echo   High accuracy:       python src/detect.py video.mp4 --model-complexity 2 --detection-confidence 0.8
echo   Fast processing:     python src/detect.py video.mp4 --model-complexity 0 --no-frames --no-overlays
echo   Custom output:       python src/detect.py video.mp4 --json my_poses.json --output-dir results/
echo.
echo ============================================================================
echo.

pause 