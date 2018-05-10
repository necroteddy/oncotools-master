'''
Image-related metadata and routines designed to mimic the Insight Toolkit.

The origin, index, size, and spacing should be specified as [X,Y,Z], while
the data buffer is actually stored in [Z,Y,X] order. This is because the last
index in an N-D array changes most rapidly. Use the get_pixel() and set_pixel()
data accessors to avoid confusion.

TODO:
    - Add image direction cosines
'''

import gzip
import numpy as np


class Image(object):
    '''
    Image-related metadata and routines designed to mimic the Insight Toolkit.

    Fields:
        :dimension:     Number of dimensions (typically 2 [2D] or 3 [3D])
        :origin:        Coordinates of the first image pixel/voxel
        :end:           Coordinates of the last image pixel/voxel
        :index:         Indices of the first pixel/voxel
        :size:          Number of pixels/voxels in each dimension
        :spacing:       Spacing between pixels/voxels
        :direction:     direction cosines
        :data:          numpy array storing image data
    Note:
        The origin, index, size, and spacing should be specified as [X,Y,Z].
        However, the data buffer is actually stored in [Z,Y,X]
        order because the last index in an N-D array changes most rapidly.
        Use the get_pixel() and set_pixel() data accessors to avoid confusion.
    '''

    def __init__(self, dim=3):
        # Number of dimensions (typically 2 [2D] or 3 [3D])
        self.dimension = dim
        self.origin = [0.0] * dim  # Coordinates of the first image pixel/voxel
        self.end = [1.0] * dim  # Coordinates of the last image pixel/voxel
        self.index = [
            0.0
        ] * dim  # Indices of the first pixel/voxel. Image does not have to start at [0,0,0]
        self.size = [1] * dim  # Number of pixels/voxels in each dimension
        self.spacing = [
            1.0
        ] * dim  # Spacing between pixels/voxels. Corresponds to pixel/voxel size
        self.direction = [1.0, 0.0, 0.0, 0.0, 1.0,
                          0.0]  # Direction cosines (TODO not yet implemented)
        self.data = np.empty(
            shape=self.size[::-1], dtype=float
        )  # Image data. Currently supports one data element per pixel. Vector images not supported

    def __str__(self):
        outputStr = 'Dimension:  ' + str(self.dimension) + '\n' \
            + 'Origin:     ' + str(self.origin) + '\n' \
            + 'End:        ' + str(self.end) + '\n' \
            + 'Spacing:    ' + str(self.spacing) + '\n' \
            + 'Index:      ' + str(self.index) + '\n' \
            + 'Size:       ' + str(self.size) + ' (voxels)' + '\n' \
            + 'Direction:  ' + str(self.direction)
        return outputStr

    @property
    def center_of_mass(self):
        '''
        Calculate the center of mass for a mask.

        Returns:
            Indices of an image's center of mass in the data matrix (X,Y,Z).
        '''
        pts = self.data.nonzero()
        return np.mean(pts, axis=1)[::-1]

    def set_image(self,
                  img,
                  origin=None,
                  index=None,
                  spacing=None,
                  direction=None):
        '''
        Set a data buffer to the current image instance. Origin, index,
        and spacing should be specified as [X,Y,Z]

        Positional arguments:
            :img:       buffer to store as data
        Keyword arguments:
            :origin:        Coordinates of the first image pixel/voxel
            :index:         Indices of the first pixel/voxel
            :spacing:       Spacing between pixels/voxels
            :direction:     direction cosines
        '''
        img = np.array(img)
        self.data = img
        self.dimension = len(img.shape)
        if origin is not None:
            self.origin = origin
        if index is not None:
            self.index = index
        if spacing is not None:
            self.spacing = spacing
        if direction is not None:
            self.direction = direction

        self.size = img.shape[::-1]
        self.update_end()

    def get_image(self):
        '''
        Get the image data.
        '''
        return self.data

    def copy_information(self, img):
        '''
        Copy image information from another image instance.

        Positional arguments:
            :img:   image from which to copy data.
        '''
        self.dimension = int(img.dimension)
        self.origin = np.array(img.origin)
        self.end = np.array(img.end)
        self.index = np.array(img.index)
        self.size = np.array(img.size)
        self.spacing = np.array(img.spacing)
        self.direction = np.array(img.direction)

    def set_origin(self, origin):
        '''
        Set the origin.

        Positional arguments:
            :origin:    new origin
        '''
        self.origin = origin

    def get_origin(self):
        '''
        Get the origin.

        Returns:
            The origin field
        '''
        return self.origin

    def set_end(self, imageEnd):
        '''
        Set the coordinates of the last pixel in the image.

        Positional arguments:
            :imageEnd:  new end
        '''
        self.end = imageEnd

    def update_end(self):
        '''
        Updates the image end.

        To be called after the origin, size, and spacing have been set.
        '''
        self.end = [
            self.origin[d] + (self.size[d] - 1) * self.spacing[d]
            for d in range(self.dimension)
        ]

    def get_end(self):
        '''
        Get the coordinates of the last pixel in the image.

        Returns:
            The end field
        '''
        return self.end

    def set_index(self, index):
        '''
        Set the index of the first pixel in the image.

        Positional arguments:
            :index:  new index
        '''
        self.index = index

    def get_index(self):
        '''
        Get the index of the first pixel in the image.

        Returns:
            The index field
        '''
        return self.index

    def set_size(self, size):
        '''
        Set the number of pixels/voxels in each dimension.

        Positional arguments:
            :size:  new index
        '''
        self.size = size

    def get_size(self):
        '''
        Get the number of pixels/voxels in each dimension.

        Returns:
            The size field
        '''
        return self.size

    def set_spacing(self, spacing):
        '''
        Set the spacing between slices in each dimension.

        Positional arguments:
            :spacing:   numpy array of spacing between slices in each dimension
        '''
        self.spacing = spacing

    def get_spacing(self):
        '''
        Get the spacing between slices in each dimension.

        Returns:
            The spacing field
        '''
        return self.spacing

    def get_voxel_volume(self):
        '''
        Get the volume of a voxel in the image.

        Returns:
            Volume of a singe voxel, calculated as the product of the spacing
        '''
        return np.product(np.array(self.spacing))

    def allocate(self, dtype=None):
        '''
        Create an empty data buffer to store image data.

        Elements are not initialized. Recall that the data buffer should be accessed as [Z,Y,X].

        Keyword arguments:
            :dtype:     data type of the values in the data array
        '''
        if dtype is None:
            self.data = np.empty(shape=np.asarray(self.size[::-1]).astype(int))
        else:
            self.data = np.empty(shape=np.asarray(
                self.size[::-1]).astype(int), dtype=dtype)

    def fill_buffer(self, value=0.0, dtype=None):
        '''
        Create a data buffer with elements initialized to 'value'.

        Recall that the data buffer should be accessed as [Z,Y,X].
        Keyword arguments:
            :value:     value to assign to all values in the array
            :dtype:     data type of the values in the data array
        '''
        if value == 0.0 and dtype is None:
            self.data = np.zeros(shape=self.size[::-1])
        elif value == 0.0:
            self.data = np.zeros(shape=self.size[::-1], dtype=dtype)
        elif dtype is None:
            self.data = dtype(value) * np.ones(shape=self.size[::-1])
        else:
            self.data = dtype(value) * np.ones(
                shape=self.size[::-1], dtype=dtype)

    def transform_index_to_physical_point(self, index):
        '''
        Get the physical coordinates for the voxel with the given index.

        Positional arguments:
            :index:     index specified as [x,y,z]. Can also specify an N x dim array of indices.
        Returns:
            numpy array of physical coordinates corresponding to index
        '''
        origin = np.array(self.origin)
        spacing = np.diag(np.array(self.spacing))
        return (np.array(index) - np.array(self.index)).dot(spacing) + origin

    def transform_physical_point_to_index(self, point):
        '''
        Transform a physical point to the nearest integer index.

        Positional arguments:
            :point:     point specified as [x,y,z]. Can also specify an N x dim array of points.
        Returns:
            numpy array of index corresponding to given point
        '''
        continuous_index, inbounds = self.transform_physical_point_to_continuous_index(
            point)
        return np.rint(continuous_index).astype(int), inbounds

    def transform_physical_point_to_continuous_index(self, point):
        '''
        Transform a physical point to a continuous image index.

        Positional arguments:
            :point:     point specified as [x,y,z]. Can also specify an N x dim array of points.
        '''
        origin = np.array(self.origin)
        inverse_spacing = np.diag(1.0 / np.array(self.spacing))
        continuous_index = (np.array(point) - origin
                            ).dot(inverse_spacing) + np.array(self.index)

        inbounds = np.logical_and(
            continuous_index >= np.array(self.index),
            continuous_index < np.array(self.index) + np.array(self.size))
        if len(inbounds.shape) > 1:
            inbounds = inbounds.all(axis=1)

        return continuous_index, inbounds

    def transform_to_point_cloud(self):
        '''
        Convert a mask image into a set of (x,y,z) points.

        Returns:
            numpy array of (x,y,z) points corresponding to nonzero values in image
        '''
        msk_idx = self.data.nonzero()
        msk_idx = np.fliplr(np.asarray(msk_idx).T)
        msk_pts = self.transform_index_to_physical_point(msk_idx)
        return msk_pts

    def set_pixel(self, idx, value):
        '''
        Set a pixel in the image data buffer.

        Positional arguments:
            :idx:   index of pixel to be assigned a value. Should be specified as [X,Y,Z].
                This will update data[Z,Y,X].
            :value: the value to assign to the pixel
        '''
        zeroedIdx = [
            round(idx[d] - self.index[d]) for d in range(self.dimension)
        ]
        idxZYX = zeroedIdx[::-1]
        self.data[tuple(idxZYX)] = value

    def get_pixel(self, idx):
        '''
        Get a pixel from the image data buffer.

        Positonal arguments:
            :idx:   index to The input index. Should be specified as [X,Y,Z]
        '''
        zeroedIdx = [
            round(idx[d] - self.index[d]) for d in range(self.dimension)
        ]
        idxZYX = zeroedIdx[::-1]
        return self.data[tuple(idxZYX)]

    def interpolate_pixel(self, continuous_idx):
        '''
        Get a pixel from the current image, using trilinear interpolation.

        Positonal arguments:
            :continuous_idx:   index to The input index. Should be specified as [X,Y,Z]
        '''
        idxZYX = continuous_idx[::-1]
        lower_idx = np.floor(idxZYX).astype(int)
        neighbor_pixel_idx = np.vstack((lower_idx, lower_idx + 1))
        neighbor_pixel_grid = np.meshgrid(
            *(neighbor_pixel_idx.transpose()), indexing='ij')
        data = self.data[tuple(neighbor_pixel_grid)]
        weight = list(np.array(idxZYX) - lower_idx)
        while weight:
            w = weight.pop()  # Pop from the end to get z, y, x
            data = data[0] * (1 - w) + data[1] * w
        return data

    def get_slice(self, slice_idx):
        '''
        Returns a 2D slice from a 3D image.

        Positonal arguments:
            :slice_idx:     index of the slice to return
        '''
        zIdx = int(round(slice_idx[2] - self.index[2]))
        return self.data[zIdx]

    def interpolate_slice(self, *args):
        '''
        Get a slice from the current image.

        Input argument(s) should be one of the following:
            - 1 input: An Nx1 list of continuous slice (z) indices
            - 3 inputs: ix, iy, iz. ix and iy specify the indices in the x-y plane
                to be included in the interpolation. iz is the list of continuous slice (z) indices.
        '''
        if len(args) == 1:
            ix = iy = None
            continuous_slice_idx = np.array(args[0])
        elif len(args) == 3:
            ix = args[0]
            iy = args[1]
            continuous_slice_idx = args[2]
        else:
            return None

        # Check inputs: ix, iy, and continuous_slice_idx must be arrays
        def scalar_to_array(s):
            try:
                s[0]
                return s
            except:
                return np.array([s])

        ix = scalar_to_array(ix)
        iy = scalar_to_array(iy)
        continuous_slice_idx = scalar_to_array(continuous_slice_idx)

        lower_slices = scalar_to_array(np.int_(continuous_slice_idx))
        upper_slices = lower_slices + 1
        upper_slices[upper_slices == self.index[2] + self.size[2]] -= 1

        weight = (continuous_slice_idx - lower_slices).reshape(-1, 1, 1)
        if ix is not None and iy is not None:
            return self.data[lower_slices, iy[0]:(iy[-1]+1), ix[0]:(ix[-1]+1)]*(1-weight) + \
                self.data[upper_slices, iy[0]:(
                    iy[-1]+1), ix[0]:(ix[-1]+1)]*(weight)
        else:
            return self.data[lower_slices] * (
                1 - weight) + self.data[upper_slices] * (weight)

    def resample(self, template):
        '''
        Resample the current image into the physical coordinates of the given template.
        Uses linear interpolation
        '''
        # Interpolate in z
        t, l, u, w = self.compute_resampled_indices(template, 2)
        data = self.data[l, :, :] * (1 - w) + self.data[u, :, :] * w
        index = [0, 0, t[0]]

        # Interpolate in y
        t, l, u, w = self.compute_resampled_indices(template, 1)
        data = data[:, l, :] * (1 - w) + data[:, u, :] * w
        index[1] = t[0]

        # Interpolate in x
        t, l, u, w = self.compute_resampled_indices(template, 0)
        data = data[:, :, l] * (1 - w) + data[:, :, u] * w
        index[2] = t[0]

        resampled_image = Image()
        resampled_image.data = data
        resampled_image.copy_information(template)
        resampled_image.size = data.shape[::-1]
        resampled_image.index = index
        resampled_image.update_end()
        return resampled_image

    def compute_resampled_indices(self, template, dim):
        '''
        Resampling helper function. Returns continuous indices inside 'self' aligned with
        slices of the template in the given dimension
        '''
        template_indices = np.arange(template.size[dim])
        coordinates = template_indices * \
            template.spacing[dim] + template.origin[dim]
        self_indices = (coordinates - self.origin[dim]
                        ) / self.spacing[dim] + self.index[dim]
        inbounds = np.logical_and(
            self_indices >= self.index[dim],
            self_indices <= self.index[dim] + self.size[dim] - 1)

        template_indices = template_indices[inbounds]
        self_indices = self_indices[inbounds]

        self_lower_indices = np.int_(self_indices)
        self_upper_indices = self_lower_indices + 1
        self_upper_indices[self_upper_indices == self.index[dim] +
                           self.size[dim]] -= 1

        reshape_dim = np.ones(self.dimension)
        reshape_dim[dim] = -1
        weights = (
            self_indices - self_lower_indices).reshape(reshape_dim[::-1])

        return template_indices, self_lower_indices, self_upper_indices, weights


def get_mask_edge_voxels(msk, exclude_z=False):
    mask_neg = np.logical_not(msk.data)

    edge_mask = Mask()
    edge_mask.copy_information(msk)
    edge_mask.fill_buffer(0, np.bool)

    sz, sy, sx = msk.data.shape
    iz, iy, ix = np.nonzero(msk.data)
    if iz.size == 0:
        return edge_mask

    if iz.min() > 0 and iz.max() < sz-1 \
            and iy.min() > 0 and iy.max() < sy-1 \
            and ix.min() > 0 and ix.max() < sx-1:
        if exclude_z:
            edge_mask.data[iz, iy, ix] = \
                np.logical_and(msk.data[iz, iy, ix],
                               np.logical_or(mask_neg[iz, iy-1, ix],
                                             np.logical_or(mask_neg[iz, iy+1, ix],
                                                           np.logical_or(mask_neg[iz, iy, ix-1],
                                                                         mask_neg[iz, iy, ix+1]))))
        else:
            edge_mask.data[iz, iy, ix] = \
                np.logical_and(msk.data[iz, iy, ix],
                               np.logical_or(mask_neg[iz-1, iy, ix],
                                             np.logical_or(mask_neg[iz+1, iy, ix],
                                                           np.logical_or(mask_neg[iz, iy-1, ix],
                                                                         np.logical_or(mask_neg[iz, iy+1, ix],
                                                                                       np.logical_or(mask_neg[iz, iy, ix-1],
                                                                                                     mask_neg[iz, iy, ix+1]))))))
    else:
        if not exclude_z:
            i = iz > 0
            edge_mask.data[iz[i], iy[i], ix[i]] = np.logical_or(
                edge_mask.data[iz[i], iy[i], ix[i]],
                mask_neg[iz[i] - 1, iy[i], ix[i]])
            i = iz < sz - 1
            edge_mask.data[iz[i], iy[i], ix[i]] = np.logical_or(
                edge_mask.data[iz[i], iy[i], ix[i]],
                mask_neg[iz[i] + 1, iy[i], ix[i]])
        i = iy > 0
        edge_mask.data[iz[i], iy[i], ix[i]] = np.logical_or(
            edge_mask.data[iz[i], iy[i], ix[i]],
            mask_neg[iz[i], iy[i] - 1, ix[i]])
        i = iy < sy - 1
        edge_mask.data[iz[i], iy[i], ix[i]] = np.logical_or(
            edge_mask.data[iz[i], iy[i], ix[i]],
            mask_neg[iz[i], iy[i] + 1, ix[i]])
        i = ix > 0
        edge_mask.data[iz[i], iy[i], ix[i]] = np.logical_or(
            edge_mask.data[iz[i], iy[i], ix[i]],
            mask_neg[iz[i], iy[i], ix[i] - 1])
        i = ix < sx - 1
        edge_mask.data[iz[i], iy[i], ix[i]] = np.logical_or(
            edge_mask.data[iz[i], iy[i], ix[i]],
            mask_neg[iz[i], iy[i], ix[i] + 1])

        edge_mask.data[iz, iy, ix] = np.logical_and(msk.data[iz, iy, ix],
                                                    edge_mask.data[iz, iy, ix])
    return edge_mask


def run_length_encode(mask):
    ''' Return a run-length-encoded string representation of the ROI binary mask '''
    maskdata = np.concatenate(([1], mask.data.flatten()))
    runlength = np.nonzero(np.diff(maskdata))
    return ','.join(map(str, runlength[0]))


def run_length_decode(runlength, dimZYX):
    ''' Return an ROI instance in the binary mask representation from the runlength string'''
    cutpoints = np.fromstring(runlength, dtype=np.int32, sep=',')
    startpoints = cutpoints[1::2]
    endpoints = cutpoints[2::2]
    mybuffer = np.zeros(int(np.prod(dimZYX)), dtype=np.dtype('b'))
    for s, e in zip(startpoints, endpoints):
        mybuffer[s:e] = True
    mybuffer = mybuffer.reshape([int(d) for d in dimZYX])
    msk = Mask()
    msk.set_image(mybuffer)
    return msk


def load_binary_mask(file, dimX=None, dimY=None, dimZ=None):
    mybuffer = None
    try:
        gz = gzip.open(file)
        mybuffer = gz.read()
        gz.close()
    except Exception:
        f = open(file, 'rb')
        mybuffer = f.read()
        f.close()

    mybuffer = np.frombuffer(mybuffer, dtype=np.dtype('b'))
    if dimX is not None and dimY is not None and dimZ is not None:
        mybuffer = mybuffer.reshape((int(dimZ), int(dimY), int(dimX)))
        mybuffer.shape = (dimZ, dimY, dimX)
    msk = Mask()
    msk.set_image(mybuffer)
    return msk


class Mask(Image):
    '''
    The mask class adds functions to the image class that specifically relate to binary masks.
    '''

    def __init__(self, dim=3):
        Image.__init__(self, dim=3)
        self.edge_mask = None
        self.volume = None

    def load(self, infile, dimX=None, dimY=None, dimZ=None):
        '''
        Load a binary mask from a file

        Positional arguments:
            :infile:  file to open
        Keyword arguments:
            :dimX:  length in the X dimension
            :dimY:  length in the Y dimension
            :dimZ:  length in the Z dimension
        '''
        dimX, dimY, dimZ = self.size
        self.set_image(load_binary_mask(infile, dimX, dimY, dimZ).data)

    @property
    def lower_bound(self):
        '''
        Get the lower bound of the binary mask.

        Returns:
            numpy array of lower bound of the nonzero elements of the mask
        '''
        z, y, x = np.amin(np.nonzero(self.data), 1)
        return np.array([x, y, z])

    @property
    def upper_bound(self):
        '''
        Get the upper bound of the binary mask.

        Returns:
            numpy array of upper bound of the nonzero elements of the mask
        '''
        z, y, x = np.amax(np.nonzero(self.data), 1)
        return np.array([x + 1, y + 1, z + 1])

    @property
    def bounds(self):
        '''
        Get the upper and lower bounds of the binary mask

        Returns:
            tuple of numpy arrays (lower bound, upper bound) of the nonzero elements of the mask
        '''
        nz = np.nonzero(self.data)
        zl, yl, xl = np.amin(nz, 1)
        zu, yu, xu = np.amax(nz, 1)
        return (np.array([xl, yl, zl]), np.array([xu + 1, yu + 1, zu + 1]))

    def get_mask_edge_voxels(self, exclude_z=False):
        '''
        Get all voxels on the edge of the mask.
        '''
        if self.edge_mask is not None:
            return self.edge_mask
        self.edge_mask = get_mask_edge_voxels(self, exclude_z)
        return self.edge_mask

    def get_volume(self, edge_voxel_weight=None):
        '''
        Compute the ROI volume from the binary mask

        Keyword arguments:
            :edge_voxel_weight: weight assigned to edge voxels when computing volume
        Returns:
            volume of the binary mask
        '''
        voxelVolume = np.prod(np.array(self.spacing))
        self.volume = len(self.data.nonzero()[0]) * voxelVolume

        if edge_voxel_weight is not None and edge_voxel_weight != 1.0:
            if self.edge_mask is None:
                self.edge_mask = self.get_mask_edge_voxels(exclude_z=True)
            self.volume -= (1 - edge_voxel_weight) * len(
                self.edge_mask.data.nonzero()[0]) * voxelVolume

        return self.volume

    def run_length_encode(self):
        '''
        Return:
            run-length-encoded string representation of the ROI binary mask
        '''
        return run_length_encode(self)

    def set_data_with_indices(self, points):
        '''
        Construct a new mask using a list of points corresponding to voxels in the mask.

        Positional arguments:
            :points:    list of (x,y,z) indices that correspond to voxels in the mask
        '''
        self.data = np.zeros(self.data.shape)
        for pt in points:
            self.data[pt[2], pt[1], pt[0]] = 1
