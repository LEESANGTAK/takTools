# coding: euc-kr

'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
You can batch playblast with this script.
Upload files on file list section and set playblast options.

Usage:
import tak_batchPB
reload(tak_batchPB)
tak_batchPB.batchPB()
'''

import maya.cmds as cmds
from functools import partial
import os, re

class batchPB():

	@classmethod
	def __init__(cls):
		cls.winName = 'batchPBWin'
		if cmds.window(cls.winName, exists = True):
			cmds.deleteUI(cls.winName)
		cls.ui()

	@classmethod
	def ui(cls):
		cmds.window(cls.winName, title = 'Batch Playblast')

		cmds.columnLayout('mainColLo', p = cls.winName, adj = True)

		cmds.rowColumnLayout('mainRowColLo', p = 'mainColLo', numberOfColumns = 2, columnSpacing = [(2, 5)], columnWidth = [(1, 430), (2, 430)])

		cmds.columnLayout('srcFileColLo', adj = True)

		cmds.textFieldButtonGrp('srcFldrTxtFldBtnGrp', p = 'srcFileColLo', label = 'Source Folder Path: ', buttonLabel = '...', bc = partial(cls.loadPath, 'srcFldrTxtFldBtnGrp'))
		cmds.textScrollList('srcFileTxtScrLs', p = 'srcFileColLo', append = 'Files to Playblast...', allowMultiSelection = True, h = 300)
		cmds.popupMenu('fileLsPopMenu', p = 'srcFileTxtScrLs')
		cmds.menuItem(label = 'Remove Selected', c = cls.rmvSelSrcFile)

		cmds.columnLayout('optColLo', p = 'mainRowColLo', adj = True)

		cmds.textFieldButtonGrp('trgFldrTxtFldBtnGrp', p = 'optColLo', label = 'Target Folder Path: ', buttonLabel = '...', bc = partial(cls.loadPath, 'trgFldrTxtFldBtnGrp'))

		cmds.separator(p = 'optColLo', style = 'in', h = 10)

		cmds.optionMenuGrp('formatOptMenuGrp', p = 'optColLo', label = 'Format: ')
		cmds.menuItem(label = 'avi')
		# cmds.menuItem(label = 'mov')
		# cmds.menuItem(label = 'mp4')
		cmds.optionMenuGrp('encodingOptMenuGrp', p = 'optColLo', label = 'Encoding: ')
		cmds.menuItem(label = 'IYUV �ڵ�')
		cmds.menuItem(label = 'MS-CRAM')
		cmds.menuItem(label = 'none')
		cmds.intSliderGrp('qualityintSldrGrp', p = 'optColLo', label = 'Quality: ', field = True, v = 100)

		cmds.separator(p = 'optColLo', style = 'in', h = 10)

		cmds.optionMenuGrp('sizeOptMenuGrp', p = 'optColLo', label = 'Display Size: ', cc = cls.dpSzCC)
		cmds.menuItem(label = 'From Render Settings')
		cmds.menuItem(label = 'Custom')
		cmds.menuItem(label = 'From Window')
		cmds.rowColumnLayout('customSizeRowColLo', p = 'optColLo', numberOfColumns = 2, columnSpacing = [(1, 140)], columnWidth = [(1, 70), (2, 70)])
		cmds.textField('cstSzWTxtFld', p = 'customSizeRowColLo', enable = False)
		cmds.textField('cstSzHTxtFld', p = 'customSizeRowColLo', enable = False)
		cmds.floatSliderGrp('scalefloatSldrGrp', p = 'optColLo', label = 'Scale: ', field = True, min = 0, max = 1, precision = 2, v = 0.5)

		cmds.separator(p = 'optColLo', style = 'in', h = 10)

		cmds.textFieldGrp('camNameConvTxtFldGrp', p = 'optColLo', label = 'Shot Camera Name: ')
		# cmds.textFieldGrp('sceneNameConvTxtFldGrp', p = 'optColLo', label = 'Scene Naming Convention: ')
		# cmds.textFieldGrp('sndNameConvTxtFldGrp', p = 'optColLo', label = 'Sound Naming Convention: ')
		# cmds.checkBoxGrp('resolutionChkBoxGrp', p = 'optColLo', label = 'Resolution Gate: ')

		cmds.button(p = 'mainColLo', label = 'Close all floating panels(Script Editor, UV Textrue Editor...) and show necessary HUD(Current Frame, Camera Names...) then click this button.', h = 30, c = cls.batchPB)

		cmds.window(cls.winName, e = True, w = 300, h = 300)
		cmds.showWindow(cls.winName)


	@classmethod
	def loadPath(cls, wdgName, *args):
		'''
		Fill folder path textFieldGrp.
		'''

		fldrPath = cmds.fileDialog2(dialogStyle = 1, fileMode = 2)[0]
		cmds.textFieldButtonGrp(wdgName, e = True, text = fldrPath)

		if wdgName == 'srcFldrTxtFldBtnGrp':
			cls.fillSrcFileTxtScrLs(fldrPath)


	@classmethod
	def fillSrcFileTxtScrLs(cls, path, *args):
		'''
		Load maya scene files in source folder path.
		'''

		if cmds.textScrollList('srcFileTxtScrLs', q = True, allItems = True):
			cmds.textScrollList('srcFileTxtScrLs', e = True, removeAll = True)

		allFiles = os.listdir(path)
		for eachFile in allFiles:
			if '.ma' in eachFile or '.mb' in eachFile:
				cmds.textScrollList('srcFileTxtScrLs', e = True, append = eachFile)


	@classmethod
	def rmvSelSrcFile(cls, *args):
		'''
		Remove selected items in source file text scroll list.
		'''

		selSrcFiles = cmds.textScrollList('srcFileTxtScrLs', q = True, selectItem = True)
		cmds.textScrollList('srcFileTxtScrLs', e = True, removeItem = selSrcFiles)


	@classmethod
	def batchPB(cls, *args):
		'''
		Playblast with ui options.
		'''

		# Get options form ui.
		srcDir = cmds.textFieldButtonGrp('srcFldrTxtFldBtnGrp', q = True, text = True)
		srcFileLs = cmds.textScrollList('srcFileTxtScrLs', q = True, allItems = True)
		trgDir = cmds.textFieldButtonGrp('trgFldrTxtFldBtnGrp', q = True, text = True)

		formatOpt = cmds.optionMenuGrp('formatOptMenuGrp', q = True, v = True)
		encodingOpt = cmds.optionMenuGrp('encodingOptMenuGrp', q = True, v = True)
		qualityOpt = cmds.intSliderGrp('qualityintSldrGrp', q = True, v = True)

		sizeOpt = cmds.optionMenuGrp('sizeOptMenuGrp', q = True, v = True)
		scaleOpt = cmds.floatSliderGrp('scalefloatSldrGrp', q = True, v = True) * 100

		camNC = cmds.textFieldGrp('camNameConvTxtFldGrp', q = True, text = True)
		# sceneNC = cmds.textFieldGrp('sceneNameConvTxtFldGrp', q = True, text = True)
		# sndNC = cmds.textFieldGrp('sndNameConvTxtFldGrp', q = True, text = True)

		# Playblast for source files.
		for srcfile in srcFileLs:
			# Open file.
			srcFilePath = srcDir + '\\' + srcfile
			cmds.file(srcFilePath, open = True, force = True)

			# Set up viewport.
			# Figure out shot camera.
			shotCam = ''
			allCam = cmds.ls(type = 'camera')
			for cam in allCam:
				if camNC in cam:
					shotCam = cam
					break
			curPanel = cmds.getPanel(withFocus = True)
			cmds.lookThru(curPanel, shotCam)
			cmds.setAttr("%s.displayResolution" %shotCam, 0)
			cmds.setAttr("%s.overscan" %shotCam, 1)
			cmds.modelEditor(curPanel, e = True, allObjects = False)
			cmds.modelEditor(curPanel, e = True, polymeshes = True)
			cmds.modelEditor(curPanel, e = True, displayAppearance = 'smoothShaded', displayTextures = True, displayLights = 'default')

			# Define size option.
			if sizeOpt == 'Custom':
				sizeW = int(cmds.textField('cstSzWTxtFld', q = True , text = True))
				sizeH = int(cmds.textField('cstSzHTxtFld', q = True, text = True))
			elif sizeOpt == 'From Window':
				sizeW = 0
				sizeH = 0
			elif sizeOpt == 'From Render Settings':
				sizeW = cmds.getAttr('defaultResolution.width')
				sizeH = cmds.getAttr('defaultResolution.height')

			# Figure out playblast file path.
			sceneName = cmds.file(q = True, sceneName = True, shortName = True)
			splitSceneName = os.path.splitext(sceneName)
			ext = splitSceneName[1]
			pbFileName = re.sub(ext, '.'+formatOpt, sceneName)
			pbFilePath = trgDir + '\\' + pbFileName

			# # Find shot sound file.
			# basename = splitSceneName[0]
			# sceneNum = basename.split(sceneNC)[-1]

			# sndLs = cmds.ls(type = 'audio')
			# shotSound = ''
			# for snd in sndLs:
			# 	soundNum = snd.split(sndNC)[-1]
			# 	if sceneNum == soundNum:
			# 		shotSound = snd
			# 		break

			# print shotSound

			# Playblast with options.
			cmds.playblast(fo = True, format = formatOpt, filename = pbFilePath, sequenceTime = 0, clearCache = True, viewer = False, showOrnaments = True, framePadding = 4, percent = scaleOpt, compression = encodingOpt, quality = qualityOpt, widthHeight = [sizeW, sizeH])


	@classmethod
	def dpSzCC(cls, *args):
		'''
		Display size option menu change command.
		'''

		dpSzOptState = cmds.optionMenuGrp('sizeOptMenuGrp', q = True, v = True)

		if dpSzOptState in ['From Render Settings', 'From Window']:
			cmds.textField('cstSzWTxtFld', e = True, enable = False)
			cmds.textField('cstSzHTxtFld', e = True, enable = False)
		elif dpSzOptState == 'Custom':
			cmds.textField('cstSzWTxtFld', e = True, enable = True)
			cmds.textField('cstSzHTxtFld', e = True, enable = True)
