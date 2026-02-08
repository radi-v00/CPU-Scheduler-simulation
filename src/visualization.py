"""
Visualization for CPU Scheduler Simulation
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Any
import os

class Visualization:
    """Generate visualizations for simulation results"""
    
    def __init__(self, output_dir="data/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def plot_gantt_chart(self, history: List[Dict], title="Gantt Chart", max_processes=20):
        """Generate Gantt chart for scheduling visualization"""
        if not history:
            print("No scheduling history available")
            return
        
        # Filter to unique process IDs for coloring
        process_ids = list(set([h['process_id'] for h in history]))
        if len(process_ids) > max_processes:
            # Take only first max_processes unique processes
            history = [h for h in history if h['process_id'] < max_processes]
            process_ids = [pid for pid in process_ids if pid < max_processes]
        
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Create color map
        colors = plt.cm.tab20c(np.linspace(0, 1, len(process_ids)))
        color_map = {pid: colors[i % len(colors)] for i, pid in enumerate(process_ids)}
        
        # Plot each scheduling interval
        y_ticks = []
        y_labels = []
        seen_pids = set()
        
        for i, event in enumerate(history):
            pid = event['process_id']
            start = event['start']
            end = event['end']
            
            # Create horizontal bar
            ax.broken_barh([(start, end - start)], 
                          (pid * 10, 8), 
                          facecolors=color_map[pid],
                          edgecolor='black',
                          linewidth=1)
            
            # Add process ID label (only once per process)
            if pid not in seen_pids:
                seen_pids.add(pid)
                y_ticks.append(pid * 10 + 4)
                y_labels.append(f"P{pid}")
        
        # Customize plot
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Process ID')
        ax.set_title(title)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.grid(True, axis='x', alpha=0.3)
        
        # Add legend
        legend_patches = [plt.Rectangle((0, 0), 1, 1, fc=color_map[pid]) 
                         for pid in process_ids[:10]]  # Limit legend size
        ax.legend(legend_patches, [f"P{pid}" for pid in process_ids[:10]], 
                 loc='upper right', bbox_to_anchor=(1.15, 1))
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/gantt_chart.png", dpi=150, bbox_inches='tight')
        plt.savefig(f"{self.output_dir}/gantt_chart.pdf")
        plt.close()
        print(f"Gantt chart saved to {self.output_dir}/gantt_chart.png")
    
    def plot_algorithm_comparison(self, results: Dict[str, Dict]):
        """Generate bar chart comparing algorithms across metrics"""
        if not results:
            print("No results to visualize")
            return
        
        # Extract metrics for comparison
        algorithms = list(results.keys())
        metrics_to_plot = ['avg_turnaround', 'avg_waiting', 'avg_response', 
                          'cpu_utilization', 'throughput', 'fairness']
        
        metric_labels = {
            'avg_turnaround': 'Avg Turnaround Time (ms)',
            'avg_waiting': 'Avg Waiting Time (ms)',
            'avg_response': 'Avg Response Time (ms)',
            'cpu_utilization': 'CPU Utilization (%)',
            'throughput': 'Throughput (proc/sec)',
            'fairness': 'Fairness Index'
        }
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.flatten()
        
        for idx, metric in enumerate(metrics_to_plot):
            if idx >= len(axes):
                break
            
            ax = axes[idx]
            values = [results[alg]['metrics'].get(metric, 0) for alg in algorithms]
            
            bars = ax.bar(range(len(algorithms)), values, 
                         color=plt.cm.Set3(np.linspace(0, 1, len(algorithms))))
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{value:.2f}', ha='center', va='bottom', fontsize=9)
            
            ax.set_xlabel('Scheduling Algorithm')
            ax.set_ylabel(metric_labels[metric])
            ax.set_title(f'{metric_labels[metric]} Comparison')
            ax.set_xticks(range(len(algorithms)))
            ax.set_xticklabels(algorithms, rotation=45, ha='right')
            ax.grid(True, axis='y', alpha=0.3)
        
        plt.suptitle('CPU Scheduling Algorithms Performance Comparison', fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/algorithm_comparison.png", dpi=150, bbox_inches='tight')
        plt.savefig(f"{self.output_dir}/algorithm_comparison.pdf")
        plt.close()
        print(f"Algorithm comparison chart saved to {self.output_dir}/algorithm_comparison.png")
    
    def plot_waiting_time_distribution(self, results: Dict[str, Dict]):
        """Generate box plot of waiting time distributions"""
        if not results:
            print("No results to visualize")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data for box plot
        data_to_plot = []
        labels = []
        
        for alg_name, result in results.items():
            waiting_times = [p.waiting_time for p in result['processes']]
            if waiting_times:
                data_to_plot.append(waiting_times)
                labels.append(alg_name)
        
        # Create box plot
        box = ax.boxplot(data_to_plot, labels=labels, patch_artist=True, showfliers=True)
        
        # Color the boxes
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        for patch, color in zip(box['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_xlabel('Scheduling Algorithm')
        ax.set_ylabel('Waiting Time (ms)')
        ax.set_title('Waiting Time Distribution Across Algorithms')
        ax.grid(True, axis='y', alpha=0.3)
        
        # Add mean markers
        for i, data in enumerate(data_to_plot):
            mean_val = np.mean(data)
            ax.plot(i + 1, mean_val, 'rD', markersize=8, label='Mean' if i == 0 else "")
        
        ax.legend(['Mean'])
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/waiting_time_distribution.png", dpi=150, bbox_inches='tight')
        plt.savefig(f"{self.output_dir}/waiting_time_distribution.pdf")
        plt.close()
        print(f"Waiting time distribution saved to {self.output_dir}/waiting_time_distribution.png")
    
    def plot_scalability_analysis(self, scalability_results: Dict):
        """Plot scalability analysis (metrics vs number of processes)"""
        if not scalability_results:
            print("No scalability results to visualize")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        metrics_to_plot = ['avg_turnaround', 'avg_waiting', 'cpu_utilization', 'throughput']
        metric_titles = ['Avg Turnaround Time', 'Avg Waiting Time', 'CPU Utilization', 'Throughput']
        metric_units = ['ms', 'ms', '%', 'proc/sec']
        
        for idx, (metric, title, unit) in enumerate(zip(metrics_to_plot, metric_titles, metric_units)):
            if idx >= len(axes):
                break
            
            ax = axes[idx]
            
            for alg_name, alg_results in scalability_results.items():
                process_counts = []
                metric_values = []
                
                for proc_count, results in alg_results.items():
                    if metric in results:
                        process_counts.append(proc_count)
                        metric_values.append(results[metric])
                
                if process_counts and metric_values:
                    ax.plot(process_counts, metric_values, 'o-', linewidth=2, 
                           markersize=8, label=alg_name)
            
            ax.set_xlabel('Number of Processes')
            ax.set_ylabel(f'{title} ({unit})')
            ax.set_title(f'{title} vs Process Count')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.suptitle('Scalability Analysis of Scheduling Algorithms', fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scalability_analysis.png", dpi=150, bbox_inches='tight')
        plt.savefig(f"{self.output_dir}/scalability_analysis.pdf")
        plt.close()
        print(f"Scalability analysis saved to {self.output_dir}/scalability_analysis.png")