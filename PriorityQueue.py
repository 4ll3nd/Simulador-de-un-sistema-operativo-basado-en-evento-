import log
class PriorityQueue():

    def __init__(self):
        self._queue = [[], [], [], [], []]

    def add(self, pcb):
        priority = pcb.priority
        self._queue[priority].append(pcb)

    def getNext(self):
        if bool(self._queue[0]):
            return self._queue[0].pop(0)
        if bool(self._queue[1]):
            return self._queue[1].pop(0)
        if bool(self._queue[2]):
            return self._queue[2].pop(0)
        if bool(self._queue[3]):
            return self._queue[3].pop(0)
        if bool(self._queue[4]):
            return self._queue[4].pop(0)

    def age(self):
        self._queue[0].extend(self._queue[1])
        self._queue[1].clear()
        self._queue[1].extend(self._queue[2])
        self._queue[2].clear()
        self._queue[2].extend(self._queue[3])
        self._queue[3].clear()
        self._queue[3].extend(self._queue[4])
        self._queue[4].clear()
        log.logger.info("SE ENVEJECIO LA PRIORITY QUEUE")

    def isNotEmpty(self):
        return bool(self._queue[0]) or bool(self._queue[1]) or bool(self._queue[2]) or bool(self._queue[3]) or bool(self._queue[4])