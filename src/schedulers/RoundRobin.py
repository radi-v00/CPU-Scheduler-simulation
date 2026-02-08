"""
Round Robin Scheduler
"""

from . import Scheduler
from typing import List
from ..simulator import PCB

class RoundRobin(Scheduler):
    """Round Robin scheduler with configurable time quantum"""
    
    def __init__(self, time_quantum=20):
        self.time_quantum = time_quantum
    
    def select_next(self, ready_queue: List[PCB], current_time: int) -> PCB:
        """Select next process in round-robin fashion"""
        if not ready_queue:
            return None
        
        # Simple round-robin: always take first in queue
        # In practice, this would maintain a circular queue
        return ready_queue[0]