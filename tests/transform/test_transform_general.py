import base64
import pickle
import unittest
import numpy as np

from Crypto.Cipher import AES
from oncotools.connect import Database
from oncotools.data_elements.image import Mask
from oncotools import transform as tf

class TestGeneralTransform(unittest.TestCase):
    '''
    Test general transformations
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
        res0 = cls.db.run(query)
        cls.patientRepID = res0.rows[0][0]

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
        res2, _ = cls.db.regions_of_interest.get_masks(cls.patientRepID, [str(r[2]) for r in res1])
        cls.masks = res2.values()

    @classmethod
    def tearDownClass(cls):
        del cls.db
        del cls.masks

    def test_combine_masks(self):
        '''
        Combine two masks
        '''
        comb_mask = tf.general.combine_masks(self.masks)
        self.assertTrue(isinstance(comb_mask, Mask))
        for m in self.masks:
            self.assertGreaterEqual(comb_mask.get_volume(), m.get_volume())

    def test_cant_combine_lt2_mask(self):
        '''
        Can't combine less than 2 masks
        '''
        self.assertRaises(ValueError, lambda: tf.general.combine_masks(self.masks[0]))
        self.assertRaises(ValueError, lambda: tf.general.combine_masks([]))

    def test_downsample_1(self):
        '''
        Downsample a mask uniformly
        '''
        ds_mask = tf.general.downsample(self.masks[0], 0.5)
        self.assertTrue(isinstance(ds_mask, Mask))
        self.assertLess(
            len(ds_mask.data.nonzero()[0]), len(self.masks[0].data.nonzero()[0]))
        self.assertTrue(np.all(ds_mask.spacing == np.divide(self.masks[0].spacing, 0.5)))

    def test_downsample_2(self):
        '''
        Downsample a mask with different rates along each axis
        '''
        rates = [0.5, 0.5, 1]
        ds_mask = tf.general.downsample(self.masks[0], rates)
        self.assertTrue(isinstance(ds_mask, Mask))
        self.assertLess(
            len(ds_mask.data.nonzero()[0]), len(self.masks[0].data.nonzero()[0]))
        self.assertTrue(np.all(ds_mask.spacing == np.divide(self.masks[0].spacing, rates)))

    def test_crop(self):
        '''
        Crop an image to the bounds of its nonzero voxels.
        Cropped masks should have the same volume and spacing,
        but different size, origin, and end.
        '''
        crop_mask = tf.general.crop(self.masks[0])
        self.assertTrue(isinstance(crop_mask, Mask))
        # Volume and spacing should not change
        self.assertEqual(crop_mask.get_volume(), self.masks[0].get_volume())
        self.assertTrue(np.all(crop_mask.get_spacing() == self.masks[0].get_spacing()))
        # Size, origin, and end of image should change
        self.assertLessEqual(crop_mask.get_size(), self.masks[0].get_size())
        self.assertTrue(np.all(crop_mask.get_origin() >= self.masks[0].get_origin()))
        self.assertTrue(np.all(crop_mask.get_end() <= self.masks[0].get_end()))

    def test_convert_to_polar(self):
        '''
        Convert a mask to polar coordinates
        '''
        polar_data, coms = tf.general.convert_to_polar(self.masks[0])
        num_slices = len(set(self.masks[0].data.nonzero()[0]))
        self.assertTrue(isinstance(polar_data, np.ndarray))
        self.assertEqual(polar_data.shape[0], num_slices)
        for slc in polar_data:
            self.assertEqual(slc.shape[1], 2)
        self.assertTrue(isinstance(coms, list))

    def test_convert_to_euclidean(self):
        '''
        Convert from polar back to euclidean
        '''
        polar_data, coms = tf.general.convert_to_polar(self.masks[0])
        euc_data = tf.general.convert_to_euclidean(polar_data, coms)
        self.assertTrue(isinstance(euc_data, np.ndarray))

if __name__ == '__main__':
    unittest.main()
