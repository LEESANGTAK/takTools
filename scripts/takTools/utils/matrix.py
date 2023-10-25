import maya.api.OpenMaya as om
from . import mesh as meshUtil


def worldXMirrorMatrix(matrix):
    worldXMirrorMatrix = [
        -1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]

    return om.MMatrix(matrix) * om.MMatrix(worldXMirrorMatrix)


def matrixToSRT(matrix, space=om.MSpace.kWorld):
    trsfMatrix = om.MTransformationMatrix(matrix)
    scale = trsfMatrix.scale(space)
    rotation = [om.MAngle(rad).asDegrees() for rad in trsfMatrix.rotation()]
    translation = trsfMatrix.translation(space)
    return scale, rotation, translation


def getAlignedMatrix(geo):
    centerPoint = meshUtil.getCenterPoint(geo)
    farthestPoint = meshUtil.getFarthestPoint(geo, centerPoint)
    closestPoint = meshUtil.getClosestPoint(geo, centerPoint)

    xVec = (farthestPoint-centerPoint)*2  # Double scaling to get proper scale vector
    yVec = (closestPoint-centerPoint)*2

    searchRayDir = (xVec ^ yVec).normalize()
    closestIntersectPoint = getClosestIntersectPoint(
        geo,
        om.MFloatPoint(centerPoint),
        om.MFloatVector(searchRayDir),
        10000
    )
    zVec = (closestIntersectPoint-centerPoint)*2

    matrix = om.MMatrix(
        [
            xVec.x, xVec.y, xVec.z, 0.0,
            yVec.x, yVec.y, yVec.z, 0.0,
            zVec.x, zVec.y, zVec.z, 0.0,
            centerPoint.x, centerPoint.y, centerPoint.z, 1.0
        ]
    )

    return matrix


def splitMatrix(matrix):
    trsfMtx = om.MTransformationMatrix(matrix)
    translateMatrix = om.MMatrix(
        [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            matrix[12], matrix[13], matrix[14], 1.0
        ]
    )
    return trsfMtx.asScaleMatrix(), trsfMtx.asRotateMatrix(), translateMatrix
