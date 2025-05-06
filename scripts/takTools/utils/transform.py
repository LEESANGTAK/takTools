import pymel.core as pm
import maya.api.OpenMaya as om
from collections import OrderedDict

from . import kdTree


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


def zeroOutChannels(transform):
    transform = pm.PyNode(transform)

    if transform.nodeType() == 'joint':
        # If the transform is a joint, transfer the values to the joint orientation.
        jointOrient = transform.jointOrient.get()
        jointVal = transform.attr('rotate').get()
        transform.attr('jointOrient').set(jointVal[0] + jointOrient[0], jointVal[1] + jointOrient[1], jointVal[2] + jointOrient[2])
        transform.attr('rotate').set(0, 0, 0)
    else:
        parentTransform = transform.getParent()
        if not parentTransform:
            return

        attrs = ['scale', 'rotate', 'translate']
        for attr in attrs:
            val = transform.attr(attr).get()
            parentVal = parentTransform.attr(attr).get()

            try:
                if attr is 'scale':
                    parentTransform.attr(attr).set(parentVal + (val-1))
                    transform.scale.set(1, 1, 1)
                else:
                    parentTransform.attr(attr).set(parentVal + val)
                    transform.attr(attr).set(0, 0, 0)
            except:
                pass


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
