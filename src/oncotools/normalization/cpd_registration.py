from copy import deepcopy
import time
import threading
import numpy as np

from oncotools.normalization.registration import Registration
from oncotools.normalization.cpd.cpd_plot import cpd_plot
import oncotools.normalization.cpd as cpd

def com_align(x, y):
    '''
    For non-rigid registration with CPD,
    the preprocessing step involves aligning the point clouds at their centers.

    Positional arguments:
        :x: n-by-d fixed point cloud
        :y: n-by-d moving point cloud

    Returns:
        List of preprocessed point clouds
    '''
    # Calculate the center of mass of the points
    xc = np.mean(x, axis=0)
    yc = np.mean(y, axis=0)
    # And the difference between the two
    cdiff = xc - yc
    # Move the points in Y to be centered at X
    ret = deepcopy(y)
    for idx, yi in enumerate(ret):
        ret[idx] = yi + cdiff
    return x, ret


def register(X,
             Y,
             lamb=3.0,
             beta=2.0,
             plateau_thresh=1.0e-5,
             plateau_length=20):
    '''
    Register Y to X using Coherent Point Drift
    '''
    ret = {'clouds': {}, 'params': {}, 'metrics': {}}
    start_time = time.time()
    T, g, wc, errors = cpd.register_nonrigid(
        X,
        Y,
        0.0,
        lamb=lamb,
        beta=beta,
        plateau_thresh=plateau_thresh,
        plateau_length=plateau_length)
    ret['clouds']['output'] = T
    ret['params']['G'] = g
    ret['params']['w'] = wc
    ret['params']['z'] = np.dot(g, wc)
    ret['metrics']['runtime'] = time.time() - start_time
    ret['metrics']['error'] = errors
    ret['metrics']['iterations'] = len(errors)
    return ret


class CPDRegistration(Registration):
    '''
    The CPDRegistration object is an implementation of the Registration class.
    Performs a non-rigid registration of two masks using the Coherent Point Drift (CPD) algorithm.
    '''

    def __init__(self,
                 dbconn,
                 fixed_patient,
                 moving_patient,
                 roi_list,
                 use_surfaces=False,
                 sampling=None,
                 crop=False,
                 plateau_thresh=1.0e-5,
                 plateau_length=20):
        super(CPDRegistration, self).__init__(
            dbconn,
            fixed_patient,
            moving_patient,
            roi_list,
            use_surfaces=use_surfaces,
            sampling=sampling,
            crop=crop)
        self.registration_type = 'CPDRegistration'
        # Stopping criteria
        self.plateau_thresh = plateau_thresh
        self.plateau_length = plateau_length

    def preprocess(self):
        '''
        For non-rigid registration with CPD,
        the preprocessing step involves aligning the point clouds at their centers.

        Returns:
            List of preprocessed point clouds
        '''
        # Get the point clouds
        pt_clouds = self.get_point_clouds()
        x = pt_clouds[self.fixed_patient]
        y = pt_clouds[self.moving_patient]

        # Find the centers of mass...
        xc = np.mean(x, axis=0)
        yc = np.mean(y, axis=0)
        # ...and compute difference between the two
        cdiff = xc - yc

        # Align the two clouds
        x, ret = com_align(x, y)

        self.clouds['preprocess'] = ret
        self.params['preprocess'] = cdiff
        return x, ret

    def register(self):
        # The initial alignment step
        X, Y = self.preprocess()
        # Perfrom nonrigid registration
        start_time = time.time()
        T, g, wc, errors = cpd.register_nonrigid(
            X,
            Y,
            0.0,
            lamb=3.0,
            beta=2.0,
            plateau_thresh=self.plateau_thresh,
            plateau_length=self.plateau_length)
        self.clouds['output'] = T
        self.params['G'] = g
        self.params['w'] = wc
        self.params['z'] = np.dot(g, wc)
        self.metrics['runtime'] = time.time() - start_time
        self.metrics['error'] = errors
        self.metrics['iterations'] = len(errors)
        return self.clouds['output']

    def plot(self):
        '''
        Plot the initial masks compared to the deformed masks using matplotlib plotting library.
        '''
        cpd_plot(self.clouds[self.fixed_patient],
                 self.clouds[self.moving_patient], self.clouds['output'])

    def plot_clouds(self, clds):
        '''
        Generalized plotting function to specify which masks to plot.

        Positional arguments:
            :clds:  list of point clouds to plot

        Returns:
            Two matplotlib 3D plots, comparing cloud 0 to 1 and 0 to 2.
        '''
        if len(clds) != 3:
            raise ValueError("Must give list of 3 items for parameter")
        cpd_plot(clds[0], clds[1], clds[2])


class CPDRegistrationThread(threading.Thread):
    '''
    Thread to register a set of point clouds to a fixed point cloud.

    Positional arguments:
        :base_cloud:    fixed point cloud
        :cloud_list:    list of moving point clouds
    '''

    def __init__(self,
                 base_cloud,
                 cloud_list,
                 plateau_thresh=1.0e-5,
                 plateau_length=20):
        threading.Thread.__init__(self)
        self.base_cloud = base_cloud
        self.cloud_list = cloud_list
        self.output = []
        self.plateau_thresh = plateau_thresh
        self.plateau_length = plateau_length

    def run(self):
        self.output = [
            register(
                self.base_cloud,
                c,
                plateau_thresh=self.plateau_thresh,
                plateau_length=self.plateau_length) for c in self.cloud_list
        ]
