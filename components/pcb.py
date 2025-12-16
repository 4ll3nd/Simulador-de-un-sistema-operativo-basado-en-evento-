class ProcessControlBlock():
    
    def __init__(self, pid, path, state, priority, pageTable):
        self._pid = pid
        self._processState = state
        self._path = path
        self._programCounter = 0
        self._priority = priority
        self._pageTable = pageTable

    @property
    def pageTable(self):
        return self._pageTable

    @property
    def pid(self):
        return self._pid

    @property
    def processState(self):
        return self._processState
    
    @property
    def programCounter(self):
        return self._programCounter
    
    @property
    def path(self):
        return self._path

    @pageTable.setter
    def pageTable(self, pageTable):
        self._pageTable = pageTable

    @processState.setter
    def processState(self, newProcessState):
        self._processState = newProcessState

    @programCounter.setter
    def programCounter(self, newProgramCounter):
        self._programCounter = newProgramCounter

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, newPriority):
        self._priority = newPriority

    def isTerminated(self):
        return self._processState.isTerminated()

    #def __repr__(self):
    #    return f"PCB: ({self.pid}), baseDir:{self.baseDir}"