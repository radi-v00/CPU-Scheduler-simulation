# CPU Scheduler Simulation Project
### 📋 Project Overview
A comprehensive discrete-event simulation framework for evaluating and comparing CPU scheduling algorithms under various workload conditions.

### 🎯 Objectives
- Design and implement a simulation framework for CPU scheduling algorithms
- Evaluate and compare algorithm performance using standard metrics
- Analyze sensitivity to different parameters and workload characteristics
- Provide comprehensive visualization of results

### 📚 Learning Outcomes
- Understand internal workings of CPU scheduling algorithms
- Develop skills in discrete-event simulation
- Analyze and interpret performance metrics
- Compare algorithm effectiveness under different scenarios
- Practice scientific methodology in computer systems evaluation

## 🏗️ Project Structure

cpu-scheduler-simulation/
├── src/ # Source code
│ ├── main.py # Main entry point
│ ├── simulator.py # Discrete-event simulation engine
│ ├── schedulers/ # Scheduling algorithms
│ ├── process_generator.py # Workload generation
│ ├── statistics.py # Performance metrics calculation
│ ├── visualization.py # Visualization generation
│ └── experiments.py # Experimental design
├── data/ # Data files
│ ├── trace_files/ # Sample trace files
│ └── results/ # Output results
├── docs/ # Documentation
├── tests/ # Unit tests
├── requirements.txt # Python dependencies
├── config.yaml # Configuration
├── run_experiments.py # Experiment runner
└── README.md # This file


## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cpu-scheduler-simulation.git
cd cpu-scheduler-simulation
```

2. Install dependencies
```bash 
pip install -r requirements.txt
```
3. Create sample data:
``` bash 
python -c "from src.process_generator import ProcessGenerator; pg = ProcessGenerator(); pg.create_sample_trace_files()"
```
Basic Usage
1. Run a single simulation:
```bash
python src/main.py --algorithm fcfs --processes 500 --visualize
```
2. run all expriment:
```bash
python run_experiments.py
```
3. Run specific experiment: 
```bash
python run_experiments.py --experiment baseline --visualize
```

## 📊 Implemented Scheduling Algorithms

    First-Come, First-Served (FCFS) - Non-preemptive

    Shortest Job First (SJF) - Both preemptive (SRTF) and non-preemptive versions

    Round Robin (RR) - Configurable time quantum

    Priority Scheduling - Both preemptive and non-preemptive with aging

    Multilevel Feedback Queue (MLFQ) - Bonus feature

## 🔬 Experimental Design
### 1. Baseline Comparison

    Compare all algorithms with identical workload (500 processes, mixed characteristics)

    Collect and compare all performance metrics

### 2. Sensitivity Analysis

    Vary time quantum for RR (5, 10, 20, 50, 100ms)

    Vary number of processes (100, 500, 1000)

### 3. Workload-Specific Performance

    Test with CPU-intensive workload

    Test with I/O-intensive workload

    Test with mixed workload

### 4. Scalability Test

    Measure performance with increasing system load

    Plot metrics vs. number of processes

## 📈 Performance Metrics
### Per-Process Metrics

    Turnaround Time: Tturnaround=Tcompletion−TarrivalTturnaround​=Tcompletion​−Tarrival​

    Waiting Time: Twaiting=Tturnaround−TburstTwaiting​=Tturnaround​−Tburst​

    Response Time: Tresponse=Tfirst_run−TarrivalTresponse​=Tfirst_run​−Tarrival​

### System-Wide Metrics

    Average Turnaround Time

    Average Waiting Time

    Average Response Time

    CPU Utilization: UCPU=∑CPU_burst_timeTotal_simulation_time×100%UCPU​=Total_simulation_time∑CPU_burst_time​×100%

    Throughput: Number of processes completed per unit time

    Fairness Index (Jain's Fairness): F=(∑i=1nxi)2n×∑i=1nxi2F=n×∑i=1n​xi2​(∑i=1n​xi​)2​


## 📊 Visualization Outputs
per unit time

    Fairness Index (Jain's Fairness): F=(∑i=1nxi)2n×∑i=1nxi2F=n×∑i=1n​xi2​(∑i=1n​xi​)2​


## 📊 Visualization Outputs

The system generates the following visualizations:

    Gantt charts for each algorithm (first 20 processes)

    Bar charts comparing average metrics across algorithms

    Line graphs showing metric trends with varying parameters

    Box plots showing distribution of waiting times