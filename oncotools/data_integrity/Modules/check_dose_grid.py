import numpy as np
from oncotools.data_integrity.Modules.Integrity_Module import Integrity_Module

class check_dose_grid(Integrity_Module):
    def __init__(self):
        Integrity_Module.__init__
        self.name = "check_dose_grid"
        self.function = "Check Dose Grid Data. \n\t:dose grid: dose object"
        self.description = {self.name: self.function}

    def check_integrity(self, dosegrid):
        '''
        Basic Integrity Check function. Subclass should modify this function.

        Generalized structure:

        Input:
            :mask:  mask object

        Output:
            :valid:  whether mask is valid
            :message:   valid/error message
            :errortype:  error message
        '''
        # Basic Validity (Integrity) Check
        max = dosegrid.max
        valid = False
        if max > 0:
            valid = True

        # Basic error message construction (if necessary)
        errortype = None
        if not valid: # Error
            errortype = "Error: " + self.name  + " Class"

        # Basic return message construction
        message = 'Return: Valid'
        description = "Dose Grid"
        if not valid: # Error
            message = 'Return: Error, ' + description + ' Invalid'

        return (valid, message, errortype)
