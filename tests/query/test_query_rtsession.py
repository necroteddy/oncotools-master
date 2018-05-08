import base64
import os
import pickle
import unittest

from Crypto.Cipher import AES
from oncotools.connect import Database
from oncotools.data_elements.dose import Dose

class TestQueryRTSession(unittest.TestCase):
    '''
    Test database connection and queries
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

        # Files to delete
        cls.file_path = 'tests/files/'
        cls.to_remove = []
    
    @classmethod
    def tearDownClass(cls):
        del cls.db
        # Clean up files
        for f in cls.to_remove:
            os.remove(f)

    def test_rtsession_ids(self):
        '''
        Get all patient representation IDs
        '''
        res = self.db.radiotherapy_sessions.get_session_ids(self.patientRepID)
        self.assertGreater(res.num_rows, -1)
        self.assertGreater(res.num_cols, 1)

    def test_get_dose_grid(self):
        '''
        Get a dose grid using an RTS ID
        '''
        res = self.db.radiotherapy_sessions.get_session_ids(self.patientRepID)
        dg = self.db.radiotherapy_sessions.get_dose_grid(res.rows[0][0])
        self.assertTrue(isinstance(dg, Dose))

    def test_write_dose_grid(self):
        '''
        Write a dose grid to a file
        '''
        res = self.db.radiotherapy_sessions.get_session_ids(self.patientRepID)
        rtsID = res.rows[0][0]
        testfilename = os.path.join(self.file_path, 'dose_test_1.obo')
        self.to_remove.append(testfilename)
        dg = self.db.radiotherapy_sessions.get_dose_grid(rtsID, output=testfilename)
        self.assertTrue(isinstance(dg, Dose))
        self.assertTrue(os.path.exists(testfilename))

    def test_get_dose(self):
        '''
        Get a dose grids using a patientRepID
        '''
        res = self.db.radiotherapy_sessions.get_dose(self.patientRepID)
        self.assertTrue(isinstance(res, dict))
        for k in res.keys():
            self.assertTrue(isinstance(k, str))

if __name__ == '__main__':
    unittest.main()
