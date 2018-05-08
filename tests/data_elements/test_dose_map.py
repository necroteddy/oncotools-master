import base64
import pickle
import unittest
import numpy as np

from Crypto.Cipher import AES
from oncotools.connect import Database
from oncotools.data_elements.dose_map import DoseMask

class TestDoseMap(unittest.TestCase):
    '''
    Test data elements: DoseMask
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
            res1[0], str(res1[2]))

        cls.mask = cls.db.regions_of_interest.get_mask(res2)
        # Create a dose mask
        cls.dm = DoseMask(cls.mask, cls.dg)


    @classmethod
    def tearDownClass(cls):
        del cls.db
        del cls.dg
        del cls.mask

    def test_check_elements(self):
        '''
        Make sure the Mask object has all the required attributes
        '''
        elem_list = [
            'mask',
            'dose',
            'data',
            'min_dose',
            'max_dose',
            'mean_dose',
            'std_dose',
            'fraction_outside_dosegrid'
        ]
        self.assertTrue(isinstance(self.dm, DoseMask))
        for elem in elem_list:
            self.assertTrue(hasattr(self.dm, elem))

    def test_dose_mask_statistics(self):
        '''
        Check the dose statistics
        '''
        nonzero_data = self.dm.data[np.nonzero(self.dm.data)]
        self.assertEqual(self.dm.min_dose, nonzero_data.min())
        self.assertEqual(self.dm.max_dose, nonzero_data.max())
        self.assertEqual(self.dm.mean_dose, nonzero_data.mean())
        self.assertEqual(self.dm.std_dose, nonzero_data.std())

    def test_compute_dvh(self):
        '''
        DVH was computed and DoseMask has DVH data
        '''
        self.assertTrue(hasattr(self.dm, 'dvh_data'))
        self.assertTrue(isinstance(self.dm.dvh_data, np.ndarray))
        self.assertEqual(self.dm.dvh_data.shape[1], 2)
        self.assertGreater(self.dm.dvh_data.shape[0], 0)

    def test_dose_to_volume(self):
        '''
        Can get the dose to a volume
        '''
        x = self.dm.get_dose_to_volume(0.5)
        self.assertLessEqual(x, self.dm.max_dose)
        self.assertGreaterEqual(x, self.dm.min_dose)

    def test_dose_to_full_volume(self):
        '''
        Dose to 100% should be the least
        '''
        x = self.dm.get_dose_to_volume(1)
        self.assertLessEqual(x, self.dm.max_dose)
        self.assertEqual(x, np.min(self.dm.dvh_data[:, 0]))

    def test_dose_to_zero_volume(self):
        '''
        Dose to 0% should be the most
        '''
        x = self.dm.get_dose_to_volume(0)
        self.assertGreaterEqual(x, self.dm.min_dose)
        self.assertEqual(x, np.max(self.dm.dvh_data[:, 0]))

    def test_volume_with_dose(self):
        '''
        Can get the dose to a volume
        '''
        y = self.dm.get_volume_with_dose(self.dm.mean_dose)
        self.assertLessEqual(y, 1)
        self.assertGreaterEqual(y, 0)

    def test_volume_with_min_dose(self):
        '''
        Volume with min dose should be 1
        '''
        y = self.dm.get_volume_with_dose(self.dm.min_dose)
        self.assertEqual(y, 1)

    def test_volume_with_max_dose(self):
        '''
        Volume with max dose should be 0
        '''
        y = self.dm.get_volume_with_dose(self.dm.max_dose)
        self.assertEqual(y, 0)

    def test_volume_with_over_max_dose(self):
        '''
        Volume with over max dose should be 0
        '''
        y = self.dm.get_volume_with_dose(self.dm.max_dose+1)
        self.assertEqual(y, 0)

if __name__ == '__main__':
    unittest.main()
