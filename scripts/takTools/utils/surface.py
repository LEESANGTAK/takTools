import maya.cmds as cmds
from . import curve as curveUtil


def _get_surface_shape(surface):
    surface = str(surface)
    if not cmds.objExists(surface):
        raise ValueError('Surface does not exist: {0}'.format(surface))

    nodeType = cmds.nodeType(surface)
    if nodeType == 'transform':
        shapes = cmds.listRelatives(surface, shapes=True, noIntermediate=True, type='nurbsSurface', fullPath=True)
        if not shapes:
            raise ValueError('No nurbsSurface shape found under transform: {0}'.format(surface))
        return shapes[0]
    if nodeType == 'nurbsSurface':
        return surface

    raise ValueError('Expected a nurbsSurface or transform node, got: {0}'.format(surface))


def _get_surface_cv_count(surface):
    surfaceShape = _get_surface_shape(surface)
    numU = cmds.getAttr('{0}.spansU'.format(surfaceShape)) + cmds.getAttr('{0}.degreeU'.format(surfaceShape))
    numV = cmds.getAttr('{0}.spansV'.format(surfaceShape)) + cmds.getAttr('{0}.degreeV'.format(surfaceShape))
    return numU, numV


def _get_surface_cv_position(surface, u, v, worldSpace=False):
    surfaceShape = _get_surface_shape(surface)
    if worldSpace:
        return cmds.surfaceCV(surfaceShape, u, v, query=True, position=True, worldSpace=True)
    return cmds.surfaceCV(surfaceShape, u, v, query=True, position=True, objectSpace=True)


def _set_surface_cv_position(surface, u, v, position, worldSpace=False):
    surfaceShape = _get_surface_shape(surface)
    if worldSpace:
        cmds.surfaceCV(surfaceShape, u, v, position=position, worldSpace=True)
    else:
        cmds.surfaceCV(surfaceShape, u, v, position=position, objectSpace=True)


def matchSurfaceCVs(source, target, space, mirror=False):
    """
    Match surface cv position.

    Args:
        source (str): Source nurbs surface transform or shape.
        target (str): Target nurbs surface transform or shape.
        space (str): coordinate space for the CV. ['transform', 'preTransform', 'object', 'world']
        mirror (bool, optional): Match by mirror option. Defaults to False.
    """

    numU, numV = _get_surface_cv_count(source)
    worldSpace = space == 'world'

    for u in range(numU):
        for v in range(numV):
            cvPoint = _get_surface_cv_position(source, u, v, worldSpace=worldSpace)
            if mirror:
                cvPoint = (-cvPoint[0], cvPoint[1], cvPoint[2])
            _set_surface_cv_position(target, u, v, cvPoint, worldSpace=worldSpace)

    cmds.refresh()


def getSurfaceLength(surface, direction='u'):
    surfaceShape = _get_surface_shape(surface)

    crvFromSrfcIso = cmds.createNode('curveFromSurfaceIso')
    if direction == 'v':
        cmds.setAttr('{0}.isoparmDirection'.format(crvFromSrfcIso), 1)

    tempCurve = cmds.createNode('nurbsCurve')

    cmds.connectAttr('{0}.worldSpace[0]'.format(surfaceShape), '{0}.inputSurface'.format(crvFromSrfcIso), force=True)
    cmds.connectAttr('{0}.outputCurve'.format(crvFromSrfcIso), '{0}.create'.format(tempCurve), force=True)

    length = curveUtil.getLength(tempCurve)

    tempCurveParent = cmds.listRelatives(tempCurve, parent=True, fullPath=True)
    if tempCurveParent:
        cmds.delete(crvFromSrfcIso, tempCurveParent[0], tempCurve)
    else:
        cmds.delete(crvFromSrfcIso, tempCurve)

    return length


def attachObjectToSurface(obj, surface, parmU, parmV):
    obj = str(obj)
    surfaceShape = _get_surface_shape(surface)

    pntOnSrfcInfo = cmds.createNode('pointOnSurfaceInfo', name='{0}_pntOnSrfcInfo'.format(obj))
    matrix = cmds.createNode('fourByFourMatrix', name='{0}_matrix'.format(obj))
    decMatrix = cmds.createNode('decomposeMatrix', name='{0}_decMatrix'.format(obj))

    cmds.connectAttr('{0}.worldSpace[0]'.format(surfaceShape), '{0}.inputSurface'.format(pntOnSrfcInfo), force=True)
    cmds.setAttr('{0}.parameterU'.format(pntOnSrfcInfo), parmU)
    cmds.setAttr('{0}.parameterV'.format(pntOnSrfcInfo), parmV)

    cmds.connectAttr('{0}.normalizedTangentUX'.format(pntOnSrfcInfo), '{0}.in00'.format(matrix), force=True)
    cmds.connectAttr('{0}.normalizedTangentUY'.format(pntOnSrfcInfo), '{0}.in01'.format(matrix), force=True)
    cmds.connectAttr('{0}.normalizedTangentUZ'.format(pntOnSrfcInfo), '{0}.in02'.format(matrix), force=True)

    cmds.connectAttr('{0}.normalizedNormalX'.format(pntOnSrfcInfo), '{0}.in10'.format(matrix), force=True)
    cmds.connectAttr('{0}.normalizedNormalY'.format(pntOnSrfcInfo), '{0}.in11'.format(matrix), force=True)
    cmds.connectAttr('{0}.normalizedNormalZ'.format(pntOnSrfcInfo), '{0}.in12'.format(matrix), force=True)

    cmds.connectAttr('{0}.normalizedTangentVX'.format(pntOnSrfcInfo), '{0}.in20'.format(matrix), force=True)
    cmds.connectAttr('{0}.normalizedTangentVY'.format(pntOnSrfcInfo), '{0}.in21'.format(matrix), force=True)
    cmds.connectAttr('{0}.normalizedTangentVZ'.format(pntOnSrfcInfo), '{0}.in22'.format(matrix), force=True)

    cmds.connectAttr('{0}.positionX'.format(pntOnSrfcInfo), '{0}.in30'.format(matrix), force=True)
    cmds.connectAttr('{0}.positionY'.format(pntOnSrfcInfo), '{0}.in31'.format(matrix), force=True)
    cmds.connectAttr('{0}.positionZ'.format(pntOnSrfcInfo), '{0}.in32'.format(matrix), force=True)

    cmds.connectAttr('{0}.output'.format(matrix), '{0}.inputMatrix'.format(decMatrix), force=True)
    cmds.connectAttr('{0}.outputTranslate'.format(decMatrix), '{0}.translate'.format(obj), force=True)
    cmds.connectAttr('{0}.outputRotate'.format(decMatrix), '{0}.rotate'.format(obj), force=True)
