'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script set up helper joint system.
Helper joint is driven by pose reader and have control.
Animator can modify helper joint transform using control when needed.
Sometimes joint rotation value that drive helper joint spit out wrong value because of gimbal lock.
That's why angle based pose reader is good for handling helper joint.

Usage:
1. Copy this script and paste in your scripts folder.

2. In maya python tab, run following code.
import tak_helperJoint
reload(tak_helperJoint)
tak_helperJoint.ui()
'''

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

from functools import partial
import re

from ..rigging import tak_createCtrl


def ui():
	winName = 'helperJointWin'

	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Helper Joint UI')

	cmds.tabLayout('mainTabLay', tv = False)
	cmds.tabLayout('subTabLay', tv = False)
	cmds.columnLayout('mainColLay', adj = True)

	cmds.textFieldGrp('poseNameTexFld', label = 'Pose Name: ', columnWidth = [(1, 120), (2, 120)])
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Sel', c = fillPoseName)
	cmds.intFieldGrp('targetPoseFrameIntFldGrp', label = 'Target Pose Frame: ')
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Current Frame', c = partial(loadCurrentFrame, 'targetPoseFrameIntFldGrp'))
	cmds.intFieldGrp('startPoseFrameIntFldGrp', label = 'Start Pose Frame: ', value1 = 1)
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Current Frame', c = partial(loadCurrentFrame, 'startPoseFrameIntFldGrp'))

	cmds.separator(h = 10, style = 'in')

	cmds.textFieldButtonGrp('drvrJointTexButGrp', label = 'Driver Joint: ', buttonLabel = '<<', columnWidth = [(1, 120), (2, 120), (3, 50)], bc = partial(loadSel, 'drvrJointTexButGrp'))
	cmds.textFieldButtonGrp('chldJointTexBtnGrp', label = 'Child Joint: ', buttonLabel = '<<', columnWidth = [(1, 120), (2, 120), (3, 50)], bc = partial(loadSel, 'chldJointTexBtnGrp'))
	cmds.textFieldButtonGrp('prntJointTexBtnGrp', label = 'Parent Joint: ', buttonLabel = '<<', columnWidth = [(1, 120), (2, 120), (3, 50)], bc = partial(loadSel, 'prntJointTexBtnGrp'))

	cmds.separator(h = 10, style = 'in')

	cmds.text(label = 'Select a vertex on problem pose.')
	cmds.button(label = 'Set Initial State', h = 30, c = initState)

	cmds.separator(h = 10, style = 'none')

	cmds.text(label = 'Place helper joint using the sdk locator.')
	cmds.button(label = 'Set Pose State', h = 30, c = setPoseState)

	cmds.separator(h = 10, style = 'in')

	cmds.text(label = 'Go to the bind pose and select helper joints.')
	cmds.rowColumnLayout('srchRplcRowColLo', numberOfColumns = 3, columnWidth = [(2, 50), (3, 50)])
	cmds.text(label = 'Driver Joint Search / Replace: ')
	cmds.textField('jntSrchTxtFld', text = '_l')
	cmds.textField('jntRplcTxtFld', text = '_r')
	cmds.text(label = 'Helper Joint Search / Replace: ')
	cmds.textField('helperJntSrchTxtFld', text = '_l_')
	cmds.textField('helperJntRplcTxtFld', text = '_r_')
	cmds.setParent('mainColLay')

	cmds.button(label = 'Mirror Selected Helper Joint', h = 30, c = mirrorCorJnt)

	cmds.window(winName, e = True, w = 250, h = 150)
	cmds.showWindow(winName)


def fillPoseName(*args):
	selObj = cmds.ls(sl = True)[0]
	selAttrs = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
	poseName = selObj

	if selAttrs:
		rawAttrVal = cmds.getAttr(selObj + '.' + selAttrs[0])
		niceAttrVal = int(round(rawAttrVal, 0))
		niceValName = ''
		if niceAttrVal >= 0:
			niceValName = 'p' + str(abs(niceAttrVal))
		else:
			niceValName = 'n' + str(abs(niceAttrVal))
		poseName += '_' + selAttrs[0] + '_' + niceValName

	cmds.textFieldGrp('poseNameTexFld', e = True, text = poseName)


def loadSel(wgtName):
	sel = cmds.ls(sl = True)[0]
	cmds.textFieldButtonGrp(wgtName, e = True, text = sel)

	# Fill parent joint text field and child joint text field.
	prntJnt = cmds.listRelatives(sel, p = True, type = 'joint')[0]
	cmds.textFieldButtonGrp('prntJointTexBtnGrp', e = True, text = prntJnt)
	childJnt = cmds.listRelatives(sel, c = True, type = 'joint')[0]
	cmds.textFieldButtonGrp('chldJointTexBtnGrp', e = True, text = childJnt)


def loadCurrentFrame(wgtName, *args):
	curFrame = cmds.currentTime(q = True)
	cmds.intFieldGrp(wgtName, e = True, value1 = curFrame)


def initState(*args):
	global helperJntInst
	helperJntInst = HelperJoint()
	helperJntInst.mainInit()


def setPoseState(*args):
	helperJntInst.poseReaderFin()



class HelperJoint:
	def __init__(self):
		# Initialize instance member varialbes
		self.poseName = cmds.textFieldGrp('poseNameTexFld', q = True, text = True)
		self.trgPoseFrame = cmds.intFieldGrp('targetPoseFrameIntFldGrp', q = True, value1 = True)
		self.startPoseFrame = cmds.intFieldGrp('startPoseFrameIntFldGrp', q = True, value1 = True)
		self.driverJnt = cmds.textFieldButtonGrp('drvrJointTexButGrp', q = True, text = True)
		self.childJnt = cmds.textFieldButtonGrp('chldJointTexBtnGrp', q = True, text = True)
		self.prntJnt = cmds.textFieldButtonGrp('prntJointTexBtnGrp', q = True, text = True)
		self.helperJnt = self.poseName + '_helper_jnt'


	def mainInit(self):
		# Check if same pose name exists.
		if cmds.objExists(self.poseName + '_helper_jnt'):
			cmds.error('Pose name already exists!')

		# Store current target pose frame and go to the start pose frame.
		cmds.currentTime(self.startPoseFrame)

		# Create a helper joint with selected vertex.
		self.createCorJnt()

		self.createLocGrp()

		self.poseReaderInit()

		# Back to the current pose frame.
		cmds.currentTime(self.trgPoseFrame)

		cmds.select(self.sdkLoc, r = True)


	def createCorJnt(self):
		'''
		Creat a helper joint with selected vertex.
		'''

		vtx = cmds.ls(sl = True)[0]

		# Create a joint from selected vertex.
		vtxWldPos = cmds.pointPosition(vtx, world = True)
		cmds.select(cl = True)
		cmds.joint(p = (vtxWldPos), n = self.helperJnt)
		cmds.CompleteCurrentTool()

		# Constraint for align to the driver joint.
		geo = vtx.split('.')[0]
		cmds.delete(cmds.orientConstraint(self.driverJnt, self.helperJnt, mo = False))

		# Freeze transform
		cmds.makeIdentity(self.helperJnt, apply = True)

		# Add influence.
		skinClst = mel.eval('findRelatedSkinCluster("%s");' %geo)
		cmds.skinCluster(skinClst, e = True, dr = 4, lw = True, wt = 0, ai = self.helperJnt)
		cmds.setAttr('%s.liw' %self.helperJnt, False)


	def createLocGrp(self):
		# Create set driven key locator
		self.sdkLoc = cmds.spaceLocator(n = '%s_sdk_loc' %self.helperJnt)[0]
		cmds.delete(cmds.parentConstraint(self.helperJnt, self.sdkLoc, mo = False, w = 1))
		cmds.parent(self.helperJnt, self.sdkLoc)

		# Create constraint group
		helperJntCnstGrp = cmds.createNode('transform', n = '%s_cnst_grp' %self.helperJnt)
		cmds.delete(cmds.parentConstraint(self.helperJnt, helperJntCnstGrp, mo = False, w = 1))
		cmds.parent(self.sdkLoc, helperJntCnstGrp)
		self.helperJntGrpCnst = cmds.parentConstraint(self.prntJnt, helperJntCnstGrp, mo = True)


		driverJntCorJntGrp = self.driverJnt + '_helper_jnt_grp'
		if cmds.objExists(driverJntCorJntGrp):
			cmds.parent(helperJntCnstGrp, driverJntCorJntGrp)
		else:
			cmds.createNode('transform', n = driverJntCorJntGrp)
			cmds.parent(helperJntCnstGrp, driverJntCorJntGrp)


	def poseReaderInit(self):
		# Get joints position
		driverJntPos = cmds.xform(self.driverJnt, q = True, ws = True, t = True)
		childJntPos = cmds.xform(self.childJnt, q = True, ws = True, t = True)

		# Create locator and place
		if not cmds.objExists(self.driverJnt + '_poseReader_base_loc'):
			self.baseLoc = cmds.spaceLocator(n = self.driverJnt + '_poseReader_base_loc')[0]
			cmds.xform(self.baseLoc, ws = True, t = driverJntPos)

			self.triggerLoc = cmds.spaceLocator(n = self.driverJnt + '_poseReader_trigger_loc')[0]
			cmds.xform(self.triggerLoc, ws = True, t = childJntPos)

		else:
			self.baseLoc = self.driverJnt + '_poseReader_base_loc'
			self.triggerLoc = self.driverJnt + '_poseReader_trigger_loc'

		self.startPoseLoc = cmds.spaceLocator(n = self.driverJnt + '_' + self.poseName + '_startPose_loc')[0]
		cmds.xform(self.startPoseLoc, ws = True, t = childJntPos)

		# Parenting
		if not self.triggerLoc in cmds.listRelatives(self.baseLoc, c = True):
			cmds.parent(self.triggerLoc, self.baseLoc)
		cmds.parent(self.startPoseLoc, self.baseLoc)

		# Create angle between and remap value node
		self.startToTargetPoseAnglBtwn = cmds.shadingNode('angleBetween', n = self.poseName + '_startToTargetPose_anglBtwn', asUtility = True)
		self.triggerToTargetPoseAnglBtwn = cmds.shadingNode('angleBetween', n = self.poseName + '_triggerToTargetPose_anglBtwn', asUtility = True)
		self.remapVal = cmds.shadingNode('remapValue', n = self.poseName + '_remapVal', asUtility = True)

		# Constraint
		cmds.pointConstraint(self.childJnt, self.triggerLoc, mo = False)
		cmds.parentConstraint(self.prntJnt, self.baseLoc, mo = True)


	def poseReaderFin(self):
		# Create target pose locator
		childJntPos = cmds.xform(self.childJnt, q = True, ws = True, t = True)
		self.trgPoseLoc = cmds.spaceLocator(n = self.driverJnt + '_' + self.poseName + '_targetPose_loc')[0]
		cmds.xform(self.trgPoseLoc, ws = True, t = childJntPos)

		# Parent target pose locator to the base locator
		cmds.parent(self.trgPoseLoc, self.baseLoc)

		# Connect attribute
		cmds.connectAttr('%s.translate' %self.startPoseLoc, '%s.vector1' %self.startToTargetPoseAnglBtwn, force = True)
		cmds.connectAttr('%s.translate' %self.trgPoseLoc, '%s.vector2' %self.startToTargetPoseAnglBtwn, force = True)

		cmds.connectAttr('%s.translate' %self.triggerLoc, '%s.vector1' %self.triggerToTargetPoseAnglBtwn, force = True)
		cmds.connectAttr('%s.translate' %self.trgPoseLoc, '%s.vector2' %self.triggerToTargetPoseAnglBtwn, force = True)

		cmds.connectAttr('%s.angle' %self.triggerToTargetPoseAnglBtwn, '%s.inputValue' %self.remapVal, force = True)
		cmds.connectAttr('%s.angle' %self.startToTargetPoseAnglBtwn, '%s.inputMax' %self.remapVal, force = True)

		# Set attributes
		cmds.setAttr('%s.outputMin' %self.remapVal, 1.0)
		cmds.setAttr('%s.outputMax' %self.remapVal, 0.0)

		# SDK
		cmds.setDrivenKeyframe('%s.translate' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)
		cmds.setDrivenKeyframe('%s.rotate' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)
		cmds.setDrivenKeyframe('%s.scale' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)

		# Go back to the start pose frame
		cmds.currentTime(self.startPoseFrame)
		cmds.xform(self.sdkLoc, t = (0, 0, 0))

		cmds.setDrivenKeyframe('%s.translate' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)
		cmds.setDrivenKeyframe('%s.rotate' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)
		cmds.setDrivenKeyframe('%s.scale' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)

		cmds.currentTime(self.trgPoseFrame)

		self.poseLocGrp()

		#self.addCtrl()

		self.offLocShapeVis()


	def poseLocGrp(self):
		poseLocGrp = cmds.createNode('transform', n = self.poseName + '_pose_loc_grp')
		cmds.delete(cmds.parentConstraint(self.baseLoc, poseLocGrp, mo = False))
		cmds.parent(self.trgPoseLoc, self.startPoseLoc, poseLocGrp)
		cmds.parent(poseLocGrp, self.baseLoc)


	def addCtrl(self):
		'''
		Add control curve above to the joint.
		Animator can modify helper joint using control curve.
		'''

		ctrl = tak_createCtrl.createCurve('sphere')
		ctrlNewName = cmds.rename(ctrl, self.helperJnt + '_ctrl')
		cmds.delete(cmds.parentConstraint(self.sdkLoc, ctrlNewName))
		cmds.parent(self.helperJnt, ctrlNewName)
		cmds.parent(ctrlNewName, self.sdkLoc)


	def offLocShapeVis(self):
		'''
		Trun off locator shape visibility.
		Because locator does not used when animation.
		'''

		# cmds.setAttr(self.baseLoc + 'Shape.visibility', False)
		# cmds.setAttr(self.triggerLoc + 'Shape.visibility', False)
		# cmds.setAttr(self.startPoseLoc + 'Shape.visibility', False)
		# cmds.setAttr(self.trgPoseLoc + 'Shape.visibility', False)
		cmds.setAttr(self.sdkLoc + 'Shape.visibility', False)



def mirrorCorJnt(*args):
	'''
	Mirror helper joints.
	'''

	jntSrch = cmds.textField('jntSrchTxtFld', q = True, text = True)
	jntRplc = cmds.textField('jntRplcTxtFld', q = True, text = True)
	helperJntSrch = cmds.textField('helperJntSrchTxtFld', q = True, text = True)
	helperJntRplc = cmds.textField('helperJntRplcTxtFld', q = True, text = True)

	selhelperJntLs = cmds.ls(sl = True)

	for helperJnt in selhelperJntLs:
		# Check if target objects exists.
		sdkLoc = helperJnt + '_sdk_loc'
		sDriver = cmds.setDrivenKeyframe(sdkLoc, q=True, cd=True)[0].split('.')[0]
		tDriver = re.sub(jntSrch, jntRplc, sDriver)
		tDriven = re.sub(helperJntSrch, helperJntRplc, sdkLoc)

		# In case target driver is not exists.
		if sDriver == tDriver:
			cmds.warning("Target driver object is not exists. Check the 'Driver Search/Replace' string.")
			return
		# In case target driven is not exists.
		elif sdkLoc == tDriven:
			cmds.warning("Target driven object is not exists. Check the 'Helper Joint Search/Replace' string.")
			return

		# Mirror joint.
		eachPrnt = cmds.listRelatives(helperJnt, parent = True)

		cmds.select(cl = True)
		cmds.joint(n='tmp_root_jnt', p=(0, 0, 0))
		cmds.parent(helperJnt, 'tmp_root_jnt')

		cmds.select(helperJnt, r = True)
		mirCorJnt = cmds.mirrorJoint(mirrorYZ = True, mirrorBehavior = True, searchReplace = (helperJntSrch, helperJntRplc))[0]

		if eachPrnt:
			cmds.parent(helperJnt, eachPrnt[0])
		else:
			cmds.parent(helperJnt, w = True)

		cmds.parent(mirCorJnt, w = True)
		cmds.delete('tmp_root_jnt')

		# Add influence.
		skClst = cmds.listConnections(helperJnt, s = False, d = True, type = 'skinCluster')[0]
		geo = cmds.listConnections(skClst, s = False, d = True, type = 'mesh')[0]
		cmds.skinCluster(skClst, e = True, dr = 4, lw = True, wt = 0, ai = mirCorJnt)
		cmds.setAttr('%s.liw' %mirCorJnt, False)

		# Mirror skin weights.
		cmds.select(geo)
		cmds.MirrorSkinWeights()
		cmds.select(cl = True)

		# Create locator and group.
		createCtrl(mirCorJnt)

		# Constraint to the othersdie parent joint.
		pCnst = list(set(cmds.listConnections('%s_cnst_grp' %helperJnt, s = False, d = True, type = 'parentConstraint')))[0]
		helperJntPrntJnt = list(set(cmds.listConnections(pCnst, s = True, d = False, type = 'joint')))[0]
		mirPrntJnt = re.sub(jntSrch, jntRplc, helperJntPrntJnt)
		cmds.parentConstraint(mirPrntJnt, '%s_cnst_grp' %mirCorJnt, mo = True)

		# Mirror pose reader.
		mirPoseReader(sdkLoc, jntSrch, jntRplc, helperJntSrch, helperJntRplc)

		# Mirror set driven key.
		driverAttr = cmds.setDrivenKeyframe(sdkLoc, q=True, cd=True)[0].split('.')[-1]
		rawDrivenAttrs = cmds.setDrivenKeyframe(sdkLoc, q=True, dn=True)
		for rawDrivenAttr in rawDrivenAttrs:
			drvnAttr = rawDrivenAttr.split('.')[-1]
			drvrVals = cmds.keyframe(rawDrivenAttr, q = True, fc = True)
			drvnVals = cmds.keyframe(rawDrivenAttr, q = True, vc = True)

			# Check if driver is more than two.
			if not drvrVals:
				animatableAttrs = pm.PyNode(sdkLoc).listAnimatable()
				for attr in animatableAttrs:
					animAttrInputNode = attr.connections(d=False, scn=True)
					if animAttrInputNode:
						if isinstance(animAttrInputNode[0], pm.nodetypes.AnimCurve): # In case animCurve
							animCurve = animAttrInputNode[0]
							animCurveInput = animCurve.input.connections(p=True, scn=True)[0]
							animCurveOutput = animCurve.output.connections(p=True, scn=True)[0]

							dupAnimCurve = animCurve.duplicate()[0]
							pm.PyNode(animCurveInput.replace(helperJntSrch, helperJntRplc)) >> dupAnimCurve.input
							dupAnimCurve.output >> pm.PyNode(animCurveOutput.replace(helperJntSrch, helperJntRplc))

						else: # In case blendWeight
							blendWeight = animAttrInputNode[0]
							animCurves = blendWeight.input.connections(scn=True)
							blendWeightOutput = blendWeight.output.connections(p=True, scn=True)[0]

							dupBlendWeight = blendWeight.duplicate()[0]
							dupBlendWeight.output >> pm.PyNode(blendWeightOutput.replace(helperJntSrch, helperJntRplc))
							for animCurve in animCurves:
								if not animCurve.numKeyframes():
									pm.delete(animCurve)
									continue

								animCurveInput = animCurve.input.connections(p=True, scn=True)[0]
								animCurveOutput = animCurve.output.connections(p=True, scn=True)[0]

								dupAnimCurve = animCurve.duplicate()[0]
								pm.PyNode(animCurveInput.replace(helperJntSrch, helperJntRplc)) >> dupAnimCurve.input
								dstIndex = re.search(r'.*\[(\d+)\]', str(animCurveOutput)).group(1)
								dupAnimCurve.output >> dupBlendWeight.input[dstIndex]

								if 'translate' in str(blendWeightOutput):
									for i in range(dupAnimCurve.numKeyframes()):
										dupAnimCurve.setValue(i, -dupAnimCurve.getValue(i))
				continue

			for i in range(len(drvrVals)):
				if 'translate' in drvnAttr:
					cmds.setDrivenKeyframe('%s.%s' %(tDriven, drvnAttr), cd = '%s.%s' %(tDriver,driverAttr), dv = drvrVals[i], v = -drvnVals[i])
				elif 'rotate' in drvnAttr:
					cmds.setDrivenKeyframe('%s.%s' %(tDriven, drvnAttr), cd = '%s.%s' %(tDriver,driverAttr), dv = drvrVals[i], v = drvnVals[i])
				elif 'scale' in drvnAttr:
					cmds.setDrivenKeyframe('%s.%s' %(tDriven, drvnAttr), cd = '%s.%s' %(tDriver,driverAttr), dv = drvrVals[i], v = drvnVals[i])
				else:
					cmds.setDrivenKeyframe('%s.%s' %(tDriven, drvnAttr), cd = '%s.%s' %(tDriver,driverAttr), dv = drvrVals[i], v = drvnVals[i])


def createCtrl(mirCorJnt):
	# Create locator.
	sdkLoc = cmds.spaceLocator(n = '%s_sdk_loc' %mirCorJnt)[0]
	cmds.setAttr(sdkLoc + 'Shape.visibility', False)
	cmds.delete(cmds.parentConstraint(mirCorJnt, sdkLoc, mo = False, w = 1))
	cmds.parent(mirCorJnt, sdkLoc)

	# # Create control.
	# ctrl = tak_createCtrl.createCurve('sphere')
	# ctrlNewName = cmds.rename(ctrl, mirCorJnt + '_ctrl')
	# cmds.delete(cmds.parentConstraint(sdkLoc, ctrlNewName))
	# cmds.parent(mirCorJnt, ctrlNewName)
	# cmds.parent(ctrlNewName, sdkLoc)

	# Create constraint group.
	helperJntCnstGrp = cmds.createNode('transform', n = '%s_cnst_grp' %mirCorJnt)
	cmds.delete(cmds.parentConstraint(mirCorJnt, helperJntCnstGrp, mo = False, w = 1))
	cmds.parent(sdkLoc, helperJntCnstGrp)


def mirPoseReader(sdkLoc, jntSrch, jntRplc, helperJntSrch, helperJntRplc):
	'''
	Description
		Mirror pose reader that connected to helper joint.

	Parameters
		sdkLoc: string - Source locator that applied set driven keyframe.

	Retruns
		None
	'''

	allCnnts = cmds.listHistory(sdkLoc, ac = True)

	# Retrive pose reader base locators.
	trigLoc = [x for x in allCnnts if 'trigger_loc' in x and cmds.objectType(x) == 'transform'][0]
	baseLoc = cmds.listRelatives(trigLoc, p = True)[0]


	mirTrigLocName = re.sub(helperJntSrch, helperJntRplc, trigLoc)
	mirBaseLocName = re.sub(helperJntSrch, helperJntRplc, baseLoc)


	# Retrive pose reader locators.
	startPoseLoc = [x for x in allCnnts if 'startPose_loc' in x][0]
	trgPoseLoc = [x for x in allCnnts if 'targetPose_loc' in x][0]
	poseReaderLocGrp = cmds.listRelatives(trgPoseLoc, p = True)[0]

	mirStartPoseLocName = re.sub(helperJntSrch, helperJntRplc, startPoseLoc)
	mirTrgPoseLocName = re.sub(helperJntSrch, helperJntRplc, trgPoseLoc)
	mirPoseReaderLocGrpName = re.sub(helperJntSrch, helperJntRplc, poseReaderLocGrp)

	# Extra nodes.
	anglBtwns = [x for x in allCnnts if 'anglBtwn' in x]
	remapVal = [x for x in allCnnts if 'remapVal' in x][0]

	mirAnglBtwnNames = []
	for anglBtwn in anglBtwns:
		mirAnglBtwnNames.append(re.sub(helperJntSrch, helperJntRplc, anglBtwn))
	mirRemapValName = re.sub(helperJntSrch, helperJntRplc, remapVal)

	# Retrive joints.
	drvrJnt = cmds.listRelatives(cmds.ls(cmds.listHistory(sdkLoc), type="joint"), parent=True, type="joint")[0]
	drvrJntPrnt = cmds.listRelatives(drvrJnt, parent=True, type="joint")[0]
	drvrJntChld = cmds.listRelatives(drvrJnt, c=True, type="joint")[0]


	mirDrvrJntPrntName = re.sub(jntSrch, jntRplc, drvrJntPrnt)
	mirDrvrJntName = re.sub(jntSrch, jntRplc, drvrJnt)
	mirDrvrJntChldName = re.sub(jntSrch, jntRplc, drvrJntChld)


	# If pose reader base locator is not exists then create.
	mirPoseReaderBaseLoc = mirDrvrJntName + '_poseReader_base_loc'
	if not cmds.objExists(mirDrvrJntName + '_poseReader_base_loc'):
		cmds.spaceLocator(n = mirPoseReaderBaseLoc)
		cmds.delete(cmds.parentConstraint(mirDrvrJntName, mirPoseReaderBaseLoc, mo = False))
		cmds.parentConstraint(mirDrvrJntPrntName, mirPoseReaderBaseLoc, mo = True)

		mirPoseReaderTriggerLoc = cmds.spaceLocator(n = mirDrvrJntName + '_poseReader_trigger_loc')
		cmds.pointConstraint(mirDrvrJntChldName, mirPoseReaderTriggerLoc, mo = False)

		cmds.parent(mirPoseReaderTriggerLoc, mirPoseReaderBaseLoc)

	# Create pose reader group.
	cmds.group(n = mirPoseReaderLocGrpName, em = True)
	cmds.delete(cmds.parentConstraint(mirPoseReaderBaseLoc, mirPoseReaderLocGrpName, mo = False))
	cmds.parent(mirPoseReaderLocGrpName, mirPoseReaderBaseLoc)

	# Create pose reader locators.
	cmds.spaceLocator(n = mirStartPoseLocName)
	cmds.spaceLocator(n = mirTrgPoseLocName)
	cmds.parent(mirStartPoseLocName, mirTrgPoseLocName, mirPoseReaderLocGrpName)

	# Move to the mirrored position.
	startPoseLocTrans = cmds.xform(startPoseLoc, q = True, t = True, ws = True)
	cmds.xform(mirStartPoseLocName, t = [-startPoseLocTrans[0], startPoseLocTrans[1], startPoseLocTrans[2]], ws = True)
	trgPoseLocTrans = cmds.xform(trgPoseLoc, q = True, t = True, ws = True)
	cmds.xform(mirTrgPoseLocName, t = [-trgPoseLocTrans[0], trgPoseLocTrans[1], trgPoseLocTrans[2]], ws = True)

	# Create extra nodes.
	for mirAnglBtwnName in mirAnglBtwnNames:
		cmds.createNode('angleBetween', n = mirAnglBtwnName)

	cmds.createNode('remapValue', n = mirRemapValName)
	cmds.setAttr(mirRemapValName + '.outputMin', 1)
	cmds.setAttr(mirRemapValName + '.outputMax', 0)

	# Connections.
	for mirAnglBtwnName in mirAnglBtwnNames:
		if 'triggerToTargetPose' in mirAnglBtwnName:
			cmds.connectAttr(mirTrigLocName + '.translate', mirAnglBtwnName + '.vector1')
			cmds.connectAttr(mirTrgPoseLocName + '.translate', mirAnglBtwnName + '.vector2')
			cmds.connectAttr(mirAnglBtwnName + '.angle', mirRemapValName + '.inputValue')
		elif 'startToTargetPose' in mirAnglBtwnName:
			cmds.connectAttr(mirStartPoseLocName + '.translate', mirAnglBtwnName + '.vector1')
			cmds.connectAttr(mirTrgPoseLocName + '.translate', mirAnglBtwnName + '.vector2')
			cmds.connectAttr(mirAnglBtwnName + '.angle', mirRemapValName + '.inputMax')



