import base64
import pickle
import unittest

from Crypto.Cipher import AES
from oncotools.connect import Database
from oncotools.data_elements.roi import Roi
from oncotools.data_elements.image import Mask

class TestQueryRegionsOfInterest(unittest.TestCase):
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

        # Select a patient
        query = 'SELECT TOP(1) ID, patientID FROM patientRepresentations'
        res = cls.db.run(query)
        cls.patientRepID = res.rows[0][0]
        cls.patientID = res.rows[0][1]

        def roi_query_helper(count):
            '''
            Get a patientRepID and ROI name that appears a certain number of times
            '''
            query = '''
                WITH query1 as (
                    SELECT patientRepID, name, count(*) as count
                    FROM RegionsOfInterest
                    GROUP BY name, patientRepID
                )
                SELECT TOP(1) * FROM query1 WHERE count = {}
            '''.format(count)
            res = cls.db.run(query)
            return res.rows[0]

        # Store patientRepID and name of ROIs with a certain number of occurrences
        res0 = roi_query_helper(1)
        cls.one_roi = [res0[0], str(res0[1])]
        res1 = roi_query_helper(2)
        cls.many_rois = [res1[0], str(res1[1])]


    @classmethod
    def tearDownClass(cls):
        del cls.db

    def test_get_roi_names(self):
        '''
        Get all distinct ROI names
        '''
        res = self.db.regions_of_interest.get_roi_names()
        self.assertGreater(len(res), 0)

    def test_get_roi_names_for_patient(self):
        '''
        Get all distinct ROI names
        '''
        res = self.db.regions_of_interest.get_roi_names(patientRepID=self.one_roi[0])
        self.assertGreater(len(res), 0)

    def test_roi_id(self):
        '''
        Get an ROI ID with a patientRepID and name
        '''
        res = self.db.regions_of_interest.get_id_by_patient_rep_id_name(
            self.one_roi[0], self.one_roi[1])
        self.assertTrue(isinstance(res, int))

    def test_patient_rep_id_from_roi(self):
        '''
        Get a patientRepID from an ROI ID
        '''
        res = self.db.regions_of_interest.get_id_by_patient_rep_id_name(
            self.one_roi[0], self.one_roi[1])
        self.assertTrue(isinstance(res, int))
        prepID = self.db.regions_of_interest.get_patient_rep_id(res)
        self.assertEqual(prepID, self.one_roi[0])

    def test_roi_id_fail(self):
        '''
        Get all distinct ROI names
        '''
        def test_function(self):
            return self.db.regions_of_interest.get_id_by_patient_rep_id_name(
                self.many_rois[0], self.many_rois[1])
        self.assertRaises(Exception, lambda: test_function(self))

    def test_roi_ids(self):
        '''
        Get an ROI ID with a patientRepID and name
        '''
        res = self.db.regions_of_interest.get_ids_by_patient_rep_id_name(
            self.many_rois[0], self.many_rois[1])
        self.assertTrue(isinstance(res, list))

    def test_get_prep_with_roi(self):
        '''
        Get all patient rep IDs with a certain ROI
        '''
        prep_list = self.db.regions_of_interest.get_patient_rep_ids_with_rois(self.one_roi[1])
        self.assertGreater(len(prep_list), -1)

    def test_get_prep_with_rois(self):
        '''
        Get all patient rep IDs with certain ROIs
        '''
        res = self.db.regions_of_interest.get_roi_names()
        rois = res[0:3]
        prep_list = self.db.regions_of_interest.get_patient_rep_ids_with_rois(rois)
        self.assertTrue(isinstance(prep_list, list))

    def test_roi_id_by_name(self):
        '''
        Get ROI IDs with a name
        '''
        res = self.db.regions_of_interest.get_ids_by_name(self.one_roi[1])
        self.assertEqual(res.num_cols, 4)
        self.assertGreater(res.num_rows, 0)

    def test_roi_id_by_names(self):
        '''
        Get ROI IDs with a name
        '''
        res = self.db.regions_of_interest.get_ids_by_name([self.one_roi[1], self.many_rois[1]])
        self.assertEqual(res.num_cols, 4)
        self.assertGreater(res.num_rows, 0)

    def test_mask_representation_with_prep(self):
        '''
        Get a patient representation with a patient representation ID
        '''
        res = self.db.regions_of_interest.get_mask_representation(patientRepID=self.one_roi[0])
        self.assertTrue(isinstance(res, dict))
        fields = [
            'patientRepID',
            'patientID',
            'xStart', 'yStart', 'zStart',
            'xVoxelSize', 'yVoxelSize', 'zVoxelSize',
            'xDimension', 'yDimension', 'zDimension']
        for field in fields:
            self.assertTrue(field in res.keys())

    def test_mask_representation_with_roi_id(self):
        '''
        Get a patient representation with an ROI ID
        '''
        res0 = self.db.regions_of_interest.get_id_by_patient_rep_id_name(
            self.one_roi[0], self.one_roi[1])
        res = self.db.regions_of_interest.get_mask_representation(roiID=res0)
        self.assertTrue(isinstance(res, dict))
        fields = [
            'patientRepID',
            'patientID',
            'xStart', 'yStart', 'zStart',
            'xVoxelSize', 'yVoxelSize', 'zVoxelSize',
            'xDimension', 'yDimension', 'zDimension']
        for field in fields:
            self.assertTrue(field in res.keys())

    def test_get_mask_rle(self):
        '''
        Retrieve a run-length encoded mask
        '''
        res = self.db.regions_of_interest.get_id_by_patient_rep_id_name(
            self.one_roi[0], self.one_roi[1])
        maskRLE = self.db.regions_of_interest.get_mask_rle(res)
        self.assertGreater(len(maskRLE), 0)

    def test_get_roi(self):
        '''
        Get an ROI
        '''
        res = self.db.regions_of_interest.get_id_by_patient_rep_id_name(
            self.one_roi[0], self.one_roi[1])
        myROI = self.db.regions_of_interest.get_roi(res)
        self.assertTrue(isinstance(myROI, Roi))

    def test_get_roi_with_rle_mask(self):
        '''
        Get an ROI with a RLE mask specified
        '''
        res = self.db.regions_of_interest.get_id_by_patient_rep_id_name(
            self.one_roi[0], self.one_roi[1])
        maskRLE = self.db.regions_of_interest.get_mask_rle(res)
        myROI = self.db.regions_of_interest.get_roi(res, maskRLE)
        self.assertTrue(isinstance(myROI, Roi))

    def __validate_get_rois(self, rois, dataType):
        for k in rois:
            if isinstance(rois[k], list):
                for r in rois[k]:
                    self.assertTrue(isinstance(r, dataType))
            else:
                self.assertTrue(isinstance(rois[k], dataType))

    def test_get_mask(self):
        '''
        Get a Mask
        '''
        res = self.db.regions_of_interest.get_id_by_patient_rep_id_name(
            self.one_roi[0], self.one_roi[1])
        myROI = self.db.regions_of_interest.get_mask(res)
        self.assertTrue(isinstance(myROI, Mask))

    def test_get_rois_one(self):
        '''
        Get many ROI's, specifying only one
        '''
        rois, not_found = self.db.regions_of_interest.get_rois(
            self.one_roi[0], self.one_roi[1])
        self.assertTrue(isinstance(rois, dict))
        self.assertEqual(len(rois.keys()), 1)
        self.__validate_get_rois(rois, Roi)
        self.assertTrue(isinstance(not_found, list))

    def test_get_rois_many(self):
        '''
        Get many ROI's, specifying many
        '''
        roi_names = self.db.regions_of_interest.get_roi_names(patientRepID=self.one_roi[0])
        roi_names = roi_names[0:4]
        rois, not_found = self.db.regions_of_interest.get_rois(
            self.one_roi[0], roi_names)
        self.assertTrue(isinstance(rois, dict))
        self.assertEqual(len(rois.keys()), 4)
        self.__validate_get_rois(rois, Roi)
        self.assertTrue(isinstance(not_found, list))

    def test_get_rois_duplicate(self):
        '''
        Get many Roi's. If there is a duplicate name, should be a list.
        '''
        rois, not_found = self.db.regions_of_interest.get_rois(
            self.many_rois[0], self.many_rois[1])
        self.assertTrue(isinstance(rois, dict))
        self.__validate_get_rois(rois, Roi)
        self.assertEqual(len(rois.keys()), 1)
        self.assertTrue(isinstance(rois[rois.keys()[0]], list))
        self.assertTrue(isinstance(not_found, list))

    def test_get_masks_one(self):
        '''
        Get many ROI's, specifying only one
        '''
        rois, not_found = self.db.regions_of_interest.get_masks(
            self.one_roi[0], self.one_roi[1])
        self.assertTrue(isinstance(rois, dict))
        self.assertEqual(len(rois.keys()), 1)
        self.__validate_get_rois(rois, Mask)
        self.assertTrue(isinstance(not_found, list))

    def test_get_masks_many(self):
        '''
        Get many ROI's, specifying many
        '''
        roi_names = self.db.regions_of_interest.get_roi_names(patientRepID=self.one_roi[0])
        roi_names = roi_names[0:4]
        rois, not_found = self.db.regions_of_interest.get_masks(
            self.one_roi[0], roi_names)
        self.assertTrue(isinstance(rois, dict))
        self.assertEqual(len(rois.keys()), 4)
        self.__validate_get_rois(rois, Mask)
        self.assertTrue(isinstance(not_found, list))

    def test_get_masks_duplicate(self):
        '''
        Get many Masks. If there is a duplicate name, should be a list.
        '''
        rois, not_found = self.db.regions_of_interest.get_masks(
            self.many_rois[0], self.many_rois[1])
        self.assertTrue(isinstance(rois, dict))
        self.__validate_get_rois(rois, Mask)
        self.assertEqual(len(rois.keys()), 1)
        self.assertTrue(isinstance(rois[rois.keys()[0]], list))
        self.assertTrue(isinstance(not_found, list))


if __name__ == '__main__':
    unittest.main()
