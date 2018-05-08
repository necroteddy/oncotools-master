'''
This module contains methods for the transformations module.
'''

from copy import deepcopy
import numpy as np

class GeneralTransform(object):
    '''
    General transformations
    '''

    def combine_masks(self, masks, weights=None):
        '''
        Combine multiple masks into one.

        Positional arguments:
            :masks:     list of mask objects to combine
        Returns:
            Mask object that is the combination of all masks given.
        Raises:
            :ValueError:    if only one mask is given
            :ValueError:    if mask specifications (dimension, origin, etc.) do not match
        '''
        # Masks must be iterable
        try:
            len(masks)
        except:
            raise ValueError('Must provide iterable list of masks.')

        # If there is only one mask given, there's nothing to do
        if len(masks) < 2:
            raise ValueError('Only one mask. Nothing to combine.')

        # Check that all specifications match
        specs = {}
        specs['dimension'] = set([m.dimension for m in masks])
        specs['origin'] = set([str(m.origin) for m in masks])
        specs['end'] = set([str(m.end) for m in masks])
        specs['index'] = set([str(m.index) for m in masks])
        specs['size'] = set([str(m.size) for m in masks])
        specs['spacing'] = set([str(m.spacing) for m in masks])
        specs['direction'] = set([str(m.direction) for m in masks])
        for k in specs.keys():
            if len(specs[k]) != 1:
                raise ValueError('Too many different values for field, {}: {}'.
                                 format(k, list(specs[k])))

        # If weights for each mask are specified
        if weights:
            if len(weights) != len(masks):
                raise ValueError('{} masks can not be mapped to {} weights'.format(
                    len(masks), len(weights)))
            # Combine the masks
            comb_mask = deepcopy(masks[0])
            comb_mask.data *= weights[0]
            for i, m in enumerate(masks[1:]):
                comb_mask.data += m.data * weights[i]
        # Otherwise, just add the given masks
        else:
            # Combine the masks
            comb_mask = deepcopy(masks[0])
            for m in masks[1:]:
                comb_mask.data += m.data

        return comb_mask


    def downsample(self, msk, fracs):
        '''
        Reduce the number of points by uniformly sampling along each axis.

        Positional arguments:
            :msk:   mask to be downsampled
            :fracs: fraction of each axis to be left.
        Returns:
            resampled mask

        Note:
            fracs can be given as either:
                1 value to scale all axes by the same amount
                list of 3 values to scale (x,y,z) axes respectively

            TODO: Does not support interpolation,
            so it is best that fracs can be expressed as 1/x where x is a whole number
        '''
        # Get fracs in the form of a list with 3 values
        fracs = np.multiply(np.ones(3), fracs)

        # Check that all fracs are < 1
        if not all(b <= 1 for b in fracs):
            raise ValueError("Fraction parameter(s) must be <= 1.")

        # Make a new mask
        new_msk = deepcopy(msk)
        # print "Downsampling {} points".format(len(msk.data.nonzero()[0]))
        # Number of indices to skip in (x,y,z) directions
        skips = [int(1 / i) for i in fracs]
        # New data
        new_msk.data = msk.data[::skips[2], ::skips[1], ::skips[0]]
        new_msk.set_spacing(tuple(np.multiply(msk.spacing, skips)))
        new_msk.set_size(new_msk.data.shape[::-1])
        # print "Reduced to {} points".format(len(new_msk.data.nonzero()[0]))
        return new_msk


    def crop(self, msk):
        '''
        Crop a mask to the bounds of the nonzero values.

        Positional arguments:
            :msk:   mask to crop
        Returns:
            cropped mask
        '''
        new_mask = deepcopy(msk)
        bnds = new_mask.bounds
        new_mask.data = new_mask.data[bnds[0][2]:bnds[1][2], bnds[0][1]:bnds[1][1],
                                      bnds[0][0]:bnds[1][0]]
        new_mask.set_origin(new_mask.origin + bnds[0] * new_mask.spacing)
        new_mask.set_size(new_mask.data.shape[::-1])
        new_mask.update_end()

        return new_mask


    def convert_to_polar(self, mask):
        '''
        For axial slices (along z), convert to (r, theta).

        Returns:
            :polar_data:  data array of points in r, theta
            :coms:        center of mass offset (x,y)
        '''
        coms = []
        polar_data = []
        for z, slc in enumerate(mask.data):
            nonz = slc.nonzero()
            # Only look at slices with data
            if len(nonz[0]) > 0:
                # Shift all points to be centered at (0,0)
                com = np.mean(nonz, axis=1)
                centered_points = np.transpose(nonz) - com
                # Convert to polar coordinates
                r = np.sqrt(centered_points[:, 0]**2 + centered_points[:, 1]**2)
                theta = np.arctan2(centered_points[:, 0],
                                   centered_points[:, 1])  # theta = arctan(y/x)
                polar_slice = np.transpose(np.asarray([r, theta]))
                # Add to a list
                coms.append(((com[1], com[0]), z))
                polar_data.append(polar_slice)
        # Return polar slices and COM offsets
        return np.asarray(polar_data), coms


    def convert_to_euclidean(self, polar_data, coms):
        '''
        For a set of polar coordinates, with offset from center of mass,
        convert back to an Euclidian (x,y,z) point cloud.
        '''
        euc_data = np.asarray([[
            row[0] * np.cos(row[1]) + coms[i][0][0],
            row[0] * np.sin(row[1]) + coms[i][0][1], coms[i][1]
        ] for i, polar_slice in enumerate(polar_data) for row in polar_slice])
        return np.asarray(euc_data, dtype=int)


    def fill_mask(self, inmask, points):
        '''
        Construct a new mask using a list of points corresponding to voxels in the mask.

        Positional arguments:
            :inmask:    base mask
            :points:    list of (x,y,z) indices that correspond to voxels in the mask
        '''
        mask = deepcopy(inmask)
        mask.data = np.zeros(mask.data.shape)
        for pt in points:
            mask.data[pt[2], pt[1], pt[0]] = 1
        return mask
