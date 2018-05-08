import oncotools.transform as tf

class Registration(object):
    '''
    Registration base class.
    Contains the general data structure, functions,
    and utility methods to implement different registration algorithms.
    '''

    def __init__(self, dbconn, fixed_patient, moving_patient,
                 roi_list, use_surfaces=False, sampling=None, crop=False):

        self.registration_type = None

        self.dbconn = dbconn
        self.fixed_patient = fixed_patient
        self.moving_patient = moving_patient

        self.roi_list = roi_list
        # Boolean flag on whether or not to use surface mask
        self.use_surfaces = use_surfaces
        # Sampling rates
        self.sampling = sampling
        # Boolean flag on whether or not to crop to non-zero bounds
        self.crop = crop

        # Lists to store masks, images, and point clouds
        self.masks = {}
        self.clouds = {}
        self.images = {}

        # Store other metrics (runtime, error per iteration)
        self.metrics = {
            "runtime": None,
            "error": []
        }
        # Store parameters here
        self.params = {}

    def get_mask(self, prep_id):
        '''
        Return a mask for the specified patient representation.
        '''
        # If the mask was already queried...
        if prep_id in self.masks.keys():
            return self.masks[prep_id]
        # If the mask was not previously queried
        else:
            # Get all ROIs for a patient
            masks, _ = self.dbconn.regions_of_interest.get_masks(prep_id, self.roi_list)
            masks = masks.values()
            # Get the combined mask for all ROIs
            mymask = tf.general.combine_masks(masks) if len(masks) > 1 else masks[0]
            # Perform any preprocessing (cropping, sampling)
            if self.crop:
                mymask = tf.general.crop(mymask)
            if self.sampling:
                # if self.sampling and prep_id != self.fixed_patient:
                mymask = tf.general.downsample(mymask, self.sampling)
            return mymask

    def get_masks(self):
        '''
        Return a dictionary of masks for each patient.
        '''
        # If both masks have not been queried...
        if len(self.masks.keys()) < 2:
            self.masks = {p: self.get_mask(p) for p in [self.fixed_patient, self.moving_patient]}
        # Return the dictionary of masks
        return self.masks

    def get_point_cloud(self, prep_id):
        '''
        Return a point cloud from a mask for a specified patient representation.
        '''
        # If the point cloud was already calculated
        if prep_id in self.clouds.keys():
            return self.clouds[prep_id]
        # If not, calculate and store it
        else:
            mymask = self.get_mask(prep_id)
            mycloud = mymask.transform_to_point_cloud()
            self.clouds[prep_id] = mycloud
            return mycloud

    def get_point_clouds(self):
        '''
        Return a dictionary of point clouds for all specified patients.
        '''
        # If both point clouds have not been made...
        if len(self.clouds.keys()) < 2:
            self.clouds = {p: self.get_point_cloud(
                p) for p in [self.fixed_patient, self.moving_patient]}
        # Return the dictionary of point clouds
        return self.clouds

    def preprocess(self):
        '''
        Any preprocessing steps.
        '''
        raise NotImplementedError(
            "Registration subclasses must implement their own preprocessing steps.")

    def register(self):
        '''
        Conduct the registration process.
        '''
        raise NotImplementedError(
            "Registration subclasses must implement their own registration algorithms.")

    def plot(self):
        '''
        Visualization methods for registration.
        '''
        raise NotImplementedError(
            "Registration subclasses must implement their own visualization algorithms.")
