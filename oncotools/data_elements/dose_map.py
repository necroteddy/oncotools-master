'''
Module to facilitate dose mapping from dose grid to mask
'''

from copy import deepcopy

import numpy as np
from .image import Image, Mask
from .dose import Dose


def compute_dose_mask(dose=None, roi=None, mask=None):
    '''
    Look up the dose value at each point in the given binary mask.

    Keyword arguments:
        :roi:   roi object containing mask.
        :mask:  mask over which to compute dose.
    Returns:
        Dose mask object with dose mapped onto ROI
    '''
    if dose is None:
        raise ValueError('DVH computation requires a dose grid.')

    mask = roi.mask if roi else mask
    if mask is None:
        raise ValueError('Must provide ROI or mask')

    mask_voxel_indices = np.transpose(mask.data.nonzero())
    if len(mask_voxel_indices[0]) < 1:
        raise ValueError('ROI Binary mask has a volume of 0 cm^3')

    # All remaining indices and point coordinates in [x,y,z]
    mask_voxel_indices_xyz = mask_voxel_indices[:, ::-1]
    mask_voxel_points = mask.transform_index_to_physical_point(
        mask_voxel_indices_xyz)
    dose_voxel_indices, inbounds = dose.transform_physical_point_to_continuous_index(
        mask_voxel_points)

    # How much of the ROI is outside the dose grid?
    fraction_outside_dosegrid = 0.0
    if np.any(~inbounds):
        fraction_outside_dosegrid = 1.0 - float(len(inbounds.nonzero()[0])) / len(inbounds)
        mask_voxel_indices = mask_voxel_indices[inbounds, :]
        mask_voxel_indices_xyz = mask_voxel_indices_xyz[inbounds, :]
        dose_voxel_indices = dose_voxel_indices[inbounds, :]

    mask_slice_indices, i = np.unique(
        mask_voxel_indices_xyz[:, -1], return_index=True)
    if len(mask_slice_indices) < 1:
        raise ValueError('ROI lies entirely outside the dose grid')
    dose_slice_indices = dose_voxel_indices[i, -1]

    # 2. Interpolate dose grid at binary mask slices
    # 2a. Reslice the dose grid into the planes of the binary mask
    dose_resliced = Dose()
    dose_resliced.copy_information(dose)
    dose_resliced.origin[2] = mask.origin[2]
    dose_resliced.size[2] = mask_slice_indices[-1] + 1
    dose_resliced.spacing[2] = mask.spacing[2]
    dose_resliced.fill_buffer(0.0)

    lower_idx = np.floor(dose_voxel_indices.min(0)).astype(np.int_)
    lower_idx = [li if li >= 0 else 0 for li in lower_idx]
    upper_idx = np.ceil(dose_voxel_indices.max(0)).astype(np.int_)
    upper_idx = [
        ui if ui < mask.size[i] else mask.size[i] - 1
        for i, ui in enumerate(upper_idx)
    ]
    ix = np.arange(lower_idx[0], upper_idx[0] + 1)
    iy = np.arange(lower_idx[1], upper_idx[1] + 1)
    iz = dose_slice_indices
    dose_resliced.data[mask_slice_indices, iy[0]:(iy[-1]+1), ix[0]:(ix[-1]+1)] = \
        dose.interpolate_slice(ix, iy, iz)

    # 2b. Bilinear interpolation of voxels from the resliced dose grid
    ix = dose_voxel_indices[:, 0]
    ix0 = np.floor(ix).astype(np.int_)
    ix1 = ix0 + 1
    ix1[ix1 == dose_resliced.data.shape[
        2]] -= 1  # Allow ROI binary mask voxels to fall on the edge of the dose grid
    iy = dose_voxel_indices[:, 1]
    iy0 = np.floor(iy).astype(np.int_)
    iy1 = iy0 + 1
    iy1[iy1 == dose_resliced.data.shape[
        1]] -= 1  # Allow ROI binary mask voxels to fall on the edge of the dose grid
    iz = mask_voxel_indices_xyz[:, 2]

    if np.any(ix0 < 0) or np.any(ix1 >= dose_resliced.data.shape[2]) \
    or np.any(iy0 < 0) or np.any(iy1 >= dose_resliced.data.shape[1]) \
    or np.any(iz < 0) or np.any(iz >= dose_resliced.data.shape[0]):
        try:
            _ = dose_resliced.data[iz, iy0,
                                      ix0] + dose_resliced.data[iz, iy1, ix1]
        except Exception as e:
            raise Exception(
                'The ROI binary mask extends outside the dose grid.\n' +
                str(e))

    # Compute the dose data by interpolation
    dose_data = \
        dose_resliced.data[iz, iy0, ix0] * (ix1 - ix) * (iy1 - iy) + \
        dose_resliced.data[iz, iy0, ix1] * (ix - ix0) * (iy1 - iy) + \
        dose_resliced.data[iz, iy1, ix0] * (ix1 - ix) * (iy - iy0) + \
        dose_resliced.data[iz, iy1, ix1] * (ix - ix0) * (iy - iy0)

    dose_mask = Image()
    dose_mask.copy_information(mask)
    dose_mask.fill_buffer(0.0)
    try:
        mi = mask_voxel_indices
        dose_mask.data[mi[:, 0], mi[:, 1], mi[:, 2]] = dose_data
    except:
        raise Exception('Unable to compute dose mask')

    return dose_mask, fraction_outside_dosegrid


class DoseMask(Mask):
    '''
    The DoseMask class is an extension of the mask class.

    Instead of a binary mask, this class is a mask
    where nonzero values correspond to the administered to that voxel.
    Calculations are performed on construction so self.data reflects
    dose values in the range of the mask.

    Positional arguments:
        :msk:   mask object to map dose onto
        :dsg:   dose grid
    '''

    def __init__(self, msk, dsg, dim=3):
        Mask.__init__(self, dim=3)
        self.mask = deepcopy(msk)
        self.dose = dsg

        # If the dose grid hasn't already been corrected
        if not self.dose.origin_modified:
            # Fix the dose grid origin to account for Pinnacle's LH coordinates
            self.__correct_dg_origin()

        self.data = None
        # Compute the dose mask
        self.compute_dose_mask()
        # Update the information
        self.copy_information(self.mask)
        # self.map_points(self.__dose_data)

        self.compute_dvh()

    def __correct_dg_origin(self):
        # Recompute origin y coordinate
        new_y_o = (
            self.mask.origin[1] + self.mask.size[1] * self.mask.spacing[1]) - (
                self.dose.origin[1] - self.mask.origin[1]) - (
                    self.dose.size[1] * self.dose.spacing[1])
        self.dose.origin[1] = new_y_o
        # Mark the dose grid as modified
        self.dose.origin_modified = True

    def __str__(self):
        outputStr = Image.__str__(self) + '\n' \
            + 'Max Dose:   ' + str(self.max_dose) + '\n' \
            + 'Min Dose:   ' + str(self.min_dose) + '\n' \
            + 'Mean Dose:  ' + str(self.mean_dose) + '\n' \
            + 'Std Dose:   ' + str(self.std_dose) + '\n'
        return outputStr

    def compute_dose_mask(self):
        '''
        Compute a dose mask using the class' roi and dose variables.

        Returns:
            List of dose values corresponding to each nonzero index in the mask
        '''
        dose_mask, self.fraction_outside_dosegrid = \
            compute_dose_mask(dose=self.dose, mask=self.mask)
        self.data = dose_mask.data

        # Compute and store dose statistics
        nonzero_data = self.data[np.nonzero(self.data)]
        self.min_dose = nonzero_data.min()
        self.max_dose = nonzero_data.max()
        self.mean_dose = nonzero_data.mean()
        self.std_dose = nonzero_data.std()

        return self

    def map_points(self, dosePts):
        '''
        Map dose values onto the mask. Changes are reflected in self.data

        Positional arguments:
            :dosePts:   List of dose values corresponding to each nonzero
                            index in the mask
        '''
        # Copy mask data as type float
        self.data = self.mask.data.astype(np.float)

        points = self.data.nonzero()
        numpts = len(points[0])

        for i in range(numpts):
            pt = [points[j][i] for j in range(3)]
            self.data[pt[0]][pt[1]][pt[2]] = dosePts[i]

    def compute_dvh(self, edge_voxel_weight=1.0, bins=200):
        '''
        Compute a DVH curve for the given ROI from the given dose grid.

        Keyword arguments:
            :mask:              mask over which to compute the DVH
            :edge_voxel_weight: weight given to voxels on the surface of the mask
            :bins:              number of bins to use, or an array of bin edges
        Returns:
            List of tuples of the DVH data.
        '''
        from .dvh import compute_dvh as cdvh

        # Steps 1 and 2 shifted to the following function
        if self.data is None:
            self.data = self.compute_dose_mask().data

        (dvh_dose_data, dvh_volume_data), self.fraction_outside_dosegrid = cdvh(
            dose_mask=self,
            edge_voxel_weight=edge_voxel_weight,
            bins=bins)

        self.dvh_data = np.vstack((dvh_dose_data, dvh_volume_data)).T
        return self.dvh_data

    def get_dose_to_volume(self, v):
        '''
        Get the dose delivered to v percent of the volume.

        Keyword arguments:
            :v:     fraction of the volume (from 0 to 1)
        Returns:
            :dose:  dose delivered to specified volume in cGy
        '''
        if self.dvh_data is None:
            self.compute_dvh()

        idx = (np.abs(self.dvh_data[:, 1] - v)).argmin()
        return self.dvh_data[idx, 0]

    def get_volume_with_dose(self, d):
        '''
        Get the dose delivered to v percent of the volume.

        Keyword arguments:
            :d:     dose value
        Returns:
            :v:     fraction of volume receiving specified dose
        '''
        if self.dvh_data is None:
            self.compute_dvh()

        if d <= self.max_dose:
            idx = (np.abs(self.dvh_data[:, 0] - d)).argmin()
            return self.dvh_data[idx, 1]
        else:
            return 0.0
