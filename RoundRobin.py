from Scheduler import Scheduler
from hardware import HARDWARE
class RoundRobin(Scheduler):

    def __init__(self, cpuBurst):
        super().__init__()
        self._cpuBurst = cpuBurst
        HARDWARE.timer.quantum = cpuBurst

    def add(self, pcb):
        self._readyQueue.append(pcb)

    def getNext(self):
        if not self.isEmpty():
            return self._readyQueue.pop(0)

    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return False
    
    def isEmpty(self):
        return not self._readyQueue

    def age(self):
        return None