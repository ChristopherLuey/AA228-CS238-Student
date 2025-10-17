import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

if __package__ is None or __package__ == "":
    PACKAGE_ROOT = Path(__file__).resolve().parent
    if str(PACKAGE_ROOT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_ROOT))
    from structure_learning import (  # type: ignore
        DiscreteDataset,
        StructureLearner,
        default_config,
    )
else:  # pragma: no cover - exercised in package context
    from .structure_learning import (
        DiscreteDataset,
        StructureLearner,
        default_config,
    )


def setup_logging(log_file: str) -> logging.Logger:
    """Set up logging to both file and console."""
    logger = logging.getLogger('project1')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler for progress info
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def write_gph(edges: List[Tuple[int, int]], idx2names: Dict[int, str], filename: str) -> None:
    # Ensure destination directory exists
    out_path = Path(filename)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as fh:
        for u, v in edges:
            fh.write(f"{idx2names[u]}, {idx2names[v]}\n")


def compute(infile: str, outfile: str, generate_png: bool = True) -> None:
    # Set up logging
    log_file = Path(outfile).parent / f"{Path(outfile).stem}_log.txt"
    logger = setup_logging(str(log_file))
    
    # Log run start
    start_time = time.time()
    logger.info("="*80)
    logger.info(f"Starting Bayesian Structure Learning")
    logger.info(f"Input file: {infile}")
    logger.info(f"Output file: {outfile}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
    
    # Load dataset and log statistics
    logger.info("Loading dataset...")
    dataset = DiscreteDataset(infile)
    logger.info(f"Dataset loaded successfully")
    logger.info(f"Variables: {dataset.num_vars}")
    logger.info(f"Rows: {dataset.num_rows}")
    logger.info(f"Variable names: {dataset.names}")
    logger.info(f"Cardinalities: {dataset.cardinalities}")
    
    # Generate and log configuration
    config = default_config(dataset.num_vars, dataset.num_rows)
    logger.info("Configuration generated:")
    logger.info(f"  Max parents: {config.max_parents}")
    logger.info(f"  Hill restarts: {config.hill_restarts}")
    logger.info(f"  Tabu tenure: {config.tabu_tenure}")
    logger.info(f"  SA iterations: {config.sa_iterations}")
    logger.info(f"  SA start temp: {config.sa_start_temp}")
    logger.info(f"  SA end temp: {config.sa_end_temp}")
    logger.info(f"  GA population: {config.ga_population}")
    logger.info(f"  GA generations: {config.ga_generations}")
    logger.info(f"  GA elite fraction: {config.ga_elite_frac}")
    logger.info(f"  GA mutation rate: {config.ga_mutation_rate}")
    logger.info(f"  GA crossover rate: {config.ga_crossover_rate}")
    logger.info(f"  Candidate limit: {config.candidate_limit}")
    logger.info(f"  Random seed: {config.random_seed}")
    
    # Run structure learning
    logger.info("Starting structure learning...")
    learner = StructureLearner(dataset, config)
    learning_start = time.time()
    result = learner.learn()
    learning_end = time.time()
    
    # Log results
    logger.info("Structure learning completed!")
    logger.info(f"Learning time: {learning_end - learning_start:.2f} seconds")
    logger.info(f"Best algorithm: {result.algorithm}")
    logger.info(f"Best score: {result.score:.6f}")
    logger.info(f"Algorithm details: {result.info}")
    
    # Count edges in final graph
    edges = list(result.dag.edges())
    logger.info(f"Final graph has {len(edges)} edges")
    logger.info("Final graph edges:")
    idx2name = {idx: name for idx, name in enumerate(dataset.names)}
    for u, v in edges:
        logger.info(f"  {idx2name[u]} -> {idx2name[v]}")
    
    # Write output file
    logger.info("Writing output file...")
    write_gph(edges, idx2name, outfile)
    
    # Log completion
    total_time = time.time() - start_time
    logger.info("="*80)
    logger.info(f"Run completed successfully!")
    logger.info(f"Total runtime: {total_time:.2f} seconds")
    logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
    
    # Create JSON summary for easy data extraction
    summary = {
        "timestamp": datetime.now().isoformat(),
        "input_file": infile,
        "output_file": outfile,
        "dataset_stats": {
            "num_vars": dataset.num_vars,
            "num_rows": dataset.num_rows,
            "variable_names": dataset.names,
            "cardinalities": dataset.cardinalities.tolist()
        },
        "config": {
            "max_parents": config.max_parents,
            "hill_restarts": config.hill_restarts,
            "tabu_tenure": config.tabu_tenure,
            "sa_iterations": config.sa_iterations,
            "sa_start_temp": config.sa_start_temp,
            "sa_end_temp": config.sa_end_temp,
            "ga_population": config.ga_population,
            "ga_generations": config.ga_generations,
            "ga_elite_frac": config.ga_elite_frac,
            "ga_mutation_rate": config.ga_mutation_rate,
            "ga_crossover_rate": config.ga_crossover_rate,
            "candidate_limit": config.candidate_limit,
            "random_seed": config.random_seed
        },
        "results": {
            "algorithm": result.algorithm,
            "score": result.score,
            "details": result.info,
            "num_edges": len(edges),
            "edges": [(idx2name[u], idx2name[v]) for u, v in edges]
        },
        "timing": {
            "total_runtime": total_time,
            "learning_time": learning_end - learning_start
        }
    }
    
    # Write JSON summary
    json_file = Path(outfile).parent / f"{Path(outfile).stem}_summary.json"
    with open(json_file, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary saved to: {json_file}")
    
    # Generate PNG visualization
    if generate_png:
        logger.info("Generating PNG visualization...")
        try:
            png_file = Path(outfile).parent / f"{Path(outfile).stem}.png"
            plot_script = Path(__file__).parent / "plot_graph.py"
            
            # Run plot_graph.py to generate PNG
            cmd = [
                sys.executable, 
                str(plot_script),
                str(outfile),
                "--output", str(png_file),
                "--no-show",
                "--title", Path(outfile).stem,
                "--layout", "hierarchy",
                "--figsize", "12x10"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info(f"PNG visualization saved to: {png_file}")
            else:
                logger.warning(f"Failed to generate PNG: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.warning("PNG generation timed out")
        except Exception as e:
            logger.warning(f"Failed to generate PNG: {e}")


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AA228 Bayesian structure learning reference implementation."
    )
    parser.add_argument("input_csv", help="CSV file with discrete data.")
    parser.add_argument("output_gph", help="Destination .gph filename.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only initialize learner and print configuration summary.",
    )
    parser.add_argument(
        "--no-png",
        action="store_true",
        help="Skip PNG visualization generation.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    infile = args.input_csv
    # Resolve output path: default to project1/output/<name>.gph when no directory provided
    requested = Path(args.output_gph)
    # Append .gph if user omitted extension
    if requested.suffix.lower() != ".gph":
        requested = requested.with_suffix(".gph")

    if requested.is_absolute() or requested.parent != Path("."):
        outfile_path = requested
    else:
        # Save under the package root's output directory
        package_root = Path(__file__).resolve().parent
        outfile_path = package_root / "output" / requested.name

    outfile = str(outfile_path)
    if args.dry_run:
        # Set up logging for dry run
        log_file = Path(outfile).parent / f"{Path(outfile).stem}_dryrun_log.txt"
        logger = setup_logging(str(log_file))
        
        logger.info("="*80)
        logger.info(f"DRY RUN - Bayesian Structure Learning")
        logger.info(f"Input file: {infile}")
        logger.info(f"Output file: {outfile}")
        logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        dataset = DiscreteDataset(infile)
        config = default_config(dataset.num_vars, dataset.num_rows)
        
        logger.info(f"Dataset: {infile}")
        logger.info(f"Variables: {dataset.num_vars}")
        logger.info(f"Rows: {dataset.num_rows}")
        logger.info(f"Variable names: {dataset.names}")
        logger.info(f"Cardinalities: {dataset.cardinalities}")
        logger.info(f"Configuration: {config}")
        
        logger.info("="*80)
        logger.info("DRY RUN COMPLETED")
        logger.info("="*80)
        return
    compute(infile, outfile, generate_png=not args.no_png)


if __name__ == "__main__":
    main()
