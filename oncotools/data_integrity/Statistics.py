import sys
from oncotools.data_integrity.AnamalyData import Anomaly
import pandas as pd

'''
The OncospaceStats module contains the classes and methods needed to evaluate the data recieved from the modules.
'''

class Report():
    '''
        will be implemented later as we work out what stats need to be collected
    '''
    
    def __init__(self):
        self.data = Anomaly();
              
    def reportAll(self, module = "All"):
        '''
        Returns all reports to screen
        '''
        self.data.toScreen();
        
    def tocsv(self, file):
        '''
        writes report of information to csv file
        
        Keyword arguments:
            :file: name of file to write to
        '''
        towrite = self.data.topandas
        with open(file, 'w') as csvfile:
            towrite.to_csv(csvfile)
        
    def loaddata(self, loaddata):
        '''
        reads data and loads from csv file
        
        Keyword arguments:
            :loaddata: name of file to load from
        '''
        dataframe = pd.read_csv(loaddata);
        for index, row in dataframe.iterrows():
            self.data.insert(patient = row.patient, mask = row.mask, errortype = row.errortype, ROI = row.ROI)


class Statistics():
    def __init__(self, lst):
        self.statlist = lst
        self.numbTrue = -1
        self.numbFalse = -1

    def calcstats(self):
        self.numbTrue = sum(self.statlist)
        self.numbFalse = len(self.statlist) - self.numbTrue

    def printstats(self):
        if self.numTrue == -1:
            self.calcstats()
        else:
            out1 = "There are {} masks with no errors found".format(self.numbTrue)
            out2 = "There are {} masks with errors found".format(self.numbFalse)
            sys.stdout.write(out1)
            sys.stdout.write(out2)
