'''
This module contains a collection of methods that transform and modify mask objects.
'''

from .utils.transformations.general import GeneralTransform
from .utils.transformations.partition import PartitionTransform
from .utils.transformations.scale import ScaleTransform

general = GeneralTransform()
partition = PartitionTransform()
scale = ScaleTransform()
