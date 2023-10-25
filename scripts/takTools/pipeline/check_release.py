"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Created: 2019.04.16
Description:
    This script is for checking error that connect alembic file to render model.
"""

import os
import glob
import re
import pymel.core as pm

ASSET_DIR = r'\\192.168.0.239\B1delivery\ZRO_delivery\190104_ZRO_asset'
b2AttachAbcToModel_san_abcPathWidget = 'abcBrowseField'
b2PipelineShotFileLocationWidget = 'shtFileLocField'


def main():
    chkRelease = CheckRelease()
    chkRelease.win.show()

class CheckRelease(object):
    winName = 'checkReleaseWin'
    win = None
    relTxtFieldBtnGrp = None
    cacheTxtScrollLs = None
    relDir = None

    def __init__(self):
        self.buildUI()
        self.getFromPipeline()


    def buildUI(self):
        if pm.window(self.winName, q=True, exists=True): pm.deleteUI(self.winName)
        self.win = pm.window(self.winName, title='Check Release', mnb=False, mxb=False)
        pm.columnLayout(adj=True, columnAlign='left')
        self.relTxtFieldBtnGrp = pm.textFieldButtonGrp(label='Release Directory: ', buttonLabel='...', bc=self.relTxtFieldBtnGrpBtnCmd, cc=self.populateCacheTxtScrollLs)
        pm.popupMenu()
        pm.menuItem(label='Get From Pipeline UI', c=self.getFromPipeline)
        pm.text(label='Caches: ')
        self.cacheTxtScrollLs = pm.textScrollList(allowMultiSelection=True)
        pm.button(label='Run', c=self.connectAbcToModel)
        pm.window(self.winName, e=True, w=100, h=100)

    def connectAbcToModel(self, *args):
        selCaches = pm.textScrollList(self.cacheTxtScrollLs, q=True, si=True)
        if not selCaches: selCaches = pm.textScrollList(self.cacheTxtScrollLs, q=True, allItems=True)
        for cache in selCaches:
            assetType, assetName, numbering = CheckRelease.parseCacheFile(cache)
            namespace = '{}_{}'.format(assetName, numbering)
            if assetType == 'cam':
                frameInfo = re.search(r'(\d+_\d+)_r\d+.abc', cache).group(1)
                CheckRelease.setFrameRange(frameInfo)
                camRef = pm.createReference(os.path.join(self.relDir, cache), namespace=namespace)
                self.lookThroughShotCam(camRef)
            elif assetType == 'set':
                ref = CheckRelease.referencingMdl(assetType, assetName, namespace)
                pm.createReference(os.path.join(self.relDir, cache), type='editMA', namespace=namespace+'_edit', applyTo=ref.refNode)
            else:
                CheckRelease.referencingMdl(assetType, assetName, namespace)
                pm.select('{}:lod03_GRP'.format(namespace), r=True)
                pm.mel.eval('b2AttachAbcToModel_san();')
                pm.textFieldButtonGrp(b2AttachAbcToModel_san_abcPathWidget, e=True, text=os.path.join(self.relDir, cache))
                pm.mel.eval('b2AttachAbcToModelCallback_san();')

    def lookThroughShotCam(self, camRef):
        shotCam = [node for node in camRef.nodes() if isinstance(node, pm.nodetypes.Camera)][0]
        panels = pm.windows.getPanel(type='modelPanel')
        for panel in panels:
            if panel.getLabel() == 'Persp View':
                pm.mel.eval('lookThroughModelPanel {} {};'.format(str(shotCam), panel.getControl().split('|')[-1]))

    def getFromPipeline(self, *args):
        pm.newFile(f=True)
        if pm.textFieldButtonGrp(b2PipelineShotFileLocationWidget, q=True, exists=True):
            self.relDir = pm.textFieldButtonGrp(b2PipelineShotFileLocationWidget, q=True, text=True)
            pm.textFieldButtonGrp(self.relTxtFieldBtnGrp, e=True, text=self.relDir)
            self.populateCacheTxtScrollLs()

    @staticmethod
    def parseCacheFile(alembicFile):
        assetType = ''
        assetName = ''
        numbering = ''
        searchObj = re.search(r'master_(\D+?)_(.*?)_(\d+?)_r\d+\.\D+', alembicFile)
        if searchObj:
            assetType = searchObj.group(1)
            assetName = searchObj.group(2)
            numbering = searchObj.group(3)
        return assetType, assetName, numbering

    @staticmethod
    def referencingMdl(assetType, assetName, namespace):
        mdlDir = os.path.join(ASSET_DIR, assetType, assetName, assetName+'_mdl')
        mdlFiles = glob.glob('{}/*.mb'.format(mdlDir))
        if len(mdlFiles) > 1: pm.error('Number of model file exists more than one.')
        ref = pm.createReference(mdlFiles[0], namespace=namespace)
        return ref

    @staticmethod
    def setFrameRange(frameInfo):
        pm.currentUnit(time='ntsc')
        frames = frameInfo.split('_')
        pm.playbackOptions(minTime=frames[0])
        pm.playbackOptions(maxTime=frames[1])
        pm.currentTime(frames[0])

    def relTxtFieldBtnGrpBtnCmd(self, *args):
        self.relDir = pm.fileDialog2(dialogStyle=1, fileMode=3)[0]
        pm.textFieldButtonGrp(self.relTxtFieldBtnGrp, e=True, text=self.relDir)
        self.populateCacheTxtScrollLs()

    def populateCacheTxtScrollLs(self, *args):
        self.relDir = pm.textFieldButtonGrp(self.relTxtFieldBtnGrp, q=True, text=True)
        abcFiles = [file.split('\\')[-1] for file in glob.glob('{}/*.abc'.format(self.relDir))]
        editMaFiles = [file.split('\\')[-1] for file in glob.glob('{}/*.editMA'.format(self.relDir))]
        if pm.textScrollList(self.cacheTxtScrollLs, q=True, allItems=True):
            pm.textScrollList(self.cacheTxtScrollLs, e=True, removeAll=True)
        pm.textScrollList(self.cacheTxtScrollLs, e=True, append=abcFiles)
        pm.textScrollList(self.cacheTxtScrollLs, e=True, append=editMaFiles)
