import os
import unittest
import numpy as np

from oncotools.normalization import cpd

class TestCPD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tol = 0.0001

    def _load_ndarray(self, file_name):
        file_path = os.path.join(os.path.join('tests', 'test_data', 'cpd_data'), file_name)
        return np.load(file_path)

    def test_register_affine(self):
        # Load input dataset
        X = self._load_ndarray('affine_X.npy')
        Y = self._load_ndarray('affine_Y.npy')
        # Load expected output
        T_desired = self._load_ndarray('affine_T.npy')
        # Call function under test
        T_actual = cpd.register_affine(X, Y, w=0.6)
        # Compare outputs
        diff = np.abs(T_actual - T_desired)
        self.assertTrue(np.all(diff < self.tol))

    def test_register_nonrigid(self):
        # Load input dataset
        X = self._load_ndarray('nonrigid_X.npy')
        Y = self._load_ndarray('nonrigid_Y.npy')
        # Load expected output
        T_desired = self._load_ndarray('nonrigid_T.npy')
        # Call function under test
        T_actual, _, _, _ = cpd.register_nonrigid(X, Y, w=0.0)
        # Compare outputs
        diff = np.abs(T_actual - T_desired)
        self.assertTrue(np.all(diff < self.tol))

    def test_register_rigid(self):
        # load input dataset
        X = self._load_ndarray('rigid_X.npy')
        Y = self._load_ndarray('rigid_Y.npy')
        # Load expected output
        T_desired = self._load_ndarray('rigid_T.npy')
        # Call function under test
        T_actual = cpd.register_rigid(X, Y, 0.0)
        # Compare outputs
        diff = np.abs(T_actual - T_desired)
        self.assertTrue(np.all(diff < self.tol))

if __name__ == '__main__':
    unittest.main()
