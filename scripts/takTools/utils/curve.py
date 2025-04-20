import maya.OpenMaya as om1
import maya.api.OpenMaya as om
from maya import cmds

import pymel.core as pm

from functools import partial

from . import globalUtil
from . import transform as trsfUtil


def combineCurves(curves):
    for curve in curves:
        pm.delete(curve, ch=True)
    for curve in curves:
        pm.makeIdentity(curve, apply=True)

    baseCurve = curves[0]
    extraCurves = curves[1:]

    extraCurveShapes = []
    for curve in extraCurves:
        extraCurveShapes.extend(curve.getShapes())

    for extraCurveShape in extraCurveShapes:
        parentCurveShape(extraCurveShape, baseCurve)

    pm.delete(extraCurves)
    pm.select(cl=True)

    return baseCurve


def parentCurveShape(sourceCrv, targetCrv):
    cvPositionDict = {}
    for cv in sourceCrv.cv:
        cvPositionDict[str(cv)] = cv.getPosition(space='world')

    if isinstance(sourceCrv, pm.nodetypes.Transform):
        sourceCrv.getShape().setParent(targetCrv, shape=True, relative=True)
    else:
        pm.parent(sourceCrv, targetCrv, shape=True, relative=True)

    for cv in sourceCrv.cv:
        cv.setPosition(cvPositionDict.get(cv), space='world')

    targetCrv.updateCurve()


def replaceCurve(origCurve, newCurve):
    origShapes = origCurve.getShapes()
    newShapes = newCurve.getShapes()

    for newShape in newShapes:
        pm.parent(newShape, origCurve, shape=True, relative=True)

    pm.delete(newCurve, origShapes)

    pm.select(cl=True)


def mirrorControlCurveShape(srcControl, trgControl):
    """
    Mirror x-axis from source control curve cvs to the target control curve cvs.

    Args:
        srcControl (str): Source control curve transform name.
        trgControl (str): Target control curve transform name.
    """
    srcShapes = pm.listRelatives(srcControl, s=True)
    trgShapes = pm.listRelatives(trgControl, s=True)
    for i in range(len(srcShapes)):
        # Get cvs count of each source curve.
        degs = pm.getAttr('%s.degree' % srcShapes[i])
        spans = pm.getAttr('%s.spans' % srcShapes[i])
        cvs = degs + spans
        for j in range(cvs):
            # Get worldspace translate value of each cv.
            cvTr = pm.xform('%s.cv[%d]' % (srcShapes[i], j), q=True, t=True, ws=True)
            # Set opposite control's cvs.
            pm.xform('%s.cv[%d]' % (trgShapes[i], j), t=(-cvTr[0], cvTr[1], cvTr[2]), ws=True)

def copyControlCurveShape(srcControl, trgControl):
    """
    Copy from source control curve cvs to the target control curve cvs.

    Args:
        srcControl (str): Source control curve transform name.
        trgControl (str): Target control curve transform name.
    """
    srcShapes = pm.listRelatives(srcControl, s=True)
    trgShapes = pm.listRelatives(trgControl, s=True)
    for i in range(len(srcShapes)):
        # Get cvs count of each source curve.
        degs = pm.getAttr('%s.degree' % srcShapes[i])
        spans = pm.getAttr('%s.spans' % srcShapes[i])
        cvs = degs + spans
        for j in range(cvs):
            cvTr = pm.xform('%s.cv[%d]' % (srcShapes[i], j), q=True, t=True, os=True)
            pm.xform('%s.cv[%d]' % (trgShapes[i], j), t=(cvTr[0], cvTr[1], cvTr[2]), os=True)


def duplicateObjectAlongCurve(crv, obj, count):
    """
    Duplicate given object and placing on along curve.

    Args:
        crv (str): Nurbs curve name.
        obj (str): Object name to duplicate.
        count (int): Duplicated object count.
    """
    crv = pm.PyNode(crv)
    obj = pm.PyNode(obj)

    numOfSpans = count - 1
    increNum = 1.0 / numOfSpans
    unNum = 0

    for i in range(count):
        objPos = pm.pointPosition('%s.un[%f]' %(crv, unNum), w=True)
        dupObj = obj.duplicate(n='{}_{}'.format(obj, i))[0]
        dupObj.translate.set(objPos)
        unNum += increNum


def createShortestPathCurve(startTransform, endTransform, pathTransforms):
    editPoints = []

    while len(pathTransforms) >= 0:
        startTrsfPivotPos = startTransform.scalePivot.get()
        if startTrsfPivotPos.get() != (0.0, 0.0, 0.0):  # In case freezed transform
            editPoints.append(startTrsfPivotPos.get())
        else:
            editPoints.append(pm.xform(startTransform, q=True, t=True, ws=True))

        if len(pathTransforms) == 0:
            break
        closestTrsf = trsfUtil.getClosestTransform(startTransform, pathTransforms)
        startTransform = closestTrsf
        pathTransforms.remove(closestTrsf)

    endTrsfPivotPos = endTransform.scalePivot.get()
    if endTrsfPivotPos.get() != (0.0, 0.0, 0.0):  # In case freezed transform
        editPoints.append(endTrsfPivotPos.get())
    else:
        editPoints.append(pm.xform(endTransform, q=True, t=True, ws=True))

    pm.curve(ep=editPoints)


def getLength(curve):
    if not isinstance(curve, str):
        curve = str(curve)
    crvDag = globalUtil.getDagPath(curve)
    try:
        crvFn = om.MFnNurbsCurve(crvDag)
    except AttributeError:
        crvDag = globalUtil.getDagPath(curve, 1)
        crvFn = om1.MFnNurbsCurve(crvDag)
    return crvFn.length()


def getCurveInfo(curve):
    crvInfo = {}
    crv = pm.PyNode(curve)
    shapes = crv.getShapes()
    for shp in shapes:
        form = shp.f.get()
        degree = shp.d.get()
        cvPos = []
        for cv in shp.cv:
            cvPos.append(list(cv.getPosition(space='world')))
        crvInfo[shp.nodeName()] = {'form': form, 'degree': degree, 'cvPos': cvPos}
    return crvInfo


def createCurve(curveInfo, curveName):
    transform = pm.createNode('transform', n=curveName)
    for shapeInfo in curveInfo.values():
        crv = pm.curve(n=curveName, p=shapeInfo['cvPos'], degree=shapeInfo['degree'])
        if shapeInfo['form'] > 0:
            pm.closeCurve(ch=False, preserveShape=False, replaceOriginal=True)
        pm.parent(crv.getShape(), transform, s=True, r=True)
        pm.delete(crv)


def setupDriveLocators(curve):
    cmds.undoInfo(openChunk=True)
    cvs = cmds.ls('{}.cv[*]'.format(curve), fl=True)
    for i, cv in enumerate(cvs):
        cvWorldPos = cmds.pointPosition(cv, world=True)
        loc = cmds.spaceLocator(n='{}_{}_loc'.format(curve, i))[0]
        cmds.xform(loc, t=cvWorldPos, ws=True)
        cmds.connectAttr('{}.worldPosition[0]'.format(loc), '{}.controlPoints[{}]'.format(curve, i))
    cmds.undoInfo(closeChunk=True)


def setupDriveClusters(curve):
    cmds.undoInfo(openChunk=True)
    cvs = cmds.ls('{}.cv[*]'.format(curve), fl=True)
    for i, cv in enumerate(cvs):
        cmds.cluster(cv, n='{}_{}_clst'.format(curve, i))
    cmds.undoInfo(closeChunk=True)


def extractCurveFromSelectedEdges():
    edges = cmds.filterExpand(cmds.ls(sl=True, fl=True), sm=32)
    if not edges:
        cmds.warning('Please select polygon edges first.')
        return
    shape = cmds.ls(edges, objectsOnly=True)[0]
    transform = cmds.listRelatives(shape, p=True)[0]
    tempMesh = cmds.duplicate(transform, n='temp_mesh')[0]
    tempMeshEdges = [edge.replace(transform, tempMesh) for edge in edges]
    cmds.select(tempMeshEdges, r=True)
    cmds.polyToCurve(form=2, degree=3, n='{}_crv'.format(transform), ch=False)
    cmds.delete(tempMesh)


def curveToMesh(curve, profileType='tube'):
    valuesInfo = [  # [interface, attrType, min, max, default, attrName]
        ['width', 'double', 0.001, 100, 5, 'scaleProfileX'],
        ['taper', 'double', 0, 5, 1, 'taper'],
        ['orientation', 'double', -360, 360, 0, 'rotateProfile'],
        ['twist', 'double', -1, 1, 0, 'twist'],
        ['lengthDivisions', 'long', 1, 50, 8, 'interpolationSteps'],
        ['widthDivisions', 'long', 1, 50, 1, 'profileArcSegments'],
    ]
    if profileType == 'tube':
        valuesInfo.insert(0, ['arcAngle', 'double', 0, 360, 360, 'profileArcAngle'])
    if profileType == 'ribbon':
        valuesInfo.insert(0, ['arcAngle', 'double', 0, 360, 90, 'profileArcAngle'])

    sweepMeshCreator = cmds.createNode('sweepMeshCreator')
    ribbonMesh = cmds.createNode('mesh')
    ribbonMeshTransform = cmds.listRelatives(ribbonMesh, p=True)[0]
    ribbonMeshTransform = cmds.rename(ribbonMeshTransform, '{}_mesh'.format(curve))

    # Set default values
    cmds.setAttr('{}.sweepProfileType'.format(sweepMeshCreator), 3)
    cmds.setAttr('{}.alignProfileEnable'.format(sweepMeshCreator), True)
    cmds.setAttr('{}.interpolationMode'.format(sweepMeshCreator), 1)
    cmds.setAttr('{}.profileArcAngle'.format(sweepMeshCreator), 180)

    # Connect nodes
    cmds.connectAttr('{}.worldSpace[0]'.format(curve), '{}.inCurveArray[0]'.format(sweepMeshCreator))
    cmds.connectAttr('{}.outMeshArray[0]'.format(sweepMeshCreator), '{}.inMesh'.format(ribbonMeshTransform))

    # Assign default material
    cmds.sets(ribbonMeshTransform, e=True, forceElement='initialShadingGroup')

    # Set interfaces
    for valueInfo in valuesInfo:
        if not cmds.objExists('{}.{}'.format(ribbonMeshTransform, valueInfo[0])):
            cmds.addAttr(ribbonMeshTransform, ln=valueInfo[0], at=valueInfo[1], min=valueInfo[2], max=valueInfo[3], dv=valueInfo[4], k=True)
        cmds.connectAttr('{}.{}'.format(ribbonMeshTransform, valueInfo[0]), '{}.{}'.format(sweepMeshCreator, valueInfo[5]))

    if profileType == 'tube':
        cmds.setAttr('{}.widthDivisions'.format(ribbonMeshTransform), 8)

    return ribbonMeshTransform
