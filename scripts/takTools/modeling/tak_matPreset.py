'''
Author: Sang-tak Lee
Contact: chst27@gamil.com

Description:
This script is a package of material presets.
'''

import maya.cmds as cmds

class MatPreset(object):
	widgets = {}
	winName = 'matPreWin'


	@classmethod
	def ui(cls):
		if cmds.window(cls.winName, exists = True):
			cmds.deleteUI(cls.winName)

		cls.widgets['win'] = cmds.window(cls.winName, title = 'Material Preset', mnb = False, mxb = False, sizeable = True)
		cls.widgets['mainLo'] = cmds.columnLayout(w = 90)
		cls.widgets['subRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 50), (2, 50)])

		cls.widgets['redMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_red.bmp', command = cls.redMat)
		cls.widgets['greenMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_green.bmp', command = cls.greenMat)
		cls.widgets['blueMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_blue.bmp', command = cls.blueMat)
		cls.widgets['whilteMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_white.bmp', command = cls.whiteMat)
		cls.widgets['blackMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_black.bmp', command = cls.blackMat)
		cls.widgets['blackholeMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_blackhole.bmp', command = cls.blackholeMat)
		cls.widgets['shadowMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_shadowMat.bmp', command = cls.shadowMat)
		cls.widgets['checkerMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_checker.bmp', command = cls.checkertMat)
		cls.widgets['lambertMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_lambert.bmp', command = cls.lambertMat)
		cls.widgets['lambertClayMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_clayLambert.bmp', command = cls.lambertClayMat)
		cls.widgets['lambertRedMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_redLambert.bmp', command = cls.lambertRedMat)
		cls.widgets['lambertOrangeMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_orangeLambert.bmp', command = cls.lambertOrangeMat)
		cls.widgets['lambertYellowMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_yellowLambert.bmp', command = cls.lambertYellowMat)
		cls.widgets['lambertGreenMat'] = cmds.symbolButton(image = r'D:\Tak\tak_maya_preset\prefs\icons\matPreset_greenLambert.bmp', command = cls.lambertGreenMat)
		cmds.window(cls.widgets['win'], edit = True, w = 90, h = 100)
		cmds.showWindow(cls.widgets['win'])


	@staticmethod
	def redMat(*args):
		selList = cmds.ls(sl = True)
		# if not exists 'red_mat' create material
		if not cmds.objExists('red_mat'):
			cmds.shadingNode('surfaceShader', asShader = True, n = 'red_mat')
			cmds.setAttr('red_mat.outColor',  1, 0, 0, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'red_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'red_mat')


	@staticmethod
	def greenMat(*args):
		selList = cmds.ls(sl = True)
		# if not exists 'green_mat' create material
		if not cmds.objExists('green_mat'):
			cmds.shadingNode('surfaceShader', asShader = True, n = 'green_mat')
			cmds.setAttr('green_mat.outColor',  0, 1, 0, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'green_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'green_mat')


	@staticmethod
	def blueMat(*args):
		selList = cmds.ls(sl = True)
		# if not exists 'blue_mat' create material
		if not cmds.objExists('blue_mat'):
			cmds.shadingNode('surfaceShader', asShader = True, n = 'blue_mat')
			cmds.setAttr('blue_mat.outColor',  0, 0, 1, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'blue_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'blue_mat')


	@staticmethod
	def whiteMat(*args):
		selList = cmds.ls(sl = True)
		# if not exists 'white_mat' create material
		if not cmds.objExists('white_mat'):
			cmds.shadingNode('surfaceShader', asShader = True, n = 'white_mat')
			cmds.setAttr('white_mat.outColor',  1, 1, 1, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'white_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'white_mat')


	@staticmethod
	def blackMat(*args):
		selList = cmds.ls(sl = True)
		# if not exists 'black_mat' create material
		if not cmds.objExists('black_mat'):
			cmds.shadingNode('surfaceShader', asShader = True, n = 'black_mat')
			cmds.setAttr('black_mat.outColor',  0, 0, 0, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'black_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'black_mat')


	@staticmethod
	def blackholeMat(*args):
		selList = cmds.ls(sl = True)
		# if not exists 'blackhole_mat' create material
		if not cmds.objExists('blackhole_mat'):
			cmds.shadingNode('lambert', asShader = True, n = 'blackhole_mat')
			cmds.setAttr('blackhole_mat.matteOpacityMode', 0)
			cmds.setAttr('blackhole_mat.color',  0.04, 0.4, 0.04, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'blackhole_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'blackhole_mat')


	@staticmethod
	def checkertMat(*args):
		selList = cmds.ls(sl = True)
		if not cmds.objExists('checker_mat'):
			lambert = cmds.shadingNode('lambert', asShader = True, n = 'checker_mat')
			checkerNode = cmds.shadingNode('checker', asTexture = True)
			texPlcNode = cmds.shadingNode('place2dTexture', asUtility = True)
			cmds.connectAttr('{0}.outUV'.format(texPlcNode), '{0}.uv'.format(checkerNode))
			cmds.connectAttr('{0}.outUvFilterSize'.format(texPlcNode), '{0}.uvFilterSize'.format(checkerNode))
			cmds.connectAttr('{0}.outColor'.format(checkerNode), '{0}.color'.format(lambert), force = True)
			cmds.setAttr('{0}.repeatU'.format(texPlcNode), 30)
			cmds.setAttr('{0}.repeatV'.format(texPlcNode), 30)
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'checker_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'checker_mat')


	@staticmethod
	def lambertMat(*args):
		selLs = cmds.ls(sl = True)
		lambert = cmds.shadingNode('lambert', asShader = True)
		cmds.select(selLs)
		cmds.hyperShade(assign = lambert)


	@staticmethod
	def lambertClayMat(*args):
		selList = cmds.ls(sl = True)
		
		if not cmds.objExists('clay_lambert_mat'):
			lambert = cmds.shadingNode('lambert', asShader = True, n = 'clay_lambert_mat')
			cmds.setAttr('clay_lambert_mat.color',  0.5, 0.32, 0.2, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'clay_lambert_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'clay_lambert_mat')


	@staticmethod
	def lambertRedMat(*args):
		selList = cmds.ls(sl = True)
		
		if not cmds.objExists('red_lambert_mat'):
			lambert = cmds.shadingNode('lambert', asShader = True, n = 'red_lambert_mat')
			cmds.setAttr('red_lambert_mat.color',  1, 0, 0, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'red_lambert_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'red_lambert_mat')


	@staticmethod
	def lambertOrangeMat(*args):
		selList = cmds.ls(sl = True)
		
		if not cmds.objExists('orange_lambert_mat'):
			lambert = cmds.shadingNode('lambert', asShader = True, n = 'orange_lambert_mat')
			cmds.setAttr('orange_lambert_mat.color',  1, 0.5, 0, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'orange_lambert_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'orange_lambert_mat')


	@staticmethod
	def lambertYellowMat(*args):
		selList = cmds.ls(sl = True)
		
		if not cmds.objExists('yellow_lambert_mat'):
			lambert = cmds.shadingNode('lambert', asShader = True, n = 'yellow_lambert_mat')
			cmds.setAttr('yellow_lambert_mat.color',  1, 1, 0, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'yellow_lambert_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'yellow_lambert_mat')


	@staticmethod
	def lambertGreenMat(*args):
		selList = cmds.ls(sl = True)
		
		if not cmds.objExists('green_lambert_mat'):
			lambert = cmds.shadingNode('lambert', asShader = True, n = 'green_lambert_mat')
			cmds.setAttr('green_lambert_mat.color',  0, 1, 0, type = 'double3')
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'green_lambert_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'green_lambert_mat')


	@staticmethod
	def shadowMat(*args):
		selList = cmds.ls(sl = True)
		
		if not cmds.objExists('shadow_mat'):
			shadowMat = cmds.shadingNode('useBackground', asShader = True, n = 'shadow_mat')
			cmds.setAttr('shadow_mat.specularColor',  0, 0, 0, type = 'double3')
			cmds.setAttr('shadow_mat.reflectivity',  0)
			cmds.setAttr('shadow_mat.reflectionLimit',  0)
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'shadow_mat')
		else:
			# assign material to the selected objects
			cmds.select(selList)
			cmds.hyperShade(assign = 'shadow_mat')