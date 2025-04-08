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

import maya.cmds as cmds
import pymel.core as pm


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

        cls.widgets['mainColLay'] = cmds.columnLayout(adj=True)

        cls.widgets['freezedTransformChkBox'] = cmds.checkBox(label='Freezed Transform', p=cls.widgets['mainColLay'], ann='When transform freezed.')
        cls.widgets['oriChkBox'] = cmds.checkBox(label='Orientation', p=cls.widgets['mainColLay'])

        cls.widgets['chkRowLay'] = cmds.rowLayout(numberOfColumns=2, p=cls.widgets['mainColLay'])
        cls.widgets['mPosOffChkBox'] = cmds.checkBox(label='Maintain Pos Offset', v=True, p=cls.widgets['chkRowLay'])
        cls.widgets['moOriOffChkBox'] = cmds.checkBox(label='Maintain Ori Offset', v=True, p=cls.widgets['chkRowLay'])

        cmds.separator(h=5, style='none', p=cls.widgets['mainColLay'])

        cls.widgets['appBtn'] = cmds.button(label='Attach It!', h=50, c=Functions.main, p=cls.widgets['mainColLay'])
        cmds.separator(h=5, style='none', p=cls.widgets['mainColLay'])
        cls.widgets['cancleParentTransBtn'] = cmds.button(label='Cancle Parent Translate', h=50, c=Functions.cancelParentTranslateForAnchors, p=cls.widgets['mainColLay'], ann='Set up to cancle parent translation for selected anchor groups.')

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

        selList = cmds.ls(sl=True)
        srcObjs = selList[0:-1]
        cls.trgObj = selList[-1]

        if '.e' in cls.trgObj:
            cls.attachToMeshEdge(oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt)
        else:
            trgShp = cmds.listRelatives(cls.trgObj, s=True, ni=True)[0]
            trgType = cmds.objectType(trgShp)

            if trgType == 'nurbsCurve':
                for srcObj in srcObjs:
                    cls.attachToCrv(srcObj, trgShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt)
            elif trgType == 'nurbsSurface':
                for srcObj in srcObjs:
                    cls.attachToSurface(srcObj, trgShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt)
            elif trgType == 'mesh':
                folLs = []
                for srcObj in srcObjs:
                    result = cls.attachToMeshFol(srcObj, trgShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt)
                    folLs.append(result)
                cmds.group(folLs, n='_fol_grp')

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

        anchorGrp = cmds.createNode('transform', n=srcObj + '_anchor')

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

        anchorGrp = cmds.createNode('transform', n=srcObj + '_anchor')

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
    def attachToMeshFol(cls, srcObj, trgMeshShp, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt):
        """
        Attach object to the target mesh using follicle node.
        Anchor transform node will be create and source object parented to it.

        Args:
            srcObj (str): Source object name to attached.
            trgMeshShp (str): Target mesh shape name.
            oriOpt (bool): Follow orientation option.
            revGrpOpt (bool): Reverse transform node creation option.
            mPosOffOpt (bool): Maintain position when parented to anchor transform node.
            mOriOffOpt (bool): Maintain orientation when parented to anchor transform node.
            freezedTransformOpt (bool): Using pivot value when source object freezed transform.

        Returns:
            folTrsf (str): Follicle transform node name.
        """

        # Get parameter u and v values.
        decMatrix = cmds.createNode('decomposeMatrix')
        nearestPntOnMeshNode = cmds.createNode('nearestPointOnMesh')

        cmds.connectAttr('%s.worldMatrix' % srcObj, '%s.inputMatrix' % decMatrix, force=True)
        if freezedTransformOpt:
            cmds.connectAttr('%s.scalePivot' % (srcObj), '%s.inPosition' % (nearestPntOnMeshNode), force=True)
        else:
            cmds.connectAttr('%s.outputTranslate' % (decMatrix), '%s.inPosition' % (nearestPntOnMeshNode), force=True)
        cmds.connectAttr('%s.outMesh' % trgMeshShp, '%s.inMesh' % nearestPntOnMeshNode, force=True)

        parmUVal = cmds.getAttr('%s.parameterU' % (nearestPntOnMeshNode))
        parmVVal = cmds.getAttr('%s.parameterV' % (nearestPntOnMeshNode))
        cmds.delete(decMatrix, nearestPntOnMeshNode)

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
        anchorGrp = cmds.createNode('transform', n=srcObj + '_anchor')

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

        # Reverse group option

        return folTrsf

    @classmethod
    def attachToMeshEdge(cls, oriOpt, mPosOffOpt, mOriOffOpt, freezedTransformOpt):
        selList = cmds.ls(sl=True, fl=True)
        edgeDic = {}
        srcObj = selList[0]

        matchObj = re.match(r'(.+)\.(\w+)\[(\d+)\]', selList[1])
        edgeOneNiceName = matchObj.group(1) + '_' + matchObj.group(2) + matchObj.group(3)
        edgeDic[1] = [edgeOneNiceName, matchObj.group(3)]

        matchObj = re.match(r'(.+)\.(\w+)\[(\d+)\]', selList[2])
        edgeTwoNiceName = matchObj.group(1) + '_' + matchObj.group(2) + matchObj.group(3)
        edgeDic[2] = [edgeTwoNiceName, matchObj.group(3)]

        trgMesh = matchObj.group(1)
        trgMeshShp = cmds.listRelatives(trgMesh, s=True)[0]

        cmds.select(cl=True)

        for edge in edgeDic.keys():
            crvFromEdgeNode = cmds.createNode('curveFromMeshEdge', n=edgeDic[edge][0] + '_crvFromEdge')
            cmds.connectAttr('%s.worldMesh[0]' % (trgMeshShp), '%s.inputMesh' % (crvFromEdgeNode), force=True)
            cmds.setAttr('%s.edgeIndex[0]' % (crvFromEdgeNode), int(edgeDic[edge][1]))

        loftNode = cmds.createNode('loft', n=edgeOneNiceName + '_' + edgeTwoNiceName + '_loft')
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

        anchorGrp = cmds.createNode('transform', n=srcObj + '_anchor')

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

        # Z Vector is normalizedTangent ^ normalizedNormal
        zVecNode = cmds.shadingNode('vectorProduct', asUtility=True, n=srcObj + '_Zvec')
        cmds.setAttr('%s.operation' % zVecNode, 2)
        cmds.setAttr('%s.normalizeOutput' % zVecNode, True)

        if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':  # In case nurbs surface
            cmds.connectAttr('%s.result.normalizedTangentU' % pntInfoNode, '%s.input1' % zVecNode, force=True)
            cmds.connectAttr('%s.result.normalizedNormal' % pntInfoNode, '%s.input2' % zVecNode, force=True)
        else:  # In case curve
            cmds.connectAttr('%s.result.normalizedTangent' % pntInfoNode, '%s.input1' % zVecNode, force=True)
            # cmds.connectAttr('%s.result.normalizedNormal' % pntInfoNode, '%s.input2' % zVecNode, force=True)
            cmds.setAttr('%s.input2X' % zVecNode, 0)
            cmds.setAttr('%s.input2Y' % zVecNode, 0)
            cmds.setAttr('%s.input2Z' % zVecNode, 1)

        cmds.connectAttr('%s.outputX' % zVecNode, '%s.in20' % matrix, force=True)
        cmds.connectAttr('%s.outputY' % zVecNode, '%s.in21' % matrix, force=True)
        cmds.connectAttr('%s.outputZ' % zVecNode, '%s.in22' % matrix, force=True)

        # X Vector is normalizedTangent
        if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':
            cmds.connectAttr('%s.result.normalizedTangentUX' % pntInfoNode, '%s.in00' % matrix, force=True)
            cmds.connectAttr('%s.result.normalizedTangentUY' % pntInfoNode, '%s.in01' % matrix, force=True)
            cmds.connectAttr('%s.result.normalizedTangentUZ' % pntInfoNode, '%s.in02' % matrix, force=True)
        else:
            cmds.connectAttr('%s.result.normalizedTangentX' % pntInfoNode, '%s.in00' % matrix, force=True)
            cmds.connectAttr('%s.result.normalizedTangentY' % pntInfoNode, '%s.in01' % matrix, force=True)
            cmds.connectAttr('%s.result.normalizedTangentZ' % pntInfoNode, '%s.in02' % matrix, force=True)

        # Y Vector
        if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':
            # Y Vector is normalizedNormal
            cmds.connectAttr('%s.normalizedNormalX' % pntInfoNode, '%s.in10' % matrix, force=True)
            cmds.connectAttr('%s.normalizedNormalY' % pntInfoNode, '%s.in11' % matrix, force=True)
            cmds.connectAttr('%s.normalizedNormalZ' % pntInfoNode, '%s.in12' % matrix, force=True)
        else:
            # Y Vector is worldZ
            cmds.setAttr('%s.in10' % matrix, 0)
            cmds.setAttr('%s.in11' % matrix, 0)
            cmds.setAttr('%s.in12' % matrix, 1)

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
    def cancelParentTranslateForAnchors(*args):
        anchorGrps = cmds.ls(sl=True)
        for anchorGrp in anchorGrps:
            fol = anchorGrp.replace('_anchor', '_fol')
            parentGrp = cmds.listRelatives(anchorGrp, p=True)[0]
            multMtx = cmds.createNode('multMatrix', n=anchorGrp.replace('_anchor', '_localMatrix'))
            decMtx = cmds.createNode('decomposeMatrix', n=anchorGrp.replace('_anchor', '_decMatrix'))

            cmds.connectAttr(fol+'.worldMatrix', multMtx+'.matrixIn[0]', f=True)
            cmds.connectAttr(parentGrp+'.worldInverseMatrix', multMtx+'.matrixIn[1]', f=True)
            cmds.connectAttr(multMtx+'.matrixSum', decMtx+'.inputMatrix', f=True)
            cmds.connectAttr(decMtx+'.outputTranslate', anchorGrp+'.t', f=True)