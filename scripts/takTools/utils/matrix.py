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
