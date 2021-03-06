'''
The Slice Feature (SliceFeature) class is an extension of the Feature abstract class.

This feature uses the bounds of the mask to create a specified number of slices along a given axis.
'''
import numpy as np

from .. import transform as tf
from ..data_elements.dose_map import DoseMask
from ..radio_morphology.feature import Feature

class SliceFeature(Feature):
    '''
    The Slice Feature (SliceFeature) class is an extension of the Feature abstract class.

    This feature uses the bounds of the mask
    to create a specified number of slices along a given axis.

    Keyword arguments:
        :num_slices:    number of slices to create, default=2
        :axis:          axis along which to be cut ('x', 'y', or 'z'), default='z'
        :dvh:           list of dvh volumes to look up
    '''

    def __init__(self, featureID, feature_type=None,
                 mask=None, dose=None, num_slices=2, axis='z', dvh=[]):
        super(SliceFeature, self).__init__(
            featureID, feature_type if feature_type else 'SliceFeature',
            mask, dose
        )
        self.dvh_vals = dvh
        self.num_slices = num_slices
        self.axis = axis

    def process_mask(self):
        '''
        Create slices of equal thickness along the specified axis
        '''
        self.feature_mask = tf.partition.slices(self.mask, self.num_slices, self.axis)
        return self.feature_mask

    def process_dose(self):
        '''
        Map dose onto each derived substructure
        '''
        if self.feature_mask is None:
            self.process_mask()
        # Map the dose masks onto each sector
        self.feature_dosemask = [
            DoseMask(m, self.dose) for m in self.feature_mask]
        return self.feature_dosemask

    def process(self):
        '''
        Process the feature and calculate the average dose in each shell.

        Returns: Dictionary with the following keys:
            :mean:      list of mean dose per shape
            :max:       list of max dose per shape
            :min:       list of min dose per shape
            :dvh:       list of doses, list of volume with each dose

        Raises:
            :ValueError:    if data is not loaded
        '''
        if not self.loaded:
            raise ValueError('Load data before processing')

        self.process_mask()
        self.process_dose()

        '''
        Output is:
        {
            'mean' : mean dose per slice,
            'max' : maximum dose per slice,
            'min' : minimum dose per slice,
            'dvh' : dvh data array per slice
        }
        '''
        self.output = {
            'mean': [dm.mean_dose for dm in self.feature_dosemask],
            'min': [dm.min_dose for dm in self.feature_dosemask],
            'max': [dm.max_dose for dm in self.feature_dosemask]
        }

        # If there are specified dvh parameters, look thmm up
        if len(self.dvh_vals) > 0:
            # If there are specified dvh parameters, look them up
            self.output['dvh'] = [np.asarray([[
                dm.get_dose_to_volume(v) for v in self.dvh_vals
            ], self.dvh_vals]).T for dm in self.feature_dosemask]
        else:
            # Otherwise, just return the entire DVH
            self.output['dvh'] = [dm.dvh_data for dm in self.feature_dosemask]

        return self.output
