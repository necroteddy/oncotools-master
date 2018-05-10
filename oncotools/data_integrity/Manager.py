from oncotools.data_integrity.Modules.Masks.check_contiguity_extent import check_contiguity_extent
from oncotools.data_integrity.Modules.Masks.check_contiguity_voxels import check_contiguity_voxels

'''
The OncospaceValidator module contains the classes and methods needed to evaluate data integrity.
'''

# Validator class ==================================================

class Manager(object):
    '''
    The manager class runs the appropriate module.
    '''

    def __init__(self):
        self.dic = ['extent', 'surface', 'volume']
        #make this dynamic later

    def getModules(self):
        '''
        return dictionary of modules
        '''
        return self.dic

    #def runModule(self, patient, module):
    def runModule(self, mask, module):
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
                #valid = check_contiguity_extent.check_integrity(patient)
                valid = check_contiguity_extent.check_integrity(mask)
            elif module == 'surface':
                #valid = check_contiguity_voxels.check_contiguity(patient, 'surface')
                valid = check_contiguity_voxels.check_contiguity(mask, 'surface')
            elif module == 'volume':
                #valid = check_contiguity_voxels.check_contiguity(patient, 'volume')
                valid = check_contiguity_voxels.check_contiguity(mask, 'volume')
            return valid

if __name__ =="__main__":
    t=Manager()
    t.test()
