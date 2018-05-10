Connecting to the database
=====================================

Learn how to use the OncospaceConnect module to configure your database connections.


Using the `Database` class
--------------------------

Create a database connection
............................

The parameters of the Database class are:
  :driver:  The database driver being used. For an Oncospace database, the {SQL Server} driver is used.
  :host:    The URL or IP address of the database.
  :dbname:  The name of the database.
  :user:    Username
  :pass:    Password

.. code-block:: python

    driver  = '{SQL Server}'
    host    = 'database.com'
    dbname  = 'myDatabase'
    user    = 'myUsername'
    pwd     = 'myPassword'

    db = Database(driver, host, dbname, user, pwd)

Run a query
.....................

Queries are passed as string parameters to the `db.run()` function.

.. code-block:: python

    query = 'SELECT * FROM myDatabase.myTable'
    result = db.run(query)



Using the `DatabaseManager` class
---------------------------------

The DatabaseManager makes it easy to manage and interact with multiple databases at once.

Add a database connection
.........................

.. code-block:: python

    dbm = DatabaseManager()

    # The first parameter is the name you assign to a connection
    dbm.add_connection('sample_conn', {SQL Server}, 'database.com', 'myDatabase', 'guest', 'guestPass')

Run a query
.....................

.. code-block:: python

    query = 'SELECT * FROM myDatabase.myTable'
    # Again, the first parameter to .execute() is the connection name
    result = dbm.run('sample_conn', query)


Using the `Results` class
-------------------------

The `Results` class provides a general structure to manage query results.

.. code-block:: python

    db = Database({SQL Server}, 'database.com', 'myDatabase', 'guest', 'guestPass')

    query = 'SELECT X, Y from DVHData dvh JOIN RoiDoseSummaries rds
      ON rds.ID = dvh.roiDoseSummaryID
      WHERE rds.roiID = 000 AND rds.radiotherapySessionID = 111'
    result = db.run(query)

    print result.columns
    # Output: ['X', 'Y']

    print result.rows[0]
    # Output: (54.04071044921875, 0.2683965563774109)
