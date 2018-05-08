from oncotools.data_integrity.Modules.Masks.check_contiguity_extent import check_contiguity_extent
from oncotools.data_integrity.Modules.Masks.check_contiguity_voxels import check_contiguity_voxels

class MaskValidator(object):
    '''
    The MaskValidator class contains validation functions for mask shapes.
    '''
    def __init__(self):
        self.check_contiguity_extent = check_contiguity_extent()
        self.check_contiguity_voxels = check_contiguity_voxels()
    
    def check_contiguity(self, mask, method='extent'):
        '''
        Check the contiguity of a mask.

        Keyword arguments:
            :method:    (default='extent') Which method should be used?
            Options are 'extent', 'volume' or 'surface'

        Algorithms:
            :extent:    fastest method, but possible to produce false negatives
            :surface:   efficient, but may rarely produce false negatives if surfaces are jagged
            :volume:    very slow, but will always be accurate
        '''
        algos = {
            'extent': lambda m: self.check_contiguity_extent(m),
            'volume': lambda m: self.check_contiguity_voxels(m, surface=False),
            'surface': lambda m: self.check_contiguity_voxels(m, surface=True)
        }
        if method not in algos:
            raise KeyError('{} is not a valid method'.format(method))
        return algos[method](mask)
    
    def modules():
        dic = {}
        dic.update(check_contiguity_extent.description())
        dic.update(check_contiguity_voxels.description())
        return dic
    

    

    
