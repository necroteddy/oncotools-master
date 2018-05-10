'''
Region of interest (ROI) class. Defines parameters and functions that relate
to ROIs.

Contours should be defined according to dicompyler conventions as a dictionary with
    key: contour plane coordinates
    value: list of all contours on that plane
'''

from matplotlib.path import Path
from . import image
import numpy as np
import warnings


def parse_contour_data(*args):
    '''
    Contour data should be passed as one of the following
    1. Contour([x0,y0,z0,x1,y1,z1,...]) - One linear (flattened) array of points
    2. Contour([[x0,y0,z0],[x1,y1,z1],...]) - An Nx3 array of points
    3. Contour([x],[y],[z]) - Separate linear arrays for each dimension
    Data is cast to floats
    '''
    # Contour data is a 2D numpy array
    if len(args) == 0:
        data, plane = None, None
    elif len(args) == 1:
        # Input option 1: Contour([x0,y0,z0,x1,y1,z1,...])
        # Input option 2: Contour([[x0,y0,z0],[x1,y1,z1],...])
        data = np.array(args[0], dtype=float).reshape(-1, 3)
        plane = data[0, 2]
    elif len(args) == 3:
        # Input option 3: Contour([x],[y],[z])
        x, y = args[0], args[1]
        try:
            plane = float(args[2][0])  # If z specified as vector
            z = args[2]
        except:
            plane = float(args[2])  # If z specified as scalar
            z = np.ones(x.shape, dtype=float) * plane
        data = np.array([x, y, z], dtype=float).T
    else:
        data, plane = None, None
        raise Exception('Failed to initialize contour. Incorrect number of input parameters')
    return data, plane


class Contour(object):
    def __init__(self, *args):
        self.data, self.plane = parse_contour_data(*args)

    def __str__(self):
        outputStr = 'Plane:      ' + str(self.plane) + '\n' \
            + 'Area:       ' + str(self.get_area()) + '\n' \
            + '# Points:   ' + str(self.data.shape[0])
        return outputStr

    def x(self):
        return self.data[:, 0]

    def y(self):
        return self.data[:, 1]

    def z(self):
        return np.array([self.plane] * len(self.x()))

    def min(self):
        return self.data.min(0)

    def max(self):
        return self.data.max(0)

    def get_path(self, direction=None):
        '''
        Returns a matplotlib path object. Input parameter 'direction' specifies whether
        the path should run counter-clockwise (direction=1) or clockwise (direction=-1).
        For a counter-clockwise path, the 'path.contains_point(s)' function radius will
        expand the path, whereas for a clockwise path, the radius will contract the path.
        '''
        data = self.data[:, :2]
        if direction is None:
            return Path(np.array(data))

        # Use a small expansion radius to account for floating-point rounding errors
        r = 0.0001

        path = Path(np.array(data))
        path_contains_point = path.contains_point(data[0, :], radius=r)
        if (direction == 1 and path_contains_point) or \
           (direction != 1 and not path_contains_point):
            return path
        else:
            return Path(np.array(data[::-1, :]))

    def get_area(self):
        '''
        Compute the area of the contour using the 'Shoelace formula'
        http://en.wikipedia.org/wiki/Shoelace_formula
        http://mathworld.wolfram.com/PolygonArea.html

        Note that the area may be negative for clockwise paths.
        '''
        x, y = self.x(), self.y()
        i = np.append(np.arange(1, len(x)), 0)  # i = [1,2,3,...,N-2,N-1,0]
        return 0.5 * np.sum(x * y[i] - x[i] * y)

    def get_direction(self):
        '''Returns 1 if contour points run counter clockwise, -1 if clockwise'''
        return np.sign(self.get_area())


class Roi(object):
    '''
    Region of interest (ROI) class. Defines parameters and functions that relate
    to ROIs.
    '''

    def __init__(self, name=None, volume=None, contours=None, msk=None):
        self.name = name  # ROI name
        # ROI meta-data (data format-specific, e.g., DICOM, Pinnacle, etc.)
        self.header = {}
        self.volume = volume  # ROI volume based on contours
        self.mask_volume = None  # ROI volume based on binary mask
        self.contours = []  # List of ROI contours
        if contours is not None:
            self.contours.extend(contours)
        self.mask = msk  # Binary mask representation (image.mask)

    def __str__(self):
        outputStr = 'Name:       ' + str(self.name) + '\n' \
            + 'Volume:     ' + str(self.volume) + '\n' \
            + '# Contours: ' + str(len(self.contours))
        return outputStr

    def add_contour(self, *args):
        '''
        Add a contour to the current ROI. By convention, contour points should be listed
        in counter-clockwise order. The exception is for ring structures (any ROIs with
        holes), in which case the inner contours should be clockwise
        '''
        self.contours.append(Contour(*args))

    def get_contour_planes(self):
        '''
        Get a sorted list of unique contour planes
        '''
        return sorted(set([c.plane for c in self.contours]))

    def get_slice_thickness(self):
        '''
        Compute the smallest gap between adjacent contour planes.

        Returns:
            - Minimum spacing between slices
            - 0 if only one contour plane exists for the current ROI
            - None if the ROI has no contours
        '''
        planes = np.array(self.get_contour_planes())
        if len(planes) > 1:
            return min(planes[1:] - planes[:-1])
        elif len(planes) == 1:
            return 0
        else:
            return None

    def check_contour_directions(self):
        '''
        Check the direction of all ROI contours.

        By convention, contour points should be listed in counter-clockwise order.
        The exception is for ring structures (any ROIs with holes),
        in which case the inner contours should be clockwise
        '''
        # Worthwhile to compute the ROI volume during this process
        self.volume = 0

        # Populate a dictionary of contours using the slice plane as the key. This simplifies
        # analysis of multiple contours per slice
        contours = {}
        for cntr in self.contours:
            plane = cntr.plane
            if plane not in contours:
                contours[plane] = []
            contours[plane].append(cntr)

        # Evaluate each plane
        slice_thickness = self.get_slice_thickness()
        if slice_thickness is None:
            slice_thickness = 0

        for plane, plane_contours in contours.items():
            paths = [c.get_path() for c in plane_contours]
            contains_path = np.zeros((len(paths), len(paths)))
            for i, p1 in enumerate(paths):
                for j, p2 in enumerate(paths):
                    if i != j:
                        contains_path[i, j] = p1.contains_path(p2)
                    # A path not contained within any other path marks the outer bound of the
                    # binary mask. A path contained within one other path marks an inner boundary
                    # of a ring structure. A path contained within two other paths marks the outer
                    # bound, etc. In essence,
                    #   A path inside an even number of paths (0,2,4,...) is an 'outer' contour
                    #   A path inside an odd number of paths (1,3,5,...) is an 'inner' contour
                    # Outer contours should have a positive area, whereas inner contours should
                    # have a negative area.
            outer_contours = (np.sum(contains_path, axis=0) % 2) == 0
            # print plane, contains_path.flatten(), np.sum(contains_path,axis=0), outer_contours,\
            # [c.get_area() for c in plane_contours]

            for i, cntr in enumerate(plane_contours):
                area = cntr.get_area()

                # Flip the contour data under 2 circumstances:
                #   1. It is an 'outer' contour but the area is negative
                #   2. It is an 'inner' contour but the area is positive
                if (outer_contours[i] and
                        area < 0) or (not outer_contours[i] and area > 0):
                    cntr.data = cntr.data[::-1, :]
                    area = -area
                self.volume += area * slice_thickness

    def get_volume(self):
        '''
        Compute the volume for the current ROI
        '''
        if self.volume is None:
            self.check_contour_directions()
        return self.volume

    def get_mask(self,
                 template=None,
                 size=None,
                 spacing=None,
                 radius=0.0,
                 map_points_to_voxels=False):
        '''
        Get the binary mask for the roi.

        Keyword arguments:
            :template:  image template can be used to specify image meta-data
                (image size, voxel size, etc.).
            :radius:    expansion radius that can be applied to the contour
                to include voxels that are only partially inside the contour.
            :map_points_to_voxels: boolean value.
                If True, contour points are mapped to the nearest mask voxel coordinates
                before generating the path.
        '''
        # In most use cases, will always go in here
        if hasattr(self, 'mask') and self.mask is not None:
            return self.mask

        # TODO: Look at this and figure out when it's useful
        # Initialize the mask image
        mask = image.Mask()
        if template:
            mask.copy_information(template)
        else:
            mask = self.get_mask_information(size=size, spacing=spacing)
        mask.fill_buffer(False, dtype=np.uint8)

        # Check the direction of contour points. Outer contours run counter-clockwise,
        # inner contours run clockwise (volume is subtracted from the mask)
        self.check_contour_directions()

        # Evaluate each contour
        for cntr in self.contours:
            # Let 'l' and 'u' correspond to the lower and upper indices of the contour
            # on the mask
            lowerIdx, _ = mask.transform_physical_point_to_index(
                cntr.min())
            upperIdx, _ = mask.transform_physical_point_to_index(
                cntr.max())
            idx = np.vstack((lowerIdx, upperIdx))
            l, u = idx.min(0), idx.max(0)
            xIndices = np.arange(l[0], u[0] + 1)
            yIndices = np.arange(l[1], u[1] + 1)

            xCoords = mask.origin[0] + xIndices * mask.spacing[0]
            yCoords = mask.origin[1] + yIndices * mask.spacing[1]
            points = np.vstack(np.meshgrid(xCoords, yCoords)).reshape(2, -1).T

            # Determine which points are inside the current contour. Use a contour expansion
            # to ensure that pixels along outer contour paths are added to the mask and
            # pixels along inner contour paths are not subtracted from the mask
            if map_points_to_voxels:
                    # Better estimate Pinnacle binary masks by mapping each contour point
                    # to the center of the nearest voxel
                contour_idx, _ = mask.transform_physical_point_to_index(
                    cntr.data)
                mapped_contour = Contour(
                    mask.transform_index_to_physical_point(contour_idx))
                path = mapped_contour.get_path()
            else:
                path = cntr.get_path()

            pointsInside = path.contains_points(points, radius=radius)
            if len(pointsInside) > 0:
                pointsInside = pointsInside.reshape(len(yIndices), -1)

                # Add the pointsInside to the mask.
                # (Operator ^= is compound assignment for XOR, which
                # is used to remove masked voxels inside ring structures)
                slice_index = int(round(
                    (cntr.plane - mask.origin[2]) / mask.spacing[2]))
                if slice_index < 0 or slice_index >= mask.data.shape[0]:
                    warnings.warn('Slice index out of bounds', Warning)
                mask.data[slice_index, l[1]:(1 + u[1]), l[0]:(
                    1 + u[0])] ^= pointsInside

        voxelVolume = abs(np.prod(mask.spacing))
        self.mask_volume = sum(sum(sum(mask.data))) * voxelVolume
        return mask

    def get_mask_volume(self, edge_voxel_weight=None):
        '''
        Compute the ROI volume from the binary mask

        Keyword arguments:
            :edge_voxel_weight: weight assigned to the voxels on the surface of the mask
        '''
        self.mask_volume = self.mask.get_volume(edge_voxel_weight)
        return self.mask_volume

    def get_mask_information(self, size=None, spacing=None):
        '''
        Compute the origin, size, and shape of the binary mask for the current ROI.
        '''
        mask = image.Mask()

        # Compute the binary mask origin and end coordinates
        roiMin = np.array([float('inf')] * 3)
        roiMax = np.array([-float('inf')] * 3)
        for cntr in self.contours:
            roiMin = np.min([roiMin, cntr.min()], axis=0)
            roiMax = np.max([roiMax, cntr.max()], axis=0)
        mask.origin = roiMin
        mask.end = roiMax

        if size and spacing:
            # Adjust the origin and end to fit the desired size and spacing
            size = np.array(size, dtype=int)
            spacing = np.array(spacing)

            required_size = np.ceil((roiMax - roiMin) / spacing) + 1
            offset = np.array(0.5 * (size - required_size) * spacing)
            mask.origin -= offset
            mask.end += offset
            mask.size = size
            mask.spacing = spacing

        elif spacing:
            # Use desired spacing to compute mask size
            spacing = np.array(spacing)
            mask.size = np.ceil((roiMax - roiMin) / spacing) + 1
            mask.spacing = spacing

        elif size:
            # Use desired size to compute mask spacing
            size = np.array(size)
            mask.spacing = (roiMax - roiMin) / (size - 1)
            mask.size = size
        else:
            # Set size equal to default and compute mask spacing
            defaultSize = [256, 256, len(self.get_contour_planes())]
            mask.size = np.array(defaultSize)
            mask.spacing = [(roiMax[d] - roiMin[d]) / (mask.size[d] - 1)
                            if mask.size[d] > 1 else 1
                            for d in range(mask.dimension)]

        return mask

    def get_mask_edge_voxels(self, exclude_z=False):
        '''
        Return a boolean image where 1's indicate that a voxel is on the mask boundary
        '''
        return self.mask.get_mask_edge_voxels(exclude_z)

    def count_mask_edge_voxels(self, mask=None, exclude_z=False):
        '''
        Compute the number of voxels on the surface of the mask.

        Keyword arguments:
            :mask:      mask to compute over
            :exclude_z: boolean value. If True, only edges in the x-y plane are computed.
        '''
        edge_mask = self.get_mask_edge_voxels(exclude_z)
        return len(edge_mask.data.nonzero()[0])

    def get_edge_mask(self, mask=None):
        '''
        Compute the mask containing voxels only on the surface of the mask.

        Keyword arguments:
            :mask:  mask to compute over
        '''
        # In most use cases, will always go in here
        if hasattr(self, 'mask') and self.mask is not None:
            return self.get_mask_edge_voxels()

        # TODO: Look at this and figure out when it's useful
        if not mask:
            mask = self.get_mask()
        else:
            # Check the direction of contour points. Outer contours run counter-clockwise,
            # inner contours run clockwise (volume is subtracted from the mask)
            self.check_contour_directions()

        edge_mask = image.Image()
        edge_mask.copy_information(mask)
        edge_mask.fill_buffer(0.0)

        for cntr in self.contours:
            # Map the contour data to continuous indices within the mask
            points, _ = mask.transform_physical_point_to_continuous_index(
                cntr.data)
            # With respect to the lower corner of the voxel, not the voxel center
            points = points + 0.5
            indexed_cntr = Contour(points)

            # Interpolate the current contour points at mask voxel edges
            final_points, is_boundary = self.interpolate_contour_at_voxel_edges(
                cntr, mask)

            num_points = len(final_points)
            i = next((idx for idx, x in enumerate(is_boundary)
                      if x), num_points)
            while i < num_points:
                # Get a short list of points representing the following 3 items:
                # 1. The intersection of the contour entering a voxel
                voxel_points = [final_points[i]]
                i += 1
                while is_boundary[i % num_points] == 0:
                    # 2. All contour points inside the voxel
                    voxel_points.append(final_points[i % num_points])
                    i += 1
                # 3. The intersection of the contour leaving a voxel
                voxel_points.append(final_points[i % num_points])

                # Determine the four corners of the current voxel and which of them are
                # inside the current contour. Corners are appended in counter-clockwise order
                min_voxel_point = np.array(voxel_points).min(axis=0)
                lower_corner = [
                    np.floor(min_voxel_point[0]),
                    np.floor(min_voxel_point[1])
                ]
                corners = [
                    list(lower_corner)
                ]  # (Note: make a copy of lower_corners to avoid overwriting later)
                corners.append([corners[0][0] + 1, corners[0][1]])
                corners.append([corners[0][0] + 1, corners[0][1] + 1])
                corners.append([corners[0][0], corners[0][1] + 1])

                corners_inside = indexed_cntr.get_path().contains_points(
                    corners, radius=0.0001)
                corners_inside = [
                    idx for idx, c in enumerate(corners_inside) if c
                ]
                corners = [corners[idx] for idx in corners_inside]

                # If only one corner inside, append to the list of voxel_points
                if len(corners) == 1:
                    voxel_points.append(corners[0])
                # Otherwise, make sure the corners are appended to the list
                #   of voxel_points in counter-clockwise order
                elif len(corners_inside) > 1:
                    # First corner point should always be closest to the last of the voxel_points
                    #   (where the contour exist the voxel)
                    x0, y0 = voxel_points[-1]
                    distances = [(x - x0)**2 + (y - y0)**2
                                 for (x, y) in corners]
                    min_distance_index = next((i
                                               for i, d in enumerate(distances)
                                               if d == min(distances)), None)
                    for idx in range(len(corners)):
                        corner_point = corners[(
                            min_distance_index + idx) % len(corners)]
                        if corner_point not in voxel_points:
                            voxel_points.append(corner_point)

                voxel_points = [[x, y, 0] for (x, y) in voxel_points]
                voxel_contour = Contour(voxel_points)
                area = voxel_contour.get_area()
                edge_mask.data[indexed_cntr.plane, lower_corner[1],
                               lower_corner[0]] += area

        edge_mask.data[edge_mask.data > 1] = 1
        edge_mask.data[edge_mask.data < 0] += 1
        return edge_mask

    def interpolate_contour_at_voxel_edges(self, cntr, mask):
        '''
        Interpolate the current contour points at mask voxel edges.

        Positional arguments:
            :cntr:  contour object
            :mask:  mask object
        '''
        points, inbounds = mask.transform_physical_point_to_continuous_index(
            cntr.data)
        # With respect to the lower corner of the voxel, not the voxel center
        points = points + 0.5

        final_points = []
        i = 0
        num_points = cntr.data.shape[0]
        while i < num_points:
            x0, y0 = points[i, :2]
            if i + 1 < num_points:
                x1, y1 = points[i + 1, :2]
            else:
                x1, y1 = points[0, :2]

            # Compute where the segment from (x0,y0) to (x1,y1) crosses voxel boundaries
            def get_range(a, b):
                if a < b:
                    if a == int(a):
                        a += 1
                    return range(int(np.ceil(a)), int(np.ceil(b)))
                else:
                    if a == int(a):
                        a -= 1
                    return range(int(np.floor(a)), int(np.floor(b)), -1)
                return []

            voxel_edge_intersections = []
            for x in get_range(x0, x1):
                y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
                if [x, y] not in voxel_edge_intersections:
                    voxel_edge_intersections.append([x, y])

            for y in get_range(y0, y1):
                x = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
                if [x, y] not in voxel_edge_intersections:
                    voxel_edge_intersections.append([x, y])

            # Sort voxel boundary intersections by proximity to (x0,y0)
            voxel_edge_intersections = sorted(
                voxel_edge_intersections,
                key=lambda x, y: (x - x0)**2 + (y - y0)**2)

            # Add point0 and the voxel edge intersections to the list of final points. Beware of contour
            # points that lie along voxel edges
            if [x0, y0] not in voxel_edge_intersections:
                final_points.append([x0, y0])
            final_points.extend(voxel_edge_intersections)
            i += 1

        # Compute the points that mark a voxel edge intersection
        i = 0
        num_points = len(final_points)
        is_boundary = []
        while i < num_points:
            x0, y0 = final_points[(i - 1) % num_points]
            x1, y1 = final_points[i]
            x2, y2 = final_points[(i + 1) % num_points]
            # If a point lies on the intersection of the contour with a voxel edge,
            # then the coordinate (x or y) will be an integer (x==int(x)), and the set of
            # previous, current, and subsequent coordinates will either all be
            # ascending (x0<x1<x2) or descending (x2<x1<x0)
            if (x1 == int(x1) and ((x0 < x1 and x1 < x2) or (x2 < x1 and x1 < x0))) or \
               (y1 == int(y1) and ((y0 < y1 and y1 < y2) or (y2 < y1 and y1 < y0))):
                is_boundary.append(1)
            else:
                is_boundary.append(0)
            i += 1

        return final_points, is_boundary

    def get_edge_weighted_mask(self,
                               template=None,
                               size=None,
                               spacing=None,
                               radius=0.0,
                               map_points_to_voxels=False):
        '''
        Computes the binary mask with weighted edge voxels.

        Keyword arguments:
            :template:  image template can be used to specify image meta-data
                (image size, voxel size, etc.).
            :radius:    expansion radius that can be applied to the contour
                to include voxels that are only partially inside the contour.
            :map_points_to_voxels: boolean value. If True, contour points are mapped
                to the nearest mask voxel coordinates before generating the path.
        Returns:
            mask object with weighted edge voxels
        '''
        # Compute the binary mask and edge_mask
        mask = self.get_mask(template, size, spacing, radius,
                             map_points_to_voxels)
        edge_mask = self.get_edge_mask(mask)

        # Initialize the edge-weighted mask
        edge_weighted_mask = image.Mask()
        edge_weighted_mask.copy_information(edge_mask)

        # Update the edge-weighted mask data
        edge_weighted_mask.data = np.array(mask.data).astype(np.float_)
        mask_voxel_indices = edge_mask.data.nonzero()
        edge_weighted_mask.data[mask_voxel_indices] = edge_mask.data[
            mask_voxel_indices]

        return edge_weighted_mask

    def load_binary_mask(self, file, dimX=None, dimY=None, dimZ=None):
        '''
        Load an ROI binary mask from a file

        Positional arguments:
            :file:  file to open
        Keyword arguments:
            :dimX:  length in the X dimension
            :dimY:  length in the Y dimension
            :dimZ:  length in the Z dimension
        '''
        self.mask = image.load_binary_mask(file, dimX, dimY, dimZ)
        return self.mask

    def run_length_encode(self):
        '''
        Returns:
            run-length-encoded string representation of the ROI binary mask
        '''
        self.mask.run_length_encode()

    def run_length_decode(self, runlength, dimZYX):
        '''
        Decode a string into an ROI object

        Positional arguments:
            :runlength: run-length-encoded string
            :dimZYX:    list of dimensions in Z, Y, and X
        Returns
            roi instance of the binary mask representation
        '''
        self.mask = image.run_length_decode(runlength, dimZYX)
        return self.mask

    def compute_edt(self, msk=None, limits=None, verbose=True):
        """
        Compute the Euclidean distance transform for the given ROI binary mask.

        Keyword arguments:
            :msK:       edge mask
            :limits:
        """
        import time
        if msk is None:
            msk = self.mask
        if msk is None:
            return None

        ND = len(msk.data.shape)  # Number of Dimensions
        edt = np.empty_like(msk.data, dtype=np.float)
        edt.fill(np.inf)
        root = np.zeros(msk.data.shape + (ND, ), dtype=np.uint16)

        idx = Index(np.nonzero(msk.data))
        edt[idx] = 0
        root[idx] = idx.array
        counter = 0
        total_voxels = 0
        while idx:
            counter += 1
            total_voxels += idx.array.shape[0]
            t0 = time.clock()
            newidx = None
            if verbose:
                print('Iteration {0}: {1} voxels, {2} total voxels, '.format(
                counter, idx.array.shape[0], total_voxels))
            for dim in range(ND):
                for offset in [-1, 1]:
                    (idx_off, inbounds) = idx.offset(dim, offset, msk)
                    idx_inbounds = idx.apply_mask(inbounds)
                    idx_off = idx_off.apply_mask(inbounds)

                    dist = idx_off.array - root[idx_inbounds]
                    for dim2 in range(ND):
                        dist[:, dim2] *= msk.spacing[dim2]
                    dist = np.sum(np.square(dist), axis=1)

                    update_edt = (dist < edt[idx_off])
                    idx_update = idx_inbounds.apply_mask(update_edt)
                    idx_off = idx_off.apply_mask(update_edt)
                    edt[idx_off] = dist[update_edt]
                    root[idx_off] = root[idx_update]

                    if idx_off.array.size:
                        if newidx is None:
                            newidx = idx_off.array
                        else:
                            newidx = np.vstack((newidx, idx_off.array))
            if newidx is None:
                idx = None
            else:
                unique_idx = np.unique(
                    np.ravel_multi_index(tuple(newidx.T), msk.data.shape))
                idx = Index(np.unravel_index(unique_idx, msk.data.shape))
            if verbose:
                print(time.clock() - t0, 'seconds')
        if verbose:
            print('Total iterations:', counter)
            print('Total voxels:', total_voxels)
        edt_out = image.Image()
        edt_out.copy_information(msk)
        edt_out.set_image(np.sqrt(edt))
        return edt_out


class Index(tuple):
    def __init__(self, tpl):
        tuple.__init__(self, tpl)
        self.array = np.array(np.transpose(tpl))

    def offset(self, dim, offset, img=None):
        idx_offset = list(self)
        idx_offset[dim] = idx_offset[dim] + offset
        if img is not None:
            if offset < 0:
                inbounds = idx_offset[dim] >= 0
            else:
                inbounds = idx_offset[dim] < img.data.shape[dim]
        else:
            inbounds = None
        return (Index(idx_offset), inbounds)

    def apply_mask(self, inbounds):
        return Index(tuple(x[inbounds] for x in list(self)))
