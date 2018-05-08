import base64
import pickle
import unittest
import numpy as np

from Crypto.Cipher import AES
from oncotools.connect import Database
from oncotools.data_elements.image import Mask
from oncotools import transform as tf

class TestPartitionTransform(unittest.TestCase):
    '''
    Test partition transformations
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

    def test_octants(self):
        '''
        Create octants around a point
        '''
        octs = tf.partition.octants_around_point(
            self.masks[0], self.masks[0].center_of_mass)
        self.assertTrue(isinstance(octs, list))
        self.assertEqual(len(octs), 8)
        for m in octs:
            self.assertTrue(isinstance(m, Mask))

    def test_octant_order(self):
        '''
        Create octants around a point.
        Check that octants are in the right order.
        '''
        base_com = self.masks[0].center_of_mass
        octs = tf.partition.octants_around_point(
            self.masks[0], base_com)
        coms = [m.center_of_mass for m in octs]
        # 0 : (+,+,+)
        self.assertTrue(np.all(coms[0] > base_com))
        # 1 : (-,+,+)
        oct_com = coms[1]
        self.assertTrue(oct_com[0] < base_com[0])
        self.assertTrue(oct_com[1] > base_com[1])
        self.assertTrue(oct_com[2] > base_com[2])
        # 2 : (-,-,+)
        oct_com = coms[2]
        self.assertTrue(oct_com[0] < base_com[0])
        self.assertTrue(oct_com[1] < base_com[1])
        self.assertTrue(oct_com[2] > base_com[2])
        # 3 : (+,-,+)
        oct_com = coms[3]
        self.assertTrue(oct_com[0] > base_com[0])
        self.assertTrue(oct_com[1] < base_com[1])
        self.assertTrue(oct_com[2] > base_com[2])
        # 4 : (+,+,-)
        oct_com = coms[4]
        self.assertTrue(oct_com[0] > base_com[0])
        self.assertTrue(oct_com[1] > base_com[1])
        self.assertTrue(oct_com[2] < base_com[2])
        # 5 : (-,+,-)
        oct_com = coms[5]
        self.assertTrue(oct_com[0] < base_com[0])
        self.assertTrue(oct_com[1] > base_com[1])
        self.assertTrue(oct_com[2] < base_com[2])
        # 6 : (-,-,-)
        self.assertTrue(np.all(coms[6] < base_com))
        # 7 : (+,-,-)
        oct_com = coms[7]
        self.assertTrue(oct_com[0] > base_com[0])
        self.assertTrue(oct_com[1] < base_com[1])
        self.assertTrue(oct_com[2] < base_com[2])

    def test_halves(self):
        '''
        Create halves around a point.
        '''
        base_com = self.masks[0].center_of_mass
        halves = tf.partition.halves(
            self.masks[0], base_com)
        self.assertTrue(isinstance(halves, list))
        self.assertEqual(len(halves), 2)
        for m in halves:
            self.assertTrue(isinstance(m, Mask))
        coms = [m.center_of_mass for m in halves]
        self.assertTrue(coms[0][2] > base_com[2])
        self.assertTrue(coms[1][2] < base_com[2])

    def __slice_test_helper_1(self, slices, numslices):
        '''
        Helper method: Check that the right number of slices were made
        '''
        self.assertTrue(isinstance(slices, list))
        self.assertEqual(len(slices), numslices)
        for m in slices:
            self.assertTrue(isinstance(m, Mask))

    def __slice_test_helper_2(self, slices, axis_index):
        '''
        Helper method: Check that slices are ordered properly
        '''
        coms = [m.center_of_mass for m in slices]
        for i, m in enumerate(coms):
            if i > 0:
                self.assertGreater(coms[i][axis_index], coms[i-1][axis_index])

    def test_slices_x(self):
        '''
        Create slices along the X axis
        '''
        numslices = [2, 3, 4]
        for n in numslices:
            slices = tf.partition.slices(self.masks[0], n, 'x')
            self.__slice_test_helper_1(slices, n)
            self.__slice_test_helper_2(slices, 0)

    def test_slices_y(self):
        '''
        Create slices along the Y axis
        '''
        numslices = [2, 3, 4]
        for n in numslices:
            slices = tf.partition.slices(self.masks[0], n, 'y')
            self.__slice_test_helper_1(slices, n)
            self.__slice_test_helper_2(slices, 1)

    def test_slices_z(self):
        '''
        Create slices along the Z axis
        '''
        numslices = [2, 3, 4]
        for n in numslices:
            slices = tf.partition.slices(self.masks[0], n, 'z')
            self.__slice_test_helper_1(slices, n)
            self.__slice_test_helper_2(slices, 2)


if __name__ == '__main__':
    unittest.main()
