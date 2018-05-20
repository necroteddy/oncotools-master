class data_roi(Query_Module):
    def __init__():
        self.name = "Query_Data"
        self.function = "Basic Data Query Class."
        self.description = {self.name: self.function}

    def get_data(dbase, ID):
        #initialize query classes
        AQ = AssessmentsQueries(self.dbase)
        return AQ.get_assessments(ID)
