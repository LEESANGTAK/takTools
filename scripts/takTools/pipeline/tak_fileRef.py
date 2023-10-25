'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 2015.08.13

Description:
Referencing while open maya is take too long time.
This script edit a ".ma" file and open it.
So You can save time.

Usage:
import tak_fileRef
reload(tak_fileRef)
tak_fileRef.UI()
'''



# Import modules
import maya.cmds as cmds
from functools import partial
import re



# UI Class
class UI(object):
	# Define attributes
	winName = 'fileRefWin'
	widgets = {}

	@classmethod
	def __init__(cls):
		# Check if current scene saved
		curScenePath = cmds.file(q = True, sceneName = True)
		if not curScenePath:
			cmds.confirmDialog(title = 'Error', message = 'Please save current scene as ".ma" file before run this script.')
			return

		# Check if window is existing
		if cmds.window(cls.winName, exists = True):
			cmds.deleteUI(cls.winName)

		# Show ui
		cls.ui()

		# If any reference already loaded in current scene, add it to ui
		refNodeList = cmds.ls(references = True)
		for refNode in refNodeList:
			# Skip for did not loaded references or double referencing
			if not cmds.referenceQuery(refNode, il = True) or ':' in refNode:
				continue
			refNodeNameSpace = cmds.referenceQuery(refNode, namespace = True, shortName = True)
			refNodeFilePath = cmds.referenceQuery(refNode, filename = True)
			cls.addRefInfo(nameSpace = refNodeNameSpace, filePath = refNodeFilePath)


	@classmethod
	def ui(cls):
		'''
		Build and show main ui.
		'''

		cmds.window(cls.winName, title = 'File Referencing Tool')

		cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)

		cls.widgets['lablRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 3, columnSpacing = [(1, 20), (2, 150), (3, 150)], p = cls.widgets['mainColLo'])
		cmds.text(label = 'Name Space', p = cls.widgets['lablRowColLo'])
		cmds.text(label = 'File Path', p = cls.widgets['lablRowColLo'])
		cmds.button(label = 'Add Item', c = partial(cls.addRefInfo, '', ''), p = cls.widgets['lablRowColLo'])

		cmds.separator(h = 5, p = cls.widgets['mainColLo'])

		cls.widgets['refInfoColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['mainColLo'])

		cmds.separator(h = 10, style = 'none', p = cls.widgets['mainColLo'])

		cmds.button(label = 'Load', h = 50, c = cls.loadRef, p = cls.widgets['mainColLo'])

		cmds.window(cls.winName, e = True, w = 300, h = 100)
		cmds.showWindow(cls.winName)


	@staticmethod
	def addRefInfo(nameSpace, filePath, *args):
		'''
		Add reference ui object to main ui with reference information.
		'''

		refInfoObj = refInfo()
		refInfoObj.ui(nameSpace, filePath)


	@classmethod
	def loadRef(cls, *args):
		'''
		Main method.
		Modify reference information of current scene file and open it.
		'''

		# Read file
		curScenePath = cmds.file(q = True, sceneName = True)
		fR = open(curScenePath, 'r')
		contents = fR.read()
		fR.close()

		# Get the information of references in file contents
		refInfoBlock = re.search(r'//Codeset: 949\n(.*?)requires', contents, re.DOTALL).group(1)
		# Check if file has no reference
		if not refInfoBlock:
			refInfoBlock = '//Codeset: 949\n'

		# Construct codes with user input informations
		refInfoToLoad = cls.codesToLoad(refInfoBlock)

		# Replace reference information code block in file with new reference information
		contents = re.sub(refInfoBlock, refInfoToLoad, unicode(contents, 'cp949'))

		# Write file
		fW = open(curScenePath, 'w')
		fW.write(contents.encode('cp949'))
		fW.close()

		# Open file
		cmds.file(curScenePath, open = True, force = True)

		# Delete ui
		cmds.deleteUI(cls.winName)


	@classmethod
	def codesToLoad(cls, refInfoBlock):
		'''
		Construct code block to load.
		'''

		refInfoCodesToLoad = ''
		defaultNameSpace = 'Asset_000'

		if refInfoBlock == '//Codeset: 949\n':
			refInfoCodesToLoad = refInfoBlock

		# Get reference inofrmation ui objects
		refInfoUiObjs = cmds.columnLayout(cls.widgets['refInfoColLo'], q = True, childArray = True)

		for refInfoUiObj in refInfoUiObjs:
			# Get child widgets of refInfoUiObj
			refInfoWidgets = cmds.rowColumnLayout(refInfoUiObj, q = True, childArray = True)

			# Get namespace
			refInfoObjNameSpace = cmds.textField(refInfoWidgets[0], q = True, text = True)
			# If already exists default namespace in the scene, replace defaultNameSpace to exists default namespace
			if 'Asset_' in refInfoObjNameSpace:
				defaultNameSpace = refInfoObjNameSpace
			# If user did not input namespace, use default namespace
			if not refInfoObjNameSpace:
				# Increase count number
				count = re.search(r'\d*\d', defaultNameSpace).group()
				padding = len(count)
				nextCount = str((int(count) + 1)).zfill(padding)
				defaultNameSpace = re.sub(count, nextCount, defaultNameSpace)

				# Replace refInfoObjNameSpace to defaultNameSpace
				refInfoObjNameSpace = defaultNameSpace

			# Get file path to referencing
			refInfoObjfilePath = cmds.textField(refInfoWidgets[2], q = True, text = True)

			# Construct codes
			refInfoCodesToLoad += 'file -r -ns "%s" -dr 1 -rfn "%sRN" "%s";\n' %(refInfoObjNameSpace, refInfoObjNameSpace, refInfoObjfilePath)

		return refInfoCodesToLoad





class refInfo(object):
	widgets = {}

	def ui(self, nameSpace = '', filePath = ''):
		'''
		ui to get input for reference informations.
		'''

		self.widgets['mainRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 5, columnWidth = [(1, 100), (3, 300)], p = UI.widgets['refInfoColLo'])
		self.widgets['nameSpceTxtFld'] = cmds.textField(text = nameSpace, p = self.widgets['mainRowColLo'])
		cmds.text(label = ' : ', p = self.widgets['mainRowColLo'])
		self.widgets['filePathTxtFld'] = cmds.textField(text = filePath, p = self.widgets['mainRowColLo'])
		cmds.button(label = '...', w = 30, c = partial(self.getFilePath, self.widgets['filePathTxtFld']), p = self.widgets['mainRowColLo'])
		cmds.button(label = '-', w = 30, c = partial(self.rmvRefInfoObj, self.widgets['mainRowColLo']), p = self.widgets['mainRowColLo'])


	def getFilePath(self, widget, *args):
		'''
		Fill the file path text field.
		'''

		path = cmds.fileDialog2(fileMode = 1, caption = 'Select a File to Referencing')
		if path:
			cmds.textField(widget, e = True, text = path[0])


	def rmvRefInfoObj(self, widget, *args):
		'''
		Remove reference infomation objects ui.
		'''

		cmds.deleteUI(widget)