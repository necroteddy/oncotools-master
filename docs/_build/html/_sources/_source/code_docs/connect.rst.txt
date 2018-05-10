Connect to the database
=======================

.. automodule:: connect


Results
---------------------

.. autoclass:: connect.Results
    :members:


Database
---------------------
The `Database` class is a wrapper of the `pyodbc` package
to connect to the Oncospace database.

Sample usage:

.. code-block:: python

    db = Database({SQL Server}, 'database.com', 'myDatabase', 'myUsername', 'myPassword')

    query = 'SELECT * FROM myDatabase.myTable'
    result = db.execute(query)

.. autoclass:: connect.Database
    :members:

Many common queries are built in to the database class: :ref:`query`.


DatabaseManager
---------------------
The `DatabaseManager` class provides an easy way to manage multiple data
connections at once. Queries can be executed by specifying the name
assigned to a database connection.

Sample usage:

.. code-block:: python

    dbm = DatabaseManager()
    dbm.add_connection('sample_conn', {SQL Server}, 'database.com', 'myDatabase', 'myUsername', 'myPassword')

    query = 'SELECT * FROM myDatabase.myTable'
    result = dbm.execute('sample_conn', query)

.. autoclass:: connect.DatabaseManager
    :members:
