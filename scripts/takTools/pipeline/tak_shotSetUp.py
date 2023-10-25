# encoding: UTF-8

'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script for setup maya scene before working.
'''

import maya.cmds as cmds
import maya.mel as mel
import os

class UI(object):
	widgets = {}
	widgets['win'] = 'shotSetUpUI'


	@classmethod
	def __init__(cls):
		# undo
		cmds.undoInfo( state = True, infinity = True )

		# soft edge display for polygon geometry
		# cmds.polyOptions(np = True, se = True)
		
		# view cube
		cmds.viewManip(v = True)
		
		# manipulator line size
		cmds.manipOptions(ls = 1)
		
		# auto save
		cmds.autoSave(en = True)
		cmds.autoSave(int = (60 * 30))
		cmds.autoSave(lim = True)
		cmds.autoSave(max = 3)
		cmds.autoSave(dst = 1)
		user = os.environ.get('USERNAME')
		cmds.autoSave(fol = 'C:/Users/%s/AppData/Local/Temp' %(user))

		# File Dialog Style
		cmds.optionVar(iv = ('FileDialogStyle', 1))

		if cmds.window(cls.widgets['win'], exists = True):
			cmds.deleteUI(cls.widgets['win'])
		cls.ui()


	@classmethod	
	def ui(cls):
		cmds.window(cls.widgets['win'], title = 'Shot Set Up', mnb = False, mxb = False)

		cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)

		cls.widgets['wuFrameLo'] = cmds.frameLayout(label = 'Working Units', collapse = False, collapsable = True, p = cls.widgets['mainColLo'])
		cls.widgets['wuRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 50), (2, 110)], columnAlign = [(1, 'right')], columnOffset = [(2, 'left', 10)], rowOffset = [(2, 'top', 5), (3, 'top', 5)])
		cmds.text(label = 'Linear:')
		cls.widgets['wuLnrOptMenu'] = cmds.optionMenu()
		cmds.menuItem(label = 'millimeter')
		cmds.menuItem(label = 'centimeter')
		cmds.menuItem(label = 'meter')
		cmds.optionMenu(cls.widgets['wuLnrOptMenu'], e = True, v = 'centimeter')
		cmds.text(label = 'Angular:')
		cls.widgets['wuAngOptMenu'] = cmds.optionMenu()
		cmds.menuItem(label = 'degree')
		cmds.menuItem(label = 'radian')
		cmds.optionMenu(cls.widgets['wuAngOptMenu'], e = True, v = 'degree')
		cmds.text(label = 'Time:')
		cls.widgets['wuTimeOptMenu'] = cmds.optionMenu()
		cmds.menuItem(label = 'Film (24 fps)')
		cmds.menuItem(label = 'PAL (25 fps)')
		cmds.menuItem(label = 'NTSC (30 fps)')
		cmds.optionMenu(cls.widgets['wuTimeOptMenu'], e = True, v = 'NTSC (30 fps)')
		cmds.columnLayout(adj = True, p = cls.widgets['wuFrameLo'])
		cmds.button(label = 'Apply', h = 30, c = Functions.setWorkingUnits)

		cls.widgets['timeSldrFrameLo'] = cmds.frameLayout(label = 'Time Slider', collapse = False, collapsable = True, p = cls.widgets['mainColLo'])
		cls.widgets['timeSldrColLo'] = cmds.columnLayout(adj = True)
		cls.widgets['timeSldrRadBtn'] = cmds.radioButtonGrp(label = 'Mode: ', labelArray3 = ['Normal', 'Time', 'Sound'], numberOfRadioButtons = 3, columnWidth = [(1, 40), (2, 80), (3, 70), (4, 70)], select = 1, changeCommand = Functions.timeModeChangeCmd, p = cls.widgets['timeSldrColLo'])
		cmds.radioButtonGrp(cls.widgets['timeSldrRadBtn'], e = True, enable1 = True)
		cls.widgets['timeSldrNrmRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnWidth = [(1, 65), (2, 50), (4, 50)], columnAlign = [(1, 'right')], p = cls.widgets['timeSldrColLo'], visible = True)
		cmds.text(label = 'Start / End: ')
		cls.widgets['timeSldrNrmStartTxtFld'] = cmds.textField(text = '101')
		cmds.text(label = ' ~ ')
		cls.widgets['timeSldrNrmEndTxtFld'] = cmds.textField()

		cls.widgets['timeSldrTimeRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 3, columnWidth = [(1, 65), (2, 50)], columnAlign = [(1, 'right')], p = cls.widgets['timeSldrColLo'], visible = False)
		cmds.text(label = 'Duration: ')
		cls.widgets['timeSldrTimeDurTxtFld'] = cmds.textField()
		cmds.text(label = ' s')
		cmds.text(label = 'Start: ')
		cls.widgets['timeSldrTimeStartTxtFld'] = cmds.textField(text = '101')
		cmds.text(label = '')

		cls.widgets['timeSldrSoundRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 3, columnWidth = [(1, 65), (2, 150), (3, 30)], columnAlign = [(1, 'right')], p = cls.widgets['timeSldrColLo'], visible = False)
		cmds.text(label = 'Sound Path: ')
		cls.widgets['timeSldrSoundPathTxtFld'] = cmds.textField()
		cls.widgets['timeSldrSoundPathBtn'] = cmds.button(label = '...', c = Functions.getSndPath)
		cmds.text(label = 'Start: ')
		cls.widgets['timeSldrSoundStartTxtFld'] = cmds.textField(text = '101')
		cmds.text(label = '')

		cmds.columnLayout(adj = True, p = cls.widgets['timeSldrFrameLo'])
		cmds.button(label = 'Apply', h = 30, c = Functions.setTimeSlider)
		
		cls.widgets['camFrameLo'] = cmds.frameLayout(label = 'Camera', collapse = False, collapsable = True, p = cls.widgets['mainColLo'])
		cls.widgets['camRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 75), (2, 150)], columnAlign = [(1, 'right')], columnOffset = [(2, 'left', 10)], rowOffset = [(2, 'top', 5)])
		cmds.text(label = 'Name:')
		cls.widgets['camTxtFld'] = cmds.textField(text = '')
		cmds.text(label = 'Camera Type:')
		cls.widgets['camTypeOptMenu'] = cmds.optionMenu()
		cmds.menuItem(label = 'Camera')
		cmds.menuItem(label = 'Camera and Aim')
		cmds.menuItem(label = 'Camera, Aim and Up')
		cmds.text(label = 'Resolution:')
		cls.widgets['camResOptMenu'] = cmds.optionMenu()
		cmds.menuItem(label = '1024 x 768')
		cmds.menuItem(label = '1024 x 1280')
		cmds.menuItem(label = '1280 x 720')
		cmds.menuItem(label = '1920 x 1080')
		cmds.optionMenu(cls.widgets['camResOptMenu'], e = True, v = '1024 x 1280')
		cmds.text(label = 'Focal Length:')
		cls.widgets['camFLOptMenu'] = cmds.optionMenu()
		cmds.menuItem(label = '80')
		cmds.menuItem(label = '35')

		cmds.columnLayout(adj = True, p = cls.widgets['camFrameLo'])
		cmds.button(label = 'Apply', h = 30, c = Functions.setShotCam)

		cmds.window(cls.widgets['win'], e = True, w = 250, h = 50)
		cmds.showWindow(cls.widgets['win'])



class Functions(object):

	@classmethod
	def setWorkingUnits(*args):
		# get data
		linearOpt = cmds.optionMenu(UI.widgets['wuLnrOptMenu'], q = True, v = True)
		angularOpt = cmds.optionMenu(UI.widgets['wuAngOptMenu'], q = True, v = True)
		timeOpt = cmds.optionMenu(UI.widgets['wuTimeOptMenu'], q = True, v = True)
		if timeOpt == 'Film (24 fps)':
			timeOpt = 'film'
		elif timeOpt == 'PAL (25 fps)':
			timeOpt = 'pal'
		elif timeOpt == 'NTSC (30 fps)':
			timeOpt = 'ntsc'

		# set with data
		cmds.currentUnit(linear = linearOpt)
		cmds.currentUnit(angle = angularOpt)
		cmds.currentUnit(time = timeOpt)

		# set time slider and current frame to 1
		cmds.playbackOptions(min = 1)
		cmds.currentTime(1)


	@classmethod
	def setTimeSlider(*args):
		mode = cmds.radioButtonGrp(UI.widgets['timeSldrRadBtn'], q = True, select = True)

		if mode == 1:
			nModeStart = cmds.textField(UI.widgets['timeSldrNrmStartTxtFld'], q = True, text = True)
			nModeEnd = cmds.textField(UI.widgets['timeSldrNrmEndTxtFld'], q = True, text = True)
			cmds.playbackOptions(minTime = nModeStart)
			cmds.playbackOptions(maxTime = nModeEnd)
			cmds.currentTime(nModeStart)
		elif mode == 2:
			tModeDur = float(cmds.textField(UI.widgets['timeSldrTimeDurTxtFld'], q = True, text = True))
			tModeStart = float(cmds.textField(UI.widgets['timeSldrTimeStartTxtFld'], q = True, text = True))
			curTime = cmds.currentUnit(q = True, time = True)
			if curTime == 'film':
				fps = 24
			elif curTime == 'pal':
				fps = 25
			elif curTime == 'ntsc':
				fps = 30
			durFrameLen = tModeDur * fps
			tModeEnd = (tModeStart + durFrameLen) - 1
			cmds.playbackOptions(minTime = tModeStart)
			cmds.playbackOptions(maxTime = tModeEnd)
			cmds.currentTime(tModeStart)
		elif mode == 3:
			mel.eval('source "updateSoundMenu.mel";')
			sModeSndPath = cmds.textField(UI.widgets['timeSldrSoundPathTxtFld'], q = True, text = True)
			sModeStart = int(cmds.textField(UI.widgets['timeSldrSoundStartTxtFld'], q = True, text = True))
			sndNode = cmds.sound(offset = sModeStart, file = sModeSndPath)
			soundLength = round(cmds.sound(sndNode, q = True, length = True)) - 1
			sModeEnd = sModeStart + soundLength
			cmds.playbackOptions(minTime = sModeStart)
			cmds.playbackOptions(maxTime = sModeEnd)
			cmds.currentTime(sModeStart)
			gPlayBackSlider = mel.eval( '$tmpVar=$gPlayBackSlider' )
			cmds.timeControl(gPlayBackSlider, edit = True, sound = sndNode)
			mel.eval('setSoundDisplay %s 1;' %(sndNode))


	@classmethod
	def timeModeChangeCmd(*args):
		mode = cmds.radioButtonGrp(UI.widgets['timeSldrRadBtn'], q = True, select = True)
		if mode == 1:
			cmds.rowColumnLayout(UI.widgets['timeSldrNrmRowColLo'], e = True, visible = True)
			cmds.rowColumnLayout(UI.widgets['timeSldrTimeRowColLo'], e = True, visible = False)
			cmds.rowColumnLayout(UI.widgets['timeSldrSoundRowColLo'], e = True, visible = False)
		if mode == 2:
			cmds.rowColumnLayout(UI.widgets['timeSldrNrmRowColLo'], e = True, visible = False)
			cmds.rowColumnLayout(UI.widgets['timeSldrTimeRowColLo'], e = True, visible = True)
			cmds.rowColumnLayout(UI.widgets['timeSldrSoundRowColLo'], e = True, visible = False)
		if mode == 3:
			cmds.rowColumnLayout(UI.widgets['timeSldrNrmRowColLo'], e = True, visible = False)
			cmds.rowColumnLayout(UI.widgets['timeSldrTimeRowColLo'], e = True, visible = False)
			cmds.rowColumnLayout(UI.widgets['timeSldrSoundRowColLo'], e = True, visible = True)


	@classmethod
	def getSndPath(*args):
		sndList = cmds.ls(type = 'audio')
		if sndList:
			sndPath = cmds.sound(sndList[0], q = True, file = True)
			startDir = os.path.dirname(sndPath)
		else:
			curScenePath = cmds.file(q = True, sceneName = True)
			startDir = os.path.dirname(curScenePath)
		sndPath = cmds.fileDialog2(fileMode = 1, caption = 'Import Sound', startingDirectory = startDir)[0]
		cmds.textField(UI.widgets['timeSldrSoundPathTxtFld'], e = True, text = sndPath)

	
	@classmethod
	def getImgPath(*args):
		curScenePath = cmds.file(q = True, sceneName = True)
		startDir = os.path.dirname(curScenePath)
		imgPath = cmds.fileDialog2(fileMode = 1, caption = 'Image Plane Path', startingDirectory = startDir)[0]
		cmds.textFieldButtonGrp(UI.widgets['imgPlaneTxtFldBtnGrp'], e = True, text = imgPath)


	@classmethod
	def setShotCam(*args):
		camName = cmds.textField(UI.widgets['camTxtFld'], q = True, text = True)
		startFrame = int(cmds.playbackOptions(q = True, minTime = True))
		endFrame = int(cmds.playbackOptions(q = True, maxTime = True))
		camTypeOpt = cmds.optionMenu(UI.widgets['camTypeOptMenu'], q = True, v = True)

		if camTypeOpt == 'Camera':
			cam = mel.eval('camera; cameraMakeNode 1 "";')
		elif camTypeOpt == 'Camera and Aim':
			cam = mel.eval('camera; cameraMakeNode 2 "";')
		elif camTypeOpt == 'Camera, Aim and Up':
			cam = mel.eval('camera; cameraMakeNode 3 "";')
		#camShp = cmds.rename(camShape, '{0}_{1}_{2}'.format(camName, startFrame, endFrame))
		camShp = cmds.rename(cam, '{0}'.format(camName))

		# set focal length
		focalLengthOpt = int(cmds.optionMenu(UI.widgets['camFLOptMenu'], q = True, v = True))
		cmds.setAttr('{0}.focalLength'.format(camShp), focalLengthOpt)

		# Set near clip plane and far clip plane
		cmds.setAttr('%s.nearClipPlane' %camShp, 1)
		cmds.setAttr('%s.farClipPlane' %camShp, 3000)

		# display camera resolusion
		cmds.setAttr('%s.displayResolution' %(camShp), True)
		cmds.setAttr('%s.overscan' %(camShp), 1.1)
		cmds.setAttr('%s.backgroundColor'%(camShp), 0.5, 0.5, 0.5, type = 'double3')
		cmds.setAttr('%s.displayGateMaskColor' %(camShp), 0, 0, 0, type = 'double3')
		cmds.setAttr('%s.displayGateMaskOpacity' %(camShp), 1)

		# set render setting
		resOpt = cmds.optionMenu(UI.widgets['camResOptMenu'], q = True, v = True)
		if resOpt == '1024 x 768':
			cmds.setAttr('defaultResolution.width', 1024)
			cmds.setAttr('defaultResolution.height', 768)
			cmds.setAttr('defaultResolution.deviceAspectRatio', 1.333)
			cmds.setAttr('defaultResolution.pixelAspect', 1.000)
		if resOpt == '1024 x 1280':
			cmds.setAttr('defaultResolution.width', 1024)
			cmds.setAttr('defaultResolution.height', 1280)
			cmds.setAttr('defaultResolution.deviceAspectRatio', 0.8)
			cmds.setAttr('defaultResolution.pixelAspect', 1.000)
		if resOpt == '1280 x 720':
			cmds.setAttr('defaultResolution.width', 1280)
			cmds.setAttr('defaultResolution.height', 720)
			cmds.setAttr('defaultResolution.deviceAspectRatio', 1.777)
			cmds.setAttr('defaultResolution.pixelAspect', 1.000)
		if resOpt == '1920 x 1080':
			cmds.setAttr('defaultResolution.width', 1920)
			cmds.setAttr('defaultResolution.height', 1080)
			cmds.setAttr('defaultResolution.deviceAspectRatio', 1.777)
			cmds.setAttr('defaultResolution.pixelAspect', 1.000)