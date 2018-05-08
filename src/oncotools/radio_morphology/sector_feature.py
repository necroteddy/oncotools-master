'''
The Sector Feature (SectorFeature) class is an extension of the Feature abstract class.

This feature calculates the center of mass of each slice along the z axis
and computes sectors based on angles calculated radially.
'''

from copy import deepcopy

import numpy as np

from oncotools import transform as tf
from oncotools.data_elements.dose_map import DoseMask
from oncotools.radio_morphology.feature import Feature

class SectorFeature(Feature):
    '''
    The Sector Feature (SectorFeature) class is an extension of the Feature abstract class.

    This feature calculates the center of mass of each slice along the z axis
    and computes sectors based on angles calculated radially.

    Keyword arguments:
        :angles:    angles that bound each sector
        :dvh:       list of dvh volumes to look up

    `angles` argument must be expressed in degrees. It can be provided as either:
        - a list of bounds
        - an N x 2 array, where each row is a set of bounds for a sector
    '''

    def __init__(self, featureID, feature_type=None,
                 mask=None, dose=None, angles=[0, 360], dvh=[]):
        super(SectorFeature, self).__init__(
            featureID, feature_type if feature_type else 'SectorFeature',
            mask, dose
        )
        self.angles = self.__compute_sector_bounds(angles)
        self.dvh_vals = dvh

    def __compute_sector_bounds(self, angles):
        # Make sure the angles are properly formatted
        angles = np.asarray(angles)
        # If a 1D array is given, turn it into an Nx2 array
        if angles.ndim == 1:
            temp_angles = [[a, angles[i+1]] for i, a in enumerate(angles) if i < len(angles)-1]
            angles = np.asarray(temp_angles)
        # If it isnt Nx2, something is wrong
        if angles.ndim != 2 or angles.shape[1] != 2:
            raise ValueError('Malformed angles array.')

        # If any values are greater than 180, subtract 360
        for x in np.nditer(angles, op_flags=['readwrite']):
            while x > 180:
                x[...] -= 360
            while x < -180:
                x[...] += 360

        sector_rads = np.multiply(angles, np.pi / 180)
        return sector_rads

    def process_mask(self):
        # Convert to polar coordinates
        pd, coms = tf.general.convert_to_polar(self.mask)

        # Compute sectors between angle pairs
        polar_sectors = []
        for bounds in self.angles:
            if bounds[0] < bounds[1]:
                polar_sectors.append([polar_slice[np.all(
                    [
                        polar_slice[:, 1] >= bounds[0], polar_slice[:, 1] <
                        bounds[1]
                    ],
                    axis=0)] for polar_slice in pd])
            elif bounds[0] >= bounds[1]:
                polar_sectors.append([polar_slice[np.any(
                    [
                        polar_slice[:, 1] >= bounds[0], polar_slice[:, 1] <
                        bounds[1]
                    ],
                    axis=0)] for polar_slice in pd])

        # Convert back to euclidian coordinates
        euclid_sectors = [
            tf.general.convert_to_euclidean(ps, coms) for ps in polar_sectors
        ]
        # Create masks for each sector
        sector_masks = [
            tf.general.fill_mask(self.mask, sect) for sect in euclid_sectors
        ]
        # Clean sectors of any weird points (because sectors < original mask)
        sectors = []
        for sec in sector_masks:
            clean_sector = deepcopy(sec)
            clean_sector.data = np.logical_and(clean_sector.data, self.mask.data)
            sectors.append(clean_sector)

        self.feature_mask = sectors
        return self.feature_mask

    def process_dose(self):
        if self.feature_mask is None:
            self.process_mask()
        # Map the dose masks onto each sector
        self.feature_dosemask = [
            DoseMask(m, self.dose) for m in self.feature_mask
        ]
        return self.feature_dosemask

    def process(self):
        '''
        Process the feature and calculate the average dose and dvh values in each half.
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
            'bounds': self.angles,
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
