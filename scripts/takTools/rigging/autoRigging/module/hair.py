import pymel.core as pm

from ..utils import globalUtil
from ..utils import skeleton as skelUtil
from ..utils import mathUtil


def setPivotToFirstCV(curves):
    curves = [pm.PyNode(crv) for crv in curves]
    for crv in curves:
        firstCvPos = crv.cv[0].getPosition('world')
        crv.setScalePivot(firstCvPos, 'world')
        crv.setRotatePivot(firstCvPos, 'world')


def createSkeleton(curves, minCount=4, maxCount=15):
    curves = [pm.PyNode(crv) for crv in curves]
    crvLengthes = [crv.length() for crv in curves]
    minLen = min(crvLengthes)
    maxLen = max(crvLengthes)

    for crv in curves:
        numJnts = mathUtil.remap(crv.length(), minLen, maxLen, minCount, maxCount)
        skelUtil.jointsFromCurve(curve=crv.name(), count=int(round(numJnts)))


def attachOutJoint(outJointRoot, curve, upObj):
    name = outJointRoot.rsplit('_', 3)[0]

    allOutJnts = outJointRoot.getChildren(ad=True, type='joint')
    allOutJnts.append(outJointRoot)

    ikh = pm.ikHandle(name=name + '_ikh', solver='ikSplineSolver', sj=outJointRoot, ee=allOutJnts[0], curve=curve, createCurve=False, parentCurve=False)[0]
    ikh.dTwistControlEnable.set(True)
    ikh.dWorldUpType.set(3)
    upObj.worldMatrix >> ikh.dWorldUpMatrix


def bindHairMesh(skeletonRoot, mesh):
    allSkelJnts = skeletonRoot.getChildren(ad=True, type='joint')
    allSkelJnts.append(skeletonRoot)

    pm.select(allSkelJnts, mesh, r=True)
    pm.skinCluster(mi=3, dr=4, toSelectedBones=True, bindMethod=0)
