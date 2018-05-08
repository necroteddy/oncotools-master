'''
This module contains a collection of predefined queries to interact with
the Oncospace database. These classes are all instantiated in the `Database`
class, for direct access to all the predefined procedures.
'''
from string import Template

# Assessments =================================================

class AssessmentsQueries(object):
    '''
    Queries on the `Assessments` table.

    Positional arguments:
        :oncospace: Database class connected to an Oncospace database
    '''

    def __init__(self, oncospace):
        '''
        Initialize this class with a database connection
        '''
        self.oncospace = oncospace


    def get_assessment_names(self, patientID=None):
        '''
        Get a list of all of a patient's assessment names.

        Positional arguments:
            :patID:     patient ID
        Returns:
            Table of names and count of all assessments
        '''
        query = '''
            SELECT DISTINCT name, count(*) as count 
            FROM ASSESSMENTS {} 
            GROUP BY name
            ORDER BY name asc
        '''.format('WHERE patientID=%s' % patientID if patientID else '')
        return self.oncospace.run(query)


    def get_assessments(self, patID, name=None, startDate=None, stopDate=None):
        '''
        Get all of a patient's assessments.

        Positional arguments:
            :patID:     patient ID

        Keyword arguments:
            :name:          name of the assessment to query
                            Can specify part of name. Case insensitive.
                            (if none given, will get all assessments)
            :startDate:     lower date boundary
            :stopDate:      upper date boundary

        Returns:
            Table of dates and assessment values
        '''
        query = '''
            SELECT name, date, grade
            FROM Assessments 
            WHERE patientID={}
        '''.format(patID)

        if name:
            query += " AND name LIKE '%{}%'".format(name)
        if startDate:
            query += ' AND date >= {}'.format(startDate)
        if stopDate:
            query += ' AND date <= {}'.format(stopDate)

        query += ' ORDER BY name, date asc'
        return self.oncospace.run(query)


    def get_binned_outcomes(self,
                            name,
                            bins=[-30, 7, 45, 90, 180, 300, 500],
                            labels=[
                                'baseline', 'onTreatment', 'endOfTreatment',
                                'acute', 'postacute', 'oneYear'
                            ]):
        '''
        Get a table of outcomes, binned by specified time intervals.

        Positional arguments:
            :name:      name of the assessment to query.
            Can specify part of name. Case insensitive.

        Keyword arguments:
            :bins:      bounds of the bins NOTE: (must have length len(labels)+1)
            :labels:    labels for each time bin
        
        Returns:
            Table of date ranges and assessment values
        '''
        # Check that bins and labels have same length
        if len(bins) != len(labels) + 1:
            raise ValueError(
                'Bin bounds must have length len(labels)+1: {} != {}+1'
                .format(len(bins), len(labels)))
        bins.sort()

        # Main select statement for query
        queryStart = 'SELECT DISTINCT axment.patientID'
        for lab in labels:
            queryStart += ', {0}.{0}'.format(lab)

        # Select patient IDs
        queryBase = '''
            FROM (
                SELECT patientID
                FROM Assessments 
            ) axment
        '''
        # Template for partition aggregator
        binTemplate = Template('''
            LEFT OUTER JOIN (
                SELECT DISTINCT patientid, grade as ${lab} 
                FROM (
                    SELECT patientID, grade, RANK() OVER 
                    (PARTITION BY patientid ORDER BY date) AS Rank from Assessments
                    WHERE name LIKE '%${name}%' AND date >= ${left} AND date < ${right}
                    GROUP BY patientID, date, grade
                ) t 
                where rank=1
            ) ${lab} ON ${lab}.patientID = axment.patientID
            ''')
        for i, lb in enumerate(labels):
            queryBase += binTemplate.substitute(
                lab=lb, name=name, left=bins[i], right=bins[i + 1])

        queryEnd = 'ORDER BY patientID asc'
        query = queryStart + queryBase + queryEnd

        return self.oncospace.run(query)
