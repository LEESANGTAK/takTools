"""
import rigging.autoRigging as ar
reload(ar)

name = 'spine'
joints = pm.selected()
verObj = ar.module.vertebra.Vertebra(name, joints)
verObj.build()
"""

import pymel.core as pm

from ..base import module
from ..base import controller
from ..utils import globalUtil
from ..utils import joint as jntUtil


class Vertebra(object):
    def __init__(self, name='new', skelJoints=[], stretch=True, parentGroup=None):
        self.name = name
        self.skelJoints = [pm.PyNode(jnt) for jnt in skelJoints]
        self.stretch = stretch
        self.parentGroup = parentGroup

    def build(self):
        moduleObj = module.Module(self.name)
        outJoints = jntUtil.createOutJoints(self.skelJoints)
        ikHandle, eff, curve = pm.ikHandle(
            name=self.name + '_ikh',
            solver='ikSplineSolver',
            sj=outJoints[0],
            ee=outJoints[-1],
            createCurve=True,
            parentCurve=False,
            simplifyCurve=True,
            numSpans=1
        )
        curve.rename('{0}_crv'.format(self.name))
        clusters = self.createClusters(curve)
        ctrls = self.createControls(clusters, outJoints)
        scaleCurve = self.setStretch(curve, outJoints)
        self.setHierarchy(ctrls)
        self.setTwist(ikHandle, ctrls)

        pm.parent(outJoints[0], moduleObj.outGrp)
        pm.parent(ikHandle, curve, clusters, moduleObj.noTransformGrp)
        pm.parent(scaleCurve, moduleObj.systemGrp)
        pm.parent(ctrls[0].spaceGrp, ctrls[1].spaceGrp, moduleObj.ctrlGrp)
        if self.parentGroup:
            pm.parent(moduleObj.topGrp, self.parentGroup)

        moduleObj.outGrp.hide()
        moduleObj.systemGrp.hide()

    def createClusters(self, curve):
        clusters = []

        for i in xrange(curve.numCVs()):
            clusters.append(pm.cluster(curve.cv[i], n='{0}_{1}_clst'.format(self.name, i))[1])

        return clusters

    def createControls(self, clusters, joints):
        ctrls = []

        segments = len(clusters) - 1
        increment = int(len(joints) / segments)
        i = 0
        for clst in clusters:
            ctrl = controller.Controller(joints[i].replace('_outJnt', '_ctrl'), shape='cube', scale=5.0, color='yellow')
            ctrl.createGroups(space=True, extra=True)
            ctrl.matchTo(clst, position=True)
            ctrl.matchTo(joints[i], orientation=True)
            ctrl.connectTo(clst, parent=True)
            ctrl.lockHide(['scale', 'visibility'], ['X', 'Y', 'Z'])
            ctrls.append(ctrl)

            i += increment

        ctrls[0].connectTo(joints[0], rotate=True)
        ctrls[-1].connectTo(joints[-1], rotate=True)

        return ctrls

    def setHierarchy(self, controls):
        for i in xrange(len(controls)):
            if i <= 1:
                continue
            preCtrl = controls[i-1]
            curCtrl = controls[i]

            pm.matchTransform(curCtrl.spaceGrp, preCtrl.transform, pivots=True)
            pm.orientConstraint(preCtrl.transform, curCtrl.spaceGrp, mo=True)

            pm.parent(curCtrl.spaceGrp, preCtrl.spaceGrp)

    def setTwist(self, ikHandle, controls):
        ikHandle.dTwistControlEnable.set(True)
        ikHandle.dWorldUpType.set(4)
        controls[0].transform.worldMatrix >> ikHandle.dWorldUpMatrix
        controls[-1].transform.worldMatrix >> ikHandle.dWorldUpMatrixEnd

    def setStretch(self, curve, outJoints):
        scaleCrv = pm.duplicate(curve, n=curve.name() + '_scale')[0]
        crvInfo = pm.createNode('curveInfo', n=curve.name() + '_curveInfo')
        scaleCrvInfo = pm.createNode('curveInfo', n=scaleCrv.name() + '_curveInfo')
        stretchRatioDiv = pm.createNode('multiplyDivide', n=curve.name() + '_stretchRatio_div')
        stretchRatioDiv.operation.set(2)

        curve.worldSpace >> crvInfo.inputCurve
        scaleCrv.worldSpace >> scaleCrvInfo.inputCurve

        crvInfo.arcLength >> stretchRatioDiv.input1X
        scaleCrvInfo.arcLength >> stretchRatioDiv.input2X

        for outJnt in outJoints:
            if outJoints.index(outJnt) == len(outJoints)-1:
                break
            stretchRatioDiv.outputX >> outJnt.scaleX

        return scaleCrv
