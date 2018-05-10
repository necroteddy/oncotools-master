import os
import unittest

from oncotools.utils import file_manager as fm

class TestFileManager(unittest.TestCase):
    '''
    Test file managment functions
    '''

    @classmethod
    def setUpClass(cls):
        cls.file_path = 'tests/files/'
        # Files to delete
        cls.to_remove = []

    @classmethod
    def tearDownClass(cls):
        # Clean up files
        for f in cls.to_remove:
            os.remove(f)

    def test_write_file_with_ending(self):
        '''
        Write a file
        '''
        testfilename = 'TESTFILE_1.obo'
        filepath = os.path.join(self.file_path, testfilename)
        self.to_remove.append(filepath)
        written = fm.write('hello, world!', filepath)
        self.assertTrue(written)

    def test_read_file_with_ending(self):
        '''
        Read a file
        '''
        testbody = 'can you read this?'
        testfilename = 'TESTFILE_2.obo'
        # Write a file
        filepath = os.path.join(self.file_path, testfilename)
        self.to_remove.append(filepath)
        written = fm.write(testbody, filepath)
        self.assertTrue(written)
        # Read a file
        intext = fm.read(filepath)
        self.assertEqual(testbody, intext)

    def test_write_file_without_ending(self):
        '''
        Write a file
        '''
        testfilename = 'TESTFILE_3'
        filepath = os.path.join(self.file_path, testfilename)
        self.to_remove.append(filepath + '.obo')
        written = fm.write('hello, world!', filepath)
        self.assertTrue(written)

    def test_read_file_without_ending(self):
        '''
        Read a file
        '''
        testbody = 'can you read this?'
        testfilename = 'TESTFILE_4'
        # Write a file
        filepath = os.path.join(self.file_path, testfilename)
        self.to_remove.append(filepath + '.obo')
        written = fm.write(testbody, filepath)
        self.assertTrue(written)
        # Read a file
        intext = fm.read(filepath)
        self.assertEqual(testbody, intext)

    def test_write_bad_filename(self):
        '''
        Write a file
        '''
        bad_chars = ':*<>|?"'
        for c in bad_chars:
            testfilename = 'TEST_CHAR_{}.obo'.format(c)
            filepath = os.path.join(self.file_path, testfilename)
            self.assertRaises(Exception, lambda: fm.write('hello, world!', filepath))

if __name__ == '__main__':
    unittest.main()
