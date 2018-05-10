import base64
import pickle
import unittest
import numpy as np

from oncotools.connect import Database
from oncotools.normalization.registration import Registration
from oncotools.data_elements.image import Mask
from schema import Schema, And, SchemaError

class TestRegistrationBase(unittest.TestCase):
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
        reg = Registration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
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
            'params'
        ]
        self.assertTrue(isinstance(reg, Registration))
        for elem in elem_list:
            self.assertTrue(hasattr(reg, elem))

    def test_registration_get_mask(self):
        '''
        Can get a single patient's masks
        '''
        reg = Registration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
        mymask = reg.get_mask(self.patientRep_1)
        self.assertTrue(isinstance(mymask, Mask))

    def test_registration_get_masks(self):
        '''
        Can get both patients' masks
        '''
        masks_schema = {
            self.patientRep_1: And(Mask, lambda x: len(x.data.nonzero()[0]) > 0),
            self.patientRep_2: And(Mask, lambda x: len(x.data.nonzero()[0]) > 0)
        }
        validator = Schema(masks_schema)
        # Create a registration object
        reg = Registration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
        mymasks = reg.get_masks()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(mymasks) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_registration_get_masks_with_cropping(self):
        '''
        Can get both patients' masks
        '''
        masks_schema = {
            self.patientRep_1: And(Mask, lambda x: len(x.data.nonzero()[0]) > 0),
            self.patientRep_2: And(Mask, lambda x: len(x.data.nonzero()[0]) > 0)
        }
        validator = Schema(masks_schema)
        # Create a registration object
        reg = Registration(
            self.db, self.patientRep_1, self.patientRep_2, self.rois,
            crop=True)
        mymasks = reg.get_masks()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(mymasks) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_registration_get_masks_with_sampling(self):
        '''
        Can get both patients' masks
        '''
        masks_schema = {
            self.patientRep_1: And(Mask, lambda x: len(x.data.nonzero()[0]) > 0),
            self.patientRep_2: And(Mask, lambda x: len(x.data.nonzero()[0]) > 0)
        }
        validator = Schema(masks_schema)
        # Create a registration object
        reg = Registration(
            self.db, self.patientRep_1, self.patientRep_2, self.rois,
            sampling=[0.5, 0.5, 1])
        mymasks = reg.get_masks()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(mymasks) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_registration_get_masks_with_surfaces(self):
        '''
        Can get both patients' masks
        '''
        masks_schema = {
            self.patientRep_1: And(Mask, lambda x: len(x.data.nonzero()[0]) > 0),
            self.patientRep_2: And(Mask, lambda x: len(x.data.nonzero()[0]) > 0)
        }
        validator = Schema(masks_schema)
        # Create a registration object
        reg = Registration(
            self.db, self.patientRep_1, self.patientRep_2, self.rois,
            use_surfaces=True)
        mymasks = reg.get_masks()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(mymasks) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_registration_get_cloud(self):
        '''
        Can get a single patient's point cloud
        '''
        reg = Registration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
        mymask = reg.get_point_cloud(self.patientRep_1)
        self.assertTrue(isinstance(mymask, np.ndarray))

    def test_registration_get_clouds(self):
        '''
        Can both patients' point clouds
        '''
        masks_schema = {
            self.patientRep_1: And(np.ndarray, lambda x: x.shape[1] == 3),
            self.patientRep_2: And(np.ndarray, lambda x: x.shape[1] == 3)
        }
        validator = Schema(masks_schema)
        # Create a registration object
        reg = Registration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
        mymasks = reg.get_point_clouds()
        # Check the output schema
        try:
            self.assertTrue(validator.validate(mymasks) is not SchemaError)
        except SchemaError:
            self.fail('Output does not match given schema')

    def test_preprocess_not_implemented(self):
        '''
        Base registration class does not have preprocess() implemented
        '''
        reg = Registration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
        self.assertRaises(NotImplementedError, lambda: reg.preprocess())

    def test_register_not_implemented(self):
        '''
        Base registration class does not have register() implemented
        '''
        reg = Registration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
        self.assertRaises(NotImplementedError, lambda: reg.register())

    def test_plot_not_implemented(self):
        '''
        Base registration class does not have plot() implemented
        '''
        reg = Registration(self.db, self.patientRep_1, self.patientRep_2, self.rois)
        self.assertRaises(NotImplementedError, lambda: reg.plot())

if __name__ == '__main__':
    unittest.main()
