import pymel.core as pm

import maya.OpenMaya as om1
import maya.api.OpenMaya as om

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
        cv.setPosition(cvPositionDict.get(str(cv)), space='world')

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
    for i in xrange(len(srcShapes)):
        # Get cvs count of each source curve.
        degs = pm.getAttr('%s.degree' % srcShapes[i])
        spans = pm.getAttr('%s.spans' % srcShapes[i])
        cvs = degs + spans
        for j in xrange(cvs):
            # Get worldspace translate value of each cv.
            cvTr = pm.xform('%s.cv[%d]' % (srcShapes[i], j), q=True, t=True, ws=True)
            # Set opposite control's cvs.
            pm.xform('%s.cv[%d]' % (trgShapes[i], j), t=(-cvTr[0], cvTr[1], cvTr[2]), ws=True)


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

    for i in xrange(count):
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
    if not isinstance(curve, basestring):
        curve = str(curve)
    crvDag = globalUtil.getDagPath(curve)
    try:
        crvFn = om.MFnNurbsCurve(crvDag)
    except AttributeError:
        crvDag = globalUtil.getDagPath(curve, 1)
        crvFn = om1.MFnNurbsCurve(crvDag)
    return crvFn.length()
