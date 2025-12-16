from hardware import HARDWARE

class MemoryManager():

    def __init__(self, kernel):
        self._freeFrames = []
        self._kernel = kernel
        freeMem = HARDWARE.memory.size
        frameSize = HARDWARE.mmu.frameSize
        frames = freeMem // frameSize
        for frame in range(frames):
            self._freeFrames.append(frame)

    def allocFrame(self):
        if bool(self._freeFrames):
            return self._freeFrames.pop(0)
        else:
            return self._kernel.memoryVictimSelector.selectVictim()
            
        
    def freeFrames(self, frames):
        self._freeFrames.extend(frames)

    def addFreeFrame(self, frame):
        self._freeFrames.append(frame)
