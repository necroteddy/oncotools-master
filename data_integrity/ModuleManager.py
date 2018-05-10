'''
The OncospaceValidator module contains the classes and methods needed to evaluate data integrity.
'''

from oncotools.data_integrity.Modules.MaskValidator import MaskValidator

# Validator class ==================================================

class Validator(object):
    '''
    The ValidatorManager class aggregates the functions in the Validation module.
    '''

    def __init__(self):
        self.mask = MaskValidator()
        self.dic = {}
        self.dic.update(self.mask.modules())
        #make this dynamic later
        
    def modules(self):
        '''
        return dictionary of modules
        '''
        return self.dic
        
    def runModule(self, module, mask):
        '''
        Runs selected modules
        
        Keyword arguments:
            :module:    Which modules whould be used?
            An array of modules which will be run
            
            :mask:      The masks that will be analysed
            an array of Roi masks names indicating which masks to look at use
        '''
        for i in module:
            if module == self.mask.check_contiguity_extent.name():
                valid = self.mask.check_contiguity(mask, 'extent')
            elif module == self.mask.check_contiguity_voxels.name():
                valid = self.mask.check_contiguity(mask, 'surface')
            elif module == self.mask.check_contiguity_voxels.name2():
                valid = self.mask.check_contiguity(mask, 'volume')
            return valid
        
if __name__ =="__main__":
    t=Validator()
    t.testFunc()