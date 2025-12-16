import log

class FIFOVictimSelector():
    
    def __init__(self, kernel):
        self._kernel = kernel
        self._pagesQueue = []

    def selectVictim(self):
        while True:
            #elijo la primer pagina de la queue
            posibleVictim =  self._pagesQueue[0]
            victimPcb = self._kernel.pcbTable.get(posibleVictim['pid'])
            
            #si pertenece a un proceso terminado la descarto y sigo buscando
            if victimPcb.isTerminated(): 
                self._pagesQueue.pop(0)
                continue
            
            #a la pagina validada le pido el frame y le marco su frame en None
            victim = self._pagesQueue.pop(0)
            victimPcb = self._kernel.pcbTable.get(victim['pid'])
            newFreeFrame = victimPcb.pageTable.getFrame(victim['page'])
            victimPcb.pageTable.setFrame(victim['page'], None)   
            
            #imprimo info de seleccion
            log.logger.info("\nLiberando frame {frame} con algoritmo de seleccion".format(frame = newFreeFrame))
            log.logger.info("Page Table de {victim}: {pageTable}".format(victim = victimPcb.path  , pageTable = victimPcb.pageTable.dict))
            
            return newFreeFrame
    
    def registerEntry(self, pcbPID, pageNumber):
        self._pagesQueue.append({'pid': pcbPID, 'page': pageNumber})