#!/bin/bash
# ============================================================================
# PipeDetect - Quick Start Script (Unix/Linux/macOS)
# ============================================================================
# Simple script to get started with pose detection quickly

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo
echo "============================================================================"
echo "                         PipeDetect - Quick Start"
echo "============================================================================"
echo

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ] && [ -d ".venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Display help first
echo -e "${CYAN}Showing available options:${NC}"
echo
python src/detect.py --help

echo
echo "============================================================================"
echo -e "${GREEN}                         Ready to detect poses!${NC}"
echo "============================================================================"
echo
echo -e "${BLUE}Basic usage examples:${NC}"
echo
echo "  Process a video:     python src/detect.py your_video.mp4"
echo "  Process an image:    python src/detect.py your_image.jpg"
echo "  Process a folder:    python src/detect.py your_images_folder/"
echo
echo -e "${BLUE}Advanced examples:${NC}"
echo
echo "  High accuracy:       python src/detect.py video.mp4 --model-complexity 2 --detection-confidence 0.8"
echo "  Fast processing:     python src/detect.py video.mp4 --model-complexity 0 --no-frames --no-overlays"
echo "  Custom output:       python src/detect.py video.mp4 --json my_poses.json --output-dir results/"
echo
echo "============================================================================"
echo

# Make the script executable
chmod +x "$0" 2>/dev/null 