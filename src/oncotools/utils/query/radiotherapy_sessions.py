'''
This module contains a collection of predefined queries to interact with
the Oncospace database. These classes are all instantiated in the `Database`
class, for direct access to all the predefined procedures.
'''
from oncotools.data_elements.dose import Dose
from oncotools.utils import file_manager as fm

import numpy as np

# RadiotherapySessions ===================================================

class RadiotherapySessionsQueries(object):
    '''
    Queries on the `RadiotherapySessions` table

    Positional arguments:
        :oncospace: Database class connected to an Oncospace database
    '''

    def __init__(self, oncospace):
        '''
        Initialize this class with a database connection
        '''
        self.oncospace = oncospace

    def get_session_ids(self, patientRepID):
        '''
        Get the radiotherapy session (RTS) ID's
        related to the patient representation ID

        Positional arguments:
            :patientRepID:  patient representation ID
        Returns:
            List of RTS ID's associated with the patient
        '''
        try:
            # For new style database with composite RTS
            rtsidQuery = """
                SELECT ID, description, compositeType, isDerived 
                FROM RadiotherapySessions
                WHERE patientRepID = {0}""".format(patientRepID)
            return self.oncospace.run(rtsidQuery)
        except:
            # If operating on a pre-composite database schema
            rtsidQuery = """
                SELECT ID, description 
                FROM RadiotherapySessions
                WHERE patientRepID = {0}""".format(patientRepID)
            return self.oncospace.run(rtsidQuery)

    def get_dose_grid(self, rtSessionID, output=None):
        '''
        Get the dose grid associated with a RTS ID

        Positional arguments:
            :rtSessionID:   an integer, or a comma-separated string of patientIDs,
                            e.g., "1,2,3,4"
        Keyword arguments:
            :output:        file name to write the dose grid to.
                Doesn't output dose grid if argument is not given.
        Returns:
            :dose:  a dose.dose() instance.
        '''
        # NOTE: TEXTSIZE is set to 2GB to prevent truncation by FreeTDS
        queryString = """
            SET TEXTSIZE 2147483647;
            SELECT rts.ID, doseGrid,
            xStart, yStart, zStart,
            xVoxelSize, yVoxelSize, zVoxelSize,
            xDimension, yDimension, zDimension
            FROM RadiotherapySessions rts
            WHERE rts.ID = {0}""".format(rtSessionID)
        result = self.oncospace.run(queryString).rows[0]
        if not result[1]:
            return None

        # Create a dose object
        origin = [float(result[2]), float(result[3]), float(result[4])]
        spacing = [float(result[5]), float(result[6]), float(result[7])]
        dim = [int(result[8]), int(result[9]), int(result[10])]
        # Reshape as Z,Y,X
        doseGrid = np.reshape(
            np.frombuffer(result[1], dtype=np.float32), (dim[2], dim[1],
                                                         dim[0]))

        d = Dose()
        d.set_dose(doseGrid)
        d.set_size(dim)
        d.dimension = len(dim)
        d.set_spacing(spacing)
        d.set_origin(origin)
        d.update_end()

        # Write dose grid to file if filename is specified
        if isinstance(output, str):
            fm.write(d, output)

        return d

    def get_dose(self, patientRepID):
        '''
        Get all Dose objects associated with a patient representation

        Positional arguments:
            :patientRepID:  patient representation ID
        Returns:
            Dictionary of RTS description: Dose object
        '''
        rts_ids = self.get_session_ids(patientRepID)
        doses = {str(row[1]): self.get_dose_grid(row[0]) for row in rts_ids.rows}
        return doses
