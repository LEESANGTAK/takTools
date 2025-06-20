"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Created: 06/16/2015
Updated: 06/14/2020

Description:
You can attach object to nurbs curve, nurbs surface, poly mesh.
Select object to attach and select target object and run.
In case poly mesh, you can also attach by selecting two edges.

Usage:
import tak_attachIt
reload(tak_attachIt)
tak_attachIt.UI()
"""

import re

from maya import cmds
import pymel.core as pm
import maya.api.OpenMaya as om


requirePlugins = ['matrixNodes', 'nearestPointOnMesh']
for plugin in requirePlugins:
    if not cmds.pluginInfo(plugin, q=True, loaded=True):
        cmds.loadPlugin(plugin)


class UI(object):
    win = 'attachItWin'
    widgets = {}

    @classmethod
    def __init__(cls):
        if cmds.window(cls.win, exists=True):
            cmds.deleteUI(cls.win)
        cls.ui()

    @classmethod
    def ui(cls):
        cmds.window(cls.win, title='Attach It', mnb=False, mxb=False)

        cls.widgets['menuBar'] = cmds.menuBarLayout(p=cls.win)
        cls.widgets['editMenu'] = cmds.menu(label='Edit', p=cls.widgets['menuBar'])
        cmds.menuItem(label='Cancel Parent Translate', p=cls.widgets['editMenu'], c=Functions.cancelParentTranslate, ann="Set up that cancel translation for it's parent for selected anchor groups to solve double translation.")
        cmds.menuItem(label='Convert to Follicle', p=cls.widgets['editMenu'], c=Functions.convertToFollicle)
        cmds.menuItem(label='Convert to UV Pin', p=cls.widgets['editMenu'], c=Functions.convertToUvPin)
        cmds.menuItem(label='Convert to Two Edge', p=cls.widgets['editMenu'], c=Functions.convertToTwoEdge)

        cls.widgets['mainColLay'] = cmds.columnLayout(adj=True)

        cls.widgets['freezedTransformChkBox'] = cmds.checkBox(label='Freezed Transform', p=cls.widgets['mainColLay'], ann='When transform freezed.')
        cls.widgets['oriChkBox'] = cmds.checkBox(label='Orientation', p=cls.widgets['mainColLay'])

        cls.widgets['chkRowLay'] = cmds.rowLayout(numberOfColumns=2, p=cls.widgets['mainColLay'])
        cls.widgets['mPosOffChkBox'] = cmds.checkBox(label='Maintain Pos Offset', v=True, p=cls.widgets['chkRowLay'])
        cls.widgets['moOriOffChkBox'] = cmds.checkBox(label='Maintain Ori Offset', v=True, p=cls.widgets['chkRowLay'])

        cmds.separator(h=5, p=cls.widgets['mainColLay'])

        cls.widgets['attachMethodRadioBtnGrp'] = cmds.radioButtonGrp(label='Attach to Mesh Method:', numberOfRadioButtons=3, labelArray3=['UV Pin', 'Follicle', 'Two Edge'], select=1, p=cls.widgets['mainColLay'], cw=[(1, 130), (2, 70), (3, 70)])

        cls.widgets['appBtn'] = cmds.button(label='Attach It!', h=50, c=Functions.main, p=cls.widgets['mainColLay'])

        cmds.window(cls.win, e=True, w=100, h=50)
        cmds.showWindow(cls.win)


class Functions(object):
    trgObj = None

    @classmethod
    def main(cls, *args):
        # get state of options
        oriOpt = cmds.checkBox(UI.widgets['oriChkBox'], q=True, v=True)
        mPosOffOpt = cmds.checkBox(UI.widgets['mPosOffChkBox'], q=True, v=True)
        freezedTransformOpt = cmds.checkBox(UI.widgets['freezedTransformChkBox'], q=True, v=True)
        mOriOffOpt = cmds.checkBox(UI.widgets['moOriOffChkBox'], q=True, v=True)
        attachMethod = cmds.radioButtonGrp(UI.widgets['attachMethodRadioBtnGrp'], q=True, select=True)

        selList = cmds.ls(sl=True)
        srcObjs = selList[0:-1]
        cls.trgObj = selList[-1]

        trgShp = cmds.listRelatives(cls.trgObj, s=True, ni=True)[0]
        trgType = cmds.objectType(trgShp)

        if trgType == 'nurbsCurve':
            for srcObj in srcObjs:
                cls.attachToCrv(srcObj, trgShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt)
        elif trgType == 'nurbsSurface':
            for srcObj in srcObjs:
                cls.attachToSurface(srcObj, trgShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt)
        elif trgType == 'mesh':
            if attachMethod == 1:  # UV Pin
                for srcObj in srcObjs:
                    cls.attachToMeshUvPin(srcObj, trgShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt)
            elif attachMethod == 2:  # Follicle
                for srcObj in srcObjs:
                    cls.attachToMeshFollicle(srcObj, trgShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt)
            else:  # Two Edge
                for srcObj in srcObjs:
                    cls.attachToMeshTwoEdge(srcObj, trgShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt)

    @classmethod
    def attachToCrv(cls, srcObj, trgCrvShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt):
        # Get srcObj parent before parent to anchorGrp.
        srcPrnt = cmds.listRelatives(srcObj, p=True)

        nPntCrvNode = cmds.createNode('nearestPointOnCurve', n=srcObj + '_nPntCrv')
        cmds.connectAttr('%s.worldSpace[0]' % (trgCrvShp), '%s.inputCurve' % (nPntCrvNode), force=True)
        decMtx = cmds.createNode('decomposeMatrix')
        if freezedTransformOpt:
            cmds.connectAttr('%s.scalePivot' % (srcObj), '%s.inPosition' % (nPntCrvNode), force=True)
        else:
            cmds.connectAttr('%s.worldMatrix' % (srcObj), '%s.inputMatrix' % decMtx)
            cmds.connectAttr('%s.outputTranslate' % (decMtx), '%s.inPosition' % (nPntCrvNode), force=True)

        pOnCrvInfoNode = cmds.createNode('pointOnCurveInfo', n=srcObj + '_pOnCrvInfo')
        cmds.connectAttr('%s.worldSpace[0]' % (trgCrvShp), '%s.inputCurve' % (pOnCrvInfoNode), force=True)
        cmds.connectAttr('%s.parameter' % (nPntCrvNode), '%s.parameter' % (pOnCrvInfoNode), force=True)
        parmVal = cmds.getAttr('%s.parameter' % (pOnCrvInfoNode))

        anchorGrp = srcObj + '_anchor'
        if not cmds.objExists(anchorGrp):
            cmds.createNode('transform', n=anchorGrp)

        cmds.connectAttr('%s.position' % (pOnCrvInfoNode), '%s.translate' % (anchorGrp), force=True)
        cmds.delete(nPntCrvNode)
        cmds.setAttr('%s.parameter' % (pOnCrvInfoNode), parmVal)

        # Connect anchorGrp rotate depend on oriOpt.
        if oriOpt:
            cls.connectOri(srcObj, pOnCrvInfoNode, anchorGrp, srcPrnt)

        # Parent srcObj to anchorGrp.
        cmds.parent(srcObj, anchorGrp)

        # If srcPrnt exists, reparent anchorGrp to srcObj's old parent.
        if srcPrnt:
            cmds.parent(anchorGrp, srcPrnt[0])

        if not mPosOffOpt:
            if freezedTransformOpt:
                pm.matchTransform(srcObj, anchorGrp)
                pm.makeIdentity(srcObj, apply=True)
            else:
                cls.setZeroAttr(srcObj, 'pos')

        if not mOriOffOpt:
            cls.setZeroAttr(srcObj, 'ori')
            if cmds.objectType(srcObj) == "joint":
                cls.setZeroJntOri(srcObj)


    @classmethod
    def attachToSurface(cls, srcObj, trgSurfShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt):
        # Get srcObj parent before parent to anchorGrp.
        srcPrnt = cmds.listRelatives(srcObj, p=True)
        if srcPrnt:
            srcPrnt = srcPrnt[0]

        # Connect anchorGrp translate.
        clPtOnSurfNode = cmds.createNode('closestPointOnSurface', n=srcObj + '_clPtOnSurf')
        cmds.connectAttr('%s.worldSpace[0]' % (trgSurfShp), '%s.inputSurface' % (clPtOnSurfNode), force=True)

        decMtx = cmds.createNode('decomposeMatrix')
        if freezedTransformOpt:
            cmds.connectAttr('%s.scalePivot' % (srcObj), '%s.inPosition' % (clPtOnSurfNode), force=True)
        else:
            cmds.connectAttr('%s.worldMatrix' % (srcObj), '%s.inputMatrix' % decMtx)
            cmds.connectAttr('%s.outputTranslate' % (decMtx), '%s.inPosition' % (clPtOnSurfNode), force=True)

        pOnSurfInfoNode = cmds.createNode('pointOnSurfaceInfo', n=srcObj + '_pOnSurfInfo')
        cmds.connectAttr('%s.worldSpace[0]' % (trgSurfShp), '%s.inputSurface' % (pOnSurfInfoNode), force=True)
        cmds.connectAttr('%s.parameterU' % (clPtOnSurfNode), '%s.parameterU' % (pOnSurfInfoNode), force=True)
        cmds.connectAttr('%s.parameterV' % (clPtOnSurfNode), '%s.parameterV' % (pOnSurfInfoNode), force=True)
        parmUVal = cmds.getAttr('%s.parameterU' % (pOnSurfInfoNode))
        parmVVal = cmds.getAttr('%s.parameterV' % (pOnSurfInfoNode))

        anchorGrp = srcObj + '_anchor'
        if not cmds.objExists(anchorGrp):
            cmds.createNode('transform', n=anchorGrp)

        if srcPrnt:
            pntMtxMult = cmds.createNode("pointMatrixMult", n="%s_pntMtxMult" % (srcObj))
            cmds.connectAttr('%s.position' % (pOnSurfInfoNode), '%s.inPoint' % (pntMtxMult))
            cmds.connectAttr('%s.worldInverseMatrix' % (srcPrnt), '%s.inMatrix' % (pntMtxMult))
            cmds.connectAttr('%s.output' % (pntMtxMult), '%s.translate' % (anchorGrp), force=True)
        else:
            cmds.connectAttr('%s.position' % (pOnSurfInfoNode), '%s.translate' % (anchorGrp), force=True)

        cmds.delete(clPtOnSurfNode)
        cmds.setAttr('%s.parameterU' % (pOnSurfInfoNode), parmUVal)
        cmds.setAttr('%s.parameterV' % (pOnSurfInfoNode), parmVVal)

        # Connect anchorGrp rotate depend on oriOpt.
        if oriOpt:
            cls.connectOri(srcObj, pOnSurfInfoNode, anchorGrp, srcPrnt)

        # Parent srcObj to anchorGrp.
        cmds.parent(srcObj, anchorGrp)

        # If srcPrnt exists, reparent anchorGrp to srcObj's old parent.
        if srcPrnt:
            cmds.parent(anchorGrp, srcPrnt)

        if not mPosOffOpt:
            if freezedTransformOpt:
                pm.matchTransform(srcObj, anchorGrp)
                pm.makeIdentity(srcObj, apply=True)
            else:
                cls.setZeroAttr(srcObj, 'pos')

        if not mOriOffOpt:
            cls.setZeroAttr(srcObj, 'ori')
            if cmds.objectType(srcObj) == "joint":
                cls.setZeroJntOri(srcObj)


    @classmethod
    def attachToMeshUvPin(cls, srcObj, trgMeshShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt):
        # Get parameter u and v values.
        mSels = om.MSelectionList()
        mSels.add(trgMeshShp)

        meshDagPath = mSels.getDagPath(0)
        fnMesh = om.MFnMesh(meshDagPath)

        srcPoint = om.MPoint(cmds.xform(srcObj, q=True, ws=True, t=True))
        parmUVal, parmVVal, faceId = fnMesh.getUVAtPoint(srcPoint, space=om.MSpace.kWorld)

        # Create uvPin and connect nodes.
        trgMeshOrig = get_intermediate_object(cmds.listRelatives(trgMeshShp, p=True)[0])
        uvPin = cmds.createNode('uvPin', n=srcObj+'_uvPin')
        cmds.setAttr(uvPin+'.normalAxis', 2)
        cmds.setAttr(uvPin+'.tangentAxis', 0)
        cmds.setAttr(uvPin+'.coordinate[0]', parmUVal, parmVVal)

        cmds.connectAttr(trgMeshShp+'.worldMesh[0]', uvPin+'.deformedGeometry', f=True)
        cmds.connectAttr(trgMeshOrig+'.outMesh', uvPin+'.originalGeometry', f=True)

        # Create anchor transform node.
        anchorGrp = srcObj + '_anchor'
        if not cmds.objExists(anchorGrp):
            cmds.createNode('transform', n=anchorGrp)

        # Get local transform if source object parent transform exists.
        srcObjParentTrsf = cmds.listRelatives(srcObj, parent=True)
        if srcObjParentTrsf:
            multMatrix = cmds.createNode('multMatrix', n='%s_localMatrix' % srcObj)
            decMatrix = cmds.createNode('decomposeMatrix', n='%s_decMatrix' % srcObj)

            cmds.connectAttr(uvPin+'.outputMatrix[0]', '%s.matrixIn[0]' % multMatrix, f=True)
            cmds.connectAttr('%s.worldInverseMatrix' % srcObjParentTrsf[0], '%s.matrixIn[1]' % multMatrix, f=True)
            cmds.connectAttr('%s.matrixSum' % multMatrix, '%s.inputMatrix' % decMatrix)
            cmds.connectAttr('%s.outputTranslate' % decMatrix, '%s.translate' % anchorGrp)
            if oriOpt:
                cmds.connectAttr('%s.outputRotate' % decMatrix, '%s.rotate' % anchorGrp)
        else:
            decMatrix = cmds.createNode('decomposeMatrix', n='%s_decMatrix' % srcObj)
            cmds.connectAttr(uvPin+'.outputMatrix[0]', '%s.inputMatrix' % decMatrix, f=True)
            cmds.connectAttr('%s.outputTranslate' % decMatrix, '%s.translate' % anchorGrp)
            if oriOpt:
                cmds.connectAttr('%s.outputRotate' % decMatrix, '%s.rotate' % anchorGrp)

        # Parenting
        if srcObjParentTrsf:
            cmds.parent(anchorGrp, srcObjParentTrsf[0])
        cmds.parent(srcObj, anchorGrp)

        # Maintain offset option
        if not mPosOffOpt:
            if freezedTransformOpt:
                pm.matchTransform(srcObj, anchorGrp)
                pm.makeIdentity(srcObj, apply=True)
            else:
                cls.setZeroAttr(srcObj, 'pos')

        if not mOriOffOpt:
            cls.setZeroAttr(srcObj, 'ori')
            if cmds.objectType(srcObj) == "joint":
                cls.setZeroJntOri(srcObj)


    @classmethod
    def attachToMeshFollicle(cls, srcObj, trgMeshShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt):
        # Get parameter u and v values.
        mSels = om.MSelectionList()
        mSels.add(trgMeshShp)

        meshDagPath = mSels.getDagPath(0)
        fnMesh = om.MFnMesh(meshDagPath)

        srcPoint = om.MPoint(cmds.xform(srcObj, q=True, ws=True, t=True))
        parmUVal, parmVVal, faceId = fnMesh.getUVAtPoint(srcPoint, space=om.MSpace.kWorld)

        # Create follicle and connect nodes.
        fol = cmds.createNode('follicle')
        folTrsf = cmds.listRelatives(fol, parent=True)[0]
        folTrsf = cmds.rename(folTrsf, srcObj + '_fol')
        fol = cmds.listRelatives(folTrsf, s=True)[0]

        cmds.setAttr('{0}.parameterU'.format(fol), parmUVal)
        cmds.setAttr('{0}.parameterV'.format(fol), parmVVal)
        cmds.connectAttr('{0}.outMesh'.format(trgMeshShp), '{0}.inputMesh'.format(fol))
        cmds.connectAttr('{0}.worldMatrix'.format(trgMeshShp), '{0}.inputWorldMatrix'.format(fol))
        cmds.connectAttr('{0}.outTranslate'.format(fol), '{0}.translate'.format(folTrsf))
        cmds.connectAttr('{0}.outRotate'.format(fol), '{0}.rotate'.format(folTrsf))

        # Create anchor transform node.
        anchorGrp = srcObj + '_anchor'
        if not cmds.objExists(anchorGrp):
            cmds.createNode('transform', n=anchorGrp)

        # Get local transform if source object parent transform exists.
        srcObjParentTrsf = cmds.listRelatives(srcObj, parent=True)
        if srcObjParentTrsf:
            multMatrix = cmds.createNode('multMatrix', n='%s_localMatrix' % srcObj)
            decMatrix = cmds.createNode('decomposeMatrix', n='%s_decMatrix' % srcObj)

            cmds.connectAttr('%s.worldMatrix' % folTrsf, '%s.matrixIn[0]' % multMatrix, f=True)
            cmds.connectAttr('%s.worldInverseMatrix' % srcObjParentTrsf[0], '%s.matrixIn[1]' % multMatrix, f=True)
            cmds.connectAttr('%s.matrixSum' % multMatrix, '%s.inputMatrix' % decMatrix)
            cmds.connectAttr('%s.outputTranslate' % decMatrix, '%s.translate' % anchorGrp)
            if oriOpt:
                cmds.connectAttr('%s.outputRotate' % decMatrix, '%s.rotate' % anchorGrp)
        else:
            cmds.connectAttr('{0}.translate'.format(folTrsf), '{0}.translate'.format(anchorGrp))
            if oriOpt:
                cmds.connectAttr('{0}.rotate'.format(folTrsf), '{0}.rotate'.format(anchorGrp))

        # Parenting
        if srcObjParentTrsf:
            cmds.parent(anchorGrp, srcObjParentTrsf[0])
        cmds.parent(srcObj, anchorGrp)

        # Maintain offset option
        if not mPosOffOpt:
            if freezedTransformOpt:
                pm.matchTransform(srcObj, anchorGrp)
                pm.makeIdentity(srcObj, apply=True)
            else:
                cls.setZeroAttr(srcObj, 'pos')

        if not mOriOffOpt:
            cls.setZeroAttr(srcObj, 'ori')
            if cmds.objectType(srcObj) == "joint":
                cls.setZeroJntOri(srcObj)

        return folTrsf

    @classmethod
    def attachToMeshTwoEdge(cls, srcObj, trgMeshShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt):
        # Get closest edges.
        mSels = om.MSelectionList()
        mSels.add(trgMeshShp)

        meshDagPath = mSels.getDagPath(0)
        fnMesh = om.MFnMesh(meshDagPath)

        srcPoint = om.MPoint(cmds.xform(srcObj, q=True, ws=True, t=True))

        # Get the closest point on the mesh and the corresponding face index
        closest_point, face_index = fnMesh.getClosestPoint(srcPoint, om.MSpace.kWorld)

        # Initialize a polygon iterator and set it to the closest face
        poly_iter = om.MItMeshPolygon(meshDagPath)
        poly_iter.setIndex(face_index)

        # Retrieve the edges of the face
        edge_indices = poly_iter.getEdges()

        edgeDic = {}

        trgMeshTrsf = cmds.listRelatives(trgMeshShp, p=True)[0]
        edgeOneNiceName = '{}_e{}'.format(trgMeshTrsf, edge_indices[0])
        edgeDic['edgeOne'] = [edgeOneNiceName, edge_indices[0]]

        edgeTwoNiceName = '{}_e{}'.format(trgMeshTrsf, edge_indices[2])
        edgeDic['edgeTwo'] = [edgeTwoNiceName, edge_indices[2]]

        cmds.select(cl=True)

        for edgeInfo in edgeDic.values():
            crvFromEdgeNode = cmds.createNode('curveFromMeshEdge', n=edgeInfo[0] + '_crvFromEdge')
            cmds.connectAttr('%s.worldMesh[0]' % (trgMeshTrsf), '%s.inputMesh' % (crvFromEdgeNode), force=True)
            cmds.setAttr('%s.edgeIndex[0]' % (crvFromEdgeNode), edgeInfo[1])

        loftNode = cmds.createNode('loft', n='{}_e{}_e{}_loft'.format(trgMeshTrsf, edgeDic['edgeOne'][1], edgeDic['edgeTwo'][1]))
        cmds.setAttr('%s.uniform' % loftNode, 1)
        cmds.setAttr('%s.reverseSurfaceNormals' % loftNode, 1)
        cmds.connectAttr('%s.outputCurve' % (edgeOneNiceName + '_crvFromEdge'), '%s.inputCurve[0]' % (loftNode),
                         force=True)
        cmds.connectAttr('%s.outputCurve' % (edgeTwoNiceName + '_crvFromEdge'), '%s.inputCurve[1]' % (loftNode),
                         force=True)

        # Get closest point's u,v parameter of lofted surface
        surfaceNode = cmds.createNode('nurbsSurface', n='%s_%s_surface' % (edgeOneNiceName, edgeTwoNiceName))
        surfaceNodeTransform = cmds.listRelatives(surfaceNode, p=True)
        cmds.connectAttr('%s.outputSurface' % loftNode, '%s.create' % surfaceNode)
        closestPointOnSurfaceNode = cmds.createNode('closestPointOnSurface', n='%s_%s_csinfo' % (edgeOneNiceName, edgeTwoNiceName))
        cmds.connectAttr('%s.worldSpace' % surfaceNode, '%s.inputSurface' % closestPointOnSurfaceNode)
        decomposeMatrixNode = cmds.createNode('decomposeMatrix', n='%s_%s_deMatrix' % (edgeOneNiceName, edgeTwoNiceName))
        cmds.connectAttr('%s.worldMatrix' % srcObj, '%s.inputMatrix' % decomposeMatrixNode)
        cmds.connectAttr('%s.outputTranslate' % decomposeMatrixNode, '%s.inPosition' % closestPointOnSurfaceNode)
        parmUVal = cmds.getAttr('%s.parameterU' % closestPointOnSurfaceNode)
        parmVVal = cmds.getAttr('%s.parameterV' % closestPointOnSurfaceNode)

        pOnSurfInfoNode = cmds.createNode('pointOnSurfaceInfo', n=srcObj + '_pOnSurfInfo')
        cmds.connectAttr('%s.outputSurface' % loftNode, '%s.inputSurface' % pOnSurfInfoNode, force=True)
        cmds.setAttr('%s.parameterU' % pOnSurfInfoNode, parmUVal)
        cmds.setAttr('%s.parameterV' % pOnSurfInfoNode, parmVVal)

        anchorGrp = srcObj + '_anchor'
        if not cmds.objExists(anchorGrp):
            cmds.createNode('transform', n=anchorGrp)

        cmds.connectAttr('{0}.position'.format(pOnSurfInfoNode), '{0}.translate'.format(anchorGrp))

        # Delete unnecessary nodes
        cmds.delete(surfaceNode, surfaceNodeTransform, closestPointOnSurfaceNode, decomposeMatrixNode)

        # Connect anchorGrp rotate depend on oriOpt.
        if oriOpt:
            cls.connectOri(srcObj, pOnSurfInfoNode, anchorGrp)

        # Get srcObj parent before parent to anchorGrp.
        srcPrnt = cmds.listRelatives(srcObj, p=True)

        # Parent srcObj to anchorGrp.
        cmds.parent(srcObj, anchorGrp)

        # If srcPrnt exists, reparent anchorGrp to srcObj's old parent.
        if srcPrnt:
            cmds.parent(anchorGrp, srcPrnt[0])

        if not mPosOffOpt:
            if freezedTransformOpt:
                pm.matchTransform(srcObj, anchorGrp)
                pm.makeIdentity(srcObj, apply=True)
            else:
                cls.setZeroAttr(srcObj, 'pos')

        if not mOriOffOpt:
            cls.setZeroAttr(srcObj, 'ori')
            if cmds.objectType(srcObj) == "joint":
                cls.setZeroJntOri(srcObj)


    @classmethod
    def setZeroAttr(cls, grp, zroType):
        posAttrList = ['translateX', 'translateY', 'translateZ']
        oriAttrList = ['rotateX', 'rotateY', 'rotateZ']

        if zroType == 'pos':
            for attr in posAttrList:
                cmds.setAttr('%s.%s' % (grp, attr), 0)
        elif zroType == 'ori':
            for attr in oriAttrList:
                cmds.setAttr('%s.%s' % (grp, attr), 0)

    @classmethod
    def setZeroJntOri(cls, srcObj):
        jntOriAttrs = ["jointOrientX", "jointOrientY", "jointOrientZ"]

        for jntOriAttr in jntOriAttrs:
            cmds.setAttr("%s.%s" % (srcObj, jntOriAttr), 0)

    @classmethod
    def connectOri(cls, srcObj, pntInfoNode, anchorGrp, parent=None):
        """
        Connect orientation to anchor group
        Args:
            srcObj: Object name for naming convention
            pntInfoNode: pointOnSurfaceInfo or pointOnCurveInfo node
            anchorGrp: Group that parent of srcObj

        Returns:
            None
        """

        matrix = cmds.shadingNode('fourByFourMatrix', asUtility=True, n=srcObj + '_matrix')

        # Y Vector is normalizedNormal normalizedTangentU
        yVecNode = cmds.shadingNode('vectorProduct', asUtility=True, n=srcObj + '_Yvec')
        cmds.setAttr('%s.operation' % yVecNode, 2)
        cmds.setAttr('%s.normalizeOutput' % yVecNode, True)

        if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':  # In case nurbs surface
            cmds.connectAttr('%s.result.normalizedNormal' % pntInfoNode, '%s.input1' % yVecNode, force=True)
            cmds.connectAttr('%s.result.normalizedTangentU' % pntInfoNode, '%s.input2' % yVecNode, force=True)
        else:  # In case curve
            cmds.connectAttr('%s.result.normalizedTangent' % pntInfoNode, '%s.input1' % yVecNode, force=True)
            # cmds.connectAttr('%s.result.normalizedNormal' % pntInfoNode, '%s.input2' % zVecNode, force=True)
            cmds.setAttr('%s.input2X' % yVecNode, 0)
            cmds.setAttr('%s.input2Y' % yVecNode, 0)
            cmds.setAttr('%s.input2Z' % yVecNode, 1)

        cmds.connectAttr('%s.outputX' % yVecNode, '%s.in10' % matrix, force=True)
        cmds.connectAttr('%s.outputY' % yVecNode, '%s.in11' % matrix, force=True)
        cmds.connectAttr('%s.outputZ' % yVecNode, '%s.in12' % matrix, force=True)

        # X Vector is normalizedTangentU
        if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':
            cmds.connectAttr('%s.result.normalizedTangentUX' % pntInfoNode, '%s.in00' % matrix, force=True)
            cmds.connectAttr('%s.result.normalizedTangentUY' % pntInfoNode, '%s.in01' % matrix, force=True)
            cmds.connectAttr('%s.result.normalizedTangentUZ' % pntInfoNode, '%s.in02' % matrix, force=True)
        else:
            cmds.connectAttr('%s.result.normalizedTangentX' % pntInfoNode, '%s.in00' % matrix, force=True)
            cmds.connectAttr('%s.result.normalizedTangentY' % pntInfoNode, '%s.in01' % matrix, force=True)
            cmds.connectAttr('%s.result.normalizedTangentZ' % pntInfoNode, '%s.in02' % matrix, force=True)

        # Z Vector
        if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':
            # Z Vector is normalizedNormal
            cmds.connectAttr('%s.normalizedNormalX' % pntInfoNode, '%s.in20' % matrix, force=True)
            cmds.connectAttr('%s.normalizedNormalY' % pntInfoNode, '%s.in21' % matrix, force=True)
            cmds.connectAttr('%s.normalizedNormalZ' % pntInfoNode, '%s.in22' % matrix, force=True)
        else:
            # Z Vector is worldZ
            cmds.setAttr('%s.in20' % matrix, 0)
            cmds.setAttr('%s.in21' % matrix, 0)
            cmds.setAttr('%s.in22' % matrix, 1)

        # Position
        cmds.connectAttr('%s.positionX' % pntInfoNode, '%s.in30' % matrix, force=True)
        cmds.connectAttr('%s.positionY' % pntInfoNode, '%s.in31' % matrix, force=True)
        cmds.connectAttr('%s.positionZ' % pntInfoNode, '%s.in32' % matrix, force=True)

        # Decompose matrix
        decMatrix = cmds.shadingNode('decomposeMatrix', asUtility=True, n=srcObj + 'decMatrix')
        if parent:
            multMtx = cmds.createNode("multMatrix", n="%s_multMtx" % (srcObj))
            cmds.connectAttr('%s.output' % matrix, '%s.matrixIn[0]' % multMtx)
            cmds.connectAttr('%s.worldInverseMatrix' % parent, '%s.matrixIn[1]' % multMtx)
            cmds.connectAttr('%s.matrixSum' % multMtx, '%s.inputMatrix' % decMatrix)
        else:
            cmds.connectAttr('%s.output' % matrix, '%s.inputMatrix' % decMatrix)

        # Connect to anchor group
        cmds.connectAttr('%s.outputRotate' % decMatrix, '%s.rotate' % anchorGrp, force=True)

    @staticmethod
    def convertToFollicle(*args):
        objs = cmds.ls(sl=True)
        for obj in objs:
            anchorGrp = findAnchorGroup(obj)
            if not anchorGrp:
                cmds.warning("No anchor group found for {}".format(obj))
                continue

            driverNode = cmds.listConnections(anchorGrp + '.translate')
            if not driverNode:
                cmds.warning("No driver node found for {}".format(anchorGrp))
                continue

            cmds.delete(driverNode[0])

    @staticmethod
    def convertToUvPin(*args):
        anchorGrps = cmds.ls(sl=True)
        for anchorGrp in anchorGrps:
            folConnectInfo = getFollicleConnectionInfo(anchorGrp)
            folTransform = folConnectInfo['follicleTransform']
            folDestinationAttr = folConnectInfo['follicleMatrixDestinationAttr']
            geo = folConnectInfo['geometry']
            geoOrig = folConnectInfo['geometryOrig']
            uvSet = folConnectInfo['uvSet']
            u = folConnectInfo['u']
            v = folConnectInfo['v']

            uvPin = cmds.createNode('uvPin', n=anchorGrp.replace('_anchor', '_uvPin'))
            cmds.setAttr(uvPin+'.normalAxis', 2)
            cmds.setAttr(uvPin+'.tangentAxis', 0)
            cmds.setAttr(uvPin+'.uvSetName', uvSet, type="string")
            cmds.setAttr(uvPin+'.coordinate[0]', u, v)

            cmds.connectAttr(geo+'.worldMesh[0]', uvPin+'.deformedGeometry', f=True)
            cmds.connectAttr(geoOrig+'.outMesh', uvPin+'.originalGeometry', f=True)
            cmds.connectAttr(uvPin+'.outputMatrix[0]', folDestinationAttr, f=True)

            cmds.delete(folTransform)

    @staticmethod
    def convertToTwoEdge(*args):
        pass

    @staticmethod
    def cancelParentTranslate(*args):
        anchorGrps = cmds.ls(sl=True)
        for anchorGrp in anchorGrps:
            parentGrp = cmds.listRelatives(anchorGrp, p=True)[0]
            multMtx = cmds.createNode('multMatrix', n=anchorGrp.replace('_anchor', '_localMatrix'))
            decMtx = cmds.createNode('decomposeMatrix', n=anchorGrp.replace('_anchor', '_decMatrix'))

            folTransform = getFollicleConnectionInfo(anchorGrp)['follicleTransform']
            uvPin = getUvPinConnectionInfo(anchorGrp)['uvPin']
            surfaceMatrix = getSurfaceMatrix(anchorGrp)

            if folTransform:
                cmds.connectAttr(folTransform+'.worldMatrix', multMtx+'.matrixIn[0]', f=True)
            elif uvPin:
                cmds.connectAttr(uvPin+'.outputMatrix[0]', multMtx+'.matrixIn[0]', f=True)
            elif surfaceMatrix:
                cmds.connectAttr(surfaceMatrix+'.output', multMtx+'.matrixIn[0]', f=True)

            cmds.connectAttr(parentGrp+'.worldInverseMatrix', multMtx+'.matrixIn[1]', f=True)
            cmds.connectAttr(multMtx+'.matrixSum', decMtx+'.inputMatrix', f=True)
            cmds.connectAttr(decMtx+'.outputTranslate', anchorGrp+'.t', f=True)

# Uils ------------------------------------------------------------------
def getFollicleConnectionInfo(anchorGrp):
    folShape = cmds.ls(cmds.listHistory(anchorGrp, ac=True), type='follicle')
    if not folShape:
        return None
    folShape = folShape[0]
    fol = cmds.listRelatives(folShape, p=True)[0]
    folDestinationAttr = cmds.listConnections(fol+'.worldMatrix[0]', plugs=True)[0]
    geo = cmds.listConnections(folShape+'.inputMesh', sh=True)[0]
    geoOrig = get_intermediate_object(cmds.listRelatives(geo, p=True)[0])
    uvSet = cmds.getAttr(folShape+'.mapSetName')
    u = cmds.getAttr(folShape+'.parameterU')
    v = cmds.getAttr(folShape+'.parameterV')

    folConnectInfo = {
        'follicleShape': folShape,
        'follicleTransform': fol,
        'follicleMatrixDestinationAttr': folDestinationAttr,
        'geometry': geo,
        'geometryOrig': geoOrig,
        'uvSet': uvSet,
        'u': u,
        'v': v
    }

    return folConnectInfo


def getUvPinConnectionInfo(anchorGrp):
    uvPin = cmds.ls(cmds.listHistory(anchorGrp, ac=True), type='uvPin')
    if not uvPin:
        return None
    uvPin = uvPin[0]
    uvPinDestinationAttr = cmds.listConnections(uvPin+'.outputMatrix[0]', plugs=True)[0]
    geo = cmds.listConnections(uvPin+'.deformedGeometry', sh=True)[0]
    geoOrig = get_intermediate_object(cmds.listRelatives(geo, p=True)[0])
    uvSet = cmds.getAttr(uvPin+'.uvSetName')
    u, v = cmds.getAttr(uvPin+'.coordinate[0]')[0]

    uvPinConnectInfo = {
        'uvPin': uvPin,
        'uvPinMatrixDestinationAttr': uvPinDestinationAttr,
        'geometry': geo,
        'geometryOrig': geoOrig,
        'uvSet': uvSet,
        'u': u,
        'v': v
    }

    return uvPinConnectInfo


def getSurfaceMatrix(anchorGrp):
    decMtx = cmds.listConnections(anchorGrp, d=False, s=True, type='decomposeMatrix')[0]
    fourByFourMtx = cmds.listConnections(decMtx, d=False, s=True, type='fourByFourMatrix')
    if not fourByFourMtx:
        return None

    return fourByFourMtx[0]


def get_intermediate_object(transform):
    # List all shapes under the transform
    shapes = cmds.listRelatives(transform, shapes=True)
    if not shapes:
        return None

    # Find the intermediate object shape
    for shape in shapes:
        if cmds.getAttr(f"{shape}.intermediateObject"):
            return shape

    return None


def findAnchorGroup(obj):
    maxCount = 10
    anhorGrp = None
    count = 1

    while not anhorGrp:
        if count > maxCount:
            break

        parent = cmds.listRelatives(obj, p=True)
        if parent:
            if '_anchor' in parent[0]:
                anhorGrp = parent[0]
                break
            else:
                obj = parent[0]
        else:
            break

        count += 1

    return anhorGrp
