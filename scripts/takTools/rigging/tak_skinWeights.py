"""
Author: Tak
Website: ta-note.com

Description:
You can assign specific numeric value to the selected vertices skin weights like using component editor.

Usage:
import tak_skinWeights
reload(tak_skinWeights)
tak_skinWeights.SkinWeights()
"""

import os
from functools import partial

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import pymel.core as pm

from ..utils import decorators


MODULE_NAME = 'takTools'
MODULE_DIR = os.path.dirname(__file__).split(MODULE_NAME, 1)[0] + MODULE_NAME
CUSTOM_DAG_MENU_FILE = '{}\\scripts\\mel\\dagMenuProc.mel'.format(MODULE_DIR).replace('\\', '/')
ORIG_DAG_MENU_FILE = "C:/Program Files/Autodesk/Maya{}/scripts/others/dagMenuProc.mel".format(cmds.about(v=True))
WIN_NAME = 'takSkinWeightsWin'
MIN_WEIGHT = 0.00001


def showUI():
    sw = SkinWeights()
    sw.ui()
    sw.enableCustomDagMenu()

    # Create script job to populate influence text scroll list automatically
    cmds.scriptJob(parent=WIN_NAME, event=['SelectionChanged', sw.loadInf])

    # When window is closed call destructor function.
    cmds.scriptJob(uid=[WIN_NAME, sw.__del__])


class SkinWeights(object):
    def __init__(self):
        self.vtxList = []
        self.uiWidgets = {}
        self.oriWeightTable = {}
        self.skinClst = ''
        self.infTxtScrLsCurrentAllItems = []

    def __del__(self):
        if self.infTxtScrLsCurrentAllItems:
            for inf in self.infTxtScrLsCurrentAllItems:
                SkinWeights.unuseObjectColor(inf)
        self.infTxtScrLsCurrentAllItems = []
        self.enableCustomDagMenu(False)

    def ui(self):
        if cmds.window(WIN_NAME, exists=True):
            cmds.deleteUI(WIN_NAME)

        cmds.window(WIN_NAME, title='Tak Skin Weights Tool')

        self.uiWidgets['mainMenuBarLo'] = cmds.menuBarLayout(p=WIN_NAME)
        self.uiWidgets['editMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='Edit')
        self.uiWidgets['copyPasteMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Copy and Paste', c=SkinWeights.copyPasteWeight, ann='Copy first selected vertex weights and paste the others.')
        self.uiWidgets['hammerMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Hammer', c="mel.eval('WeightHammer;')", ann='Set average weights with neighbor vertices.')
        self.uiWidgets['mirrorMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Mirror', c="mel.eval('MirrorSkinWeights;')", ann='Mirror skin weights positive X to negative X.')
        self.uiWidgets['pruneMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Prune Small Weights', c=SkinWeights.prunSkinWeights)
        self.uiWidgets['rmvUnusedInfMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Remove Unused Influences', c="mel.eval('removeUnusedInfluences;')")
        self.uiWidgets['optMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='Options')
        self.uiWidgets['hideZroInfMenuItem'] = cmds.menuItem(p=self.uiWidgets['optMenu'], checkBox=True,
                                                            label='Hide Zero Influences', c=self.loadInf)
        self.uiWidgets['sortHierMenuItem'] = cmds.menuItem(p=self.uiWidgets['optMenu'], checkBox=False,
                                                          label='Sort by Hierarchy', c=self.loadInf)
        self.uiWidgets['toggleCustomDagMenuItem'] = cmds.menuItem(p=self.uiWidgets['optMenu'], checkBox=True,
                                                          label='Custom DAG Menu', c=self.toggleCustomDagMenu)

        self.uiWidgets['mainColLo'] = cmds.columnLayout(p=WIN_NAME, adj=True)

        # Selection buttons layout
        self.uiWidgets['selectRowLo'] = cmds.rowLayout(p=self.uiWidgets['mainColLo'], nc=4)
        self.uiWidgets['shrinkBtn'] = cmds.button(l='Shrink', w=70, c=lambda x: mel.eval('ShrinkPolygonSelectionRegion;'))
        self.uiWidgets['growBtn'] = cmds.button(l='Grow', w=70, c=lambda x: mel.eval('GrowPolygonSelectionRegion;'))
        self.uiWidgets['ringBtn'] = cmds.button(l='Ring', w=70, c=selectVtxRing)
        self.uiWidgets['loopBtn'] = cmds.button(l='Loop', w=70, c=lambda x: mel.eval('polySelectSp -loop;'))

        self.uiWidgets['mainTabLo'] = cmds.tabLayout(p=self.uiWidgets['mainColLo'], tv=False)
        self.uiWidgets['infWghtRowColLo'] = cmds.rowColumnLayout(p=self.uiWidgets['mainTabLo'], numberOfColumns=2,
                                                                columnWidth=[(1, 140), (2, 140)],
                                                                columnSpacing=[(2, 5)])
        self.uiWidgets['infFrmLo'] = cmds.frameLayout(p=self.uiWidgets['infWghtRowColLo'], label='Influences')
        self.uiWidgets['infTxtScrLs'] = cmds.textScrollList(p=self.uiWidgets['infFrmLo'], h=200, sc=self.infTxtScrLsSelCmd,
                                                           allowMultiSelection=True)
        self.uiWidgets['infPopMenu'] = cmds.popupMenu(p=self.uiWidgets['infTxtScrLs'])
        self.uiWidgets['loadInfMenu'] = cmds.menuItem(p=self.uiWidgets['infPopMenu'], label='Load Influences',
                                                     c=self.loadInf)

        self.uiWidgets['wghtFrmLo'] = cmds.frameLayout(p=self.uiWidgets['infWghtRowColLo'], label='Weight Value')
        self.uiWidgets['wghtTxtScrLs'] = cmds.textScrollList(p=self.uiWidgets['wghtFrmLo'], h=200, enable=True,
                                                            allowMultiSelection=True)

        self.uiWidgets['wghtPrsRowColLo'] = cmds.rowColumnLayout(p=self.uiWidgets['mainColLo'], numberOfColumns=5,
                                                                columnWidth=[(1, 50), (2, 50), (3, 50), (4, 50),
                                                                             (5, 50)],
                                                                columnSpacing=[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7)])
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='0', c=partial(self.setWeight, 0.0))
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='0.25', c=partial(self.setWeight, 0.25))
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='0.5', c=partial(self.setWeight, 0.5))
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='0.75', c=partial(self.setWeight, 0.75))
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='1', c=partial(self.setWeight, 1.0))

        self.uiWidgets['wghtSubAddRowColLo'] = cmds.rowColumnLayout(p=self.uiWidgets['mainColLo'], numberOfColumns=4,
                                                                   columnWidth=[(1, 107), (2, 50), (3, 50), (4, 50)],
                                                                   columnSpacing=[(1, 7), (2, 7), (3, 7), (4, 7)])
        cmds.button(p=self.uiWidgets['wghtSubAddRowColLo'], label='Set Custom Weight',
                    c=partial(self.subAddWeight, 'default'))
        self.uiWidgets['rltvWghtValfloatFld'] = cmds.floatField(p=self.uiWidgets['wghtSubAddRowColLo'], v=0.050,
                                                               min=0.001, max=1.000, step=0.010, precision=3)
        cmds.button(p=self.uiWidgets['wghtSubAddRowColLo'], label='-', c=partial(self.subAddWeight, 'sub'))
        cmds.button(p=self.uiWidgets['wghtSubAddRowColLo'], label='+', c=partial(self.subAddWeight, 'add'))

        self.uiWidgets['wghtTrsfRowColLo'] = cmds.rowColumnLayout(p=self.uiWidgets['mainColLo'], numberOfColumns=4,
                                                                 columnWidth=[(1, 93), (2, 20), (3, 93), (4, 50)],
                                                                 columnSpacing=[(1, 7), (2, 7), (3, 7), (4, 7)])
        self.uiWidgets['srcInfTxtFld'] = cmds.textField(p=self.uiWidgets['wghtTrsfRowColLo'])
        cmds.popupMenu()
        cmds.menuItem(label='Load Selected Influence', c=partial(self.loadSelInf, self.uiWidgets['srcInfTxtFld']))
        cmds.text(p=self.uiWidgets['wghtTrsfRowColLo'], label='>>>')
        self.uiWidgets['trgInfTxtFld'] = cmds.textField(p=self.uiWidgets['wghtTrsfRowColLo'])
        cmds.popupMenu()
        cmds.menuItem(label='Load Selected Influence', c=partial(self.loadSelInf, self.uiWidgets['trgInfTxtFld']))
        cmds.button(p=self.uiWidgets['wghtTrsfRowColLo'], label='Transfer', c=self.transferWeights)

        self.uiWidgets['maxInfRowColLo'] = cmds.rowColumnLayout(p=self.uiWidgets['mainColLo'], numberOfColumns=3, columnSpacing=[(1, 2), (2, 2), (3, 2)])
        cmds.button(p=self.uiWidgets['maxInfRowColLo'], label='Max Influences', c=SkinWeights.checkMaxInfluences)
        self.uiWidgets['maxInfsOptMenu'] = cmds.optionMenu(p=self.uiWidgets['maxInfRowColLo'], label='Max Influences:')
        cmds.menuItem(label='4')
        cmds.menuItem(label='8')
        cmds.menuItem(label='12')
        cmds.optionMenu(self.uiWidgets['maxInfsOptMenu'], e=True, v='4')
        cmds.button(p=self.uiWidgets['maxInfRowColLo'], label='Set', c=self.fitMaxInfluence, w=50)

        cmds.window(WIN_NAME, e=True, w=100, h=200)
        cmds.showWindow(WIN_NAME)

    def loadInf(self, *args):
        '''
        Main method.
        Populate influence and weight value text scroll list.
        '''
        # Deactivate influences object color
        if self.infTxtScrLsCurrentAllItems:
            for inf in self.infTxtScrLsCurrentAllItems:
                SkinWeights.unuseObjectColor(inf)

        # Get options
        hideZroInfOpt = cmds.menuItem(self.uiWidgets['hideZroInfMenuItem'], q=True, checkBox=True)
        hierSortOpt = cmds.menuItem(self.uiWidgets['sortHierMenuItem'], q=True, checkBox=True)

        self.vtxList = cmds.ls(sl=True)

        # Check selection error
        geoChkResult = self.checkGeoNum()
        if not '.' in str(self.vtxList) or not geoChkResult:
            self.userFeedback()
            return

        # Get skin cluster from selected vertex
        self.getSkinClst(self.vtxList[0])
        if not self.skinClst:
            self.userFeedback()
            return

        # Get influences
        infs = cmds.skinCluster(self.skinClst, q=True, inf=True)

        # Make influences weight value table
        self.skinWeightTable(self.skinClst, self.vtxList, infs)

        # Hide zero weighted influences depend on option state
        if hideZroInfOpt:
            rmvedZroWghtTable = self.hideZeroWghtInfs()
            infs = rmvedZroWghtTable.keys()

        # Sorting
        if hierSortOpt:
            infs = self.sortByHierarchy(infs)
        else:
            infs = self.sortByAlphabetically(infs)

        # Populate text scroll list
        self.populateInfList(infs)
        self.populateWghtList(infs)

    def getSkinClst(self, vtx):
        '''
        Get skin cluster with a vertex.
        '''

        geo = vtx.split('.')[0]

        self.skinClst = mel.eval('findRelatedSkinCluster "%s";' % geo)

    def skinWeightTable(self, skinClst, vtxList, infs):
        '''
        Make skin influences weight table.
        '''
        self.oriWeightTable = {}

        # Initialize original weight value table
        for inf in infs:
            self.oriWeightTable[inf] = str(0.0) + '   ' + inf

        # Replace initialized value if not value is 0
        for inf in infs:
            for vtx in vtxList:
                infWeightVal = cmds.skinPercent(skinClst, vtx, q=True, transform=inf)
                if not infWeightVal == 0.0:
                    self.oriWeightTable[inf] = str(round(infWeightVal, 4)) + '   ' + inf
                else:
                    continue

    def populateInfList(self, infs):
        '''
        Populate influences text scroll list.
        '''

        items = cmds.textScrollList(self.uiWidgets['infTxtScrLs'], q=True, allItems=True)
        selItems = cmds.textScrollList(self.uiWidgets['infTxtScrLs'], q=True, selectItem=True)
        if items:
            cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, removeAll=True)
        cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, append=infs)

        cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, selectItem=selItems)

    def populateWghtList(self, infs):
        '''
        Populate weight value for each influence.
        '''

        items = cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], q=True, allItems=True)
        if items:
            cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, removeAll=True)
        for inf in infs:
            cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, append=self.oriWeightTable[inf])

    def hideZeroWghtInfs(self, *args):
        '''
        Hide zero weights value influences in the list.
        '''
        # Initialize data
        rmvZroWghtTable = {}

        for inf in self.oriWeightTable.keys():
            if float(self.oriWeightTable[inf].split(' ')[0]) < 0.0001:
                continue
            else:
                rmvZroWghtTable[inf] = self.oriWeightTable[inf]


        return rmvZroWghtTable

    def setWeight(self, weightVal, mode='default', *args):
        '''
        Set weight value with given value.
        '''

        # Get selected influence
        selInfList = cmds.textScrollList(self.uiWidgets['infTxtScrLs'], q=True, selectItem=True)

        for selInf in selInfList:
            if mode == 'sub':
                cmds.skinPercent(self.skinClst, self.vtxList, transformValue=[(selInf, -weightVal)], prw=0, relative=True)
            elif mode == 'add':
                cmds.skinPercent(self.skinClst, self.vtxList, transformValue=[(selInf, weightVal)], prw=0, relative=True)
            else:
                cmds.skinPercent(self.skinClst, self.vtxList, transformValue=[(selInf, weightVal)], prw=0)

        self.loadInf()
        self.infTxtScrLsSelCmd()

    def subAddWeight(self, mode, *args):
        '''
        Subtract or Add weight value for selected influence.
        '''

        weightVal = cmds.floatField(self.uiWidgets['rltvWghtValfloatFld'], q=True, v=True)

        self.setWeight(weightVal, mode)

    def sortByHierarchy(self, infs, *args):
        '''
        Sorting influences order by hierarchy depend on option.
        '''

        allInfList = cmds.skinCluster(self.skinClst, q=True, inf=True)
        hierSortInfList = []

        for inf in allInfList:
            if inf in infs:
                hierSortInfList.append(inf)
            else:
                continue

        return hierSortInfList

    def sortByAlphabetically(self, infs, *args):
        '''
        Sorting influences order by alphanetically depend on option.
        '''

        alphSortList = sorted(infs)

        return alphSortList

    def toggleCustomDagMenu(self, *args):
        loadCustomDagMenu = cmds.menuItem(self.uiWidgets['toggleCustomDagMenuItem'], q=True, checkBox=True)
        self.enableCustomDagMenu(loadCustomDagMenu)

    def enableCustomDagMenu(self, enable=True):
        if enable:
            mel.eval('source "{}"'.format(CUSTOM_DAG_MENU_FILE))
        else:
            mel.eval('source "{}"'.format(ORIG_DAG_MENU_FILE))

    def infTxtScrLsSelCmd(self, *args):
        """ Select matching weight value in weight value text scroll list """

        allInfs = cmds.textScrollList(self.uiWidgets['infTxtScrLs'], q=True, allItems=True)
        selInfList = cmds.textScrollList(self.uiWidgets['infTxtScrLs'], q=True, selectItem=True)

        self.infTxtScrLsCurrentAllItems = allInfs

        cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, deselectAll=True)
        selInfWghtList = []

        if selInfList:
            for selInf in selInfList:
                matchingWeightVal = self.oriWeightTable[selInf]
                selInfWghtList.append(matchingWeightVal)
                wghtVal = self.oriWeightTable[selInf].split(' ')[0]

            self.changeSelInfCol(allInfs, selInfList)

    def changeSelInfCol(self, allInfs, selInfList):
        for inf in allInfs:
            SkinWeights.unuseObjectColor(inf)

        for selInf in selInfList:
            SkinWeights.useObjectColor(selInf)

    @staticmethod
    def unuseObjectColor(inf):
        infNode = pm.PyNode(inf)
        infNode.setObjectColor(0)

    @staticmethod
    def useObjectColor(inf):
        infNode = pm.PyNode(inf)
        infNode.setObjectColor(8)

    def userFeedback(self):
        """ Annotation when user did not select a vertex """

        # Remove items in influences text scroll list
        items = cmds.textScrollList(self.uiWidgets['infTxtScrLs'], q=True, allItems=True)
        if items:
            cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, removeAll=True)

        # Remove items in weight value text scroll list
        items = cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], q=True, allItems=True)
        if items:
            cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, removeAll=True)

    def checkGeoNum(self):
        '''
        Check if user select component more than two geometry.
        '''

        geoList = []

        for vtx in self.vtxList:
            geo = vtx.split('.')[0]
            if not geo in geoList:
                geoList.append(geo)

        if len(geoList) >= 2:
            cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, removeAll=True)
            cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, append='Select vertex of one object')
            return False
        else:
            return True

    def loadSelInf(self, wgt, *arg):
        '''
        Load selected influence that in the influences text scroll list.
        '''

        selInf = cmds.textScrollList(self.uiWidgets['infTxtScrLs'], q=True, selectItem=True)
        cmds.textField(wgt, e=True, text=selInf[0])

    def transferWeights(self, *args):
        vtxList = cmds.ls(sl=True, fl=True)

        srcInf = cmds.textField(self.uiWidgets['srcInfTxtFld'], q=True, text=True)
        trgInf = cmds.textField(self.uiWidgets['trgInfTxtFld'], q=True, text=True)

        for vtx in vtxList:
            # get skin weight value
            srcInfSkinVal = cmds.skinPercent(self.skinClst, vtx, transform=srcInf, query=True)
            trgInfSkinVal = cmds.skinPercent(self.skinClst, vtx, transform=trgInf, query=True)

            resultSkinVal = srcInfSkinVal + trgInfSkinVal

            # transfer skin weights
            cmds.skinPercent(self.skinClst, vtx, transformValue=[(srcInf, 0), (trgInf, resultSkinVal)], nrm=True)

        # Refresh influence text scroll list.
        self.loadInf()

    @decorators.printElapsedTime
    def fitMaxInfluence(self, *args):
        for mesh in cmds.ls(sl=True):
            meshMaxInfs = SkinWeights.getMaxInfluences(mesh)
            targetMaxInfs = int(cmds.optionMenu(self.uiWidgets['maxInfsOptMenu'], q=True, v=True))
            if meshMaxInfs <= targetMaxInfs:
                print('"{}"s max influence is {} already. Skip processing.'.format(mesh, meshMaxInfs))
                continue

            # Create progress window
            cmds.window('progWin', title='working on "{}"'.format(mesh), mnb=False, mxb=False)
            cmds.columnLayout(adj=True)
            cmds.progressBar('progBar', w=400, isMainProgressBar=True, beginProgress=True, isInterruptable=True)
            cmds.showWindow('progWin')

            skinClst = mel.eval('findRelatedSkinCluster("{}");'.format(mesh))

            # Optimize weights and influences to speed up processing
            SkinWeights.prunSkinWeights(skinClst, mesh)
            cmds.skinCluster(skinClst, e=True, removeUnusedInfluence=True)

            # Set max influences for a skin cluster
            cmds.setAttr("{}.maintainMaxInfluences".format(skinClst), True)
            cmds.setAttr("{}.maxInfluences".format(skinClst), targetMaxInfs)

            infPrunedWeights = SkinWeights.pruneSkinInfluences(mesh, skinClst, targetMaxInfs)
            SkinWeights.setWeights(mesh, skinClst, infPrunedWeights)
            print('Fitting max influence for the "{}" is done.'.format(mesh))

            # Remove zero weighted influences
            cmds.skinCluster(skinClst, e=True, removeUnusedInfluence=True)

            cmds.progressBar('progBar', e=True, endProgress=True)
            cmds.deleteUI('progWin')

    @staticmethod
    def getMaxInfluences(mesh=None, ignoreWeight=MIN_WEIGHT):
        if not mesh:
            mesh = cmds.ls(sl=True)[0]
        skinClst = mel.eval('findRelatedSkinCluster("{}");'.format(mesh))
        vertCount = cmds.polyEvaluate(mesh, v=True)
        numInfsPerVtx = []
        for i in range(vertCount):
            numInfsPerVtx.append(len(cmds.skinPercent(skinClst, '{}.vtx[{}]'.format(mesh, i), q=True, ignoreBelow=ignoreWeight, v=True)))
        maxInfs = max(numInfsPerVtx)
        return maxInfs

    @staticmethod
    def checkMaxInfluences(*args):
        meshes = cmds.filterExpand(cmds.ls(sl=True), sm=12)
        for mesh in meshes:
            maxInfs = SkinWeights.getMaxInfluences(mesh)
            print('"{}" Max Influences: {}'.format(mesh, maxInfs))

    @staticmethod
    def prunSkinWeights(skinCluster=None, mesh=None, threshold=MIN_WEIGHT):
        if not mesh:
            # Try to get a mesh from selection
            meshes = cmds.filterExpand(cmds.ls(sl=True), sm=12)
            if not meshes:
                return
            mesh = meshes[0]

        if not skinCluster:
            skinCluster = mel.eval('findRelatedSkinCluster("{}");'.format(mesh))

        cmds.skinPercent(skinCluster, mesh, pruneWeights=threshold)

    @staticmethod
    def pruneSkinInfluences(mesh, skinClst, maxInfs):
        if cmds.nodeType(mesh) == 'transform':
            mesh = cmds.listRelatives(mesh, shapes=True, ni=True)[0]

        vertCount = cmds.polyEvaluate(mesh, vertex=True)

        cmds.progressBar('progBar', e=True, min=0, max=vertCount)

        resultMeshWeights = []
        for i in range(vertCount):
            vert = '{}.vtx[{}]'.format(mesh, i)
            infs = cmds.skinPercent(skinClst, vert, q=True, transform=None)
            weights = cmds.skinPercent(skinClst, vert, q=True, v=True)
            infWeightMap = dict(zip(infs, weights))

            sortedItems = sorted(infWeightMap.items(), key=lambda item: item[1], reverse=True)
            prunedItems = sortedItems[:maxInfs] + [(jnt, 0.0) for jnt, w in sortedItems[maxInfs:]]

            totalWeight = sum([item[1] for item in prunedItems])
            prunedItemsNormalizedMap = dict([(jnt, weight/totalWeight) for jnt, weight in prunedItems])

            resultVtxWeights = [prunedItemsNormalizedMap.get(inf) for inf in infs]
            resultMeshWeights.extend(resultVtxWeights)

            cmds.progressBar('progBar', e=True, step=1)

        return resultMeshWeights

    @staticmethod
    def setWeights(mesh, skinClst, weights):
        sels = om.MSelectionList()
        sels.add(mesh)
        sels.add(skinClst)
        meshDag = sels.getDagPath(0)
        skObj = sels.getDependNode(1)

        cpntFn = om.MFnSingleIndexedComponent()
        cpntObj = cpntFn.create(om.MFn.kMeshVertComponent)
        vertCount = cmds.polyEvaluate(mesh, vertex=True)
        cpntFn.setCompleteData(vertCount)

        skFn = oma.MFnSkinCluster(skObj)
        infIds = om.MIntArray([id for id in range(len(skFn.influenceObjects()))])
        weights = om.MDoubleArray(weights)
        skFn.setWeights(meshDag, cpntObj, infIds, weights)

    @staticmethod
    def copyPasteWeight(*args):
        '''
        Copy first vertex skin weights in selection list and paste to the others.
        '''
        selVtxs = cmds.ls(os=True, fl=True)
        srcVtx = selVtxs[0]
        trgVtxs = selVtxs[1:]

        cmds.select(srcVtx, r=True)
        mel.eval('artAttrSkinWeightCopy;')
        cmds.select(trgVtxs, r=True)
        mel.eval('artAttrSkinWeightPaste;')
        cmds.select(srcVtx, add=True)

def selectVtxRing(*args):
    mel.eval('PolySelectConvert 20;')
    mel.eval('polySelectSp -ring;')
    mel.eval('PolySelectConvert 3;')
