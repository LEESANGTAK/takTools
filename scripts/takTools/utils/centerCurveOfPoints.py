"""
Author: Tak
Created: 03/04/2025
Updated: 03/04/2025
Version: 1.0
Contact: https://ta-note.com

Description:
This script is an implementation of the Center Curve of Point Cloud algorithm in Maya.
The algorithm takes a set of 3D points and computes a curve that represents the center of the point cloud.
Reference is here: https://github.com/maggielovedd/3D-Point-Cloud-Curve-Extraction-and-Optimization/tree/main
"""

import numpy as np
from scipy.spatial import cKDTree
import maya.cmds as cmds
import time


def thin_line(points, point_cloud_thickness=5, skipCount=0):
    """
    Thins a set of 3D points by projecting them onto their local regression line.

    Args:
    - points (np.array): Input points in the format [[x1, y1, z1], [x2, y2, z2], ...].
    - point_cloud_thickness (float): Radius for local neighborhood of points. Increasing this value will result in more straightened line and takes more time.
    - sample_points (int): Number of points to sample from the beginning. If 0, use all points.

    Returns:
    - np.array: Transformed points.
    - list: Regression lines for each point.
    """

    if skipCount != 0:
        points = points[::skipCount]

    # Construct a KDTree for efficient nearest neighbor queries
    point_tree = cKDTree(points)

    new_points = []          # Transformed points
    regression_lines = []    # Regression lines for each point

    for point in points:
        # Find points within the specified radius
        points_in_radius = point_tree.data[point_tree.query_ball_point(point, point_cloud_thickness)]

        # Compute the mean of these points
        data_mean = points_in_radius.mean(axis=0)

        # Calculate the principal component (3D regression line) for these points
        _, _, vv = np.linalg.svd(points_in_radius - data_mean)
        linepts = vv[0] * np.mgrid[-1:1:2j][:, np.newaxis]
        linepts += data_mean
        regression_lines.append(list(linepts))

        # Project the original point onto the regression line
        ap = point - linepts[0]
        ab = linepts[1] - linepts[0]
        point_moved = linepts[0] + np.dot(ap, ab) / np.dot(ab, ab) * ab
        new_points.append(list(point_moved))

    return np.array(new_points), regression_lines


def sort_points_on_regression_line(points, regression_lines, index, sorted_point_distance, search_distance, direction=1, method='min_angle'):
    """
    Sorts points based on the specified method along the regression line.
    Various method can be applied here, and I found minimum angle gives the best result
    """
    sorted_points = []
    regression_line_prev = regression_lines[index][1] - regression_lines[index][0]
    point_tree = cKDTree(points)

    while True:
        v = regression_lines[index][1] - regression_lines[index][0]
        if np.dot(regression_line_prev, v) < 0:
            v = regression_lines[index][0] - regression_lines[index][1]
        regression_line_prev = v

        distR_point = points[index] + direction * (v / np.linalg.norm(v)) * sorted_point_distance
        points_in_radius = point_tree.data[point_tree.query_ball_point(distR_point, search_distance)]

        if len(points_in_radius) < 1:
            break

        # Minimum angle: choose the point that the line between this point and orginal point align with the regression line of original point
        if method == 'min_angle':
            distR_point_vector = distR_point - points[index]
            angles = [np.arccos(np.dot(distR_point_vector, x - points[index]) / (np.linalg.norm(distR_point_vector) * np.linalg.norm(x - points[index]))) for x in points_in_radius]
            nearest_point = points_in_radius[np.argmin(angles)]
            index = np.where(points == nearest_point)[0][0]

        # Mean: choose the point that is nearest to the center of point in radius
        elif method == 'mean':
            mean_point = np.mean(points_in_radius, axis=0)
            index = (np.linalg.norm(points - mean_point, axis=1)).argmin()

        # Shortest Distance: Choose the point that is closest to the current point.
        # This is a straightforward method and can be computed using the Euclidean distance.
        elif method == 'shortest_distance':
            distances = [np.linalg.norm(x - points[index]) for x in points_in_radius]
            nearest_point = points_in_radius[np.argmin(distances)]
            index = np.where(points == nearest_point)[0][0]

        # Maximum Dot Product: Instead of finding the smallest angle, you can find the point that has the maximum dot product with the regression line.
        # This will give the point that is most aligned with the regression line.
        elif method == 'max_dot_product':
            dot_products = [np.dot(v, x - points[index]) for x in points_in_radius]
            nearest_point = points_in_radius[np.argmax(dot_products)]
            index = np.where(points == nearest_point)[0][0]

        # Density-Based: Choose the point that has the highest density of neighboring points within a certain radius.
        # This can be useful if you want to prioritize areas with a higher concentration of points.
        elif method == 'density_based':
            densities = [len(point_tree.query_ball_point(x, search_distance)) for x in points_in_radius]
            nearest_point = points_in_radius[np.argmax(densities)]
            index = np.where(points == nearest_point)[0][0]

        # Curvature-Based: If the points represent a curve, you can compute the curvature at each point and
        # choose the point with the highest curvature. This will prioritize points that are on sharper bends or turns.
        elif method == 'curvature_based':
            curvatures = []
            for x in points_in_radius:
                neighbors = point_tree.query_ball_point(x, search_distance)
                curvature = 0
                if len(neighbors) > 2:
                    a, b, c = points[neighbors[:3]]
                    curvature = np.linalg.norm(np.cross(b-a, c-a)) / (0.5 * np.linalg.norm(b-c))
                curvatures.append(curvature)
            nearest_point = points_in_radius[np.argmax(curvatures)]
            index = np.where(points == nearest_point)[0][0]

        sorted_points.append(points[index])

    return sorted_points


def sort_points(points, regression_lines, sorted_point_distance=0.2, search_ratio=1.2):
    """
    Sorts points along the regression line in both directions.
    """
    index = 0
    search_distance = sorted_point_distance / search_ratio

    sort_points_left = [points[index]] + sort_points_on_regression_line(points, regression_lines, index, sorted_point_distance, search_distance, direction=1)
    sort_points_right = sort_points_on_regression_line(points, regression_lines, index, sorted_point_distance, search_distance, direction=-1)

    return np.array(sort_points_left[::-1] + sort_points_right)


def create_nurbs_curve_from_points(points):
    """
    Creates a NURBS curve in Maya from the given points.

    Args:
    - points (np.array): Array of points in the format [[x1, y1, z1], [x2, y2, z2], ...].
    """
    curve_points = [(point[0], point[1], point[2]) for point in points]
    crv = cmds.curve(p=curve_points, d=3)
    return crv


def showGUI():
    cmds.window(title="Center Curve of Points", mnb=False, mxb=False)
    cmds.columnLayout(adjustableColumn=True)

    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 100)])
    cmds.text(label='Curvature:')
    cmds.floatField('curvatureFltFld', min=1.0, value=3.0, precision=2, annotation='Higher value will result in a more curved line. Decrease value or select centric vertices manually if produce a too short curve. Default is 3.0')

    cmds.setParent('..')
    cmds.button(label='Create Curve', command=main)

    cmds.showWindow()


def main(*args):
    startTime = time.time()

    # Get user input
    curvature = cmds.floatField('curvatureFltFld', q=True, value=True)

    # Example usage with Maya vertices
    sels = cmds.ls(sl=True, fl=True)
    selected_vertices = cmds.filterExpand(sels, sm=31)
    selected_mesh = cmds.filterExpand(sels, sm=12)
    if not selected_vertices and not selected_mesh:
        cmds.error("Please select vertices or a mesh.")
        return

    if not selected_vertices:
        selected_vertices = cmds.ls(cmds.polyListComponentConversion(selected_mesh, toVertex=True), flatten=True)
    points = np.array([cmds.pointPosition(vertex) for vertex in selected_vertices])

    # Get bounding box width for selected vertices
    bounding_box = cmds.exactWorldBoundingBox(selected_vertices)
    bounding_box_width = max(bounding_box[3] - bounding_box[0], bounding_box[4] - bounding_box[1], bounding_box[5] - bounding_box[2])

    # Thin and sort points
    thickness = bounding_box_width / curvature
    skip = int(len(selected_vertices) / 1000)  # Optimization: Skip points for faster computation
    thinned_points, regression_lines = thin_line(points, point_cloud_thickness=thickness, skipCount=skip)
    sorted_points = sort_points(thinned_points, regression_lines, sorted_point_distance=thickness)

    # Create NURBS curve from sorted points
    crv = create_nurbs_curve_from_points(sorted_points)
    cmds.rebuildCurve(crv, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=8, d=3)
    cmds.select(crv, r=True)

    if selected_mesh:
        cmds.rename(crv, '{}_centerCurve'.format(selected_mesh[0]))
    else:
        mesh = cmds.listRelatives(cmds.ls(selected_vertices, o=True)[0], p=True)[0]
        cmds.rename(crv, '{}_centerCurve'.format(mesh))

    print("# Execution time: %s seconds" % (time.time() - startTime))
