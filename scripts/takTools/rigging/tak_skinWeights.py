"""
Author: Tak
Contact: https://ta-note.com

Description:
You can assign specific numeric value to the selected vertices skin weights like using component editor.

Usage:
import tak_skinWeights
reload(tak_skinWeights)
tak_skinWeights.SkinWeights()
"""

# Python Modules
import os
from functools import partial

# Maya Modules
from maya import cmds
from maya import mel
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma

# Custom Modules
from imp import reload
from ..rigging import All_Deformers_2_SkinCluster as ad2sc; reload(ad2sc)
from ..utils import skin as skinUtil; reload(skinUtil)
from ..utils import decorators

# Constants
MODULE_NAME = 'takTools'
MODULE_DIR = os.path.dirname(__file__).split(MODULE_NAME, 1)[0] + MODULE_NAME
CUSTOM_DAG_MENU_FILE = '{}\\scripts\\mel\\dagMenuProc.mel'.format(MODULE_DIR).replace('\\', '/')
ORIG_DAG_MENU_FILE = "C:/Program Files/Autodesk/Maya{}/scripts/others/dagMenuProc.mel".format(cmds.about(v=True))
WIN_NAME = 'takSkinWeightsWin'
MIN_WEIGHT = 0.00001
OBJECT_COLOR = om.MColor([0.0, 1.0, 1.0])

# Global Variables
swInstance = None


def showUI():
    global swInstance
    swInstance = SkinWeights()
    swInstance.ui()
    swInstance.loadInf()
    swInstance.enableCustomDagMenu()

    # Create script job to populate influence text scroll list automatically
    cmds.scriptJob(parent=WIN_NAME, event=['SelectionChanged', swInstance.loadInf])

    # When window is closed call destructor function.
    cmds.scriptJob(uid=[WIN_NAME, swInstance.__del__])


class SkinWeights(object):
    def __init__(self):
        self.vtxList = []
        self.uiWidgets = {}
        self.infWeightTable = {}
        self.weightInfTable = {}
        self.skinClst = ''
        self.infs = []
        self.infTxtScrLsCurrentAllItems = []

    def __del__(self):
        self._disableInfluencesColor()
        self.infTxtScrLsCurrentAllItems = []
        self.enableCustomDagMenu(False)

    def ui(self):
        if cmds.window(WIN_NAME, exists=True):
            cmds.deleteUI(WIN_NAME)

        cmds.window(WIN_NAME, title='Tak Skin Weights Tool')

        self.uiWidgets['mainMenuBarLo'] = cmds.menuBarLayout(p=WIN_NAME)

        # Menus
        ## Edit Menu
        self.uiWidgets['editMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='Edit', tearOff=True)
        self.uiWidgets['rebindMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Rebind', c=rebind, ann='Rebind in current state for the selected geometries.')
        self.uiWidgets['copyPasteMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Copy and Paste', c=SkinWeights.copyPasteWeight, ann='Copy first selected vertex weights and paste the others.')
        self.uiWidgets['copyOverlapMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Copy Overlaped Vertices', c=SkinWeights.copySkinOverlapVertices, ann='Copy a source mesh skin to a target mesh only for overlaped vertices.')
        cmds.menuItem(divider=True)
        self.uiWidgets['hammerMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Hammer', c="mel.eval('WeightHammer;')", ann='Set average weights with neighbor vertices.')
        self.uiWidgets['mirrorMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Mirror', c="mel.eval('MirrorSkinWeights;')", ann='Mirror skin weights positive X to negative X.')
        cmds.menuItem(optionBox=True, c='mel.eval("MirrorSkinWeightsOptions;")')
        cmds.menuItem(divider=True, dividerLabel='Optimization')
        self.uiWidgets['pruneMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Prune Small Weights', c=SkinWeights.prunSkinWeights)
        self.uiWidgets['rmvUnusedInfMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Remove Unused Influences', c="mel.eval('removeUnusedInfluences;')")

        ## Select Menu
        self.uiWidgets['selectMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='Select', tearOff=True)
        self.uiWidgets['selectInfsMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Influences', c=selectInfluences, ann='Select influences with selected meshes.')
        self.uiWidgets['selectVtxsMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Vertices', c=selAffectedVertex, ann='Select weighted vertices with selected joints.')
        cmds.menuItem(divider=True, dividerLabel='Modify')
        self.uiWidgets['growEdgeLoopSelMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Grow Edge Loop', c=extendEdgeLoopSelection, ann='Grow current edge loop selection.')
        self.uiWidgets['growEdgeRingSelMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Grow Edge Ring', c=extendEdgeRingSelection, ann='Grow current edge ring selection.')
        self.uiWidgets['growSelMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Grow', c=lambda x: mel.eval('GrowPolygonSelectionRegion;'), ann='Grow current selection.')
        self.uiWidgets['shrinkSelMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Shrink', c=lambda x: mel.eval('ShrinkPolygonSelectionRegion;'), ann='Shrink current selection.')

        ## View Menu
        self.uiWidgets['viewMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='View')
        self.uiWidgets['hideZroInfMenuItem'] = cmds.menuItem(p=self.uiWidgets['viewMenu'], checkBox=True, label='Hide Zero Influences', c=self.loadInf)
        self.uiWidgets['sortWeightMenuItem'] = cmds.menuItem(self.uiWidgets['viewMenu'], checkBox=False, label='Sort by Weight', c=self.loadInf)
        self.uiWidgets['toggleCustomDagMenuItem'] = cmds.menuItem(p=self.uiWidgets['viewMenu'], checkBox=True, label='Custom DAG Menu', c=self.toggleCustomDagMenu)

        ## Utils Menu
        self.uiWidgets['utilsMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='Utils')
        self.uiWidgets['SSDMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='SSD', c=lambda x: skinUtil.SSD(cmds.ls(sl=True)[0]), ann='Bake skin combined with other deforemr to a single skin cluster for a selected geometry.')
        self.uiWidgets['convertMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='Convert Deformer', c=ad2sc.showGUI, ann='Convert any deformers to a skin cluster for controllers.')
        self.uiWidgets['transferMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='Transfer', c=transferWeightsGUI, ann='Transfer weights form a joint to other joint.')
        self.uiWidgets['skinIOMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='Skin I/O...', c=SkinWeights.showSkinIOGUI, ann='Import/Export skin weights for selected geometries.')

        # Main GUI
        self.uiWidgets['mainColLo'] = cmds.columnLayout(p=WIN_NAME, adj=True)

        self.uiWidgets['mainTabLo'] = cmds.tabLayout(p=self.uiWidgets['mainColLo'], tv=False)
        self.uiWidgets['infWghtRowColLo'] = cmds.rowColumnLayout(p=self.uiWidgets['mainTabLo'], numberOfColumns=2, columnWidth=[(1, 220), (2, 60)], columnSpacing=[(2, 5)])
        self.uiWidgets['infFrmLo'] = cmds.frameLayout(p=self.uiWidgets['infWghtRowColLo'], label='Influences')
        self.uiWidgets['infTxtScrLs'] = cmds.textScrollList(p=self.uiWidgets['infFrmLo'], h=200, sc=self.infTxtScrLsSelCmd, allowMultiSelection=True)
        self.uiWidgets['infPopMenu'] = cmds.popupMenu(p=self.uiWidgets['infTxtScrLs'])
        self.uiWidgets['loadInfMenu'] = cmds.menuItem(p=self.uiWidgets['infPopMenu'], label='Load Influences', c=self.loadInf)

        self.uiWidgets['wghtFrmLo'] = cmds.frameLayout(p=self.uiWidgets['infWghtRowColLo'], label='Weights')
        self.uiWidgets['wghtTxtScrLs'] = cmds.textScrollList(p=self.uiWidgets['wghtFrmLo'], h=200, sc=self.weightTxtScrLsSelCmd, allowMultiSelection=True)

        self.uiWidgets['wghtPrsRowColLo'] = cmds.rowColumnLayout(p=self.uiWidgets['mainColLo'], numberOfColumns=5, columnWidth=[(1, 50), (2, 50), (3, 50), (4, 50), (5, 50)], columnSpacing=[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7)])
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='0', c=partial(self.setWeight, 0.0))
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='0.25', c=partial(self.setWeight, 0.25))
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='0.5', c=partial(self.setWeight, 0.5))
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='0.75', c=partial(self.setWeight, 0.75))
        cmds.button(p=self.uiWidgets['wghtPrsRowColLo'], label='1', c=partial(self.setWeight, 1.0))

        self.uiWidgets['wghtSubAddRowColLo'] = cmds.rowColumnLayout(p=self.uiWidgets['mainColLo'], numberOfColumns=4, columnWidth=[(1, 107), (2, 50), (3, 50), (4, 50)], columnSpacing=[(1, 7), (2, 7), (3, 7), (4, 7)])
        cmds.button(p=self.uiWidgets['wghtSubAddRowColLo'], label='Set Custom Weight', c=partial(self.subAddWeight, 'default'))
        self.uiWidgets['rltvWghtValfloatFld'] = cmds.floatField(p=self.uiWidgets['wghtSubAddRowColLo'], v=0.050, min=0.001, max=1.000, step=0.010, precision=3)
        cmds.button(p=self.uiWidgets['wghtSubAddRowColLo'], label='-', c=partial(self.subAddWeight, 'sub'))
        cmds.button(p=self.uiWidgets['wghtSubAddRowColLo'], label='+', c=partial(self.subAddWeight, 'add'))

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
        self._disableInfluencesColor()

        # Get options
        hideZroInfOpt = cmds.menuItem(self.uiWidgets['hideZroInfMenuItem'], q=True, checkBox=True)
        weightSortOpt = cmds.menuItem(self.uiWidgets['sortWeightMenuItem'], q=True, checkBox=True)

        self.vtxList = cmds.filterExpand(cmds.ls(sl=True, fl=True), sm=31)

        # Check selection error
        if not self.vtxList or not self.isMultipleGeoSelected():
            self.userFeedback()
            return

        # Get skin cluster from selected vertex
        self.getSkinClst(self.vtxList[0])
        if not self.skinClst:
            self.userFeedback()
            return

        # Get influences
        self.infs = cmds.skinCluster(self.skinClst, q=True, inf=True)

        # Make influences weight value table
        self.updateWeightTable(self.skinClst, self.vtxList, self.infs)

        # Hide zero weighted influences depend on option state
        if hideZroInfOpt:
            self.infs = self.removeZeroWeightInfs().keys()

        # Sorting
        sortedInfs = sorted(self.infs)
        if weightSortOpt:
            sortedInfs = self.sortByWeight(self.infs)

        # Populate text scroll list
        self.populateInfList(sortedInfs)
        self.populateWghtList(sortedInfs)
        self.infTxtScrLsSelCmd()

    def getSkinClst(self, vtx):
        '''
        Get skin cluster with a vertex.
        '''
        geo = vtx.split('.')[0]
        self.skinClst = mel.eval('findRelatedSkinCluster "%s";' % geo)

    #@decorators.printElapsedTime
    def updateWeightTable(self, skinClst, vtxList, infs):
        '''
        Make skin influences weight table.
        '''
        self.infWeightTable = {}
        self.weightInfTable = {}

        for inf in infs:
            vtxsWeightsForInf = [cmds.skinPercent(skinClst, vtx, q=True, transform=inf) for vtx in vtxList]
            meanWeight = sum(vtxsWeightsForInf) / len(vtxsWeightsForInf)
            weightStr = '{}               {}'.format(round(meanWeight, 4), inf)
            self.infWeightTable[inf] = weightStr
            self.weightInfTable[weightStr] = inf

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
            cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, append=self.infWeightTable[inf])

    def removeZeroWeightInfs(self, *args):
        rmvZroWghtTable = {}

        for inf in self.infWeightTable.keys():
            if float(self.infWeightTable[inf].split(' ')[0]) < 0.0001:
                continue
            else:
                rmvZroWghtTable[inf] = self.infWeightTable[inf]

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

    def sortByWeight(self, infs):
        weightSortedItems = sorted(self.infWeightTable.items(), key=lambda item: float(item[1].split(' ')[0]))
        weightSortedInfs = [item[0] for item in weightSortedItems]
        validInfs = [inf for inf in weightSortedInfs if inf in infs]
        return validInfs

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
        self._disableInfluencesColor()

        selInfList = cmds.textScrollList(self.uiWidgets['infTxtScrLs'], q=True, selectItem=True)
        cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, deselectAll=True)

        toSelWeightStrs = []

        for selInf in selInfList:
            matchingWeightStr = self.infWeightTable[selInf]
            toSelWeightStrs.append(matchingWeightStr)
            displayObjectColor(selInf, True)

        for toSelWeightStr in toSelWeightStrs:
            cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, selectItem=toSelWeightStr)

    def weightTxtScrLsSelCmd(self, *args):
        """ Select matching influences in influences text scroll list """
        self._disableInfluencesColor()

        selWeightStrs = cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], q=True, selectItem=True)
        cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, deselectAll=True)

        selInfList = []

        for selWeightStr in selWeightStrs:
            matchingInfStr = self.weightInfTable[selWeightStr]
            selInfList.append(matchingInfStr)

        for selInf in selInfList:
            cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, selectItem=selInf)
            displayObjectColor(selInf, True)

    def _disableInfluencesColor(self):
        if self.infs:
            for inf in self.infs:
                displayObjectColor(inf, False)

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

    def isMultipleGeoSelected(self):
        '''
        Check if user select component more than two geometry.
        '''

        geoList = list(set(cmds.ls(self.vtxList, objectsOnly=True)))

        if len(geoList) > 1:
            cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, removeAll=True)
            cmds.textScrollList(self.uiWidgets['infTxtScrLs'], e=True, append='Select vertex of one object')
            return False
        else:
            return True

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
            try:
                numInfsPerVtx.append(len(cmds.skinPercent(skinClst, '{}.vtx[{}]'.format(mesh, i), q=True, ignoreBelow=ignoreWeight, v=True)))
            except:
                cmds.select('{}.vtx[{}]'.format(mesh, i), r=True)
                mel.eval('doHammerWeightsArgList 1 { "1" };')
                cmds.select(mesh, r=True)
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
    def showSkinIOGUI(*args):
        from ..utils import skin as skUtil

        def importSkin(skinDirectory, *args):
            for skinFile in os.listdir(skinDirectory):
                print(os.path.join(skinDirectory, skinFile))
                skUtil.loadBSkin(os.path.join(skinDirectory, skinFile))

        def exportSkin(skinDirectory, *args):
            meshes = cmds.filterExpand(cmds.ls(sl=True), sm=12)
            if not meshes:
                return
            for mesh in meshes:
                skUtil.saveBSkin(mesh, skinDirectory)

        def setDirectory(*args):
            dir = cmds.fileDialog2(fm=3)
            if dir:
                cmds.textFieldButtonGrp('skinDirTxtFldBtnGrp', e=True, text=dir[0])

        cmds.window(title='Skin I/O', p=WIN_NAME)
        cmds.columnLayout(adj=True)
        cmds.textFieldButtonGrp('skinDirTxtFldBtnGrp', label='Skin Directory:', buttonLabel='...', bc=setDirectory)
        cmds.button(label='Import', c=lambda x: importSkin(cmds.textFieldButtonGrp('skinDirTxtFldBtnGrp', q=True, text=True)))
        cmds.button(label='Export', c=lambda x: exportSkin(cmds.textFieldButtonGrp('skinDirTxtFldBtnGrp', q=True, text=True)))
        cmds.showWindow()

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

    @staticmethod
    def copySkinOverlapVertices(*args):
        meshes = cmds.filterExpand(cmds.ls(os=True), sm=12)
        skinUtil.copySkinOverlapVertices(meshes[0], meshes[1])


def extendEdgeRingSelection(*args):
    preSelEdges = cmds.ls(sl=True, fl=True)

    mel.eval('ConvertSelectionToFaces;')
    mel.eval('ConvertSelectionToEdges;')
    faceEdges = cmds.ls(sl=True, fl=True)

    ringEdges = []
    for preSelEdge in preSelEdges:
        cmds.select(preSelEdge, r=True)
        mel.eval('polySelectSp -ring;')
        ringEdges.extend(cmds.ls(sl=True, fl=True))

    cmds.select(set(faceEdges) & set(ringEdges), r=True)


def extendEdgeLoopSelection(*args):
    preSelEdges = cmds.ls(sl=True, fl=True)

    loopEdges = []
    for preSelEdge in preSelEdges:
        cmds.select(preSelEdge, r=True)
        mel.eval('polySelectSp -loop;')
        loopEdges.extend(cmds.ls(sl=True, fl=True))

    cmds.select(preSelEdges, r=True)
    mel.eval('GrowPolygonSelectionRegion;')
    extenedEdges = cmds.ls(sl=True, fl=True)

    cmds.select(set(loopEdges) & set(extenedEdges), r=True)


def selAffectedVertex(*args):
    infs = cmds.ls(sl=True)
    vtxs = []
    for inf in infs:
        vtxs.extend(skinUtil.getAffectedVertex(inf, 0.001))
    if not vtxs:
        print('No vertices be affected by selected infuences.')
        return
    cmds.select(vtxs, r=True)


def selectInfluences(*args):
    sels = cmds.ls(sl=True)
    infs = []
    for sel in sels:
        skClu = mel.eval('findRelatedSkinCluster("%s");' % sel)
        infs.extend(cmds.skinCluster(skClu, q=True, inf=True))
    cmds.select(infs)
    return infs


def rebind(*args):
    selGeos = cmds.filterExpand(cmds.ls(sl=True), sm=[9, 10, 12])
    for sel in selGeos:
        skinUtil.reBind(sel)


def transferWeightsGUI(*args):
    cmds.window(title='Transfer Weights', p=WIN_NAME, tlb=True)
    cmds.columnLayout(adj=True)
    cmds.rowLayout(numberOfColumns=3)
    cmds.textField('srcInfTxtFld')
    cmds.popupMenu()
    cmds.menuItem(label='Load Selected Influence', c=partial(loadSelInf, 'srcInfTxtFld'))
    cmds.text(label='>>>')
    cmds.textField('trgInfTxtFld')
    cmds.popupMenu()
    cmds.menuItem(label='Load Selected Influence', c=partial(loadSelInf, 'trgInfTxtFld'))
    cmds.setParent('..')
    cmds.button(label='Transfer', c=transferWeights)
    cmds.showWindow()


def loadSelInf(wgt, *arg):
    selInfs = cmds.textScrollList(swInstance.uiWidgets['infTxtScrLs'], q=True, selectItem=True)
    if selInfs:
        cmds.textField(wgt, e=True, text=selInfs[0])


def transferWeights(*args):
    srcInf = cmds.textField('srcInfTxtFld', q=True, text=True)
    trgInf = cmds.textField('trgInfTxtFld', q=True, text=True)
    if not srcInf or not trgInf:
        cmds.warning('Provided not enough influences. Please set source influence and target influence.')
        return

    selVtxs = cmds.ls(sl=True, fl=True)
    meshes = list(set(cmds.ls(selVtxs, objectsOnly=True)))
    if not selVtxs or len(meshes) > 1:
        cmds.warning('Please select vertices of a mesh.')
        return

    skinClst = mel.eval('findRelatedSkinCluster("{}");'.format(meshes[0]))
    for vtx in selVtxs:
        srcInfSkinVal = cmds.skinPercent(skinClst, vtx, transform=srcInf, query=True)
        trgInfSkinVal = cmds.skinPercent(skinClst, vtx, transform=trgInf, query=True)
        resultSkinVal = srcInfSkinVal + trgInfSkinVal
        cmds.skinPercent(skinClst, vtx, transformValue=[(srcInf, 0), (trgInf, resultSkinVal)], nrm=True)

    swInstance.loadInf()


def displayObjectColor(object='', use=True):
    sels = om.MSelectionList()
    sels = om.MGlobal.getActiveSelectionList() if not object else sels.add(object)
    assert sels.length() != 0, 'No object given to set color.'

    dagPath = sels.getDagPath(0)
    fnDag = om.MFnDagNode(dagPath)
    fnDag.objectColorRGB = OBJECT_COLOR
    fnDag.objectColorType = int(use) * 2  # Use object color type RGB when True
