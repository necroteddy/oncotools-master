from oncotools.data_integrity.data.Query_Module import Query_Module
from oncotools.utils.query.assessments import AssessmentsQueries

class data_assessments(Query_Module):
    '''
    Predefined query for patient assessments
    '''
    def __init__(self):
        self.name = "Query_Data"
        self.function = "Basic Data Query Class."
        self.description = {self.name: self.function}

    def get_data(dbase, ID):
        '''
        gets assessment data for specific patient
        
        Keyword arguments:
            :dbase:     Database to connect to
            A Database instance from oncotools.connect
            
            :ID:        Patient id
            A patient representation id
        '''
        #initialize query classes
        AQ = AssessmentsQueries(dbase)
        return AQ.get_assessments(ID)
