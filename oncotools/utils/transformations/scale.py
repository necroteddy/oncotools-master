'''
This module contains methods for the transformations module.
'''

from copy import deepcopy
import numpy as np

class ScaleTransform(object):
    '''
    Scaling transformations
    '''

    def __expand_contract_helper(self, msk, expansion):
        '''
        Expand the binary mask surface by the given expansion in physical units (e.g., mm, cm, ...)

        Note that all expansions should be positive values!

        Positional arguments:
            :msk:       mask to transform
            :expansion: float or list of floats defining the expansion

        Note: Expansion may be given as:
            - A single number:       uniform expansion in all dimensions
            - A list of 1 number:    uniform expansion in all dimensions
            - A list of 3 numbers:   expansion in x, y, and z, respectively
            - A list of 6 numbers:   expansion in -x, +x, -y, +y, -z, and +z, respectively
        '''
        # Process the expansion. Convert to negative (n) and positive (p) x, y, and z
        if isinstance(expansion, str):
            expansion = float(expansion)

        try:
            n_exp = len(expansion)
        except:
            expansion = [expansion]
            n_exp = 1

        if any([e < 0 for e in expansion]):
            raise TypeError('Expansions and contractions cannot be negative')

        if n_exp == 1:
            nx = px = ny = py = nz = pz = float(expansion[0])
        elif n_exp == 3:
            nx = px = float(expansion[0])
            ny = py = float(expansion[1])
            nz = pz = float(expansion[2])
        elif n_exp == 6:
            nx, px, ny, py, nz, pz = [float(e) for e in expansion]
        else:
            raise TypeError('Invalid expansion: ' + str(expansion))

        # Convert physical expansions to voxel expansions
        nix = int(round(nx / msk.spacing[0]))
        pix = int(round(px / msk.spacing[0]))
        niy = int(round(ny / msk.spacing[1]))
        piy = int(round(py / msk.spacing[1]))
        niz = int(round(nz / msk.spacing[2]))
        piz = int(round(pz / msk.spacing[2]))

        # Determine the indices of all neighboring voxels within the bounds of the voxel expansions
        shape = (niz + piz + 1, niy + piy + 1, nix + pix + 1)
        kernel = np.zeros(shape, dtype=bool)
        for iz in range(-niz, piz + 1):
            for iy in range(-niy, piy + 1):
                for ix in range(-nix, pix + 1):
                    # For a voxel to be inside the expansion surface, do NOT assume
                    # that the expansion surface must contain the voxel center. Instead,
                    # assume that the expansion surface overlaps the ellipse positioned
                    # at the center of the voxel having radii equal to 1/4 the voxel size.
                    if ix < 0:
                        x = nx + msk.spacing[0] / 4
                    else:
                        x = px + msk.spacing[0] / 4
                    if iy < 0:
                        y = ny + msk.spacing[1] / 4
                    else:
                        y = py + msk.spacing[1] / 4
                    if iz < 2:
                        z = nz + msk.spacing[2] / 4
                    else:
                        z = pz + msk.spacing[2] / 4

                    sum_of_squares = 0.0
                    if x != 0:
                        sum_of_squares += (ix * msk.spacing[0] / x)**2
                    if y != 0:
                        sum_of_squares += (iy * msk.spacing[1] / y)**2
                    if z != 0:
                        sum_of_squares += (iz * msk.spacing[2] / z)**2
                    if sum_of_squares <= 1:
                        kernel[iz + niz, iy + niy, ix + nix] = 1

        expansion_voxels = np.transpose(np.nonzero(kernel))
        expansion_voxels[:, 0] -= niz
        expansion_voxels[:, 1] -= niy
        expansion_voxels[:, 2] -= nix

        # Apply expansion voxels to mask surface
        expansion_mask = msk.get_mask_edge_voxels(exclude_z=False)
        expansion_mask_idx = np.transpose(np.nonzero(expansion_mask.data))
        for i in range(expansion_mask_idx.shape[0]):
            new_mask_idx = expansion_mask_idx[i, :] + expansion_voxels
            in_bounds = np.logical_and(
                new_mask_idx[:, 0] >= 0,
                np.logical_and(
                    new_mask_idx[:, 0] < msk.size[2],
                    np.logical_and(
                        new_mask_idx[:, 1] >= 0,
                        np.logical_and(
                            new_mask_idx[:, 1] < msk.size[1],
                            np.logical_and(new_mask_idx[:, 2] >= 0,
                                        new_mask_idx[:, 2] < msk.size[0])))))
            z, y, x = np.transpose(new_mask_idx[in_bounds, :])
            expansion_mask.data[z, y, x] = 1
        return expansion_mask


    def expand(self, msk, expansion):
        '''
        Expand the binary mask surface by the given expansion in physical units (e.g., mm, cm, ...)

        Note that all expansions should be positive values!

        Positional arguments:
            :msk:       mask to transform
            :expansion: float or list of floats defining the expansion

        Note: Expansion may be given as:
            - A single number:       uniform expansion in all dimensions
            - A list of 1 number:    uniform expansion in all dimensions
            - A list of 3 numbers:   expansion in x, y, and z, respectively
            - A list of 6 numbers:   expansion in -x, +x, -y, +y, -z, and +z, respectively
        '''
        expansion_mask = self.__expand_contract_helper(deepcopy(msk), expansion)
        expansion_mask.data = np.logical_or(expansion_mask.data, msk.data)
        return expansion_mask


    def contract(self, msk, contraction):
        '''
        Contract the binary mask by the given parameters in physical units (e.g., mm, cm, ...)

        Positional arguments:
            :msk:           mask to transform
            :contraction:   float or list of floats defining the contraction

        Note: Contraction may be given as:
            - A single number:       uniform contraction in all dimensions
            - A list of 1 number:    uniform contraction in all dimensions
            - A list of 3 numbers:   contraction in x, y, and z, respectively
            - A list of 6 numbers:   contraction in -x, +x, -y, +y, -z, and +z, respectively
        '''
        contraction_mask = self.__expand_contract_helper(deepcopy(msk), contraction)
        contraction_mask.data = np.logical_and(msk.data, np.logical_not(contraction_mask.data))
        return contraction_mask


    def shells(self, msk, expansions=[], contractions=[]):
        '''
        Create shells from a list of contractions and expansions.

        Positional arguments:
            :msk:   binary mask to contract to create shells
        Keyword arguments:
            :cts:   list of contractions
            :exp:   list of expansions
        Returns:
            - List of expansion and contraction factors, and
            - List of masks representing the shells, where each shell sits inside the previous.
            The index of each mask corresponds to the index of each expansion/contraction factor
        '''
        orig = deepcopy(msk)
        # Order the expansions and contractions
        exp = deepcopy(expansions)
        cts = deepcopy(contractions)
        exp.sort(reverse=True)
        cts.sort(reverse=False)
        # List of expansion and contraction factors defining the shells
        # bounds = deepcopy(exp)
        bounds = ["+" + str(e) for e in exp]
        bounds.extend(["+0.0"])
        bounds.extend(["-" + str(c) for c in cts])

        # Create expanded and contracted masks
        exps = [self.expand(orig, e) for e in exp]
        cons = [self.contract(orig, c) for c in cts]
        # Create a list of all expanded and contracted masks
        shls = deepcopy(exps)
        shls.extend([orig])
        shls.extend(cons)

        # Create shells from the expanded and contracted masks
        for idx, s in enumerate(shls):
            if idx < len(shls) - 1:
                s.data = np.logical_and(s.data, np.logical_not(shls[idx + 1].data))

        return bounds, shls
