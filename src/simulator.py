"""
Discrete-Event Simulation Engine
"""

import heapq
from enum import Enum
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

class ProcessState(Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"

@dataclass
class PCB:
    """Process Control Block"""
    process_id: int
    arrival_time: int
    cpu_burst_time: int
    io_burst_time: int = 0
    priority: int = 1
    
    # Dynamic state
    state: ProcessState = ProcessState.READY
    current_cpu_burst: int = field(init=False)
    current_io_burst: int = field(init=False)
    remaining_time: int = field(init=False)
    
    # Statistics
    waiting_time: int = 0
    turnaround_time: int = 0
    response_time: int = 0
    completion_time: int = 0
    first_run_time: Optional[int] = None
    cpu_time_used: int = 0
    
    # For MLFQ
    queue_level: int = 0
    time_in_queue: int = 0
    last_cpu_time: int = 0
    
    def __post_init__(self):
        self.current_cpu_burst = self.cpu_burst_time
        self.current_io_burst = self.io_burst_time
        self.remaining_time = self.cpu_burst_time
    
    def update_statistics(self, current_time: int):
        """Update process statistics"""
        if self.state == ProcessState.TERMINATED:
            self.turnaround_time = self.completion_time - self.arrival_time
            self.waiting_time = self.turnaround_time - self.cpu_time_used
    
    def __lt__(self, other):
        # For priority queue ordering
        return self.process_id < other.process_id

@dataclass
class Event:
    """Simulation Event"""
    time: int
    event_type: str  # 'arrival', 'completion', 'io_completion', 'timeout'
    process: PCB
    priority: int = 0  # For heap ordering
    
    def __lt__(self, other):
        # Primary key: time, secondary key: priority
        if self.time == other.time:
            return self.priority < other.priority
        return self.time < other.time

class SimulationEngine:
    """Discrete-event simulation engine"""
    
    def __init__(self, scheduler, context_switch_time=2):
        self.clock = 0
        self.event_queue = []  # Min-heap for events
        self.ready_queue = []
        self.running = None
        self.waiting_queue = []
        self.completed = []
        self.scheduler = scheduler
        self.context_switch_time = context_switch_time
        self.total_time = 0
        self.idle_time = 0
        self.scheduling_history = []  # For Gantt chart
        
        # Statistics
        self.context_switches = 0
    
    def schedule_event(self, event: Event):
        """Add event to priority queue"""
        heapq.heappush(self.event_queue, event)
    
    def run(self, processes: List[PCB]) -> List[PCB]:
        """Main simulation loop"""
        # Initialize with arrival events
        for process in processes:
            arrival_event = Event(
                time=process.arrival_time,
                event_type='arrival',
                process=process
            )
            self.schedule_event(arrival_event)
        
        # Main simulation loop
        while self.event_queue or self.ready_queue or self.running or self.waiting_queue:
            # Advance clock to next event
            if self.event_queue:
                next_event_time = self.event_queue[0].time
                if self.running:
                    # Process might complete before next event
                    remaining_burst = min(
                        self.running.remaining_time,
                        next_event_time - self.clock
                    )
                    # Round Robin: cap by time quantum
                    if type(self.scheduler).__name__ == 'RoundRobin':
                        time_used_this_slice = self.clock - self.running.last_cpu_time
                        quantum_left = self.scheduler.time_quantum - time_used_this_slice
                        remaining_burst = min(remaining_burst, max(0, quantum_left))
                    self.clock += remaining_burst
                    self.running.remaining_time -= remaining_burst
                    self.running.cpu_time_used += remaining_burst
                    
                    # Record scheduling history
                    self.scheduling_history.append({
                        'process_id': self.running.process_id,
                        'start': self.clock - remaining_burst,
                        'end': self.clock,
                        'state': 'RUNNING'
                    })
                    
                    # Check if process completed CPU burst
                    if self.running.remaining_time == 0:
                        self._handle_completion()
                    elif type(self.scheduler).__name__ == 'RoundRobin':
                        # Check for time quantum expiration
                        time_used = self.clock - self.running.last_cpu_time
                        if time_used >= self.scheduler.time_quantum:
                            self._handle_timeout()
                else:
                    # CPU is idle
                    idle_time = next_event_time - self.clock
                    self.clock = next_event_time
                    self.idle_time += idle_time
            else:
                # No more events, finish current process
                if self.running:
                    self.clock += self.running.remaining_time
                    self.running.cpu_time_used += self.running.remaining_time
                    self.running.remaining_time = 0
                    self._handle_completion()
                break
            
            # Process all events at current time
            while self.event_queue and self.event_queue[0].time <= self.clock:
                event = heapq.heappop(self.event_queue)
                self._handle_event(event)
            
            # Schedule next process if CPU is idle
            if not self.running and self.ready_queue:
                self._schedule_next_process()
        
        # Finalize statistics
        self.total_time = self.clock
        for process in self.completed:
            process.update_statistics(self.clock)
        
        return self.completed
    
    def _handle_event(self, event: Event):
        """Process different event types"""
        if event.event_type == 'arrival':
            self._handle_arrival(event.process)
        elif event.event_type == 'io_completion':
            self._handle_io_completion(event.process)
        elif event.event_type == 'timeout':
            self._handle_timeout()
    
    def _handle_arrival(self, process: PCB):
        """Handle process arrival"""
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        
        # If no process is running, schedule next
        if not self.running:
            self._schedule_next_process()
    
    def _handle_completion(self):
        """Handle process completion of CPU burst"""
        if not self.running:
            return
        
        process = self.running
        
        if process.current_io_burst > 0:
            # Process goes to I/O
            process.state = ProcessState.WAITING
            io_completion_time = self.clock + process.current_io_burst
            
            io_event = Event(
                time=io_completion_time,
                event_type='io_completion',
                process=process
            )
            self.schedule_event(io_event)
            self.waiting_queue.append(process)
        else:
            # Process terminates
            process.state = ProcessState.TERMINATED
            process.completion_time = self.clock
            self.completed.append(process)
        
        self.running = None
        self.context_switches += 1
        
        # Schedule next process
        self._schedule_next_process()
    
    def _handle_io_completion(self, process: PCB):
        """Handle I/O completion - process has finished its single I/O burst and terminates"""
        if process in self.waiting_queue:
            self.waiting_queue.remove(process)
            process.state = ProcessState.TERMINATED
            process.completion_time = self.clock
            self.completed.append(process)
            
            if not self.running:
                self._schedule_next_process()
    
    def _handle_timeout(self):
        """Handle time quantum expiration for RR"""
        if not self.running:
            return
        
        process = self.running
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        self.running = None
        self.context_switches += 1
        
        self._schedule_next_process()
    
    def _schedule_next_process(self):
        """Select and run next process using scheduler"""
        if not self.ready_queue:
            return
        
        # Apply context switch overhead
        if self.running is None and self.clock > 0:
            self.clock += self.context_switch_time
        
        # Use scheduler to select next process
        next_process = self.scheduler.select_next(self.ready_queue, self.clock)
        
        if next_process:
            self.ready_queue.remove(next_process)
            next_process.state = ProcessState.RUNNING
            self.running = next_process
            
            # Record response time (first time process runs)
            if next_process.first_run_time is None:
                next_process.first_run_time = self.clock
                next_process.response_time = self.clock - next_process.arrival_time
            
            # Update last CPU time for RR
            next_process.last_cpu_time = self.clock