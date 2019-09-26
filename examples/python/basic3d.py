import time

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R

from polylidar import extractPlanesAndPolygons
from polylidarutil import (generate_test_points, plot_points, plot_triangles, generate_3d_plane, set_axes_equal, plot_planes_3d,
                            plot_triangle_meshes, get_triangles_from_he, get_plane_triangles, plot_polygons, scale_points)

np.random.seed(1)
# generate random plane with hole
plane = generate_3d_plane(bounds_x=[0,10,0.4], bounds_y=[0, 10, 0.5], holes=[[[3,5], [3, 5]]], height_noise=0.02, planar_noise=0.05)
# Generate top of box (causing the hole that we see)
box_top = generate_3d_plane(bounds_x=[3, 5, 0.2], bounds_y=[3, 5, 0.2], holes=[], height_noise=0.02, height=2, planar_noise=0.05)
# Generate side of box (causing the hole that we see)
box_side = generate_3d_plane(bounds_x=[0, 2, 0.2], bounds_y=[0, 2, 0.2], holes=[], height_noise=0.02)
r = R.from_euler('y', -90, degrees=True)
box_side = r.apply(box_side) + [5, 3, 0]
# All points joined together
points = np.concatenate((plane, box_side, box_top))

# Extracts planes and polygons, time
# in practice zThresh would probably be 0.1 with this noise level. Set to large 1.0 to try and force issue of triangle wall climbing.
t1 = time.time()
delaunay, planes, polygons = extractPlanesAndPolygons(points, xyThresh=0.0, alpha=0.0, lmax=1.0, minTriangles=20, zThresh=1.0, normThresh=0.95, normThreshMin=0.5)
t2 = time.time()
print("Took {:.2f} milliseconds".format((t2 - t1) * 1000))
print("Should see two planes extracted, please rotate.")


triangles = np.asarray(delaunay.triangles).reshape(int(len(delaunay.triangles)/ 3), 3)
fig, ax = plt.subplots(figsize=(10, 10), nrows=1, ncols=1, subplot_kw=dict(projection='3d'))
# plot all triangles
plot_planes_3d(points, triangles, planes, ax)
# plot points
ax.scatter(*scale_points(points), c='k')
set_axes_equal(ax)
plt.show()
print("")
# This time WITHOUT normThreshMin. Notice the triangles starting to climb up the wall.
t1 = time.time()
delaunay, planes, polygons = extractPlanesAndPolygons(points, xyThresh=0.0, alpha=0.0, lmax=1.0, minTriangles=20, zThresh=1, normThresh=0.98, normThreshMin=0.01)
t2 = time.time()
print("Took {:.2f} milliseconds".format((t2 - t1) * 1000))
print("Should see two planes extracted with significant triangle wall climbing.")
print("The triangles are climbing because their height is less than zThresh bypassing normal filtering")
print("Use normThreshMin to prevent this issue, forcing all triangles to have planarity no matter their height. This setting was disabled, causing the issues you see.")


triangles = np.asarray(delaunay.triangles).reshape(int(len(delaunay.triangles)/ 3), 3)
fig, ax = plt.subplots(figsize=(10, 10), nrows=1, ncols=1, subplot_kw=dict(projection='3d'))
# plot all triangles
plot_planes_3d(points, triangles, planes, ax)
# plot points
ax.scatter(*scale_points(points), c='k')
set_axes_equal(ax)
plt.show()

print()
print("Final Note: normThreshMin is only required for dense point clouds that are quite noisy.")