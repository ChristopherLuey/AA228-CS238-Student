#!/bin/bash

# Comprehensive Bayesian Network Structure Learning Script
# Runs small, medium, and large datasets with full monitoring and organization
# Author: Generated for AA228 Project 1
# Date: $(date)

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
DATA_DIR="$PROJECT_ROOT/data"
OUTPUT_BASE="$PROJECT_ROOT/output"
LOG_DIR="$OUTPUT_BASE/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MASTER_LOG="$LOG_DIR/master_run_${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Dataset configurations
DATASETS="small medium large"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${message}" >> "$MASTER_LOG"
}

print_header() {
    echo -e "${CYAN}================================================================================${NC}"
    echo -e "${CYAN}  AA228 Bayesian Network Structure Learning - Comprehensive Run${NC}"
    echo -e "${CYAN}================================================================================${NC}"
    echo -e "${CYAN}  Start Time: $(date)${NC}"
    echo -e "${CYAN}  Project Root: $PROJECT_ROOT${NC}"
    echo -e "${CYAN}  Master Log: $MASTER_LOG${NC}"
    echo -e "${CYAN}================================================================================${NC}"
    echo ""
}

print_footer() {
    echo ""
    echo -e "${CYAN}================================================================================${NC}"
    echo -e "${CYAN}  Run Completed: $(date)${NC}"
    echo -e "${CYAN}  Total Runtime: $TOTAL_RUNTIME${NC}"
    echo -e "${CYAN}  Master Log: $MASTER_LOG${NC}"
    echo -e "${CYAN}================================================================================${NC}"
}

# Function to create directory structure
setup_directories() {
    print_status $BLUE "Setting up directory structure..."
    
    mkdir -p "$OUTPUT_BASE"
    mkdir -p "$LOG_DIR"
    
    for dataset in $DATASETS; do
        mkdir -p "$OUTPUT_BASE/$dataset"
        print_status $GREEN "Created output directory: $OUTPUT_BASE/$dataset"
    done
}

# Function to check prerequisites
check_prerequisites() {
    print_status $BLUE "Checking prerequisites..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_status $RED "ERROR: python3 not found. Please install Python 3."
        exit 1
    fi
    
    # Check if required files exist
    if [[ ! -f "$PROJECT_ROOT/project1.py" ]]; then
        print_status $RED "ERROR: project1.py not found in $PROJECT_ROOT"
        exit 1
    fi
    
    if [[ ! -f "$PROJECT_ROOT/plot_graph.py" ]]; then
        print_status $RED "ERROR: plot_graph.py not found in $PROJECT_ROOT"
        exit 1
    fi
    
    # Check if data files exist
    for dataset in $DATASETS; do
        data_file="$DATA_DIR/${dataset}.csv"
        if [[ ! -f "$data_file" ]]; then
            print_status $RED "ERROR: Data file not found: $data_file"
            exit 1
        fi
        print_status $GREEN "Found data file: $data_file"
    done
    
    print_status $GREEN "All prerequisites satisfied!"
}

# Function to get dataset info
get_dataset_info() {
    local dataset=$1
    local data_file="$DATA_DIR/${dataset}.csv"
    
    print_status $YELLOW "Analyzing dataset: $dataset"
    
    # Get basic info using Python
    python3 -c "
import pandas as pd
import sys

try:
    df = pd.read_csv('$data_file')
    print(f'Rows: {len(df)}')
    print(f'Columns: {len(df.columns)}')
    print(f'Variables: {list(df.columns)}')
    print(f'Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB')
except Exception as e:
    print(f'Error analyzing dataset: {e}')
    sys.exit(1)
" >> "$MASTER_LOG"
}

# Function to run a single dataset
run_dataset() {
    local dataset=$1
    local data_file="$DATA_DIR/${dataset}.csv"
    local output_dir="$OUTPUT_BASE/$dataset"
    local output_file="$output_dir/${dataset}.gph"
    local start_time=$(date +%s)
    
    print_status $PURPLE "================================================================================="
    print_status $PURPLE "  Starting $dataset dataset processing"
    print_status $PURPLE "================================================================================="
    
    # Get dataset info
    get_dataset_info "$dataset"
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    
    # Run the structure learning
    print_status $BLUE "Running Bayesian structure learning for $dataset..."
    print_status $YELLOW "Command: python3 project1.py \"$data_file\" \"$output_file\""
    
    if python3 project1.py "$data_file" "$output_file"; then
        local end_time=$(date +%s)
        local runtime=$((end_time - start_time))
        local runtime_formatted=$(printf '%02d:%02d:%02d' $((runtime/3600)) $((runtime%3600/60)) $((runtime%60)))
        
        print_status $GREEN "✓ $dataset dataset completed successfully!"
        print_status $GREEN "  Runtime: $runtime_formatted"
        print_status $GREEN "  Output files created in: $output_dir"
        
        # List generated files
        print_status $BLUE "Generated files:"
        ls -la "$output_dir" | while read -r line; do
            print_status $CYAN "  $line"
        done
        
        # Store runtime for summary
        echo "$dataset:$runtime" >> "$OUTPUT_BASE/runtime_summary.txt"
        
    else
        local end_time=$(date +%s)
        local runtime=$((end_time - start_time))
        print_status $RED "✗ $dataset dataset failed after $runtime seconds"
        print_status $RED "Check logs in: $output_dir"
        return 1
    fi
}

# Function to generate summary report
generate_summary() {
    print_status $BLUE "Generating comprehensive summary report..."
    
    local summary_file="$OUTPUT_BASE/run_summary_${TIMESTAMP}.txt"
    
    {
        echo "================================================================================="
        echo "  AA228 Bayesian Network Structure Learning - Run Summary"
        echo "================================================================================="
        echo "Run Date: $(date)"
        echo "Project Root: $PROJECT_ROOT"
        echo "Master Log: $MASTER_LOG"
        echo ""
        echo "Dataset Results:"
        echo "---------------"
        
        for dataset in $DATASETS; do
            local output_dir="$OUTPUT_BASE/$dataset"
            local gph_file="$output_dir/${dataset}.gph"
            local png_file="$output_dir/${dataset}.png"
            local json_file="$output_dir/${dataset}_summary.json"
            local log_file="$output_dir/${dataset}_log.txt"
            
            echo ""
            echo "Dataset: $dataset"
            echo "  Data file: ${dataset}.csv"
            echo "  Output directory: $output_dir"
            
            if [[ -f "$gph_file" ]]; then
                local edge_count=$(wc -l < "$gph_file")
                echo "  ✓ Graph file: $gph_file ($edge_count edges)"
            else
                echo "  ✗ Graph file: MISSING"
            fi
            
            if [[ -f "$png_file" ]]; then
                echo "  ✓ Visualization: $png_file"
            else
                echo "  ✗ Visualization: MISSING"
            fi
            
            if [[ -f "$json_file" ]]; then
                echo "  ✓ Summary JSON: $json_file"
            else
                echo "  ✗ Summary JSON: MISSING"
            fi
            
            if [[ -f "$log_file" ]]; then
                echo "  ✓ Log file: $log_file"
            else
                echo "  ✗ Log file: MISSING"
            fi
        done
        
        echo ""
        echo "Runtime Summary:"
        echo "---------------"
        if [[ -f "$OUTPUT_BASE/runtime_summary.txt" ]]; then
            while IFS=':' read -r dataset runtime; do
                local runtime_formatted=$(printf '%02d:%02d:%02d' $((runtime/3600)) $((runtime%3600/60)) $((runtime%60)))
                echo "  $dataset: $runtime_formatted"
            done < "$OUTPUT_BASE/runtime_summary.txt"
        fi
        
        echo ""
        echo "Total Runtime: $TOTAL_RUNTIME"
        echo "================================================================================="
        
    } > "$summary_file"
    
    print_status $GREEN "Summary report saved to: $summary_file"
}

# Function to cleanup temporary files
cleanup() {
    print_status $BLUE "Cleaning up temporary files..."
    rm -f "$OUTPUT_BASE/runtime_summary.txt"
    print_status $GREEN "Cleanup completed!"
}

# Function to handle script interruption
handle_interrupt() {
    print_status $RED "Script interrupted by user!"
    print_status $YELLOW "Cleaning up..."
    cleanup
    print_status $RED "Script terminated!"
    exit 130
}

# Main execution
main() {
    # Set up signal handling
    trap handle_interrupt INT TERM
    
    # Record start time
    SCRIPT_START_TIME=$(date +%s)
    
    # Initialize master log
    mkdir -p "$LOG_DIR"
    touch "$MASTER_LOG"
    
    # Print header
    print_header
    
    # Setup
    setup_directories
    check_prerequisites
    
    # Run datasets
    local failed_datasets=()
    for dataset in $DATASETS; do
        if ! run_dataset "$dataset"; then
            failed_datasets+=("$dataset")
        fi
    done
    
    # Calculate total runtime
    SCRIPT_END_TIME=$(date +%s)
    TOTAL_RUNTIME_SECONDS=$((SCRIPT_END_TIME - SCRIPT_START_TIME))
    TOTAL_RUNTIME=$(printf '%02d:%02d:%02d' $((TOTAL_RUNTIME_SECONDS/3600)) $((TOTAL_RUNTIME_SECONDS%3600/60)) $((TOTAL_RUNTIME_SECONDS%60)))
    
    # Generate summary
    generate_summary
    
    # Cleanup
    cleanup
    
    # Print footer
    print_footer
    
    # Final status
    if [[ ${#failed_datasets[@]} -eq 0 ]]; then
        print_status $GREEN "🎉 All datasets processed successfully!"
        exit 0
    else
        print_status $RED "⚠️  Some datasets failed: ${failed_datasets[*]}"
        exit 1
    fi
}

# Run main function
main "$@"