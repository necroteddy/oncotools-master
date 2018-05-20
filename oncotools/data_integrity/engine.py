import numpy as np
import sys
sys.path.insert(0, '../../')

from oncotools.connect import Database

from oncotools.data_integrity.Manager import Manager
from oncotools.utils.query.patient_representations import PatientRepresentationsQueries
from oncotools.data_integrity.Statistics import Report

class engine(object):
    def __init__(self, dr=None, ho=None, db='OncospaceHeadNeck', us='oncoguest', pw='0ncosp@ceGuest'):
        #connect to database
        self.dbase = Database(dr, ho, db, us, pw)
        self.manager = Manager()

    def modules(self):
        '''
        Prints avaiable modules to screen
        '''
        for i in self.manager.getModules():
            print(i)

    def module_List(self):
        '''
        Prints a list of all module names
        '''
        print(self.manager.getModules())

    def data_List(self):
        '''
        Returns a list of all module names
        '''
        print(self.manager.get_data_type())

    def masks_ROI(self):
        '''
        return the Roi names of all masks
        '''
        return self.ROIQ.get_roi_names()

    def run(self, datatype, patient_IDs = "All", module = "All", outfile = "output.txt"):
        '''
        Runs data set through error detection modules prompting user every time error is detected

        Keyword arguments:
            :modules:    (default='All') Which modules should be used?
            Options are "All" or an array of modules indicating which modules to use module_List() to see list

            :datatype:       (default='All') What should be analysed?
            Options are "All" or an array of data names indicating which masks to look at use data_List() to see list of masks

            :outputfile:      (default='output.txt') Prints output to file
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

        output = []
        for ID in patient_representation_IDs:
            patient_data = self.manager.find_data(self.dbase, ID, datatype)
            row = []
            #print(ID)
            for data in patient_data:
                valid = self.manager.runModule(data, module)
                row.append(valid)
            output.append(row)

        output = np.array(output)
        np.savetxt(outfile, output, fmt='%i')

    def report_compile(self, outfile):
        self.report = Report(outfile)
        self.report.statCompile

    def print_reports(self):
        self.report.toScreen

if __name__ =="__main__":
    t=engine()
    t.run()
