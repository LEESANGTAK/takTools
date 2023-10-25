'''
Author: TAK
Website: https://ta-note.com
Updated: 12/30/2021

Description:
This script edit .ma file without opening in maya app.

Usage:
import tak_editMayaAsciiFile
reload(tak_editMayaAsciiFile)
tak_editMayaAsciiFile.ui()
'''


import maya.cmds as cmds
import os
import logging
import shutil

logger = logging.getLogger('EditMayaASCII')
logger.setLevel(logging.WARNING)


def ui():
    winName = 'editMaWin'
    if cmds.window(winName, exists = True):
        cmds.deleteUI(winName)

    cmds.window(winName, title = 'Edit Maya ASCII', mnb = False, mxb = False)

    cmds.columnLayout('mainColLo', adj = True, rowSpacing = 5)

    cmds.rowColumnLayout('fileLsRowColLo', numberOfColumns = 2, columnWidth = [(1, 500)])
    cmds.textScrollList('fileLsTxtScrLs', allowMultiSelection = True)
    cmds.columnLayout('fileLsBtnColLo', adj = True, rowSpacing = 5)
    cmds.button(label = '+', c = addFileToLs)
    cmds.button(label = '-', c = rmvFileFromLs)
    cmds.setParent('mainColLo')

    cmds.textFieldGrp('srchTxtFldGrp', label='Search String:')
    cmds.textFieldGrp('rplcTxtFldGrp', label='Replace String:')
    cmds.button(label = 'Apply', c = main, h = 50)

    cmds.window(winName, e = True, w = 300, h = 100)
    cmds.showWindow(winName)


def main(*args):
    filePathToEditLs = cmds.textScrollList('fileLsTxtScrLs', q = True, allItems = True)
    searchStr = cmds.textFieldGrp('srchTxtFldGrp', q=True, text=True)
    replaceStr = cmds.textFieldGrp('rplcTxtFldGrp', q=True, text=True)

    # Create progress bar window
    if cmds.window('progWin', exists = True): cmds.deleteUI('progWin')
    cmds.window('progWin', title = 'Processing...')
    cmds.columnLayout(adj=True)
    cmds.text('progText', l='')
    cmds.progressBar('progBar', minValue = 0, maxValue = len(filePathToEditLs), width = 300, isMainProgressBar = True, beginProgress = True, isInterruptable = True)
    cmds.window('progWin', e = True, w = 300, h = 10)
    cmds.showWindow('progWin')

    unchangedFiles = []
    isUnicode = False
    for filePath in filePathToEditLs:
        # Edit progress bar
        if cmds.progressBar('progBar', q = True, isCancelled = True):
            break
        fileName = os.path.basename(filePath)
        cmds.text('progText', e=True, label=fileName)
        cmds.progressBar('progBar', e = True, step = 1)

        # Make backup file
        backupFilePath = filePath.replace(fileName, 'old_{0}'.format(fileName))
        if not os.path.exists(backupFilePath):
            shutil.copyfile(filePath, backupFilePath)

        # Read file contents
        with open(filePath, 'r') as f:
            contents = f.read()

        # Edit file contents
        try:
            newContents = contents.replace(searchStr, replaceStr)
        except UnicodeDecodeError:
            contents = unicode(contents, 'cp949')
            newContents = contents.replace(searchStr, replaceStr)
            isUnicode = True

        # If file is not modified print warning and continue to next file
        if hash(contents) == hash(newContents):
            logger.warning('Not found search string. {0} is unchanged.'.format(filePath))
            unchangedFiles.append(filePath)
            continue

        # If file is modified correctly write file with new contents
        with open(filePath, 'w') as f:
            if isUnicode:
                f.write(newContents.encode('cp949'))
                isUnicode = False
            else:
                f.write(newContents)

    cmds.progressBar('progBar', e = True, endProgress = True)
    cmds.deleteUI('progWin')

    # Remain only unchanged files in the text scroll list ui
    cmds.textScrollList('fileLsTxtScrLs', e=True, removeAll=True)
    for file in unchangedFiles:
        cmds.textScrollList('fileLsTxtScrLs', e=True, append=file)


def addFileToLs(*args):
    curScenePath = cmds.file(q = True, sceneName = True)
    curWorkDir = os.path.dirname(curScenePath)

    filePath = cmds.fileDialog2(fileMode = 4, caption = 'Load', fileFilter = 'Maya ASCII (*.ma)', startingDirectory = curWorkDir)
    cmds.textScrollList('fileLsTxtScrLs', e = True, append = filePath)


def rmvFileFromLs(*args):
    selItemLs = cmds.textScrollList('fileLsTxtScrLs', q = True, selectItem = True)

    cmds.textScrollList('fileLsTxtScrLs', e = True, removeItem = selItemLs)