@echo off
REM ============================================================================
REM PipeDetect - Pose Detection Examples (Windows Batch Script)
REM ============================================================================
REM
REM This script demonstrates various ways to run the PipeDetect pose detection
REM program from the command line with different configurations and options.
REM
REM Prerequisites:
REM   1. Ensure you have activated the virtual environment:
REM      .venv\Scripts\activate
REM   2. Have some test video/image files ready
REM ============================================================================

echo.
echo ============================================================================
echo                    PipeDetect - Pose Detection Examples
echo ============================================================================
echo.

REM Check if virtual environment is activated
python -c "import sys; print('✓ Python environment ready') if 'pipedetect' in sys.path[0] else print('⚠ Please activate virtual environment: .venv\\Scripts\\activate')" 2>nul
if errorlevel 1 (
    echo ⚠ Please ensure Python is installed and virtual environment is activated
    echo Run: .venv\Scripts\activate
    pause
    exit /b 1
)

echo.
echo --- BASIC EXAMPLES ---
echo.

echo 1. Display help and available options:
echo python detect.py --help
echo.

echo 2. Process a single video file (basic usage):
echo python detect.py video.mp4
echo.

echo 3. Process a single image file:
echo python detect.py image.jpg
echo.

echo 4. Process all images in a directory:
echo python detect.py images_folder/
echo.

echo 5. Specify custom output directory:
echo python detect.py video.mp4 --output-dir results/
echo.

echo.
echo --- ADVANCED CONFIGURATION ---
echo.

echo 6. High-precision detection with heavy model:
echo python detect.py video.mp4 --model-complexity 2 --detection-confidence 0.8 --tracking-confidence 0.8
echo.

echo 7. Fast processing with light model:
echo python detect.py video.mp4 --model-complexity 0 --detection-confidence 0.3 --no-frames --no-overlays
echo.

echo 8. Enable pose segmentation for detailed analysis:
echo python detect.py video.mp4 --segmentation --model-complexity 2
echo.

echo 9. Custom output filenames:
echo python detect.py video.mp4 --json my_poses.json --csv my_analysis.csv
echo.

echo.
echo --- OUTPUT CONTROL ---
echo.

echo 10. Save only pose data (no frame images):
echo python detect.py video.mp4 --no-frames --no-overlays
echo.

echo 11. Generate only overlay visualizations:
echo python detect.py video.mp4 --no-frames
echo.

echo 12. Process with custom confidence thresholds:
echo python detect.py video.mp4 --detection-confidence 0.7 --tracking-confidence 0.6
echo.

echo.
echo --- LOGGING AND DEBUGGING ---
echo.

echo 13. Verbose output with detailed logging:
echo python detect.py video.mp4 --verbose --verbose
echo.

echo 14. Save processing logs to file:
echo python detect.py video.mp4 --log-file processing.log --verbose
echo.

echo 15. Quiet mode (suppress console output):
echo python detect.py video.mp4 --quiet
echo.

echo 16. Hide progress bar:
echo python detect.py video.mp4 --no-progress
echo.

echo.
echo --- BATCH PROCESSING EXAMPLES ---
echo.

echo 17. Process multiple videos in sequence:
echo for %%f in (*.mp4) do python detect.py "%%f" --output-dir "results_%%~nf"
echo.

echo 18. Fast batch processing of images:
echo python detect.py images/ --model-complexity 0 --no-frames --csv batch_results.csv
echo.

echo.
echo --- RESEARCH/ANALYSIS SETUPS ---
echo.

echo 19. Maximum accuracy for research:
echo python detect.py video.mp4 --model-complexity 2 --detection-confidence 0.9 --segmentation --json detailed_analysis.json
echo.

echo 20. Biomechanics analysis with comprehensive logging:
echo python detect.py sports_video.mp4 --model-complexity 2 --detection-confidence 0.8 --verbose --log-file biomechanics.log
echo.

echo.
echo --- SAMPLE COMMANDS TO RUN ---
echo.
echo Choose a command to run (or modify paths for your files):
echo.

set /p choice="Enter the number of the example you want to run (1-20), or 'q' to quit: "

if "%choice%"=="q" goto :end
if "%choice%"=="1" (
    python detect.py --help
    goto :end
)

REM Add interactive examples for testing
if "%choice%"=="2" (
    echo.
    echo Running: python detect.py video.mp4
    echo Note: Replace 'video.mp4' with your actual video file
    echo.
    set /p confirm="Do you have a video.mp4 file to test? (y/n): "
    if /i "%confirm%"=="y" (
        python detect.py video.mp4
    ) else (
        echo Please place a video file named 'video.mp4' in the current directory and run again.
    )
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo Running: python detect.py image.jpg
    echo Note: Replace 'image.jpg' with your actual image file
    echo.
    set /p confirm="Do you have an image.jpg file to test? (y/n): "
    if /i "%confirm%"=="y" (
        python detect.py image.jpg
    ) else (
        echo Please place an image file named 'image.jpg' in the current directory and run again.
    )
    goto :end
)

echo.
echo Example %choice% command displayed above. 
echo Modify the file paths to match your actual files and run the command.
echo.

:end
echo.
echo ============================================================================
echo For more information, run: python detect.py --help
echo Documentation: docs/USAGE.md
echo ============================================================================
echo.
pause 