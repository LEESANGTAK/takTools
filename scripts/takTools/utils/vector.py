import pymel.core as pm
import maya.api.OpenMaya as om


def getCenterVector(points):
    sumVector = om.MVector()
    for pnt in points:
        vector = om.MVector(pnt)
        sumVector += vector
    midVector = sumVector / len(points)
    return midVector


def poleVectorLocator():
    selList = pm.selected()
    strtJnt = selList[0]
    midJnt = selList[1]
    endJnt = selList[2]
    loc = pm.spaceLocator(n='poleVector_loc')

    startJntRawPos = pm.xform(strtJnt, q=True, rp=True, ws=True)
    endJntRawPos = pm.xform(endJnt, q=True, rp=True, ws=True)
    midJntRawPos = pm.xform(midJnt, q=True, rp=True, ws=True)

    strtJntVector = om.MVector(*startJntRawPos)
    endJntVector = om.MVector(*endJntRawPos)
    midJntVector = om.MVector(*midJntRawPos)

    # calculate the pole vector position
    centerOfStartToEnd = (strtJntVector + endJntVector) * 0.5
    poleVector = midJntVector - centerOfStartToEnd
    poleVecLocPos = midJntVector + poleVector

    # place locator to the pole vector position
    pm.xform(loc, t=(poleVecLocPos.x, poleVecLocPos.y, poleVecLocPos.z), ws=True)
