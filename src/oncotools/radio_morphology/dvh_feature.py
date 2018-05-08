'''
The DVH Feature (DVHFeature) class is an extension of the Feature abstract class.

This feature computes dose statistics for a mask without any shape transfrmations.
'''
from copy import deepcopy
import numpy as np

from oncotools.data_elements.dose_map import DoseMask
from oncotools.radio_morphology.feature import Feature


class DVHFeature(Feature):
    '''
    The DVH Feature (DVHFeature) class is an extension of the Feature abstract class.

    This feature computes dose statistics for a mask without any shape transfrmations.

    Keyword arguments:
        :dvh:       list of dvh volumes to look up
    '''

    def __init__(self, featureID, feature_type=None,
                 mask=None, dose=None, dvh=[]):
        super(DVHFeature, self).__init__(
            featureID, feature_type if feature_type else 'DVHFeature',
            mask, dose
        )
        self.dvh_vals = dvh

    def process_mask(self):
        '''
        No shape transformations for this feature. Just returns the mask
        '''
        self.feature_mask = deepcopy(self.mask)
        return self.feature_mask

    def process_dose(self):
        '''
        Map dose onto the mask
        '''
        if self.feature_mask is None:
            self.process_mask()
        self.feature_dosemask = DoseMask(self.feature_mask, self.dose)
        return self.feature_dosemask

    def process(self):
        '''
        Process the mask and dose

        Returns: Dictionary with the following keys:
            :mean:      mean dose
            :max:       max dose
            :min:       min dose
            :dvh:       list of doses, list of volumes with each dose

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
            'mean' : mean dose,
            'max' : maximum dose,
            'min' : minimum dose,
            'dvh' : dvh data array
        }
        '''
        self.output = {
            'mean': self.feature_dosemask.mean_dose,
            'min': self.feature_dosemask.min_dose,
            'max': self.feature_dosemask.max_dose
        }

        if len(self.dvh_vals) > 0:
            # If there are specified dvh parameters, look them up
            self.output['dvh'] = np.asarray([[
                self.feature_dosemask.get_dose_to_volume(v) for v in self.dvh_vals
            ], self.dvh_vals]).T
        else:
            # Otherwise, just return the entire DVH
            self.output['dvh'] = self.feature_dosemask.dvh_data

        return self.output
