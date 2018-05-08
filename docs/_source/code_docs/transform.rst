.. transform:

Transform
=====================

.. automodule:: transform
    :members:

There are three types of transformations: general, scaling, and partitioning

General
-----------------------

General transformations include many different methods that to allow for manipulation of masks.

.. autoclass:: utils.transformations.general.GeneralTransform
    :members:


Partitioning
-----------------------

Partitioning transformations break down a mask into many smaller masks.

.. autoclass:: utils.transformations.partition.PartitionTransform
    :members:


Scaling
-----------------------

Scaling transformations manipulate masks by expansion and contraction.

.. autoclass:: utils.transformations.scale.ScaleTransform
    :members:

