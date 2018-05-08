import base64
import pickle
import unittest
import numpy as np

from Crypto.Cipher import AES
from oncotools.connect import Database
from oncotools.data_elements.image import Mask
from oncotools.data_elements.dose_map import DoseMask
from oncotools.radio_morphology.octant_shells_feature import OctantShellsFeature
from schema import Schema, And, SchemaError

class TestOctantShellsFeature(unittest.TestCase):
    '''
    Test RM features: Octant-Shells feature
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
        feat = OctantShellsFeature('test')
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
        self.assertTrue(isinstance(feat, OctantShellsFeature))
        for elem in elem_list:
            self.assertTrue(hasattr(feat, elem))

    def test_create_with_featuretype(self):
        '''
        Can specify a certain feature type
        '''
        feat = OctantShellsFeature('test', feature_type='sample_type')
        self.assertFalse(feat.loaded)
        self.assertEqual(feat.type, 'sample_type')

    def test_create_with_expansions(self):
        '''
        Can specify a certain feature type
        '''
        feat = OctantShellsFeature('test', expand=0.2)
        self.assertEqual(feat.expansions, 0.2)

    def test_create_with_contractions(self):
        '''
        Can specify a certain feature type
        '''
        feat = OctantShellsFeature('test', contract=0.2)
        self.assertEqual(feat.contractions, 0.2)

    def test_create_with_expansions_contractions(self):
        '''
        Can specify a certain feature type
        '''
        feat = OctantShellsFeature('test', expand=0.2, contract=0.3)
        self.assertEqual(feat.expansions, 0.2)
        self.assertEqual(feat.contractions, 0.3)

    def test_process_before_load(self):
        '''
        Cannot process before loading data
        '''
        feat = OctantShellsFeature('test')
        self.assertFalse(feat.loaded)
        self.assertRaises(ValueError, lambda: feat.process())

    def test_values_before_load(self):
        '''
        Cannot get values before loading data
        '''
        feat = OctantShellsFeature('test')
        self.assertRaises(ValueError, lambda: feat.values)

    def test_create_feature_with_values(self):
        '''
        Can initialize with mask and dose grid
        '''
        feat = OctantShellsFeature('test', mask=self.mask, dose=self.dg)
        self.assertTrue(feat.mask is not None)
        self.assertTrue(feat.dose is not None)
        self.assertTrue(feat.loaded)

    def test_load_feature(self):
        '''
        Can initialize with mask and dose grid
        '''
        feat = OctantShellsFeature('test')
        feat.load(self.mask, self.dg)
        self.assertTrue(feat.mask is not None)
        self.assertTrue(feat.dose is not None)
        self.assertTrue(feat.loaded)

    def test_process_mask(self):
        '''
        DVH feature class has trivial mask processing
        '''
        v = Schema([Mask])
        feat = OctantShellsFeature('test', mask=self.mask, dose=self.dg)
        output = feat.process_mask()
        try:
            self.assertTrue(v.validate(output) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_process_dose(self):
        '''
        DVH feature class computes mean, min, max, and dvh
        '''
        v = Schema([DoseMask])
        feat = OctantShellsFeature('test', mask=self.mask, dose=self.dg)
        output = feat.process_dose()
        try:
            self.assertTrue(v.validate(output) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def __helper_test_process(self, exp, cont):
        '''
        Helper method to validate slice feature
        '''
        if not isinstance(exp, list):
            exp = [exp]
        if not isinstance(cont, list):
            cont = [cont]

        # Create a schema validator
        n = 8 * (len(exp) + len(cont) + 1)
        com_schema = {
            'bounds': And([str], lambda x: len(x) == n),
            'mean': And([float], lambda x: len(x) == n),
            'min': And([float], lambda x: len(x) == n),
            'max': And([float], lambda x: len(x) == n),
            'dvh': And([np.ndarray], lambda x: len(x) == n)
        }
        validator = Schema(com_schema)

        # Compute features
        feat = OctantShellsFeature('test', mask=self.mask, dose=self.dg,
                                   expand=exp, contract=cont)
        output = feat.process()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(output) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_process_1(self):
        '''
        Process values for OctantShellsFeature
        '''
        return self.__helper_test_process(0.2, [])

    def test_process_2(self):
        '''
        Process values for OctantShellsFeature
        '''
        return self.__helper_test_process([], 0.1)

    def test_process_with_dvh(self):
        '''
        Can list specific DVH values to compute
        '''
        # Set up a schema validator
        com_schema = {
            'bounds': And([str], lambda x: len(x) == 8),
            'mean': And([float], lambda x: len(x) == 8),
            'min': And([float], lambda x: len(x) == 8),
            'max': And([float], lambda x: len(x) == 8),
            'dvh': And([np.ndarray],
                       lambda x: np.all([d.shape == (6, 2) for d in x]),
                       lambda x: len(x) == 8)
        }
        validator = Schema(com_schema)
        # Compute features
        dvh_vals = [0, 0.2, 0.4, 0.6, 0.8, 1]
        feat = OctantShellsFeature('test', mask=self.mask, dose=self.dg, dvh=dvh_vals)
        output = feat.process()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(output) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

if __name__ == '__main__':
    unittest.main()
