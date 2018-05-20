import sys
import pandas as pd

'''
The OncospaceStats module contains the classes and methods needed to evaluate the data recieved from the modules.
'''

class Report():
    '''
        Basic report function of reading data into dataframe and outputing results or writing to file
    '''

    def __init__(self, data):
        self.data = pd.read_csv(data);

    def reportAll(self, module = "All"):
        '''
        Returns all reports to screen
        '''
        print(self.data.to_string());

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


class quickStats():
    '''
        Simple implementation that reads data and outputs quick stats
    '''
    def __init__(self, lst):
        self.statlist = lst
        self.numbTrue = -1
        self.numbFalse = -1

    def calcstats(self):
        '''
        function for stat preprocessing
        '''
        self.numbTrue = sum(self.statlist)
        self.numbFalse = len(self.statlist) - self.numbTrue

    def stoutstats(self):
        '''
        prints stats to standard out
        '''
        if self.numTrue == -1:
            self.calcstats()
        else:
            out1 = "There are {} masks with no errors found".format(self.numbTrue)
            out2 = "There are {} masks with errors found".format(self.numbFalse)
            sys.stdout.write(out1)
            sys.stdout.write(out2)
