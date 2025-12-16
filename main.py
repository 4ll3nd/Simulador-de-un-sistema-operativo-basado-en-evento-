from FirstComeFirstServed import FirstComeFirstServed
from PreemtivePriority import PreemtivePriority
from Priority import Priority
from RoundRobin import RoundRobin
from so import *
import log
from hardware import HARDWARE

##
##  MAIN 
##
if __name__ == '__main__':
    log.setupLogger()
    log.logger.info('Starting emulator')

    ## setup our hardware and set memory size to 24 "cells" and 6 "frames"
    HARDWARE.setup(40)

    ## Switch on computer
    HARDWARE.switchOn()

    ## new create the Operative System Kernel
    # "booteamos" el sistema operativo
    kernel = Kernel(FirstComeFirstServed())

    # Ahora vamos a intentar ejecutar 3 programas a la vez
    ##################
    prg1 = Program("prg1.exe", [ASM.CPU(2), ASM.IO(), ASM.CPU(3), ASM.IO(), ASM.CPU(2)])
    prg2 = Program("prg2.exe", [ASM.CPU(7)])
    prg3 = Program("prg3.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(1)])

    kernel.fileSystem.write("c:/prg1.exe", prg1)
    kernel.fileSystem.write("c:/prg2.exe", prg2)
    kernel.fileSystem.write("c:/prg3.exe", prg3)

    # ejecutamos los programas a partir de un "path" (con una prioridad x)
    kernel.run("c:/prg1.exe", 0)
    kernel.run("c:/prg2.exe", 2)
    kernel.run("c:/prg3.exe", 1)
