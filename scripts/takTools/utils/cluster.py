import maya.api.OpenMaya as om
import pymel.core as pm
import maya.cmds as cmds

from . import globalUtil
from . import transform as trsfUtil
from . import vector as vectorUtil
from . import name as nameUtil


def createClusters(components, orientation='normal'):
    """
    Creates clusters for each component.

    components (list): Vertex or CV components for creating clusters.
    orientation (str): Cluster orientation. Default is 'normal'. Values: 'normal', 'object', 'world'.
    """

    shape = globalUtil.getShapeFromComponent(components[0])
    pnts = [om.MPoint(pm.pointPosition(item, world=True)) for item in components]
    midPoint = om.MPoint(vectorUtil.getCenterVector(pnts))
    basisXVector = (pnts[0] - midPoint) ^ (pnts[1] - pnts[0])

    i = 0
    for cpnt in components:
        clst, clstHandle = pm.cluster(cpnt, n='%s_clst' % nameUtil.convertNiceComponentName(cpnt.name()))
        clstLoc = pm.createNode('locator', name='%s_loc' % clst.name())
        clstLocTrsf = clstLoc.getParent()

        if orientation == 'world':
            pass  # Cluster default orientation is aligned to the world.
            clstLocTrsf.translate.set(clstHandle.scalePivot.get())
            trsfUtil.addGroup(clstLocTrsf, '_zero')
            clstLocTrsf | clstHandle

        elif orientation == 'object':
            pass

        elif orientation == 'normal':
            curPnt = pnts[i]

            # If there is no next point in the point list, use previous toNextPntVector.
            try:
                toNextPntVector = pnts[i+1] - curPnt
            except IndexError:
                pass

            normalVector = curPnt - midPoint

            xVector = normalVector ^ toNextPntVector
            # If x vector direction is opposite to the basis x vector, inverse x vector.
            if (xVector * basisXVector) < 0:
                xVector = -xVector

            zVector = xVector ^ normalVector

            # Normalize to build matrix.
            normalVector = normalVector.normalize()
            zVector = zVector.normalize()
            xVector = xVector.normalize()

            orientedMatrix = om.MMatrix(
                [
                    xVector.x, xVector.y, xVector.z, 0,
                    normalVector.x, normalVector.y, normalVector.z, 0,
                    zVector.x, zVector.y, zVector.z, 0,
                    curPnt[0], curPnt[1], curPnt[2], 1
                ]
            )

            pm.xform(clstLocTrsf, matrix=orientedMatrix, objectSpace=True)
            trsfUtil.addGroup(clstLocTrsf, '_zero')
            clstLocTrsf | clstHandle

        i += 1


def softSelectionToCluster():
    softSelection = om.MGlobal.getRichSelection()
    richSelection = om.MRichSelection(softSelection)
    selectionList = richSelection.getSelection()

    component = selectionList.getComponent(0)
    dag = component[0]
    cpntObj = component[1]
    if dag.apiType() == om.MFn.kLattice:
        singleIndexCpnt = om.MFnTripleIndexedComponent(cpntObj)
        cpntList = singleIndexCpnt.getElements()
    elif dag.apiType() == om.MFn.kNurbsSurface:
        singleIndexCpnt = om.MFnDoubleIndexedComponent(cpntObj)
        cpntList = singleIndexCpnt.getElements()
    else:
        singleIndexCpnt = om.MFnSingleIndexedComponent(cpntObj)
        cpntList = singleIndexCpnt.getElements()

    weightList = dict()
    for i in range(len(cpntList)):
        weightObj = singleIndexCpnt.weight(i)
        influence = weightObj.influence  # influence means weight
        weightList.setdefault(cpntList[i], influence)

    manipPos = globalUtil.getManipPosition()
    newHandle = cmds.createNode('transform', n='softClusterHandle#')
    cmds.xform(newHandle, t=manipPos, ws=True)
    cmds.makeIdentity(newHandle, apply=True)

    rangeVertexs = selectionList.getSelectionStrings()
    myCluster = cmds.cluster(rangeVertexs, n='softCluster#')
    clusterHandleShape = cmds.listRelatives(myCluster[1], s=True)[0]

    for cpnt, influence in weightList.items():
        if dag.apiType() == om.MFn.kLattice:
            cmds.percent(myCluster[0], '%s.pt[%i][%i][%i]' % (dag.partialPathName(), cpnt[0], cpnt[1], cpnt[2]), v=influence)
        elif dag.apiType() == om.MFn.kNurbsSurface:
            cmds.percent(myCluster[0], '%s.cv[%i][%i]' % (dag.partialPathName(), cpnt[0], cpnt[1]), v=influence)
        else:
            cmds.setAttr('%s.weightList[0].w[%i]'% (myCluster[0], cpnt), influence)

    replaceClusterHandle(myCluster[0], clusterHandleShape, newHandle)

def replaceClusterHandle(clusterShape, clusterHandleShape, newHandle):
    oldHandle = cmds.listRelatives(clusterHandleShape, p=True)[0]
    newHandlePos = cmds.xform(newHandle, q=True, rp=True, ws=True)
    cmds.parent(clusterHandleShape, newHandle, s=True, r=True)
    cmds.setAttr('{0}.originX'.format(clusterHandleShape), newHandlePos[0])
    cmds.setAttr('{0}.originY'.format(clusterHandleShape), newHandlePos[1])
    cmds.setAttr('{0}.originZ'.format(clusterHandleShape), newHandlePos[2])
    cmds.delete(oldHandle)
    cmds.connectAttr('{0}.worldMatrix'.format(newHandle), '{0}.matrix'.format(clusterShape), f=True)

