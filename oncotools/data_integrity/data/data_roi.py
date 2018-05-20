class data_roi(Query_Module):
    def __init__(self):
        self.name = "Query_Data"
        self.function = "Basic Data Query Class."
        self.description = {self.name: self.function}

    def get_data(dbase, ID):
        #initialize query classes
        ROIQ = RegionsOfInterestQueries(self.dbase)
        roi_names = ROIQ.get_roi_names()
        data = []
        for name in roi_names:
            ROI_ID = ROIQ.get_id_by_patient_rep_id_name(ID, name)
            if ROI_ID is not None:
                mask = ROQI.get_mask(ROI_ID)
                data.append(mask)
        return data
