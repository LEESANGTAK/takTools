'''
Author: Sang-tak Lee
Conttact: chst27@gmail.com

Description:
This script build up the pose reader.
Poser reader's out value 0~1 can drive arbitary attribute's value.
'''


import maya.cmds as cmds


def ui():
	winName = 'poseReaderWin'

	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Pose Reader', mnb = False, mxb = False)
	
	cmds.columnLayout('mainColLo', adj = True)
	cmds.rowColumnLayout('mainRoColLo', numberOfColumns = 2)
	
	cmds.tabLayout(tv = False)
	cmds.columnLayout('poseReaderColLo', adj = True)
	cmds.textFieldGrp('poseNameTxtFldGrp', label = 'Pose Name: ')
	cmds.textFieldGrp('startPoseFrameTxtFldGrp', label = 'Start Pose Frame: ')

	cmds.separator(h = 5, style = 'in')

	cmds.textFieldGrp(label = 'Driver Joint: ')
	cmds.textFieldGrp(label = 'Child Joint: ')
	cmds.textFieldGrp(label = 'Parent Joint: ')

	cmds.setParent('mainRoColLo')
	cmds.columnLayout('drivenAttrsColLo', adj = True)
	cmds.frameLayout(label = 'Driven Attributes')
	cmds.textScrollList()

	cmds.setParent('mainColLo')
	cmds.button(label = 'Apply')

	cmds.window(winName, e = True, w = 300, h = 300)
	cmds.showWindow(winName)


class PoseReader:
	def __init__(self, poseName, startPoseFrame, targetPoseFrame, driverJnt, childJnt, parentJnt, drivenAttrs):
		# Initialize instance variables to store datas
		self.poseName = poseName
		self.startPoseFrame = startPoseFrame
		self.targetPoseFrame = targetPoseFrame
		self.driverJnt = driverJnt
		self.childJnt = childJnt
		self.parentJnt = parentJnt
		self.drivenAttrs = drivenAttrs

	
	def createLocators(self):
		# Create locators on target pose
		baseLoc = cmds.spaceLocator(n = self.driverJnt + '_base_loc')
		cmds.delete(cmds.pointConstraint(self.driverJnt, baseLoc, mo = False))
		cmds.parentConstraint(self.parentJnt, baseLoc, mo = True)

		self.poseTriggerLoc = cmds.spaceLocator(n = self.driverJnt + 'poseTrigger_loc')
		cmds.pointConstraint(self.childJnt, self.poseTriggerLoc, mo = False)
		cmds.parent(self.poseTriggerLoc, baseLoc)

		poseLocGrp = cmds.createNode('transform', n = self.driverJnt + '_' + self.poseName + '_loc_grp')
		cmds.delete(cmds.pointConstraint(self.driverJnt, poseLocGrp, mo = False))
		cmds.parent(poseLocGrp, baseLoc)

		self.targetPoseLoc = cmds.spaceLocator(n = self.driverJnt + '_' + self.poseName + '_targetPose_loc')
		cmds.delete(cmds.pointConstraint(self.childJnt, self.targetPoseLoc, mo = False))
		cmds.parent(self.targetPoseLoc, poseLocGrp)

		# Create locators on start pose
		targetPoseFrame = cmds.currentTime(q = True)
		cmds.currentTime(self.startPoseFrame)

		self.startPoseLoc = cmds.spaceLocator(n = self.driverJnt + '_' + self.poseName + '_startPose_loc')
		cmds.delete(cmds.pointConstraint(self.childJnt, self.startPoseLoc, mo = False))
		cmds.parent(self.startPoseLoc, poseLocGrp)

		cmds.currentTime(targetPoseFrame)


	def createAngleAndRemapValNode(self):
		pass


	def connectNodes(self):
		pass


def applyCmd(*args):
	pass
	# Create pose reader

	# Set driven key for driven attributes


def setDrivenKey():
	pass