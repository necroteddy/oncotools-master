import base64
import os
import pickle
import unittest

from Cryptodome.Cipher import AES
from oncotools.connect import *

class TestConnection(unittest.TestCase):
    '''
    Test database connection and queries
    '''
    
    @classmethod
    def setUpClass(cls):
        # Read the secret key. Must be 16 bytes long without trailing whitespace
        fhandle = open('config/credentials.key', 'r')
        secret_key = fhandle.readline().strip()
        fhandle.close()

        # Create the cipher
        cipher = AES.new(secret_key.encode(), AES.MODE_ECB)

        # Read the credentials file
        encoded = pickle.load(open('tests/credentials', 'rb'))
        decoded = cipher.decrypt(base64.b64decode(encoded)).strip()
        cls.cd = json.loads(decoded)

        # Files to delete
        cls.to_remove = []

    @classmethod
    def tearDownClass(cls):
        del cls.cd
        # Clean up files
        for f in cls.to_remove:
            os.remove(f)

    def test_get_databases(self):
        '''
        Get a list of all databses
        '''
        dblist = get_all_databases(self.cd['us'], self.cd['pw'])
        self.assertTrue(isinstance(dblist, list))
        self.assertGreater(len(dblist), 0)

    def test_create_login(self):
        '''
        Create a login file
        '''
        # Create the credentials file
        cred_file = create_login(
            'tests/files/test_credentials',
            'config/credentials.key',
            db = self.cd['db'],
            us = self.cd['us'],
            pw = self.cd['pw']
        )
        # Log in with the created credentials
        db = Database.from_key('tests/files/test_credentials', 'config/credentials.key')
        self.assertEqual(cred_file, 'tests/files/test_credentials')
        self.assertTrue(isinstance(db, Database))
        self.to_remove.append(cred_file)

    def test_create_connection(self):
        '''
        Create a database connection
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        self.assertTrue(isinstance(db, Database))

    def test_create_connection_from_credentials_file(self):
        '''
        Create a database connection from a credentials file
        '''
        db = Database.from_key('tests/credentials', 'config/credentials.key')
        self.assertTrue(isinstance(db, Database))

    def test_run_query_no_results(self):
        '''
        Run a query and get no results
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        query = 'SELECT * FROM patientRepresentations WHERE 0=1'
        res = db.run(query)
        self.assertTrue(isinstance(res, Results))
        self.assertEqual(res.num_rows, 0)

    def test_run_query_with_results(self):
        '''
        Run a query and get results
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        query = 'SELECT TOP(5) ID, patientID FROM patientRepresentations'
        res = db.run(query)
        self.assertTrue(isinstance(res, Results))
        self.assertTrue(isinstance(res.rows, list))
        self.assertTrue(isinstance(res.columns, list))
        self.assertEqual(res.num_rows, 5)
        self.assertEqual(res.num_cols, 2)
    
    def test_results_to_array(self):
        '''
        Convert a query's results to an array
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        query = 'SELECT TOP(5) ID, patientID FROM patientRepresentations'
        res = db.run(query).to_array()
        self.assertTrue(isinstance(res, list))
        self.assertEqual(len(res), 5)
        self.assertEqual(len(res[0]), 2)

    def test_close_connection(self):
        '''
        Close a database connection
        '''
        db = Database(db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
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
        db = Database(db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        db.close()
        db.open(db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
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
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        self.assertTrue(isinstance(dbm, DatabaseManager))

    def test_get_connection(self):
        '''
        Get a connection from a database manager
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        conn = dbm.get_connection('conn1')
        self.assertTrue(isinstance(conn, Database))

    def test_list_connection(self):
        '''
        List all of a database manager's connections
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        conn_dict = dbm.list_connections()
        self.assertTrue(isinstance(conn_dict, dict))
        self.assertEqual(len(conn_dict.keys()), 1)

    def test_remove_connection(self):
        '''
        Remove a connection from a database manager
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        dbm.remove_connection('conn1')
        conn_dict = dbm.list_connections()
        self.assertTrue(isinstance(conn_dict, dict))
        self.assertEqual(len(conn_dict.keys()), 0)

    def test_add_connections(self):
        '''
        Add connections to a database manager
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        dbm.add_connection('conn2', db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])        
        conn_dict = dbm.list_connections()
        self.assertTrue(isinstance(conn_dict, dict))
        self.assertEqual(len(conn_dict.keys()), 2)

    def test_dbm_query(self):
        '''
        Run a query from a database manager
        '''
        dbm = DatabaseManager()
        dbm.add_connection('conn1', db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
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
            'conn1', db='OncospaceHeadNeck', us=self.cd['us'], pw=self.cd['pw'])
        query = 'SELECT TOP(5) ID, patientID FROM patientRepresentations'
        self.assertRaises(KeyError, lambda: dbm.run('conn2', query))

if __name__ == '__main__':
    unittest.main()
