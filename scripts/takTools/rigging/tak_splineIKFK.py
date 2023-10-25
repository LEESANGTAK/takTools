'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 02/19/2016

Description:
Build spline IK/FK for selected curves.

Usage:
import tak_splineIKFK
reload(tak_splineIKFK)
tak_splineIKFK.SplineIKFK()
'''

import re
import maya.cmds as cmds

from ..common import tak_misc


class SplineIKFK(object):

    uiWdgDic = {}
    uiWdgDic['winName'] = 'splineIkFKWin'

    @classmethod
    def __init__(cls):
        if cmds.window(cls.uiWdgDic['winName'], exists = True):
            cmds.deleteUI(cls.uiWdgDic['winName'])

        cls.ui()


    @classmethod
    def ui(cls):
        cmds.window(cls.uiWdgDic['winName'], title = 'Build Spline IK/FK')

        cls.uiWdgDic['mainColLo'] = cmds.columnLayout(p = cls.uiWdgDic['winName'], adj = True)
        # cls.uiWdgDic['nameTxtFldGrp'] = cmds.textFieldGrp(p = cls.uiWdgDic['mainColLo'], label = 'Name: ')
        # cls.uiWdgDic['sideChkBoxGrp'] = cmds.checkBoxGrp(p = cls.uiWdgDic['mainColLo'], label = 'Side: ', numberOfCheckBoxes = 3, labelArray3 = ['lf', 'rt', 'ct'])

        cls.uiWdgDic['preChkBoxGrp'] = cmds.checkBoxGrp(p = cls.uiWdgDic['mainColLo'], label = "Preview Options: ", numberOfCheckBoxes = 2, labelArray2 = ['Rebuild Curve', 'Auto Orient Controls and Joints'], v1 = True, v2 = True)
        cls.uiWdgDic['numCtrlIntSldrGrp'] = cmds.intSliderGrp(p = cls.uiWdgDic['mainColLo'], label = 'Number of Controls: ', field = True, min = 3, max = 50, v = 5, cc = cls.numCtrlCC)
        cls.uiWdgDic['numJntIntSldrGrp'] = cmds.intSliderGrp(p = cls.uiWdgDic['mainColLo'], label = 'Number of Joints: ', field = True, min = 5, max = 200, v = 9, cc = cls.nunJntsCC)

        cmds.separator(p = cls.uiWdgDic['mainColLo'], style = 'in', h = 10)

        cls.uiWdgDic['optChkBoxGrp'] = cmds.checkBoxGrp(p = cls.uiWdgDic['mainColLo'], label = 'Build Options: ', numberOfCheckBoxes = 3, labelArray3 = ['FK', 'Stretch', 'Dynamic'], v2 = True)

        cmds.button(p = cls.uiWdgDic['mainColLo'], label = 'Build', h = 30, c = cls.buildSplineIKFK)
        cmds.button(p = cls.uiWdgDic['mainColLo'], label = "Bind(Select a '_ctrl' and geometry(s).)", h = 30, c = cls.bindGeo)
        cmds.button(p = cls.uiWdgDic['mainColLo'], label = "Select 'all_ctrl' from Selected Controls", h = 30, c = cls.selAllCtrl)

        cmds.window(cls.uiWdgDic['winName'], e = True, w = 150, h = 50)
        cmds.showWindow(cls.uiWdgDic['winName'])


    @classmethod
    def buildSplineIKFK(cls, *args):
        '''
        Main method.
        '''

        numOfCtrl = cmds.intSliderGrp(cls.uiWdgDic['numCtrlIntSldrGrp'], q = True, v = True)
        ctrlNumOfSpan = numOfCtrl - 1
        ctrlIncreNum = 1.0 / ctrlNumOfSpan

        numOfJnt = cmds.intSliderGrp(cls.uiWdgDic['numJntIntSldrGrp'], q = True, v = True)
        jntNumOfSpan = numOfJnt - 1
        jntIncreNum = 1.0 / jntNumOfSpan

        stretchOpt = cmds.checkBoxGrp(cls.uiWdgDic['optChkBoxGrp'], q = True, v2 = True)

        crv = cmds.ls(sl = True)[0]
        # for crv in crvLs:

        # # Create control layout
        # crvBndJntLs = cls.ctrlLayout(crv, numOfCtrl, ctrlNumOfSpan, ctrlIncreNum)

        # # Create joint chain
        # bndJntLs = cls.jntChain(crv, numOfJnt, jntIncreNum)

        # Build spline IK
        ikh = cmds.ikHandle(sol = 'ikSplineSolver', sj = cls.bndJntLs[0], ee = cls.bndJntLs[-1], curve = crv, ccv = False, pcv = False)[0]

        # Create controls
        ctrlLs = cls.createCtrl(crv, cls.crvBndJntLs)

        # Bind curve with curve bind joints
        cmds.select(cls.crvBndJntLs, crv, r = True)
        cmds.skinCluster(dr = 4, toSelectedBones = True, bindMethod = 0)

        # Turn off inherits transform of curve transform node.
        cmds.setAttr('%s.inheritsTransform' %crv, False)

        # Add stretch function
        if stretchOpt:
            cls.stretchy(crv, cls.bndJntLs)

        # Twist set up
        cmds.setAttr('%s.dTwistControlEnable' % ikh, True)
        cmds.setAttr('%s.dWorldUpType' % ikh, 4)
        cmds.connectAttr('%s.worldMatrix[0]' % ctrlLs[1], '%s.dWorldUpMatrix' % ikh)
        cmds.connectAttr('%s.worldMatrix[0]' % ctrlLs[-1], '%s.dWorldUpMatrixEnd' % ikh)

        # Setup scaleNormalize curve
        scaleNormalizeCrv = cls.setUpScaleNormalizeCurve(crv)

        # Add dynamic function

        # Clean up outliner
        cls.cleanUpOutliner(cls.crvBndJntLs, cls.bndJntLs, ctrlLs, crv, scaleNormalizeCrv, ikh)

        # Connect attributes
        cls.connections(crv, cls.bndJntLs)


    @classmethod
    def numCtrlCC(cls, *args):
        '''
        Number of Controls slider change command.
        '''

        selCrvLs = cmds.ls(sl = True)

        numOfCtrl = cmds.intSliderGrp(cls.uiWdgDic['numCtrlIntSldrGrp'], q = True, v = True)
        numOfSpan = numOfCtrl - 1
        increNum = 1.0 / numOfSpan

        for crv in selCrvLs:
            cls.ctrlLayout(crv, numOfCtrl, numOfSpan, increNum)

        cmds.select(selCrvLs, r = True)


    @classmethod
    def ctrlLayout(cls, crv, numOfCtrl, numOfSpan, increNum, *args):
        # Initialize un value.
        unNum = 0

        reCrvOpt = cmds.checkBoxGrp(cls.uiWdgDic['preChkBoxGrp'], q = True, v1 = True)
        if reCrvOpt:
            # Rebuild curve's control points uniformly for even joint distribution.
            cmds.rebuildCurve(crv, ch = 1, rpo = 1, rt = 0, end = 1, kr = 0, kcp = 0, kep = 1, kt = 0, s = numOfSpan, d = 3, tol = 0)

        # Delete curve bind joint chain if exists it.
        if cmds.objExists('%s_*_crv_jnt' %crv):
            cmds.delete('%s_*_crv_jnt' %crv)

        # Build joint chain hierarchy for orient joints.
        cmds.select(cl = True)
        cls.crvBndJntLs = []
        for i in xrange(numOfCtrl):
            crvBndJntPos = cmds.pointPosition('%s.un[%f]' %(crv, unNum), w = True)
            crvBndJnt = cmds.joint(p = crvBndJntPos, n = '%s_%d_crv_jnt' %(crv, i), radius = 10)
            cls.crvBndJntLs.append(crvBndJnt)
            unNum += increNum
        cmds.CompleteCurrentTool()

        # Orient curve bind joints
        oriJntOpt = cmds.checkBoxGrp(cls.uiWdgDic['preChkBoxGrp'], q = True, v2 = True)
        if oriJntOpt:
            cls.orientJntChain(cls.crvBndJntLs)

        # Unparent curve bind joints.
        for crvBndJnt in cls.crvBndJntLs:
            if cmds.listRelatives(crvBndJnt, p = True):
                cmds.parent(crvBndJnt, w = True)
            else:
                pass

        return cls.crvBndJntLs


    @classmethod
    def nunJntsCC(cls, *args):
        '''
        Number of Joints slider change command.
        '''

        selCrvLs = cmds.ls(sl = True)

        numOfJnt = cmds.intSliderGrp(cls.uiWdgDic['numJntIntSldrGrp'], q = True, v = True)
        numOfSpan = numOfJnt - 1
        increNum = 1.0 / numOfSpan

        for crv in selCrvLs:
            cls.jntChain(crv, numOfJnt, increNum)

        cmds.select(selCrvLs, r = True)


    @classmethod
    def jntChain(cls, crv, numOfJnt, increNum, *args):
        # Initialize un value.
        unNum = 0

        # Delete joint chain if exists it.
        if cmds.objExists('%s_0_jnt' %crv):
            cmds.delete('%s_0_jnt' %crv)

        # Build joint chain
        cls.bndJntLs = []
        cmds.select(cl = True)
        for i in xrange(numOfJnt):
            jntPos = cmds.pointPosition('%s.un[%f]' %(crv, unNum), w = True)
            bndJnt = cmds.joint(p = jntPos, n = '%s_%d_jnt' %(crv, i))
            cls.bndJntLs.append(bndJnt)
            unNum += increNum
        cmds.CompleteCurrentTool()

        # Orient joints
        oriJntOpt = cmds.checkBoxGrp(cls.uiWdgDic['preChkBoxGrp'], q = True, v2 = True)
        if oriJntOpt:
            cls.orientJntChain(cls.bndJntLs)

        # cmds.select(cls.bndJntLs, r = True)
        # cmds.ToggleLocalRotationAxes()
        # cmds.select(crv, r = True)

        return cls.bndJntLs


    @classmethod
    def createCtrl(cls, crv, jntLs):
        fkOpt = cmds.checkBoxGrp(cls.uiWdgDic['optChkBoxGrp'], q = True, v1 = True)

        ctrlLs = []

        # Create all control
        allCtrl = cmds.curve(n = crv + '_all_ctrl', d = 3, p = [[0, 0, -2.995565], [0.789683, 0, -2.990087], [2.37399, 0, -2.329641], [3.317845, 0, 0.0217106], [2.335431, 0, 2.360484], [-0.0144869, 0, 3.320129], [-2.355941, 0, 2.340014], [-3.317908, 0, -0.00724357], [-2.353569, 0, -2.350269], [-0.76356, 0, -2.996864], [0, 0, -2.995565]], k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0))
        ctrlLs.append(allCtrl)
        ctrlGrpLs = cls.ctrlGrp(allCtrl)
        cmds.delete(cmds.parentConstraint(jntLs[0], ctrlGrpLs[0], mo = False))
        cmds.addAttr(allCtrl, ln = 'bindJointsVis', nn = 'Bind Joints Vis', keyable = True, at = 'bool')
        cmds.setAttr('%s.visibility' %allCtrl, lock = True, keyable = False, channelBox = False)

        # Create each joint control
        for jnt in jntLs:
            # Create cube shape control
            ctrl = cmds.curve(n = jnt.rsplit('_crv_jnt')[0] + '_ctrl', d = 1, p = [(-1, 1, 1),(1, 1, 1),(1, 1, -1),(-1, 1, -1),(-1, 1, 1),(-1, -1, 1),(-1, -1, -1),(1, -1, -1),(1, -1, 1),(-1, -1, 1),(1, -1, 1),(1, 1, 1),(1, 1, -1),(1, -1, -1),(-1, -1, -1),(-1, 1, -1)], k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
            ctrlLs.append(ctrl)

            # Lock and hide unused attributes of control.
            unUsedAttr = ['scaleX', 'scaleY', 'scaleZ', 'visibility']
            for attr in unUsedAttr:
                cmds.setAttr("%s.%s" %(ctrl, attr), lock = True, keyable = False, channelBox = False)

            # Control group hierarchy
            ctrlGrpLs = cls.ctrlGrp(ctrl)
            cmds.parent(ctrl, ctrlGrpLs[2])

            # Match control to the joint
            cmds.delete(cmds.parentConstraint(jnt, ctrlGrpLs[0], mo = False))

            # Constraint part
            cmds.parentConstraint(ctrl, jnt, mo = False)
            cmds.scaleConstraint(ctrl, jnt, mo = False)
            if fkOpt:
                cmds.orientConstraint(ctrl, ctrlGrpLs[3], mo = False)

            # Parent to the parent child rotation pivot group
            matchObj = re.match(r'(.+)_(\d+)_.+', jnt)
            crvName = matchObj.group(1)
            jntNum = int(matchObj.group(2))

            if jntNum == 0:
                cmds.parent(ctrlGrpLs[3],  '%s_all_ctrl' %crvName)
            else:
                parentJntNum = jntNum - 1
                cmds.parent(ctrlGrpLs[0], ctrlGrpLs[3],  '%s_%d_ctrl_chldRoPivot' %(crvName, parentJntNum))

        cmds.parent(ctrlLs[1] + '_zero', allCtrl)

        return ctrlLs


    @classmethod
    def ctrlGrp(cls, ctrl):
        '''
        Make control gorup hierarchy.
        '''

        zeroGrp = tak_misc.doGroup(ctrl, '_zero')
        autoGrp = tak_misc.doGroup(ctrl, '_auto')
        extraGrp = tak_misc.doGroup(ctrl, '_extra')
        if not '_all_ctrl' in ctrl:
            chldRoPivotGrp = tak_misc.doGroup(ctrl, '_chldRoPivot')
            return zeroGrp, autoGrp, extraGrp, chldRoPivotGrp

        return zeroGrp, autoGrp, extraGrp


    @classmethod
    def orientJntChain(cls, jntChainLs):
        '''
        Correct joint chain orientation using aim constraint.
        '''

        # Create plane with 3 joints position(start, mid, end).
        plane = cls.jntChainPlane(jntChainLs)

        # Get poly plane's face normal vector.
        faceNormalVec = cls.getFaceNormalVec(plane + '.f[0]')

        for i in xrange(len(jntChainLs)):
            curJnt = jntChainLs[i]

            # If a joint is end joint, orient to parent joint.
            if i == len(jntChainLs)-1:
                cmds.joint(curJnt, e = True, oj = 'none', ch = True, zso = True)
            else:
                # Unparent child joint
                chldJnt = jntChainLs[i+1]
                cmds.parent(chldJnt, world = True)

                # Aim constraint
                cmds.delete(cmds.aimConstraint(chldJnt, curJnt, mo = False, aimVector = [1.0, 0.0, 0.0], upVector = [0.0, 0.0, 1.0], worldUpType = "vector", worldUpVector = faceNormalVec))

                # Freeze transform
                cmds.makeIdentity(curJnt, apply = True)

                # Reparent child joint
                cmds.parent(chldJnt, curJnt)

        # cmds.delete(upVecLoc)
        cmds.delete(plane)


    @classmethod
    def jntChainPlane(cls, jntLs):
        '''
        Create a plane conform to joint chain.
        '''

        # Get start, mid, end joint.
        startJnt = jntLs[0]
        midJnt = jntLs[int(len(jntLs) / 2)]
        endJnt = jntLs[-1]

        # Get world position of joints.
        startJntPos = cmds.xform(startJnt, q = True, t = True, ws = True)
        midJntPos = cmds.xform(midJnt, q = True, t = True, ws = True)
        endJntPos = cmds.xform(endJnt, q = True, t = True, ws = True)

        # Create a plane.
        plane = cmds.polyCreateFacet(n = 'jntUpVecPlane_geo', p = [startJntPos, midJntPos, endJntPos])[0]

        return plane


    @classmethod
    def getFaceNormalVec(cls, face):
        '''
        Get normal vector of a given face.
        '''

        rawFaceNormalInfo = cmds.polyInfo(face, faceNormals = True)[0]
        normalVecStr = re.match(r'.+:\s(.+)\n', rawFaceNormalInfo).group(1)
        normalVecStrLs = normalVecStr.split(' ')
        faceNormalVec = []

        for normalVecStr in normalVecStrLs:
            faceNormalVec.append(float(normalVecStr))

        return faceNormalVec


    @classmethod
    def stretchy(cls, curve, bndJntLs):
        '''
        Control aim axis joint scale depend on curve length.
        '''

        # Create curveInfo node.
        crvInfo = cmds.createNode('curveInfo', n = curve + '_crvInfo')

        # Connect curve shape's worldspace attribute to curveInfo node's inputCurve
        crvShp = cmds.listRelatives(curve, s = True)[0]
        cmds.connectAttr('%s.worldSpace' %crvShp, '%s.inputCurve' %crvInfo, f = True)

        # Get curve length
        crvLength = cmds.getAttr('%s.arcLength' %crvInfo)

        # Create multiplyDivide node and connections.
        jntMulDiv = cmds.createNode('multiplyDivide', n = curve + '_jntMulVal_div')
        cmds.setAttr('%s.operation' %jntMulDiv, 2)
        cmds.setAttr('%s.input2X' %jntMulDiv, crvLength)
        cmds.connectAttr('%s.arcLength' %crvInfo, '%s.input1X' %jntMulDiv, f = True)

        # Connect jntMulDiv's outputX to bind joints aim axis scale
        for bndJnt in bndJntLs:
            # If bndJnt is end joint, skip connection.
            if bndJnt == bndJntLs[-1]:
                continue
            cmds.connectAttr('%s.outputX' %jntMulDiv, '%s.scaleX' %bndJnt, f = True)


    @classmethod
    def setUpScaleNormalizeCurve(cls, crv):
        crvShape = cmds.listRelatives(crv, shapes=True, noIntermediate=True)[0]
        crvInfo = cmds.listConnections(crvShape, type='curveInfo')[0]
        mulDivNode = cmds.listConnections(crvInfo, type='multiplyDivide')[0]

        scaleNormalizeCrv = cmds.duplicate(crv, n='%s_scaleNormalizeCrv' % crv)[0]
        scaleNormalizeCrvInfo = cmds.createNode('curveInfo', n='%s_crvInfo' % scaleNormalizeCrv)

        scaleNormalizeCrvShape = cmds.listRelatives(scaleNormalizeCrv, shapes=True, ni=True)[0]
        cmds.connectAttr(scaleNormalizeCrvShape+'.worldSpace', scaleNormalizeCrvInfo+'.inputCurve')
        cmds.connectAttr(scaleNormalizeCrvInfo+'.arcLength', mulDivNode+'.input2X')

        cmds.setAttr(scaleNormalizeCrv+'.inheritsTransform', True)
        cmds.setAttr(scaleNormalizeCrv+'.visibility', False)

        return scaleNormalizeCrv


    @classmethod
    def cleanUpOutliner(cls, crvBndJntLs, bndJntLs, ctrlLs, crv, scaleNormalizeCrv, ikh):
        '''
        Create gorup hierarchy and parent nodes to related group and hide unneeded objects.
        '''

        allGrp = cmds.createNode('transform', n = crv + '_splineIKFK_grp')

        chldGrpNameLs = ['doNotTouch_grp', 'crv_jnt_grp', 'jnt_grp', 'ctrl_grp']
        hideObjLs = []

        # Create group and parent related nodes.
        for grpName in chldGrpNameLs:
            chldGrp = cmds.createNode('transform', n = crv + '_' + grpName)

            if grpName == 'doNotTouch_grp':
                cmds.parent(chldGrp, allGrp)

            if grpName == 'crv_jnt_grp':
                cmds.parent(crvBndJntLs, chldGrp)
                cmds.parent(chldGrp, crv + '_doNotTouch_grp')
                hideObjLs.append(chldGrp)

            elif grpName == 'jnt_grp':
                cmds.parent(bndJntLs[0], chldGrp)
                cmds.parent(chldGrp, crv + '_doNotTouch_grp')

            elif grpName == 'ctrl_grp':
                cmds.parent(ctrlLs[0] + '_zero', chldGrp)
                cmds.parent(chldGrp, allGrp)

        cmds.parent(crv, scaleNormalizeCrv, ikh, crv + '_doNotTouch_grp')
        hideObjLs.append(crv)
        hideObjLs.append(ikh)

        # Hide unneeded objects.
        for obj in hideObjLs:
            cmds.setAttr('%s.visibility' %obj, False)


    @classmethod
    def connections(cls, crv, bndJntLs):
        '''
        Make connections to all_ctrl.
        '''

        allCtrl = crv + '_all_ctrl'

        cmds.connectAttr('%s.bindJointsVis' %allCtrl, '%s_jnt_grp.visibility' %crv, f = True)

        for bndJnt in bndJntLs:
            cmds.connectAttr('%s.scaleY' %allCtrl, '%s.scaleY' %bndJnt, f = True)
            cmds.connectAttr('%s.scaleY' %allCtrl, '%s.scaleZ' %bndJnt, f = True)
            # If bndJnt is end joint, connect scaleX also.
            if bndJnt == bndJntLs[-1]:
                cmds.connectAttr('%s.scaleY' %allCtrl, '%s.scaleX' %bndJnt, f = True)


    @classmethod
    def bindGeo(cls, *args):
        '''
        Bind geometry with bind joints.
        '''

        selLs = cmds.ls(sl = True)

        ctrl = selLs[0]
        geoLs = selLs[1:]

        crv = re.match(r'(.+)_.+_ctrl', ctrl).group(1)
        bndJntRoot = crv + '_0_jnt'
        bndJnts = cmds.listRelatives(bndJntRoot, ad = True, type = 'joint')

        for geo in geoLs:
            cmds.select(bndJntRoot, r = True)
            cmds.select(bndJnts, add = True)
            cmds.select(geo, add = True)

            cmds.skinCluster(dr = 4, toSelectedBones = True, bindMethod = 0)


    @classmethod
    def selAllCtrl(cls, *args):
        selCtrls = cmds.ls(sl = True)

        allCtrls = []

        for selCtrl in selCtrls:
            crv = re.match(r'(.+)_.+_ctrl', selCtrl).group(1)
            allCtrl = crv + '_all_ctrl'
            allCtrls.append(allCtrl)

        cmds.select(allCtrls, r = True)
