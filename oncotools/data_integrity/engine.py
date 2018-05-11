from oncotools.connect import Database
from oncotools.utils.query.patient_representations import PatientRepresentationsQueries
from oncotools.utils.query.regions_of_interest import RegionsOfInterestQueries

from oncotools.data_integrity.Manager import Manager
from oncotools.data_integrity.Statistics import Statistics
import oncotools.visualize as visual
#from oncotools.data_integrity.Reader import Reader
#import data

import numpy as np

class engine(object):
    def __init__(self, None, None, db = 'OncospaceHeadNeck', us='oncoguest', pw='0ncosp@ceGuest'):
        #connect to database
        self.dbase = Database(db, us, pw) #how to close?

        #initialize query classes
        self.PRQ = PatientRepresentationsQueries(self.dbase)
        self.ROIQ = RegionsOfInterestQueries(self.dbase)

        #initialize manager classes
        self.manager = Manager()
        self.stat = Statistics()

        self.moduleDic = {}
        self.moduleDic.update(self.validator.modules())
        #make this dynamic later

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

    def point_run(self, modules = "All", masks = "All"):
        '''
        Runs data set through error detection modules prompting user every time error is detected

        Keyword arguments:
            :modules:    (default='All') Which modules should be used?
            Options are "All" or an array of modules indicating which modules to use module_List() to see list

            :masks:       (default='All') Which masks should be analysed?
            Options are "All" or an array of Roi masks names indicating which masks to look at use masks_ROI() to see list of masks
        '''
        #create patient  list
        patients = PRQ.get_patient_id_LUT()
        masks = ROIQ.get_roi_names()
        module = 'dose'
        output = []
        #output = np.tile(-1, (10, len(masks)))#(len(patients), len(masks)))
        i = 0
        v = False
        #print(len(patients))
        #print(len(masks))
        for key in patients:
            j = 0
            print("Patient %f out of %f"%(i, len(patients)))
            RTS_information = np.array(RSQ.get_session_ids(key).to_array())
            #print(RTS_information)
            RTS_IDs = RTS_information[:,0]
            row = []
            for ID in RTS_IDs:
                print("Patient %f, %s"%(i, ID))
                dosegrid = RSQ.get_dose_grid(ID)
                valid = manager.runModule(dosegrid, module)
                row.append(valid)
                #print(row)
                j = j + 1
            output.append(row)
            #print(output)
            #for name in masks2:
                #print("Patient %f, Mask %f"%(i, j))
                #pull mask from ROI
                #ROI_ID = ROIQ.get_id_by_patient_rep_id_name(key, name)
            '''
                if ROI_ID is not None: # mask exists
                    #print("Patient %f, Mask %f"%(i, j))
                    tempmask = ROIQ.get_mask(ROI_ID)
                    dosegrid = RSQ.get_dose_grid(patients[key])
                    mask = DoseMask(tempmask, dosegrid).compute_dose_mask()

                    if v is False:
                        print('visual start')
                        visual.visualize_mask(mask, None, None, 0.1)
                        v = True
                        print('visual done')

                    valid = manager.runModule(mask, module)
                    output[i][j] = valid
                    #print("State: %f"%(output[i][j]))
                    #print("Patient %f, Mask %f, State %f"%(i, j, output[i][j]))
                j = j + 1
            '''
            i = i + 1
            if i is 100:
                break;
        output = np.array(output)
        np.savetxt('output2.txt', output, fmt='%i')


        '''
        for key in patients:
            assessement = AQ.get_assessment_names(key)
            print(assessement)
        '''

    def run(self, modules = "All", masks = "All"):
        '''
        Runs data set through error detection modules without prompting user every time error is detected

        Keyword arguments:
            :modules:    (default='All') Which modules should be used?
            Options are "All" or an array of modules indicating which modules to use module_List() to see list

            :masks:       (default='All') Which masks should be analysed?
            Options are "All" or an array of Roi masks names indicating which masks to look at use masks_ROI() to see list of masks
        '''
        #create paitent list
        patients = self.PRQ.get_patient_id_LUT()

        if modules == "All":
            module = self.module_List()
        if masks == "All":
            masks = self.masks_ROI()
        #itterate through patients
        for key in patients:
            for name in masks:
                #pull mask from ROI
                ROI_ID = self.ROIQ.get_id_by_patient_rep_id_name(key, name)
                mask = self.ROIQ.get_mask(ROI_ID)
                for module in modules:
                    valid = Validator.runModule(module, mask)
                    if valid[1] == False:
                        self.anamoly.insert(key, mask, valid[3], name)

    def report_compile(self):
        self.report.statCompile

    def print_reports(self):
        self.report.toScreen

if __name__ =="__main__":
    t=engine()
    t.testFunc()
