from oncotools.data_integrity.data.Query_Module import Query_Module
from oncotools.utils.query.radiotherapy_sessions import RadiotherapySessionsQueries
import numpy as np

class data_doses(Query_Module):
    '''
    Predefined query for dose of Radio therapy Sessions
    '''
    def __init__(self):
        self.name = "Query_Data"
        self.function = "Basic Data Query Class."
        self.description = {self.name: self.function}

    def get_data(dbase, ID):
        '''
        gets dose data for specific patient
        
        Keyword arguments:
            :dbase:     Database to connect to
            A Database instance from oncotools.connect
            
            :ID:        Patient id
            A patient representation id
        '''
        #initialize query classes
        RSQ = RadiotherapySessionsQueries(dbase)
        RTS_information = np.array(RSQ.get_session_ids(ID).to_array())
        RTS_IDs = RTS_information[:,0]
        data = []
        for ID in RTS_IDs:
            dosegrid = RSQ.get_dose_grid(ID)
            data.append(dosegrid)
        return data
