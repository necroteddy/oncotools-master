import numpy as np

class Integrity_Module(object):
    def __init__(self):
        self.name = "Integrity_Check"
        self.function = "Basic Integrity Check Class. \n\t:mask:  mask object"
        self.description = {self.name: self.function}

    def check_integrity(self, data):
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
        valid = False

        # Basic error message construction (if necessary)
        errortype = None
        if not valid: # Error
            errortype = "Error: " + self.name  + " Class"

        # Basic return message construction
        message = 'Return: Valid'
        if not valid: # Error
            message = 'Return: Error, ' + description + ' Mask Invalid'

        # Return generated (valid, message, errortype)
        return valid #(valid, message, errortype)
