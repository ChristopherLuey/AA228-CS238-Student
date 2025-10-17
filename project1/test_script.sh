#!/bin/bash

# Quick test script to verify the comprehensive script works
# This runs only the small dataset as a test

set -e
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
DATA_DIR="$PROJECT_ROOT/data"
OUTPUT_BASE="$PROJECT_ROOT/output"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Testing comprehensive script with small dataset only...${NC}"

# Create test output directory
mkdir -p "$OUTPUT_BASE/test_small"

# Change to project directory
cd "$PROJECT_ROOT"

# Run small dataset
echo -e "${GREEN}Running small dataset...${NC}"
python3 project1.py "$DATA_DIR/small.csv" "$OUTPUT_BASE/test_small/small.gph"

echo -e "${GREEN}Test completed! Check output in: $OUTPUT_BASE/test_small/${NC}"
ls -la "$OUTPUT_BASE/test_small/"
