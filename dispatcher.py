from hardware import HARDWARE


class Dispatcher():

    def load(self, pcb):
        HARDWARE.cpu.pc = pcb.programCounter

         ## al hacer un context switch
        HARDWARE.mmu.resetTLB()
        pages = pcb.pageTable.numberOfPages()
        for page in range(pages):
            HARDWARE.mmu.setPageFrame(page, pcb.pageTable.getFrame(page))    
        

    def save(self, pcb):
        pcb.programCounter = HARDWARE.cpu.pc #guardo el ultimo pc del pcb que se estaba corriendo
        HARDWARE.cpu.pc = -1 #el cpu queda idle
        HARDWARE.timer.reset()

