'''
The Center of Mass Feature (ComFeature) class is an extension of the Feature abstract class.

This feature first calculates the center of mass of the mask
by averaging the coordinates of every point in the mask.
With the center of mass as the orgin, the feature will calculate octants along the x,y,z axes
and will split the mask into 8 separate masks, each representing an octant.
'''
import numpy as np

from oncotools import transform as tf
from oncotools.data_elements.dose_map import DoseMask
from oncotools.radio_morphology.feature import Feature

class ComFeature(Feature):
    '''
    The Center of Mass Feature (ComFeature) class is an extension of the Feature abstract class.

    This feature first calculates the center of mass of the mask
    by averaging the coordinates of every point in the mask.
    With the center of mass as the orgin, the feature will calculate octants along the x,y,z axes
    and will split the mask into 8 separate masks, each representing an octant.
    A DoseMap for each smaller mask will be calculated.

    Each value in the values correspond to a single octant;
    for quick reference the octant positions are defined as follows:

    Note:
        Octants are defined as follows:

        (plus) indicates the the octant include the positive direction of the corresponding axis.

        +--------+-----------+
        | Index  | Axis      |
        +========+===========+
        |  i     | (x,y,z)   |
        +--------+-----------+
        |  0     | (+,+,+)   |
        +--------+-----------+
        |  1     | (-,+,+)   |
        +--------+-----------+
        |  2     | (-,-,+)   |
        +--------+-----------+
        |  3     | (+,-,+)   |
        +--------+-----------+
        |  4     | (+,+,-)   |
        +--------+-----------+
        |  5     | (-,+,-)   |
        +--------+-----------+
        |  6     | (-,-,-)   |
        +--------+-----------+
        |  7     | (+,-,-)   |
        +--------+-----------+

    Keyword arguments:
        :dvh:       list of dvh volumes to look up
    '''

    def __init__(self, featureID, feature_type=None,
                 mask=None, dose=None, dvh=[]):
        super(ComFeature, self).__init__(
            featureID, feature_type if feature_type else 'ComFeature',
            mask, dose
        )
        self.dvh_vals = dvh

    def process_mask(self):
        '''
        Partition the mask into octants
        '''
        self.feature_mask = tf.partition.octants_around_point(self.mask, self.mask.center_of_mass)
        return self.feature_mask

    def process_dose(self):
        '''
        Map dose onto each octant
        '''
        if self.feature_mask is None:
            self.process_mask()
        self.feature_dosemask = [
            DoseMask(octant, self.dose) for octant in self.feature_mask]
        return self.feature_dosemask

    def process(self):
        '''
        Process the mask and dose

        Returns: Dictionary with the following keys:
            :mean:      list of mean dose per octant
            :max:       list of max dose per octant
            :min:       list of min dose per octant
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
            'mean' : mean dose per octant,
            'max' : maximum dose per octant,
            'min' : minimum dose per octant,
            'dvh' : dvh data array per octant
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
