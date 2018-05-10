from abc import ABC
import numpy as np

class Integrity_Check(ABC):
    def __init__(self):
        self.name = "Integrity_Check"
        self.function = "Basic Integrity Check Class. \n\t:mask:  mask object"
        self.description = {self.name: self.function}

    def name(self):
        return self.name

    def function(self):
        return self.function

    def description(self):
        return self.description

    @abstractmethod
    def check_valid(self, mask):
        pass

    @abstractmethod
    def generate_message(self, mask):
        pass

    def generate_error(self, valid):
        if valid: # No error
            return None
        else: # Error
            return "Error: " + self.name  + " Class"


    def check_integrity(self, patient):
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
        valid = check_valid(self, mask)

        # Basic error message construction (if necessary)
        error = generate_error(self, mask, valid)

        # Basic return message construction
        if valid:
            # No error
            message = 'Return: Valid'
        else:
            # Description of error
            message = 'Return: Error, ' + 'Mask Invalid'

        # Return generated (valid, message, errortype)
        return (valid, message, errortype)
