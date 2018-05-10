'''
Dose-related metadata and routines designed to mimic the Insight Toolkit.
Inherits from the 'Image' class and provides additional parameters and
methods specific to dose grids.
'''

from .image import Image
import numpy as np


class Dose(Image):
    '''
    The dose class is a representation of the dose grid and all associated metadata.

    Keyword arguments:
        :dose_grid:             numpy array storing dose information
        :dose_scaling_factor:   scaling factor for dose values
    '''

    def __init__(self, dose_grid=None, dose_scaling_factor=1.0):
        Image.__init__(self, dim=3)
        self.data = None        # Dose data
        self.dose_units = None  # Gy, cGy, normalized, etc.
        self.scaled_data = None # Dose data * dose_scaling_factor
        # Mimic DICOM dose, which allows dose grid to be scaled by a multiplicative factor
        self.dose_scaling_factor = dose_scaling_factor
        self.min_dose = 0.0     # Minimum dose
        self.max_dose = 0.0     # Maximum dose
        self.mean_dose = 0.0    # Mean dose
        self.std_dose = 0.0     # Dose standard deviation
        self.dvh = {}           # DVH for a given ROI obtained
        if dose_grid is not None:
            self.set_dose(dose_grid, dose_scaling_factor)
        # Was the dose grid's origin corrected?
        self.origin_modified = False

    def __str__(self):
        outputStr = Image.__str__(self) + '\n' \
                  + 'Dose Units: ' + str(self.dose_units) + '\n' \
                  + 'Scaling:    ' + str(self.dose_scaling_factor) + '\n' \
                  + 'Max Dose:   ' + str(self.max) + '\n' \
                  + '# DVHs:     ' + str(len(self.dvh))
        return outputStr

    def set_dose(self, dose_grid, dose_scaling_factor=1.0):
        '''
        Set the dose grid. Input is converted to a numpy array

        Positional arguments:
            :dose_grid:     dose grid representing dose per voxel
        Keyword arguments:
            :dose_scaling_factor:   scaling factor for dose values
        '''
        self.set_image(self, dose_grid)
        self.dose_scaling_factor = dose_scaling_factor
        self.data = np.array(dose_grid)
        self.scaled_data = self.data * dose_scaling_factor
        self.min_dose = self.scaled_data.min()
        self.max_dose = self.scaled_data.max()
        self.mean_dose = self.scaled_data.mean()
        self.std_dose = self.scaled_data.std()

    def get_dose(self):
        '''
        Get the dose grid.

        Returns:
            numpy array of dose data per voxel
        '''
        if self.dose_scaling_factor == 1.0:
            return self.data
        elif hasattr(self, 'scaled_data'):
            return self.scaled_data
        else:
            scaled_data = self.data * float(self.dose_scaling_factor)
            self.scaled_data = np.array(scaled_data, dtype=np.float32)
            return self.scaled_data

    @property
    def min(self):
        '''
        Get the min dose.
        '''
        if self.min_dose == 0.0:
            dose_data = self.get_dose()
            dose_data = dose_data[dose_data.nonzero()]
            self.min_dose = np.min(dose_data)
        return self.min_dose

    @property
    def max(self):
        '''
        Get the max dose.
        '''
        if self.max_dose == 0.0:
            self.max_dose = np.max(self.get_dose())
        return self.max_dose

    @property
    def mean(self):
        '''
        Get the mean dose.
        '''
        if self.mean_dose == 0.0:
            dose_data = self.get_dose()
            dose_data = dose_data[dose_data.nonzero()]
            self.mean_dose = np.mean(dose_data)
        return self.mean_dose

    @property
    def std(self):
        '''
        Get the standard deviation of the dose.
        '''
        if self.std_dose == 0.0:
            dose_data = self.get_dose()
            dose_data = dose_data[dose_data.nonzero()]
            self.std_dose = np.std(self.get_dose())
        return self.std_dose

    def copy_information(self, img):
        '''
        Copy image information from the input image instance

        Positional arguments:
            :img: dose object
        '''
        Image.copy_information(self, img)
        self.dose_units = str(img.dose_units)
        self.dose_scaling_factor = float(img.dose_scaling_factor)
        self.data = img.data
        self.scaled_data = img.data * img.dose_scaling_factor
        self.min_dose = img.scaled_data.min()
        self.max_dose = img.scaled_data.max()
        self.mean_dose = img.scaled_data.mean()
        self.std_dose = img.scaled_data.std()

    def set_pixel(self, idx, value):
        '''
        Set a pixel in the image data buffer.

        Positional arguments:
            :idx:   (x,y,z) index of pixel to be updated
            :value: value to assign to the given voxel
        Note:
            The input index should be specified as [X,Y,Z].
            This will update data, which is indexed [Z,Y,X].
        '''
        Image.set_pixel(self, idx, value * self.dose_scaling_factor)

    def get_pixel(self, idx):
        '''
        Get a pixel from the image data buffer.

        Positional arguments:
            :idx:   (x,y,z) index of pixel to be read
        Note:
            The input index should be specified as [X,Y,Z].
            This will update data, which is indexed [Z,Y,X].
        Returns:
            Value of selected pixel
        '''
        return Image.get_pixel(self, idx) * self.dose_scaling_factor

    def interpolate_pixel(self, continuous_idx):
        '''
        Get a pixel from the current image. This function allows the image
        to be interpolated via tri-linear interpolation.

        Positional arguments:
            :continuous_idx:   (x,y,z) index of pixel to be read
        Note:
            The input index should be specified as [X,Y,Z].
            This will update data, which is indexed [Z,Y,X].
        Returns:
            Value of selected interpolated pixel
        '''
        return Image.interpolate_pixel(
            self, continuous_idx) * self.dose_scaling_factor

    def get_slice(self, slice_idx):
        '''
        Returns a 2D slice from a 3D image.

        Positional arguments:
            :slice_idx:     index of the slice to return
        Returns:
            2-D image object of the selected slice
        '''
        return Image.get_slice(self, slice_idx) * self.dose_scaling_factor

    def interpolate_slice(self, *args):
        '''
        Get a slice from the current image.

        Input argument(s) should be one of the following:
            - 1 input: An Nx1 list of continuous slice (z) indices
            - 3 inputs: ix, iy, iz
                Note:
                    ix and iy specify the indices in the x-y plane to be included in the
                    interpolation. iz is the list of continuous slice (z) indices
        '''
        myslice = Image.interpolate_slice(self, *args)
        if myslice is None:
            return None
        return myslice * self.dose_scaling_factor

    def get_dose_points(self, points):
        '''
        Look up the list of points in the dose grid.

        Positional arguments:
            :points:    list of (x,y,z) index of pixel to be updated
        Note:
            The input index should be specified as [X,Y,Z].
        Returns:
            List of Values of the given pixels
        '''
        return [
            Image.get_pixel(self, idx) * self.dose_scaling_factor
            for idx in points
        ]

def load_dose(infile, dimX=None, dimY=None, dimZ=None):
    '''
    Load dose from a buffer into a Dose object
    '''
    f = open(infile, 'rb')
    mybuff = f.read()
    f.close()

    mybuffer = np.frombuffer(mybuff, dtype=np.dtype(np.dtype('<f4')))
    if dimX is not None and dimY is not None and dimZ is not None:
        mybuffer.shape = (dimZ, dimY, dimX)
    d = Dose()
    d.set_image(mybuffer)
    return d
