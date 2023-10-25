import pymel.core as pm

import maya.OpenMaya as om1
import maya.api.OpenMaya as om


def getDagPath(nodeName, apiVersion=2):
    if apiVersion == 1:
        mSelLs = om1.MSelectionList()
        mSelLs.add(nodeName)
        dagPath = om1.MDagPath()
        mSelLs.getDagPath(0, dagPath)
    else:
        mSelLs = om.MSelectionList()
        mSelLs.add(nodeName)
        dagPath = mSelLs.getDagPath(0)
    return dagPath


def getShapeFromComponent(component):
    shapeName = component.split('.')[0]
    return pm.PyNode(shapeName)


def findMultiAttributeEmptyIndex(node, attribute):
    """
    Find available index of multi attribute.
    Args:
        node (string): Node name.
        attribute (string): Attribute name

    Returns:
        Available index
    """
    node = pm.PyNode(node)
    id = 0
    while node.attr(attribute)[id].isConnected():
        id += 1
    return id

def reverseOrder(oldList):
    newList = []

    i = -1
    for item in oldList:
        newList.append(oldList[i])
        i -= 1

    return newList

def getSpaceGrp(obj):
    spaceGrp = None

    obj = pm.PyNode(obj)
    count = 1
    countLimit = 10
    found = False
    while not found:
        if count >= countLimit:
            break
        objParent = obj.getParent(generations=count)
        if 'zero' in objParent.name():
            found = True
            spaceGrp = objParent
        count += 1

    return spaceGrp


def isEndItem(item, itemList):
    return itemList.index(item) == len(itemList)-1


def findClosestJoint(searchPoint, joints):
    closestJnt = None

    minDist = 100000.0
    for jnt in joints:
        jntPnt = pm.dt.Point(pm.xform(jnt, q=True, rp=True, ws=True))
        delta = jntPnt - searchPoint
        if delta.length() < minDist:
            closestJnt = jnt
            minDist = delta.length()

    return closestJnt