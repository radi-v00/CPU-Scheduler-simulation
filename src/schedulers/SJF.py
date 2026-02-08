"""
Shortest Job First Scheduler (SJF and SRTF)
"""

from . import Scheduler
from typing import List
from ..simulator import PCB

class SJF(Scheduler):
    """Shortest Job First scheduler (preemptive and non-preemptive)"""
    
    def __init__(self, preemptive=False):
        self.preemptive = preemptive
    
    def select_next(self, ready_queue: List[PCB], current_time: int) -> PCB:
        """Select process with shortest remaining time"""
        if not ready_queue:
            return None
        
        if self.preemptive:
            # SRTF: Consider remaining time
            return min(ready_queue, key=lambda p: p.remaining_time)
        else:
            # Non-preemptive SJF: Consider total CPU burst
            return min(ready_queue, key=lambda p: p.cpu_burst_time)