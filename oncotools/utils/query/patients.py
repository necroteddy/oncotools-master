'''
This module contains a collection of predefined queries to interact with
the Oncospace database. These classes are all instantiated in the `Database`
class, for direct access to all the predefined procedures.
'''

# PatientRepresentations =================================================

class PatientsQueries(object):
    '''
    Queries on the `PatientRepresentations` table.

    Positional arguments:
        :oncospace: Database class connected to an Oncospace database
    '''

    def __init__(self, oncospace):
        '''
        Initialize this class with a database connection
        '''
        self.oncospace = oncospace

    def get_all_patient_ids(self):
        '''
        Get a list of all Patient IDs

        Returns:
            Table of patientRepID's and patientID's
        '''
        queryString = 'SELECT patientID FROM Patients ORDER BY patientID asc'
        res = self.oncospace.run(queryString)
        return [row.patientID for row in res.rows]

    def get_patient_info(self, patientID=None):
        '''
        Get patient metadata
        '''
        query = '''
            SELECT patientID, ageAtRefDate, diagnosisICD9, diagnosisICD10
            FROM Patients
            {}
            ORDER BY patientID asc
        '''.format('WHERE patientID={}'.format(patientID) if patientID else '')
        return self.oncospace.run(query)
