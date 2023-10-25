'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 03/02/2016

Description:
Build Ribbon IK/FK for selected curves.

Usage:
import tak_ribbonIKFK
reload(tak_ribbonIKFK)
tak_ribbonIKFK.ribbonIKFK()
'''

import maya.cmds as cmds
import maya.mel as mel

import re

from ..common import tak_misc

# Load matrixNodes plug in for using decompose matrix node
if not cmds.pluginInfo('matrixNodes.mll', q=True, loaded=True):
    cmds.loadPlugin('matrixNodes.mll')



class ribbonIKFK(object):

	uiWdgDic = {}
	uiWdgDic['winName'] = 'ribbonIkFKWin'

	@classmethod
	def __init__(cls):
		if cmds.window(cls.uiWdgDic['winName'], exists = True):
			cmds.deleteUI(cls.uiWdgDic['winName'])

		cls.ui()


	@classmethod
	def ui(cls):
		cmds.window(cls.uiWdgDic['winName'], title = 'Build Ribbon IK/FK')

		cls.uiWdgDic['mainColLo'] = cmds.columnLayout(p = cls.uiWdgDic['winName'], adj = True)

		cls.uiWdgDic['preChkBoxGrp'] = cmds.checkBoxGrp(p = cls.uiWdgDic['mainColLo'], label = "Preview Options: ", numberOfCheckBoxes = 2, labelArray2 = ['Rebuild Curve', 'Auto Orient Controls and Joints'], v1 = True, v2 = True)
		cls.uiWdgDic['numCtrlIntSldrGrp'] = cmds.intSliderGrp(p = cls.uiWdgDic['mainColLo'], label = 'Number of Controls: ', field = True, min = 3, max = 50, v = 1, step=2, cc = cls.numCtrlCC)
		cls.uiWdgDic['numJntIntSldrGrp'] = cmds.intSliderGrp(p = cls.uiWdgDic['mainColLo'], label = 'Number of Joints: ', field = True, min = 5, max = 200, v = 1, cc = cls.numJntsCC)

		cmds.separator(p = cls.uiWdgDic['mainColLo'], style = 'in', h = 10)

		cls.uiWdgDic['optChkBoxGrp'] = cmds.checkBoxGrp(p = cls.uiWdgDic['mainColLo'], label = 'Build Options: ', numberOfCheckBoxes = 2, labelArray2 = ['FK', 'Dynamic'], v1 = False, v2 = False)

		cmds.button(p = cls.uiWdgDic['mainColLo'], label = 'Build', h = 30, c = cls.buildRibbonIKFK)
		cmds.button(p = cls.uiWdgDic['mainColLo'], label = "Bind(Select a '_ctrl' and geometry(s).)", h = 30, c = cls.bindGeo)
		cmds.button(p = cls.uiWdgDic['mainColLo'], label = "Select 'all_ctrl' from Selected Controls", h = 30, c = cls.selAllCtrl)

		cmds.window(cls.uiWdgDic['winName'], e = True, w = 150, h = 50)
		cmds.showWindow(cls.uiWdgDic['winName'])


	@classmethod
	def buildRibbonIKFK(cls, *args):
		'''
		Main method.
		'''

		crv = cmds.ls(sl = True)[0]

		# Create controls
		ctrlLs = cls.createCtrl(crv, cls.rbBndJntLs)

		# Bind ribbon with ribbon bind joints
		cmds.select(cls.rbBndJntLs, cls.ribbon, r = True)
		cmds.skinCluster(dr = 4, toSelectedBones = True, bindMethod = 0)

		# Turn off inherits transform of ribbon transform node.
		# cmds.setAttr('%s.inheritsTransform' %cls.ribbon, False)

		# Add dynamic function

		# Clean up outliner
		cls.cleanUpOutliner(cls.rbBndJntLs, cls.bndJntLs, ctrlLs, crv, cls.ribbon)

		# Connect attributes
		cls.connections(crv, cls.bndJntLs)


	@classmethod
	def ribbonFromCrv(cls, crv, span):
		'''
		Create nurbs ribbon with a curve.
		'''

		# Attach stroke to curve.
		strkDens = 1
		strkWidth = 0.1

		cmds.select(crv, r = True)

		cmds.AttachBrushToCurves()
		strk = cmds.ls(sl = True)[0]
		strkShp = cmds.listRelatives(strk, s = True)[0]
		brush = cmds.listConnections(strkShp, s = True, type = 'brush')[0]

		cmds.setAttr('%s.sampleDensity' %strkShp, strkDens)
		cmds.setAttr('%s.smoothing' %strkShp, 1)
		cmds.setAttr('%s.brushWidth' %brush, strkWidth)
		cmds.setAttr('%s.flatness1' %brush, 1)

		# Convert stroke paint effect to ribbon.
		cmds.select(strk, r = True)
		mel.eval('doPaintEffectsToNurbs(1);')
		cmds.hyperShade(assign = 'lambert1')

		# Rebuild nurbs plane
		ribbon = cmds.listRelatives(c = True)[0]
		cmds.rebuildSurface(ribbon, ch = 1, rpo = 1, rt = 0, end = 1, kr = 0, kcp = 0, kc = 1, su = 1, du = 3, sv = span, dv = 3, tol = 0.01, fr = 0, dir = 2)
		cls.ribbon = cmds.rename(ribbon, crv + '_ribbon')

		# Clean up
		cmds.parent(cls.ribbon, w = True)
		cmds.delete(cls.ribbon, ch = True)
		cmds.delete(strk, strkShp + 'Surfaces')
		cmds.delete(brush + 'Shader', brush + 'ShaderSG')

		return cls.ribbon


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
		else:
			crvNumOfSpan = cmds.getAttr('%s.spans' %crv)
			numOfSpan = crvNumOfSpan

		# Delete ribbon if exists
		if cmds.objExists('%s_ribbon' %crv):
			cmds.delete('%s_ribbon' %crv)

		# Create ribbon
		cls.ribbon = cls.ribbonFromCrv(crv, numOfSpan)

		# Delete ribbon bind joint chain if exists it.
		if cmds.objExists('%s_*_rbBnd' %crv):
			cmds.delete('%s_*_rbBnd' %crv)

		# Build joint chain hierarchy for orient joints.
		cmds.select(cl = True)
		cls.rbBndJntLs = []
		for i in range(numOfCtrl):
			rbBndJntPos = cmds.pointPosition('%s.un[%f]' %(crv, unNum), w = True)
			rbBndJnt = cmds.joint(p = rbBndJntPos, n = '%s_%d_rbBnd' %(crv, i), radius = 5)
			cls.rbBndJntLs.append(rbBndJnt)
			unNum += increNum
		cmds.CompleteCurrentTool()

		# Unparent ribbon bind joints.
		for rbBndJnt in cls.rbBndJntLs:
			if cmds.listRelatives(rbBndJnt, p = True):
				cmds.parent(rbBndJnt, w = True)
			else:
				pass

		# Orient ribbon bind joints
		oriJntOpt = cmds.checkBoxGrp(cls.uiWdgDic['preChkBoxGrp'], q = True, v2 = True)
		if oriJntOpt:
			cls.orientJnt(cls.rbBndJntLs, cls.ribbon, 'rbBndJnt')

		return cls.rbBndJntLs


	@classmethod
	def numJntsCC(cls, *args):
		'''
		Number of Joints slider change command.
		'''

		selCrvLs = cmds.ls(sl = True)

		numOfJnt = cmds.intSliderGrp(cls.uiWdgDic['numJntIntSldrGrp'], q = True, v = True)
		numOfSpan = numOfJnt - 1
		increNum = 1.0 / numOfSpan

		for crv in selCrvLs:
			cls.createBndJnt(crv, numOfJnt, increNum)

		cmds.select(selCrvLs, r = True)


	@classmethod
	def createBndJnt(cls, crv, numOfJnt, increNum, *args):
		# Delete bind joints and pointOnSurfaceInfo node if exists it.
		if cmds.objExists('%s_*_jnt' %crv):
			cmds.delete('%s_*_jnt' %crv)
		if cmds.objExists('%s_*_jnt_pOnSurfInfo' %crv):
			cmds.delete('%s_*_jnt_pOnSurfInfo' %crv)

		# Initialize un value.
		unNum = 0

		# Build joint chain
		cls.bndJntLs = []
		cmds.select(cl = True)
		for i in range(numOfJnt):
			jntPos = cmds.pointPosition('%s.un[%f]' %(crv, unNum), w = True)
			bndJnt = cmds.joint(p = jntPos, n = '%s_%d_jnt' %(crv, i))
			cls.bndJntLs.append(bndJnt)
			unNum += increNum
		cmds.CompleteCurrentTool()

		# Unparent curve bind joints.
		for crvBndJnt in cls.bndJntLs:
			if cmds.listRelatives(crvBndJnt, p = True):
				cmds.parent(crvBndJnt, w = True)
			else:
				pass

		# Orient curve bind joints
		oriJntOpt = cmds.checkBoxGrp(cls.uiWdgDic['preChkBoxGrp'], q = True, v2 = True)
		if oriJntOpt:
			cls.orientJnt(cls.bndJntLs, cls.ribbon, 'bndJnt')

		return cls.bndJntLs


	@classmethod
	def orientJnt(cls, jntLs, ribbon, jntType):
		'''
		Align joint orientation to the ribbon surface.
		'''

		trgSurfShp = cmds.listRelatives(ribbon, s = True)[0]

		for i in range(len(jntLs)):
			curJnt = jntLs[i]

			# Get joint's u,v position on ribbon surface.
			clPtOnSurfNode =  cmds.createNode('closestPointOnSurface', n = curJnt + '_clPtOnSurf')
			cmds.connectAttr('%s.worldSpace[0]' %(trgSurfShp), '%s.inputSurface' %(clPtOnSurfNode), force = True)
			cmds.connectAttr('%s.translate' %(curJnt), '%s.inPosition' %(clPtOnSurfNode), force = True)

			pOnSurfInfoNode = cmds.createNode('pointOnSurfaceInfo', n = curJnt + '_pOnSurfInfo')
			cmds.connectAttr('%s.worldSpace[0]' %(trgSurfShp), '%s.inputSurface' %(pOnSurfInfoNode), force = True)
			cmds.connectAttr('%s.parameterU' %(clPtOnSurfNode), '%s.parameterU' %(pOnSurfInfoNode), force = True)
			cmds.connectAttr('%s.parameterV' %(clPtOnSurfNode), '%s.parameterV' %(pOnSurfInfoNode), force = True)
			parmUVal = cmds.getAttr('%s.parameterU' %(pOnSurfInfoNode))
			parmVVal = cmds.getAttr('%s.parameterV' %(pOnSurfInfoNode))

			cmds.delete(clPtOnSurfNode)
			cmds.setAttr('%s.parameterU' %(pOnSurfInfoNode), parmUVal)
			cmds.setAttr('%s.parameterV' %(pOnSurfInfoNode), parmVVal)
			# cmds.setAttr('%s.parameterV' %(pOnSurfInfoNode), 0.5)

			jntTRVal = cls.getJntPosRo(curJnt, pOnSurfInfoNode, jntType)

			if jntType == 'rbBndJnt':
				cmds.setAttr('%s.translate' %curJnt, *jntTRVal[0])
				cmds.setAttr('%s.rotate' %curJnt, *jntTRVal[1])

				cmds.makeIdentity(curJnt, apply = True)


	@classmethod
	def getJntPosRo(cls, jnt, pntInfoNode, jntType):
		'''
		Build matrix and connect to joint's translate and rotate.
		'''

		# regard aim axis is X
		zVecNode = cmds.shadingNode('vectorProduct', asUtility = True, n = jnt + '_Zvec')
		cmds.connectAttr('%s.result.normal' %pntInfoNode, '%s.input1' %zVecNode, force = True)
		if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':
			cmds.connectAttr('%s.result.tangentV' %pntInfoNode, '%s.input2' %zVecNode, force = True)
		else:
			cmds.connectAttr('%s.result.tangent' %pntInfoNode, '%s.input2' %zVecNode, force = True)
		cmds.setAttr('%s.operation' %zVecNode, 2)

		yVecNode = cmds.shadingNode('vectorProduct', asUtility = True, n = jnt + '_Yvec')
		if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':
			cmds.connectAttr('%s.tangentV' %pntInfoNode, '%s.input1' %yVecNode, force = True)
		else:
			cmds.connectAttr('%s.tangent' %pntInfoNode, '%s.input1' %yVecNode, force = True)
		cmds.connectAttr('%s.output' %zVecNode, '%s.input2' %yVecNode, force = True)
		cmds.setAttr('%s.operation' %yVecNode, 2)

		matrix = cmds.shadingNode('fourByFourMatrix', asUtility = True, n = jnt + '_matrix')
		if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':
			cmds.connectAttr('%s.tangentV.tangentVx' %pntInfoNode, '%s.in00' %matrix, force = True)
			cmds.connectAttr('%s.tangentV.tangentVy' %pntInfoNode, '%s.in01' %matrix, force = True)
			cmds.connectAttr('%s.tangentV.tangentVz' %pntInfoNode, '%s.in02' %matrix, force = True)
		else:
			cmds.connectAttr('%s.tangentX' %pntInfoNode, '%s.in00' %matrix, force = True)
			cmds.connectAttr('%s.tangentY' %pntInfoNode, '%s.in01' %matrix, force = True)
			cmds.connectAttr('%s.tangentZ' %pntInfoNode, '%s.in02' %matrix, force = True)
		cmds.connectAttr('%s.outputX' %yVecNode, '%s.in10' %matrix, force = True)
		cmds.connectAttr('%s.outputY' %yVecNode, '%s.in11' %matrix, force = True)
		cmds.connectAttr('%s.outputZ' %yVecNode, '%s.in12' %matrix, force = True)
		cmds.connectAttr('%s.outputX' %zVecNode, '%s.in20' %matrix, force = True)
		cmds.connectAttr('%s.outputY' %zVecNode, '%s.in21' %matrix, force = True)
		cmds.connectAttr('%s.outputZ' %zVecNode, '%s.in22' %matrix, force = True)
		cmds.connectAttr('%s.positionX' %pntInfoNode, '%s.in30' %matrix, force = True)
		cmds.connectAttr('%s.positionY' %pntInfoNode, '%s.in31' %matrix, force = True)
		cmds.connectAttr('%s.positionZ' %pntInfoNode, '%s.in32' %matrix, force = True)

		deMatrix = cmds.shadingNode('decomposeMatrix', asUtility = True, n = jnt + 'deMatrix')
		cmds.connectAttr('%s.output' %matrix, '%s.inputMatrix' %deMatrix)

		cmds.connectAttr('%s.outputTranslate' %deMatrix, '%s.translate' %jnt, force = True)
		cmds.connectAttr('%s.outputRotate' %deMatrix, '%s.rotate' %jnt, force = True)

		translateVal = cmds.getAttr('%s.translate' %jnt)[0]
		rotateVal = cmds.getAttr('%s.rotate' %jnt)[0]

		if jntType == 'rbBndJnt':
			cmds.delete(pntInfoNode)

		return translateVal, rotateVal


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
			ctrl = cmds.curve(n = jnt.rsplit('_rbBnd')[0] + '_ctrl', d = 1, p = [(-1, 1, 1),(1, 1, 1),(1, 1, -1),(-1, 1, -1),(-1, 1, 1),(-1, -1, 1),(-1, -1, -1),(1, -1, -1),(1, -1, 1),(-1, -1, 1),(1, -1, 1),(1, 1, 1),(1, 1, -1),(1, -1, -1),(-1, -1, -1),(-1, 1, -1)], k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
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
	def cleanUpOutliner(cls, rbBndJntLs, bndJntLs, ctrlLs, crv, ikh):
		'''
		Create gorup hierarchy and parent nodes to related group and hide unneeded objects.
		'''

		allGrp = cmds.createNode('transform', n = crv + '_ribbonIKFK_grp')

		chldGrpNameLs = ['doNotTouch_grp', 'crv_jnt_grp', 'jnt_grp', 'ctrl_grp']
		hideObjLs = []

		# Create group and parent related nodes.
		for grpName in chldGrpNameLs:
			chldGrp = cmds.createNode('transform', n = crv + '_' + grpName)

			if grpName == 'doNotTouch_grp':
				cmds.setAttr('%s.inheritsTransform' %chldGrp, False)
				cmds.parent(chldGrp, allGrp)

			if grpName == 'crv_jnt_grp':
				cmds.parent(rbBndJntLs, chldGrp)
				cmds.parent(chldGrp, crv + '_doNotTouch_grp')
				hideObjLs.append(chldGrp)

			elif grpName == 'jnt_grp':
				cmds.parent(bndJntLs, chldGrp)
				cmds.parent(chldGrp, crv + '_doNotTouch_grp')

			elif grpName == 'ctrl_grp':
				cmds.parent(ctrlLs[0] + '_zero', chldGrp)
				cmds.parent(chldGrp, allGrp)

		cmds.parent(crv, ikh, crv + '_doNotTouch_grp')
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
			cmds.scaleConstraint(allCtrl, bndJnt, mo = True)
			# cmds.connectAttr('%s.scale' %allCtrl, '%s.scale' %bndJnt, f = True)


	@classmethod
	def bindGeo(cls, *args):
		'''
		Bind geometry with bind joints.
		'''

		selLs = cmds.ls(sl = True)

		ctrl = selLs[0]
		geoLs = selLs[1:]

		cmds.select(cmds.listRelatives(type = 'joint'))

		crv = re.match(r'(.+)_.+_ctrl', ctrl).group(1)
		bndJntGrp = crv + '_jnt_grp'
		bndJnts = cmds.listRelatives(bndJntGrp, ad = True, type = 'joint')

		for geo in geoLs:
			cmds.select(bndJnts, r = True)
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
