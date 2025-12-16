from Scheduler import Scheduler

class FirstComeFirstServed(Scheduler):

    def getNext(self):
        return self._readyQueue.pop(0)

    def isEmpty(self):
        return not bool(self._readyQueue)

    def age(self):
        return None