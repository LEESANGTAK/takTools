'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 11/04/2016

Description:
Save and rebuild render layer set up.

Usage:
Copy and paste this script to maya scripts folder.

Run following code in python tab.
import tak_saveRenderLayer
reload(tak_saveRenderLayer)
renLyrSaveObj = tak_saveRenderLayer.SaveRenderLayer()
renLyrSaveObj.UI()
'''


import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import os, pickle


renStatLs = ['castsShadows', 'receiveShadows', 'motionBlur', 'primaryVisibility', 'smoothShading', 'visibleInReflections', 'visibleInRefractions', 'doubleSided']

class SaveRenderLayer(object):
	def UI(self):
		winName = 'saveRenLyrWin'

		if cmds.window(winName, exists = True):
			cmds.deleteUI(winName)

		cmds.window(winName, title = 'Save Render Layer', mnb = False, mxb = False)
		cmds.columnLayout(adj = True)
		cmds.button(label = 'Save Render Layer Information', c = self.saveRenLyrInfoBtnCmd)
		cmds.separator(style = 'in', h = 10)

		cmds.optionMenu('nameSpaceOptMenu', label = 'Namespace: ')
		refNodeList = cmds.ls(references = True)
		for refNode in refNodeList:
			try:
				namespace = cmds.referenceQuery(refNode, namespace = True, shortName = True)
				if 'abc' in namespace or 'cam' in namespace:
					pass
				else:
					cmds.menuItem(label = namespace)
			except:
				pass

		cmds.checkBox('recreateRenChkBox', label = 'Recreate Render Layer: ', v = True)
		cmds.button(label = 'Load Render Layer Information', c = self.loadRenLyrInfoBtnCmd)
		cmds.window(winName, e = True, w = 100, h = 50)
		cmds.showWindow(winName)


	def saveRenLyrInfoBtnCmd(self, *args):
		filePath = self.getFilePath('save')
		renLyrInfo = self.getRenLyrInfo()
		self.saveInfo(renLyrInfo, filePath)


	def loadRenLyrInfoBtnCmd(self, *args):
		filePath = self.getFilePath('load')
		renLyrObjInfo, renLyrShpInfo = self.loadInfo(filePath)
		self.buildRenLyr(renLyrObjInfo, renLyrShpInfo)


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

		with open(filePath, 'w') as f:
			try:
				pickle.dump(info, f)
				OpenMaya.MGlobal.displayInfo('Success to write information.')
			except:
				OpenMaya.MGlobal.displayError('Fail to write information.')
			f.close()


	def loadInfo(self, filePath):
		'''
		Read information from a text file.
		'''

		f = open(filePath, 'r')
		info = pickle.load(f)
		f.close()

		return info


	def getRenLyrInfo(self, *args):
		'''
		Get objects in render layer, material assigning, shape render stats information.
		'''

		renLyrObjInfo = {}
		renLyrShpInfo = {}

		renLyrLs = cmds.ls(type = 'renderLayer')

		for renLyr in renLyrLs:
			# Pass if render layer is default render layer.
			if 'defaultRenderLayer' in renLyr:
				continue
			else:
				try:
					# Select render layer.
					cmds.editRenderLayerGlobals(currentRenderLayer = renLyr)

					objsInRenLyr = cmds.listConnections('%s.renderInfo' %renLyr, s = False, d = True)
					if objsInRenLyr:
						# Initialize list
						shpInfoObjLs = []

						renLyrObjInfo[renLyr] = objsInRenLyr
						for obj in objsInRenLyr:
							shps = cmds.ls(cmds.listRelatives(obj, ad = True, ni = True), type = 'mesh', noIntermediate = True)
							if shps:
								for shp in shps:
									shpInfoObj = ShapeInfo(shp)
									shpInfoObjLs.append(shpInfoObj)

						renLyrShpInfo[renLyr] = shpInfoObjLs
					else:
						continue # If no objects in render layer skip to the next render layer.
				except:
					pass

		cmds.editRenderLayerGlobals(currentRenderLayer = 'defaultRenderLayer')

		# Print result.
		for renLyr in renLyrShpInfo.keys():
			print('> Render Layer: ' + renLyr, '   Objects: ' + str(renLyrObjInfo[renLyr]))

		return renLyrObjInfo, renLyrShpInfo


	def buildRenLyr(self, renLyrObjInfo, renLyrShpInfo, *args):
		'''
		Create render layer and add corresponding object to render layer.
		Assign materials for each render layer with renLyrShpInfo dictionary data.
		Set shape render stats.
		'''

		nameSpace = cmds.optionMenu('nameSpaceOptMenu', q = True, v = True)

		cmds.editRenderLayerGlobals(currentRenderLayer = 'defaultRenderLayer')

		recreateRenLyrOpt = cmds.checkBox('recreateRenChkBox', q = True, v = True)
		if recreateRenLyrOpt:
			# Delete all render layers.
			oldRendLyrLs = cmds.ls(type = 'renderLayer')
			for oldRenLyr in oldRendLyrLs:
				if not 'defaultRenderLayer' in oldRenLyr:
					cmds.delete(oldRenLyr)
			# Create render layers.
			for renderLayer in renLyrShpInfo.keys():
				cmds.createRenderLayer(empty = True, name = renderLayer, noRecurse = True)

		for renLyr in renLyrShpInfo.keys():
			cmds.editRenderLayerGlobals(currentRenderLayer = renLyr)

			# Add objects to corresponding render layer.
			for obj in renLyrObjInfo[renLyr]:
				if ':' in obj:
					obj = nameSpace + ':' + obj.split(':', 1)[-1]
				if cmds.objExists(obj):
					cmds.editRenderLayerMembers(renLyr, obj, noRecurse = True)
				else:
					pass

			for shpObj in renLyrShpInfo[renLyr]:
				mat = shpObj.assignedMat
				if ':' in mat:
					mat = nameSpace + ':' + mat.split(':', 1)[-1]
				if not cmds.objExists(mat):
					continue

				shape = shpObj.shapeName
				if ':' in shape:
					newNameSpacedName = nameSpace + ':' + shape.split(':', 1)[-1]
					if cmds.objExists(newNameSpacedName):
						# Material assign.
						cmds.select(newNameSpacedName, r = True)
						cmds.hyperShade(assign = mat)

						# Set shape render stats.
						for renStat in renStatLs:
							renStatVal = getattr(shpObj, renStat)
							cmds.setAttr('%s.%s' %(newNameSpacedName, renStat), renStatVal)
					else:
						pass
				else:
					if cmds.objExists(shape):
						# Material assign.
						cmds.select(shape, r = True)
						cmds.hyperShade(assign = mat)

						# Set shape render stats.
						for renStat in renStatLs:
							renStatVal = getattr(shpObj, renStat)
							cmds.setAttr('%s.%s' %(shape, renStat), renStatVal)
					else:
						pass

		print('> Build render layer job is done.')



class ShapeInfo(object):
	assignedMat = ''

	def __init__(self, shape):
		self.shapeName = shape
		self.getShpRenStat(shape)
		self.getAssignedMat(shape)


	def getShpRenStat(self, shp):
		for renStat in renStatLs:
			stat = cmds.getAttr('%s.%s' %(shp, renStat))
			setattr(self, renStat, stat)


	def getAssignedMat(self, shp):
			sg = cmds.ls(cmds.listConnections(shp), type = 'shadingEngine')
			rmvSgSet = set(['initialShadingGroup'])
			sg = list(set(sg) - rmvSgSet)

			if sg:
				mat = cmds.ls(cmds.listConnections(sg), materials = True)
				setattr(self, 'assignedMat', mat[0])
			else:
				pass