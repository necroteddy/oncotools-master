from oncotools.data_integrity.Modules.check_contiguity_extent import check_contiguity_extent
from oncotools.data_integrity.Modules.check_contiguity_voxels import check_contiguity_voxels
from oncotools.data_integrity.Modules.check_dose_grid import check_dose_grid
from oncotools.data_integrity.data.data_doses import data_doses
from oncotools.data_integrity.data.data_roi import data_roi
from oncotools.data_integrity.data.data_assessments import data_assessments
import sys

'''
The Manager module contains the classes and methods needed to evaluate data integrity.
'''

# Validator class ==================================================

class Manager(object):
    '''
    The manager class runs the appropriate module.
    '''

    def __init__(self):
        self.dic = ['extent', 'surface', 'volume', 'dose']
        self.dic2 = ['roi', 'dosemask', 'assessments']

    def getModules(self):
        '''
        return list of modules
        '''
        return self.dic

    #def runModule(self, patient, module):
    def runModule(self, input, module):
        '''
        Runs selected modules

        Keyword arguments:
            :module:    Which modules whould be used?
            An array of modules which will be run

            :mask:      The masks that will be analysed
            an array of Roi masks names indicating which masks to look at use
        '''
        for i in module:
            if module == 'extent':
                valid = check_contiguity_extent.check_integrity(input)
            elif module == 'surface':
                valid = check_contiguity_voxels.check_integrity(input, 'surface')
            elif module == 'volume':
                valid = check_contiguity_voxels.check_integrity(input, 'volume')
            elif module == 'dose':
                valid = check_dose_grid.check_integrity(input)
            else:
                sys.stderr.write("Module chosen does not exist.")
            return valid
    
    def get_data_type(self):
        '''
        return list of avalable data type readers
        '''
        return self.dic2
            
    def find_data(dbase, ID, datatype):
        '''
        Run selected predefined data queries
        
        Keywork arguments:
            :dbase:     Database to connect to
            A Database instance from oncotools.connect
            
            :ID:        Patient id
            A patient representation id
            
            :datatype:  The data type to be queried
            input to select the predefined data queries to run, get_data_type() returns a list of avalable ones
        '''
        if datatype == 'roi':
            data = data_roi.get_data(dbase, ID)
        elif datatype == 'dosemask':
            data = data_doses.get_data(dbase, ID)
        elif datatype == 'assessments':
            data = data_assessments.get_data(dbase, ID)
        else:
            sys.stderr.write("Reader for data type chosen does not exist.")
        return data


if __name__ =="__main__":
    t=Manager()
    t.test()
