import base64
import pickle
import unittest
import numpy as np

from Crypto.Cipher import AES
from oncotools.connect import Database
from oncotools.data_elements.dose import Dose

class TestDose(unittest.TestCase):
    '''
    Test data elements: Dose
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

        res = cls.db.radiotherapy_sessions.get_session_ids(cls.patientRepID)
        # Normal dose grid
        cls.dg = cls.db.radiotherapy_sessions.get_dose_grid(res.rows[0][0])
        # Scaled dose grid
        cls.dg_scaled = cls.db.radiotherapy_sessions.get_dose_grid(res.rows[0][0])
        cls.dg_scaled.dose_scaling_factor = 0.5

    @classmethod
    def tearDownClass(cls):
        del cls.db
        del cls.dg
        del cls.dg_scaled

    def test_check_elements(self):
        '''
        Make sure the Mask object has all the required attributes
        '''
        elem_list = [
            'data',
            'dose_units',
            'scaled_data',
            'dose_scaling_factor',
            'min_dose',
            'max_dose',
            'mean_dose',
            'std_dose'
        ]
        self.assertTrue(isinstance(self.dg, Dose))
        for elem in elem_list:
            self.assertTrue(hasattr(self.dg, elem))

    def test_get_dose(self):
        '''
        Can get dose
        '''
        dose_data = self.dg.get_dose()
        self.assertTrue(isinstance(dose_data, np.ndarray))

    def test_get_scaled_dose(self):
        '''
        Can get dose after scaling
        '''
        dose_data = self.dg_scaled.get_dose()
        self.assertTrue(isinstance(dose_data, np.ndarray))

    def test_compare_scaled_dose(self):
        '''
        Scaled dose is scaled
        '''
        dose_data0 = self.dg.get_dose()
        dose_data1 = self.dg_scaled.get_dose()
        # Dose should be scaled...
        self.assertTrue(np.all(dose_data0 >= dose_data1))
        # ...but image properties should be the same
        fields = ['origin', 'end', 'spacing', 'dimension']
        for f in fields:
            self.assertTrue(np.all(getattr(self.dg, f) == getattr(self.dg_scaled, f)))

    def test_dose_stats(self):
        '''
        Can access dose statistics properties
        '''
        dose_min = self.dg.min
        dose_max = self.dg.max
        dose_mean = self.dg.mean
        dose_std = self.dg.std
        self.assertLessEqual(dose_min, dose_max)
        self.assertLessEqual(dose_min, dose_mean)
        self.assertGreaterEqual(dose_max, dose_mean)
        self.assertGreaterEqual(dose_std, 0)

    def test_copy_info(self):
        '''
        Copy information into a new dose grid
        '''
        new_dg = Dose()
        new_dg.copy_information(self.dg)
        fields = ['min', 'max', 'mean', 'std']
        for f in fields:
            self.assertEqual(getattr(new_dg, f), getattr(self.dg, f))

if __name__ == '__main__':
    unittest.main()
