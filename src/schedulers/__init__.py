"""
Scheduling Algorithms Base Classes
"""

from abc import ABC, abstractmethod
from typing import List
from ..simulator import PCB

class Scheduler(ABC):
    """Abstract base class for all schedulers"""
    
    @abstractmethod
    def select_next(self, ready_queue: List[PCB], current_time: int) -> PCB:
        """Select next process to run"""
        pass
    
    def __str__(self):
        return self.__class__.__name__

from .FCFS import FCFS
from .SJF import SJF
from .RoundRobin import RoundRobin
from .Priority import PriorityScheduler
from .MLFQ import MLFQ

__all__ = ['Scheduler', 'FCFS', 'SJF', 'RoundRobin', 'PriorityScheduler', 'MLFQ']