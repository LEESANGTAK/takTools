'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 06/09/2016

Description:
This script can save specific scene information in a text file and recreate with saved file.

Usage:
import tak_saveSceneInfo
reload(tak_saveSceneInfo)
tak_saveSceneInfo.ui()
'''



import os
import pickle
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya



def ui():
	win = 'saveInfoWin'

	if cmds.window(win, exists = True):
		cmds.deleteUI(win)

	cmds.window(win, title = 'Save Scene Information')

	cmds.columnLayout('mainColLo', p = win, adj = True)
	cmds.rowColumnLayout('setRowColLo', p = 'mainColLo', numberOfColumns = 2, columnWidth = [(1, 130), (2, 130)])
	cmds.button(p = 'setRowColLo', label = 'Save Selected Set Info', c = saveSetBtnCmd)
	cmds.button(p = 'setRowColLo', label = 'Create Set from a File', c = createSetBtnCmd)

	cmds.separator(p = 'mainColLo', h = 5, style = 'in')

	cmds.rowColumnLayout('litLnkRowColLo', p = 'mainColLo', numberOfColumns = 2, columnWidth = [(1, 130), (2, 130)])
	cmds.button(p = 'litLnkRowColLo', label = 'Save Scene Light Link Info', c = saveLitLnkBtnCmd)
	cmds.button(p = 'litLnkRowColLo', label = 'Relink Lights from a File', c = reLnkLitBtnCmd)

	cmds.window(win, e = True, w = 50, h = 50)
	cmds.showWindow(win)


def saveSetBtnCmd(*args):
	'''
	Save set button command.
	'''

	setInfoObj = SetInfo() # Create set information object.

	filePath = setInfoObj.getFilePath('save')
	setInfo = setInfoObj.getSelSetInfo()
	setInfoObj.saveInfo(setInfo, filePath)


def createSetBtnCmd(*args):
	'''
	Create set button command.
	'''

	setInfoObj = SetInfo() # Create set information object.

	filePath = setInfoObj.getFilePath('load')
	info = setInfoObj.readInfo(filePath)
	setInfoObj.createSet(info)


def saveLitLnkBtnCmd(*args):
	'''
	Save light link button command.
	'''

	litLnkInfoObj = LightLinkInfo() # Create set information object.

	filePath = litLnkInfoObj.getFilePath('save')
	litLnkInfo = litLnkInfoObj.getSceneLitLnkInfo()
	litLnkInfoObj.saveInfo(litLnkInfo, filePath)


def reLnkLitBtnCmd(*args):
	'''
	Relink light button command.
	'''

	litLnkInfoObj = LightLinkInfo() # Create set information object.

	filePath = litLnkInfoObj.getFilePath('load')
	info = litLnkInfoObj.readInfo(filePath)
	litLnkInfoObj.relinkLit(info)



class SceneInfoBase():
	'''
	Save scene information base class.
	Contain common attributes and methods for saving scene information and reading scene information.
	'''

	def getFilePath(self, mode):
		'''
		Get file path and return.
		'''

		# Show file dialog.
		curScenePath = cmds.file(q = True, sceneName = True)
		curWorkDir = os.path.dirname(curScenePath)

		if mode == 'save':
			filePath = cmds.fileDialog2(fileMode = 0, caption = 'Save', startingDirectory = curWorkDir, fileFilter = '*.txt')[0]
		elif mode == 'load':
			filePath = cmds.fileDialog2(fileMode = 1, caption = 'Load', startingDirectory = curWorkDir, fileFilter = '*.txt')[0]

		return filePath


	def saveInfo(self, info, filePath):
		'''
		Write information in a text file.
		'''

		with open(filePath, 'wb') as f:
			try:
				pickle.dump(info, f)
				OpenMaya.MGlobal.displayInfo('Success to write information.')
			except Exception as e:
				OpenMaya.MGlobal.displayError('Fail to write information.')


	def readInfo(self, filePath):
		'''
		Read information from a text file.
		'''

		with open(filePath, 'rb') as f:
			info = pickle.load(f)

		return info



class SetInfo(SceneInfoBase):
	'''
	Set information class.
	Save set information and create set from saved information.
	'''

	def getSelSetInfo(self):
		'''
		Get selected set and subset information.
		'''

		setTable = {}

		def getSetInfo(set):
			setMembers = cmds.sets(set, q=True)
			setTable[set] = setMembers

			sets = cmds.ls(setMembers, type='objectSet')
			if not sets:
				return
			else:
				for item in sets:
					getSetInfo(item)

		rootSet = cmds.ls(sl=True, type='objectSet')[0]
		getSetInfo(rootSet)

		return setTable


	def createSet(self, info):
		'''
		Create set with information.
		'''

		for set in reversed(list(info.keys())):
			if info[set] == None:
				continue

			existsObjLs = []
			for obj in info[set]:
				if cmds.objExists(obj):
					existsObjLs.append(obj)
				else:
					OpenMaya.MGlobal.displayWarning('%s is not exists in the %s.' %(obj, set))
			info[set] = existsObjLs

			# Create set.
			cmds.sets(info[set], n = set)


class LightLinkInfo(SceneInfoBase):
	'''
	Light link information class.
	Save light link information and create light link from saved information.
	'''

	def getSceneLitLnkInfo(self):
		'''
		Get current scene light links information.
		'''

		litLinkTable = {}

		litLs = cmds.ls(type = 'light')
		if litLs:
			for lit in litLs:
				ilObjLs = cmds.ls(cmds.lightlink(query = True, light = lit), type = 'mesh')
				litLinkTable[lit] = ilObjLs

		return litLinkTable


	def relinkLit(self, info):
		'''
		Relink lights with information.
		'''

		for lit in info.keys():
			# Break current light links.
			ilObjLs = cmds.ls(cmds.lightlink(query = True, light = lit), type = 'mesh')
			cmds.lightlink(b = True, light = lit, object = ilObjLs)

			# Get object list linked to light from saved information.
			litLinkObjLs = info[lit]
			for litLinkObj in litLinkObjLs:
				try:
					# Make light link to each shape.
					cmds.lightlink(make = True, light = lit, object = litLinkObj)
				except:
					OpenMaya.MGlobal.displayWarning("%s is not exists.\n Can't be linked with %s." %(litLinkObj, lit))