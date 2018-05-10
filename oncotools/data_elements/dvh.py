'''
Module to facilitate DVH calculation and manipulation of Dose Volume Histograms

TODO: rescale DVH with fraction outside dose grid
'''

from copy import deepcopy
import numpy as np
import warnings

# Define how to cumulate / differentiate dose and volume
def cumulate_dose(d):
    for i in range(1, len(d)):
        d[i] += d[i - 1]
    return d


def differentiate_dose(d):
    return np.hstack(([d[0]], np.diff(d)))


def cumulate_volume(v):
    i = len(v) - 2
    while i >= 0:
        v[i] += v[i + 1]
        i -= 1
    return v


def differentiate_volume(v):
    return np.hstack((v[:-1] - v[1:], [v[-1]]))


def compute_dvh(dose_mask=None, mask=None, dose=None,
                edge_voxel_weight=None, bins=200,
                type='cum'):
    '''
    Compute a DVH curve for the given ROI from the given dose grid. Returns
    the DVH data. If no binary mask is specified, one will be computed for
    the dvh.roi. The value of each voxel contained within the mask is used
    to weight the dose data in the final histogram. Input parameter "bins"
    may be specified as an integer number of bins to include in the histogram,
    or it may be a vector of bin edges (see np.histogram).

    If an edge_voxel_weight is specified, all edge voxels in the x-y plane of
    the binary mask are multipled by the specified weight.
    '''
    from .dose_map import compute_dose_mask as cdm

    # Must have dose and mask, or dose_mask
    fraction_outside_dosegrid = None
    if dose_mask is None:
        if dose is None:
            raise ValueError('DVH computation requires a dose grid to compute DVH data')
        if mask is None:
            raise ValueError('DVH computation requires either an ROI or a binary mask')
        dose_mask, fraction_outside_dosegrid = cdm(dose=dose, mask=mask)
    elif hasattr(dose_mask, 'fraction_outside_dosegrid'):
        fraction_outside_dosegrid = dose_mask.fraction_outside_dosegrid

    # Compute histogram
    voxelVolume = abs(
        dose_mask.spacing[0] * dose_mask.spacing[1] * dose_mask.spacing[2])
    try:
        # modifiedBins = bins - 1
        useModifiedBins = True
    except ValueError:
        useModifiedBins = False

    # Compute the weight associated with each dose point
    mask_voxel_indices = dose_mask.data.nonzero()
    dose_weights = np.ones_like(
        dose_mask.data[mask_voxel_indices], dtype=np.float_)
    if (edge_voxel_weight is not None) and (edge_voxel_weight != 1):
        edge_mask = mask.get_mask_edge_voxels(exclude_z=True)
        dose_weights[edge_mask.data[mask_voxel_indices] > 0] *= edge_voxel_weight

    if useModifiedBins:
        # Last dose bin has a volume of 0
        hist, edges = np.histogram(
            dose_mask.data[mask_voxel_indices],
            bins=bins - 1,
            density=False,
            weights=dose_weights)
        hist = np.append(hist, 0)
    else:
        # Last dose bin may not have a volume of 0
        hist, edges = np.histogram(
            dose_mask.data[mask_voxel_indices],
            bins=bins,
            density=False,
            weights=dose_weights)
        edges = edges[:-1]

    dose_data = np.array(edges)
    dvh_volume_data = np.array(hist) * voxelVolume

    # If requesting a cumulative dvh, accumulate the volumes
    if 'cum' in type:
        i = len(dvh_volume_data) - 2
        while i >= 0:
            dvh_volume_data[i] += dvh_volume_data[i + 1]
            i -= 1
        dvh_volume_data[:] = [v / dvh_volume_data[0] for v in dvh_volume_data]

    return (dose_data, dvh_volume_data), fraction_outside_dosegrid


class Dvh(object):
    '''
    Dose Volume Histogram representation.

    Initialize the DVH class with either the data
    or both a structure and dose class.

    Keyword arguments:
        :data:  points defining a dose volume histogram
        :roi:   Roi class
        :mask:  Mask class
        :dose:  Dose class
    '''

    def __init__(self, data=None, roi=None, mask=None, dose=None):
        # DVH data: Nx2 numpy array [[dose,volume]] tuples
        self.data = data
        # An ROI class
        self.roi = deepcopy(roi)
        # Get a mask either from the ROI class or mask argument
        if mask is not None:
            self.mask = deepcopy(mask)
        elif self.roi is not None:
            self.mask = self.roi.mask
        # A dose class
        self.dose = deepcopy(dose)

        # If data wasn't provided, must have a dose and mask
        if self.data is None:
            if self.dose is None:
                raise ValueError('DVH computation requires a dose grid to compute DVH data')
            if self.mask is None:
                raise ValueError('DVH computation requires either an ROI or a binary mask')


        self.dose_type = None       # 'cum', 'diff'
        self.dose_units = None      # 'cGy', 'Gy', 'normalized'
        self.volume_type = None     # 'cum', 'diff'
        self.volume_units = None    # 'cm3', 'normalized'

        self.volume = None
        if self.mask is not None:
            self.volume = self.mask.get_volume()
        elif self.roi is not None:
            self.volume = self.roi.get_volume()

        # DVH values
        self.dose_data = []
        self.volume_data = []
        if data is not None:
            self.set_data(data)

        # These are updated by self.compute_dvh
        self.dose_mask = None
        self.min_dose = None
        self.max_dose = None
        self.mean_dose = None
        self.std_dose = None
        self.fraction_outside_dosegrid = None

        # Compute the DVH
        self.compute_dvh()

    def __str__(self):
        outputStr = 'Dose type:     ' + str(self.dose_type) + '\n' \
                  + 'Dose units:    ' + str(self.dose_units) + '\n' \
                  + 'Volume type:   ' + str(self.volume_type) + '\n' \
                  + 'Volume units:  ' + str(self.volume_units) + '\n' \
                  + 'Num Points:    ' + str(len(self.dose_data)) + '\n' \
                  + 'Min Dose:      ' + str(self.min_dose) + '\n' \
                  + 'Max Dose:      ' + str(self.max_dose) + '\n' \
                  + 'Mean Dose:     ' + str(self.mean_dose) + '\n' \
                  + 'Std Dose:      ' + str(self.std_dose) + '\n' \
                  + 'Fraction Outside Dose Grid: ' + str(self.fraction_outside_dosegrid)
        return outputStr

    def set_data(self, data):
        '''
        Set the DVH data.

        Positonal arguments:
            :data:  list of (dose, volume) tuples
        '''
        self.data = np.array(data)
        if len(self.data.shape) > 1 and self.data.shape[1] > 0:
            self.dose_data = self.data[:, 0]
            # Update dose statistics
            self.min_dose = np.min(self.dose_data)
            self.max_dose = np.max(self.dose_data)
            self.mean_dose = np.mean(self.dose_data)
            self.std_dose = np.std(self.dose_data)
            if self.dose_units is None:
                if self.min_dose <= 1.0 and self.max_dose == 1.0:
                    self.dose_units = 'normalized'
                elif self.max_dose > 1000:
                    self.dose_units = 'cGy'
                else:
                    self.dose_units = 'Gy'
        else:
            self.dose_data = []
            self.min_dose = None
            self.max_dose = None
            self.dose_units = None

        if len(self.data.shape) > 1 and self.data.shape[1] > 1:
            self.volume_data = self.data[:, 1]
            if self.volume is None:
                self.volume = np.amax(self.volume_data)
            if self.volume_units is None:
                if self.volume == 1.0:
                    self.volume_units = 'normalized'
                else:
                    self.volume_units = 'cm3'
        else:
            self.volume_data = []
            self.volume_units = None

    def get_dose(self, type='cum', normalized=False):
        '''
        Get the dose data.

        Positional arguments:
            :type:  type of dose to calculate
                - 'cum' for cumulative dose
                - 'diff' for differential dose
        Keyword arguments:
            :normalized:    boolean value. If True, normalize all dose values by the maximum dose.
        Returns:
            Dose data bins from the dvh object
        '''
        if 'cum' in type:
            d = self.get_cumulative_dose()
        elif 'diff' in type:
            d = self.get_differential_dose()
        else:
            raise ValueError('Dose type "{0}" not recognized.'.format(type))

        if normalized:
            maxdose = np.amax(d)
            if maxdose == 0:
                raise TypeError('Normalization error: Maximum dose is 0.')
            d = d / maxdose
        return d

    def get_cumulative_dose(self, normalized=None):
        '''
        Convert dose bin widths to cumulative dose points

        Returns:
            Cumulative dose data bins
        '''
        if self.dose_type != 'cum':
            self.dose_type = 'cum'
            self.dose_data = cumulate_dose(self.dose_data)
            self.data[:, 0] = self.dose_data

        if normalized and ('norm' not in self.dose_units.lower()):
            maxdose = np.amax(self.dose_data)
            if maxdose == 0:
                raise TypeError('Normalization error: Maximum dose is 0.')
            self.data[:, 0] /= maxdose

        return self.dose_data

    def get_differential_dose(self, normalized=None):
        '''
        Convert cumulative dose points to dose bin widths (e.g., DICOM standard)

        Returns:
            Differential dose data bins
        '''
        if self.dose_type != 'diff':
            self.dose_type = 'diff'
            self.dose_data = differentiate_dose(self.dose_data)
            self.data[:, 0] = self.dose_data

        if self.dose_units is not None and 'norm' in self.dose_units:
            if self.volume is not None and self.volume > 0:
                self.dose_data *= self.volume
                self.data[:, 0] *= self.volume
            else:
                raise Exception(
                    'Cannot compute differential dose \
                    when the dose points are normalized unless the dvh.volume is given'
                )
        return self.dose_data

    def get_volume(self, type, normalized=False):
        '''
        Get the volume data.

        Positional arguments:
            :type:  type of dose to calculate
                - 'cum' for cumulative dose
                - 'diff' for differential dose
        Keyword arguments:
            :normalized:    boolean value. If True, normalize all dose values by the maximum dose.
        Returns:
            Volume data from the dvh object
        '''
        if 'cum' in type:
            v = self.get_cumulative_volume()
        elif 'diff' in type:
            v = self.get_differential_volume()
        else:
            raise ValueError('Dose type "{0}" not recognized.'.format(type))

        if normalized:
            maxvolume = np.amax(v)
            if maxvolume == 0:
                warnings.warn('Maximum volume is 0, normalization not performed.', Warning)
                return v
            v = v / maxvolume
        return v

    def get_cumulative_volume(self):
        '''
        Convert differential volume bins to cumulative volume bins

        Returns:
            Cumulative volume data bins
        '''
        if self.volume_type != 'cum':
            self.volume_type = 'cum'
            self.volume_data = cumulate_volume(self.volume_data)
            self.data[:, 1] = self.volume_data
        return self.volume_data

    def get_differential_volume(self):
        '''
        Convert cumulative volumes to differential volumes

        Returns:
            Differential volume data bins
        '''
        if self.volume_type != 'diff':
            self.volume_type = 'diff'
            self.volume_data = differentiate_volume(self.volume_data)
            self.data[:, 1] = self.volume_data
        return self.volume_data

    def get_differential_dvh(self):
        '''
        Compute the differential DVH data points

        Returns:
            List of tuples of differential DVH datapoints
        '''
        dose = self.get_cumulative_dose()
        volume = self.get_differential_volume()
        return [(d, v) for d, v in zip(dose, volume)]

    def estimate_mean(self):
        '''
        Estimate the mean dose from the differential DVH

        Returns:
            Mean dose
        '''
        dose = np.array(self.dose_data)
        if self.dose_type != 'cum':
            dose = cumulate_dose(dose)

        volume = np.array(self.volume_data)
        if self.volume_type != 'diff':
            volume = differentiate_volume(volume)

        if sum(volume) > 0:
            return sum(dose * volume) / sum(volume)
        return 0

    def compute_dose_mask(self):
        '''
        Compute a dose mask using the DVH class' roi and dose variables.

        Returns:
            List of dose values corresponding to each nonzero index in the mask
        '''
        from .dose_map import compute_dose_mask as cdm

        self.dose_mask, self.fraction_outside_dosegrid = cdm(dose=self.dose, mask=self.mask)
        # Compute stats
        self.min_dose = self.dose.min
        self.max_dose = self.dose.max
        self.mean_dose = self.dose.mean
        self.std_dose = self.dose.std
        return self.dose_mask

    def compute_dvh(self):
        '''
        Compute a DVH curve for the given ROI from the given dose grid. Returns
        the DVH data. If no binary mask is specified, one will be computed for
        the dvh.roi. The value of each voxel contained within the mask is used
        to weight the dose data in the final histogram. Input parameter "bins"
        may be specified as an integer number of bins to include in the histogram,
        or it may be a vector of bin edges (see np.histogram).

        If an edge_voxel_weight is specified, all edge voxels in the x-y plane of
        the binary mask are multipled by the specified weight.
        '''
        self.dose_mask = self.compute_dose_mask()
        (self.dose_data, self.volume_data), frac_outside_dosegrid = compute_dvh(
            dose_mask=self.dose_mask)
        if frac_outside_dosegrid is not None:
            self.fraction_outside_dosegrid = frac_outside_dosegrid

        self.data = np.vstack((self.dose_data, self.volume_data)).T
        return self.data

    def get_dose_to_volume(self, v):
        '''
        Get the dose delivered to v percent of the volume.

        Keyword arguments:
            :v:     fraction of the volume (from 0 to 1)
        Returns:
            :d:     dose delivered to specified volume in cGy
        '''
        if self.data is None:
            self.compute_dvh()

        idx = (np.abs(self.data[:, 1] - v)).argmin()
        return self.data[idx, 0]

    def get_volume_with_dose(self, d):
        '''
        Get the dose delivered to v percent of the volume.

        Keyword arguments:
            :d:     dose value
        Returns:
            :v:     fraction of volume receiving specified dose
        '''
        if self.data is None:
            self.compute_dvh()

        if d <= self.max_dose:
            idx = (np.abs(self.data[:, 0] - d)).argmin()
            return self.data[idx, 1]
        else:
            return 0.0
