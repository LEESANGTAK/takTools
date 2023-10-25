#-*- coding: euc-kr -*-

'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script will update the current references to the latest reference version.


Usage:
import tak_updateRef
reload(tak_updateRef)
tak_updateRef(filePath)
FilePath parameter should be full file path what you want to update.

Update Note:
06/19/2014 v1.0
1st release.

07/02/2014 v1.1
Create ui.

'''

import os, re
import maya.cmds as cmds
from functools import partial

# modify file contents depend on options in the ui
def updateAsset(assetListObjs, contents, filePath, *args):
    # modify contents depend on options in the ui
    for assetListObj in assetListObjs:
        chkBoxOpt = cmds.checkBox(assetListObj.chkBox, q = True, v = True)
    if chkBoxOpt:
        releaseOpt = cmds.optionMenu(assetListObj.releaseOptMenu, q = True, v = True)
        lodOpt = cmds.optionMenu(assetListObj.lodOptMenu, q = True, v = True)
        # substitute current release version to the selected release version
        selectedReferencePath = re.sub(r'r\d\d\d', releaseOpt, assetListObj.currentReferencePath)
        # if lod exists, substitute current lod to the selected lod
        if lodOpt:
            selectedReferencePath = re.sub(r'lod\d\d', lodOpt, selectedReferencePath)
            # replace current reference path to the selected reference path
            contents = contents.replace(assetListObj.currentReferencePath, str(selectedReferencePath))

    # set updated file path
    updatedFilePath = filePath.replace('.ma', '_refUpdated.ma')

    # save as updated file
    fW = open(updatedFilePath, 'w')
    fW.write(contents)
    fW.close()

    # delete the window and open updated file
    cmds.deleteUI('uaWin')
    cmds.file(updatedFilePath, open = True, force = True, prompt = False)

# if user push the cancel button, open the original file
def openOrigFile(filePath, *args):
    cmds.deleteUI('uaWin')
    cmds.file(filePath, open = True, force = True, prompt = False)

# this function allow to update reference to the latest version when open in local directory
def localOpen():
    curScenePath = cmds.file(q = True, sceneName = True)
    curWorkDir = os.path.dirname(curScenePath)
    filePath = cmds.fileDialog2(fileMode = 1, caption = 'Open with Reference Update', startingDirectory = curWorkDir)[0]
    updateRef(filePath)

# main function #
def updateRef(filePath):
    # read the contents from the given file path
    fR = open(filePath, 'r')
    contents = fR.read()
    fR.close()

    # extract referenceDepthInfo of assets from the contents
    refInfos = re.findall(r'.*-rdi.*Asset/.*', contents)

    # remove develop in refInfos
    while 'develop' in str(refInfos):
        for refInfo in refInfos:
            if 'develop' in refInfo:
                refInfos.remove(refInfo)

    # check if exists latest release version for assets
    if chkLatestRelease(refInfos):
        # if latest release version exists, show update asset ui
        updateAssetUI(refInfos, contents, filePath)
    else:
        # else all references are latest version, open original file
        updateAssetUI(refInfos, contents, filePath)
        #cmds.file(filePath, open = True, force = True, prompt = False)

# this function will check if exists latest release version
def chkLatestRelease(refInfos):
    for refInfo in refInfos:
        # in case referencing develop, return false
        if 'develop' in refInfo:
            continue

    # release directory
    releaseDir = re.search(r'\w:/.*/release', refInfo).group()

    # current release version
    currentRelease = re.search(r'r\d\d\d', refInfo).group()

    # get latest release version
    releaseList = os.listdir(releaseDir)
    latestRelease = max(releaseList)

    if currentRelease != latestRelease:
        return True
    return False

# main ui
def updateAssetUI(refInfos, contents, filePath):
    if cmds.window('uaWin', exists = True):
        cmds.deleteUI('uaWin')
    cmds.window('uaWin', title = 'Update Asset UI')

    # main formLayout
    cmds.formLayout('mainForm', nd = 100)

    # main tabLayout
    cmds.tabLayout('mainTab', tv = False)
    cmds.tabLayout('subTab', tv = False, scrollable = True, childResizable = True)

    # main columnLayout
    cmds.columnLayout('mainColLay', adj = True)

    cmds.text(label = '������Ʈ �� ������ üũ�ϰ� Update Selected Asset ��ư�� ���� �ּ���.\n������Ʈ ���� �������� Do not update ��ư�� ��������.\n���� ���� ���� �Ϸ��� X ��ư�� ���� â�� �ݾ� �ּ���.')

    cmds.separator(h = 10, style = 'in')

    # rowColumnLayout for items
    cmds.rowColumnLayout('itemRCLay', numberOfColumns = 6,
    columnWidth = [(1, 100), (2, 100), (3, 100), (4, 130),(5, 130),(6, 50)],
    columnAttach = [(1, 'left', 10), (6, 'right', 5)])

    cmds.text('assetText', label = 'Asset List')
    cmds.text('curVerText', label = 'Current Version')
    cmds.text('latestVerText', label = 'Latest Version')
    cmds.text('releaseText', label = 'Release History')
    cmds.text('lodText', label = 'LOD List')
    cmds.text('infoText', label = 'Info')

    # set parent itemRCLay to the mainColLay
    cmds.setParent('mainColLay')

    cmds.separator(h = 10, style = 'in')

    # populate asset list
    assetListObjs = populateAssetList(refInfos)

    # set parent main columnLayout to the subTab
    cmds.setParent('subTab')

    # parent main tabLayout to the main formLayout
    cmds.setParent('mainForm')

    # apply and cancel button
    cmds.button('appButton', label = 'Update Selected Asset', c = partial(updateAsset, assetListObjs, contents, filePath))
    cmds.button('cancelButton', label = 'Do Not Update', c = partial(openOrigFile, filePath))

    # arrange main formLayout
    cmds.formLayout('mainForm', e = True,
                    attachForm = [('mainTab', 'top', 5), ('mainTab', 'left', 5), ('mainTab', 'right', 5), ('appButton', 'left', 5), ('appButton', 'bottom', 5), ('cancelButton', 'right', 5), ('cancelButton', 'bottom', 5)],
                    attachPosition = [('appButton', 'right', 2.5, 50), ('cancelButton', 'left', 2.5, 50)],
                    attachControl = [('mainTab', 'bottom', 5, 'appButton')]
                    )

    cmds.window('uaWin', e = True, w = 660, h = 300, sizeable = True)
    cmds.showWindow('uaWin')

# create asset list objcts
def populateAssetList(refInfos):
    assetListObjs = []
    for refInfo in refInfos:
        # asset name
        assetName = re.search(r'(.*Asset/.*?/)(.*?)(/.*)', refInfo).group(2)
        # create asset list object
        assetName = AssetList(refInfo)
        # add to the win
        assetName.addToWin()
        # append to the assetListObjs variable
        assetListObjs.append(assetName)
    return assetListObjs

# This class for create asset list objects.
class AssetList:
    currentLod = None
    # set initial asset list data
    def __init__(self, refInfo):
        # current reference path
        self.currentReferencePath = re.search(r'\w:/.*.ma', refInfo).group()

        # asset name
        self.assetName = re.search(r'(.*Asset/.*?/)(.*?)(/.*)', refInfo).group(2)

        # release directory
        self.releaseDir = re.search(r'\w:/.*/release/', refInfo).group()

        # current release version
        self.currentReleaseVer = re.search(r'r\d\d\d', refInfo).group()

        # release list
        self.releaseList = os.listdir(self.releaseDir)

        # get latest release version
        self.latestReleaseVer = max(self.releaseList)

        # current lod status
        match = re.search(r'lod\d\d', refInfo)
        if match != None:
            self.currentLod = match.group()

    # add the asset list to the main ui
    def addToWin(self):
        # create asset list ui and add to the window
        cmds.separator(h = 5, style = 'none')

        self.RCLay = cmds.rowColumnLayout(numberOfColumns = 6,
        columnWidth = [(1, 100), (2, 100), (3, 100), (4, 130),(5, 130),(6, 50)],
        columnAttach = [(1, 'left', 0), (4, 'both', 10), (5, 'both', 10), (6, 'right', 0)])

        self.chkBox = cmds.checkBox(label = self.assetName)
        self.curVerText = cmds.text(label = self.currentReleaseVer)
        self.latestVerText = cmds.text(label = self.latestReleaseVer)
        self.releaseOptMenu = cmds.optionMenu()

        # populate release option menu
        self.populateReleaseOptMenu()

        self.lodOptMenu = cmds.optionMenu()
        self.infoButton = cmds.button(label = 'Info', c = self.releaseInfo)

        # callbacks
        cmds.optionMenu(self.releaseOptMenu, e = True, cc = self.populateLodOptMenu)

        # populate initial lod option menu
        self.populateLodOptMenu()

        # if not same current version and lastest version, fill color to the row column layout
        if self.currentReleaseVer != self.latestReleaseVer:
            cmds.rowColumnLayout(self.RCLay, e = True, bgc = [0.35, 0.35, 0.35])
            cmds.checkBox(self.chkBox, e = True, v = True)

        # if not exists latest version, disable the check box, release option menu and lod option menu and info
        if self.currentReleaseVer == self.latestReleaseVer:
            '''cmds.checkBox(self.chkBox, e = True, enable = False)
            cmds.optionMenu(self.releaseOptMenu, e = True, enable = False)
            cmds.optionMenu(self.lodOptMenu, e = True, enable = False)'''
            cmds.checkBox(self.chkBox, e = True, v = True)

        # set parent itemRCLay to the mainColLay
        cmds.setParent('mainColLay')

    def populateReleaseOptMenu(self):
        for release in self.releaseList:
            cmds.menuItem(label = release, parent = self.releaseOptMenu)
        # set the option menu value to the latest release version
        cmds.optionMenu(self.releaseOptMenu, e = True, v = self.latestReleaseVer)

    def populateLodOptMenu(self, *args):
        # get release files
        selectedRelease = cmds.optionMenu(self.releaseOptMenu, q = True, v = True)
        releaseDir = self.releaseDir + selectedRelease + '/'
        releaseFiles = os.listdir(releaseDir)

        lodList = []
        # if release files contains lod extract lod list else if not exists lod then disable lodOptMenu
        for releaseFile in releaseFiles:
                match = re.search(r'lod\w\w', releaseFile)
                if match != None:
                    lodList.append(match.group())
        if not lodList:
            cmds.optionMenu(self.lodOptMenu, e = True, enable = False)

        # if already exists menu item in the lod list, delete menu items before populate lodOptMenu
        lodMenuItems = cmds.optionMenu(self.lodOptMenu, q = True, itemListLong = True)
        if lodMenuItems != None:
            for lodMenuItem in lodMenuItems:
                cmds.deleteUI(lodMenuItem)

        for lod in lodList:
            cmds.menuItem(label = lod, parent = self.lodOptMenu)

        # set lod option menu value to the current lod status
        if self.currentLod in lodList:
            cmds.optionMenu(self.lodOptMenu, e = True, v = self.currentLod)

    def releaseInfo(self, *args):
        print('comming soon...')
