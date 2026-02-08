#!/usr/bin/env python3
"""
Main script to run all experiments
"""

import sys
import os
import argparse

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from experiments import run_all_experiments

def main():
    parser = argparse.ArgumentParser(description="Run CPU Scheduler Experiments")
    parser.add_argument("--experiment", type=str, default="all",
                       choices=["all", "baseline", "sensitivity", "workload", "scalability"],
                       help="Which experiment to run")
    parser.add_argument("--config", type=str, default="config.yaml",
                       help="Configuration file")
    parser.add_argument("--visualize", action="store_true",
                       help="Generate visualizations")
    
    args = parser.parse_args()
    
    if args.experiment == "all":
        results = run_all_experiments()
    else:
        from experiments import ExperimentRunner
        runner = ExperimentRunner(args.config)
        
        if args.experiment == "baseline":
            results = runner.run_baseline_comparison()
        elif args.experiment == "sensitivity":
            results = runner.run_sensitivity_analysis()
        elif args.experiment == "workload":
            results = runner.run_workload_specific_tests()
        elif args.experiment == "scalability":
            results = runner.run_scalability_test()
        else:
            print(f"Unknown experiment: {args.experiment}")
            return
    
    print("\n" + "="*60)
    print("EXPERIMENTS COMPLETED")
    print("="*60)
    print(f"\nResults saved to data/results/")
    
    if args.visualize:
        print("Visualizations generated in data/results/")
    
    return results

if __name__ == "__main__":
    main()