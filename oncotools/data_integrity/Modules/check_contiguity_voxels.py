import random
import numpy as np
from scipy.spatial import KDTree

class check_contiguity_voxels(object):
    def __init__(self):
        self.name = "check_contiguity_voxels(mask, surface)"
        self.function = "Check that a mask is contiguous using region neighbor-crawling technique. \nPositional arguments: \n\t:mask:  mask object \n\nKeyword arguments:\n\t:surface:   (default=True) If true, use the surface mask, else use the volume mask"

    def name(self):
        return self.name

    def name2():
        return "check_contiguity_voxels(mask, volume)"

    def function(self):
        return self.function

    def description(self):
        return {self.name: self.function, self.name2(): self.function}

    #def check_integrity(self, patient, surface=True):
    def check_integrity(self, mask, surface=True):
        '''
        Check that a mask is contiguous using region neighbor-crawling technique.

        Positional arguments:
            :mask:  mask object

        Keyword arguments:
            :surface:   (default=True) If true, use the surface mask, else use the volume mask
        '''

        def find_neighbors(kd, node_idx, node_val, r):
            # HELPER FUNCTION: Find all neighbors (and remove starting node fron list)
            neighbors = kd.query_ball_point(node_val, r)
            if node_idx in neighbors:
                neighbors.remove(node_idx)
            return neighbors

        # Get the nonzero indices
        nz = mask.get_mask_edge_voxels().data.nonzero() if surface is True else mask.data.nonzero()
        # Transpose and horizontally stack the rows
        indices = np.fliplr(np.transpose(np.asarray(nz)))

        # Construct a KDTree of the points
        kd = KDTree(indices)
        # Search radius
        rad = np.sqrt(3)

        # Select a random point in the point cloud
        idx = random.randint(0, len(indices))
        node = indices[idx]

        # List of visited points
        visited = [idx]
        # Find neighbors for starting point
        neighbors = find_neighbors(kd, idx, node, rad)
        # Add neighbors to visited
        visited = list(set(visited + neighbors))

        # Crawl over all neighbors
        while len(neighbors) > 0:
            neighbors = [
                find_neighbors(kd, n, indices[n], rad) for n in neighbors
            ]
            # Flatten the list and remove duplicates
            neighbors = list(
                set([
                    n for sublist in neighbors for n in sublist
                    if n not in visited
                ]))
            # Add new neighbors to list of visited points
            visited = list(set(visited + neighbors))

        # Valid if all voxels were reached
        valid = len(visited) == len(indices)
        message = 'Mask is {}contiguous'.format(''
                                                if valid is True else 'not ')
        if valid == False:
            errortype = "error found by check_contiguity_voxels()"
        else:
            errortype = None

        return (valid, message, errortype)
