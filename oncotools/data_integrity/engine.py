import numpy as np
import sys
sys.path.insert(0, '../../')

from oncotools.connect import Database
from oncotools.utils.query.patient_representations import PatientRepresentationsQueries
from oncotools.utils.query.regions_of_interest import RegionsOfInterestQueries
from oncotools.utils.query.radiotherapy_sessions import RadiotherapySessionsQueries
from oncotools.utils.query.assessments import AssessmentsQueries
from oncotools.data_elements.dose_map import DoseMask
import oncotools.visualize as visual

from oncotools.data_integrity.Manager import Manager
from oncotools.data_integrity.Statistics import Statistics
import oncotools.visualize as visual
#from oncotools.data_integrity.Reader import Reader
#import data

class engine(object):
    def __init__(self, dr=None, ho=None, db='OncospaceHeadNeck', us='oncoguest', pw='0ncosp@ceGuest'):
        #connect to database
        self.dbase = Database(dr, ho, db, us, pw) #how to close?

    def modules(self):
        '''
        Prints avaiable modules to screen, with description of how to use
        '''
        for key in self.moduleDic:
            print(key)
            print(self.moduleDic[key])

    def module_List(self):
        '''
        Returns a list of all module names
        '''
        output = []
        for key in self.moduleDic:
            output.append(key)

    def masks_ROI(self):
        '''
        return the Roi names of all masks
        '''
        return self.ROIQ.get_roi_names()

    def run(self, patient_IDs = "All", datatype, modules = "All", outfile = "output.txt"):
        '''
        Runs data set through error detection modules prompting user every time error is detected

        Keyword arguments:
            :modules:    (default='All') Which modules should be used?
            Options are "All" or an array of modules indicating which modules to use module_List() to see list

            :masks:       (default='All') Which masks should be analysed?
            Options are "All" or an array of Roi masks names indicating which masks to look at use masks_ROI() to see list of masks
        '''
        PRQ = PatientRepresentationsQueries(self.dbase)
        # Get patient representation IDs from patient IDs
        patient_representation_IDs = []
        if patient_IDs == "All":
            patient_representation_IDs = PRQ.get_patient_id_LUT()
        else: # given patient id, find patient representation id
            patient_ID_dict = PRQ.get_patient_rep_id_LUT()
            for ID in patient_IDs:
                PR_ID = patient_ID_dict[ID]
            patient_representation_IDs.append(PR_ID)

        manager = Manager()
        for ID in patient_representation_IDs:
            patient_data = manager.find_data(ID, datatype)
            row = []
            for data in patient_data:
                valid = manager.runModule(data, module)
                row.append(valid)
            output.append(row)

        output = np.array(output)
        np.savetxt(outfile, output, fmt='%i')

    def report_compile(self):
        self.report.statCompile

    def print_reports(self):
        self.report.toScreen

if __name__ =="__main__":
    t=engine()
    t.run()
