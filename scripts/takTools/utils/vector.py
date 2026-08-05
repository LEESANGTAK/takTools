from maya import cmds
import maya.api.OpenMaya as om


def getCenterVector(points):
    sumVector = om.MVector()
    for pnt in points:
        vector = om.MVector(pnt)
        sumVector += vector
    midVector = sumVector / len(points)
    return midVector


def poleVectorLocator():
    selList = cmds.ls(selection=True)
    strtJnt = selList[0]
    midJnt = selList[1]
    endJnt = selList[2]
    loc = cmds.spaceLocator(name='poleVector_loc')

    startJntRawPos = cmds.xform(strtJnt, q=True, rp=True, ws=True)
    endJntRawPos = cmds.xform(endJnt, q=True, rp=True, ws=True)
    midJntRawPos = cmds.xform(midJnt, q=True, rp=True, ws=True)

    strtJntVector = om.MVector(*startJntRawPos)
    endJntVector = om.MVector(*endJntRawPos)
    midJntVector = om.MVector(*midJntRawPos)

    # calculate the pole vector position
    centerOfStartToEnd = (strtJntVector + endJntVector) * 0.5
    poleVector = midJntVector - centerOfStartToEnd
    poleVecLocPos = midJntVector + poleVector

    # place locator to the pole vector position
    cmds.xform(loc, t=(poleVecLocPos.x, poleVecLocPos.y, poleVecLocPos.z), ws=True)
