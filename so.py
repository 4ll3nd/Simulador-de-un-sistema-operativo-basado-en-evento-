#!/usr/bin/env python
from enum import Enum

from loader import Loader
from dispatcher import *
from components.pcb import *
from components.pcbTable import *
from FileSystem import FileSystem
from MemoryManager import MemoryManager
from hardware import *
from FIFOVictimSelector import FIFOVictimSelector


## emulates a compiled program
class Program():

    def __init__(self, name, instructions):
        self._name = name
        self._instructions = self.expand(instructions)

    @property
    def name(self):
        return self._name

    @property
    def instructions(self):
        return self._instructions

    def addInstr(self, instruction):
        self._instructions.append(instruction)

    def expand(self, instructions):
        expanded = []
        for i in instructions:
            if isinstance(i, list):
                ## is a list of instructions
                expanded.extend(i)
            else:
                ## a single instr (a String)
                expanded.append(i)

        ## now test if last instruction is EXIT
        ## if not... add an EXIT as final instruction
        last = expanded[-1]
        if not ASM.isEXIT(last):
            expanded.append(INSTRUCTION_EXIT)

        return expanded

    def __repr__(self):
        return "Program({name}, {instructions})".format(name=self._name, instructions=self._instructions)


## emulates an Input/Output device controller (driver)
class IoDeviceController():

    def __init__(self, device):
        self._device = device
        self._waiting_queue = []
        self._currentPCB = None

    def runOperation(self, pcb, instruction):
        pair = {'pcb': pcb, 'instruction': instruction}
        # append: adds the element at the end of the queue
        self._waiting_queue.append(pair)
        # try to send the instruction to hardware's device (if is idle)
        self.__load_from_waiting_queue_if_apply()

    def getFinishedPCB(self):
        finishedPCB = self._currentPCB
        self._currentPCB = None
        self.__load_from_waiting_queue_if_apply()
        return finishedPCB

    def __load_from_waiting_queue_if_apply(self):
        if (len(self._waiting_queue) > 0) and self._device.is_idle:
            ## pop(): extracts (deletes and return) the first element in queue
            pair = self._waiting_queue.pop(0)
            # print(pair)
            pcb = pair['pcb']
            instruction = pair['instruction']
            self._currentPCB = pcb
            self._device.execute(instruction)

    def __repr__(self):
        return f"IoDeviceController for {self._device.deviceId}, running: {self._currentPCB.path if self._currentPCB else "None"}, waiting: {self._waiting_queue}"


## emulates the  Interruptions Handlers
class AbstractInterruptionHandler():
    def __init__(self, kernel):
        self._kernel = kernel

    @property
    def kernel(self):
        return self._kernel

    def execute(self, irq):
        log.logger.error("-- EXECUTE MUST BE OVERRIDEN in class {classname}".format(classname=self.__class__.__name__))

    # si la readyQueue esta vacia lo delego al dispatcher para q lo ponga a correr
    def runPCBIfCPUIsIdle(self, pcb):
        if self.kernel.pcbTable.runningPCB:
            self.expropiateIfIsNeeded(self.kernel.pcbTable.runningPCB, pcb)
        else:
            self.kernel.dispatcher.load(pcb)
            self.kernel.pcbTable.runningPCB = pcb
            pcb.processState = State.RUNNING

    def expropiateIfIsNeeded(self, pcbInCPU, pcbToAdd):
        if self.kernel.scheduler.mustExpropiate(pcbInCPU, pcbToAdd):
            self.kernel.dispatcher.save(pcbInCPU)
            self.kernel.scheduler.add(pcbInCPU)
            pcbInCPU.processState = State.READY
            self.kernel.dispatcher.load(pcbToAdd)
            pcbToAdd.processState = State.RUNNING
            self.kernel.pcbTable.runningPCB = pcbToAdd
        else:
            self.kernel.scheduler.add(pcbToAdd)
            pcbToAdd.processState = State.READY

    # OTRO PROCESO ENTRA AL CPU
    def searchPCBAndRun(self):
        if not self.kernel.scheduler.isEmpty():
            readyPCB = self.kernel.scheduler.getNext()
            log.logger.info(f"cargando en cpu: {readyPCB.path}")
            self.kernel.dispatcher.load(readyPCB)
            readyPCB.processState = State.RUNNING  # pongo a correr el primer pcb de la readyQueue
            self.kernel.pcbTable.runningPCB = readyPCB  # guardo el primer pcb de la ready queue como el pcbRunnign de la Table


class KillInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        killPCB = self.kernel.pcbTable.runningPCB
        self.kernel.dispatcher.save(killPCB)
        self.kernel.pcbTable.runningPCB = None
        killPCB.processState = State.TERMINATED

        self.kernel.memoryManager.freeFrames(killPCB.pageTable.usedFrames())
        
        log.logger.info("Program {path} Finished ".format(path=killPCB.path))
        log.logger.info("Frames disponibles en memoria: {frames}\n".format(frames=self.kernel.memoryManager._freeFrames))

        self.searchPCBAndRun()


class IoInInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        # SE VA A ENTRADA SALIDA
        operation = irq.parameters
        pcb = self.kernel.pcbTable.runningPCB
        self.kernel.dispatcher.save(pcb)
        self.kernel.pcbTable.runningPCB = None
        pcb.processState = State.WAITING
        self.kernel.ioDeviceController.runOperation(pcb, operation)  # lo añade a la waitingQueue
        log.logger.info(self.kernel.ioDeviceController)

        self.searchPCBAndRun()



class IoOutInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        pcb = self.kernel.ioDeviceController.getFinishedPCB()

        self.runPCBIfCPUIsIdle(pcb)

        log.logger.info(self.kernel.ioDeviceController)


class TimeoutInterruptionHandler(AbstractInterruptionHandler):
    def execute(self,irq=None):
        if self.kernel.scheduler.isEmpty():
            HARDWARE.timer.reset()
        else:
            #mantengo consistente el estado del pcb y la queue del scheduler
            pcbSalienteDeCpu = self.kernel.pcbTable.runningPCB
            self.kernel.dispatcher.save(pcbSalienteDeCpu)
            pcbSalienteDeCpu.processState = State.READY #cambio estado a ready
            self.kernel.scheduler.add(pcbSalienteDeCpu)

            self.searchPCBAndRun()

class NewInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        parameters = irq.parameters
        path = parameters['path']
        priority = parameters['priority']

        # delego al loader para q lo cargue en memoria y me de la direccion fisica
        #aca deberia retornar la pageTable

        # le pido a la pcbTable q me genere un pid unico
        newPID = self.kernel.pcbTable.getNewPID()

        # creo el pcb y lo guardo en la pcbTable
        newPCB = ProcessControlBlock(newPID, path, State.NEW, priority, None)
        self.kernel.loader.crearPageTable(newPCB) 

        self.kernel.pcbTable.add(newPCB)
        
        self.runPCBIfCPUIsIdle(newPCB)

        log.logger.info("Programa {nombre} cargado. \n" \
            "PageTable = {pageTable}\n" \
            "Frames disponibles en memoria: {frames}\n"
        .format(nombre=newPCB.path, pageTable=newPCB.pageTable.dict, frames=self._kernel.memoryManager._freeFrames))
        #imprimo memoria
        log.logger.info(HARDWARE)
        
        


class StatInterruptionHandler(AbstractInterruptionHandler):

        def __init__(self,kernel):
            super().__init__(kernel)
            self._list = []
            self._toBeExecute= True

        def execute(self, irq):
            if (HARDWARE.clock.currentTick == 1):
                self._list.append(["TICKS"])
                self._pids = list(self._kernel.pcbTable.dict.items())
                for i in range(len(self._pids)):
                    self._list.append(["PID " + str(self._pids[i][0])])
            if (HARDWARE.clock.currentTick >= 1):
                self._list[0].append(HARDWARE.clock.currentTick)
                self._list[1].append(self._pids[0][1].processState.state2letter())
                self._list[2].append(self._pids[1][1].processState.state2letter())
                self._list[3].append(self._pids[2][1].processState.state2letter())
            if (self._kernel.pcbTable.allProcessTerminated() and self._toBeExecute):
                gantt = tabulate(self._list)
                with open("gantt.txt", "w") as archivo:
                    archivo.write(gantt)
                self._toBeExecute = False

            if (HARDWARE.clock.currentTick > 0 and HARDWARE.clock.currentTick % 5 == 0):
                self.kernel.scheduler.age()

class PageFaultIntHandler(AbstractInterruptionHandler):

        def execute(self, irq):
            page_number = irq.parameters
            pcbToLoad = self.kernel.pcbTable.runningPCB
            
            #guardo el PID del proceso en el queue del algoritmo de seleccion de busqueda
            self._kernel.memoryVictimSelector.registerEntry(pcbToLoad.pid, page_number)
            
            self.kernel.loader.load(pcbToLoad, page_number)

            #imprimo memoria y frames disponibles
            log.logger.info("Frames disponibles en memoria: {frames}\n".format(frames=self.kernel.memoryManager._freeFrames))
            log.logger.info("Page Table de {runningPcb}: {pageTable}".format(runningPcb = pcbToLoad.path  , pageTable = pcbToLoad.pageTable.dict))
            log.logger.info(HARDWARE)



# emulates the core of an Operative System
class Kernel():
    #añado el scheduler al momento de instanciar el kernel
    def __init__(self, scheduler):
        ## setup interruption handlers
        HARDWARE.mmu.frameSize = 4

        self._fileSystem = FileSystem()

        killHandler = KillInterruptionHandler(self)
        HARDWARE.interruptVector.register(KILL_INTERRUPTION_TYPE, killHandler)

        ioInHandler = IoInInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_IN_INTERRUPTION_TYPE, ioInHandler)

        ioOutHandler = IoOutInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_OUT_INTERRUPTION_TYPE, ioOutHandler)

        newHandler = NewInterruptionHandler(self)
        HARDWARE.interruptVector.register(NEW_INTERRUPTION_TYPE, newHandler)

        statHandler = StatInterruptionHandler(self)
        HARDWARE.interruptVector.register(STAT_INTERRUPTION_TYPE, statHandler)
        HARDWARE.cpu.enable_stats = False

        pageFaultHandler = PageFaultIntHandler(self)
        HARDWARE.interruptVector.register(PAGE_FAULT_INTERRUPTION_TYPE, pageFaultHandler)

        ## controls the Hardware's I/O Device
        self._ioDeviceController = IoDeviceController(HARDWARE.ioDevice)

        timeoutHandler = TimeoutInterruptionHandler(self)

        HARDWARE.interruptVector.register(TIMEOUT_INTERRUPTION_TYPE, timeoutHandler)

        #asigno el scheduler que le llega por parametro como variable de instancia
        self._scheduler = scheduler
        #se añade el kernel, ya que este tiene el FileSystem que tiene que usar el loader
        self._loader = Loader(self)

        self._dispatcher = Dispatcher()

        self._pcbTable = PCBTable()

        self._memoryManager = MemoryManager(self)

        self._memoryVictimSelector = FIFOVictimSelector(self)

    @property
    def memoryManager(self):
        return self._memoryManager

    @property
    def fileSystem(self):
        return self._fileSystem

    @property
    def scheduler(self):
        return self._scheduler

    @property
    def loader(self):
        return self._loader

    @property
    def dispatcher(self):
        return self._dispatcher

    @property
    def pcbTable(self):
        return self._pcbTable

    @property
    def ioDeviceController(self):
        return self._ioDeviceController
    
    @property
    def memoryVictimSelector(self):
        return self._memoryVictimSelector

    ## emulates a "system call" for programs execution
    def run(self, path, priority):
        parameters = {'path': path, 'priority': priority}
        newIrq = IRQ(NEW_INTERRUPTION_TYPE, parameters)
        HARDWARE.interruptVector.handle(newIrq)

    def __repr__(self):
        return "Kernel "


class State(Enum):
    NEW = 'new'
    READY = 'ready'
    RUNNING = 'running'
    WAITING = 'waiting'
    TERMINATED = 'terminated'

    def state2letter(self):
        if self == State.NEW:
            return "N"
        if self == State.READY:
            return "RQ"
        if self == State.RUNNING:
            return "R"
        if self == State.WAITING:
            return "W"
        if self == State.TERMINATED:
            return "T"

    def isTerminated(self):
        return self == State.TERMINATED