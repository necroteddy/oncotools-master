class DataNode:
    def __init__(self, patient = None, mask = None, errortype = None, ROI = None):
        self.patient = patient
        self.mask = mask
        self.errortype = errortype
        self.ROI = ROI
    
    def patient(self):
        return self.patient
    
    def mask(self):
        return self.mask
    
    def ROI(self): 
        return self.ROI
    
    def toScreen(self):
        print("patient: ", self.patient)
        print("mask: ", self.mask)
        print("errortype: ", self.errortype)
        print("ROI: ", self.errortype)
        