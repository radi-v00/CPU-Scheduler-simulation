#!/usr/bin/env python3
"""
CPU Scheduler Simulation - Main Entry Point
Mehrdad Ahmadzadeh - Fall 1404
"""

import argparse
import copy
import yaml
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulator import SimulationEngine  # pyright: ignore[reportMissingImports]
from src.process_generator import ProcessGenerator  # pyright: ignore[reportMissingImports]
from src.visualization import Visualization  # pyright: ignore[reportMissingImports]
from src.statistics import StatisticsCollector  # pyright: ignore[reportMissingImports]
from src.schedulers import FCFS, SJF, RoundRobin, PriorityScheduler, MLFQ  # pyright: ignore[reportMissingImports]

def load_config(config_file="config.yaml"):
    """Load configuration from YAML file"""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="CPU Scheduler Simulation")
    parser.add_argument("--algorithm", type=str, default="fcfs",
                       choices=["fcfs", "sjf", "rr", "priority", "mlfq", "all"],
                       help="Scheduling algorithm to use")
    parser.add_argument("--workload", type=str, default="synthetic",
                       choices=["synthetic", "trace", "cpu_intensive", "io_intensive", "mixed"],
                       help="Type of workload")
    parser.add_argument("--processes", type=int, default=500,
                       help="Number of processes")
    parser.add_argument("--time_quantum", type=int, default=20,
                       help="Time quantum for RR (ms)")
    parser.add_argument("--config", type=str, default="config.yaml",
                       help="Configuration file")
    parser.add_argument("--visualize", action="store_true",
                       help="Generate visualizations")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    print("=" * 60)
    print("CPU SCHEDULER SIMULATION")
    print("=" * 60)
    
    # Generate workload
    generator = ProcessGenerator()
    
    if args.workload == "trace":
        trace_file = f"data/trace_files/{args.workload}.txt"
        processes = generator.generate_from_trace(trace_file)
    else:
        processes = generator.generate_synthetic(
            num_processes=args.processes,
            workload_type=args.workload
        )
    
    print(f"Generated {len(processes)} processes")
    print(f"Workload type: {args.workload}")
    
    # Select scheduler
    schedulers_to_run = []
    
    if args.algorithm == "all":
        schedulers_to_run = [
            ("FCFS", FCFS()),
            ("SJF", SJF(preemptive=False)),
            ("SRTF", SJF(preemptive=True)),
            (f"RR-q{args.time_quantum}", RoundRobin(time_quantum=args.time_quantum)),
            ("Priority", PriorityScheduler(preemptive=True)),
        ]
        if config.get('enable_mlfq', False):
            schedulers_to_run.append(("MLFQ", MLFQ()))
    else:
        scheduler_map = {
            "fcfs": ("FCFS", FCFS()),
            "sjf": ("SJF", SJF(preemptive=False)),
            "rr": (f"RR-q{args.time_quantum}", RoundRobin(time_quantum=args.time_quantum)),
            "priority": ("Priority", PriorityScheduler(preemptive=True)),
            "mlfq": ("MLFQ", MLFQ())
        }
        schedulers_to_run = [scheduler_map[args.algorithm]]
    
    # Run simulations
    results = {}
    for name, scheduler in schedulers_to_run:
        print(f"\nRunning {name} scheduler...")
        simulator = SimulationEngine(scheduler, 
                                   context_switch_time=config['context_switch_time'])
        
        # Run simulation
        completed_processes = simulator.run(copy.deepcopy(processes))
        
        # Collect statistics
        stats_collector = StatisticsCollector(completed_processes, 
                                            simulator.total_time)
        metrics = stats_collector.collect_all_metrics()
        
        results[name] = {
            'metrics': metrics,
            'processes': completed_processes,
            'history': simulator.scheduling_history,
            'total_time': simulator.total_time
        }
        
        # Print summary
        print(f"  Total simulation time: {simulator.total_time} ms")
        print(f"  Average turnaround: {metrics['avg_turnaround']:.2f} ms")
        print(f"  Average waiting: {metrics['avg_waiting']:.2f} ms")
        print(f"  CPU utilization: {metrics['cpu_utilization']:.2f}%")
        print(f"  Throughput: {metrics['throughput']:.2f} processes/sec")
        print(f"  Fairness index: {metrics['fairness']:.3f}")
    
    # Generate visualizations
    if args.visualize and results:
        viz = Visualization()
        
        # Save results for later analysis
        import pickle
        with open('data/results/latest_simulation.pkl', 'wb') as f:
            pickle.dump(results, f)
        
        # Generate comparison charts
        viz.plot_algorithm_comparison(results)
        
        # Generate Gantt chart for first scheduler
        first_scheduler = list(results.keys())[0]
        viz.plot_gantt_chart(results[first_scheduler]['history'][:20], 
                           title=f"{first_scheduler} - First 20 Processes")
        
        # Generate waiting time distribution
        viz.plot_waiting_time_distribution(results)
        
        print("\nVisualizations saved to data/results/")
    
    return results

if __name__ == "__main__":
    main()