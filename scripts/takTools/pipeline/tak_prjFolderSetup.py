'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description: This script set up project folders.

Usage:
'''

# import modules
import maya.cmds as cmds
import os, re

# UI part
def UI():
	winName = 'pfWin'
	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)
	cmds.window(winName, title = 'Project Folder Setup UI')

	cmds.columnLayout(adj = True)
	cmds.textFieldButtonGrp('prjPathTxtFldBtnGrp', label = 'Project Path: ', buttonLabel = '...', bc = getPath)
	cmds.textFieldGrp('prjFldTxtFldGrp', label = 'Project Name:')
	cmds.textFieldGrp('subFldsTxtFldGrp', label = 'Sub Folders: ', text = 'AE, images, movies, references, scenes')
	cmds.button('mkBtn', label = 'Make!', c = main)

	cmds.window(winName, e = True, w = 300, h = 100)
	cmds.showWindow(winName)


# main function
def main(*args):
	projectPath = cmds.textFieldButtonGrp('prjPathTxtFldBtnGrp', q = True, text = True)
	projectFolderName = cmds.textFieldGrp('prjFldTxtFldGrp', q = True, text = True)
	subFolders = cmds.textFieldGrp('subFldsTxtFldGrp', q = True, text = True)
	subFolderList = re.findall(r'\w+', subFolders)

	# make project folder
	os.mkdir('%s\/%s' %(projectPath, projectFolderName))

	# make subFolders
	for subFolder in subFolderList:
		os.mkdir('%s\/%s\/%s' %(projectPath, projectFolderName, subFolder))

def getPath(*args):
	prjPath = cmds.fileDialog2(fileMode = 3)
	if prjPath:
		cmds.textFieldButtonGrp('prjPathTxtFldBtnGrp', e = True, text = prjPath[0])

# set current to default

# load default setting

# save current setting

# load setting