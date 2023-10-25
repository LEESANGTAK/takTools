"""
Author: LEE SANGTAK
Contact: chst27@gmail.com
"""

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

VENDOR = 'Tak'
VERSION = '1.0'


class RampBlendShape(OpenMayaMPx.MPxNode):
    name = 'rampBlendShape'
    id = OpenMaya.MTypeId(0x00002734)

    outGeoAttr = OpenMaya.MObject()
    baseGeoAttr = OpenMaya.MObject()
    targetGeoAttr = OpenMaya.MObject()
    envelopeAttr = OpenMaya.MObject()
    centerAttr = OpenMaya.MObject()
    rangeAttr = OpenMaya.MObject()
    weightRampAttr = OpenMaya.MObject()
    inverseAttr = OpenMaya.MObject()

    def __init__(self):
        super(RampBlendShape, self).__init__()

    def compute(self, plug, dataBlock):
        if not plug == RampBlendShape.outGeoAttr:
            raise RuntimeError('Requested plug is wrong')

        baseGeoHandle = dataBlock.inputValue(RampBlendShape.baseGeoAttr)
        targetGeo = dataBlock.inputValue(RampBlendShape.targetGeoAttr).asMesh()
        envelope = dataBlock.inputValue(RampBlendShape.envelopeAttr).asFloat()
        center = dataBlock.inputValue(RampBlendShape.centerAttr).asFloat()
        range = dataBlock.inputValue(RampBlendShape.rangeAttr).asFloat()

        # Get target geometry points
        targetGeoFn = OpenMaya.MFnMesh(targetGeo)
        targetGeoPoints = OpenMaya.MPointArray()
        targetGeoFn.getPoints(targetGeoPoints)

        # Copy base geometry to create output mesh
        meshDataFn = OpenMaya.MFnMeshData()
        outMesh = meshDataFn.create()
        outMeshFn = OpenMaya.MFnMesh()
        outMeshFn.copy(baseGeoHandle.asMeshTransformed(), outMesh)

        thisNode = self.thisMObject()
        weightRamp = OpenMaya.MRampAttribute(thisNode, RampBlendShape.weightRampAttr)

        minRange = center - range
        maxRange = center + range

        baseGeoIter = OpenMaya.MItGeometry(baseGeoHandle)
        while not baseGeoIter.isDone():
            targetGeoPoint = targetGeoPoints[baseGeoIter.index()]
            deltaVector = targetGeoPoint - baseGeoIter.position()

            if minRange <= baseGeoIter.position().x <= maxRange:
                normalizedXPosition = RampBlendShape.remapValue(minRange, maxRange, 0, 1, baseGeoIter.position().x)
                valAtPos = RampBlendShape.getValAtPos(weightRamp, normalizedXPosition)
                deltaVector = deltaVector * valAtPos
            else:
                deltaVector = deltaVector * 0

            outPoint = baseGeoIter.position() + (deltaVector * envelope)
            outMeshFn.setPoint(baseGeoIter.index(), outPoint)
            baseGeoIter.next()

        outGeoHandle = dataBlock.outputValue(RampBlendShape.outGeoAttr)
        outGeoHandle.setMObject(outMesh)
        outGeoHandle.setClean()
        dataBlock.setClean(plug)

    @staticmethod
    def getValAtPos(rampAttr, position):
        valAtUtil = OpenMaya.MScriptUtil()
        valAtUtil.createFromDouble(1.0)
        valAtPtr = valAtUtil.asFloatPtr()
        rampAttr.getValueAtPosition(position, valAtPtr)
        return valAtUtil.getFloat(valAtPtr)

    @staticmethod
    def remapValue(inMin, inMax, outMin, outMax, inValue):
        outValue = outMin + ((inValue-inMin)*(outMax-outMin) / (inMax-inMin))
        return outValue

    @staticmethod
    def creator():
        return OpenMayaMPx.asMPxPtr(RampBlendShape())

    @staticmethod
    def initialize():
        typeAttrFn = OpenMaya.MFnTypedAttribute()
        numericAttrFn = OpenMaya.MFnNumericAttribute()
        rampAttrFn = OpenMaya.MRampAttribute()

        RampBlendShape.outGeoAttr = typeAttrFn.create('outGeo', 'outGeo', OpenMaya.MFnData.kMesh)
        typeAttrFn.setWritable(False)
        typeAttrFn.setStorable(False)
        RampBlendShape.addAttribute(RampBlendShape.outGeoAttr)

        RampBlendShape.baseGeoAttr = typeAttrFn.create('baseGeo', 'baseGeo', OpenMaya.MFnData.kMesh)
        RampBlendShape.addAttribute(RampBlendShape.baseGeoAttr)
        RampBlendShape.attributeAffects(RampBlendShape.baseGeoAttr, RampBlendShape.outGeoAttr)

        RampBlendShape.targetGeoAttr = typeAttrFn.create('targetGeo', 'targetGeo', OpenMaya.MFnData.kMesh)
        RampBlendShape.addAttribute(RampBlendShape.targetGeoAttr)
        RampBlendShape.attributeAffects(RampBlendShape.targetGeoAttr, RampBlendShape.outGeoAttr)

        RampBlendShape.envelopeAttr = numericAttrFn.create('envelope', 'envelope', OpenMaya.MFnNumericData.kFloat, 1.0)
        numericAttrFn.setKeyable(True)
        numericAttrFn.setMin(0.0)
        numericAttrFn.setMax(1.0)
        RampBlendShape.addAttribute(RampBlendShape.envelopeAttr)
        RampBlendShape.attributeAffects(RampBlendShape.envelopeAttr, RampBlendShape.outGeoAttr)

        RampBlendShape.centerAttr = numericAttrFn.create('center', 'center', OpenMaya.MFnNumericData.kFloat, 0.0)
        numericAttrFn.setKeyable(True)
        RampBlendShape.addAttribute(RampBlendShape.centerAttr)
        RampBlendShape.attributeAffects(RampBlendShape.centerAttr, RampBlendShape.outGeoAttr)

        RampBlendShape.rangeAttr = numericAttrFn.create('range', 'range', OpenMaya.MFnNumericData.kFloat, 5.0)
        numericAttrFn.setKeyable(True)
        numericAttrFn.setMin(0.01)
        RampBlendShape.addAttribute(RampBlendShape.rangeAttr)
        RampBlendShape.attributeAffects(RampBlendShape.rangeAttr, RampBlendShape.outGeoAttr)

        RampBlendShape.weightRampAttr = rampAttrFn.createCurveRamp('weightCurveRamp', 'weightCurveRamp')
        RampBlendShape.addAttribute(RampBlendShape.weightRampAttr)
        RampBlendShape.attributeAffects(RampBlendShape.weightRampAttr, RampBlendShape.outGeoAttr)

        RampBlendShape.inverseAttr = numericAttrFn.create('inverse', 'inverse', OpenMaya.MFnNumericData.kBoolean)
        RampBlendShape.addAttribute(RampBlendShape.inverseAttr)
        RampBlendShape.attributeAffects(RampBlendShape.inverseAttr, RampBlendShape.outGeoAttr)

    def postConstructor(self):
        thisNode = self.thisMObject()
        RampBlendShape.initializeCurveRamp(thisNode, RampBlendShape.weightRampAttr, 0, 0.0, 0.0, 2)
        RampBlendShape.initializeCurveRamp(thisNode, RampBlendShape.weightRampAttr, 1, 0.5, 1.0, 2)
        RampBlendShape.initializeCurveRamp(thisNode, RampBlendShape.weightRampAttr, 2, 1.0, 0.0, 2)

    @staticmethod
    def initializeCurveRamp(node, rampAttr, index, position, value, interpolation):
        rampPlug = OpenMaya.MPlug(node, rampAttr)
        elementPlug = rampPlug.elementByLogicalIndex(index)

        positionPlug = elementPlug.child(0)
        positionPlug.setFloat(position)

        valuePlug = elementPlug.child(1)
        valuePlug.setFloat(value)

        interpPlug = elementPlug.child(2)
        interpPlug.setInt(interpolation)


def initializePlugin(mObj):
    pluginFn = OpenMayaMPx.MFnPlugin(mObj, VENDOR, VERSION)
    try:
        pluginFn.registerNode(RampBlendShape.name, RampBlendShape.id,
                              RampBlendShape.creator, RampBlendShape.initialize,
                              OpenMayaMPx.MPxNode.kDependNode)
    except:
        raise RuntimeError('Failed to register node: %s' % RampBlendShape.name)


def uninitializePlugin(mObj):
    pluginFn = OpenMayaMPx.MFnPlugin(mObj)
    try:
        pluginFn.deregisterNode(RampBlendShape.id)
    except:
        raise RuntimeError('Failed to deregister node: %s' % RampBlendShape.name)
