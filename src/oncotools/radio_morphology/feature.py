'''
Features are consistently identifiable characteristics of images or masks.
'''

from copy import deepcopy

class Feature(object):
    '''
    The Feature class is an abstract representation of an RM feature.
    Many types of RM features can be defined as extensions of this base class.

    Each subclass can take different arguments and perform different processing steps.

    Positional arguments:
        :featureID:         feature identifier
    Properties:
        :id:                patient identifier
        :type:              identifier for the type of feature calculation
        :loaded:            flag for whether or not necessary values have been loaded
    Loaded properties:
        :mask:      binary mask that is loaded
        :dose:      dose grid that is loaded
    Calculated properties:
        :feature_mask:      mask after shape transformation
        :feature_dosemask:  dose_masks making up the feature
        :values:            the values associated with the feature
    '''
    def __init__(self, featureID, feature_type=None, mask=None, dose=None):
        self.id = featureID
        self.type = feature_type
        self.output = None

        self.dose = None
        self.mask = None
        self.feature_mask = None
        self.feature_dosemask = None
        # Try and load from keyword arguments
        if mask is not None:
            self.mask = mask
        if dose is not None:
            self.dose = dose
        self.loaded = self.mask is not None and self.dose is not None

    @property
    def values(self):
        '''
        Get the values.

        Each type of feature class has a different type of output.
        See each class's documentation for further details.
        '''
        if self.output is None:
            self.process()
        return self.output

    def load(self, mask, dose):
        '''
        Load the feature with a mask and a dose grid.

        Positional arguments:
            :mask:   mask to be processed
            :dose:   dose grid
        '''
        self.mask = deepcopy(mask)
        self.dose = deepcopy(dose)
        self.loaded = True

    def process_mask(self):
        '''
        Process the data: perform the shape transformations.

        The process_mask() method is different for each type of feature.
        '''
        raise NotImplementedError("Feature processing not implemented")

    def process_dose(self):
        '''
        Process the data: compute the feature values.

        The process() method is different for each type of feature.
        '''
        raise NotImplementedError("Feature processing not implemented")

    def process(self):
        '''
        Process the feature.
        '''
        if not self.loaded:
            raise ValueError("Load data before processing")

        self.process_mask()
        self.process_dose()

        return self.output
