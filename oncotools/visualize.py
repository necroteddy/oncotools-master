'''
This module contains a collection of methods that help visualize Mask and DoseMap objects.
Mask visualizations can be performed using the matplotlib or .obj filetypes.
DoseMap visualizations include gradients for color based on Dose stength in a given region.

matplotlib visualizations are best for quick checks of mask structure
while debugging scripts or performing data validation.
To perform inline plots in an iPython Notebook, add this line after importing visualize.py:

.. code-block:: python

    %matplotlib inline

.obj visualizations are best for storing visualizations of DoseMaps.
Recommended application for openning .obj files is MeshLab: http://meshlab.sourceforge.net
'''
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import numpy as np


def visualize_point_cloud(cloud, title=None, alpha=1.0):
    '''
    3D Scatter plot of a point cloud using matplotlib.
    Use this method for quickly visualizing data while debugging or performing data validation.

    Positional arguments:
        :cloud_list: List of point clouds to show
    '''
    ax = Axes3D(plt.figure(1))
    ax.plot(cloud[:, 0], cloud[:, 1], cloud[:, 2], 'bo', alpha=alpha)
    if title:
        ax.set_title(title, fontdict=None, loc='center')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()


def visualize_point_clouds(cloud_list, title=None, alpha=1.0):
    '''
    3D Scatter plot of multiple point clouds using matplotlib.
    Use this method for quickly visualizing data while debugging or performing data validation.

    Positional arguments:
        :cloud_list: List of point clouds to show
    '''
    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'w']
    ax = Axes3D(plt.figure(1))
    if type(alpha) == list and len(alpha) == len(cloud_list):
        for i, cloud in enumerate(cloud_list):
            ax.scatter(
                cloud[:, 0],
                cloud[:, 1],
                cloud[:, 2],
                alpha=alpha[i],
                color=colors[i])
    else:
        for i, cloud in enumerate(cloud_list):
            ax.scatter(
                cloud[:, 0],
                cloud[:, 1],
                cloud[:, 2],
                alpha=alpha,
                color=colors[i])
    if title:
        ax.set_title(title, fontdict=None, loc='center')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()


def visualize_mask(msk, cameraElev=None, cameraAzim=None, alpha=1.0):
    '''
    3D Scatter plot of mask using matplotlib.
    Use this method for quickly visualizing data while debugging or performing data validation.
    Keyword arguments specify the location of the camera for the 3D plot.

    Positional arguments:
        :msk: A mask to plot.

    Keywork arguments:
        :cameraElev: position on the z axis to place the camera (between 0 and max index of z axis)
        :cameraAzim: azimuth rotation angle to adjust the camera's view (value between 0 and 360)
        :alpha: opacity of points (0.0-1.0)
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    pts = msk.data.nonzero()
    ax.scatter(pts[2], pts[1], pts[0], alpha=alpha)
    ax.view_init(elev=cameraElev, azim=cameraAzim)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()


def visualize_masks(msks,
                    cameraElev=None, cameraAzim=None, alpha=None,
                    xLabel='X',
                    yLabel='Y',
                    zLabel='Z'):
    '''
    3D Scatter plot of mask using matplotlib.
    Use this method for quickly visualizing data while debugging or performing data validation.
    Keyword arguments specify the location of the camera for the 3D plot.

    Positional arguments:
        :msks: List of masks to plot.

    Keywork arguments:
        :cameraElev: position on the z axis to place the camera (between 0 and max index of z axis)
        :cameraAzim: azimuth rotation angle to adjust the camera's view (value between 0 and 360)
        :alpha: opacity of points (0.0-1.0)
    '''
    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'w']
    if len(msks) > 8:
        raise ValueError('Too many masks. Can plot up to 8 at a time')
    if isinstance(alpha, list) and len(alpha) != len(msks):
        raise ValueError('List of alphas must be same length as masks')
    else:
        alpha = [1.0]*len(msks)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i, msk in enumerate(msks):
        pts = msk.data.nonzero()
        ax.scatter(pts[2], pts[1], pts[0], alpha=alpha[i], color=colors[i])
        ax.view_init(elev=cameraElev, azim=cameraAzim)
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_zlabel(zLabel)
    plt.show()


def visualize_mask_edges(msk, cameraElev=None, cameraAzim=None):
    '''
    3D Scatter plot of mask only of edge voxels using matplotlib.
    Use this method for quickly visualizing data while debugging or performing data validation.
    Keyword arguments specify the location of the camera for the 3D plot.

    Positional arguments:
        :msk: A mask to plot.

    Keywork arguments:
        :cameraElev: position on the z axis to place the camera (between 0 and max index of z axis)
        :cameraAzim: azimuth rotation angle to adjust the camera's view (value between 0 and 360)
    '''
    visualize_mask(
        msk.get_mask_edge_voxels(),
        cameraElev=cameraElev,
        cameraAzim=cameraAzim)


def mask_to_obj(msk, fileName):
    '''
    Output a .obj file representing mask voxels.

    Positional arguments:
        :msk: A mask to plot.
        :fileName: Name of a file to write to (.obj file type will be appended to fileName).
    '''
    data = msk.data.nonzero()
    output = open(fileName + '.obj', 'w')
    for i in range(len(data[0])):
        output.write('v ' + str(data[2][i]) + ' ' + str(data[1][i]) + ' ' +
                     str(data[0][i]) + ' .666 .666 .666\n')
    output.close()


def mask_edges_to_obj(msk, fileName):
    '''
    Output a .obj file representing a mask's edge voxels.

    Positional arguments:
        :msk: A mask to plot.
        :fileName: Name of a file to write to (.obj file type will be appended to fileName).
    '''
    mask_to_obj(msk.get_mask_edge_voxels(), fileName)


def visualize_dose_mask(dose_map,
                        cameraElev=None,
                        cameraAzim=None,
                        xLabel='X',
                        yLabel='Y',
                        zLabel='Z'):
    '''
    Visualize a dose map. Voxels will be assigned a color based on dose strength at that region.
    Use this method for quickly visualizing data while debugging or performing data validation.
    Keyword arguments specify the location of the camera for the 3D plot.
    Gradient for voxel coloring will be automatically generated
    based on minimum and maximum dose in the dose_map.

    Positional arguments:
        :dose_map: A doseMask object to plot.

    Keywork arguments:
        :cameraElev: position on the z axis to place the camera (between 0 and max index of z axis)
        :cameraAzim: azimuth rotation angle to adjust the camera's view (value between 0 and 360)
    '''
    pts = dose_map.data.nonzero()
    ptsAndDoses = [(pts[0][ind], pts[1][ind], pts[2][ind],
                    dose_map.data[pts[0][ind]][pts[1][ind]][pts[2][ind]])
                   for ind, _ in enumerate(pts[0])]

    jet = plt.get_cmap('plasma')
    cNorm = colors.Normalize(vmin=0, vmax=np.amax(dose_map.data))
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
    allDem = []
    for i in range(10):
        colorVal = scalarMap.to_rgba(i + .3)
        allDem.append(colorVal)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for ind, tup in enumerate(ptsAndDoses):
        colorVal = scalarMap.to_rgba(tup[3])
        arr = np.array([colorVal[0], colorVal[1], colorVal[2]])
        ax.scatter(tup[2], tup[1], tup[0], depthshade=False, c=arr)

    ax.view_init(elev=cameraElev, azim=cameraAzim)
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_zlabel(zLabel)
    plt.show()
    scalarMap.set_array(cNorm)
    cbar = fig.colorbar(scalarMap, orientation='vertical')


def dose_mask_to_obj(dose_map, fileName):
    '''
    Output a .obj file representing a dose map.
    Voxels will be assigned a color based on dose strength at that region.
    Gradient for voxel coloring will be automatically generated
    based on minimum and maximum dose in the dose_map.
    Color is applied using .obj's per-vertex coloring.

    Positional arguments:
        :dose_map: A doseMap object to plot.
        :fileName: Name of a file to write to (.obj file type will be appended to fileName)
    '''
    pts = dose_map.data.nonzero()
    ptsAndDoses = [(pts[0][ind], pts[1][ind], pts[2][ind],
                    dose_map.data[pts[0][ind]][pts[1][ind]][pts[2][ind]])
                   for ind, _ in enumerate(pts[0])]

    jet = plt.get_cmap('plasma')
    cNorm = colors.Normalize(vmin=0, vmax=np.amax(dose_map.data))
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
    allDem = []
    for i in range(10):
        colorVal = scalarMap.to_rgba(i + .3)
        allDem.append(colorVal)

    output = open(fileName + '.obj', 'w')

    for ind, tup in enumerate(ptsAndDoses):
        colorVal = scalarMap.to_rgba(tup[3])
        output.write('v ' + str(tup[2]) + ' ' + str(tup[1]) + ' ' +
                     str(tup[0]) + ' ' + str(colorVal[0]) + ' ' +
                     str(colorVal[1]) + ' ' + str(colorVal[2]) + '\n')

    output.close()
