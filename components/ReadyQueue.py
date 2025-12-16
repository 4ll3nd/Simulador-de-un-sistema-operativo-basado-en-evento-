class ReadyQueue():
    
    def __init__(self):
        self._queue = []
    

    def next(self):
        return self._queue.pop(0)
    
    def add(self, pcb):
        self._queue.append(pcb)

    def isNotEmpty(self):
        return bool(self._queue)