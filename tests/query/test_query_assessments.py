import base64
import pickle
import unittest

from Crypto.Cipher import AES
from oncotools.connect import Database

class TestQueryAssessments(unittest.TestCase):
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

        query = 'SELECT TOP(1) ID, patientID FROM patientRepresentations'
        res = cls.db.run(query)
        cls.patientRepID = res.rows[0][0]
        cls.patientID = res.rows[0][1]

    @classmethod
    def tearDownClass(cls):
        del cls.db

    def test_list_all_assessments(self):
        '''
        How many of each assessment did this patient receive
        '''
        res = self.db.assessments.get_assessment_names()
        self.assertGreater(res.num_rows, 0)

    def test_list_all_assessments_for_patient(self):
        '''
        How many of each assessment did this patient receive
        '''
        res = self.db.assessments.get_assessment_names(self.patientID)
        self.assertGreater(res.num_rows, 0)
        self.assertEqual(res.num_cols, 2)

    def test_get_all_assessments_for_patient(self):
        '''
        Get all of a patient's assessments
        '''
        res = self.db.assessments.get_assessments(self.patientID)
        self.assertGreater(res.num_rows, 0)
        self.assertEqual(res.num_cols, 3)

    def test_get_all_assessments(self):
        '''
        Get all of a certain type of assessment
        '''
        res = self.db.assessments.get_assessment_names(self.patientID)
        my_axment = next(x[0] for x in res.rows if x[1] > 1)
        res = self.db.assessments.get_assessments(self.patientID, my_axment)
        self.assertGreater(res.num_rows, 1)
        self.assertEqual(res.num_cols, 3)

    def helper_assessment_start_stop(self):
        '''
        Get the first and last dates for an assessment
        '''
        res = self.db.assessments.get_assessment_names(self.patientID)
        my_axment = next(x[0] for x in res.rows if x[1] > 1)
        res = self.db.assessments.get_assessments(self.patientID, my_axment)
        dates = [r[1] for r in res.rows]
        return my_axment, min(dates), max(dates)

    def test_get_all_assessments_with_start(self):
        '''
        Get all of a certain type of assessment after a certain date
        '''
        name, min_date, _ = self.helper_assessment_start_stop()
        res1 = self.db.assessments.get_assessments(self.patientID, name)
        res2 = self.db.assessments.get_assessments(self.patientID, name, startDate=min_date+1)
        self.assertGreater(res1.num_rows, res2.num_rows)

    def test_get_all_assessments_with_stop(self):
        '''
        Get all of a certain type of assessment before a certain date
        '''
        name, _, max_date = self.helper_assessment_start_stop()
        res1 = self.db.assessments.get_assessments(self.patientID, name)
        res2 = self.db.assessments.get_assessments(self.patientID, name, stopDate=max_date-1)
        self.assertGreater(res1.num_rows, res2.num_rows)

    def test_get_all_assessments_with_start_stop(self):
        '''
        Get all of a certain type of assessment after a start date
        '''
        name, min_date, max_date = self.helper_assessment_start_stop()
        res0 = self.db.assessments.get_assessments(self.patientID, name)
        res1 = self.db.assessments.get_assessments(self.patientID, name, startDate=min_date+1)
        res2 = self.db.assessments.get_assessments(self.patientID, name, stopDate=max_date-1)
        res3 = self.db.assessments.get_assessments(self.patientID, name,
                                                   startDate=min_date+1,
                                                   stopDate=max_date-1)
        self.assertGreater(res0.num_rows, res1.num_rows)
        self.assertGreater(res0.num_rows, res2.num_rows)
        self.assertGreater(res0.num_rows, res3.num_rows)
        self.assertGreater(res1.num_rows, res3.num_rows)
        self.assertGreater(res2.num_rows, res3.num_rows)

    def test_get_binned_outcomes(self):
        '''
        Get a all outcomes binned by dates for each patient
        '''
        res = self.db.assessments.get_binned_outcomes('xerostomia')
        self.assertGreater(res.num_rows, 0)
        self.assertEqual(res.num_cols, 7)

    def test_get_custom_binned_outcomes(self):
        '''
        Get a all outcomes binned by dates for each patient.
        Use custom date ranges for the bins
        '''
        res = self.db.assessments.get_binned_outcomes('xerostomia',
                                                      bins=[0, 100],
                                                      labels=['sampleDate'])
        self.assertGreater(res.num_rows, 0)
        self.assertEqual(res.num_cols, 2)

    def test_get_binned_outcomes_fail(self):
        '''
        Get a all outcomes binned by dates for each patient.
        Should fail if bins are not given properly
        '''
        def testFunction(self):
            return self.db.assessments.get_binned_outcomes('xerostomia',
                                                           bins=[0, 100],
                                                           labels=['date1', 'date2'])
        self.assertRaises(ValueError, lambda: testFunction(self))

if __name__ == '__main__':
    unittest.main()
