import base64
import pickle
import unittest

from oncotools.connect import Database
from oncotools.data_elements.image import Mask
from oncotools.data_elements.roi import Roi


class TestRoi(unittest.TestCase):
    '''
    Test data elements: ROI
    '''

    @classmethod
    def setUpClass(cls):
        # Set up a database connection
        cls.db = Database.from_key('tests/credentials', 'config/credentials.key')

        # Select a patient
        query = 'SELECT TOP(1) ID, patientID FROM patientRepresentations'
        res = cls.db.run(query)
        cls.patientRepID = res.rows[0].ID
        cls.patientID = res.rows[0].patientID

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
            res0.patientRepID, str(res0.name))
        cls.test_roi = cls.db.regions_of_interest.get_roi(res)

    @classmethod
    def tearDownClass(cls):
        del cls.db

    def test_check_elements(self):
        '''
        Make sure the Mask object has all the required attributes
        '''
        elem_list = [
            'name',
            'header',
            'volume',
            'mask_volume',
            'contours',
            'mask',
        ]
        self.assertTrue(isinstance(self.test_roi, Roi))
        for elem in elem_list:
            self.assertTrue(hasattr(self.test_roi, elem))

    def test_get_mask(self):
        '''
        Get a Mask from an ROI
        '''
        mask = self.test_roi.get_mask()
        self.assertTrue(isinstance(mask, Mask))

    def test_get_volume(self):
        '''
        Get the volume of a mask
        '''
        roi_volume = self.test_roi.get_volume()
        self.assertGreaterEqual(roi_volume, 0)

    def test_get_mask_information(self):
        '''
        Get a Mask from an ROI
        '''
        mask = self.test_roi.get_mask_information()
        self.assertTrue(isinstance(mask, Mask))

    def test_get_mask_edge_voxels(self):
        '''
        Get the edge voxels for a mask
        '''
        edge_mask = self.test_roi.get_mask_edge_voxels()
        edge_count = self.test_roi.count_mask_edge_voxels()
        self.assertEqual(edge_count, len(edge_mask.data.nonzero()[0]))

    def test_get_mask_edge_voxels_excludez(self):
        '''
        Get the edge voxels for a mask
        '''
        edge_count0 = self.test_roi.count_mask_edge_voxels()
        edge_count1 = self.test_roi.count_mask_edge_voxels(exclude_z=True)
        self.assertGreaterEqual(edge_count0, edge_count1)


if __name__ == '__main__':
    unittest.main()