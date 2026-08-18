"""
Author: Tak
Created: 03/04/2025
Updated: 08/18/2026
Contact: chst27@gmail.com

Description:
This script is an implementation of the Center Curve of Point Cloud algorithm in Maya.
The algorithm takes a set of 3D points and computes a curve that represents the center of the point cloud.
Reference is here: https://github.com/maggielovedd/3D-Point-Cloud-Curve-Extraction-and-Optimization/tree/main
"""

import numpy as np
from scipy.spatial import cKDTree
from maya.api import OpenMaya as om
import maya.cmds as cmds
import time


DEFAULT_CURVATURE = 3.0  # Default curvature value for the curve creation
TIME_OUT_THRESHOLD = 3.0  # Time threshold in seconds for the curve creation process


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


def sort_points_on_regression_line(points, regression_lines, index, sorted_point_distance, search_distance, direction=1):
    """
    Sorts points based on the specified method along the regression line.
    Various method can be applied here, and I found minimum angle gives the best result
    """
    sorted_points = []
    regression_line_prev = regression_lines[index][1] - regression_lines[index][0]
    point_tree = cKDTree(points)

    start_time = time.time()
    while True:
        if time.time() - start_time > TIME_OUT_THRESHOLD:
            break

        v = regression_lines[index][1] - regression_lines[index][0]
        if np.dot(regression_line_prev, v) < 0:
            v = regression_lines[index][0] - regression_lines[index][1]
        regression_line_prev = v

        distR_point = points[index] + direction * (v / np.linalg.norm(v)) * sorted_point_distance
        points_in_radius = point_tree.data[point_tree.query_ball_point(distR_point, search_distance)]

        if len(points_in_radius) < 1:
            break

        # Minimum angle: choose the point that the line between this point and orginal point align with the regression line of original point
        distR_point_vector = distR_point - points[index]
        angles = [np.arccos(np.dot(distR_point_vector, x - points[index]) / (np.linalg.norm(distR_point_vector) * np.linalg.norm(x - points[index]))) for x in points_in_radius]
        nearest_point = points_in_radius[np.argmin(angles)]
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
    crv = None

    # Remove duplicate points
    unique_points = np.unique(points, axis=0)

    # Ensure there are enough points to create a curve
    if len(unique_points) < 4:  # Minimum points required for a degree-3 curve
        return None

    curve_points = [(point[0], point[1], point[2]) for point in points]
    crv = cmds.curve(p=curve_points, d=3)

    return crv


def showGUI():
    cmds.window(title="Center Curve of Points", mnb=False, mxb=False)
    cmds.columnLayout(adjustableColumn=True)

    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 100)])
    cmds.text(label='Curvature:', annotation='Higher value will result in a more curved line.\nDecrease value or select centric vertices manually if produce a too short curve.\nDefault is 3.0')
    cmds.floatField('curvatureFltFld', min=1.0, value=DEFAULT_CURVATURE, precision=2)

    cmds.setParent('..')
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 100), (2, 100)])
    cmds.text(label='Root Locator:', annotation='This locator is for right direction of the curves.\nPlace the locator at the desired starting point for the curves such as the center of the skull.')
    cmds.textField('rootLocTxtFld')
    cmds.button(label='<<', command='cmds.textField("rootLocTxtFld", e=True, text=cmds.ls(sl=True)[0])', annotation='Select a locator to set as root locator.')

    cmds.setParent('..')
    cmds.button(label='Create Curve', command=main)

    cmds.showWindow()


def main(*args):
    # Get user input
    curvature = cmds.floatField('curvatureFltFld', q=True, value=True)
    rootLocator = cmds.textField('rootLocTxtFld', q=True, text=True)

    centerCruves = create_from_selection(curvature, rootLocator)
    if centerCruves:
        cmds.select(centerCruves, r=True)


def create_from_selection(curvature=DEFAULT_CURVATURE, rootLocator=None):
    centerCurves = []

    # Get selected vertices and meshes
    sels = cmds.ls(sl=True, fl=True)
    selected_vertices = cmds.filterExpand(sels, sm=[28, 31])
    selected_meshes = cmds.filterExpand(sels, sm=12)

    if not selected_vertices and not selected_meshes:
        cmds.error("Please select vertices or a meshe(s).")
        return

    if selected_vertices:
        crv = create(selected_vertices, curvature)
        postCrv = post_process_curve(selected_vertices, crv)
        centerCurves.append(postCrv)

    if selected_meshes:
        for mesh in selected_meshes:
            vertices = cmds.ls(cmds.polyListComponentConversion(mesh, toVertex=True), flatten=True)

            arcLength = 0.0
            minArcLen = 0.001
            tempCurvature = curvature
            start_time = time.time()
            while (arcLength < minArcLen):
                if tempCurvature < 0.1:
                    cmds.warning("Can't create a curve from '{}'.".format(mesh))
                    break

                if time.time() - start_time > TIME_OUT_THRESHOLD:
                    cmds.warning("Timed out while creating a curve from '{}'.".format(mesh))
                    break

                crv = create(vertices, tempCurvature)
                if crv:
                    arcLength = cmds.arclen(crv, ch=False)
                    if arcLength < minArcLen:
                        cmds.delete(crv)

                tempCurvature -= 0.5

            if crv:
                postCrv = post_process_curve(vertices, crv, rootLocator)
                centerCurves.append(postCrv)

    return centerCurves

def create(vertices=[], curvature=DEFAULT_CURVATURE):
    crv = None

    points = np.array([cmds.pointPosition(vertex) for vertex in vertices])

    # Get bounding box width for selected vertices
    bounding_box = cmds.exactWorldBoundingBox(vertices)
    bounding_box_width = max(bounding_box[3] - bounding_box[0], bounding_box[4] - bounding_box[1], bounding_box[5] - bounding_box[2])

    # Thin and sort points
    thickness = bounding_box_width / curvature
    skip = int(len(vertices) / 1000)  # Optimization: Skip points for faster computation
    thinned_points, regression_lines = thin_line(points, point_cloud_thickness=thickness, skipCount=skip)
    sorted_points = sort_points(thinned_points, regression_lines, sorted_point_distance=thickness)

    # Create NURBS curve from sorted points
    crv = create_nurbs_curve_from_points(sorted_points)

    return crv


def post_process_curve(vertices, curve, rootLocator=None):
    # Reverse cruve if curve is upside down from the root locator
    if rootLocator:
        cvs = cmds.ls('{}.cv[*]'.format(curve), fl=True)
        rootCvPoint = om.MPoint(cmds.xform(cvs[0], q=True, ws=True, t=True))
        endCvPoint = om.MPoint(cmds.xform(cvs[-1], q=True, ws=True, t=True))
        locPoint = om.MPoint(cmds.xform(rootLocator, q=True, ws=True, t=True))

        locToRootCvLen = (rootCvPoint - locPoint).length()
        locToEndCvLen = (endCvPoint - locPoint).length()

        if locToRootCvLen > locToEndCvLen:
            cmds.reverseCurve(curve, ch=False, rpo=True)

    # Rebuild curve to make it more smooth
    cmds.rebuildCurve(curve, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=8, d=3)
    cmds.select(curve, r=True)

    # Rename curve to match the mesh name
    mesh = cmds.listRelatives(cmds.ls(vertices, o=True)[0], p=True)[0]
    niceName = '{}_centerCurve'.format(mesh)
    cmds.rename(curve, niceName)

    return niceName
