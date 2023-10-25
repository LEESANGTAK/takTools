import pymel.core as pm
from . import curve as curveUtil


def matchSurfaceCVs(source, target, space, mirror=False):
    """
    Match surface cv position.

    Args:
        source (pymel.nodetypes.NurbsSurface): Source nurbs surface
        target (pymel.nodetypes.NurbsSurface): Target nurbs surface
        space (str): coordinate space for the CV. ['transform', 'preTransform', 'object', 'world']
        mirror (bool, optional): Match by mirror option. Defaults to False.
    """

    # Get uv count of source surface
    numU = source.numCVsInU()
    numV = source.numCVsInV()

    # Match target cvs
    for u in range(numU):
        for v in range(numV):
            cvPoint = source.getCV(u, v, space=space)
            if mirror:
                cvPoint = pm.datatypes.Point(-cvPoint[0], cvPoint[1], cvPoint[2])
            target.setCV(u, v, cvPoint, space=space)

    # Update surface for viewport refresh
    target.updateSurface()


def getSurfaceLength(surface, direction='u'):
    surface = pm.PyNode(surface)

    crvFromSrfcIso = pm.createNode('curveFromSurfaceIso')
    if direction == 'v':
        crvFromSrfcIso.isoparmDirection.set(1)
    tempCurve = pm.createNode('nurbsCurve')

    surface.worldSpace >> crvFromSrfcIso.inputSurface
    crvFromSrfcIso.outputCurve >> tempCurve.create

    length = curveUtil.getLength(tempCurve)

    pm.delete(crvFromSrfcIso, tempCurve.getParent(), tempCurve)

    return length


def attachObjectToSurface(obj, surface, parmU, parmV):
    pntOnSrfcInfo = pm.createNode('pointOnSurfaceInfo', n='%s_pntOnSrfcInfo' % obj)
    matrix = pm.createNode('fourByFourMatrix', n='%s_matrix' % obj)
    decMatrix = pm.createNode('decomposeMatrix', n='%s_decMatrix' % obj)

    surface.worldSpace >> pntOnSrfcInfo.inputSurface
    pntOnSrfcInfo.parameterU.set(parmU)
    pntOnSrfcInfo.parameterV.set(parmV)

    # Transform x vector is surface tangent u
    pntOnSrfcInfo.normalizedTangentUX >> matrix.in00
    pntOnSrfcInfo.normalizedTangentUY >> matrix.in01
    pntOnSrfcInfo.normalizedTangentUZ >> matrix.in02

    # Transform y vector is surface normal
    pntOnSrfcInfo.normalizedNormalX >> matrix.in10
    pntOnSrfcInfo.normalizedNormalY >> matrix.in11
    pntOnSrfcInfo.normalizedNormalZ >> matrix.in12

    # Transfom z vector is surface tangent v
    pntOnSrfcInfo.normalizedTangentVX >> matrix.in20
    pntOnSrfcInfo.normalizedTangentVY >> matrix.in21
    pntOnSrfcInfo.normalizedTangentVZ >> matrix.in22

    pntOnSrfcInfo.positionX >> matrix.in30
    pntOnSrfcInfo.positionY >> matrix.in31
    pntOnSrfcInfo.positionZ >> matrix.in32

    matrix.output >> decMatrix.inputMatrix
    decMatrix.outputTranslate >> obj.translate
    decMatrix.outputRotate >> obj.rotate
