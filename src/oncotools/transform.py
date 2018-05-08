'''
This module contains a collection of methods that transform and modify mask objects.
'''

from oncotools.utils.transformations.general import GeneralTransform
from oncotools.utils.transformations.partition import PartitionTransform
from oncotools.utils.transformations.scale import ScaleTransform

general = GeneralTransform()
partition = PartitionTransform()
scale = ScaleTransform()
