import base64
import pickle
import unittest

from Crypto.Cipher import AES
from oncotools.connect import Database

import oncotools.transform as tf
from oncotools.data_integrity.validator import Validator

class TestMaskIntegrity(unittest.TestCase):
    '''
    Test data integrity validation methods
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

        base_mask = cls.db.regions_of_interest.get_mask(res2)
        # Make one mask that is contiguous
        cont_pts = [[i, j, k]
                    for i in range(10)
                    for j in range(10)
                    for k in range(10)]
        cls.good_mask = tf.general.fill_mask(base_mask, cont_pts)
        # And create one that is discontiguous
        discont_pts = [[i, j, k]
                       for i in range(10)
                       for j in range(10)
                       for k in range(10) if k < 4 or k > 5]
        cls.bad_mask = tf.general.fill_mask(base_mask, discont_pts)

    @classmethod
    def tearDownClass(cls):
        del cls.db
        del cls.good_mask
        del cls.bad_mask

    def test_check_elements(self):
        '''
        Make sure the Feature object has all the required attributes
        '''
        v = Validator()
        elem_list = [
            'mask'
        ]
        self.assertTrue(isinstance(v, Validator))
        for elem in elem_list:
            self.assertTrue(hasattr(v, elem))

    def test_valid_mask_extent(self):
        '''
        Validate contiguousness with extent
        '''
        v = Validator()
        self.assertTrue(v.mask.check_contiguity(self.good_mask, 'extent')[0])

    def test_valid_mask_surface(self):
        '''
        Validate contiguousness with region growing over the surface
        '''
        v = Validator()
        self.assertTrue(v.mask.check_contiguity(self.good_mask, 'surface')[0])

    def test_valid_mask_volume(self):
        '''
        Validate contiguousness with region growing over the volume
        '''
        v = Validator()
        self.assertTrue(v.mask.check_contiguity(self.good_mask, 'volume')[0])

    def test_invalid_mask_extent(self):
        '''
        Validate contiguousness with extent
        '''
        v = Validator()
        self.assertFalse(v.mask.check_contiguity(self.bad_mask, 'extent')[0])

    def test_invalid_mask_surface(self):
        '''
        Validate contiguousness with region growing over the surface
        '''
        v = Validator()
        self.assertFalse(v.mask.check_contiguity(self.bad_mask, 'surface')[0])

    def test_invalid_mask_volume(self):
        '''
        Validate contiguousness with region growing over the volume
        '''
        v = Validator()
        self.assertFalse(v.mask.check_contiguity(self.bad_mask, 'volume')[0])

if __name__ == '__main__':
    unittest.main()
