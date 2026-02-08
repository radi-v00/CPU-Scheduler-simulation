"""
First-Come, First-Served Scheduler
"""

from . import Scheduler
from typing import List
from ..simulator import PCB

class FCFS(Scheduler):
    """Non-preemptive First-Come, First-Served scheduler"""
    
    def select_next(self, ready_queue: List[PCB], current_time: int) -> PCB:
        """Select process with earliest arrival time"""
        if not ready_queue:
            return None
        
        # Sort by arrival time
        ready_queue.sort(key=lambda p: p.arrival_time)
        return ready_queue[0]