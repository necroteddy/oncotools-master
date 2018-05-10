'''
This module contains a collection of predefined queries to interact with
the Oncospace database. These classes are all instantiated in the `Database`
class, for direct access to all the predefined procedures.
'''

# PatientRepresentations =================================================

class PatientRepresentationsQueries(object):
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

    def get_all_patient_representation_ids(self):
        '''
        Get a list of all PatientRepresentation IDs and corresponding patient IDs.

        Returns:
            Table of patientRepID's and patientID's
        '''
        queryString = 'SELECT ID, patientID FROM PatientRepresentations ORDER BY ID asc'
        return self.oncospace.run(queryString)

    def get_patient_id_LUT(self):
        '''
        Get a LUT of patient representation ID to patient ID

        Returns:
            Dictionary mapping patientRepID to patientID
        '''
        res = self.get_all_patient_representation_ids()
        return {row.ID: row.patientID for row in res.rows}

    def get_patient_rep_id_LUT(self):
        '''
        Get a LUT of patient ID to patient representation IDs

        Returns:
            Dictionary mapping patientID to list of patientRepID
        '''
        res = self.get_all_patient_representation_ids()
        # Create a dictionary mapping patient ID to an empty list
        myLUT = {row.patientID: [] for row in res.rows}
        # Fill each list with that patient's representations
        for row in res.rows:
            myLUT[row.patientID].append(row.ID)
        return myLUT

    def get_patient_representation(self, patientRepID):
        '''
        Get the fields associated to a patient representation.

        Positional arguments:
            :patientRepID:  patient representation ID
        Returns:
            Dictionary containing fields of a patient representation

            Keys:
                patientRepID\n
                patientID\n
                xStart, yStart, zStart\n
                xVoxelSize, yVoxelSize, zVoxelSize\n
                xDimension, yDimension, zDimension
        '''
        queryString = """
            SELECT ID, patientID, xStart, yStart, zStart,
            xVoxelSize, yVoxelSize, zVoxelSize,
            xDimension, yDimension, zDimension
            FROM PatientRepresentations
            WHERE ID = {0}""".format(patientRepID)

        rep = self.oncospace.run(queryString).rows[0]
        if not rep:
            msg = 'Error in query.PatientRepresentations.\
                GetPatientRepresentation:\n'

            msg += 'Query returned no results. Query string:\n'
            msg += queryString
            raise (Exception(msg))
            return {}
        return {
            'patientRepID': int(rep[0]),
            'patientID': int(rep[1]),
            'xStart': float(rep[2]),
            'yStart': float(rep[3]),
            'zStart': float(rep[4]),
            'xVoxelSize': float(rep[5]),
            'yVoxelSize': float(rep[6]),
            'zVoxelSize': float(rep[7]),
            'xDimension': float(rep[8]),
            'yDimension': float(rep[9]),
            'zDimension': float(rep[10])
        }
