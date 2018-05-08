from oncotools.data_integrity.Modules.AnamolyNode import DataNode

'''
The OncospaceAnomalyData module ccolated the data recieved from the modules.
'''

class Anomaly():
    def __init__(self):
        self.current = 0
        self.end = 0
        self.list = []
        #may have to have text version
        
    def insert(self, patient = None, mask = None, errortype = None, ROI = None):
        '''
        Inserts data into Anaomaly data List
        
        Keyword arguments:
            :patient: Patient identification
            :mask: binary mask associated with patient
            :errortype: description of error
            :ROI: region of interest
        '''
        self.list.append(DataNode(patient, mask, errortype, ROI))
        self.end += 1
    
    def remove(self):
        '''
        Deletes current node
        '''
        del self.list[self.current]
        self.end -= 1
    
    def toScreen(self, patient, mask):
        '''
        Prints to screen specific patient and mask
        
        Keyword arguments:
            :patient: Patient identification
            :mask: binary mask associated with patient
        '''
        for i in self.list:
            if self.list[i].patient() == patient:
                if self.list[i].mask() == mask:
                    return i

    def toScreenAll(self):
        '''
        Prints all to screen
        '''
        print(self.list)