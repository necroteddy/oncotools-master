'''
Test runner:
Runs all tests in the test directory using `unittest`
'''

# Imports
import sys
import unittest

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
