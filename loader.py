import math
import log

from hardware import HARDWARE
from FileSystem import (FileSystem)

class PageTable:
    def __init__(self):
        self._dict = {}

    @property
    def dict(self):
        return self._dict

    def numberOfPages(self):
        return len(self._dict)

    def addMapping(self, pageNumber, frameNumber):
        #asocia la página lógica y un frame físico.
        self._dict[pageNumber] = frameNumber
    
    def setFrame(self, pageNumber, frame):
        self._dict[pageNumber] = frame
    
    def getFrame(self, pageNumber):
        return self._dict[pageNumber]
    
    def usedFrames(self):
        memoryFrames = []
        for page in range(len(self._dict)):
            if not self._dict[page] is None:   
                memoryFrames.append(self._dict[page])
        return memoryFrames

class Loader():

    def __init__(self, kernel):
        self._nextFisicalDir = 0
        self._kernel = kernel

    def load(self, pcb, pageNumber): 
        #actualizo la pageTable 
        freeFrame = self.freeFrameToLoad() 
        pcb.pageTable.addMapping(pageNumber, freeFrame)
        
        #busco la pagina a cargar
        instructions = self._kernel.fileSystem.read(pcb.path).instructions
        pageToLoad = self.searchPage(instructions, HARDWARE.mmu.frameSize, pageNumber)

        self.cargarPagina(freeFrame, pageToLoad,pageNumber)

    
        

    def crearPageTable(self,pcb):
        instructions = self._kernel.fileSystem.read(pcb.path).instructions
        instructionsSize = len(instructions)
        pageTable = PageTable()

        if instructionsSize % HARDWARE.mmu.frameSize > 0:
            numberOfPages =  (instructionsSize // HARDWARE.mmu.frameSize) + 1
        else:
            numberOfPages = instructionsSize // HARDWARE.mmu.frameSize
        
        for page in range(numberOfPages):
            pageTable.addMapping(page, None)

        pcb.pageTable = pageTable
                



    def cargarPagina(self, frame, pageToLoad, pageNumber):        
        frame_basedir = frame * HARDWARE.mmu.frameSize

        HARDWARE.mmu.setPageFrame(pageNumber, frame)

        for despl in range(len(pageToLoad)):
            HARDWARE.memory.write(frame_basedir + despl, pageToLoad[despl])

        

        

    #solicita al Memory Manager los frames necesarios para cargar el programa
    def freeFrameToLoad(self):
        return self._kernel.memoryManager.allocFrame()

    def searchPage(self, instructions, frameSize, pageNumber):
        page = instructions[(pageNumber*frameSize) : ((pageNumber*frameSize) + frameSize)]
        
        #para la fragmentacion interna, seteo los espacios sobrantes en None
        missingCells = frameSize - len(page)

        if missingCells > 0:
            page.extend([None] * missingCells)
        
        return page
