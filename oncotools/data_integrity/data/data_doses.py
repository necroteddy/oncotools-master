class data_doses(Query_Module):
    def __init__():
        self.name = "Query_Data"
        self.function = "Basic Data Query Class."
        self.description = {self.name: self.function}

    def get_data(dbase, ID):
        #initialize query classes
        RSQ = RadiotherapySessionsQueries(self.dbase)
        RTS_information = np.array(RSQ.get_session_ids(ID).to_array())
        RTS_IDs = RTS_information[:,0]
        data = []
        for ID in RTS_IDs:
            dosegrid = RSQ.get_dose_grid(ID)
            data.append(dosegrid)
        return data
