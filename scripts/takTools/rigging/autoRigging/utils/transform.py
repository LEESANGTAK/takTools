import pymel.core as pm
import maya.api.OpenMaya as om
from . import globalUtil
from collections import OrderedDict
from takTools.utils import kdTree


def transferValueToParent(transform, channels=['translate', 'rotate'], axis=['X', 'Y', 'Z']):
    transform = pm.PyNode(transform)
    parent = transform.getParent()

    for ch in channels:
        for ax in axis:
            attrName = ch + ax
            parentVal = parent.attr(attrName).get()
            transformVal = transform.attr(attrName).get()

            parent.attr(attrName).set(parentVal + transformVal)
            transform.attr(attrName).set(0)

def mirrorX(source, target, connect=False):
    """
    Connect or match source transform to target transform mirrorX behaviour.

    Args:
        source (pm.nodetypes.Transform): Source transform node
        target (pm.nodetypes.Transform): Target transform node
        connect (bool): Keep connection or not
    """
    source = pm.PyNode(source)
    target = pm.PyNode(target)

    mirrorXMatrix = pm.datatypes.Matrix(
        [
            -1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]
    )
    multMatrix = pm.createNode('multMatrix', n='%s_mirrorX_multMatrix' % source.name())
    decMatrix = pm.createNode('decomposeMatrix', n='%s_mirrorX_decMatrix' % source.name())

    source.worldMatrix >> multMatrix.matrixIn[0]
    multMatrix.matrixIn[1].set(mirrorXMatrix)
    multMatrix.matrixSum >> decMatrix.inputMatrix
    decMatrix.outputTranslate >> target.translate
    decMatrix.outputRotate >> target.rotate
    decMatrix.outputScale >> target.scale

    if not connect:
        decMatrix.outputTranslate // target.translate
        decMatrix.outputRotate // target.rotate
        decMatrix.outputScale // target.scale

        pm.delete(decMatrix, multMatrix)


def getOrientation(aimVector, upVector):
    aimVector = om.MVector(aimVector).normalize()
    upVector = om.MVector(upVector).normalize()

    zVec = aimVector ^ upVector
    yVec = zVec ^ aimVector
    matrix = om.MMatrix(
        [
            aimVector.x, aimVector.y, aimVector.z, 0.0,
            yVec.x, yVec.y, yVec.z, 0.0,
            zVec.x, zVec.y, zVec.z, 0.0,
            0.0, 0.0, 0.0, 1.0
        ]
    )

    trsfMatrix = om.MTransformationMatrix(matrix)
    orientation = [om.MAngle(rad).asDegrees() for rad in trsfMatrix.rotation()]
    return orientation


def addGroup(transform, suffix):
    transform = pm.PyNode(transform)
    transformParent = transform.getParent()

    group = pm.createNode('transform', name=transform+suffix)
    transformWsMatrix = transform.worldMatrix.get()
    group.setMatrix(transformWsMatrix)

    group | transform
    if transformParent:
        transformParent | group

    return group


def getClosestTransform(srcTransform, trgTransforms):
    """
    Get a closest target transform to source transform.

    Args:
        srcTransform (pymel.core.nodetypes.Transform): Source transform.
        trgTransforms (list<pymel.core.nodetypes.Transform>): Transforms to compare with source transform.

    Returns:
        pymel.nodetypes.Transform: A closest target transform to source transform.
    """
    minDistance = 10000000
    closestTrsf = None

    srcTrsfPivotPos = srcTransform.scalePivot.get()
    if srcTrsfPivotPos.get() != (0.0, 0.0, 0.0):  # In case freezed transform
        srcTrsfPoint = om.MPoint(srcTrsfPivotPos)
    else:
        srcTrsfPoint = om.MPoint(pm.xform(srcTransform, q=True, t=True, ws=True))

    for trgTrsf in trgTransforms:
        trgTrsfPivotPos = trgTrsf.scalePivot.get()
        if trgTrsfPivotPos.get() != (0.0, 0.0, 0.0):  # In case freezed transform
            trgTrsfPoint = om.MPoint(trgTrsfPivotPos)
        else:
            trgTrsfPoint = om.MPoint(pm.xform(trgTrsf, q=True, t=True, ws=True))

        srcToTrgDist = srcTrsfPoint.distanceTo(trgTrsfPoint)
        if srcToTrgDist < minDistance:
            closestTrsf = trgTrsf
            minDistance = srcToTrgDist

    return closestTrsf


def matchControllersToBindPose(skeletonRoot, controllers):
    """Set controllers transformation to nearest joint's bind pose.

    :param skeletonRoot: Skeleton root joint name
    :type skeletonRoot: str
    :param controllers: Controllers in hierarchy order
    :type controllers: list<str>
    """

    joints = pm.listRelatives(skeletonRoot, type='joint', ad=True)

    kdt = kdTree.KDTree()
    kdt.buildData(joints)
    kdt.buildTree()

    ctrlBindPoseInfo = OrderedDict()
    for ctrl in controllers:
        ctrl = pm.PyNode(ctrl)

        # Get nearest joint from a controller
        searchPoint = pm.xform(ctrl, q=True, t=True, ws=True)
        nearestJntInfo = kdt.searchNearestData(searchPoint)
        nearestJnt = pm.PyNode(nearestJntInfo['name'])

        # Get controller matrix that keep offset matching the joint bind pose
        ctrlBindPose = ctrl.worldMatrix.get() * nearestJnt.worldInverseMatrix.get() * nearestJnt.bindPose.get()
        ctrlBindPoseInfo[ctrl] = ctrlBindPose

    # Set controller transformation in order
    pm.undoInfo(openChunk=True)
    for ctrl, bindPose in ctrlBindPoseInfo.items():
        pm.xform(ctrl, matrix=bindPose, ws=True)
    pm.undoInfo(closeChunk=True)


def setupHybridIK(controls):
    unlockAttrs = ['rotateX', 'rotateY', 'rotateZ']
    for i in range(len(controls)):
        curCtrl = controls[i]
        for unlockAttr in unlockAttrs:
            curCtrl.attr(unlockAttr).setKeyable(True)
            curCtrl.attr(unlockAttr).unlock()

        if i == 0:
            continue
        parentCtrl = controls[i-1]
        parentCtrlSpace = globalUtil.getSpaceGrp(parentCtrl)
        curCtrlSpace = globalUtil.getSpaceGrp(curCtrl)
        pm.parent(curCtrlSpace, parentCtrlSpace)
        pm.matchTransform(curCtrlSpace, parentCtrl, pivots=True)
        pm.orientConstraint(parentCtrl, curCtrlSpace, mo=True)
