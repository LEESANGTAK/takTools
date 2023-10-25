"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Created: 2019.06.07

Test Codes:
import pymel.core as pm

# Test Build
pm.loadPlugin('pointsToCurve')
node = pm.createNode('pointsToCurve')
motionTrail = pm.PyNode('motionTrail1HandleShape')
nurbsCurve = pm.createNode('nurbsCurve')

motionTrail.points >> node.points
node.outCurve >> nurbsCurve.create


# Test Remove
pm.delete(node, nurbsCurve)
pm.flushUndo()
pm.unloadPlugin('pointsToCurve')
"""


import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx


kPluginNodeName = 'pointsToCurve'
kPluginNodeId = OpenMaya.MTypeId(0x00002735)


class PointsToCurve(OpenMayaMPx.MPxNode):
    points = OpenMaya.MObject()
    outCurve = OpenMaya.MObject()

    def __init__(self):
        super(PointsToCurve, self).__init__()

    def compute(self, plug, datablock):
        if plug != PointsToCurve.outCurve:
            return OpenMaya.kUnknownParameter

        pointsObj = datablock.inputValue(PointsToCurve.points).data()
        pointArrayDataFn = OpenMaya.MFnPointArrayData(pointsObj)
        points = pointArrayDataFn.array()

        curveDataFn = OpenMaya.MFnNurbsCurveData()
        outCurveData = curveDataFn.create()

        curveFn = OpenMaya.MFnNurbsCurve()
        curveFn.createWithEditPoints(points, 3, OpenMaya.MFnNurbsCurve.kOpen, False, False, True, outCurveData)

        outputHd = datablock.outputValue(PointsToCurve.outCurve)
        outputHd.setMObject(outCurveData)
        outputHd.setClean()


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(PointsToCurve())


def nodeInitializer():
    fnTypeAttr = OpenMaya.MFnTypedAttribute()

    # Create and set attributes properties
    PointsToCurve.points = fnTypeAttr.create('points', 'pts', OpenMaya.MFnPointArrayData.kPointArray)
    PointsToCurve.outCurve = fnTypeAttr.create('outCurve', 'oc', OpenMaya.MFnData.kNurbsCurve)
    fnTypeAttr.storable = False
    fnTypeAttr.writable = False

    # Add Attributes
    PointsToCurve.addAttribute(PointsToCurve.points)
    PointsToCurve.addAttribute(PointsToCurve.outCurve)

    # Attributes Dependency
    PointsToCurve.attributeAffects(PointsToCurve.points, PointsToCurve.outCurve)


def initializePlugin(obj):
    fnPlugin = OpenMayaMPx.MFnPlugin(obj, 'Tak', '1.0')
    try:
        fnPlugin.registerNode(kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('Failed to register node %s' % kPluginNodeName)


def uninitializePlugin(obj):
    fnPlugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        fnPlugin.deregisterNode(kPluginNodeId)
    except:
        sys.stderr.write('Failed to register node %s' % kPluginNodeName)
