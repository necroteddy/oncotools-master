import os
import unittest

from oncotools.interpreters import DicomReader

from schema import Schema, Or, SchemaError

class TestDicomReader(unittest.TestCase):
    '''
    Make sure all modules can be found and that there are no syntax errors
    '''

    @classmethod
    def setUpClass(cls):
        file_path = os.path.join('tests', 'test_data', 'dicom_data')
        (_, _, file_list) = next(os.walk(file_path))
        cls.files = [open(os.path.join(file_path, f), 'rb') for f in file_list]
        cls.reader = DicomReader(cls.files)

    def test_metadata(self):
        '''
        Make sure that metadata was constructed properly
        '''
        metadata_schema = {
            'mrn': Or(None, str),
            'patient_name': Or(None, str),
            'last_name': Or(None, str),
            'first_name': Or(None, str),
            'attending': Or(None, str),
            'manufacturer': Or(None, str)
        }
        validator = Schema(metadata_schema)
        try:
            self.assertTrue(validator.validate(self.reader.get_metadata()) is not SchemaError)
        except SchemaError:
            self.fail('Metadata does not match given schema')

    def test_get_all_structures(self):
        '''
        Get all structures
        '''
        self.reader.get_structures()
        self.assertTrue(isinstance(self.reader.structures, dict))

    def test_get_some_structures(self):
        '''
        Get some structures
        '''
        # Some names that are known to be in the sample dataset
        structs = self.reader.get_structures(names=['mandible', 'thyroid'])
        self.assertTrue(isinstance(structs, dict))
        self.assertEqual(len(structs.keys()), 2)

    def test_get_some_structures_after_all(self):
        '''
        Get some structures after loading all
        '''
        # Some names that are known to be in the sample dataset
        structs1 = self.reader.get_structures()
        structs2 = self.reader.get_structures(names=['mandible', 'thyroid'])
        # Both calls should return dictionaries
        self.assertTrue(isinstance(structs1, dict))
        self.assertTrue(isinstance(structs2, dict))
        self.assertTrue(isinstance(self.reader.structures, dict))
        # There should be a different number of keys
        self.assertGreater(len(structs1.keys()), len(structs2.keys()))
        self.assertEqual(len(structs2.keys()), 2)
        self.assertEqual(len(structs1.keys()), len(self.reader.structures.keys()))

if __name__ == '__main__':
    unittest.main()
