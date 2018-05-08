import pickle
import numpy as np


def read(filename):
    '''
    Read in an oncotools binary object. Must have .obo file extension.
    '''
    if filename.find('.obo') == -1:
        filename = filename + '.obo'
    fhandle = open(filename, 'r')
    obj = pickle.load(fhandle)
    fhandle.close()
    return obj


def write(obj, filename):
    '''
    Write data to binary file.
    '''
    # Check that there are no unwanted characters in the filename
    bad_chars = ':*<>|?"'
    invalid_chars = np.asarray([filename.find(c) for c in bad_chars])
    if np.any(invalid_chars > -1):
        err_chars = ''.join([bad_chars[i]
                             for i, v in enumerate(invalid_chars) if v > -1])
        raise Exception(
            'Invalid character: cannot use the following characters {}'.format(err_chars))
    # If already doesn't have the .obo ending
    if filename.find('.obo') != len(filename)-4:
        filename += '.obo'
    fhandle = open(filename, 'w')
    pickle.dump(obj, fhandle)
    fhandle.close()
    return True
