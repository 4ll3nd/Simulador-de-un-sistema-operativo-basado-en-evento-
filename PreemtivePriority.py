from  Priority import *

class PreemtivePriority(Priority):
    
    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return pcbInCPU.priority > pcbToAdd.priority