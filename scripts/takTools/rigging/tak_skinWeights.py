"""
Author: Sang-tak Lee
Website: ta-note.com
Created: 09/16/2015
Updated: 10/06/2020

Description:
You can assign specific numeric value to the selected vertices skin weights like using component editor.

Usage:
import tak_skinWeights
reload(tak_skinWeights)
tak_skinWeights.SkinWeights()
"""

from functools import partial

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import pymel.core as pm


class SkinWeights(object):
    vtxList = []
    uiWidgets = {}
    oriWeightTable = {}
    skinClst = ''
    infTxtScrLsCurrentAllItems = []

    @classmethod
    def __init__(cls):
        cls.uiWidgets['winName'] = 'takWeightsWin'

        if cmds.window(cls.uiWidgets['winName'], exists=True):
            cmds.deleteUI(cls.uiWidgets['winName'])

        # Show user interface
        cls.ui()

        # Create script job to populate influence text scroll list automatically
        cmds.scriptJob(parent=cls.uiWidgets['winName'], event=['SelectionChanged', cls.loadInf])

        # When window is closed call destructor function.
        cmds.scriptJob(uid=[cls.uiWidgets['winName'], cls.__del__])

    @classmethod
    def __del__(cls):
        if SkinWeights.infTxtScrLsCurrentAllItems:
            for inf in SkinWeights.infTxtScrLsCurrentAllItems:
                cls.unuseObjectColor(inf)
        SkinWeights.infTxtScrLsCurrentAllItems = []

    @classmethod
    def ui(cls):
        cmds.window(cls.uiWidgets['winName'], title='Tak Skin Weights Tool')

        cls.uiWidgets['mainMenuBarLo'] = cmds.menuBarLayout(p=cls.uiWidgets['winName'])
        cls.uiWidgets['editMenu'] = cmds.menu(p=cls.uiWidgets['mainMenuBarLo'], label='Edit')
        cls.uiWidgets['copyPasteMenuItem'] = cmds.menuItem(p=cls.uiWidgets['editMenu'], label='Copy and Paste', c=cls.copyPasteWeight, ann='Copy first selected vertex weights and paste the others.')
        cls.uiWidgets['hammerMenuItem'] = cmds.menuItem(p=cls.uiWidgets['editMenu'], label='Hammer', c="mel.eval('WeightHammer;')", ann='Set average weights with neighbor vertices.')
        cls.uiWidgets['mirrorMenuItem'] = cmds.menuItem(p=cls.uiWidgets['editMenu'], label='Mirror', c="mel.eval('MirrorSkinWeights;')", ann='Mirror skin weights positive X to negative X.')
        cls.uiWidgets['pruneMenuItem'] = cmds.menuItem(p=cls.uiWidgets['editMenu'], label='Prune Small Weights', c="mel.eval('PruneSmallWeights;')")
        cls.uiWidgets['rmvUnusedInfMenuItem'] = cmds.menuItem(p=cls.uiWidgets['editMenu'], label='Remove Unused Influences', c="mel.eval('removeUnusedInfluences;')")
        cls.uiWidgets['optMenu'] = cmds.menu(p=cls.uiWidgets['mainMenuBarLo'], label='Options')
        cls.uiWidgets['hideZroInfMenuItem'] = cmds.menuItem(p=cls.uiWidgets['optMenu'], checkBox=True,
                                                            label='Hide Zero Influences', c=cls.loadInf)
        cls.uiWidgets['sortHierMenuItem'] = cmds.menuItem(p=cls.uiWidgets['optMenu'], checkBox=False,
                                                          label='Sort by Hierarchy', c=cls.loadInf)

        cls.uiWidgets['mainColLo'] = cmds.columnLayout(p=cls.uiWidgets['winName'], adj=True)

        # Selection buttons layout
        cls.uiWidgets['selectRowLo'] = cmds.rowLayout(p=cls.uiWidgets['mainColLo'], nc=4)
        cls.uiWidgets['shrinkBtn'] = cmds.button(l='Shrink', w=70, c=lambda x: mel.eval('ShrinkPolygonSelectionRegion;'))
        cls.uiWidgets['growBtn'] = cmds.button(l='Grow', w=70, c=lambda x: mel.eval('GrowPolygonSelectionRegion;'))
        cls.uiWidgets['ringBtn'] = cmds.button(l='Ring', w=70, c=selectVtxRing)
        cls.uiWidgets['loopBtn'] = cmds.button(l='Loop', w=70, c=lambda x: mel.eval('polySelectSp -loop;'))

        cls.uiWidgets['mainTabLo'] = cmds.tabLayout(p=cls.uiWidgets['mainColLo'], tv=False)
        cls.uiWidgets['infWghtRowColLo'] = cmds.rowColumnLayout(p=cls.uiWidgets['mainTabLo'], numberOfColumns=2,
                                                                columnWidth=[(1, 140), (2, 140)],
                                                                columnSpacing=[(2, 5)])
        cls.uiWidgets['infFrmLo'] = cmds.frameLayout(p=cls.uiWidgets['infWghtRowColLo'], label='Influences')
        cls.uiWidgets['infTxtScrLs'] = cmds.textScrollList(p=cls.uiWidgets['infFrmLo'], h=200, sc=cls.infTxtScrLsSelCmd,
                                                           allowMultiSelection=True, append='Select a skined vertex(s)')
        cls.uiWidgets['infPopMenu'] = cmds.popupMenu(p=cls.uiWidgets['infTxtScrLs'])
        cls.uiWidgets['loadInfMenu'] = cmds.menuItem(p=cls.uiWidgets['infPopMenu'], label='Load Influences',
                                                     c=cls.loadInf)

        cls.uiWidgets['wghtFrmLo'] = cmds.frameLayout(p=cls.uiWidgets['infWghtRowColLo'], label='Weight Value')
        cls.uiWidgets['wghtTxtScrLs'] = cmds.textScrollList(p=cls.uiWidgets['wghtFrmLo'], h=200, enable=True,
                                                            allowMultiSelection=True)

        cls.uiWidgets['wghtPrsRowColLo'] = cmds.rowColumnLayout(p=cls.uiWidgets['mainColLo'], numberOfColumns=5,
                                                                columnWidth=[(1, 50), (2, 50), (3, 50), (4, 50),
                                                                             (5, 50)],
                                                                columnSpacing=[(1, 7), (2, 7), (3, 7), (4, 7), (5, 7)])
        cmds.button(p=cls.uiWidgets['wghtPrsRowColLo'], label='0', c=partial(cls.setWeight, 0.0))
        cmds.button(p=cls.uiWidgets['wghtPrsRowColLo'], label='0.25', c=partial(cls.setWeight, 0.25))
        cmds.button(p=cls.uiWidgets['wghtPrsRowColLo'], label='0.5', c=partial(cls.setWeight, 0.5))
        cmds.button(p=cls.uiWidgets['wghtPrsRowColLo'], label='0.75', c=partial(cls.setWeight, 0.75))
        cmds.button(p=cls.uiWidgets['wghtPrsRowColLo'], label='1', c=partial(cls.setWeight, 1.0))

        cls.uiWidgets['wghtSubAddRowColLo'] = cmds.rowColumnLayout(p=cls.uiWidgets['mainColLo'], numberOfColumns=4,
                                                                   columnWidth=[(1, 107), (2, 50), (3, 50), (4, 50)],
                                                                   columnSpacing=[(1, 7), (2, 7), (3, 7), (4, 7)])
        cmds.button(p=cls.uiWidgets['wghtSubAddRowColLo'], label='Set Custom Weight',
                    c=partial(cls.subAddWeight, 'default'))
        cls.uiWidgets['rltvWghtValfloatFld'] = cmds.floatField(p=cls.uiWidgets['wghtSubAddRowColLo'], v=0.050,
                                                               min=0.001, max=1.000, step=0.010, precision=3)
        cmds.button(p=cls.uiWidgets['wghtSubAddRowColLo'], label='-', c=partial(cls.subAddWeight, 'sub'))
        cmds.button(p=cls.uiWidgets['wghtSubAddRowColLo'], label='+', c=partial(cls.subAddWeight, 'add'))

        cls.uiWidgets['wghtTrsfRowColLo'] = cmds.rowColumnLayout(p=cls.uiWidgets['mainColLo'], numberOfColumns=4,
                                                                 columnWidth=[(1, 93), (2, 20), (3, 93), (4, 50)],
                                                                 columnSpacing=[(1, 7), (2, 7), (3, 7), (4, 7)])
        cls.uiWidgets['srcInfTxtFld'] = cmds.textField(p=cls.uiWidgets['wghtTrsfRowColLo'])
        cmds.popupMenu()
        cmds.menuItem(label='Load Selected Influence', c=partial(cls.loadSelInf, cls.uiWidgets['srcInfTxtFld']))
        cmds.text(p=cls.uiWidgets['wghtTrsfRowColLo'], label='>>>')
        cls.uiWidgets['trgInfTxtFld'] = cmds.textField(p=cls.uiWidgets['wghtTrsfRowColLo'])
        cmds.popupMenu()
        cmds.menuItem(label='Load Selected Influence', c=partial(cls.loadSelInf, cls.uiWidgets['trgInfTxtFld']))
        cmds.button(p=cls.uiWidgets['wghtTrsfRowColLo'], label='Transfer', c=cls.transferWeights)

        cls.uiWidgets['maxInfRowColLo'] = cmds.rowColumnLayout(p=cls.uiWidgets['mainColLo'], numberOfColumns=3, columnSpacing=[(1, 2), (2, 2), (3, 2)])
        cmds.button(p=cls.uiWidgets['maxInfRowColLo'], label='Check Max Influences', c=cls.getMaxInfluence)
        cls.uiWidgets['maxInfsOptMenu'] = cmds.optionMenu(p=cls.uiWidgets['maxInfRowColLo'], label='Max Influences:')
        cmds.menuItem(label='4')
        cmds.menuItem(label='8')
        cmds.menuItem(label='12')
        cmds.optionMenu(cls.uiWidgets['maxInfsOptMenu'], e=True, v='8')
        cmds.button(p=cls.uiWidgets['maxInfRowColLo'], label='Set', c=cls.fitMaxInfluence, w=50)

        cmds.window(cls.uiWidgets['winName'], e=True, w=100, h=200)
        cmds.showWindow(cls.uiWidgets['winName'])

    @classmethod
    def loadInf(cls, *args):
        '''
        Main method.
        Populate influence and weight value text scroll list.
        '''

        cmds.undoInfo(openChunk=True)

        # Deactivate influences object color
        if SkinWeights.infTxtScrLsCurrentAllItems:
            for inf in SkinWeights.infTxtScrLsCurrentAllItems:
                cls.unuseObjectColor(inf)

        cmds.undoInfo(closeChunk=True)

        # Get options
        hideZroInfOpt = cmds.menuItem(cls.uiWidgets['hideZroInfMenuItem'], q=True, checkBox=True)
        hierSortOpt = cmds.menuItem(cls.uiWidgets['sortHierMenuItem'], q=True, checkBox=True)

        cls.vtxList = cmds.ls(sl=True)

        # Check selection error
        geoChkResult = cls.checkGeoNum()
        if not '.' in str(cls.vtxList) or not geoChkResult:
            cls.userFeedback()
            return

        # Get skin cluster from selected vertex
        cls.getSkinClst(cls.vtxList[0])
        if not cls.skinClst:
            cls.userFeedback()
            return

        # Get influences
        infs = cmds.skinCluster(cls.skinClst, q=True, inf=True)

        # Make influences weight value table
        cls.skinWeightTable(cls.skinClst, cls.vtxList, infs)

        # Hide zero weighted influences depend on option state
        if hideZroInfOpt:
            rmvedZroWghtTable = cls.hideZeroWghtInfs()
            infs = rmvedZroWghtTable.keys()

        # Sorting
        if hierSortOpt:
            infs = cls.sortByHierarchy(infs)
        else:
            infs = cls.sortByAlphabetically(infs)

        # Populate text scroll list
        cls.populateInfList(infs)
        cls.populateWghtList(infs)

    @classmethod
    def getSkinClst(cls, vtx):
        '''
        Get skin cluster with a vertex.
        '''

        geo = vtx.split('.')[0]

        cls.skinClst = mel.eval('findRelatedSkinCluster "%s";' % geo)

    @classmethod
    def skinWeightTable(cls, skinClst, vtxList, infs):
        '''
        Make skin influences weight table.
        '''
        cls.oriWeightTable = {}

        # Initialize original weight value table
        for inf in infs:
            cls.oriWeightTable[inf] = str(0.0) + '   ' + inf

        # Replace initialized value if not value is 0
        for inf in infs:
            for vtx in vtxList:
                infWeightVal = cmds.skinPercent(skinClst, vtx, q=True, transform=inf)
                if not infWeightVal == 0.0:
                    cls.oriWeightTable[inf] = str(round(infWeightVal, 4)) + '   ' + inf
                else:
                    continue


    @classmethod
    def populateInfList(cls, infs):
        '''
        Populate influences text scroll list.
        '''

        items = cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], q=True, allItems=True)
        selItems = cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], q=True, selectItem=True)
        if items:
            cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], e=True, removeAll=True)
        cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], e=True, append=infs)

        cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], e=True, selectItem=selItems)

    @classmethod
    def populateWghtList(cls, infs):
        '''
        Populate weight value for each influence.
        '''

        items = cmds.textScrollList(cls.uiWidgets['wghtTxtScrLs'], q=True, allItems=True)
        if items:
            cmds.textScrollList(cls.uiWidgets['wghtTxtScrLs'], e=True, removeAll=True)
        for inf in infs:
            cmds.textScrollList(cls.uiWidgets['wghtTxtScrLs'], e=True, append=cls.oriWeightTable[inf])

    @classmethod
    def hideZeroWghtInfs(cls, *args):
        '''
        Hide zero weights value influences in the list.
        '''
        # Initialize data
        rmvZroWghtTable = {}

        for inf in cls.oriWeightTable.keys():
            if float(cls.oriWeightTable[inf].split(' ')[0]) < 0.0001:
                continue
            else:
                rmvZroWghtTable[inf] = cls.oriWeightTable[inf]


        return rmvZroWghtTable

    @classmethod
    def setWeight(cls, weightVal, mode='default', *args):
        '''
        Set weight value with given value.
        '''

        # Get selected influence
        selInfList = cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], q=True, selectItem=True)

        # for vtx in cls.vtxList:
        #     for selInf in selInfList:
        #         if mode == 'sub':
        #             cmds.skinPercent(cls.skinClst, vtx, transformValue=[(selInf, -weightVal)], prw=0, relative=True)
        #         elif mode == 'add':
        #             cmds.skinPercent(cls.skinClst, vtx, transformValue=[(selInf, weightVal)], prw=0, relative=True)
        #         else:
        #             cmds.skinPercent(cls.skinClst, vtx, transformValue=[(selInf, weightVal)], prw=0)
        for selInf in selInfList:
            if mode == 'sub':
                cmds.skinPercent(cls.skinClst, cls.vtxList, transformValue=[(selInf, -weightVal)], prw=0, relative=True)
            elif mode == 'add':
                cmds.skinPercent(cls.skinClst, cls.vtxList, transformValue=[(selInf, weightVal)], prw=0, relative=True)
            else:
                cmds.skinPercent(cls.skinClst, cls.vtxList, transformValue=[(selInf, weightVal)], prw=0)

        cls.loadInf()
        cls.infTxtScrLsSelCmd()

    @classmethod
    def subAddWeight(cls, mode, *args):
        '''
        Subtract or Add weight value for selected influence.
        '''

        weightVal = cmds.floatField(cls.uiWidgets['rltvWghtValfloatFld'], q=True, v=True)

        cls.setWeight(weightVal, mode)

    @classmethod
    def sortByHierarchy(cls, infs, *args):
        '''
        Sorting influences order by hierarchy depend on option.
        '''

        allInfList = cmds.skinCluster(cls.skinClst, q=True, inf=True)
        hierSortInfList = []

        for inf in allInfList:
            if inf in infs:
                hierSortInfList.append(inf)
            else:
                continue

        return hierSortInfList

    @classmethod
    def sortByAlphabetically(cls, infs, *args):
        '''
        Sorting influences order by alphanetically depend on option.
        '''

        alphSortList = sorted(infs)

        return alphSortList

    @classmethod
    def infTxtScrLsSelCmd(cls, *args):
        """ Select matching weight value in weight value text scroll list """

        allInfs = cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], q=True, allItems=True)
        selInfList = cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], q=True, selectItem=True)

        SkinWeights.infTxtScrLsCurrentAllItems = allInfs

        cmds.textScrollList(cls.uiWidgets['wghtTxtScrLs'], e=True, deselectAll=True)
        selInfWghtList = []

        if selInfList:
            for selInf in selInfList:
                matchingWeightVal = cls.oriWeightTable[selInf]
                selInfWghtList.append(matchingWeightVal)
                wghtVal = cls.oriWeightTable[selInf].split(' ')[0]

            cls.changeSelInfCol(allInfs, selInfList)

    @classmethod
    def changeSelInfCol(cls, allInfs, selInfList):
        for inf in allInfs:
            cls.unuseObjectColor(inf)

        for selInf in selInfList:
            cls.useObjectColor(selInf)

    @staticmethod
    def unuseObjectColor(inf):
        infNode = pm.PyNode(inf)
        infNode.setObjectColor(0)

    @staticmethod
    def useObjectColor(inf):
        infNode = pm.PyNode(inf)
        infNode.setObjectColor(8)

    @classmethod
    def userFeedback(cls):
        """ Annotation when user did not select a vertex """

        # Remove items in influences text scroll list
        items = cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], q=True, allItems=True)
        if items:
            cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], e=True, removeAll=True)
        cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], e=True, append='Select a skined vertex(s)')

        # Remove items in weight value text scroll list
        items = cmds.textScrollList(cls.uiWidgets['wghtTxtScrLs'], q=True, allItems=True)
        if items:
            cmds.textScrollList(cls.uiWidgets['wghtTxtScrLs'], e=True, removeAll=True)

    @classmethod
    def checkGeoNum(cls):
        '''
        Check if user select component more than two geometry.
        '''

        geoList = []

        for vtx in cls.vtxList:
            geo = vtx.split('.')[0]
            if not geo in geoList:
                geoList.append(geo)

        if len(geoList) >= 2:
            cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], e=True, removeAll=True)
            cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], e=True, append='Select vertex of one object')
            return False
        else:
            return True

    @classmethod
    def loadSelInf(cls, wgt, *arg):
        '''
        Load selected influence that in the influences text scroll list.
        '''

        selInf = cmds.textScrollList(cls.uiWidgets['infTxtScrLs'], q=True, selectItem=True)
        cmds.textField(wgt, e=True, text=selInf[0])

    @classmethod
    def transferWeights(cls, *args):
        vtxList = cmds.ls(sl=True, fl=True)

        srcInf = cmds.textField(cls.uiWidgets['srcInfTxtFld'], q=True, text=True)
        trgInf = cmds.textField(cls.uiWidgets['trgInfTxtFld'], q=True, text=True)

        for vtx in vtxList:
            # get skin weight value
            srcInfSkinVal = cmds.skinPercent(cls.skinClst, vtx, transform=srcInf, query=True)
            trgInfSkinVal = cmds.skinPercent(cls.skinClst, vtx, transform=trgInf, query=True)

            resultSkinVal = srcInfSkinVal + trgInfSkinVal

            # transfer skin weights
            cmds.skinPercent(cls.skinClst, vtx, transformValue=[(srcInf, 0), (trgInf, resultSkinVal)], nrm=True)

        # Refresh influence text scroll list.
        cls.loadInf()

    @classmethod
    def getMaxInfluence(cls, *args, mesh=None, printResult=True, ignoreWeight=0.00001):
        if not mesh:
            mesh = cmds.ls(sl=True)[0]
        skinClst = mel.eval('findRelatedSkinCluster("{}");'.format(mesh))
        vertCount = cmds.polyEvaluate(mesh, v=True)
        numInfsPerVtx = []
        for i in range(vertCount):
            numInfsPerVtx.append(len(cmds.skinPercent(skinClst, '{}.vtx[{}]'.format(mesh, i), q=True, ignoreBelow=ignoreWeight, v=True)))
        maxInf = max(numInfsPerVtx)
        if printResult:
            print('"{}" Max Influence: {}'.format(mesh, maxInf))
        return maxInf

    @classmethod
    def fitMaxInfluence(cls, *args, ignoreWeight=0.00001):
        for mesh in cmds.ls(sl=True):
            meshMaxInfs = cls.getMaxInfluence(mesh=mesh, printResult=False)
            targetMaxInfs = int(cmds.optionMenu(cls.uiWidgets['maxInfsOptMenu'], q=True, v=True))
            if meshMaxInfs <= targetMaxInfs:
                print('"{}"s max influence is {}. Skip processing.'.format(mesh, meshMaxInfs))
                continue

            # Create progress window
            cmds.window('progWin', title='working on "{}"'.format(mesh), mnb=False, mxb=False)
            cmds.columnLayout(adj=True)
            cmds.progressBar('progBar', w=400, isMainProgressBar=True, beginProgress=True, isInterruptable=True)
            cmds.showWindow('progWin')

            skinClst = mel.eval('findRelatedSkinCluster("{}");'.format(mesh))

            # Optimize weights and influences to speed up processing
            cmds.skinPercent(skinClst, mesh, pruneWeights=0.001)
            cmds.skinCluster(skinClst, e=True, removeUnusedInfluence=True)

            # Set max influences for a skin cluster
            cmds.setAttr("{}.maintainMaxInfluences".format(skinClst), True)
            cmds.setAttr("{}.maxInfluences".format(skinClst), targetMaxInfs)

            vertCount = cmds.polyEvaluate(mesh, v=True)
            cmds.progressBar('progBar', e=True, min=0, max=vertCount)
            for i in range(vertCount):
                if cmds.progressBar('progBar', q=True, isCancelled=True):
                    print('Fitting max influence job for a "{}" is cancelled.'.format(mesh))
                    break
                vert = '{}.vtx[{}]'.format(mesh, i)
                weights = cmds.skinPercent(skinClst, vert, q=True, ignoreBelow=ignoreWeight, v=True)
                infs = cmds.skinPercent(skinClst, vert, q=True, ignoreBelow=ignoreWeight, transform=None)
                itemsToRemove = sorted(zip(weights, infs), reverse=True)[targetMaxInfs:]
                weightsForRemoveInfs = [(item[1], 0.0) for item in itemsToRemove]
                cmds.skinPercent(skinClst, vert, transformValue=weightsForRemoveInfs)
                cmds.progressBar('progBar', e=True, step=1)
            print('Fitting max influence for a "{}" is done.'.format(mesh))

            cmds.progressBar('progBar', e=True, endProgress=True)
            cmds.deleteUI('progWin')

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
    def smoothSkinWeights(*args):
        selLs = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selLs)
        selShape = om.MDagPath()
        selLs.getDagPath(0, selShape)
        selShape.extendToShape()
        skinClst = SkinWeights.getSkinCluster(selShape)

        vtxIt = om.MItMeshVertex(selShape)
        neighborVtxs = om.MIntArray()
        singleIndexComponentFn = om.MFnSingleIndexedComponent()
        weights = om.MDoubleArray()
        util = om.MScriptUtil()
        numInf = util.asUintPtr()
        influenceIndices = om.MIntArray()
        while not vtxIt.isDone():
            weightsList = []
            vtxIt.getConnectedVertices(neighborVtxs)
            for vtxId in neighborVtxs:
                component = singleIndexComponentFn.create(om.MFn.kMeshVertComponent)
                singleIndexComponentFn.addElement(vtxId)
                skinClst.getWeights(selShape, component, weights, numInf)
                weightsList.append(weights)
            averageWeights = [item/len(neighborVtxs) for item in map(sum, zip(*weightsList))]
            skinClst.setWeights(selShape,
                                vtxIt.currentItem(),
                                createIntArrayFromList(range(util.getUint(numInf))),
                                createDoubleArrayFromList(averageWeights))
            vtxIt.next()

    @staticmethod
    def getSkinCluster(shape):
        """
        Parameters:
            shape<MDagPath>: Shape dag path
        """
        dgIt = om.MItDependencyGraph(shape.node(), om.MFn.kSkinClusterFilter, om.MItDependencyGraph.kUpstream)
        skinClst = None
        while not dgIt.isDone():
            skinClst = oma.MFnSkinCluster(dgIt.currentItem())
            dgIt.next()
        return skinClst



def createIntArrayFromList(list):
    intArray = om.MIntArray()
    for item in list:
        intArray.append(item)
    return intArray


def createDoubleArrayFromList(list):
    doubleArray = om.MDoubleArray()
    for item in list:
        doubleArray.append(item)
    return doubleArray


def selectVtxRing(*args):
    mel.eval('PolySelectConvert 20;')
    mel.eval('polySelectSp -ring;')
    mel.eval('PolySelectConvert 3;')
