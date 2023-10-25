'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
Additional functions for the 'IH_buildSpIkChain.mel' script.
'''



import maya.cmds as cmds
import random


def ui():
	winName = 'addFuncIH_buildSpIkChainWin'

	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Addtional Functions for IH_buildSpIkChain', mnb = False, mxb = False)
	cmds.columnLayout('mainColLo', adj = True, rs = 5)
	cmds.text(label = 'Select \'...Block_GRP\'.', align = 'left')
	cmds.button(label = 'Reset Zero Transform Node', c = resetZeroTrsf)
	cmds.button(label = 'Transfer Control Value to Zero Transform Node', c = trnsCtrlValToZeroTrsf)
	cmds.button(label = 'Default Setting', c = setHairChainDefaultValue)
	cmds.button(label = 'Set Random Rotation Value for Sine Deformer', c = setRandRoValSinDfm, ann = 'Select \'Block\' group.')
	cmds.button(label = 'Fk/IK Hybrid Setup', c = fkIkHbrd)
	cmds.window(winName, e = True, w = 150, h = 30)
	cmds.showWindow(winName)


def resetZeroTrsf(*args):
	'''
	Set to 0 for '_ctr#_zero' group of selected hair block.
	'''

	selHairBlock = cmds.ls(sl = True)[0]

	prefix = selHairBlock.split('_Block')[0]

	attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']

	for i in range(1, 10, 1):
		for attr in attrList:
			try:
				if attr == 'translateZ' and i != 1:
					cmds.setAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr), -5)
				else:
					cmds.setAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr), 0)
			except:
				if attr == 'translateZ' and i != 1:
					cmds.setAttr('%s.%s' %('%s_ctrEnd_zero' %prefix, attr), -5)
				else:
					cmds.setAttr('%s.%s' %('%s_ctrEnd_zero' %prefix, attr), 0)


def trnsCtrlValToZeroTrsf(*args):
	'''
	Transfer value of 'hair#_ctr#_crv' attributes to the '_zero group'.
	'''

	selList = cmds.ls(sl = True)
	attrList = ['rotateX', 'rotateY', 'rotateZ']
	for sel in selList:
		prefix = sel.split('_Block')[0]
		for i in range(1, 10, 1):
			for attr in attrList:
				try:
					crvAttrVal = cmds.getAttr('%s.%s' %('%s_ctr%i_crv' %(prefix, i), attr))
					if crvAttrVal == 0:
						continue
					else:
						zeroAttrVal = cmds.getAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr))
						setAttrVal = zeroAttrVal + crvAttrVal
						cmds.setAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr), setAttrVal)
						cmds.setAttr('%s.%s' %('%s_ctr%i_crv' %(prefix, i), attr), 0)
				except:
					break


def setHairChainDefaultValue(*args):
	'''
	Set Default Value for Hair Chain Attributes
	'''

	hairChainBlockGrps = cmds.ls(sl = True)
	for grp in hairChainBlockGrps:
		hairChainName = grp.rsplit('_Block_GRP')[0]
		
		if cmds.objExists(hairChainName + '_nucleus'):
			# Set nucleus attributes.
			nucName = hairChainName + '_nucleus'
			cmds.setAttr('%s.spaceScale' %nucName, 1)
		
		# Set endCtr attributes.
		cmds.select('%s*_ctrEnd_crv' %hairChainName, r = True)
		endCtrLs = cmds.ls(sl = True, type = 'transform')
		for endCtr in endCtrLs:
			if cmds.objExists(hairChainName + '_nucleus'):
				# Set dynamic attributes
				cmds.setAttr('%s.Damp' %endCtr, 0.1)
				cmds.setAttr('%s.Friction' %endCtr, 0.1)
				cmds.setAttr('%s.startCurveAttract' %endCtr, 0.0)
				cmds.setAttr('%s.bendResistance' %endCtr, 0.25)
			
				# Set hair system attributes.
				hairSysName = endCtr.rsplit('_ctrEnd_crv')[0] + '_hairSystemShape'
				cmds.setAttr('%s.stretchResistance' %hairSysName, 200)
				cmds.setAttr('%s.compressionResistance' %hairSysName, 200)
				cmds.setAttr("%s.hairWidthScale[0].hairWidthScale_FloatValue" %hairSysName, 100)
				cmds.setAttr("%s.hairWidthScale[1].hairWidthScale_FloatValue" %hairSysName, 200)

			# Set sine deformer attributes.
			cmds.setAttr('%s.waveSize' %endCtr, 0.25)
			ikCrvName = endCtr.rsplit('_ctrEnd_crv')[0] + '_splineIKCurveShape'
			sine = cmds.listConnections(ikCrvName, s = True, d = False, type = 'nonLinear')[0]
			cmds.setAttr('%s.wavelength' %sine, 3)


def fkIkHbrd(*args):
	'''
	FK/IK Hybrid Setup
	'''

	selLs = cmds.ls(sl = True)
	drvrCtrl = selLs[0]
	drvnCtrlZero = selLs[1]

	oriGrp = cmds.duplicate(drvrCtrl, po = True, n = drvrCtrl + '_ori_grp')
	cmds.orientConstraint(drvrCtrl, oriGrp, mo = False)
	cmds.parent(drvnCtrlZero, oriGrp)


def setRandRoValSinDfm(*args):
	'''
	Description:
		Set random value on sine deformer handle's rotateZ that twist axis.

	Parameters:
		None

	Returns:
		None
	'''

	sineHndls = [x for x in cmds.ls(sl = True, dag = True) if 'sine' in x and not 'Shape' in x]

	for sineHndl in sineHndls:
		ranVal = random.uniform(1, 90)
		cmds.setAttr(sineHndl + '.rotateZ', ranVal)