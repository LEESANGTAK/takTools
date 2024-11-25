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
from ..utils import bifrost as bfUtil; reload(bfUtil)
from ..utils import decorators

# Constants
MODULE_NAME = 'takTools'
MODULE_DIR = os.path.dirname(__file__).split(MODULE_NAME, 1)[0] + MODULE_NAME
CUSTOM_DAG_MENU_FILE = '{}/scripts/mel/dagMenuProc.mel'.format(MODULE_DIR.replace('\\', '/'))
ORIG_DAG_MENU_FILE = "C:/Program Files/Autodesk/Maya{}/scripts/others/dagMenuProc.mel".format(cmds.about(v=True))
WIN_NAME = 'takSkinWeightsWin'
MIN_WEIGHT = 0.00001
OBJECT_COLOR = om.MColor([0.0, 1.0, 0.0])

# Global Variables
swInstance = None


def showUI():
    global swInstance
    swInstance = SkinWeights()
    swInstance.ui()
    swInstance.loadInf()
    SkinWeights.enableCustomDagMenu()

    # Create script job to populate influence text scroll list automatically
    cmds.scriptJob(parent=WIN_NAME, event=['SelectionChanged', swInstance.loadInf])

    # When window is closed call destructor function.
    cmds.scriptJob(uid=[WIN_NAME, swInstance.__del__])


class SkinWeights(object):
    def __init__(self):
        self.selVertices = []
        self.uiWidgets = {}
        self.infWeightTable = {}
        self.weightInfTable = {}
        self.skinClst = ''
        self.infs = []
        self.infTxtScrLsCurrentAllItems = []

    def __del__(self):
        self._disableInfluencesColor()
        self.infTxtScrLsCurrentAllItems = []
        SkinWeights.enableCustomDagMenu(False)

    def ui(self):
        if cmds.window(WIN_NAME, exists=True):
            cmds.deleteUI(WIN_NAME)

        cmds.window(WIN_NAME, title='Tak Skin Weights')

        self.uiWidgets['mainMenuBarLo'] = cmds.menuBarLayout(p=WIN_NAME)

        # Menus
        ## Select Menu
        self.uiWidgets['selectMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='Select', tearOff=True)
        self.uiWidgets['selectInfsMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Influences', c=selectInfluences, ann='Select influences with selected meshes.')
        self.uiWidgets['selectVtxsMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Vertices', c=selAffectedVertex, ann='Select weighted vertices with selected joints.')
        cmds.menuItem(divider=True, dividerLabel='Modify')
        self.uiWidgets['growSelMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Grow', c=lambda x: mel.eval('GrowPolygonSelectionRegion;'), ann='Grow current selection.')
        self.uiWidgets['shrinkSelMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Shrink', c=lambda x: mel.eval('ShrinkPolygonSelectionRegion;'), ann='Shrink current selection.')
        self.uiWidgets['growEdgeLoopSelMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Grow Edge Loop', c=extendEdgeLoopSelection, ann='Grow current edge loop selection.')
        self.uiWidgets['growEdgeRingSelMenuItem'] = cmds.menuItem(p=self.uiWidgets['selectMenu'], label='Grow Edge Ring', c=extendEdgeRingSelection, ann='Grow current edge ring selection.')

        ## Edit Menu
        self.uiWidgets['editMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='Edit', tearOff=True)
        self.uiWidgets['rebindMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Rebind', c=rebind, ann='Rebind in current state for the selected geometries.')
        self.uiWidgets['updateBindPoseMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Update Bind Pose', c=updateBindPose, ann='Update bind pose for selected root joint.')
        cmds.menuItem(divider=True)
        self.uiWidgets['hammerMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Hammer', c="mel.eval('WeightHammer;')", ann='Set average weights with neighbor vertices.')
        self.uiWidgets['rigidifyMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Rigidify', c=skinUtil.rigidifySkin, ann='Rigidify skin for selected vertices. It is good for thin surface like collar.')
        self.uiWidgets['mirrorMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Mirror', c=skinUtil.mirrorSkin, ann='Mirror skin weights positive X to negative X.')
        cmds.menuItem(optionBox=True, c='mel.eval("MirrorSkinWeightsOptions;")')
        cmds.menuItem(divider=True, dividerLabel='Copy')
        self.uiWidgets['copyMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Copy Skin', c=copySkin, ann='Copy a source mesh skin to a target meshes.\nIf components and a mesh selected copy weights from mesh to components.')
        self.uiWidgets['copyOverlapMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Copy Overlaped Vertices', c=SkinWeights.copySkinOverlapVertices, ann='Copy a source mesh skin to a target mesh only for overlaped vertices.')
        self.uiWidgets['copyPasteMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Copy and Paste', c=copyPasteWeight, ann='Copy first selected vertex weights and paste the others.')
        cmds.menuItem(optionBox=True, c=copyPasteGUI)
        cmds.menuItem(divider=True, dividerLabel='Optimization')
        self.uiWidgets['pruneMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Prune Small Weights', c=SkinWeights.prunSkinWeights)
        self.uiWidgets['rmvUnusedInfMenuItem'] = cmds.menuItem(p=self.uiWidgets['editMenu'], label='Remove Unused Influences', c="mel.eval('removeUnusedInfluences;')")

        ## View Menu
        self.uiWidgets['viewMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='View')
        self.uiWidgets['hideZroInfMenuItem'] = cmds.menuItem(p=self.uiWidgets['viewMenu'], checkBox=True, label='Hide Zero Influences', c=self.loadInf)
        self.uiWidgets['sortWeightMenuItem'] = cmds.menuItem(self.uiWidgets['viewMenu'], checkBox=False, label='Sort by Weight', c=self.loadInf)
        self.uiWidgets['colorFeedbackMenuItem'] = cmds.menuItem(p=self.uiWidgets['viewMenu'], checkBox=True, label='Color Feedback', c=colorFeedback)
        self.uiWidgets['toggleCustomDagMenuItem'] = cmds.menuItem(p=self.uiWidgets['viewMenu'], checkBox=True, label='Custom DAG Menu', c=self.toggleCustomDagMenu)

        # Tools
        self.uiWidgets['toolsMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='Tools', tearOff=True)
        self.uiWidgets['brSmoothWeightsMenuItem'] = cmds.menuItem(p=self.uiWidgets['toolsMenu'], label='brSmoothWeights', c=runBrSmoothWeights, ann='Run brSmoothWeights tool.')
        self.uiWidgets['averageSkinWeightsBrushMenuItem'] = cmds.menuItem(p=self.uiWidgets['toolsMenu'], label='Average Weights Brush', c=runAverageWeightsBrush, ann='Run average weights brush tool.')
        self.uiWidgets['hammerWeightsBrushMenuItem'] = cmds.menuItem(p=self.uiWidgets['toolsMenu'], label='Hammer Weights Brush', c=runHammerWeightsBrush, ann='Run hammer weights brush tool.')

        ## Utils Menu
        self.uiWidgets['utilsMenu'] = cmds.menu(p=self.uiWidgets['mainMenuBarLo'], label='Utils')
        self.uiWidgets['skinCageMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='Skin Cage...', c=lambda x: bfUtil.showConvertToCageMeshUI(WIN_NAME), ann='Make skin cage mesh.')
        self.uiWidgets['SSDMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='SSD...', c=ssdGUI, ann='Bake skin combined with other deforemr to a single skin cluster for a selected geometry.')
        self.uiWidgets['convertMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='Converter...', c=lambda x: ad2sc.showGUI(WIN_NAME), ann='Convert any deformers to a skin cluster for controllers.')
        self.uiWidgets['transferMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='Transfer...', c=transferWeightsGUI, ann='Transfer weights form a joint to other joint.')
        self.uiWidgets['maxInfsMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='Max Influences...', c=maxInfluencesGUI, ann='Manage max influences.')
        self.uiWidgets['skinIOMenuItem'] = cmds.menuItem(p=self.uiWidgets['utilsMenu'], label='Skin I/O...', c=showSkinIOGUI, ann='Import/Export skin weights for selected geometries.')
        cmds.menuItem(optionBox=True, c=bSkinSaverGUI)

        # Main GUI
        self.uiWidgets['mainColLo'] = cmds.columnLayout(p=WIN_NAME, adj=True)

        self.uiWidgets['mainTabLo'] = cmds.tabLayout(p=self.uiWidgets['mainColLo'], tv=False)
        self.uiWidgets['infWghtRowColLo'] = cmds.rowColumnLayout(p=self.uiWidgets['mainTabLo'], numberOfColumns=2, columnWidth=[(1, 220), (2, 60)], columnSpacing=[(2, 5)])
        self.uiWidgets['infFrmLo'] = cmds.frameLayout(p=self.uiWidgets['infWghtRowColLo'], label='Influences')
        cmds.textScrollList('infsTxtScrLs', p=self.uiWidgets['infFrmLo'], h=200, sc=self.infTxtScrLsSelCmd, vcc=self.infTxtScrLsSelCmd, allowMultiSelection=True)
        self.uiWidgets['infPopMenu'] = cmds.popupMenu(p='infsTxtScrLs')
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

        # Get vertices from selection
        selComponents = cmds.ls(sl=True, fl=True)
        self.selVertices = cmds.filterExpand(selComponents, sm=[31, 28, 46]) or []
        selEdgesFaces = cmds.filterExpand(selComponents, sm=[32, 34])
        if selEdgesFaces:
            verticesFromEdgesFaces = cmds.ls(cmds.polyListComponentConversion(selEdgesFaces, toVertex=True), fl=True)
            self.selVertices.extend(verticesFromEdgesFaces)

        # Check selection error
        if not self.selVertices:
            self.userFeedback('Select skined component(s).')
            return

        if self.isMultipleGeoSelected():
            self.userFeedback('Select component(s) of one geometry.')
            return

        # Get skin cluster from selected vertex
        self.getSkinClst(self.selVertices[0])
        if not self.skinClst:
            self.userFeedback('Component(s) has no skin cluster.')
            return

        # Get influences
        self.infs = cmds.skinCluster(self.skinClst, q=True, inf=True)

        # Make influences weight value table
        self.updateWeightTable(self.skinClst, self.selVertices, self.infs)

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

    def updateWeightTable(self, skinClst, vertices, infs):
        '''
        Make skin influences weight table.
        '''
        self.infWeightTable = {}
        self.weightInfTable = {}

        verticesWeights = []
        for vertex in vertices:
            vtxWeights = cmds.skinPercent(skinClst, vertex, q=True, v=True)
            verticesWeights.append(vtxWeights)

        for i, item in enumerate(zip(*verticesWeights)):
            inf = infs[i]
            meanWeight = sum(item) / len(vertices)
            weightStr = '{}               {}'.format(round(meanWeight, 4), inf)
            self.infWeightTable[inf] = weightStr
            self.weightInfTable[weightStr] = inf

    def populateInfList(self, infs):
        '''
        Populate influences text scroll list.
        '''
        items = cmds.textScrollList('infsTxtScrLs', q=True, allItems=True)
        selItems = cmds.textScrollList('infsTxtScrLs', q=True, selectItem=True)
        if items:
            cmds.textScrollList('infsTxtScrLs', e=True, removeAll=True)
        cmds.textScrollList('infsTxtScrLs', e=True, append=infs)
        cmds.textScrollList('infsTxtScrLs', e=True, selectItem=selItems)

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
        selInfList = cmds.textScrollList('infsTxtScrLs', q=True, selectItem=True)

        for selInf in selInfList:
            if mode == 'sub':
                cmds.skinPercent(self.skinClst, self.selVertices, transformValue=[(selInf, -weightVal)], prw=0, relative=True)
            elif mode == 'add':
                cmds.skinPercent(self.skinClst, self.selVertices, transformValue=[(selInf, weightVal)], prw=0, relative=True)
            else:
                cmds.skinPercent(self.skinClst, self.selVertices, transformValue=[(selInf, weightVal)], prw=0)

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
        SkinWeights.enableCustomDagMenu(loadCustomDagMenu)

    @staticmethod
    def enableCustomDagMenu(enable=True):
        if enable:
            mel.eval('source "{}"'.format(CUSTOM_DAG_MENU_FILE))
        else:
            mel.eval('source "{}"'.format(ORIG_DAG_MENU_FILE))

    def infTxtScrLsSelCmd(self, *args):
        """ Select matching weight value in weight value text scroll list """
        self._disableInfluencesColor()

        selInfs = cmds.textScrollList('infsTxtScrLs', q=True, selectItem=True)
        cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, deselectAll=True)

        toSelWeightStrs = []

        if selInfs:
            for selInf in selInfs:
                matchingWeightStr = self.infWeightTable[selInf]
                toSelWeightStrs.append(matchingWeightStr)
                displayObjectColor(selInf, True)

            for toSelWeightStr in toSelWeightStrs:
                cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, selectItem=toSelWeightStr)

    def weightTxtScrLsSelCmd(self, *args):
        """ Select matching influences in influences text scroll list """
        self._disableInfluencesColor()

        selWeights = cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], q=True, selectItem=True)
        cmds.textScrollList('infsTxtScrLs', e=True, deselectAll=True)

        selInfList = []

        if selWeights:
            for selWeightStr in selWeights:
                matchingInfStr = self.weightInfTable[selWeightStr]
                selInfList.append(matchingInfStr)

            for selInf in selInfList:
                cmds.textScrollList('infsTxtScrLs', e=True, selectItem=selInf)
                displayObjectColor(selInf, True)

    def _disableInfluencesColor(self):
        if self.infs:
            for inf in self.infs:
                displayObjectColor(inf, False)

    def userFeedback(self, message=''):
        """ Annotation when user did not select a vertex """
        cmds.textScrollList('infsTxtScrLs', e=True, removeAll=True)
        cmds.textScrollList(self.uiWidgets['wghtTxtScrLs'], e=True, removeAll=True)
        cmds.textScrollList('infsTxtScrLs', e=True, append=message)

    def isMultipleGeoSelected(self):
        '''
        Check if user select component more than two geometry.
        '''
        geoList = list(set(cmds.ls(self.selVertices, objectsOnly=True)))
        return len(geoList) > 1

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
    def copySkinOverlapVertices(*args):
        meshes = cmds.filterExpand(cmds.ls(os=True), sm=12)
        skinUtil.copySkinOverlapVertices(meshes[0], meshes[1])


# ------------ Utils
def displayObjectColor(object='', use=True):
    sels = om.MSelectionList()
    sels = om.MGlobal.getActiveSelectionList() if not object else sels.add(object)
    assert sels.length() != 0, 'No object given to set color.'

    dagPath = sels.getDagPath(0)
    fnDag = om.MFnDagNode(dagPath)
    fnDag.objectColorRGB = OBJECT_COLOR
    fnDag.objectColorType = int(use) * 2  # Use object color type RGB when True


def rebind(*args):
    selGeos = cmds.filterExpand(cmds.ls(sl=True), sm=[9, 10, 12])
    for sel in selGeos:
        skinUtil.reBind(sel)


def updateBindPose(*args):
    sels = cmds.ls(sl=True, type='joint')
    if len(sels) == 1 and not cmds.listRelatives(sels[0], p=True):
        skinUtil.updateBindPose(sels[0])
    else:
        cmds.error('Please select a root joint.')


def colorFeedback(*args):
    colorFeedbackState = cmds.menuItem(swInstance.uiWidgets['colorFeedbackMenuItem'], q=True, checkBox=True)
    melStr = '''string $curCtx = `currentCtx`;\nartAttrCtx -e -colorfeedback ({}) $curCtx;'''.format(int(colorFeedbackState))
    mel.eval(melStr)
# ------------


# ------------ Selection
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
        vtxs.extend(skinUtil.getAffectedVertex(inf, MIN_WEIGHT))
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
# ------------



# ------------  Transfer Weights
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
    selInfs = cmds.textScrollList('infsTxtScrLs', q=True, selectItem=True)
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
# ------------


# ------------  Copy and Paste
def copySkin(*args):
    import takTools.common.tak_misc as tak_misc
    import imp; imp.reload(tak_misc)
    tak_misc.addInfCopySkin()


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


def copyPasteGUI(*args):
    cmds.window(title='Copy & Paste', tlb=True, p=WIN_NAME)
    cmds.rowLayout(numberOfColumns=2)
    cmds.button(label='Copy', c=lambda x: mel.eval('artAttrSkinWeightCopy;'))
    cmds.button(label='Paste', c=lambda x: mel.eval('artAttrSkinWeightPaste;'))
    cmds.showWindow()
# ------------


# ------------ Tools
def runBrSmoothWeights(*args):
    if not cmds.pluginInfo('brSmoothWeights', q=True, loaded=True):
        cmds.loadPlugin('brSmoothWeights')
    mel.eval('brSmoothWeightsToolCtx;')


def runHammerWeightsBrush(*args):
    weightHammerBrush = cmds.artSelectCtx(beforeStrokeCmd='select -cl;', afterStrokeCmd='if (size(`ls -sl`) > 0){WeightHammer;}')
    cmds.setToolTo(weightHammerBrush)


def runAverageWeightsBrush(*args):
    import takTools.rigging.averageVertexSkinWeightBrush as averageVertexSkinWeightBrush
    import imp; imp.reload(averageVertexSkinWeightBrush)
    averageVertexSkinWeightBrush.paint()
# ------------


# ------------ SSD
def ssdGUI(*args):
    cmds.window(title='SSD(Smooth Skin Decomposition)', tlb=True, p=WIN_NAME)
    cmds.columnLayout(adj=True)
    cmds.button(label='Decompose Skin', c=lambda x: skinUtil.SSD(cmds.ls(sl=True)[0]))
    cmds.showWindow()
# ------------


# ------------  Max Influences
def maxInfluencesGUI(*args):
    cmds.window(title='Max Influences Manager', h=10, tlb=True, p=WIN_NAME)
    cmds.columnLayout(adj=True)
    cmds.button(label='Check Max Influences', c=checkMaxInfluences)
    cmds.rowColumnLayout(numberOfColumns=2, columnSpacing=[(1, 2), (2, 2)])
    cmds.optionMenu('maxInfsOptMenu', label='Max Influences:')
    cmds.menuItem(label='4')
    cmds.menuItem(label='8')
    cmds.menuItem(label='12')
    cmds.optionMenu('maxInfsOptMenu', e=True, v='4')
    cmds.button(label='Set', c=fitMaxInfluence, w=50)
    cmds.showWindow()


def checkMaxInfluences(*args):
    meshes = cmds.filterExpand(cmds.ls(sl=True), sm=12)
    for mesh in meshes:
        maxInfs = SkinWeights.getMaxInfluences(mesh)
        print('"{}" Max Influences: {}'.format(mesh, maxInfs))


@decorators.printElapsedTime
def fitMaxInfluence(*args):
    for mesh in cmds.ls(sl=True):
        meshMaxInfs = SkinWeights.getMaxInfluences(mesh)
        targetMaxInfs = int(cmds.optionMenu('maxInfsOptMenu', q=True, v=True))
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
# ------------


# ------------ Skin I/O
def showSkinIOGUI(*args):
    cmds.window(title='Skin I/O', tlb=True, p=WIN_NAME)
    cmds.columnLayout(adj=True)
    cmds.textFieldButtonGrp('skinDirTxtFldBtnGrp', label='Skin Directory:', buttonLabel='...', bc=setDirectory)
    cmds.button(label='Import', c=lambda x: importSkin(cmds.textFieldButtonGrp('skinDirTxtFldBtnGrp', q=True, text=True)))
    cmds.button(label='Export', c=lambda x: exportSkin(cmds.textFieldButtonGrp('skinDirTxtFldBtnGrp', q=True, text=True)))
    cmds.showWindow()

def importSkin(skinDirectory, *args):
    for skinFile in os.listdir(skinDirectory):
        skinFilePath = os.path.join(skinDirectory, skinFile)
        if not os.path.isfile(skinFilePath):
            continue
        if not os.path.splitext(skinFilePath)[-1] == '.sw':
            continue

        print(os.path.join(skinDirectory, skinFile))
        skinUtil.loadBSkin(os.path.join(skinDirectory, skinFile))

def exportSkin(skinDirectory, *args):
    meshes = cmds.filterExpand(cmds.ls(sl=True), sm=12)
    if not meshes:
        return
    for mesh in meshes:
        skinUtil.saveBSkin(mesh, skinDirectory)

def setDirectory(*args):
    dir = cmds.fileDialog2(fm=3)
    if dir:
        cmds.textFieldButtonGrp('skinDirTxtFldBtnGrp', e=True, text=dir[0])
# ------------


def bSkinSaverGUI(*args):
    import takTools.rigging.bSkinSaver as bSkinSaver
    import imp; imp.reload(bSkinSaver)
    bSkinSaver.showUI()
