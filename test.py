'''
Test runner:
Runs all tests in the test directory using `unittest`
'''

# Imports
import sys
import unittest

import numpy as np
from oncotools.data_integrity.Manager import Manager

from oncotools.connect import Database
from oncotools.utils.query.patient_representations import PatientRepresentationsQueries
from oncotools.utils.query.regions_of_interest import RegionsOfInterestQueries
from oncotools.utils.query.assessments import AssessmentsQueries
import oncotools.visualize as visual

# Test directory
TESTDIR = 'tests'

# Valid flags that can be provided
VALID_FLAGS = [
    '--help', '-h',
    '--quiet', '--default', '--verbose',
    '-q', '-d', '-v'
]

# HELPER METHODS ==================================================================================

def get_help():
    '''
    Print the help message, and exit the process
    '''
    help_str = '''
    ---- HELP ----

    Usage: python test.py [flags]

    flags:
        -h, --help:     print this message
        -q, --quiet:    quiet output, get total numbers of tests and results
        -d, --default:  print a dot for each test (or E and F for errors and failures)
        -v, --verbose:  verbose output when running tests
    '''
    sys.stdout.write(help_str)
    sys.exit()

def flag_error():
    '''
    Print an error if conflicting flags are given, and exit the process
    '''
    flag_str = '''
    Usage: python test.py [flags]

    ERROR: Too many flags provided. Only use ONE of the following:
        -q, --quiet:    quiet output, get total numbers of tests and results
        -d, --default:  print a dot for each test (or E and F for errors and failures)
        -v, --verbose:  verbose output when running tests
    '''
    sys.stdout.write(flag_str)
    sys.exit()

def parse_flags(flags):
    '''
    Parse the flags

    Returns verbosity code for test runner (or exits if flags signal an error)
    '''
    verbosity_flags = []
    for f in flags:
        # If the user asks for help, print the help string and exit
        if '-h' in f:
            get_help()
        # If the user provided one of the flags for verbosity
        if ('-q' in f) or ('-v' in f) or ('-d' in f):
            start_idx = f.rfind('-')
            verbosity_flags.append(f[start_idx:start_idx + 2])

    # Can only provide one flag for verbosity
    if len(verbosity_flags) > 1:
        flag_error()
    # Set the verbosity level
    else:
        verb_dict = {
            '-q': 0,
            '-d': 1,
            '-v': 2
        }
        return verb_dict[verbosity_flags[0]]


# RUN ALL UNIT TESTS ==============================================================================

if __name__ == '__main__':

    db = 'OncospaceHeadNeck'
    us = 'oncoguest'
    pw = '0ncosp@ceGuest'
    #connect to database
    dbase = Database(None, None, db, us, pw) #how to close?

    #initialize query classes
    PRQ = PatientRepresentationsQueries(dbase)
    ROIQ = RegionsOfInterestQueries(dbase)
    AQ = AssessmentsQueries(dbase)
    manager = Manager()

    #create patient  list
    patients = PRQ.get_patient_id_LUT()
    masks = ROIQ.get_roi_names()
    #module = 'extent'
    module = 'surface'
    #module = 'volume'
    output = np.tile(-1, (10, len(masks)))#(len(patients), len(masks)))
    i = 0
    j = 0
    v = False
    #print(len(patients))
    #print(len(masks))
    for key in patients:
        j = 0
        #print("Patient %f out of %f"%(i, len(patients)))
        for name in masks:
            #print("Patient %f, Mask %f"%(i, j))
            #pull mask from ROI
            ROI_ID = ROIQ.get_id_by_patient_rep_id_name(key, name)
            if ROI_ID is not None: # mask exists
                print("Patient %f, Mask %f"%(i, j))
                mask = ROIQ.get_mask(ROI_ID)
                if v is False:
                    print('visual start')
                    visual.visualize_mask(mask, None, None, 0.1)
                    v = True
                    print('visual done')
                valid = manager.runModule(mask, module)
                output[i][j] = valid
                print("State: %f"%(output[i][j]))
                #print("Patient %f, Mask %f, State %f"%(i, j, output[i][j]))
            j = j + 1
        i = i + 1
        if i is 10:
            break;
    np.savetxt('output2.txt', output, fmt='%i')


    '''
    for key in patients:
        assessement = AQ.get_assessment_names(key)
        print(assessement)
    '''

    """
    # Parse the flags
    flags = []
    bad_flags = []
    for f in sys.argv[1:]:
        if f in VALID_FLAGS:
            flags.append(f)
        else:
            bad_flags.append(f)
    # If there are unknown flags, give help and quit
    if bad_flags:
        sys.stdout.write(
            '\n    ERROR! One or more invalid flags provided: {}\n'.format(', '.join(bad_flags)))
        get_help()

    # Default verbosity
    VERBOSITY = 1
    # Check the flags for verbosity arguments
    if flags:
        VERBOSITY = parse_flags(flags)

    # Create the test suite, discover all the tests
    test_suite = unittest.TestLoader().discover(TESTDIR)
    # Create the test runner
    runner = unittest.TextTestRunner(verbosity=VERBOSITY)

    # Run the tests!
    sys.stdout.write('Starting unit tests!\n')
    runner.run(test_suite)
    """
