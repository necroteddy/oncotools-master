import base64
import pickle
import unittest

from Crypto.Cipher import AES
from oncotools.connect import Database

class TestQueryPatientReps(unittest.TestCase):
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

        query = 'SELECT TOP(1) ID, patientID FROM patientRepresentations'
        res = cls.db.run(query)
        cls.patientRepID = res.rows[0][0]        
        cls.patientID = res.rows[0][1]
    
    @classmethod
    def tearDownClass(cls):
        del cls.db

    def test_get_all_patient_reps(self):
        '''
        Get all patient representation IDs
        '''
        res = self.db.patient_representations.get_all_patient_representation_ids()
        self.assertGreater(res.num_rows, 0)
        self.assertEqual(res.num_cols, 2)

    def test_patient_id_LUT(self):
        '''
        Get a LUT of patient representation ID to patient ID
        '''
        res = self.db.patient_representations.get_all_patient_representation_ids()
        myLUT = self.db.patient_representations.get_patient_id_LUT()
        self.assertGreater(len(myLUT.keys()), 0)
        self.assertEqual(res.num_rows, len(myLUT.keys()))

    def test_patient_rep_id_LUT(self):
        myLUT = self.db.patient_representations.get_patient_rep_id_LUT()
        for k in myLUT:
            self.assertTrue(isinstance(myLUT[k], list))

    def test_get_patient_rep(self):
        '''
        Get all patient representation IDs
        '''
        res = self.db.patient_representations.get_patient_representation(self.patientRepID)
        self.assertTrue(isinstance(res, dict))
        fields = [
            'patientRepID',
            'patientID',
            'xStart', 'yStart', 'zStart',
            'xVoxelSize', 'yVoxelSize', 'zVoxelSize',
            'xDimension', 'yDimension', 'zDimension']
        for field in fields:
            self.assertTrue(field in res.keys())

if __name__ == '__main__':
    unittest.main()
