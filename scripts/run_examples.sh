#!/bin/bash
# ============================================================================
# PipeDetect - Pose Detection Examples (Unix Shell Script)
# ============================================================================
#
# This script demonstrates various ways to run the PipeDetect pose detection
# program from the command line with different configurations and options.
#
# Prerequisites:
#   1. Ensure you have activated the virtual environment:
#      source .venv/bin/activate
#   2. Have some test video/image files ready
#
# Usage:
#   chmod +x run_examples.sh
#   ./run_examples.sh
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo
echo "============================================================================"
echo "                    PipeDetect - Pose Detection Examples"
echo "============================================================================"
echo

# Check if virtual environment is activated and Python/dependencies are available
if python -c "import pipedetect" 2>/dev/null; then
    echo -e "${GREEN}✓ Python environment and PipeDetect ready${NC}"
else
    echo -e "${YELLOW}⚠ Please activate virtual environment: source .venv/bin/activate${NC}"
    echo -e "${YELLOW}⚠ And ensure dependencies are installed: uv sync${NC}"
    exit 1
fi

echo
echo -e "${CYAN}--- BASIC EXAMPLES ---${NC}"
echo

echo -e "${BLUE}1. Display help and available options:${NC}"
echo "python src/detect.py --help"
echo

echo -e "${BLUE}2. Process a single video file (basic usage):${NC}"
echo "python src/detect.py video.mp4"
echo

echo -e "${BLUE}3. Process a single image file:${NC}"
echo "python src/detect.py image.jpg"
echo

echo -e "${BLUE}4. Process all images in a directory:${NC}"
echo "python src/detect.py images_folder/"
echo

echo -e "${BLUE}5. Specify custom output directory:${NC}"
echo "python src/detect.py video.mp4 --output-dir results/"
echo

echo
echo -e "${CYAN}--- ADVANCED CONFIGURATION ---${NC}"
echo

echo -e "${BLUE}6. High-precision detection with heavy model:${NC}"
echo "python src/detect.py video.mp4 \\"
echo "  --model-complexity 2 \\"
echo "  --detection-confidence 0.8 \\"
echo "  --tracking-confidence 0.8"
echo

echo -e "${BLUE}7. Fast processing with light model:${NC}"
echo "python src/detect.py video.mp4 \\"
echo "  --model-complexity 0 \\"
echo "  --detection-confidence 0.3 \\"
echo "  --no-frames --no-overlays"
echo

echo -e "${BLUE}8. Enable pose segmentation for detailed analysis:${NC}"
echo "python src/detect.py video.mp4 --segmentation --model-complexity 2"
echo

echo -e "${BLUE}9. Custom output filenames:${NC}"
echo "python src/detect.py video.mp4 --json my_poses.json --csv my_analysis.csv"
echo

echo
echo -e "${CYAN}--- OUTPUT CONTROL ---${NC}"
echo

echo -e "${BLUE}10. Save only pose data (no frame images):${NC}"
echo "python src/detect.py video.mp4 --no-frames --no-overlays"
echo

echo -e "${BLUE}11. Generate only overlay visualizations:${NC}"
echo "python src/detect.py video.mp4 --no-frames"
echo

echo -e "${BLUE}12. Process with custom confidence thresholds:${NC}"
echo "python src/detect.py video.mp4 --detection-confidence 0.7 --tracking-confidence 0.6"
echo

echo
echo -e "${CYAN}--- LOGGING AND DEBUGGING ---${NC}"
echo

echo -e "${BLUE}13. Verbose output with detailed logging:${NC}"
echo "python src/detect.py video.mp4 --verbose --verbose"
echo

echo -e "${BLUE}14. Save processing logs to file:${NC}"
echo "python src/detect.py video.mp4 --log-file processing.log --verbose"
echo

echo -e "${BLUE}15. Quiet mode (suppress console output):${NC}"
echo "python src/detect.py video.mp4 --quiet"
echo

echo -e "${BLUE}16. Hide progress bar:${NC}"
echo "python src/detect.py video.mp4 --no-progress"
echo

echo
echo -e "${CYAN}--- BATCH PROCESSING EXAMPLES ---${NC}"
echo

echo -e "${BLUE}17. Process multiple videos in sequence:${NC}"
echo "for video in *.mp4; do"
echo "  python src/detect.py \"\$video\" --output-dir \"results_\$(basename \"\$video\" .mp4)\""
echo "done"
echo

echo -e "${BLUE}18. Fast batch processing of images:${NC}"
echo "python src/detect.py images/ --model-complexity 0 --no-frames --csv batch_results.csv"
echo

echo
echo -e "${CYAN}--- RESEARCH/ANALYSIS SETUPS ---${NC}"
echo

echo -e "${BLUE}19. Maximum accuracy for research:${NC}"
echo "python src/detect.py video.mp4 \\"
echo "  --model-complexity 2 \\"
echo "  --detection-confidence 0.9 \\"
echo "  --segmentation \\"
echo "  --json detailed_analysis.json"
echo

echo -e "${BLUE}20. Biomechanics analysis with comprehensive logging:${NC}"
echo "python src/detect.py sports_video.mp4 \\"
echo "  --model-complexity 2 \\"
echo "  --detection-confidence 0.8 \\"
echo "  --verbose \\"
echo "  --log-file biomechanics.log"
echo

echo
echo -e "${CYAN}--- INTERACTIVE EXAMPLES ---${NC}"
echo

# Interactive menu
show_menu() {
    echo -e "${YELLOW}Choose an example to run:${NC}"
    echo "1) Show help"
    echo "2) Test with sample video (if available)"
    echo "3) Test with sample image (if available)"
    echo "4) Create sample test files"
    echo "5) Run performance benchmark"
    echo "q) Quit"
    echo
}

run_example() {
    case $1 in
        1)
            echo -e "${GREEN}Running: python src/detect.py --help${NC}"
            python src/detect.py --help
            ;;
        2)
            if [ -f "video.mp4" ] || [ -f "test.mp4" ] || [ -f "sample.mp4" ]; then
                video_file=$(ls *.mp4 2>/dev/null | head -1)
                echo -e "${GREEN}Running: python src/detect.py $video_file${NC}"
                python src/detect.py "$video_file"
            else
                echo -e "${YELLOW}No video files found. Please add a .mp4 file to test.${NC}"
            fi
            ;;
        3)
            if [ -f "image.jpg" ] || [ -f "test.jpg" ] || [ -f "sample.jpg" ]; then
                image_file=$(ls *.jpg *.jpeg *.png 2>/dev/null | head -1)
                echo -e "${GREEN}Running: python src/detect.py $image_file${NC}"
                python src/detect.py "$image_file"
            else
                echo -e "${YELLOW}No image files found. Please add an image file to test.${NC}"
            fi
            ;;
        4)
            echo -e "${GREEN}Creating sample test directory structure...${NC}"
            mkdir -p test_data
            echo -e "${YELLOW}Place your video/image files in the test_data/ directory${NC}"
            echo -e "${YELLOW}Then run: python src/detect.py test_data/${NC}"
            ;;
        5)
            echo -e "${GREEN}Running performance benchmark...${NC}"
            echo "This will test different model complexities:"
            
            if [ -f "*.mp4" ]; then
                video_file=$(ls *.mp4 2>/dev/null | head -1)
                
                echo -e "${CYAN}Testing Light Model (fast):${NC}"
                time python src/detect.py "$video_file" --model-complexity 0 --no-frames --no-overlays --quiet
                
                echo -e "${CYAN}Testing Full Model (balanced):${NC}"
                time python src/detect.py "$video_file" --model-complexity 1 --no-frames --no-overlays --quiet
                
                echo -e "${CYAN}Testing Heavy Model (accurate):${NC}"
                time python src/detect.py "$video_file" --model-complexity 2 --no-frames --no-overlays --quiet
            else
                echo -e "${YELLOW}No video file found for benchmark. Please add a .mp4 file.${NC}"
            fi
            ;;
        q)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            ;;
    esac
}

# Interactive mode
if [ "$1" = "--interactive" ] || [ "$1" = "-i" ]; then
    while true; do
        echo
        show_menu
        read -p "Enter your choice: " choice
        echo
        run_example "$choice"
        echo
        read -p "Press Enter to continue..."
    done
else
    echo -e "${CYAN}--- SAMPLE COMMANDS TO RUN ---${NC}"
    echo
    echo "Choose any of the commands above and modify the file paths for your needs."
    echo
    echo -e "${YELLOW}For interactive mode, run: ./run_examples.sh --interactive${NC}"
    echo
fi

echo
echo "============================================================================"
echo -e "${GREEN}For more information:${NC}"
echo "  • Run: python src/detect.py --help"
echo "  • Read: docs/USAGE.md"
echo "  • Check: docs/INSTALLATION.md"
echo "============================================================================"
echo 