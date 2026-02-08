"""
Experimental Design and Execution
"""

import yaml
import json
import pickle
import copy
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulator import SimulationEngine
from src.process_generator import ProcessGenerator
from src.statistics import StatisticsCollector
from src.visualization import Visualization
from src.schedulers import FCFS, SJF, RoundRobin, PriorityScheduler, MLFQ

class ExperimentRunner:
    """Run experiments as specified in the project requirements"""
    
    def __init__(self, config_file="config.yaml"):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.generator = ProcessGenerator(seed=self.config.get('random_seed', 42))
        self.viz = Visualization()
    
    def run_baseline_comparison(self):
        """Experiment 1: Baseline comparison of all algorithms"""
        print("\n" + "="*60)
        print("EXPERIMENT 1: BASELINE COMPARISON")
        print("="*60)
        
        # Generate workload
        processes = self.generator.generate_synthetic(
            num_processes=500,
            workload_type="mixed"
        )
        
        # Define schedulers to test
        schedulers = {
            "FCFS": FCFS(),
            "SJF (Non-preemptive)": SJF(preemptive=False),
            "SRTF (Preemptive)": SJF(preemptive=True),
            "RR-q10": RoundRobin(time_quantum=10),
            "RR-q20": RoundRobin(time_quantum=20),
            "RR-q50": RoundRobin(time_quantum=50),
            "Priority (Preemptive)": PriorityScheduler(preemptive=True),
        }
        
        if self.config.get('enable_mlfq', False):
            schedulers["MLFQ"] = MLFQ()
        
        # Run simulations
        results = {}
        for name, scheduler in schedulers.items():
            print(f"\nRunning {name}...")
            
            simulator = SimulationEngine(
                scheduler, 
                context_switch_time=self.config['context_switch_time']
            )
            
            completed_processes = simulator.run(copy.deepcopy(processes))
            stats_collector = StatisticsCollector(completed_processes, simulator.total_time)
            metrics = stats_collector.collect_all_metrics()
            
            results[name] = {
                'metrics': metrics,
                'processes': completed_processes,
                'history': simulator.scheduling_history[:100],  # Save first 100 events for Gantt
                'total_time': simulator.total_time
            }
            
            # Print summary
            summary = stats_collector.generate_summary_table(metrics)
            print(summary)
        
        # Save results
        with open('data/results/baseline_comparison.pkl', 'wb') as f:
            pickle.dump(results, f)
        
        # Generate visualizations
        self.viz.plot_algorithm_comparison(results)
        self.viz.plot_waiting_time_distribution(results)
        
        # Generate Gantt for first algorithm
        first_alg = list(results.keys())[0]
        self.viz.plot_gantt_chart(
            results[first_alg]['history'][:20],
            title=f"{first_alg} - First 20 Processes"
        )
        
        return results
    
    def run_sensitivity_analysis(self):
        """Experiment 2: Sensitivity analysis (vary parameters)"""
        print("\n" + "="*60)
        print("EXPERIMENT 2: SENSITIVITY ANALYSIS")
        print("="*60)
        
        # Test different time quanta for RR
        time_quanta = [5, 10, 20, 50, 100]
        results_rr = {}
        
        processes = self.generator.generate_synthetic(num_processes=500, workload_type="mixed")
        
        for quantum in time_quanta:
            print(f"\nTesting RR with quantum={quantum}ms")
            
            scheduler = RoundRobin(time_quantum=quantum)
            simulator = SimulationEngine(
                scheduler,
                context_switch_time=self.config['context_switch_time']
            )
            
            completed_processes = simulator.run(copy.deepcopy(processes))
            stats_collector = StatisticsCollector(completed_processes, simulator.total_time)
            metrics = stats_collector.collect_all_metrics()
            
            results_rr[f"RR-q{quantum}"] = metrics
        
        # Test with different numbers of processes
        process_counts = [100, 500, 1000]
        schedulers_to_test = {
            "FCFS": FCFS(),
            "SRTF": SJF(preemptive=True),
            "RR-q20": RoundRobin(time_quantum=20),
            "Priority": PriorityScheduler(preemptive=True),
        }
        
        results_scalability = {name: {} for name in schedulers_to_test.keys()}
        
        for proc_count in process_counts:
            print(f"\nTesting with {proc_count} processes")
            processes = self.generator.generate_synthetic(num_processes=proc_count, workload_type="mixed")
            
            for name, scheduler in schedulers_to_test.items():
                simulator = SimulationEngine(
                    scheduler,
                    context_switch_time=self.config['context_switch_time']
                )
                
                completed_processes = simulator.run(copy.deepcopy(processes))
                stats_collector = StatisticsCollector(completed_processes, simulator.total_time)
                metrics = stats_collector.collect_all_metrics()
                
                results_scalability[name][proc_count] = metrics
        
        # Save results
        sensitivity_results = {
            'rr_time_quanta': results_rr,
            'scalability': results_scalability
        }
        
        with open('data/results/sensitivity_analysis.pkl', 'wb') as f:
            pickle.dump(sensitivity_results, f)
        
        # Generate visualizations
        self._plot_sensitivity_results(sensitivity_results)
        
        return sensitivity_results
    
    def run_workload_specific_tests(self):
        """Experiment 3: Workload-specific performance"""
        print("\n" + "="*60)
        print("EXPERIMENT 3: WORKLOAD-SPECIFIC PERFORMANCE")
        print("="*60)
        
        workload_types = ["cpu_intensive", "io_intensive", "mixed"]
        schedulers = {
            "FCFS": FCFS(),
            "SRTF": SJF(preemptive=True),
            "RR-q20": RoundRobin(time_quantum=20),
            "Priority": PriorityScheduler(preemptive=True),
        }
        
        if self.config.get('enable_mlfq', False):
            schedulers["MLFQ"] = MLFQ()
        
        workload_results = {}
        
        for workload in workload_types:
            print(f"\nTesting {workload.upper()} workload")
            
            if workload == "trace":
                # Use trace files
                trace_file = f"data/trace_files/{workload}.txt"
                processes = self.generator.generate_from_trace(trace_file)
            else:
                # Generate synthetic workload
                processes = self.generator.generate_synthetic(
                    num_processes=300,
                    workload_type=workload
                )
            
            workload_results[workload] = {}
            
            for name, scheduler in schedulers.items():
                print(f"  Running {name}...")
                
                simulator = SimulationEngine(
                    scheduler,
                    context_switch_time=self.config['context_switch_time']
                )
                
                completed_processes = simulator.run(copy.deepcopy(processes))
                stats_collector = StatisticsCollector(completed_processes, simulator.total_time)
                metrics = stats_collector.collect_all_metrics()
                
                workload_results[workload][name] = metrics
        
        # Save results
        with open('data/results/workload_specific.pkl', 'wb') as f:
            pickle.dump(workload_results, f)
        
        # Generate visualizations
        self._plot_workload_specific_results(workload_results)
        
        return workload_results
    
    def run_scalability_test(self):
        """Experiment 4: Scalability test with increasing load"""
        print("\n" + "="*60)
        print("EXPERIMENT 4: SCALABILITY TEST")
        print("="*60)
        
        process_counts = [100, 200, 500, 800, 1000, 1500, 2000]
        schedulers = {
            "FCFS": FCFS(),
            "SRTF": SJF(preemptive=True),
            "RR-q20": RoundRobin(time_quantum=20),
            "Priority": PriorityScheduler(preemptive=True),
        }
        
        scalability_results = {name: {} for name in schedulers.keys()}
        
        for proc_count in process_counts:
            print(f"\nTesting scalability with {proc_count} processes")
            
            # Generate workload with increasing arrival rate for heavier load
            arrival_rate = 0.01 * (proc_count / 500)  # Scale arrival rate with load
            processes = self.generator.generate_synthetic(
                num_processes=proc_count,
                workload_type="mixed"
            )
            
            for name, scheduler in schedulers.items():
                simulator = SimulationEngine(
                    scheduler,
                    context_switch_time=self.config['context_switch_time']
                )
                
                completed_processes = simulator.run(copy.deepcopy(processes))
                stats_collector = StatisticsCollector(completed_processes, simulator.total_time)
                metrics = stats_collector.collect_all_metrics()
                
                scalability_results[name][proc_count] = metrics
        
        # Save results
        with open('data/results/scalability_test.pkl', 'wb') as f:
            pickle.dump(scalability_results, f)
        
        # Generate visualization
        self.viz.plot_scalability_analysis(scalability_results)
        
        return scalability_results
    
    def _plot_sensitivity_results(self, results):
        """Plot sensitivity analysis results"""
        # Plot RR time quantum sensitivity
        rr_results = results.get('rr_time_quanta', {})
        
        if rr_results:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            axes = axes.flatten()
            
            metrics_to_plot = ['avg_turnaround', 'avg_waiting', 'cpu_utilization', 'throughput']
            
            for idx, metric in enumerate(metrics_to_plot):
                if idx >= len(axes):
                    break
                
                ax = axes[idx]
                quanta = []
                values = []
                
                for name, metrics in rr_results.items():
                    quantum = int(name.split('-q')[1])
                    quanta.append(quantum)
                    values.append(metrics.get(metric, 0))
                
                # Sort by quantum
                sorted_data = sorted(zip(quanta, values))
                quanta_sorted, values_sorted = zip(*sorted_data)
                
                ax.plot(quanta_sorted, values_sorted, 'o-', linewidth=2, markersize=8)
                ax.set_xlabel('Time Quantum (ms)')
                ax.set_ylabel(metric.replace('_', ' ').title())
                ax.set_title(f'RR: {metric.replace("_", " ").title()} vs Time Quantum')
                ax.grid(True, alpha=0.3)
                ax.set_xscale('log')
            
            plt.suptitle('Round Robin Sensitivity to Time Quantum', fontsize=16, y=1.02)
            plt.tight_layout()
            plt.savefig('data/results/rr_sensitivity.png', dpi=150, bbox_inches='tight')
            plt.close()
    
    def _plot_workload_specific_results(self, results):
        """Plot workload-specific results"""
        workload_types = list(results.keys())
        schedulers = list(results[workload_types[0]].keys())
        
        # Create comparison for each metric
        metrics_to_plot = ['avg_turnaround', 'avg_waiting', 'cpu_utilization', 'throughput']
        metric_titles = ['Avg Turnaround Time', 'Avg Waiting Time', 'CPU Utilization', 'Throughput']
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        for idx, (metric, title) in enumerate(zip(metrics_to_plot, metric_titles)):
            ax = axes[idx]
            
            x = np.arange(len(workload_types))
            width = 0.8 / len(schedulers)
            
            for i, scheduler in enumerate(schedulers):
                values = [results[workload][scheduler].get(metric, 0) for workload in workload_types]
                offset = (i - len(schedulers)/2 + 0.5) * width
                bars = ax.bar(x + offset, values, width, label=scheduler)
            
            ax.set_xlabel('Workload Type')
            ax.set_ylabel(title)
            ax.set_title(f'{title} by Workload Type')
            ax.set_xticks(x)
            ax.set_xticklabels([w.replace('_', ' ').title() for w in workload_types])
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, axis='y', alpha=0.3)
        
        plt.suptitle('Performance Across Different Workload Types', fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig('data/results/workload_comparison.png', dpi=150, bbox_inches='tight')
        plt.close()

def run_all_experiments():
    """Run all experiments and generate comprehensive report"""
    runner = ExperimentRunner()
    
    print("CPU SCHEDULER SIMULATION - COMPREHENSIVE EXPERIMENTS")
    print("="*60)
    
    # Run all experiments
    baseline_results = runner.run_baseline_comparison()
    sensitivity_results = runner.run_sensitivity_analysis()
    workload_results = runner.run_workload_specific_tests()
    scalability_results = runner.run_scalability_test()
    
    print("\n" + "="*60)
    print("ALL EXPERIMENTS COMPLETED SUCCESSFULLY")
    print("="*60)
    print("\nResults saved to data/results/")
    print("Use generate_report.py to create technical report")
    
    return {
        'baseline': baseline_results,
        'sensitivity': sensitivity_results,
        'workload': workload_results,
        'scalability': scalability_results
    }

if __name__ == "__main__":
    run_all_experiments()