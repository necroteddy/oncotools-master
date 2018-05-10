'''
Connect is a collection of classes used to connect to
and query an Oncospace database.
'''

import base64
import json
import pickle
import platform
import pyodbc
from numpy import asarray

from Cryptodome.Cipher import AES

# Oncospace Database utilities for querying
from .utils.query import assessments
from .utils.query import patient_representations
from .utils.query import patients
from .utils.query import radiotherapy_sessions
from .utils.query import regions_of_interest

def get_all_databases(username, pwd, server='rtmw-oncodb.radonc.jhmi.edu'):
    '''
    List all databases.
    '''
    sysname = platform.system()
    # Connect from Windows
    if sysname == 'Windows':
        cn = pyodbc.connect(
            driver='{SQL Server}', host=server, database='master', user=username, password=pwd)
    # Connect from Unix (assumes FreeTDS and unixODBC are set up)
    else:
        cn = pyodbc.connect(
            driver='{FreeTDS}', DSN='master', user=username, password=pwd)
    cursor = cn.cursor()
    cursor.execute('SELECT name from sys.databases')
    results = Results(cursor)
    return [str(row.name) for row in results.rows]

def create_login(outfile, secret, dr=None, ho=None, db=None, us=None, pw=None):
    '''
    Create an encrypted credentials file
    Positional arguments:
        :outfile:   file path to write credentials
        :secret:    file path to secret key
    Keyword arguments:
        :dr:        database driver
        :ho:        host
        :db:        database name
        :us:        user name
        :pw:        password
    '''
    if (db is None) or (us is None) or (pw is None):
        raise TypeError('Missing required connection parameters.')
    config_data = {
        'db': db,
        'us': us,
        'pw': pw,
        'ho': ho,
        'dr': dr
    }
    # Encode connection data as JSON
    msg_text = json.dumps(config_data)
    # Make sure the encoded string is a multiple of 16 bytes
    byte_len = len(msg_text.encode('utf-8'))
    wspace = 16 - (byte_len % 16)
    msg_text += ' '*wspace

    # Read the secret key. Must be 16 bytes long
    fhandle = open(secret, 'r')
    secret_key = fhandle.readline().strip()
    fhandle.close()

    # Encode the credentials
    cipher = AES.new(secret_key.encode(), AES.MODE_ECB)
    encoded = base64.b64encode(cipher.encrypt(msg_text.encode()))

    # Write to file
    pickle.dump(encoded, open(outfile, 'wb'))
    return outfile


# Results class ==========================================================


class Results(object):
    '''
    Object to store query results.

    The `Results` class provides a generalized format to store
    and manipulate query results. All calls to `Database.execute(query)`
    produce a `Results` object.

    Positional arguments / Attributes:
        :columns:   List of column names to be stored
        :rows:      List of `pyodbc` rows to be stored
    '''

    def __init__(self, cursor):
        # List of column names
        self.columns = [column[0] for column in cursor.description]
        # List of pyodbc rows in results
        self.rows = cursor.fetchall()

    def __str__(self):
        '''
        Create string representation of object
        '''
        numRows = len(self.rows)
        s = ''
        s += 'Results: {0} row{1}\n'.format(numRows, 's'
                                            if numRows > 1 else '')
        s += 'Columns: {0}\n'.format(tuple(self.columns))
        s += 'Rows:\n'
        s += '\n'.join([str(r) for r in self.rows])
        return s

    @property
    def num_rows(self):
        '''
        The number of rows in the results
        '''
        return len(self.rows)

    @property
    def num_cols(self):
        '''
        The number of columns in the results
        '''
        return len(self.columns)

    def to_array(self):
        '''
        Convert to a 2D array of results
        '''
        return asarray(self.rows).tolist()


# DatabaseManager class ==================================================


class DatabaseManager(object):
    '''
    Manage multiple `Database` connections
    '''

    def __init__(self):
        '''
        Initialize db object with private dictionary of connections
        '''
        self.__conn = {}

    def add_connection(self, name, dr=None, ho=None, db=None, us=None, pw=None):
        '''
        Create a connection to a database.

        Positional arguments:
            :name:  name of the connection
            :dr:    database driver
            :ho:    host
            :db:    database name
            :us:    user name
            :pw:    password
        Returns:
            Database class that was created
        '''
        self.__conn[name] = Database(dr, ho, db, us, pw)
        return self.__conn[name]

    def remove_connection(self, name):
        '''
        Remove a connection to a database.

        Positional arguments:
            :name:      name of the connection
        Raises:
            :KeyError:  if connection name was not found
        '''
        try:
            self.__conn[name].close()
            del self.__conn[name]
        except:
            raise KeyError('Connection name not found')

    def list_connections(self):
        '''
        List all associated connections.

        Returns:
            Dictionary - {connection name: connection details}
        '''
        cnxns = {c: str(self.__conn[c]) for c in self.__conn}
        return cnxns

    def get_connection(self, dbname):
        '''
        Access a certain database connection.

        Positional arguments:
            :dbname:    name of the database connection
        Returns:
            Database connection associated to the key, dbname
        Raises:
            :KeyError:  if connection name was not found
        '''
        try:
            return self.__conn[dbname]
        except:
            raise KeyError('Connection not found')

    def run(self, dbname, query):
        '''
        Run a query on a database.

        Positional arguments:
            :dbname:    name of the database connection to use
            :query:     query to perform
        Returns:
            Query results stored in a Results object
        Raises:
            :KeyError:  if connection name was not found
        '''
        try:
            return self.__conn[dbname].run(query)
        except:
            raise KeyError('Connection not found')

    def execute(self, dbname, query):
        '''
        Execute a statement on a database.

        Positional arguments:
            :dbname:    name of the database connection to use
            :query:     query to perform
        Returns:
            Query results stored in a Results object
        Raises:
            :KeyError:  if connection name was not found
        '''
        try:
            return self.__conn[dbname].execute(query)
        except:
            raise KeyError('Connection not found')


# Database class =========================================================


class Database(object):
    '''
    `pyodbc` wrapper to connect to Oncospace database

    Queries can be performed using `.execute(query)` where `query` is
    any SQL query. Predefined queries can also be performed using the
    `PatientRepresentations`, `RegionsOfInterest`, and `RadiotherapySessions`
    classes.

    Keyword arguments:
        :dr:    database driver
        :ho:    host
        :db:    database name
        :us:    user name
        :pw:    password
    '''

    def __init__(self, dr=None, ho=None, db=None, us=None, pw=None):
        # Check the OS
        sysname = platform.system()

        if (db is None) or (us is None) or (pw is None):
            raise TypeError('Missing required connection parameters.')
        if ho is None:
            ho = 'rtmw-oncodb.radonc.jhmi.edu'

        # Connection settings for Windows operating system
        if sysname == 'Windows':
            if dr is None:
                dr = '{SQL Server}'
            # Open the connection
            self.__conn = self.open(dr, ho, db, us, pw)

        # Connection settings for Unix operating systems
        else:
            # Default values for driver and host if none provided
            if dr is None:
                dr = '{FreeTDS}'
            self.__conn = self.open(dr, ho, db, us, pw)

        # Store connection fields (except password) as private variables
        self.__driver = dr
        self.__host = ho
        self.__database = db
        self.__user = us

        # Built in queries
        self.assessments = assessments.AssessmentsQueries(self)
        self.patient_representations = patient_representations.PatientRepresentationsQueries(self)
        self.patients = patients.PatientsQueries(self)     
        self.regions_of_interest = regions_of_interest.RegionsOfInterestQueries(self)
        self.radiotherapy_sessions = radiotherapy_sessions.RadiotherapySessionsQueries(self)

    # Alternate constructor
    @classmethod
    def from_key(cls, credentials_file, key_file):
        '''
        Create a database connection from an encrypted credentials file
        '''
        # Read the secret key. Must be 16 bytes long without trailing whitespace
        fhandle = open(key_file, 'r')
        secret_key = fhandle.readline().strip()
        fhandle.close()

        # Create the cipher
        cipher = AES.new(secret_key.encode(), AES.MODE_ECB)

        # Read the credentials file
        encoded = pickle.load(open(credentials_file, 'rb'))
        decoded = cipher.decrypt(base64.b64decode(encoded)).strip()
        connect_data = json.loads(decoded)

        # Create the database connection
        return cls(
            dr = connect_data.get('dr', None),
            ho = connect_data.get('ho', None),
            db = connect_data.get('db', None),
            us = connect_data.get('us', None),
            pw = connect_data.get('pw', None)
        )

    def __str__(self):
        '''
        Create string representation of the database class
            to show all connection details (except password)
        '''
        s = '<driver={0}, host={1}, database={2}, user={3}>'.format(
            self.__driver, self.__host, self.__database, self.__user)
        return s

    def get_connection_details(self):
        '''
        Return the connection details.
        '''
        ret = {}
        ret['driver'] = self.__driver
        ret['host'] = self.__host
        ret['database'] = self.__database
        ret['user'] = self.__user
        return ret

    def open(self, dr=None, ho=None, db=None, us=None, pw=None, conn_string=None):
        '''
        Open a connection to the database
        '''
        # If a connection string is provided
        if conn_string is not None:
            self.__conn = pyodbc.connect(conn_string)
        # If connection details are provided
        else:
            dr = self.__driver if dr is None else dr
            ho = self.__host if ho is None else ho
            sysname = platform.system()
            # Connect from Windows
            if sysname == 'Windows':
                self.__conn = pyodbc.connect(driver=dr, host=ho, database=db, user=us, password=pw)
            # Connect from Unix (assumes FreeTDS and unixODBC are set up)
            else:
                self.__conn = pyodbc.connect(driver=dr, DSN=db, user=us, password=pw)
        return self.__conn

    def close(self):
        '''
        Close the connection to the database
        '''
        self.__conn.close()

    def run(self, query):
        '''
        Run a query on a database

        Positional arguments:
            :query:     query to perform
        Return:
            query results stored in a Results object
        '''
        cursor = self.__conn.cursor()
        cursor.execute(query)
        return Results(cursor)

    def execute(self, query, params=None):
        '''
        Execute a statement on a database

        Positional arguments:
            :query:     query to perform
        '''
        cursor = self.__conn.cursor()
        if params is None:
            res = cursor.execute(query)
        else:
            res = cursor.execute(query, params)
        res.commit()
        return res
