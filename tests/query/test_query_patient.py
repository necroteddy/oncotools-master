import base64
import pickle
import unittest

from oncotools.connect import Database

class TestQueryPatients(unittest.TestCase):
    '''
    Test database connection and queries
    '''

    @classmethod
    def setUpClass(cls):
        # Set up a database connection
        cls.db = Database.from_key('tests/credentials', 'config/credentials.key')

        query = 'SELECT TOP(1) patientID FROM Patients'
        res = cls.db.run(query)
        cls.patientID = res.rows[0].patientID
    
    @classmethod
    def tearDownClass(cls):
        del cls.db

    def test_get_all_patient_ids(self):
        '''
        Get all patient representation IDs
        '''
        res = self.db.patients.get_all_patient_ids()
        self.assertGreater(len(res), 0)

    def test_get_all_patient_info(self):
        '''
        Get all patient representation IDs
        '''
        res = self.db.patients.get_patient_info()
        self.assertGreater(res.num_rows, 0)
        self.assertEqual(res.num_cols, 4)

    def test_get_patient_info(self):
        '''
        Get all patient representation IDs
        '''
        res = self.db.patients.get_patient_info(patientID=self.patientID)
        self.assertEqual(res.num_rows, 1)
        self.assertEqual(res.num_cols, 4)

if __name__ == '__main__':
    unittest.main()
