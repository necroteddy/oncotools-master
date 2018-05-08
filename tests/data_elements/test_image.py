import base64
import pickle
import unittest
import numpy as np

from Crypto.Cipher import AES
from oncotools.connect import Database
from oncotools.data_elements.image import Mask
from copy import deepcopy

class TestImage(unittest.TestCase):
    '''
    Test data elements: Image and Mask
    '''

    @classmethod
    def setUpClass(cls):
        # Read the secret key and set up the cipher
        fhandle = open('config/credentials.key', 'r')
        secret_key = fhandle.readline().strip()
        fhandle.close()
        cipher = AES.new(secret_key, AES.MODE_ECB)
        # Read the credentials file and decrypt the data
        encoded = pickle.load(open('tests/credentials', 'rb'))
        decoded = cipher.decrypt(base64.b64decode(encoded))
        data = decoded.strip().split(', ')
        cls.db = Database(db='OncospaceHeadNeck', us=data[0], pw=data[1])

        # Select a patient
        query = 'SELECT TOP(1) ID, patientID FROM patientRepresentations'
        res = cls.db.run(query)
        cls.patientRepID = res.rows[0][0]
        cls.patientID = res.rows[0][1]

        def roi_query_helper(count):
            '''
            Get a patientRepID and ROI name that appears a certain number of times
            '''
            query = '''
                WITH query1 as (
                    SELECT patientRepID, name, count(*) as count
                    FROM RegionsOfInterest
                    GROUP BY name, patientRepID
                )
                SELECT TOP(1) * FROM query1 WHERE count = {}
            '''.format(count)
            res = cls.db.run(query)
            return res.rows[0]

        # Store patientRepID and name of ROIs with a certain number of occurrences
        res0 = roi_query_helper(1)

        res = cls.db.regions_of_interest.get_id_by_patient_rep_id_name(
            res0[0], str(res0[1]))
        cls.test_mask = cls.db.regions_of_interest.get_mask(res)

    @classmethod
    def tearDownClass(cls):
        del cls.db

    def test_check_elements(self):
        '''
        Make sure the Mask object has all the required attributes
        '''
        elem_list = [
            'dimension',
            'origin',
            'end',
            'index',
            'size',
            'spacing',
            'direction',
            'data'
        ]
        self.assertTrue(isinstance(self.test_mask, Mask))
        for elem in elem_list:
            self.assertTrue(hasattr(self.test_mask, elem))

    def test_com(self):
        '''
        Has center of mass property
        '''
        data_size = self.test_mask.get_size()
        data_com = self.test_mask.center_of_mass
        self.assertTrue(np.all(data_com <= data_size))

    def test_set_data(self):
        '''
        Set the data in a mask using X,Y,Z indices
        '''
        temp_mask = deepcopy(self.test_mask)
        pts = [[0, 0, 0], [1, 1, 1], [2, 2, 2]]
        temp_mask.set_data_with_indices(pts)
        self.assertEqual(len(temp_mask.data.nonzero()[0]), 3)

    def test_get_image(self):
        '''
        Can access data
        '''
        self.assertTrue(isinstance(self.test_mask.get_image(), np.ndarray))

    def test_update_end(self):
        '''
        Compute the end of the image
        '''
        end0 = self.test_mask.get_end()
        self.test_mask.update_end()
        self.assertTrue(np.all(self.test_mask.get_end() == end0))

    def test_transform_idx_to_pt(self):
        '''
        Get physical coordinates from the voxel index
        '''
        data_com = self.test_mask.center_of_mass
        data_pt = self.test_mask.transform_index_to_physical_point(data_com)
        self.assertTrue(np.all(data_pt >= self.test_mask.origin))
        self.assertTrue(np.all(data_pt <= self.test_mask.end))

    def test_transform_idxs_to_pts(self):
        '''
        Get physical coordinates from the voxel index.
        Can specify an N x dim array of points
        '''
        data_com = self.test_mask.center_of_mass
        data_com = np.vstack([data_com, data_com])
        data_pts = self.test_mask.transform_index_to_physical_point(data_com)
        self.assertTrue(np.all(data_pts[0] == data_pts[1]))
        for data_pt in data_pts:
            self.assertTrue(np.all(data_pt >= self.test_mask.origin))
            self.assertTrue(np.all(data_pt <= self.test_mask.end))

    def test_transform_pt_to_idx(self):
        '''
        Get voxel index from physical coordinates
        '''
        data_com = self.test_mask.center_of_mass
        data_pt = self.test_mask.transform_index_to_physical_point(data_com)
        com_idx, _ = self.test_mask.transform_physical_point_to_index(
            data_pt
        )
        self.assertTrue(np.all(com_idx >= self.test_mask.get_index()))
        self.assertTrue(np.all(com_idx <= self.test_mask.get_size()))

    def test_transform_pts_to_idxs(self):
        '''
        Get voxel index from physical coordinates
        Can specify an N x dim array of points
        '''
        data_com = self.test_mask.center_of_mass
        data_com = np.vstack([data_com, data_com])
        data_pt = self.test_mask.transform_index_to_physical_point(data_com)
        com_idxs, _ = self.test_mask.transform_physical_point_to_index(
            data_pt
        )
        self.assertTrue(np.all(com_idxs[0] == com_idxs[1]))
        for com_idx in com_idxs:
            self.assertTrue(np.all(com_idx >= self.test_mask.get_index()))
            self.assertTrue(np.all(com_idx <= self.test_mask.get_size()))

    def test_transform_to_point_cloud(self):
        '''
        Transform image to point cloud
        '''
        pt_cloud = self.test_mask.transform_to_point_cloud()
        self.assertTrue(isinstance(pt_cloud, np.ndarray))

    def test_get_mask_edge_voxels(self):
        '''
        Get a mask's edge voxels
        '''
        edge_mask = self.test_mask.get_mask_edge_voxels()
        edge_nonzero = np.nonzero(edge_mask.data)
        len_edge = len(edge_nonzero[0])
        mask_nonzero = np.nonzero(self.test_mask.data)
        len_mask = len(mask_nonzero[0])
        self.assertGreaterEqual(len_mask, len_edge)

    def test_get_lower_bound(self):
        '''
        Get a mask's lower bound
        '''
        lb = self.test_mask.lower_bound
        data_com = self.test_mask.center_of_mass
        self.assertTrue(np.all(lb <= data_com))

    def test_get_upper_bound(self):
        '''
        Get a mask's upper bound
        '''
        ub = self.test_mask.upper_bound
        data_com = self.test_mask.center_of_mass
        self.assertTrue(np.all(ub >= data_com))

    def test_get_bounds(self):
        '''
        Get lower and upper bounds
        '''
        (lb, ub) = self.test_mask.bounds
        data_com = self.test_mask.center_of_mass
        self.assertTrue(np.all(lb <= data_com))
        self.assertTrue(np.all(ub >= data_com))

    def test_get_volume(self):
        '''
        Get the volume of a mask
        '''
        mask_vol = self.test_mask.get_volume()
        self.assertGreaterEqual(mask_vol, 0)

    def test_get_volume_weight_edges(self):
        '''
        Get the volume of a mask.
        Weight the edges of the mask.
        '''
        mask_vol0 = self.test_mask.get_volume()
        mask_vol1 = self.test_mask.get_volume(edge_voxel_weight=0.5)
        self.assertGreaterEqual(mask_vol0, mask_vol1)


if __name__ == '__main__':
    unittest.main()
