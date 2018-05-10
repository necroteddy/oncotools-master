from oncotools.connect import Database
from oncotools.utils.query.patient_representations import PatientRepresentationsQueries
from oncotools.utils.query.regions_of_interest import RegionsOfInterestQueries
from oncotools.utils.query.assessments import AssessmentsQueries
#import data

db = 'OncospaceHeadNeck'
us = 'oncoguest'
pw = '0ncosp@ceGuest'
#connect to database
dbase = Database(db, us, pw) #how to close?

#initialize query classes
PRQ = PatientRepresentationsQueries(dbase)
ROIQ = RegionsOfInterestQueries(dbase)
AQ = AssessmentsQueries(dbase)

#create patient  list
patients = PRQ.get_patient_id_LUT()

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
