from maya import cmds
import maya.api.OpenMaya as om


def mirrorX(source, target, connect=False):
    """
    Connect or match source transform to target transform mirrorX behaviour.

    Args:
        source (str): Source transform node name.
        target (str): Target transform node name.
        connect (bool): Keep connection or not.
    """
    source = str(source)
    target = str(target)

    mirrorXMatrix = om.MMatrix(
        [
            -1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ]
    )
    multMatrix = cmds.createNode('multMatrix', name='%s_mirrorX_multMatrix' % source)
    decMatrix = cmds.createNode('decomposeMatrix', name='%s_mirrorX_decMatrix' % source)

    cmds.connectAttr('{}.worldMatrix'.format(source), '{}.matrixIn[0]'.format(multMatrix), force=True)
    cmds.setAttr('{}.matrixIn[1]'.format(multMatrix), list(mirrorXMatrix), type='matrix')
    cmds.connectAttr('{}.matrixSum'.format(multMatrix), '{}.inputMatrix'.format(decMatrix), force=True)
    cmds.connectAttr('{}.outputTranslate'.format(decMatrix), '{}.translate'.format(target), force=True)
    cmds.connectAttr('{}.outputRotate'.format(decMatrix), '{}.rotate'.format(target), force=True)
    cmds.connectAttr('{}.outputScale'.format(decMatrix), '{}.scale'.format(target), force=True)

    if not connect:
        try:
            cmds.disconnectAttr('{}.outputTranslate'.format(decMatrix), '{}.translate'.format(target))
        except RuntimeError:
            pass
        try:
            cmds.disconnectAttr('{}.outputRotate'.format(decMatrix), '{}.rotate'.format(target))
        except RuntimeError:
            pass
        try:
            cmds.disconnectAttr('{}.outputScale'.format(decMatrix), '{}.scale'.format(target))
        except RuntimeError:
            pass

        cmds.delete(decMatrix, multMatrix)


def zeroOutChannels(transform):
    transform = str(transform)

    if cmds.nodeType(transform) == 'joint':
        # If the transform is a joint, transfer the values to the joint orientation.
        jointOrient = cmds.getAttr('{}.jointOrient'.format(transform))[0]
        jointVal = cmds.getAttr('{}.rotate'.format(transform))[0]
        cmds.setAttr('{}.jointOrient'.format(transform), jointVal[0] + jointOrient[0], jointVal[1] + jointOrient[1], jointVal[2] + jointOrient[2])
        cmds.setAttr('{}.rotate'.format(transform), 0, 0, 0)
    else:
        parentTransform = cmds.listRelatives(transform, parent=True, fullPath=True)
        if not parentTransform:
            return

        parentTransform = parentTransform[0]
        attrs = ['scale', 'rotate', 'translate']
        for attr in attrs:
            val = cmds.getAttr('{}.{}'.format(transform, attr))[0]
            parentVal = cmds.getAttr('{}.{}'.format(parentTransform, attr))[0]

            try:
                if attr == 'scale':
                    cmds.setAttr('{}.{}'.format(parentTransform, attr), parentVal[0] + (val[0] - 1), parentVal[1] + (val[1] - 1), parentVal[2] + (val[2] - 1))
                    cmds.setAttr('{}.scale'.format(transform), 1, 1, 1)
                else:
                    cmds.setAttr('{}.{}'.format(parentTransform, attr), parentVal[0] + val[0], parentVal[1] + val[1], parentVal[2] + val[2])
                    cmds.setAttr('{}.{}'.format(transform, attr), 0, 0, 0)
            except RuntimeError:
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
            0.0, 0.0, 0.0, 1.0,
        ]
    )

    trsfMatrix = om.MTransformationMatrix(matrix)
    orientation = [om.MAngle(rad).asDegrees() for rad in trsfMatrix.rotation()]
    return orientation


def addGroup(transform, suffix):
    transform = str(transform)
    transformParent = cmds.listRelatives(transform, parent=True, fullPath=True)

    group = cmds.createNode('transform', name=transform + suffix)
    transformWsMatrix = cmds.xform(transform, q=True, ws=True, m=True)
    cmds.xform(group, ws=True, m=transformWsMatrix)

    if transformParent:
        cmds.parent(group, transformParent[0])

    cmds.parent(transform, group)
    return group


def getClosestTransform(srcTransform, trgTransforms):
    """
    Get a closest target transform to source transform.

    Args:
        srcTransform (str): Source transform node name.
        trgTransforms (list[str]): Transforms to compare with source transform.

    Returns:
        str: A closest target transform to source transform.
    """
    srcTransform = str(srcTransform)
    minDistance = 10000000
    closestTrsf = None

    srcTrsfPivotPos = cmds.getAttr('{}.scalePivot'.format(srcTransform))[0]
    if srcTrsfPivotPos != (0.0, 0.0, 0.0):  # In case freezed transform
        srcTrsfPoint = om.MPoint(srcTrsfPivotPos)
    else:
        srcTrsfPoint = om.MPoint(cmds.xform(srcTransform, q=True, t=True, ws=True))

    for trgTrsf in trgTransforms:
        trgTrsf = str(trgTrsf)
        trgTrsfPivotPos = cmds.getAttr('{}.scalePivot'.format(trgTrsf))[0]
        if trgTrsfPivotPos != (0.0, 0.0, 0.0):  # In case freezed transform
            trgTrsfPoint = om.MPoint(trgTrsfPivotPos)
        else:
            trgTrsfPoint = om.MPoint(cmds.xform(trgTrsf, q=True, t=True, ws=True))

        srcToTrgDist = srcTrsfPoint.distanceTo(trgTrsfPoint)
        if srcToTrgDist < minDistance:
            closestTrsf = trgTrsf
            minDistance = srcToTrgDist

    return closestTrsf
