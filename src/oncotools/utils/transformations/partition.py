'''
This module contains methods for the transformations module.
'''

from copy import deepcopy
from oncotools.data_elements.image import Mask
import numpy as np

class PartitionTransform(object):
    '''
    Partitioning transformations
    '''

    def octants_around_point(self, msk, pt):
        '''
        Create octants around a point in the dose grid.
        Specify a point to be the center of the octants.

        Positional arguments:
            :msk:   binary mask to contract to create octants
            :pt:    center of octants to cut around, specified as XYZ indices
        Returns:
            List of mask objects representing each octant.

        Note:
            Octants are defined as follows:

            \+ indicates the the octant include the positive direction of the corresponding axis.

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
        '''
        octantMasks = []

        pt = np.asarray(np.round(pt), dtype=int)
        for i in range(8):
            aMask = deepcopy(msk)
            if i != 0:
                aMask.data[pt[2]:, pt[1]:, pt[0]:] = 0
            if i != 1:
                aMask.data[pt[2]:, pt[1]:, 0:pt[0]] = 0
            if i != 2:
                aMask.data[pt[2]:, 0:pt[1], 0:pt[0]] = 0
            if i != 3:
                aMask.data[pt[2]:, 0:pt[1], pt[0]:] = 0
            if i != 4:
                aMask.data[0:pt[2], pt[1]:, pt[0]:] = 0
            if i != 5:
                aMask.data[0:pt[2], pt[1]:, 0:pt[0]] = 0
            if i != 6:
                aMask.data[0:pt[2], 0:pt[1], 0:pt[0]] = 0
            if i != 7:
                aMask.data[0:pt[2], 0:pt[1], pt[0]:] = 0
            octantMasks.append(aMask)

        return octantMasks


    def halves(self, msk, pt):
        '''
        Cut into superior and inferior halves along the z-axis.

        Positional arguments:
            :msk:   mask object to be cut
            :pt:    point (x,y,z) around which to cut the mask
        Returns:
            List of mask objects representing inferior and superior halves
        '''
        halfMasks = []

        pt = np.asarray(np.round(pt), dtype=int)
        for i in range(2):
            aMask = deepcopy(msk)
            if i == 0:
                aMask.data[0:pt[2], :, :] = 0
            if i == 1:
                aMask.data[pt[2]:, :, :] = 0
            halfMasks.append(aMask)

        return halfMasks


    def slices(self, msk, numSlices, axis):
        '''
        Cut a mask into slices of equal thickness along a specified axis.

        Positional arguments:
            :msk:       mask object to be cut
            :numSlices: number of slices to be created
            :axis:      axis along which to be cut ("x", "y", or "z")
        Returns:
            List of mask objects representing each slice
        '''
        if axis.lower() == "x":
            ax = 0
        elif axis.lower() == "y":
            ax = 1
        elif axis.lower() == "z":
            ax = 2
        else:
            raise ValueError("Axis must be either x, y, or z.")

        bounds = msk.bounds
        sliceBounds = []

        # Compute spacing and produce a list of slice bounds
        spacing = (bounds[1][ax] - bounds[0][ax]) / numSlices
        b = bounds[0][ax]
        sliceBounds.append(b)
        for i in range(numSlices - 1):
            b += spacing
            sliceBounds.append(b)
        sliceBounds.append(-1)

        sliceMasks = []

        for i in range(numSlices):
            # New mask object that will be modified
            slMask = deepcopy(msk)

            # Data that will be used to compute slice mask data
            dataA = deepcopy(msk.data)

            if ax == 0:
                dataA[:, :, sliceBounds[i]:sliceBounds[i + 1]] = 0
            elif ax == 1:
                dataA[:, sliceBounds[i]:sliceBounds[i + 1], :] = 0
            elif ax == 2:
                dataA[sliceBounds[i]:sliceBounds[i + 1], :, :] = 0

            slMask.data = np.logical_xor(msk.data, dataA)
            sliceMasks.append(slMask)

        return sliceMasks
