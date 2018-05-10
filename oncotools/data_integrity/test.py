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
    assessement = AQ.get_assessment_names(key)
    print(assessment)
