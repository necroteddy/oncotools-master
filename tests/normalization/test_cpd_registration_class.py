import base64
import pickle
import unittest
import numpy as np

from oncotools.connect import Database
from oncotools.normalization.cpd_registration import CPDRegistration
from schema import Schema, And, SchemaError

class TestRegistrationCPD(unittest.TestCase):
    '''
    Test RM features: Base class
    '''

    @classmethod
    def setUpClass(cls):
        # Set up a database connection
        cls.db = Database.from_key('tests/credentials', 'config/credentials.key')

        cls.rois = ['l_parotid', 'r_parotid']
        prepIDs = cls.db.regions_of_interest.get_patient_rep_ids_with_rois(cls.rois)
        if len(prepIDs) >= 2:
            cls.patientRep_1 = prepIDs[0]
            cls.patientRep_2 = prepIDs[1]

    @classmethod
    def tearDownClass(cls):
        del cls.db

    def test_check_elements(self):
        '''
        Make sure the Feature object has all the required attributes
        '''
        reg = CPDRegistration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
        elem_list = [
            'registration_type',
            'dbconn',
            'fixed_patient',
            'moving_patient',
            'roi_list',
            'use_surfaces',
            'sampling',
            'crop',
            'masks',
            'clouds',
            'images',
            'metrics',
            'params',
            'plateau_thresh',
            'plateau_length'
        ]
        self.assertTrue(isinstance(reg, CPDRegistration))
        for elem in elem_list:
            self.assertTrue(hasattr(reg, elem))

    def test_preprocess(self):
        '''
        CPD Preprocessing involves center of mass alignments
        '''
        preprocess_schema = (
            And(np.ndarray, lambda x: lambda x: x.shape[1] == 3),
            And(np.ndarray, lambda x: lambda x: x.shape[1] == 3)
        )
        validator = Schema(preprocess_schema)
        # Create a registration object
        myreg = CPDRegistration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
        res = myreg.preprocess()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(res) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_registration(self):
        '''
        CPD Registration involves center of mass alignments
        '''
        # Check the registration output
        registration_schema = And(np.ndarray, lambda x: lambda x: x.shape[1] == 3)
        reg_v = Schema(registration_schema)
        # Check the parameters
        params_schema = {
            'preprocess': np.ndarray,
            'G': np.ndarray,
            'w': np.ndarray,
            'z': np.ndarray
        }
        param_v = Schema(params_schema)
        # Check the metrics
        metrics_schema = {
            'runtime': lambda x: x > 0,
            'error': And([float], lambda x: x[-1] > 0),
            'iterations': And(int, lambda x: x > 0)
        }
        metric_v = Schema(metrics_schema)

        # Create a registration object
        myreg = CPDRegistration(self.db, self.patientRep_1, self.patientRep_2, self.rois,
                                sampling=[0.1, 0.1, 0.5])
        res = myreg.register()
        try:
            self.assertTrue(reg_v.validate(res) is not SchemaError)
            self.assertTrue(param_v.validate(myreg.params) is not SchemaError)
            self.assertTrue(metric_v.validate(myreg.metrics) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')


if __name__ == '__main__':
    unittest.main()
