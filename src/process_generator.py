"""
Workload Generation for CPU Scheduler Simulation
"""

import numpy as np
import random
from typing import List, Dict, Any
from .simulator import PCB

class ProcessGenerator:
    """Generate synthetic and trace-based workloads"""
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        random.seed(seed)
    
    def generate_synthetic(self, num_processes=500, workload_type="mixed") -> List[PCB]:
        """
        Generate synthetic workload with configurable characteristics
        
        Args:
            num_processes: Number of processes to generate
            workload_type: "cpu_intensive", "io_intensive", or "mixed"
        
        Returns:
            List of PCB objects
        """
        processes = []
        
        # Configure distributions based on workload type
        if workload_type == "cpu_intensive":
            cpu_mean, cpu_std = 80, 20
            io_range = (5, 30)
            arrival_rate = 0.01  # Less frequent arrivals
        elif workload_type == "io_intensive":
            cpu_mean, cpu_std = 20, 10
            io_range = (50, 200)
            arrival_rate = 0.02  # More frequent arrivals
        else:  # mixed
            cpu_mean, cpu_std = 50, 20
            io_range = (10, 100)
            arrival_rate = 0.015
        
        current_time = 0
        
        for i in range(num_processes):
            # Arrival time: Poisson process (exponential inter-arrival times)
            inter_arrival = np.random.exponential(1/arrival_rate)
            current_time += max(1, int(inter_arrival))
            
            # CPU burst: Normal distribution
            cpu_burst = np.random.normal(cpu_mean, cpu_std)
            cpu_burst = max(1, int(cpu_burst))
            
            # I/O burst: Uniform distribution
            io_burst = np.random.uniform(*io_range)
            io_burst = int(io_burst)
            
            # Priority: Uniform distribution (1-10, 1 = highest)
            priority = np.random.randint(1, 11)
            
            # Create PCB
            process = PCB(
                process_id=i,
                arrival_time=current_time,
                cpu_burst_time=cpu_burst,
                io_burst_time=io_burst,
                priority=priority
            )
            
            processes.append(process)
        
        return processes
    
    def generate_from_trace(self, trace_file: str) -> List[PCB]:
        """
        Generate workload from trace file
        
        Trace format:
        ProcessID, ArrivalTime, CPUBurst, IOBurst, Priority
        """
        processes = []
        
        try:
            with open(trace_file, 'r') as f:
                for line_num, line in enumerate(f):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        parts = line.split(',')
                        if len(parts) >= 5:
                            pid = int(parts[0])
                            arrival = int(parts[1])
                            cpu_burst = int(parts[2])
                            io_burst = int(parts[3])
                            priority = int(parts[4])
                            
                            process = PCB(
                                process_id=pid,
                                arrival_time=arrival,
                                cpu_burst_time=cpu_burst,
                                io_burst_time=io_burst,
                                priority=priority
                            )
                            processes.append(process)
                    except ValueError as e:
                        print(f"Warning: Invalid line {line_num} in trace file: {line}")
                        continue
            
            print(f"Loaded {len(processes)} processes from trace file")
            
        except FileNotFoundError:
            print(f"Trace file not found: {trace_file}")
            print("Generating synthetic workload instead...")
            processes = self.generate_synthetic(100, "mixed")
        
        return processes
    
    def create_sample_trace_files(self):
        """Create sample trace files for different workload types"""
        
        # CPU-intensive workload
        with open("data/trace_files/cpu_intensive.txt", 'w') as f:
            f.write("# ProcessID, ArrivalTime, CPUBurst, IOBurst, Priority\n")
            current_time = 0
            for i in range(100):
                arrival = current_time + np.random.exponential(50)
                current_time = int(arrival)
                cpu_burst = np.random.normal(80, 15)
                cpu_burst = max(10, int(cpu_burst))
                io_burst = np.random.uniform(5, 30)
                io_burst = int(io_burst)
                priority = np.random.randint(1, 6)
                f.write(f"{i},{arrival},{cpu_burst},{io_burst},{priority}\n")
        
        # I/O-intensive workload
        with open("data/trace_files/io_intensive.txt", 'w') as f:
            f.write("# ProcessID, ArrivalTime, CPUBurst, IOBurst, Priority\n")
            current_time = 0
            for i in range(100):
                arrival = current_time + np.random.exponential(20)
                current_time = int(arrival)
                cpu_burst = np.random.normal(20, 8)
                cpu_burst = max(5, int(cpu_burst))
                io_burst = np.random.uniform(50, 150)
                io_burst = int(io_burst)
                priority = np.random.randint(1, 11)
                f.write(f"{i},{arrival},{cpu_burst},{io_burst},{priority}\n")
        
        # Mixed workload
        with open("data/trace_files/mixed_workload.txt", 'w') as f:
            f.write("# ProcessID, ArrivalTime, CPUBurst, IOBurst, Priority\n")
            current_time = 0
            for i in range(100):
                arrival = current_time + np.random.exponential(30)
                current_time = int(arrival)
                cpu_burst = np.random.normal(50, 20)
                cpu_burst = max(5, int(cpu_burst))
                io_burst = np.random.uniform(10, 100)
                io_burst = int(io_burst)
                priority = np.random.randint(1, 11)
                f.write(f"{i},{arrival},{cpu_burst},{io_burst},{priority}\n")
        
        print("Sample trace files created in data/trace_files/")