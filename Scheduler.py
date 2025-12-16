from abc import abstractmethod

class Scheduler():
    def __init__(self):
        self._readyQueue = []

    def add(self, pcb):
        self._readyQueue.append(pcb)

    @abstractmethod
    def getNext(self):
        pass
    
    @abstractmethod
    def isEmpty(self):
        pass

    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return not pcbInCPU

    #lo tiene que tener el scheduler sino el stathandler no puede usar el metodo
    def age(self):
        pass