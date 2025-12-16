class PCBTable():

    def __init__(self):
        self._dict = {}
        self._pid = 0
        self._runningPCB = None
    
    def getNewPID(self):
        pid = self._pid
        self._pid += 1 
        return pid   

    def add(self, pcb):
        self._dict[pcb.pid] = pcb
    
    def get(self, pid):
        return self._dict.get(pid)

    @property
    def dict(self):
        return self._dict

    def remove(self, pid):
        self._dict.pop(pid)

    @property
    def runningPCB(self):
        return self._runningPCB

    @runningPCB.setter
    def runningPCB(self, runningPCB):
        self._runningPCB = runningPCB

    def allProcessTerminated(self):
        return all(pcb.isTerminated() for pcb in list(self._dict.values()))