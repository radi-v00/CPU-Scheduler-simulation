"""
Priority Scheduler (Preemptive and Non-preemptive)
"""

from . import Scheduler
from typing import List
from ..simulator import PCB

class PriorityScheduler(Scheduler):
    """Priority scheduler (preemptive and non-preemptive). Lower priority number = higher priority."""

    def __init__(self, preemptive=False):
        self.preemptive = preemptive

    def select_next(self, ready_queue: List[PCB], current_time: int) -> PCB:
        """Select process with highest priority (lowest priority number)"""
        if not ready_queue:
            return None

        return min(ready_queue, key=lambda p: p.priority)
