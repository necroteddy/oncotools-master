import base64
import pickle
import unittest
import numpy as np

from oncotools.connect import Database
from oncotools.data_elements.image import Mask
from oncotools.data_elements.dose_map import DoseMask
from oncotools.radio_morphology.sup_inf_feature import SIFeature
from schema import Schema, And, SchemaError

class TestSupInfFeature(unittest.TestCase):
    '''
    Test RM features: Superior-Inferior feature
    '''

    @classmethod
    def setUpClass(cls):
        # Set up a database connection
        cls.db = Database.from_key('tests/credentials', 'config/credentials.key')

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
            res1.patientRepID, str(res1.name))

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
        feat = SIFeature('test')
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
        self.assertTrue(isinstance(feat, SIFeature))
        for elem in elem_list:
            self.assertTrue(hasattr(feat, elem))

    def test_create_with_featuretype(self):
        '''
        Can specify a certain feature type
        '''
        feat = SIFeature('test', feature_type='sample_type')
        self.assertFalse(feat.loaded)
        self.assertEqual(feat.type, 'sample_type')

    def test_process_before_load(self):
        '''
        Cannot process before loading data
        '''
        feat = SIFeature('test')
        self.assertFalse(feat.loaded)
        self.assertRaises(ValueError, lambda: feat.process())

    def test_values_before_load(self):
        '''
        Cannot get values before loading data
        '''
        feat = SIFeature('test')
        self.assertRaises(ValueError, lambda: feat.values)

    def test_create_feature_with_values(self):
        '''
        Can initialize with mask and dose grid
        '''
        feat = SIFeature('test', mask=self.mask, dose=self.dg)
        self.assertTrue(feat.mask is not None)
        self.assertTrue(feat.dose is not None)
        self.assertTrue(feat.loaded)

    def test_load_feature(self):
        '''
        Can initialize with mask and dose grid
        '''
        feat = SIFeature('test')
        feat.load(self.mask, self.dg)
        self.assertTrue(feat.mask is not None)
        self.assertTrue(feat.dose is not None)
        self.assertTrue(feat.loaded)

    def test_process_mask(self):
        '''
        DVH feature class has trivial mask processing
        '''
        v = Schema([Mask])
        feat = SIFeature('test', mask=self.mask, dose=self.dg)
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
        feat = SIFeature('test', mask=self.mask, dose=self.dg)
        output = feat.process_dose()
        try:
            self.assertTrue(v.validate(output) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_process(self):
        '''
        Process values for SIFeature
        '''
        com_schema = {
            'mean': And([float], lambda x: len(x) == 2),
            'min': And([float], lambda x: len(x) == 2),
            'max': And([float], lambda x: len(x) == 2),
            'dvh': And([np.ndarray], lambda x: len(x) == 2)
        }
        validator = Schema(com_schema)
        # Compute features
        feat = SIFeature('test', mask=self.mask, dose=self.dg)
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
        com_schema = {
            'mean': And([float], lambda x: len(x) == 2),
            'min': And([float], lambda x: len(x) == 2),
            'max': And([float], lambda x: len(x) == 2),
            'dvh': And([np.ndarray],
                       lambda x: np.all([d.shape == (6, 2) for d in x]),
                       lambda x: len(x) == 2)
        }
        validator = Schema(com_schema)
        # Compute features
        dvh_vals = [0, 0.2, 0.4, 0.6, 0.8, 1]
        feat = SIFeature('test', mask=self.mask, dose=self.dg, dvh=dvh_vals)
        output = feat.process()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(output) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

if __name__ == '__main__':
    unittest.main()
