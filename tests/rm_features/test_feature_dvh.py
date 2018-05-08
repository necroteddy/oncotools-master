import base64
import pickle
import unittest
import numpy as np

from Crypto.Cipher import AES
from oncotools.connect import Database
from oncotools.data_elements.image import Mask
from oncotools.data_elements.dose_map import DoseMask
from oncotools.radio_morphology.dvh_feature import DVHFeature
from schema import Schema, And, SchemaError

class TestDVHFeature(unittest.TestCase):
    '''
    Test RM features: DVH Feature
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

    @classmethod
    def tearDownClass(cls):
        del cls.db
        del cls.dg
        del cls.mask

    def test_check_elements(self):
        '''
        Make sure the Feature object has all the required attributes
        '''
        feat = DVHFeature('test')
        elem_list = [
            'id',
            'type',
            'output',
            'dose',
            'mask',
            'feature_mask',
            'feature_dosemask',
            'loaded'
        ]
        self.assertTrue(isinstance(feat, DVHFeature))
        for elem in elem_list:
            self.assertTrue(hasattr(feat, elem))

    def test_create_with_featuretype(self):
        '''
        Can specify a certain feature type
        '''
        feat = DVHFeature('test', feature_type='sample_type')
        self.assertFalse(feat.loaded)
        self.assertEqual(feat.type, 'sample_type')

    def test_process_before_load(self):
        '''
        Cannot process before loading data
        '''
        feat = DVHFeature('test')
        self.assertFalse(feat.loaded)
        self.assertRaises(ValueError, lambda: feat.process())

    def test_values_before_load(self):
        '''
        Cannot get values before loading data
        '''
        feat = DVHFeature('test')
        self.assertRaises(ValueError, lambda: feat.values)

    def test_create_feature_with_values(self):
        '''
        Can initialize with mask and dose grid
        '''
        feat = DVHFeature('test', mask=self.mask, dose=self.dg)
        self.assertTrue(feat.mask is not None)
        self.assertTrue(feat.dose is not None)
        self.assertTrue(feat.loaded)

    def test_load_feature(self):
        '''
        Can initialize with mask and dose grid
        '''
        feat = DVHFeature('test')
        feat.load(self.mask, self.dg)
        self.assertTrue(feat.mask is not None)
        self.assertTrue(feat.dose is not None)
        self.assertTrue(feat.loaded)

    def test_process_mask(self):
        '''
        DVH feature class has trivial mask processing
        '''
        feat = DVHFeature('test', mask=self.mask, dose=self.dg)
        feat.process_mask()
        self.assertTrue(isinstance(feat.feature_mask, Mask))

    def test_process_dose(self):
        '''
        DVH feature class computes mean, min, max, and dvh
        '''
        feat = DVHFeature('test', mask=self.mask, dose=self.dg)
        feat.process_dose()
        self.assertTrue(isinstance(feat.feature_dosemask, DoseMask))

    def test_process(self):
        '''
        Process values for DVHFeature
        '''
        # Set up a schema validator
        dvh_schema = {
            'mean': And(float),
            'min': And(float),
            'max': And(float),
            'dvh': And(np.ndarray)
        }
        validator = Schema(dvh_schema)
        # Compute features
        feat = DVHFeature('test', mask=self.mask, dose=self.dg)
        output = feat.process()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(output) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_process_with_dvh(self):
        '''
        Can list specific DVH values to compute
        '''
        # Set up a schema validator
        dvh_schema = {
            'mean': float,
            'min': float,
            'max': float,
            'dvh': And(np.ndarray, lambda x: x.shape == (6, 2))
        }
        validator = Schema(dvh_schema)
        # Compute features
        dvh_vals = [0, 0.2, 0.4, 0.6, 0.8, 1]
        feat = DVHFeature('test', mask=self.mask, dose=self.dg, dvh=dvh_vals)
        output = feat.process()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(output) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')


if __name__ == '__main__':
    unittest.main()
