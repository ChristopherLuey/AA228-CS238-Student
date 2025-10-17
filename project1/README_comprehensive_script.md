# AA228 Bayesian Network Structure Learning - Comprehensive Run Script

This directory contains a comprehensive shell script that runs Bayesian network structure learning on all three datasets (small, medium, large) with full monitoring, logging, and organization.

## Files

- `run_all_datasets.sh` - Main comprehensive script
- `test_script.sh` - Quick test script for verification
- `project1.py` - Modified to automatically generate PNG visualizations
- `plot_graph.py` - Graph visualization utility
- `structure_learning.py` - Core structure learning implementation

## Usage

### Run All Datasets (Comprehensive)

```bash
./run_all_datasets.sh
```

This will:
1. Run structure learning on small, medium, and large datasets
2. Create separate output folders for each dataset
3. Generate PNG visualizations automatically
4. Create comprehensive logs and summaries
5. Provide runtime statistics and error handling

### Quick Test (Small Dataset Only)

```bash
./test_script.sh
```

### Manual Run (Individual Dataset)

```bash
python3 project1.py data/small.csv output/small/small.gph
python3 project1.py data/medium.csv output/medium/medium.gph  
python3 project1.py data/large.csv output/large/large.gph
```

## Output Structure

After running the comprehensive script, you'll have:

```
output/
├── logs/
│   └── master_run_YYYYMMDD_HHMMSS.log
├── small/
│   ├── small.gph
│   ├── small.png
│   ├── small_summary.json
│   └── small_log.txt
├── medium/
│   ├── medium.gph
│   ├── medium.png
│   ├── medium_summary.json
│   └── medium_log.txt
├── large/
│   ├── large.gph
│   ├── large.png
│   ├── large_summary.json
│   └── large_log.txt
└── run_summary_YYYYMMDD_HHMMSS.txt
```

## Features

### Comprehensive Monitoring
- Real-time progress tracking
- Colored output for easy reading
- Detailed logging to files
- Runtime measurement for each dataset
- Error handling and recovery

### Automatic Organization
- Separate folders for each dataset
- Consistent naming conventions
- Master log file for overall run
- Summary report generation

### Visualization
- Automatic PNG generation using `plot_graph.py`
- Hierarchical layout for better readability
- High-resolution output (300 DPI)

### Error Handling
- Prerequisites checking
- Graceful failure handling
- Interrupt signal handling (Ctrl+C)
- Detailed error reporting

## Configuration

The script automatically detects:
- Dataset files in `data/` directory
- Python installation
- Required project files
- Output directory structure

## Requirements

- Python 3 with required packages (pandas, numpy, matplotlib, networkx, tqdm)
- Bash shell
- Sufficient disk space for output files
- Memory requirements vary by dataset size

## Troubleshooting

1. **Permission denied**: Make sure script is executable (`chmod +x run_all_datasets.sh`)
2. **Python not found**: Install Python 3 and ensure it's in PATH
3. **Missing data files**: Ensure `small.csv`, `medium.csv`, `large.csv` exist in `data/` directory
4. **Memory issues**: Large dataset may require significant RAM
5. **Long runtime**: Medium and large datasets can take 10+ minutes each

## Output Files Explained

- `.gph` - Graph structure file (edge list format)
- `.png` - Visual representation of the learned network
- `_summary.json` - Detailed results and configuration
- `_log.txt` - Detailed execution log
- `run_summary_*.txt` - Overall run summary with statistics
