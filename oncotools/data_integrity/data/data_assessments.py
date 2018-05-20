from oncotools.data_integrity.data.Query_Module import Query_Module
from oncotools.utils.query.assessments import AssessmentsQueries

class data_assessments(Query_Module):
    def __init__(self):
        self.name = "Query_Data"
        self.function = "Basic Data Query Class."
        self.description = {self.name: self.function}

    def get_data(dbase, ID):
        #initialize query classes
        AQ = AssessmentsQueries(dbase)
        return AQ.get_assessments(ID)
