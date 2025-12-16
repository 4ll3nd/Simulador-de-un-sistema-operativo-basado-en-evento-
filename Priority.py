from PriorityQueue import PriorityQueue
from Scheduler import Scheduler

class Priority(Scheduler):

    def __init__(self):
        super().__init__()
        self._priorityQueue = PriorityQueue()

    def add(self, pcb):
        self._priorityQueue.add(pcb)

    def getNext(self):
        return self._priorityQueue.getNext()

    def age(self):
        self._priorityQueue.age()

    def isEmpty(self):
        return not self._priorityQueue.isNotEmpty()