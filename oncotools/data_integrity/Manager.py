from oncotools.data_integrity.Modules.check_contiguity_extent import check_contiguity_extent
from oncotools.data_integrity.Modules.check_contiguity_voxels import check_contiguity_voxels
from oncotools.data_integrity.Modules.check_dose_grid import check_dose_grid
from oncotools.data_integrity.data.doses import doses_reader
from oncotools.data_integrity.data.roi import roi_reader
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

    def getModules(self):
        '''
        return dictionary of modules
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

    def find_data(ID, datatype):
        if datatype == 'roi':
            data = roi_reader(ID, datatype)
        elif datatype == 'dosemask':
            data = doses_reader(ID, datatype)
        else:
            sys.stderr.write("Reader for data type chosen does not exist.")
        return data


if __name__ =="__main__":
    t=Manager()
    t.test()
