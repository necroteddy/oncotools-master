.. radio_morphology:

Radio-morphology
======================

Radio-morphologic (RM) analysis refers to a process by which consistently identifiable physical characteristics
of an image can be used to analyze the dose distributions throughout a region of interest (ROI).
Rather that examining the dose distribution on the broad scale of an entire organ
or on the analytically intractable level of individual voxels,
RM analysis selects a level of specificity using prior anatomical understanding to create meaningful substructures.
Parametrically defined shape transformations are used to produce substructures from a given ROI or set of ROI's. 

The concept of RM features is implemented in the `radio_morphology` module and the :ref:`features` classes.

Features
=====================

Features Base Class
-------------------------
.. autoclass:: radio_morphology.feature.Feature
    :members:
