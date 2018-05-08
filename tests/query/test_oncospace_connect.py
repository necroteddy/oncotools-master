import base64
import pickle
import unittest

from Crypto.Cipher import AES
from oncotools.connect import *

class TestConnection(unittest.TestCase):
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
        cls.cd = {
            'username': data[0],
            'password': data[1]
        }

    @classmethod
    def tearDownClass(cls):
        del cls.cd

    def test_get_databases(self):
        '''
        Get a list of all databses
        '''
        dblist = get_all_databases(self.cd['username'], self.cd['password'])
        self.assertTrue(isinstance(dblist, list))
        self.assertGreater(len(dblist), 0)

    def test_create_connection(self):
        '''
        Create a database connection
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        self.assertTrue(isinstance(db, Database))

    def test_run_query_no_results(self):
        '''
        Run a query and get no results
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        query = 'SELECT * FROM patientRepresentations WHERE 0=1'
        res = db.run(query)
        self.assertTrue(isinstance(res, Results))
        self.assertEqual(res.num_rows, 0)

    def test_run_query_with_results(self):
        '''
        Run a query and get results
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        query = 'SELECT TOP(5) ID, patientID FROM patientRepresentations'
        res = db.run(query)
        self.assertTrue(isinstance(res, Results))
        self.assertTrue(isinstance(res.rows, list))
        self.assertTrue(isinstance(res.columns, list))
        self.assertEqual(res.num_rows, 5)
        self.assertEqual(res.num_cols, 2)

    def test_close_connection(self):
        '''
        Close a database connection
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        db.close()
        query = 'SELECT * FROM patientRepresentations WHERE 0=1'
        fail_flag = 0
        try:
            db.run(query)
        except:
            fail_flag = 1
        self.assertEqual(fail_flag, 1)

    def test_reopen_connection(self):
        '''
        Reopen a database connection
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        db.close()
        db.open(db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        query = 'SELECT * FROM patientRepresentations WHERE 0=1'
        res = db.run(query)
        self.assertTrue(isinstance(res, Results))
        self.assertEqual(res.num_rows, 0)

    def test_create_dbmanager(self):
        '''
        Create a database manager
        '''
        dbm = DatabaseManager()
        self.assertTrue(isinstance(dbm, DatabaseManager))

    def test_add_connection(self):
        '''
        Add a connection to a database manager
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        self.assertTrue(isinstance(dbm, DatabaseManager))

    def test_get_connection(self):
        '''
        Get a connection from a database manager
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        conn = dbm.get_connection('conn1')
        self.assertTrue(isinstance(conn, Database))

    def test_list_connection(self):
        '''
        List all of a database manager's connections
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        conn_dict = dbm.list_connections()
        self.assertTrue(isinstance(conn_dict, dict))
        self.assertEqual(len(conn_dict.keys()), 1)

    def test_remove_connection(self):
        '''
        Remove a connection from a database manager
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        dbm.remove_connection('conn1')
        conn_dict = dbm.list_connections()
        self.assertTrue(isinstance(conn_dict, dict))
        self.assertEqual(len(conn_dict.keys()), 0)

    def test_add_connections(self):
        '''
        Add connections to a database manager
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        dbm.add_connection('conn2', db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])        
        conn_dict = dbm.list_connections()
        self.assertTrue(isinstance(conn_dict, dict))
        self.assertEqual(len(conn_dict.keys()), 2)

    def test_dbm_query(self):
        '''
        Run a query from a database manager
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        query = 'SELECT TOP(5) ID, patientID FROM patientRepresentations'
        res = dbm.run('conn1', query)
        self.assertTrue(isinstance(res, Results))
        self.assertTrue(isinstance(res.rows, list))
        self.assertTrue(isinstance(res.columns, list))
        self.assertEqual(res.num_rows, 5)
        self.assertEqual(res.num_cols, 2)

    def test_dbm_query_fail(self):
        '''
        Run a query from a database manager. Should fail if connection doesn't exist.
        '''
        dbm = DatabaseManager()
        dbm.add_connection(
            'conn1', db='OncospaceHeadNeck', us=self.cd['username'], pw=self.cd['password'])
        query = 'SELECT TOP(5) ID, patientID FROM patientRepresentations'
        self.assertRaises(KeyError, lambda: dbm.run('conn2', query))

if __name__ == '__main__':
    unittest.main()
