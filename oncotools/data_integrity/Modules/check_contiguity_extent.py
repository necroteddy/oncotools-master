import numpy as np

class check_contiguity_extent(object):
    def __init__(self):
        self.name = "check_contiguity_extent(mask)"
        self.function = "Check that a mask is contiguous using projections along x, y, and z axes. \nPositional arguments: \n\t:mask:  mask object"

    def name(self):
        return self.name

    def function(self):
        return self.function

    def description(self):
        return {self.name: self.function}

    #def check_integrity(self, patient):
    def check_integrity(self, mask):
        '''
        Check that a mask is contiguous using projections along x, y, and z axes.

        Positional arguments:
            :mask:  mask object
        '''
        # Get the nonzero indices
        nz = mask.data.nonzero()
        # Transpose and horizontally stack the rows
        indices = np.fliplr(np.transpose(np.asarray(nz)))

        # Compute extent in the x, z, and z directions
        extents = [max(indices[:, i]) - min(indices[:, i]) for i in range(3)]

        # How many slices are missing along each axis?
        missing = [
            extents[i] + 1 - len(np.unique(indices[:, i])) for i in range(3)
        ]

        # Valid if no nonzero numbers of missing slices
        valid = not np.any(missing)
        # Construct the message string
        if valid:
            message = 'Mask is contiguous along all axes.'
        else:
            axis_names = ['x', 'y', 'z']
            missing_message = [
                '{0} slices missing along {1}-axis'.format(
                    missing[i], axis_names[i]) for i in range(3)
                if missing[i] > 0
            ]
            message = 'Warning: ' + ', '.join(missing_message)

        if valid == False:
            errortype = "error found by check_contiguity_extent()"
        else:
            errortype = None

        return (valid, message, errortype)
