import unittest

class TestImports(unittest.TestCase):
    '''
    Make sure all modules can be found and that there are no syntax errors
    '''

    def test_import_data_elements(self):
        '''
        Import data elements
        '''
        from oncotools.data_elements import dose
        from oncotools.data_elements import dose_map
        from oncotools.data_elements import dvh
        from oncotools.data_elements import image
        from oncotools.data_elements import roi
        self.assertTrue(True)

    def test_import_connect(self):
        '''
        Import connection module
        '''
        from oncotools import connect
        self.assertTrue(True)

    def test_import_transform(self):
        '''
        Import transformations module
        '''
        from oncotools import transform
        self.assertTrue(True)

    def test_import_visualize(self):
        '''
        Import visualization module
        '''
        from oncotools import visualize
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
