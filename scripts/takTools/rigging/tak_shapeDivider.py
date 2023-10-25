"""
Author: LEE SANGTAK
Contact: chst27@gmail.com

Usage:
    import takShapeDivider

    shapeDivider = takShapeDivider.ShapeDivider(baseGeo='face', targetGeo='eyebrows_up')
    shapeDivider.build()

    # Fit border using leftBorderPlane

    shapeDivider.divide(numOfShapes=6)
"""

import pymel.core as pm


class ShapeDivider(object):
    def __init__(self, baseGeo=None, targetGeo=None):
        self.baseGeo = None
        self.targetGeo = None
        self.outGeo = None
        self.rampBS = None
        self.centerPlane = None
        self.leftBorderPlane = None
        self.rightBorderPlane = None
        self.refPlaneRootGrp = None
        self.targetGeoBoundingBox = None
        self.numOfShapes = None

        if not pm.pluginInfo('rampBlendShape', q=True, loaded=True):
            pm.loadPlugin('rampBlendShape')

        if not baseGeo or not targetGeo:
            selLs = pm.ls(sl=True)
            if not len(selLs) == 2:
                raise RuntimeError('Select baseGeo and targetGeo')
            self.baseGeo = selLs[0]
            self.targetGeo = selLs[1]
        else:
            baseGeo = pm.PyNode(baseGeo)
            targetGeo = pm.PyNode(targetGeo)

            self.baseGeo = baseGeo
            self.targetGeo = targetGeo

    def build(self, numOfShapes=2, centerFalloff=5):
        """
        Args:
            numOfShapes: Number of shapes
            centerFalloff: Percentage of falloff from center
        """
        self.numOfShapes = numOfShapes
        offset = centerFalloff * 0.01

        self.outGeo = self.baseGeo.duplicate(n='%s_rampBS' % self.targetGeo.name())[0]
        pm.delete(pm.parentConstraint(self.targetGeo, self.outGeo, mo=False))

        self._createRefPlanes()

        self.rampBS = pm.createNode('rampBlendShape')
        if self.numOfShapes == 2:
            pm.removeMultiInstance(self.rampBS.weightCurveRamp[2], b=True)
            self.rampBS.weightCurveRamp[0].weightCurveRamp_Position.set(0.5-offset)
            self.rampBS.weightCurveRamp[1].weightCurveRamp_Position.set(0.5+offset)

        self._connectNodes()

        self.targetGeo.hide()

    def _createRefPlanes(self):
        self.refPlaneRootGrp = pm.group(n='refPlaneRoot_grp', empty=True)

        self.baseGeoBoundingBox = self.baseGeo.getBoundingBox(space='world')
        boundingBoxWidth = self.baseGeoBoundingBox.width()
        boundingBoxHeight = self.baseGeoBoundingBox.height()

        self.centerPlane = pm.polyPlane(n='centerPlane', w=boundingBoxWidth, h=boundingBoxHeight, sw=1, sh=1, axis=[1, 0, 0], ch=False)[0]
        self.leftBorderPlane = self.centerPlane.duplicate(n='leftBorderPlane')[0]
        self.rightBorderPlane = self.centerPlane.duplicate(n='rightBorderPlane')[0]

        self.refPlaneRootGrp | self.centerPlane
        self.centerPlane | self.leftBorderPlane
        self.centerPlane | self.rightBorderPlane

        self.refPlaneRootGrp.setTranslation(self.targetGeo.getBoundingBox(space='world').center())
        self.centerPlane.translate.set(0, 0, 0)
        pm.parentConstraint(self.outGeo, self.refPlaneRootGrp, mo=True)

        leftBorderPlaneInvXMul = pm.createNode('multiplyDivide', n='leftBorderPlaneInvX_mul')
        leftBorderPlaneInvXMul.input2X.set(-1)

        self.leftBorderPlane.translateX >> leftBorderPlaneInvXMul.input1X
        leftBorderPlaneInvXMul.outputX >> self.rightBorderPlane.translateX

        borderMargin = 0.1
        self.leftBorderPlane.translateX.set(boundingBoxWidth/2 + borderMargin)

    def _connectNodes(self):
        self.baseGeo.getShape().worldMesh >> self.rampBS.baseGeo
        self.targetGeo.getShape().worldMesh >> self.rampBS.targetGeo
        self.rampBS.outGeo >> self.outGeo.inMesh

        self.centerPlane.translateX >> self.rampBS.attr('center')
        self.leftBorderPlane.translateX >> self.rampBS.range

    def divide(self):
        dividedGeoOrigin = self.targetGeo.getTranslation(space='world')
        dividedGeoXOffset = self.targetGeoBoundingBox.width()

        if self.numOfShapes == 2:
            for i in xrange(2):
                dividedGeo = self.outGeo.duplicate(n='%s%s' % (self.targetGeo, i+1))[0]
                dividedGeoPos = dividedGeoOrigin + pm.datatypes.Vector((dividedGeoXOffset*(i+1)), 0.0, 0.0)
                dividedGeo.setTranslation(dividedGeoPos, space='world')
                self.rampBS.weightCurveRamp[0].weightCurveRamp_FloatValue.set(1)
                self.rampBS.weightCurveRamp[1].weightCurveRamp_FloatValue.set(0)

        elif self.numOfShapes >= 2 :
            wholeRange = self.rampBS.range.get() * 2
            divisionRange = wholeRange / (self.numOfShapes-1)
            startCenter = -(wholeRange / 2)

            self.leftBorderPlane.translateX.set(divisionRange)

            for i in xrange(self.numOfShapes):
                self.centerPlane.translateX.set(startCenter)

                dividedGeo = self.outGeo.duplicate(n='%s%s' % (self.targetGeo, i+1))[0]
                dividedGeoPos = dividedGeoOrigin + pm.datatypes.Vector((dividedGeoXOffset*(i+1)), 0.0, 0.0)
                dividedGeo.setTranslation(dividedGeoPos, space='world')

                startCenter += divisionRange

        self.targetGeo.show()

        pm.delete(self.outGeo, self.refPlaneRootGrp)
