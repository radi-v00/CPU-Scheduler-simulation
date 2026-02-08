"""
Statistics Collection and Performance Metrics Calculation
"""

import numpy as np
from typing import List, Dict, Any
from .simulator import PCB

class StatisticsCollector:
    """Collect and calculate performance metrics"""
    
    def __init__(self, processes: List[PCB], total_time: int):
        self.processes = processes
        self.total_time = total_time
    
    def collect_all_metrics(self) -> Dict[str, float]:
        """Collect all performance metrics"""
        metrics = {}
        
        # Per-process metrics
        turnaround_times = []
        waiting_times = []
        response_times = []
        cpu_burst_times = []
        
        for process in self.processes:
            turnaround_times.append(process.turnaround_time)
            waiting_times.append(process.waiting_time)
            response_times.append(process.response_time)
            cpu_burst_times.append(process.cpu_time_used)
        
        # System-wide metrics
        metrics['avg_turnaround'] = np.mean(turnaround_times) if turnaround_times else 0
        metrics['std_turnaround'] = np.std(turnaround_times) if turnaround_times else 0
        metrics['avg_waiting'] = np.mean(waiting_times) if waiting_times else 0
        metrics['std_waiting'] = np.std(waiting_times) if waiting_times else 0
        metrics['avg_response'] = np.mean(response_times) if response_times else 0
        metrics['std_response'] = np.std(response_times) if response_times else 0
        
        # CPU utilization
        total_cpu_time = sum(cpu_burst_times)
        metrics['cpu_utilization'] = (total_cpu_time / self.total_time * 100) if self.total_time > 0 else 0
        
        # Throughput (processes per second)
        metrics['throughput'] = (len(self.processes) / self.total_time * 1000) if self.total_time > 0 else 0
        
        # Fairness index (Jain's Fairness)
        metrics['fairness'] = self._calculate_fairness_index(turnaround_times)
        
        # Additional statistics
        metrics['min_turnaround'] = min(turnaround_times) if turnaround_times else 0
        metrics['max_turnaround'] = max(turnaround_times) if turnaround_times else 0
        metrics['min_waiting'] = min(waiting_times) if waiting_times else 0
        metrics['max_waiting'] = max(waiting_times) if waiting_times else 0
        
        return metrics
    
    def _calculate_fairness_index(self, turnaround_times: List[float]) -> float:
        """Calculate Jain's Fairness Index"""
        if not turnaround_times:
            return 0
        
        # Normalize turnaround times
        min_time = min(turnaround_times)
        if min_time == 0:
            min_time = 1
        
        normalized_times = [t / min_time for t in turnaround_times]
        
        # Jain's formula: F = (Σx_i)² / (n * Σx_i²)
        numerator = sum(normalized_times) ** 2
        denominator = len(normalized_times) * sum(x ** 2 for x in normalized_times)
        
        return numerator / denominator if denominator > 0 else 0
    
    def generate_summary_table(self, metrics: Dict[str, float]) -> str:
        """Generate formatted summary table"""
        summary = f"{'='*60}\n"
        summary += "PERFORMANCE METRICS SUMMARY\n"
        summary += f"{'='*60}\n"
        summary += f"Total processes: {len(self.processes)}\n"
        summary += f"Total simulation time: {self.total_time} ms\n\n"
        
        summary += f"{'Metric':<25} {'Value':<15} {'Unit':<10}\n"
        summary += f"{'-'*50}\n"
        
        for metric, value in metrics.items():
            if 'avg' in metric or metric in ['cpu_utilization', 'fairness', 'throughput']:
                if 'turnaround' in metric:
                    unit = 'ms'
                    fmt_value = f"{value:.2f}"
                elif 'waiting' in metric or 'response' in metric:
                    unit = 'ms'
                    fmt_value = f"{value:.2f}"
                elif metric == 'cpu_utilization':
                    unit = '%'
                    fmt_value = f"{value:.2f}"
                elif metric == 'throughput':
                    unit = 'proc/sec'
                    fmt_value = f"{value:.2f}"
                elif metric == 'fairness':
                    unit = ''
                    fmt_value = f"{value:.3f}"
                else:
                    unit = ''
                    fmt_value = f"{value:.2f}"
                
                summary += f"{metric:<25} {fmt_value:<15} {unit:<10}\n"
        
        return summary