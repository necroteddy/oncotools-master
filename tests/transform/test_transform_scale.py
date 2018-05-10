import base64
import pickle
import unittest

from oncotools.connect import Database
from oncotools.data_elements.image import Mask
from oncotools import transform as tf

class TestScaleTransform(unittest.TestCase):
    '''
    Test scaling transformations
    '''

    @classmethod
    def setUpClass(cls):
        # Set up a database connection
        cls.db = Database.from_key('tests/credentials', 'config/credentials.key')

        # Select a patient
        query = 'SELECT TOP(1) ID, patientID FROM patientRepresentations'
        res0 = cls.db.run(query)
        cls.patientRepID = res0.rows[0].ID

        def roi_query_helper(prepID):
            '''
            Get all ROI's for a patient ID
            '''
            query = '''
                SELECT TOP(2) patientRepID, ID, name
                FROM RegionsOfInterest
                WHERE patientRepID = {}
                ORDER BY name asc
            '''.format(prepID)
            return cls.db.run(query).rows

        # Store patientRepID and a few ROI names and IDs
        res1 = roi_query_helper(cls.patientRepID)
        # Get a few masks
        res2, _ = cls.db.regions_of_interest.get_masks(cls.patientRepID, [str(r.name) for r in res1])
        cls.masks = list(res2.values())

    @classmethod
    def tearDownClass(cls):
        del cls.db
        del cls.masks

    def test_expand_1(self):
        '''
        Expand by a certain amount
        '''
        exp = 0.5
        mask_a = tf.scale.expand(self.masks[0], exp)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertGreater(mask_a.get_volume(), self.masks[0].get_volume())

    def test_expand_2(self):
        '''
        Expand by various amounts
        '''
        exp1 = 0.5
        exp2 = 0.75
        mask_a = tf.scale.expand(self.masks[0], exp1)
        mask_b = tf.scale.expand(self.masks[0], exp2)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertTrue(isinstance(mask_b, Mask))
        self.assertGreater(mask_a.get_volume(), self.masks[0].get_volume())
        self.assertGreater(mask_b.get_volume(), mask_a.get_volume())

    def test_expand_3(self):
        '''
        Expand by a list of one amount
        '''
        exp = [0.5]
        mask_a = tf.scale.expand(self.masks[0], exp)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertGreater(mask_a.get_volume(), self.masks[0].get_volume())

    def test_expand_4(self):
        '''
        Expand by a list of three amounts
        '''
        exp1 = 0.5
        exp2 = [0.5, 0.5, 0.5]
        mask_a = tf.scale.expand(self.masks[0], exp1)
        mask_b = tf.scale.expand(self.masks[0], exp2)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertTrue(isinstance(mask_b, Mask))
        self.assertGreater(mask_a.get_volume(), self.masks[0].get_volume())
        self.assertEqual(mask_b.get_volume(), mask_a.get_volume())

    def test_expand_5(self):
        '''
        Expand by a list of three amounts
        '''
        exp1 = 0.5
        exp2 = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        mask_a = tf.scale.expand(self.masks[0], exp1)
        mask_b = tf.scale.expand(self.masks[0], exp2)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertTrue(isinstance(mask_b, Mask))
        self.assertGreater(mask_a.get_volume(), self.masks[0].get_volume())
        self.assertEqual(mask_b.get_volume(), mask_a.get_volume())

    def test_contract_1(self):
        '''
        Contract by a certain amount
        '''
        ctr = 0.5
        mask_a = tf.scale.contract(self.masks[0], ctr)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertLess(mask_a.get_volume(), self.masks[0].get_volume())

    def test_contract_2(self):
        '''
        Contract by various amounts
        '''
        ctr1 = 0.5
        ctr2 = 0.75
        mask_a = tf.scale.contract(self.masks[0], ctr1)
        mask_b = tf.scale.contract(self.masks[0], ctr2)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertTrue(isinstance(mask_b, Mask))
        self.assertLess(mask_a.get_volume(), self.masks[0].get_volume())
        self.assertLess(mask_b.get_volume(), mask_a.get_volume())

    def test_contract_3(self):
        '''
        Contract by a list of one amount
        '''
        exp = [0.5]
        mask_a = tf.scale.contract(self.masks[0], exp)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertLess(mask_a.get_volume(), self.masks[0].get_volume())

    def test_contract_4(self):
        '''
        Contract by a list of three amounts
        '''
        exp1 = 0.5
        exp2 = [0.5, 0.5, 0.5]
        mask_a = tf.scale.contract(self.masks[0], exp1)
        mask_b = tf.scale.contract(self.masks[0], exp2)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertTrue(isinstance(mask_b, Mask))
        self.assertLess(mask_a.get_volume(), self.masks[0].get_volume())
        self.assertEqual(mask_b.get_volume(), mask_a.get_volume())

    def test_contract_5(self):
        '''
        Contract by a list of three amounts
        '''
        exp1 = 0.5
        exp2 = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        mask_a = tf.scale.contract(self.masks[0], exp1)
        mask_b = tf.scale.contract(self.masks[0], exp2)
        self.assertTrue(isinstance(mask_a, Mask))
        self.assertTrue(isinstance(mask_b, Mask))
        self.assertLess(mask_a.get_volume(), self.masks[0].get_volume())
        self.assertEqual(mask_b.get_volume(), mask_a.get_volume())

if __name__ == '__main__':
    unittest.main()
