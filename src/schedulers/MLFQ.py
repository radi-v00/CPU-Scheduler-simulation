"""
Multilevel Feedback Queue Scheduler (Bonus)
"""

from . import Scheduler
from typing import List, Deque
from collections import deque
from ..simulator import PCB

class MLFQ(Scheduler):
    """Multilevel Feedback Queue scheduler with multiple priority levels"""
    
    def __init__(self, num_queues=3):
        self.num_queues = num_queues
        self.queues = [deque() for _ in range(num_queues)]
        
        # Time quanta for each queue (decreases with priority)
        self.time_quanta = [100, 50, 25]  # ms
        
        # Boost interval to prevent starvation
        self.boost_interval = 500  # ms
        self.last_boost_time = 0
    
    def select_next(self, ready_queue: List[PCB], current_time: int) -> PCB:
        """Select process from highest priority non-empty queue"""
        # Add processes from ready_queue to appropriate MLFQ queue
        for process in ready_queue[:]:
            if process.queue_level >= self.num_queues:
                process.queue_level = self.num_queues - 1
            
            if process not in self.queues[process.queue_level]:
                self.queues[process.queue_level].append(process)
                ready_queue.remove(process)
        
        # Apply priority boost periodically
        if current_time - self.last_boost_time >= self.boost_interval:
            self._boost_priority(current_time)
            self.last_boost_time = current_time
        
        # Find highest priority non-empty queue
        for i in range(self.num_queues):
            if self.queues[i]:
                process = self.queues[i].popleft()
                process.queue_level = i
                process.time_in_queue = 0
                return process
        
        return None
    
    def _boost_priority(self, current_time: int):
        """Boost priority of all processes to prevent starvation"""
        for queue in self.queues[1:]:  # Skip highest priority queue
            for process in queue:
                process.queue_level = max(0, process.queue_level - 1)
                process.time_in_queue = 0