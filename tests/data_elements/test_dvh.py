import base64
import pickle
import unittest
import numpy as np

from oncotools.connect import Database
from oncotools.data_elements.dvh import Dvh

class TestDVH(unittest.TestCase):
    '''
    Test data elements: DVH
    '''

    @classmethod
    def setUpClass(cls):
        # Set up a database connection
        cls.db = Database.from_key('tests/credentials', 'config/credentials.key')

        # Select a patient
        query = 'SELECT TOP(1) ID, patientID FROM patientRepresentations'
        res = cls.db.run(query)
        cls.patientRepID = res.rows[0].ID

        # Get a dose grid for a patient
        res0 = cls.db.radiotherapy_sessions.get_session_ids(cls.patientRepID)
        cls.dg = cls.db.radiotherapy_sessions.get_dose_grid(res0.rows[0][0])

        def roi_query_helper(prepID):
            '''
            Get all ROI's for a patient ID
            '''
            query = '''
                SELECT TOP(1) patientRepID, ID, name
                FROM RegionsOfInterest
                WHERE patientRepID = {}
                ORDER BY name asc
            '''.format(prepID)
            return cls.db.run(query).rows[0]

        # Store patientRepID and name of ROIs with a certain number of occurrences
        res1 = roi_query_helper(cls.patientRepID)

        res2 = cls.db.regions_of_interest.get_id_by_patient_rep_id_name(
            res1.patientRepID, str(res1.name))

        cls.mask = cls.db.regions_of_interest.get_mask(res2)
        # Create a DVH instance
        cls.dvh = Dvh(mask=cls.mask, dose=cls.dg)

    @classmethod
    def tearDownClass(cls):
        del cls.db
        del cls.dvh

    def test_compute_dvh(self):
        '''
        DVH was computed and DoseMask has DVH data
        '''
        self.assertTrue(hasattr(self.dvh, 'data'))
        self.assertTrue(isinstance(self.dvh.data, np.ndarray))
        self.assertEqual(self.dvh.data.shape[1], 2)
        self.assertGreater(self.dvh.data.shape[0], 0)

    def test_dose_to_volume(self):
        '''
        Can get the dose to a volume
        '''
        x = self.dvh.get_dose_to_volume(0.5)
        self.assertLessEqual(x, self.dvh.max_dose)
        self.assertGreaterEqual(x, self.dvh.min_dose)

    def test_dose_to_full_volume(self):
        '''
        Dose to 100% should be the least
        '''
        x = self.dvh.get_dose_to_volume(1)
        self.assertLessEqual(x, self.dvh.max_dose)
        self.assertEqual(x, np.min(self.dvh.data[:, 0]))

    def test_dose_to_zero_volume(self):
        '''
        Dose to 0% should be the most
        '''
        x = self.dvh.get_dose_to_volume(0)
        self.assertGreaterEqual(x, self.dvh.min_dose)
        self.assertEqual(x, np.max(self.dvh.data[:, 0]))

    def test_volume_with_dose(self):
        '''
        Can get the dose to a volume
        '''
        y = self.dvh.get_volume_with_dose(self.dvh.mean_dose)
        self.assertLessEqual(y, 1)
        self.assertGreaterEqual(y, 0)

    def test_volume_with_min_dose(self):
        '''
        Volume with min dose should be 1
        '''
        y = self.dvh.get_volume_with_dose(self.dvh.min_dose)
        self.assertEqual(y, 1)

    def test_volume_with_max_dose(self):
        '''
        Volume with max dose should be 0
        '''
        y = self.dvh.get_volume_with_dose(self.dvh.max_dose)
        self.assertEqual(y, 0)

    def test_volume_with_over_max_dose(self):
        '''
        Volume with over max dose should be 0
        '''
        y = self.dvh.get_volume_with_dose(self.dvh.max_dose+1)
        self.assertEqual(y, 0)

if __name__ == '__main__':
    unittest.main()
