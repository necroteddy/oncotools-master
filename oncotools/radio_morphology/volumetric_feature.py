'''
The VolumetricFeature class is an extension of the Feature abstract class.

This class uses a list of expansions and contractions
to create a set of concentric shells.
Values are calculated as the average dose between in each shell
and specified DVH values.
'''
import numpy as np

from .. import transform as tf
from ..data_elements.dose_map import DoseMask
from ..radio_morphology.feature import Feature

class VolumetricFeature(Feature):
    '''
    The VolumetricFeature class is an extension of the Feature abstract class.

    This class uses a list of expansions and contractions
    to create a set of concentric shells.
    Values are calculated as the average dose between in each shell
    and specified DVH values.

    Keyword arguments:
        :contract:  list of contractions to be performed on the mask
        :expand:    list of expansions to be performed on the mask
        :dvh:       list of dvh volumes to look up

    Note: Contraction and Expansion values may be given as:
        - A single number:       uniform expansion in all dimensions
        - A list of 1 number:    uniform expansion in all dimensions
        - A list of 3 numbers:   expansion in x, y, and z, respectively
        - A list of 6 numbers:   expansion in -x, +x, -y, +y, -z, and +z, respectively

    Values:
        The values field of a VolumetricFeature is a tuple of lists where...
            - the first element is a list of expansion and contraction factors,
            ordered to define the outer bounds of each shell
            - the second element is a list of average dose in each shell

        Note:
            Given `n` total expansions and contractions, there will be `n+1` average dose values.
    '''

    def __init__(self, featureID, feature_type=None,
                 mask=None, dose=None, contract=[], expand=[], dvh=[]):
        super(VolumetricFeature, self).__init__(
            featureID, feature_type if feature_type else 'VolumetricFeature',
            mask, dose
        )
        self.dvh_vals = dvh
        self.contractions = contract
        self.expansions = expand

    def process_mask(self):
        '''
        Create shells by expanding and contracting the mask
        '''
        # Create shells using given contractions and expansions
        self.bounds, self.feature_mask = tf.scale.shells(
            self.mask, contractions=self.contractions, expansions=self.expansions)
        return self.feature_mask

    def process_dose(self):
        '''
        Map dose onto each derived substructure
        '''
        if self.feature_mask is None:
            self.process_mask()
        self.feature_dosemask = [
            DoseMask(m, self.dose) for m in self.feature_mask]
        return self.feature_dosemask

    def process(self):
        '''
        Process the feature and calculate the average dose in each shell.

        Returns: Dictionary with the following keys:
            :bounds:    identifying name for each sub-section
            :mean:      list of mean dose per shape
            :max:       list of max dose per shape
            :min:       list of min dose per shape
            :dvh:       list of doses, list of volume with each dose        Raises:

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
            'bounds': identifying name for each sub-section
            'mean' : mean dose per slice,
            'max' : maximum dose per slice,
            'min' : minimum dose per slice,
            'dvh' : dvh data array per slice
        }
        '''
        self.output = {
            'bounds': self.bounds,
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
