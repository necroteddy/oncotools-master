
# coding: utf-8

# # Demo: Oncotools

# ### Import modules

# In[1]:


from oncotools.connect import Database
from oncotools.data_elements.dose_map import DoseMask

import numpy as np


# ### Connect to the database

# In[2]:


db = Database(db='OncospaceHeadNeck', us='oncoguest', pw='0ncosp@ceGuest')


# ### Patient ID and Patient representation ID
# 
# Individual patients are identified by a patientID. 
# 
# Each patient has at least one patient representations. A patient representation corresponds to one scan (a certain geometry) and a set of structures from that one scan.

# In[3]:


# Map patient representation ID to patient ID
patLUT = db.patient_representations.get_patient_id_LUT()

# Map patient ID to patient representation ID(s)
prepLUT = db.patient_representations.get_patient_rep_id_LUT()


# ### Get a list of ROI's
# 
# Get a list of all the ROI's in the database

# In[4]:


db.regions_of_interest.get_roi_names()


# ### Get a list of patients with certain ROIs

# In[5]:


# Pick an ROI or a list of ROI's
rois = ['l_parotid', 'r_parotid']


# In[6]:


# Get a list of patient representation's with all the ROI's we specified
patient_list = db.regions_of_interest.get_patient_rep_ids_with_rois(rois)
print len(patient_list), 'patient representations with given ROI\'s'


# In[7]:


# Let's pick one of these patients
mypatient = patient_list[0]


# # The major data types:

# ## Regions of Interest (ROIs)
# 
# Binary masks of an anatomical structure or a contour from a patient scan
# The `Roi` class stores information for each ROI, and contains a `Mask` object.
# 
# The image is stored as a 3D matrix with binary values (1 = in the structure, 0 = not in the structure)

# ### Get ROI's or Masks for a set of structures
# 
# `db.regions_of_interest.get_rois()` and `db.regions_of_interest.get_masks()` return:
# - a dictionary mapping ROI name to the Roi/Mask object
# - a list of ROI's that were not found

# In[8]:


# Get certain ROI's for our patient
myrois, _ = db.regions_of_interest.get_rois(mypatient, rois)
myrois


# In[9]:


# We can also get just the masks
mymasks, _ = db.regions_of_interest.get_masks(mypatient, rois)
mymasks


# In[10]:


# Let's pick a mask
amask = mymasks['l_parotid']


# Masks are images with the following fields

# In[11]:


print amask


# They are represented as a 3D bitmap. Note that the X and Z coordinates are reversed in the data matrix, so be careful directly indexing the data matrix.

# In[12]:


print amask.data.shape


# Masks can also be represented as a point cloud in physical coordinates

# In[13]:


mymasks['l_parotid'].transform_to_point_cloud()


# ## Dose Grids
# 
# Dose grids store the dose that is delivered to a patient for treatment.
# 
# Image data is stored as a 3D matrix with `float` values for the dose at each voxel

# ### Get a dose grid
# 
# `db.regions_of_interest.get_rois()` returns a dictionary mapping the dose grid name to the `Dose` object

# In[14]:


mydoses = db.radiotherapy_sessions.get_dose(mypatient)
mydoses


# In[15]:


# Let's pick a dose grid
adose = mydoses['trial']


# ## Dose Masks
# 
# Dose masks map a dose grid onto an ROI. Since the dose grids and the ROI's are on different coordinate systems, this process involves a coordinate transformation and interpolation.
# 
# Image data is stored as a 3D matrix with `float` values for the dose at each voxel in the ROI

# ### Construct a dose mask object
# 
# Specify a mask and a dose grid to construct a `DoseMask`

# In[16]:


dm = DoseMask(amask, adose)


# In[17]:


print dm


# ### Dose masks have DVH data
# 
# - Column 0: dose values in centigray (x-axis)
# - Column 1: fraction of volume (y-axis)

# In[18]:


dm.dvh_data


# ### Extract certain points from a DVH

# **DX parameters**
# 
# Get the dose to X percent of the structure. For example, D25 (a high dose) is the dose to 25% (0.25) of a structure

# In[19]:


dm.get_dose_to_volume(0.25)


# **VX parameters**
# 
# Get the volume that received a certain dose. For example, V55 is the fraction of the structure that received 5500 cGy

# In[20]:


dm.get_volume_with_dose(5500)

