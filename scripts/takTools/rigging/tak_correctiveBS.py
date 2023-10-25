'''
Author: TAK
Website: ta-note.com
Create Date: 05/14/2015
Latest Update: 11/24/2021

Description:
This script for creating and managing corrective shapes.

Usage:
import tak_correctiveBS
reload(tak_correctiveBS)
tak_correctiveBS.UI()
'''

import re
from functools import partial

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.OpenMaya as OpenMaya

from ..common import tak_lib


# ----------------------------------------------------------------
# Utils
# ----------------------------------------------------------------
def findMultiAttributeEmptyIndex(node, attribute):
    """
    Find available index of multi attribute.
    Args:
        node (string): Node name.
        attribute (string): Attribute name

    Returns:
        Available index
    """
    node = pm.PyNode(node)
    id = 0
    while node.attr(attribute)[id].isConnected():
        id += 1
    return id

def getShape(transform):
    shape = None
    shapes = cmds.listRelatives(transform, s=True, ad=True, ni=True)
    if shapes:
        shape = shapes[0]
    return shape


# ----------------------------------------------------------------
# UI Class
# ----------------------------------------------------------------
class UI(object):
    widgets = {}
    winName = 'takCorrectiveUI'


    @classmethod
    def __init__(cls):
        if cmds.window(cls.winName, exists = True):
            cmds.deleteUI(cls.winName)

        if cmds.window('reNameWin', exists = True):
            cmds.deleteUI('reNameWin')

        cls.ui()


    @classmethod
    def ui(cls):
        cmds.window(cls.winName, title = 'Corrective Blend Shape Tool', menuBar = True)

        cls.widgets['createMenu'] = cmds.menu(label = 'Create', tearOff = True, p = cls.winName)
        cls.widgets['addBsMenuItem'] = cmds.menuItem(label = 'Add Blend Shape Node', c = Functions.addBsNode)
        cls.widgets['addTrgMenuItem'] = cmds.menuItem(label = 'Add Selected Targets', c = Functions.addTrg)

        cls.widgets['editMenu'] = cmds.menu(label = 'Edit', tearOff = True, p = cls.winName)
        cls.widgets['selBsMenuItem'] = cmds.menuItem(label = 'Select Blend Shape Node', c = Functions.selBsNode)
        cls.widgets['renameBsMenuItem'] = cmds.menuItem(label = 'Rename Blend Shape Node', c = Functions.renameBsNode)

        cls.widgets['helpMenu'] = cmds.menu(label = 'Help', tearOff = True, p = cls.winName)

        cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)

        cmds.separator(h = 5, p = cls.widgets['mainColLo'])

        cls.widgets['baseGeoRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 3)
        cmds.text(label = 'Base Geometry: ', p = cls.widgets['baseGeoRowColLo'])
        cls.widgets['baseGeoTxtFld'] = cmds.textField(p = cls.widgets['baseGeoRowColLo'])
        cmds.button(label = '<<', p = cls.widgets['baseGeoRowColLo'], c = Functions.loadGeoBS)

        cls.widgets['bsNodeRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, p = cls.widgets['mainColLo'])
        cmds.text(label = 'Blend Shape Node: ', p = cls.widgets['bsNodeRowColLo'])
        cls.widgets['bsNodeOptMenu'] = cmds.optionMenu(cc = Functions.populateCorrectiveTrgList, p = cls.widgets['bsNodeRowColLo'])

        cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

        cls.widgets['correctiveTrgNameRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnSpacing = [(3, 30)], p = cls.widgets['mainColLo'])
        cmds.text(label = 'New Corrective: ', p = cls.widgets['correctiveTrgNameRowColLo'])
        cls.widgets['correctiveTrgNameTxtFld'] = cmds.textField(p = cls.widgets['correctiveTrgNameRowColLo'])
        cmds.popupMenu()
        cmds.menuItem(label = 'Load Selected', c = partial(Functions.loadSel, cls.widgets['correctiveTrgNameTxtFld']))
        cmds.text(label = 'SymVtxSrch Tolerance: ', p = cls.widgets['correctiveTrgNameRowColLo'])
        cls.widgets['symVtxSrchTolFlFld'] = cmds.floatField(v = 0.001, p = cls.widgets['correctiveTrgNameRowColLo'], annotation = 'If caused error on symmetry functions \nthen try again with higher number about 0.005 ~ 0.01')


        cls.widgets['scltBtnRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 205), (2, 205)], columnSpacing = [(2, 5)], p = cls.widgets['mainColLo'])
        cls.widgets['sclptBtn'] = cmds.button(label = 'Sculpt', p = cls.widgets['scltBtnRowColLo'], c = Functions.sculptMode)
        cls.widgets['cancelBtn'] = cmds.button(label = 'Cancel', enable = False, p = cls.widgets['scltBtnRowColLo'], c = Functions.cancelSculpt)
        cls.widgets['createBtn'] = cmds.button(label = 'Done', enable = False, h = 40, p = cls.widgets['mainColLo'], c = partial(Functions.createCorrectiveTarget, 'create'))

        cmds.separator(h = 5, style = 'none', p = cls.widgets['mainColLo'])

        cls.widgets['correctiveTrgFrmLo'] = cmds.frameLayout(label = 'Target Shape List', collapsable = True, p = cls.widgets['mainColLo'])
        cls.widgets['correctiveTrgColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['correctiveTrgFrmLo'])
        cls.widgets['correctiveTrgRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 350), (2, 60)])
        cls.widgets['correctiveTrgTxtScrList'] = cmds.textScrollList(allowMultiSelection = True, p = cls.widgets['correctiveTrgRowColLo'], sc = Functions.correctiveTrgListSelCmd)
        cmds.popupMenu(postMenuCommand = Functions.popupMenuCmd)
        cmds.menuItem(label = 'Refresh List', c = Functions.populateCorrectiveTrgList)
        cls.widgets['popMenuRename'] = cmds.menuItem(label = 'Rename', c = Functions.renameUI, enable = False)
        cmds.menuItem(divider = True)
        cls.widgets['popMenuEdit'] = cmds.menuItem(label = 'Edit', c = Functions.trgListEidtCmd, enable = False)
        cls.widgets['popMenuCombo'] = cmds.menuItem(label = 'Combo', c = Functions.trgListComboCmd, enable = False)
        cmds.menuItem(divider = True)
        cls.widgets['popupMenuSplit'] = cmds.menuItem(label = 'Split L/R', c = Functions.splitLR, enable = False)
        cls.widgets['popMenuMerge'] = cmds.menuItem(label = 'Merge Selected', c = Functions.mergeTrg, enable = False)
        cls.widgets['popMenuFlip'] = cmds.menuItem(label = 'Flip', c = Functions.flip, enable = False)
        cls.widgets['popMenuMirror'] = cmds.menuItem(label = 'Mirror', c = Functions.mirror, enable = False)
        cls.widgets['popMenuOpSite'] = cmds.menuItem(label = 'Create Opposite', c = Functions.createOppositeUI, enable = True)
        cls.widgets['popMenuDup'] = cmds.menuItem(label = 'Duplicate', c = Functions.dupTrg, enable = False)
        cls.widgets['popMenuExtractMesh'] = cmds.menuItem(label = 'Extract Mesh', c = Functions.extractMesh, enable = True)
        cmds.menuItem(divider = True)
        cls.widgets['popMenuSetToCurPose'] = cmds.menuItem(label = 'Set to Current Pose', c = Functions.setToCurPose, enable = True)
        cls.widgets['popMenuPreInf'] = cmds.menuItem(subMenu = True, label = 'Pre Infinity', enable = False)
        cls.widgets['popMenuPreInfCnst'] = cmds.menuItem(label = 'Constant', c = Functions.preInfCnst, enable = True)
        cls.widgets['popMenuPreInfCyc'] = cmds.menuItem(label = 'Cycle with Offset', c = Functions.preInfCyc, enable = True)
        cmds.setParent('..', menu = True)
        cls.widgets['popMenuPostInf'] = cmds.menuItem(subMenu = True, label = 'Post Infinity', enable = False)
        cls.widgets['popMenuPostInfCnst'] = cmds.menuItem(label = 'Constant', c = Functions.postInfCnst, enable = True)
        cls.widgets['popMenuPostInfCyc'] = cmds.menuItem(label = 'Cycle with Offset', c = Functions.postInfCyc, enable = True)
        cmds.setParent('..', menu = True)
        cmds.menuItem(divider = True)
        cls.widgets['popMenuBreak'] = cmds.menuItem(label = 'Break Connection', c = Functions.breakConnect, enable = False)
        cls.widgets['popMenuRmv'] = cmds.menuItem(label = 'Remove', c = Functions.removeTrg)

        cls.widgets['correctiveTrgWgtScrLo'] = cmds.scrollLayout(p = cls.widgets['correctiveTrgRowColLo'])

        cls.widgets['slderRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 370)], p = cls.widgets['correctiveTrgColLo'])
        cls.widgets['trgFltSldrGrp'] = cmds.floatSliderGrp(field = True, columnWidth = [(1, 30)], min = 0.00, max = 1.00, step = 0.01, dc = Functions.trgSldrDragCmd, cc = Functions.trgSldrDragCmd, enable = True, p = cls.widgets['slderRowColLo'])
        cmds.symbolButton(image = 'setKeyframe.png', c = Functions.setKey, p = cls.widgets['slderRowColLo'])

        cls.widgets['shpDrvrFrmLo'] = cmds.frameLayout(label = 'Shape Driver', collapse = True, collapsable = True, p = cls.widgets['mainColLo'])

        # create tab
        cls.widgets['shpDrvrTab'] = cmds.tabLayout(p = cls.widgets['shpDrvrFrmLo'])
        cls.widgets['posRdrTab'] = cmds.columnLayout(adj = True, p = cls.widgets['shpDrvrTab'])
        cls.widgets['sdkTab'] = cmds.columnLayout(adj = True, p = cls.widgets['shpDrvrTab'])
        cls.widgets['distTab'] = cmds.columnLayout(adj = True, p = cls.widgets['shpDrvrTab'])
        cls.widgets['cbTab'] = cmds.columnLayout(adj = True, p = cls.widgets['shpDrvrTab'])
        cmds.tabLayout(cls.widgets['shpDrvrTab'], e = True, tabLabel = [(cls.widgets['sdkTab'], 'Set Driven Key'), (cls.widgets['posRdrTab'], 'Pose Reader'), (cls.widgets['distTab'], 'Distance'), (cls.widgets['cbTab'], 'Combo')])

        cls.widgets['sdkDrvrFrmLo'] = cmds.frameLayout(label = 'Driver', p = cls.widgets['sdkTab'])
        cls.widgets['sdkDrvrColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['sdkDrvrFrmLo'])
        cls.widgets['sdkDrvrRowColLo'] = cmds.rowColumnLayout(w = 300, numberOfColumns = 4, columnWidth = [(1, 50), (2, 250), (3, 40), (4, 50)], columnAttach = [(1, 'left', 10), (4, 'right', 5)], bgc = [0.5, 0.5, 0.5], p = cls.widgets['sdkDrvrColLo'])
        cmds.text(label = 'Object', p = cls.widgets['sdkDrvrRowColLo'])
        cmds.text(label = 'Attribute', p = cls.widgets['sdkDrvrRowColLo'])
        cmds.text(label = 'Start', p = cls.widgets['sdkDrvrRowColLo'])
        cmds.text(label = 'End', p = cls.widgets['sdkDrvrRowColLo'])
        cls.widgets['sdkDrvrSclLo'] = cmds.scrollLayout(h = 100, p = cls.widgets['sdkDrvrColLo'])
        cls.widgets['sdkDrvnFrmLo'] = cmds.frameLayout(label = 'Driven', p = cls.widgets['sdkTab'])
        cls.widgets['sdkDrvnColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['sdkDrvnFrmLo'])
        cls.widgets['sdkDrvnRowColLo'] = cmds.rowColumnLayout(w = 300, numberOfColumns = 4, columnWidth = [(1, 50), (2, 250), (3, 40), (4, 50)], columnAttach = [(1, 'left', 10), (4, 'right', 5)], bgc = [0.5, 0.5, 0.5], p = cls.widgets['sdkDrvnColLo'])
        cmds.text(label = 'Object', p = cls.widgets['sdkDrvnRowColLo'])
        cmds.text(label = 'Attribute', p = cls.widgets['sdkDrvnRowColLo'])
        cmds.text(label = 'Start', p = cls.widgets['sdkDrvnRowColLo'])
        cmds.text(label = 'End', p = cls.widgets['sdkDrvnRowColLo'])
        cls.widgets['sdkDrvnSclLo'] = cmds.scrollLayout(h = 100, p = cls.widgets['sdkDrvnColLo'])
        cls.widgets['sdkBtnRowColLo'] = cmds.rowColumnLayout(w = 300, numberOfColumns = 4, columnWidth = [(1, 105), (2, 105), (3, 105), (4, 97)], p = cls.widgets['sdkTab'])
        cmds.button(label = 'Load Driver', p = cls.widgets['sdkBtnRowColLo'], c = partial(Functions.loadDriver, cls.widgets['sdkDrvrSclLo']))
        cmds.button(label = 'Load Driven', p = cls.widgets['sdkBtnRowColLo'], c = partial(Functions.loadDriven, cls.widgets['sdkDrvnSclLo']))
        cmds.button(label = 'Add Driven', p = cls.widgets['sdkBtnRowColLo'], c = partial(Functions.addDriven, cls.widgets['sdkDrvnSclLo']))
        cmds.button(label = 'Key', p = cls.widgets['sdkBtnRowColLo'], c = Functions.sdk)

        cls.widgets['poseReaderRadioBtnGrp'] = cmds.radioButtonGrp(label = 'Type: ', labelArray2=['RBF', 'Angle'], numberOfRadioButtons=2, select = 2, columnWidth=[(1, 30), (2, 50)], p = cls.widgets['posRdrTab'])
        cls.widgets['drvrJntTexBtnGrp'] = cmds.textFieldButtonGrp(label = 'Driver: ', buttonLabel = '<<', columnWidth = [(1, 80), (2, 120), (3, 50)], p = cls.widgets['posRdrTab'])
        cmds.textFieldButtonGrp(cls.widgets['drvrJntTexBtnGrp'], e = True, bc = partial(Functions.loadSel, cls.widgets['drvrJntTexBtnGrp']))
        cls.widgets['childJointTexBtnGrp'] = cmds.textFieldButtonGrp(label = 'Child: ', buttonLabel = '<<', columnWidth = [(1, 80), (2, 120), (3, 50)], p = cls.widgets['posRdrTab'])
        cmds.textFieldButtonGrp(cls.widgets['childJointTexBtnGrp'], e = True, bc = partial(Functions.loadSel, cls.widgets['childJointTexBtnGrp']))
        cls.widgets['prntJointTexBtnGrp'] = cmds.textFieldButtonGrp(label = 'Parent: ', buttonLabel = '<<', columnWidth = [(1, 80), (2, 120), (3, 50)], p = cls.widgets['posRdrTab'])
        cmds.textFieldButtonGrp(cls.widgets['prntJointTexBtnGrp'], e = True, bc = partial(Functions.loadSel, cls.widgets['prntJointTexBtnGrp']))
        cmds.text(label = 'Make sure that select a target in Target Shape List.\nGo to the pose then apply.', align = 'left', p = cls.widgets['posRdrTab'])
        cmds.button(label = 'Apply', h = 30, c = Functions.poseReader, p = cls.widgets['posRdrTab'])

        cls.widgets['drvrObjTexBtnGrp'] = cmds.textFieldButtonGrp(label = 'Driver Object: ', buttonLabel = '<<', columnWidth = [(1, 80), (2, 120), (3, 50)], p = cls.widgets['distTab'])
        cmds.textFieldButtonGrp(cls.widgets['drvrObjTexBtnGrp'], e = True, bc = partial(Functions.loadSel, cls.widgets['drvrObjTexBtnGrp']))
        cmds.text(label = 'Make sure that select a target in Target Shape List.\nGo to the pose then apply.', align = 'left', p = cls.widgets['distTab'])
        cmds.button(label = 'Apply', h = 30, c = Functions.distDrvr, p = cls.widgets['distTab'])

        # Combo Tab
        cls.widgets['cbDrvrFrmLo'] = cmds.frameLayout(label = 'Driver', p = cls.widgets['cbTab'])
        cls.widgets['cbDrvrColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['cbDrvrFrmLo'])
        cls.widgets['cbDrvrRowColLo'] = cmds.rowColumnLayout(w = 300, numberOfColumns = 4, columnWidth = [(1, 50), (2, 250), (3, 40), (4, 50)], columnAttach = [(1, 'left', 10), (4, 'right', 5)], bgc = [0.5, 0.5, 0.5], p = cls.widgets['cbDrvrColLo'])
        cmds.text(label = 'Object', p = cls.widgets['cbDrvrRowColLo'])
        cmds.text(label = 'Attribute', p = cls.widgets['cbDrvrRowColLo'])
        cmds.text(label = 'Start', p = cls.widgets['cbDrvrRowColLo'])
        cmds.text(label = 'End', p = cls.widgets['cbDrvrRowColLo'])
        cls.widgets['cbDrvrSclLo'] = cmds.scrollLayout(h = 100, p = cls.widgets['cbDrvrColLo'])
        cls.widgets['cbDrvnFrmLo'] = cmds.frameLayout(label = 'Driven', p = cls.widgets['cbTab'])
        cls.widgets['cbDrvnColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['cbDrvnFrmLo'])
        cls.widgets['cbDrvnRowColLo'] = cmds.rowColumnLayout(w = 300, numberOfColumns = 4, columnWidth = [(1, 50), (2, 250), (3, 40), (4, 50)], columnAttach = [(1, 'left', 10), (4, 'right', 5)], bgc = [0.5, 0.5, 0.5], p = cls.widgets['cbDrvnColLo'])
        cmds.text(label = 'Object', p = cls.widgets['cbDrvnRowColLo'])
        cmds.text(label = 'Attribute', p = cls.widgets['cbDrvnRowColLo'])
        cmds.text(label = 'Start', p = cls.widgets['cbDrvnRowColLo'])
        cmds.text(label = 'End', p = cls.widgets['cbDrvnRowColLo'])
        cls.widgets['cbDrvnSclLo'] = cmds.scrollLayout(h = 100, p = cls.widgets['cbDrvnColLo'])
        cls.widgets['cbBtnRowColLo'] = cmds.rowColumnLayout(w = 300, numberOfColumns = 4, columnWidth = [(1, 105), (2, 105), (3, 105), (4, 97)], p = cls.widgets['cbTab'])
        cmds.button(label = 'Load Driver', p = cls.widgets['cbBtnRowColLo'], c = partial(Functions.loadDriver, cls.widgets['cbDrvrSclLo']))
        cmds.button(label = 'Add Driver', p = cls.widgets['cbBtnRowColLo'], c = partial(Functions.addDriven, cls.widgets['cbDrvrSclLo']))
        cmds.button(label = 'Load Driven', p = cls.widgets['cbBtnRowColLo'], c = partial(Functions.loadDriven, cls.widgets['cbDrvnSclLo']))
        cmds.button(label = 'Connect', p = cls.widgets['cbBtnRowColLo'], c = Functions.connectCb)

        cmds.window(cls.winName, e = True, w = 400, h = 300)
        cmds.showWindow(cls.winName)



class Functions(object):
    baseGeo = ''
    bsNodeName = ''
    deformerList = ['blendShape', 'cluster', 'ffd', 'wrap', 'nonLinear', 'sculpt', 'softMod', 'jiggle', 'wire']

    @classmethod
    def loadGeoBS(cls, *args):
        # Get base geometry
        cls.baseGeo = cmds.ls(sl = True)[0]

        cls.removeGarbageOrigShape()

        # Check number of shpaes of base geometry.
        if len(cmds.listRelatives(cls.baseGeo)) > 2:
            OpenMaya.MGlobal.displayError('Base geometry has ' + str(len(cmds.listRelatives(cls.baseGeo))) + ' number of shapes.')
            return
        cmds.textField(UI.widgets['baseGeoTxtFld'], e = True, text = cls.baseGeo)

        # If already exists menu item in the bsOptMenu, delete menu items before populate.
        bsOptItems = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, itemListLong = True)
        if bsOptItems != None:
            for bsOptItem in bsOptItems:
                cmds.deleteUI(bsOptItem)

        # Load BS nodes
        cls.bsList = []
        dfms = tak_lib.getAllDeformers(cls.baseGeo)
        if dfms:
            cls.bsList = [x for x in dfms if cmds.objectType(x) == 'blendShape']

        if cls.bsList:
            for bsNode in cls.bsList:
                    cmds.menuItem(label = bsNode, p = UI.widgets['bsNodeOptMenu'])
        else:
            cmds.menuItem(label = 'None', p = UI.widgets['bsNodeOptMenu'])

        cls.populateCorrectiveTrgList()

    @classmethod
    def removeGarbageOrigShape(cls):
        origShapes = [shape for shape in cmds.listRelatives(cls.baseGeo) if 'Orig' in shape]
        for origShape in origShapes:
            if not cmds.listConnections(origShape): cmds.delete(origShape)

    @classmethod
    def addBsNode(cls, *args):
        bsNode = cmds.blendShape(cls.baseGeo, origin = 'local')[0]
        bsOptItems = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, itemListLong = True)
        if bsOptItems != None:
            for bsOptItem in bsOptItems:
                cmds.deleteUI(bsOptItem)
        cmds.menuItem(label = bsNode, p = UI.widgets['bsNodeOptMenu'])

        cls.bsNodeName = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, v = True)

        # reoerder deformers
        cls.skinCluster = cls.getSkinCluster()
        if cls.skinCluster:
            cmds.reorderDeformers(cls.skinCluster, cls.bsNodeName, cls.baseGeo)

        cls.populateCorrectiveTrgList()


    @classmethod
    def renameBsNode(cls, *args):
        # Get specific name
        result = cmds.promptDialog(title = 'Rename Blend Shape', message = 'New blend shape node name.', text = '', button = ['OK', 'Cancel'], defaultButton = 'OK', cancelButton = 'Cancel', dismissString = 'Cancel')
        if result == 'OK':
            newBsName = cmds.promptDialog(q = True, text = True)
            cmds.rename(cls.bsNodeName, newBsName)

            # Refresh blend shape node option menu
            bsOptItems = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, itemListLong = True)
            if bsOptItems != None:
                for bsOptItem in bsOptItems:
                    cmds.deleteUI(bsOptItem)
            cmds.menuItem(label = newBsName, p = UI.widgets['bsNodeOptMenu'])

            cls.bsNodeName = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, v = True)

            cls.populateCorrectiveTrgList()
        else:
            return


    @classmethod
    def selBsNode(cls, *args):
        cmds.select(cls.bsNodeName, r = True)


    @classmethod
    def sculptMode(cls, arg = None, mode = 'default'):
        # get data
        cls.correctiveTrgName = cmds.textField(UI.widgets['correctiveTrgNameTxtFld'], q = True, text = True)

        # Check if user input corrective name
        if not cls.correctiveTrgName:
            cls.correctiveTrgName = 'corrective_###'

        # check if already same corrective name
        if cmds.objExists(cls.correctiveTrgName):
            cmds.confirmDialog(title = 'Warning', message = "'%s' is already exists.\nTry another corrective name." %(cls.correctiveTrgName), button = 'OK')
            cmds.textField(UI.widgets['correctiveTrgNameTxtFld'], e = True, text = '')
            return

        # if base geometry has no blend shape node add one
        if cls.bsNodeName == 'None':
            cls.addBsNode()

        # duplicate skined geometry
        cls.sculptGeoTrnsf = cmds.duplicate(cls.baseGeo, n = cls.correctiveTrgName + '_sculpt')[0]
        cls.sculptGeo = cmds.listRelatives(cls.sculptGeoTrnsf, s = True)[0]

        # delete intermediate shape
        shapList = cmds.ls(cls.sculptGeo, dag = True, s = True)
        for shap in shapList:
            if cmds.getAttr('%s.intermediateObject' %(shap)):
                cmds.delete(shap)

        # display hud
        if cmds.headsUpDisplay('sclptHUD', q = True, exists = True):
            cmds.headsUpDisplay('sclptHUD', remove = True)
        tak_lib.showHUD('sclptHUD', 'Sculpt Mode')

        if mode == 'default':
            cmds.button(UI.widgets['sclptBtn'], e = True, enable = False)
            cmds.button(UI.widgets['cancelBtn'], e = True, enable = True)
            cmds.button(UI.widgets['createBtn'], e = True, enable = True)

        # hide skin geometry
        cmds.setAttr('%s.visibility' %cls.baseGeo, False)

        cmds.select(cls.sculptGeo, r = True)


    @classmethod
    def cancelSculpt(cls, *args):
        cmds.headsUpDisplay('sclptHUD', remove = True)
        cmds.delete(cls.sculptGeoTrnsf)
        cmds.setAttr('%s.visibility' %cls.baseGeo, True)

        cmds.button(UI.widgets['sclptBtn'], e = True, enable = True)
        cmds.button(UI.widgets['cancelBtn'], e = True, enable = False)
        cmds.button(UI.widgets['createBtn'], e = True, enable = False)


    @classmethod
    def createCorrectiveTarget(cls, mode, *args):
        '''
        Description
            Main function.
        Parameters
            mode: string, Operation mode.
        Returns
            None
        '''

        # Set current working unit to centimeter
        curUnit = cmds.currentUnit(q = True, linear = True)
        if curUnit != 'cm':
            cmds.currentUnit(linear = 'cm')

        # HUD
        cmds.headsUpDisplay('sclptHUD', remove = True)
        cmds.textField(UI.widgets['correctiveTrgNameTxtFld'], e = True, text = '')

        # UI eidts
        cmds.button(UI.widgets['sclptBtn'], e = True, enable = True)
        cmds.button(UI.widgets['cancelBtn'], e = True, enable = False)
        cmds.button(UI.widgets['createBtn'], e = True, enable = False)

        # Show base geometry
        cmds.setAttr('%s.visibility' %cls.baseGeo, True)

        # Get delta vector
        cls.deltaVecArray = cls.getDeltaVec(cls.baseGeo, cls.sculptGeo)

        # If baseGeo has skin cluster, reverse joint transformation for delta vector.
        if cls.getSkinCluster():
            cls.rvrsSkinDfm()

        # If on edit mode, don't create new corrective geometry.
        if mode == 'edit':
            cls.correctiveTrgName = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)[0]
        else:
            # If on combo mode, correctiveTrgName is concatenating selected target names.
            if mode == 'combo':
                selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
                cls.correctiveTrgName =  '_'.join(selTrgList) + '_cb'
            cls.createCorGeo()

        # Move corrective geometry's vertices by delta vector.
        cls.moveCorGeoVtx()

        # add corrective target geometry to geo_grp
        if mode != 'edit':
            correctiveTrgGeoGrpName = cls.baseGeo + '_correctiveTrg_geo_grp'
            if cmds.objExists(correctiveTrgGeoGrpName):
                cmds.parent(cls.correctiveTrgName, correctiveTrgGeoGrpName)
                cmds.setAttr('%s.visibility' %cls.correctiveTrgName, False)
            else:
                cmds.createNode('transform', n = correctiveTrgGeoGrpName)
                cmds.parent(cls.correctiveTrgName, correctiveTrgGeoGrpName)
                cmds.setAttr('%s.visibility' %cls.correctiveTrgName, False)

        # delete sculpt geometry
        cmds.delete(cls.sculptGeoTrnsf)

        # add corrective target to blend shape node
        if mode != 'edit':
            if cls.bsNodeName != 'None':
                bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
                if not bsAttrList:
                    cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.baseGeo, 0, cls.correctiveTrgName, 1.0))
                    cmds.setAttr('%s.%s' %(cls.bsNodeName, cls.correctiveTrgName), 1)
                else:
                    weightNumList = []
                    for bsAttr in bsAttrList:
                        if 'weight' in bsAttr:
                            reObj = re.search(r'\d+', bsAttr)
                            weightNum = reObj.group()
                            weightNumList.append(int(weightNum))
                    bsIndex = max(weightNumList) + 1

                    cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.baseGeo, bsIndex, cls.correctiveTrgName, 1.0))
                    cmds.setAttr('%s.%s' %(cls.bsNodeName, cls.correctiveTrgName), 1)
            elif cls.bsNodeName == 'None':
                cls.bsNodeName = '{0}_correctiveBS'.format(cls.baseGeo)
                cmds.blendShape(cls.correctiveTrgName, cls.baseGeo, n = cls.bsNodeName, frontOfChain = True)[0]
                cmds.setAttr('%s.%s' %(cls.bsNodeName, cls.correctiveTrgName), 1)
                # fill blend shape node option menu
                # load BS nodes
                cls.bsList = []
                allConnections = cmds.listHistory(cls.baseGeo)
                for item in allConnections:
                    if cmds.objectType(item) == 'blendShape':
                        cls.bsList.append(item)

                # if already exists menu item in the bsOptMenu, delete menu items before populate
                bsOptItems = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, itemListLong = True)
                if bsOptItems != None:
                    for bsOptItem in bsOptItems:
                        cmds.deleteUI(bsOptItem)
                if cls.bsList:
                    for bsNode in cls.bsList:
                        cmds.menuItem(label = bsNode, p = UI.widgets['bsNodeOptMenu'])


        # connect combo corrective target blend shape
        if mode == 'combo':
            exprNodeName = cls.correctiveTrgName + '_expr'
            exprStr = '{0}.{1} = '.format(cls.bsNodeName, cls.correctiveTrgName)
            # convert target list name to 'blend shape node.target name'
            for i in range(len(selTrgList)):
                selTrgList[i] = cls.bsNodeName + '.' + selTrgList[i]
            exprStr += ' * '.join(selTrgList)
            cmds.expression(s = exprStr, ae = True, uc = 'all', n = exprNodeName)

        # refresh corrective target list
        cls.populateCorrectiveTrgList()

        # Trun back working unit
        cmds.currentUnit(linear = curUnit)


    @classmethod
    def getDeltaVec(cls, baseGeo, sculptGeo):
        '''
        Description
            Calculate delta vector between baseGeo to sculptGeo.
        Parameters
            baseGeo: string, Deformed geometry.
            sculptGeo: string, Sculpted geometry.
        Returns
            deltaVecArray: MVectorArray
        '''

        selLs = OpenMaya.MSelectionList()
        selLs.add(baseGeo)
        selLs.add(sculptGeo)

        baseGeoDagPath = OpenMaya.MDagPath()
        sculptGeoDagPath = OpenMaya.MDagPath()
        selLs.getDagPath(0, baseGeoDagPath)
        selLs.getDagPath(1, sculptGeoDagPath)

        sculptMeshFn = OpenMaya.MFnMesh(sculptGeoDagPath)
        sculptMeshPoints = OpenMaya.MPointArray()
        sculptMeshFn.getPoints(sculptMeshPoints)

        deltaVecArray = OpenMaya.MVectorArray()
        baseGeoIt = OpenMaya.MItGeometry(baseGeoDagPath)
        while not baseGeoIt.isDone():
            baseGeoPoint = baseGeoIt.position()
            deltaVec = sculptMeshPoints[baseGeoIt.index()] - baseGeoPoint
            deltaVecArray.append(deltaVec)

            baseGeoIt.next()

        return deltaVecArray


    @classmethod
    def rvrsSkinDfm(cls):
        '''
        Description
            Reverse skin deformation for delta vector.
        Parameters
            None
        Retruns
            None
        '''

        for i in range(cls.deltaVecArray.length()):
            # If vertex isn't moved skip calculation.
            if cls.deltaVecArray[i].length() == 0.0:
                continue

            # set matrix pallete
            trsfedMatrix = OpenMaya.MMatrix()
            matrixPalletInitList = [0.0, 0.0, 0.0, 0.0,
                                    0.0, 0.0, 0.0, 0.0,
                                    0.0, 0.0, 0.0, 0.0,
                                    0.0, 0.0, 0.0, 0.0]
            OpenMaya.MScriptUtil.createMatrixFromList(matrixPalletInitList, trsfedMatrix)

            # get influences
            influenceList = cmds.skinCluster('%s.vtx[%d]' %(cls.baseGeo, i), q = True, wi = True)

            # Get influence's transform matrix from bind pose matrix.
            for influence in influenceList:
                if cmds.nodeType(influence) != 'joint':
                    continue
                infBindMatrixList = cmds.getAttr('%s.bindPose' %influence)
                infBindMatrix = OpenMaya.MMatrix()
                OpenMaya.MScriptUtil.createMatrixFromList(infBindMatrixList, infBindMatrix)

                infWorldMatrixList = cmds.getAttr('%s.worldMatrix' %influence)
                infWorldMatrix = OpenMaya.MMatrix()
                OpenMaya.MScriptUtil.createMatrixFromList(infWorldMatrixList, infWorldMatrix)

                infWeight = cmds.skinPercent(cls.skinCluster, '%s.vtx[%d]' %(cls.baseGeo, i), q = True, transform = influence, v = True)

                trsfedMatrix += (infBindMatrix.inverse() * infWorldMatrix) * infWeight

            # Reverse delta vector by multipling inverse matrix.
            revVec = cls.deltaVecArray[i] * trsfedMatrix.inverse()
            cls.deltaVecArray.set(revVec, i)


    @classmethod
    def createCorGeo(cls):
        '''
        Create corrective geometry by duplicating intermediate object.
        '''

        cmds.duplicate(cls.baseGeo, n = cls.correctiveTrgName)
        corTrgShps = cmds.listRelatives(cls.correctiveTrgName)

        intmObj = ''
        for corTrgShp in corTrgShps:
            if cmds.getAttr(corTrgShp + '.intermediateObject'):
                cmds.setAttr(corTrgShp + '.intermediateObject', False)
                intmObj = corTrgShp
            else:
                cmds.delete(corTrgShp)

        cmds.rename(intmObj, cls.correctiveTrgName + 'Shape')


    @classmethod
    def moveCorGeoVtx(cls):
        selLs = OpenMaya.MSelectionList()
        selLs.add(cls.correctiveTrgName)

        dagPath = OpenMaya.MDagPath()
        selLs.getDagPath(0, dagPath)

        corGeoIt = OpenMaya.MItGeometry(dagPath)
        while not corGeoIt.isDone():
            if cls.deltaVecArray[corGeoIt.index()].length() == 0.0:
                corGeoIt.next()

            corGeoPoint = corGeoIt.position()
            corGeoPoint += cls.deltaVecArray[corGeoIt.index()]

            corGeoIt.setPosition(corGeoPoint)

            corGeoIt.next()


    @classmethod
    def getSkinCluster(cls):
        cmds.select(cls.baseGeo, r = True)
        mel.eval('string $selList[] = `ls -sl`;')
        mel.eval('string $source = $selList[0];')
        cls.skinCluster = mel.eval('findRelatedSkinCluster($source);')
        cmds.select(cl = True)
        return cls.skinCluster


    @classmethod
    def populateCorrectiveTrgList(cls, *args):
        cls.bsNodeName = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, v = True)
        bsTrgList = []

        # Delete exists items before populate
        if cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, allItems = True):
            cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, removeAll = True)
        trgWgts = cmds.scrollLayout(UI.widgets['correctiveTrgWgtScrLo'], q = True, childArray = True)
        if trgWgts:
            for trgWgt in trgWgts:
                cmds.deleteUI(trgWgt)

        if cls.bsNodeName != 'None':
            try:
                bsTrgList = cmds.listAttr('%s.w' %(cls.bsNodeName), multi = True)
                if bsTrgList:
                    cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, append = bsTrgList)
                    for i in range(len(bsTrgList)):
                        # Set bold font for connected targets
                        if cmds.listConnections('{0}.{1}'.format(cls.bsNodeName, bsTrgList[i]), source = True, destination = False):
                            cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, lineFont = (i + 1, 'boldLabelFont'))

                        cls.addTrgWgtWdgt(bsTrgList[i])
            except:
                pass

        #cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], e = True, enable = False)


    @classmethod
    def addTrgWgtWdgt(cls, bsTrg):
        bsTrgWgtFltFld = cmds.floatField(bsTrg + '_wgtFltFld', precision = 2, w = 30, p = UI.widgets['correctiveTrgWgtScrLo'])
        cmds.connectControl(bsTrgWgtFltFld, cls.bsNodeName + '.' + bsTrg)
        cmds.floatField(bsTrg + '_wgtFltFld', e = True, enable = False)


    @classmethod
    def trgSldrDragCmd(cls, *args):
        trgSldrVal = cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], q = True, v = True)
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
        if selTrgList:
            for selTrg in selTrgList:
                try:
                    cmds.setAttr('{0}.{1}'.format(cls.bsNodeName, selTrg), trgSldrVal)
                except:
                    pass


    @classmethod
    def correctiveTrgListSelCmd(cls, *args):
        allTrgs = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, allItems = True)
        selTrgs = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        poseLocs = []
        for selTrg in selTrgs:
            poseLoc = selTrg + '_pose_loc'
            if cmds.objExists(poseLoc):
                poseLocs.append(poseLoc)

        # Enable related weight float field.
        for trg in allTrgs:
            if trg in selTrgs:
                cmds.floatField(trg + '_wgtFltFld', e = True, enable = True)
            else:
                cmds.floatField(trg + '_wgtFltFld', e = True, enable = False)

        if poseLocs:
            cmds.select(poseLocs, r = True)
        else:
            cmds.select(cls.bsNodeName)


    @classmethod
    def popupMenuCmd(cls, *args):
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        if selTrgList == None:
            cmds.menuItem(UI.widgets['popMenuEdit'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuRename'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popupMenuSplit'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuMerge'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuFlip'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuMirror'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuRmv'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuDup'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuBreak'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuPreInf'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuPostInf'], e = True, enable = False)

        elif len(selTrgList) == 1:
            cmds.menuItem(UI.widgets['popMenuEdit'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuCombo'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuRename'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popupMenuSplit'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuMerge'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuFlip'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuMirror'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuRmv'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuDup'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuBreak'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuPreInf'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuPostInf'], e = True, enable = True)

        elif len(selTrgList) >= 2:
            cmds.menuItem(UI.widgets['popMenuEdit'], e = True, enable = False)
            cmds.menuItem(UI.widgets['popMenuCombo'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuRename'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popupMenuSplit'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuMerge'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuFlip'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuMirror'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuRmv'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuDup'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuBreak'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuPreInf'], e = True, enable = True)
            cmds.menuItem(UI.widgets['popMenuPostInf'], e = True, enable = True)


    @classmethod
    def renameUI(cls, *args):
        '''
        UI for renaming.
        '''

        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        win = 'reNameWin'

        if cmds.window(win, exists = True):
            cmds.deleteUI(win)

        cmds.window(win, title = 'Rename Win')

        cmds.columnLayout(adj = True)
        cmds.textFieldGrp('newNameTxtFldGrp', label = 'New Name: ', columnWidth = [(1, 60), (2, 200)])
        cmds.textFieldGrp('prefixTxtFldGrp', label = 'Prefix: ', columnWidth = [(1, 60), (2, 200)])
        cmds.textFieldGrp('srchTxtFldGrp', label = 'Search: ', columnWidth = [(1, 60), (2, 200)])
        cmds.textFieldGrp('rplcTxtFldGrp', label = 'Replace: ', columnWidth = [(1, 60), (2, 200)])
        cmds.textFieldGrp('suffixTxtFldGrp', label = 'Suffix: ', columnWidth = [(1, 60), (2, 200)])

        cmds.button(label = 'Apply', c = partial(cls.rename, win, selTrgList))

        if len(selTrgList) >= 2:
            cmds.textFieldGrp('newNameTxtFldGrp', e = True, vis = False)
        else:
            cmds.textFieldGrp('prefixTxtFldGrp', e=True, vis=False)
            cmds.textFieldGrp('srchTxtFldGrp', e=True, vis=False)
            cmds.textFieldGrp('rplcTxtFldGrp', e=True, vis=False)
            cmds.textFieldGrp('suffixTxtFldGrp', e=True, vis=False)

        cmds.window(win, e = True, w = 150, h = 50)
        cmds.showWindow(win)


    @classmethod
    def rename(cls, winName, selTrgList, *args):
        newName = cmds.textFieldGrp('newNameTxtFldGrp', q = True, text = True)
        prefix = cmds.textFieldGrp('prefixTxtFldGrp', q = True, text = True)
        srch = cmds.textFieldGrp('srchTxtFldGrp', q = True, text = True)
        rplc = cmds.textFieldGrp('rplcTxtFldGrp', q = True, text = True)
        suffix = cmds.textFieldGrp('suffixTxtFldGrp', q = True, text = True)

        for selTrg in selTrgList:
            # Seek naming
            if newName:
                print('newName:', newName)
                otherSideName = newName
            else:
                otherSideName = re.sub(srch, rplc, prefix+selTrg+suffix)

            # rename blend shape name
            cmds.aliasAttr(otherSideName, '%s.%s' %(cls.bsNodeName, selTrg))

            # rename target geometry name
            try:
                cmds.rename(selTrg, otherSideName)
            except:
                pass

        cls.populateCorrectiveTrgList()

        cmds.deleteUI(winName)


    @classmethod
    def trgListEidtCmd(cls, *args):
        cls.sculptMode(mode = 'edit')
        cls.createHudBtn('edit')


    @classmethod
    def doneEdit(cls, *args):
        cls.createCorrectiveTarget('edit')
        cls.removeHudBtn('edit')


    @classmethod
    def cancelEdit(cls, *args):
        cls.cancelSculpt()
        cls.removeHudBtn('edit')


    @classmethod
    def trgListComboCmd(cls, *args):
        cls.sculptMode(mode = 'combo')
        cls.createHudBtn('combo')


    @classmethod
    def addCombo(cls, *args):
        cls.createCorrectiveTarget('combo')
        cls.removeHudBtn('combo')
        cls.populateCorrectiveTrgList()


    @classmethod
    def cancelCombo(cls, *args):
        cls.cancelSculpt()
        cls.removeHudBtn('combo')


    @classmethod
    def createHudBtn(cls, mode):
        if mode == 'edit':
            cmds.hudButton('doneEditHudBtn', s = 3, b = 4, vis = 1, l = 'Done Edit', bw = 80, bsh = 'roundRectangle', rc = cls.doneEdit)
            cmds.hudButton('cancelEditHudBtn', s = 3, b = 6, vis = 1, l = 'Cancel Edit', bw = 80, bsh = 'roundRectangle', rc = cls.cancelEdit)

        elif mode == 'combo':
            cmds.hudButton('addComboHudBtn', s = 3, b = 4, vis = 1, l = 'Add Combo', bw = 80, bsh = 'roundRectangle', rc = cls.addCombo)
            cmds.hudButton('cancelComboHudBtn', s = 3, b = 6, vis = 1, l = 'Cancel', bw = 80, bsh = 'roundRectangle', rc = cls.cancelCombo)


    @classmethod
    def removeHudBtn(cls, mode):
        if mode == 'edit':
            cmds.headsUpDisplay('doneEditHudBtn', remove = True)
            cmds.headsUpDisplay('cancelEditHudBtn', remove = True)

        elif mode == 'combo':
            cmds.headsUpDisplay('addComboHudBtn', remove = True)
            cmds.headsUpDisplay('cancelComboHudBtn', remove = True)


    @classmethod
    def createOppositeUI(cls, *args):
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        win = 'createOppWin'

        if cmds.window(win, exists = True):
            cmds.deleteUI(win)

        cmds.window(win, title = 'Create Opposite Shape', mnb = False, mxb = False)

        cmds.columnLayout(adj = True)
        cmds.textFieldGrp('srchTxtFldGrp', label = 'Search: ', text = '_L', columnWidth = [(1, 60), (2, 200)])
        cmds.textFieldGrp('rplcTxtFldGrp', label = 'Replace: ', text = '_R', columnWidth = [(1, 60), (2, 200)])

        cmds.button(label = 'Apply', c = partial(cls.createOpposite, win, selTrgList))

        cmds.window(win, e = True, w = 150, h = 50)
        cmds.showWindow(win)


    @classmethod
    def createOpposite(cls, winName, selTrgList, *args):
        srchTxt = cmds.textFieldGrp('srchTxtFldGrp', q = True, text = True)
        rplcTxt = cmds.textFieldGrp('rplcTxtFldGrp', q = True, text = True)
        cmds.deleteUI(winName)

        cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, selectItem = selTrgList)
        dupTrgLs = cls.dupTrg()
        cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, selectItem = dupTrgLs)
        flipTrgLs = cls.flip()
        cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, selectItem = flipTrgLs)

        for trg in flipTrgLs:
            oppsiteTrgName = re.sub(srchTxt, rplcTxt, trg).split('_dup_flip')[0]

            # rename blend shape name
            try:
                cmds.aliasAttr(oppsiteTrgName, '%s.%s' %(cls.bsNodeName, trg))
            except:
                pass

            # rename target geometry name
            try:
                cmds.rename(trg, oppsiteTrgName)
            except:
                pass

        cls.populateCorrectiveTrgList()


    @classmethod
    def dupTrg(cls, *args):
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
        bsTrgList = cmds.listAttr('%s.w' %(cls.bsNodeName), multi = True)

        dupTrgLs = []

        for selTrg in selTrgList:
            bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
            weightNumList = []
            for bsAttr in bsAttrList:
                if 'weight' in bsAttr:
                    reObj = re.search(r'\d+', bsAttr)
                    weightNum = reObj.group()
                    weightNumList.append(int(weightNum))
            bsIndex = max(weightNumList) + 1

            # duplicate
            dupGeo = cmds.duplicate(selTrg, n = selTrg + '_dup')[0]
            dupTrgLs.append(dupGeo)
            # add to blend shape node
            cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.baseGeo, bsIndex, dupGeo, 1.0))

        cls.populateCorrectiveTrgList()
        return dupTrgLs


    @classmethod
    def extractMesh(cls, *args):
        allTrgs = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, allItems = True)
        for trg in allTrgs:
            cmds.setAttr('{0}.{1}'.format(cls.bsNodeName, trg), 0)

        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
        for selTrg in selTrgList:
            cmds.setAttr('{0}.{1}'.format(cls.bsNodeName, selTrg), 1)
            extractedMesh = cmds.duplicate(cls.baseGeo, n=selTrg)[0]
            cmds.parent(extractedMesh, world=True)
            cmds.setAttr('{0}.{1}'.format(cls.bsNodeName, selTrg), 0)


    @classmethod
    def breakConnect(cls, *args):
        mel.eval('source channelBoxCommand;')

        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        for selTrg in selTrgList:
            try:
                poseLoc = selTrg + '_pose_loc'
                conNodes = cmds.listConnections(poseLoc)
                for node in conNodes:
                    cmds.delete(node)
                cmds.delete(poseLoc)
            except:
                pass

            attr = cls.bsNodeName + '.' + selTrg
            mel.eval('CBdeleteConnection "%s"' %attr)

        cls.populateCorrectiveTrgList()
        cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, selectItem = selTrgList)


    @classmethod
    def removeTrg(cls, *args):
        cls.breakConnect()

        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        for selTrg in selTrgList:
            try:
                bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
                selTrgIndexInList = bsAttrList.index(selTrg)
                selTrgWeightIndex = selTrgIndexInList + 1
                reObj = re.search(r'\d+', bsAttrList[selTrgWeightIndex])
                selTrgIndex = int(reObj.group())
            except:
                bsAttrList = cmds.listAttr(cls.bsNodeName, k = True, multi = True)
                bsAttrList.remove('envelope')
                selTrgIndex = bsAttrList.index(selTrg)

            # delete blend shape
            cmds.removeMultiInstance('%s.%s' %(cls.bsNodeName, selTrg), b = True)
            try:
                cmds.aliasAttr(cls.bsNodeName + '.' + selTrg, rm = True)
            except:
                pass
            try:
                cmds.blendShape(cls.bsNodeName, e = True, remove = True, target = (cls.baseGeo, selTrgIndex, selTrg, 1.0))
            except:
                pass

        cls.populateCorrectiveTrgList()


    @classmethod
    def splitLR(cls, *args):
        baseName = cls.baseGeo
        targetList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
        lPrefix = 'L_'
        rPrefix = 'R_'
        correctiveTrgGeoGrpName = cls.baseGeo + '_correctiveTrg_geo_grp'

        for targetName in targetList:
            # Check target mesh existsing.
            # If not exists create by duplicating baseGeo with target weight 1.
            if not cmds.objExists(targetName):
                cmds.setAttr('{0}.{1}'.format(cls.bsNodeName, targetName), 1)
                cmds.duplicate(cls.baseGeo, n = targetName)
                cmds.parent(targetName, correctiveTrgGeoGrpName)
                cmds.setAttr(targetName + ".visibility", False)
                cmds.setAttr('{0}.{1}'.format(cls.bsNodeName, targetName), 0)

        # percentage of center fall off distance
        centerFallOff = 10 * 0.01
        maxVtxX = cls.getMaxXPos(baseName)
        fallOffRange = (centerFallOff * maxVtxX) * 2

        # set all deformer of skin geometry envelop to 0
        cls.getSkinCluster()
        if cls.skinCluster:
            cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
        allConnections = cmds.listHistory(cls.baseGeo)
        for item in allConnections:
            if cmds.objectType(item) in cls.deformerList:
                cmds.setAttr('%s.envelope' %item, 0)

        for targetName in targetList:
            targetPos = cmds.xform(targetName, q = True, ws = True, rp = True)
            boundingBox = cmds.exactWorldBoundingBox(targetName)
            LRDist = boundingBox[3] - boundingBox[0]

            lrTargets = []

            # create left side blend target
            lBlendTarget = cmds.duplicate(baseName, n = lPrefix + targetName, rr = True, renameChildren = True)
            lrTargets.append(lBlendTarget[0])
            # unlock attributes
            attrList = ['translateX', 'translateY', 'translateZ']
            for attr in attrList:
                cmds.setAttr(lBlendTarget[0] + '.' + str(attr), lock = False)
            # move to target's left side
            cmds.xform(lBlendTarget, ws = True, t = ((targetPos[0] + LRDist), targetPos[1], targetPos[2]))
            # parent to correctiveTrg_geo_grp
            if cmds.objExists(correctiveTrgGeoGrpName):
                cmds.parent(lBlendTarget[0], correctiveTrgGeoGrpName)
                cmds.setAttr('%s.visibility' %lBlendTarget[0], False)
            else:
                cmds.createNode('transform', n = correctiveTrgGeoGrpName)
                cmds.parent(lBlendTarget[0], correctiveTrgGeoGrpName)
                cmds.setAttr('%s.visibility' %lBlendTarget[0], False)

            # create right side belnd target
            rBlendTarget = cmds.duplicate(baseName, n = rPrefix + targetName, rr = True, renameChildren = True)
            lrTargets.append(rBlendTarget[0])
            # unlock attributes
            for attr in attrList:
                cmds.setAttr(rBlendTarget[0] + '.' + str(attr), lock = False)
            # move to target's right side
            cmds.xform(rBlendTarget, ws = True, t = ((targetPos[0] - LRDist), targetPos[1], targetPos[2]))
            # parent to correctiveTrg_geo_grp
            cmds.parent(rBlendTarget[0], correctiveTrgGeoGrpName)
            cmds.setAttr('%s.visibility' %rBlendTarget[0], False)

            # initialize list variables
            baseChildList = []
            targetChildList = []
            lTargetChildList = []
            rTargetChildList = []

            baseChildList.append(baseName)
            targetChildList.append(targetName)
            lTargetChildList.append(lBlendTarget[0])
            rTargetChildList.append(rBlendTarget[0])

            # vector calculation for each geometry
            for x in range(len(baseChildList)):
                # get symmetrical matching vertex data
                symVtxDic, cVtxList = cls.matchSymVtx(baseChildList[x])

                for lVtxIndex in symVtxDic.keys():
                    trgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(targetChildList[x], lVtxIndex), local = True)
                    baseVtxPos = cmds.pointPosition('%s.vtx[%d]' %(baseChildList[x], lVtxIndex), local = True)

                    trgVtxVec = OpenMaya.MVector(*trgVtxPos)
                    baseVtxVec = OpenMaya.MVector(*baseVtxPos)
                    moveVec = trgVtxVec - baseVtxVec

                    # if vertex didn't move, skip caculation
                    if moveVec.length() == 0:
                        continue

                    # weight value calculation
                    weightVal = 0.5 + (baseVtxVec.x / fallOffRange)
                    if weightVal >= 1:
                        weightVal = 1
                    symWeightVal = 1 - weightVal


                    lTrgVtxVec = baseVtxVec
                    lMoveVec = moveVec * weightVal
                    finalVec = lTrgVtxVec + lMoveVec

                    # assign to the left blend target
                    cmds.xform('%s.vtx[%d]' %(lTargetChildList[x], lVtxIndex), os = True, t = (finalVec.x, finalVec.y, finalVec.z))
                    # assign to the right blend target's symmetry vertex
                    cmds.xform('%s.vtx[%d]' %(rTargetChildList[x], symVtxDic[lVtxIndex]), os = True, t = (-finalVec.x, finalVec.y, finalVec.z))

                    # assign to the symmetry vertex
                    symVtxPos = cmds.pointPosition('%s.vtx[%d]' %(baseChildList[x], symVtxDic[lVtxIndex]), local = True)
                    symVtxVec = OpenMaya.MVector(*symVtxPos)

                    if 0 < abs(symVtxVec.x) <= fallOffRange:
                        symMoveVec = moveVec * symWeightVal
                        symFinalVec = [(symVtxVec.x + -symMoveVec.x), (symVtxVec.y + symMoveVec.y), (symVtxVec.z + symMoveVec.z)]

                        # assign to the right blend target
                        cmds.xform('%s.vtx[%d]' %(lTargetChildList[x], symVtxDic[lVtxIndex]), os = True, t = (symFinalVec[0], symFinalVec[1], symFinalVec[2]))
                        # assign to the left blend target's symmetry vertex
                        cmds.xform('%s.vtx[%d]' %(rTargetChildList[x], lVtxIndex), os = True, t = (-symFinalVec[0], symFinalVec[1], symFinalVec[2]))

                # center vertex
                for cVtxIndex in cVtxList:
                    trgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(targetChildList[x], cVtxIndex), local = True)
                    baseVtxPos = cmds.pointPosition('%s.vtx[%d]' %(baseChildList[x], cVtxIndex), local = True)

                    trgVtxVec = OpenMaya.MVector(*trgVtxPos)
                    baseVtxVec = OpenMaya.MVector(*baseVtxPos)
                    moveVec = trgVtxVec - baseVtxVec

                    # if vertex didn't move, skip caculation
                    if moveVec.length() == 0:
                        continue

                    cMoveVec = moveVec * 0.5

                    # final center vertex position
                    finalVec = baseVtxVec + cMoveVec
                    cmds.xform('%s.vtx[%d]' %(lTargetChildList[x], cVtxIndex), os = True, t = (finalVec.x, finalVec.y, finalVec.z))
                    cmds.xform('%s.vtx[%d]' %(rTargetChildList[x], cVtxIndex), os = True, t = (finalVec.x, finalVec.y, finalVec.z))

            # add left and right targets to the blend shape
            for target in lrTargets:
                bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
                weightNumList = []
                for bsAttr in bsAttrList:
                    if 'weight' in bsAttr:
                        reObj = re.search(r'\d+', bsAttr)
                        weightNum = reObj.group()
                        weightNumList.append(int(weightNum))
                bsIndex = max(weightNumList) + 1

                cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.baseGeo, bsIndex, target, 1.0))

        # set all deformer of skin geometry envelop to 1
        if cls.skinCluster:
            cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
        allConnections = cmds.listHistory(cls.baseGeo)
        for item in allConnections:
            if cmds.objectType(item) in cls.deformerList:
                cmds.setAttr('%s.envelope' %item, 1)

        cls.populateCorrectiveTrgList()


    @staticmethod
    def getMaxXPos(base):
        maxXPos = 0
        numOfVtx = cmds.polyEvaluate(base, v = True)
        for i in range(numOfVtx):
            vtxPos = cmds.pointPosition('{0}.vtx[{1}]'.format(base, i), local = True)
            if vtxPos[0] > maxXPos:
                maxXPos = vtxPos[0]
        return maxXPos


    # function for match symmetry vertex
    @staticmethod
    def matchSymVtx(geomtry):
        # get number of vertex
        numOfVtx = cmds.polyEvaluate(geomtry, v = True)

        # get left and right and center vertex list
        lVtxList = []
        rVtxList = []
        cVtxList = []
        symVtxDic = {}

        for i in range(numOfVtx):
            vtxPos = cmds.pointPosition('%s.vtx[%d]' %(geomtry, i), local = True)

            # refine raw vtxPos data
            for val in range(len(vtxPos)):
                if 'e' in str(vtxPos[val]):
                    vtxPos[val] = 0.0
                else:
                    vtxPos[val] = round(vtxPos[val], 3)

            if vtxPos[0] > 0:
                lVtxList.append(i)
            elif vtxPos[0] < 0:
                rVtxList.append(i)
            else:
                cVtxList.append(i)

        # get symmetry vertex tolerance value for find matching right side symmetry vertex
        symVtxTol =  cmds.floatField(UI.widgets['symVtxSrchTolFlFld'], q = True, v = True)

        # get symVtxDic
        for lVtxIndex in lVtxList:
            lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(geomtry, lVtxIndex), local = True)
            symVtxPos = -lVtxPos[0], lVtxPos[1], lVtxPos[2]
            symVtxVec = OpenMaya.MVector(*symVtxPos)

            for rVtxIndex in rVtxList:
                rVtxPos = cmds.pointPosition('%s.vtx[%d]' %(geomtry, rVtxIndex), local = True)
                rVtxVec = OpenMaya.MVector(*rVtxPos)

                dist = symVtxVec - rVtxVec

                if dist.length() <= symVtxTol:
                    symVtxDic[lVtxIndex] = rVtxIndex
                    index = rVtxList.index(rVtxIndex)
                    rVtxList.pop(index)
                    break

        return symVtxDic, cVtxList


    @classmethod
    def mergeTrg(cls, *args):
        # merged target name
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
        joinStr = '_'
        selTrgNameList = []
        for selTrg in selTrgList:
            selTrgNameList.append(selTrg)
        merTrgName =  joinStr.join(selTrgNameList) + '_mrg'

        # set all deformer of skin geometry envelop to 0
        cls.getSkinCluster()
        if cls.skinCluster:
            cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
        allConnections = cmds.listHistory(cls.baseGeo)
        for item in allConnections:
            if cmds.objectType(item) in cls.deformerList:
                cmds.setAttr('%s.envelope' %item, 0)

        # duplicate skin geometry to get merged target
        cmds.duplicate(cls.baseGeo, n = merTrgName)
        # delete intermediate shape
        shapList = cmds.ls(merTrgName, dag = True, s = True)
        for shap in shapList:
            if cmds.getAttr('%s.intermediateObject' %(shap)):
                cmds.delete(shap)

        # get vertex number
        numOfVtx = cmds.polyEvaluate(cls.baseGeo, v = True)

        # for each target in selected targets
        finDeltaDic = {}
        trgCounter = 0
        for trg in selTrgList:
            # for each vertex of target
            for i in range(numOfVtx):
                # get delta between target geometry vertex position and merge target vertex position
                trgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(trg, i), local = True)
                trgVtxVec = OpenMaya.MVector(*trgVtxPos)
                mrgTrgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(merTrgName, i), local = True)
                mrgTrgVtxVec = OpenMaya.MVector(*mrgTrgVtxPos)

                delta = trgVtxVec - mrgTrgVtxVec

                # initialize finDeltaDic
                if trgCounter == 0:
                    finDeltaDic[i] = delta

                # if vertex didn't move, skip caculation
                if delta.length() == 0:
                    continue

                # sum to the final delta dictionary
                if trgCounter != 0:
                    finDeltaDic[i] += delta

            trgCounter += 1

        # set final vertex position
        for i in range(numOfVtx):
            mrgTrgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(merTrgName, i), local = True)
            mrgTrgVtxVec = OpenMaya.MVector(*mrgTrgVtxPos)

            # add delta to merged target vertex position
            finVec = mrgTrgVtxVec + finDeltaDic[i]

            # set merged target vertex position
            cmds.xform('%s.vtx[%d]' %(merTrgName, i), os = True, t = (finVec.x, finVec.y, finVec.z))

        # set all deformer of skin geometry envelop to 0
        if cls.skinCluster:
            cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
        allConnections = cmds.listHistory(cls.baseGeo)
        for item in allConnections:
            if cmds.objectType(item) in cls.deformerList:
                cmds.setAttr('%s.envelope' %item, 1)

        correctiveTrgGeoGrpName = cls.baseGeo + '_correctiveTrg_geo_grp'
        # parent to correctiveTrg_geo_grp
        cmds.parent(merTrgName, correctiveTrgGeoGrpName)
        cmds.setAttr('%s.visibility' %merTrgName, False)

        # add to blend shape node
        bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
        weightNumList = []
        for bsAttr in bsAttrList:
            if 'weight' in bsAttr:
                reObj = re.search(r'\d+', bsAttr)
                weightNum = reObj.group()
                weightNumList.append(int(weightNum))
        bsIndex = max(weightNumList) + 1

        cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.baseGeo, bsIndex, merTrgName, 1.0))
        cmds.setAttr('%s.%s' %(cls.bsNodeName, merTrgName), 1)

        # refresh corrective target list
        cls.populateCorrectiveTrgList()


    @classmethod
    def flip(cls, *args):
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
        flipTrgLs = []

        correctiveTrgGeoGrpName = cls.baseGeo + '_correctiveTrg_geo_grp'
        if not cmds.objExists(correctiveTrgGeoGrpName):
            cmds.createNode('transform', n = correctiveTrgGeoGrpName)

        # set all deformer of skin geometry envelop to 0
        cls.getSkinCluster()
        if cls.skinCluster:
            cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
        allConnections = cmds.listHistory(cls.baseGeo)
        for item in allConnections:
            if cmds.objectType(item) in cls.deformerList:
                cmds.setAttr('%s.envelope' %item, 0)

        # Check if the base geometry symmetry
        cmds.select(cls.baseGeo, r = True)

        symVtxDic, cVtxList = cls.matchSymVtx(cls.baseGeo)
        for selTrg in selTrgList:
            for lVtxIndex in symVtxDic.keys():
                # get left and right vertex position
                lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(selTrg, lVtxIndex), local = True)
                rVtxPos = cmds.pointPosition('%s.vtx[%d]' %(selTrg, symVtxDic[lVtxIndex]), local = True)

                # change lVtxPos and rVtxPos
                lVtxPos, rVtxPos = (-rVtxPos[0], rVtxPos[1], rVtxPos[2]), (-lVtxPos[0], lVtxPos[1], lVtxPos[2])

                # set vertex position
                cmds.xform('%s.vtx[%d]' %(selTrg, lVtxIndex), os = True, t = lVtxPos)
                cmds.xform('%s.vtx[%d]' %(selTrg, symVtxDic[lVtxIndex]), os = True, t = rVtxPos)

            # Rename selTrg
            cmds.aliasAttr(selTrg + '_flip', '%s.%s' %(cls.bsNodeName, selTrg))

            # rename target geometry name
            try:
                cmds.rename(selTrg, selTrg + '_flip')
            except:
                pass

            flipTrgLs.append(selTrg + '_flip')

        # set all deformer of skin geometry envelop to 1
        if cls.skinCluster:
            cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
        allConnections = cmds.listHistory(cls.baseGeo)
        for item in allConnections:
            if cmds.objectType(item) in cls.deformerList:
                cmds.setAttr('%s.envelope' %item, 1)
        cmds.select(cl = True)

        cls.populateCorrectiveTrgList()
        return flipTrgLs


    @classmethod
    def mirror(cls, *args):
        mirOpt = cmds.confirmDialog(title = 'Mirror Option', message = 'What do you want?', button = ['x to -x', '-x to x'], defaultButton = 'Cancel', cancelButton = 'Cancel', dismissString = 'Cancel' )
        if mirOpt == 'Cancel':
            return
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        # set all deformer of skin geometry envelop to 0
        cls.getSkinCluster()
        if cls.skinCluster:
            cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
        allConnections = cmds.listHistory(cls.baseGeo)
        for item in allConnections:
            if cmds.objectType(item) in cls.deformerList:
                cmds.setAttr('%s.envelope' %item, 0)

        symVtxDic, cVtxList = cls.matchSymVtx(cls.baseGeo)
        for selTrg in selTrgList:
            for lVtxIndex in symVtxDic.keys():
                if mirOpt == 'x to -x':
                    lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(selTrg, lVtxIndex), local = True)
                    cmds.xform('%s.vtx[%d]' %(selTrg, symVtxDic[lVtxIndex]), os = True, t = (-lVtxPos[0], lVtxPos[1], lVtxPos[2]))
                elif mirOpt == '-x to x':
                    lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(selTrg, symVtxDic[lVtxIndex]), local = True)
                    cmds.xform('%s.vtx[%d]' %(selTrg, lVtxIndex), os = True, t = (-lVtxPos[0], lVtxPos[1], lVtxPos[2]))

        # set all deformer of skin geometry envelop to 1
        if cls.skinCluster:
            cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
        allConnections = cmds.listHistory(cls.baseGeo)
        for item in allConnections:
            if cmds.objectType(item) in cls.deformerList:
                cmds.setAttr('%s.envelope' %item, 1)
        cmds.select(cl = True)


    @staticmethod
    def loadDriver(prntWdg, *args):
        drvrs = cmds.scrollLayout(prntWdg, q = True, childArray = True)
        if drvrs:
            for drvr in drvrs:
                cmds.deleteUI(drvr)
        selList = cmds.ls(sl = True)
        if selList:
            for sel in selList:
                selNodeType = cmds.nodeType(sel)
                selAttrs = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
                if selAttrs:
                    for selAttr in selAttrs:
                        if selNodeType in ['transform', 'joint']:
                            selAttr = cmds.attributeQuery(selAttr, longName = True, node = sel)
                            SdkObject(prntWdg, sel, 'driver', selAttr)
                        else:
                            SdkObject(prntWdg, sel, 'driver', selAttr)
                else:
                    SdkObject(prntWdg, sel, 'driver')


    @staticmethod
    def loadDriven(prntWdg, *args):
        drvns = cmds.scrollLayout(prntWdg, q = True, childArray = True)
        if drvns:
            for drvn in drvns:
                cmds.deleteUI(drvn)
        selList = cmds.ls(sl = True)
        if selList:
            for sel in selList:
                selNodeType = cmds.nodeType(sel)
                selAttrs = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
                if selAttrs:
                    for selAttr in selAttrs:
                        if selNodeType == 'transform':
                            selAttr = cmds.attributeQuery(selAttr, longName = True, node = sel)
                            SdkObject(prntWdg, sel, 'driven', selAttr)
                        else:
                            SdkObject(prntWdg, sel, 'driven', selAttr)
                else:
                    SdkObject(prntWdg, sel, 'driven')


    @staticmethod
    def addDriven(prntWdg, *args):
        selList = cmds.ls(sl = True)
        if selList:
            for sel in selList:
                selNodeType = cmds.nodeType(sel)
                selAttrs = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
                if selAttrs:
                    for selAttr in selAttrs:
                        if selNodeType in ['transform', 'joint']:
                            selAttr = cmds.attributeQuery(selAttr, longName = True, node = sel)
                            SdkObject(prntWdg, sel, 'driven', selAttr)
                        else:
                            SdkObject(prntWdg, sel, 'driven', selAttr)
                else:
                    SdkObject(prntWdg, sel, 'driven')


    @classmethod
    def sdk(cls, *args):
        driverVals = []
        # get driver data
        drvrObj = cmds.scrollLayout(UI.widgets['sdkDrvrSclLo'], q = True, childArray = True)
        drvrElem = cmds.rowColumnLayout(drvrObj, q = True, childArray = True)
        drvrName = cmds.text(drvrElem[0], q = True, label = True)
        drvrAttrName = cmds.optionMenu(drvrElem[1], q = True, value = True)
        drvrStartVal = cmds.textField(drvrElem[2], q = True, text = True)
        driverVals.append(drvrStartVal)
        drvrEndVal = cmds.textField(drvrElem[3], q = True, text = True)
        driverVals.append(drvrEndVal)

        # get drivens data
        drvnObjs = cmds.scrollLayout(UI.widgets['sdkDrvnSclLo'], q = True, childArray = True)
        drvnElems = []
        for drvnObj in drvnObjs:
            drvnElem = cmds.rowColumnLayout(drvnObj, q = True, childArray = True)
            drvnElems.append(tuple(drvnElem))
        drvnDatas = []
        for drvnElem in drvnElems:
            drvnElemBuffer = []
            drvnName = cmds.text(drvnElem[0], q = True, label = True)
            drvnElemBuffer.append(drvnName)
            drvnAttrName = cmds.optionMenu(drvnElem[1], q = True, value = True)
            drvnElemBuffer.append(drvnAttrName)
            drvnStartVal = cmds.textField(drvnElem[2], q = True, text = True)
            drvnElemBuffer.append(drvnStartVal)
            drvnEndVal = cmds.textField(drvnElem[3], q = True, text = True)
            drvnElemBuffer.append(drvnEndVal)
            drvnDatas.append(tuple(drvnElemBuffer))

        # set driven key
        for drvnData in drvnDatas:
            j = 2
            for i in range(2):
                cmds.setDrivenKeyframe('%s.%s' %(drvnData[0], drvnData[1]), cd = '%s.%s' %(drvrName, drvrAttrName), dv = float(driverVals[i]), v = float(drvnData[j]))
                j += 1

        cls.populateCorrectiveTrgList()


    @classmethod
    def connectCb(cls, *args):
        # get drivers data
        drvrObjs = cmds.scrollLayout(UI.widgets['cbDrvrSclLo'], q = True, childArray = True)
        drvrElems = []
        for drvrObj in drvrObjs:
            drvrElem = cmds.rowColumnLayout(drvrObj, q = True, childArray = True)
            drvrElems.append(tuple(drvrElem))
        drvrDatas = []
        for drvrElem in drvrElems:
            drvrElemBuffer = []
            drvrName = cmds.text(drvrElem[0], q = True, label = True)
            drvrElemBuffer.append(drvrName)
            drvrAttrName = cmds.optionMenu(drvrElem[1], q = True, value = True)
            drvrElemBuffer.append(drvrAttrName)
            drvrStartVal = cmds.textField(drvrElem[2], q = True, text = True)
            drvrElemBuffer.append(drvrStartVal)
            drvrEndVal = cmds.textField(drvrElem[3], q = True, text = True)
            drvrElemBuffer.append(drvrEndVal)
            drvrDatas.append(tuple(drvrElemBuffer))

        drivnVals = []
        # get driver data
        drvnObj = cmds.scrollLayout(UI.widgets['cbDrvnSclLo'], q = True, childArray = True)
        drvnElem = cmds.rowColumnLayout(drvnObj, q = True, childArray = True)
        drvnName = cmds.text(drvnElem[0], q = True, label = True)
        drvnAttrName = cmds.optionMenu(drvnElem[1], q = True, value = True)
        drvnStartVal = cmds.textField(drvnElem[2], q = True, text = True)
        drivnVals.append(drvnStartVal)
        drvnEndVal = cmds.textField(drvnElem[3], q = True, text = True)
        drivnVals.append(drvnEndVal)

        # Create combo expression
        exprNodeName = drvnAttrName + '_expr'
        exprStr = '{0}.{1} = '.format(drvnName, drvnAttrName)

        # Convert driver data to string for expression
        for i in range(len(drvrDatas)):
            drvrName = drvrDatas[i][0]
            drvrAttrName = drvrDatas[i][1]
            drvrStartVal = drvrDatas[i][2]
            drvrEndVal = drvrDatas[i][3]
            drvrDatas[i] = '`clamp 0 1 (%s.%s / (%s - %s))`' %(drvrName, drvrAttrName, drvrEndVal, drvrStartVal)

        exprStr += ' * '.join(drvrDatas)
        cmds.expression(s = exprStr, ae = True, uc = 'all', n = exprNodeName)

        cls.populateCorrectiveTrgList()


    @classmethod
    def setKey(cls, *args):
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
        val =  cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], q = True, v = True)
        curFrame = cmds.currentTime(q = True)

        for selTrg in selTrgList:
            cmds.setKeyframe('%s.%s' %(cls.bsNodeName, selTrg), v = val, time = curFrame, itt = 'linear', ott = 'linear')

        cls.populateCorrectiveTrgList()

        cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, selectItem = selTrgList)


    @classmethod
    def loadSel(cls, wdgName, *args):
        sel = cmds.ls(sl = True)[0]
        if wdgName == UI.widgets['drvrJntTexBtnGrp']:
            selChld = cmds.listRelatives(sel, children = True, type = 'joint')[0]
            selPrnt = cmds.listRelatives(sel, parent = True, type = 'joint')[0]
            cmds.textFieldButtonGrp(wdgName, e = True, text = sel)
            cmds.textFieldButtonGrp(UI.widgets['childJointTexBtnGrp'], e = True, text = selChld)
            cmds.textFieldButtonGrp(UI.widgets['prntJointTexBtnGrp'], e = True, text = selPrnt)
        elif wdgName == UI.widgets['correctiveTrgNameTxtFld']:
            rawSelAttr = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
            niceAttrName = cmds.attributeQuery(rawSelAttr, longName = True, node = sel)

            rawAttrVal = cmds.getAttr('%s.%s' %(sel, rawSelAttr[0]))
            niceAttrVal = int(round(rawAttrVal, 0))
            if niceAttrVal < 0:
                pmStr = 'n' # pmStr = 'Plus Minus String'.
            else:
                pmStr = 'p'

            poseName = '%s_%s_%s_%s%d' %(cls.baseGeo, sel, rawSelAttr[0], pmStr, abs(niceAttrVal))

            cmds.textField(UI.widgets['correctiveTrgNameTxtFld'], e = True, text = poseName)
        else:
            try:
                cmds.textFieldButtonGrp(wdgName, e = True, text = sel)
            except:
                cmds.textField(wdgName, e = True, text = sel)


    @classmethod
    def poseReader(cls, *args):
        driverJoint = cmds.textFieldButtonGrp(UI.widgets['drvrJntTexBtnGrp'], q = True, text = True)
        parentJoint =  cmds.textFieldButtonGrp(UI.widgets['prntJointTexBtnGrp'], q = True, text = True)
        childJoint =  cmds.textFieldButtonGrp(UI.widgets['childJointTexBtnGrp'], q = True, text = True)
        trgName = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)[0]

        # get joints position
        driverJointPos = cmds.xform(driverJoint, q = True, ws = True, rp = True)
        locatorJointPos = cmds.xform(childJoint, q = True, ws = True, rp = True)

        # create locator and place
        if not cmds.objExists(trgName + '_base_loc'):
            baseLoc = cmds.spaceLocator(n = trgName + '_base_loc')[0]
            cmds.xform(baseLoc, ws = True, t = driverJointPos)

            triggerLoc = cmds.spaceLocator(n = trgName + '_trigger_loc')[0]
            cmds.xform(triggerLoc, ws = True, t = locatorJointPos)

            corLocGrp = cmds.createNode('transform', n = trgName + '_loc_grp')
        else:
            baseLoc = trgName + '_base_loc'
            triggerLoc = trgName + '_trigger_loc'
            corLocGrp = trgName + '_loc_grp'

        poseLoc = cmds.spaceLocator(n = trgName + '_pose_loc')[0]
        cmds.addAttr(poseLoc, ln = 'startAngle', at = 'double', dv = 45, keyable = True)
        # add vector attribute for saving pose
        cmds.addAttr(poseLoc, ln = driverJoint + '_poseX', at = 'double', keyable = False)
        cmds.addAttr(poseLoc, ln = driverJoint + '_poseY', at = 'double', keyable = False)
        cmds.addAttr(poseLoc, ln = driverJoint + '_poseZ', at = 'double', keyable = False)
        driverJointRot = cmds.xform(driverJoint, q = True, os = True, ro = True)
        cmds.setAttr('%s.%s_poseX' %(poseLoc, driverJoint), driverJointRot[0])
        cmds.setAttr('%s.%s_poseY' %(poseLoc, driverJoint), driverJointRot[1])
        cmds.setAttr('%s.%s_poseZ' %(poseLoc, driverJoint), driverJointRot[2])
        cmds.xform(poseLoc, ws = True, t = locatorJointPos)

        # parenting
        # if create pose corrective in first time...
        if not triggerLoc in cmds.listRelatives(baseLoc, c = True):
            cmds.parent(triggerLoc, baseLoc)
            cmds.parent(baseLoc, corLocGrp)
        cmds.parent(poseLoc, baseLoc)

        # constraint
        cmds.parentConstraint(childJoint, triggerLoc, mo = True)
        cmds.pointConstraint(driverJoint, baseLoc, mo = True)
        cmds.parentConstraint(parentJoint, baseLoc, skipTranslate=['x', 'y', 'z'], mo = True)

        # hide locator
        cmds.setAttr('%s.visibility' %baseLoc, 0)

        # Connect target
        poseReaderType = cmds.radioButtonGrp(UI.widgets['poseReaderRadioBtnGrp'], q=True, select=True)
        if poseReaderType == 1:  # RBF type driver
            if not cmds.pluginInfo('takRBF', q=True, loaded=True):
                cmds.loadPlugin('takRBF')

            rbfNode = '{0}_rbf'.format(parentJoint)
            if not cmds.objExists(rbfNode):
                cmds.createNode('takRBF', n=rbfNode)
                cmds.connectAttr('{0}.worldPosition'.format(getShape(triggerLoc)), '{0}.pose'.format(rbfNode))

            index = findMultiAttributeEmptyIndex(rbfNode, 'target')
            cmds.connectAttr('{0}.worldPosition'.format(getShape(poseLoc)), '{0}.target[{1}]'.format(rbfNode, index))
            cmds.connectAttr('{0}.outWeight[{1}]'.format(rbfNode, index), '{0}.{1}'.format(cls.bsNodeName, trgName))

        elif poseReaderType == 2:  # Angle type driver
            # create angle between node and remap value node
            anglBtwn = cmds.shadingNode('angleBetween', n = trgName + '_anglBtwn', asUtility = True)
            remapVal = cmds.shadingNode('remapValue', n = trgName + '_remapVal', asUtility = True)
            cmds.setAttr('%s.inputMax' %remapVal, 0)
            cmds.setAttr('%s.value[0].value_Interp' % remapVal, 1)
            cmds.setAttr('%s.value[1].value_Interp' % remapVal, 1)

            # connect attributes
            cmds.connectAttr('%s.translate' %triggerLoc, '%s.vector1' %anglBtwn, force = True)
            cmds.connectAttr('%s.translate' %poseLoc, '%s.vector2' %anglBtwn, force = True)
            cmds.connectAttr('%s.angle' %anglBtwn, '%s.inputValue' %remapVal, force = True)
            cmds.connectAttr('%s.startAngle' %poseLoc, '%s.inputMin' %remapVal, force = True)
            cmds.connectAttr('%s.outValue' %remapVal, '%s.%s' %(cls.bsNodeName, trgName), force = True)

        cls.populateCorrectiveTrgList()

    @classmethod
    def distDrvr(cls, *args):
        trgName = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)[0]
        drvrObj = cmds.textFieldButtonGrp(UI.widgets['drvrObjTexBtnGrp'], q = True, text = True)

        # create locators for measure distance
        poseLoc = cmds.spaceLocator(n = trgName + '_pose_loc')[0]
        cmds.addAttr(poseLoc, ln = 'startDist', at = 'double', keyable = True)
        prntCnst = cmds.parentConstraint(drvrObj, poseLoc, mo = False)
        cmds.delete(prntCnst)
        trigLoc = cmds.spaceLocator(n = trgName + '_trigger_loc')[0]
        prntCnst = cmds.parentConstraint(drvrObj, trigLoc, mo = False)
        cmds.delete(prntCnst)
        cmds.parentConstraint(drvrObj, trigLoc, mo = False)

        # create distance node and remapvalue node
        distNode = cmds.shadingNode('distanceBetween', n = trgName + '_DIST', asUtility = True)
        remapVal = cmds.shadingNode('remapValue', n = trgName + '_remapVal', asUtility = True)
        cmds.setAttr('%s.inputMax' %remapVal, 0)

        # connect attributes
        poseLocShp = cmds.listRelatives(poseLoc, s = True)[0]
        cmds.connectAttr('%s.worldPosition[0]' %poseLocShp, '%s.point1' %distNode)
        trigLocShp = cmds.listRelatives(trigLoc, s = True)[0]
        cmds.connectAttr('%s.worldPosition[0]' %trigLocShp, '%s.point2' %distNode)
        cmds.connectAttr('%s.distance' %distNode, '%s.inputValue' %remapVal, force = True)
        cmds.connectAttr('%s.startDist' %poseLoc, '%s.inputMin' %remapVal, force = True)
        cmds.connectAttr('%s.outValue' %remapVal, '%s.%s' %(cls.bsNodeName, trgName), force = True)

        cmds.setAttr('%s.translateX' %drvrObj, 0)
        cmds.setAttr('%s.translateY' %drvrObj, 0)
        cmds.setAttr('%s.translateZ' %drvrObj, 0)
        distVal = cmds.getAttr('%s.distance' %distNode)
        cmds.setAttr('%s.startDist' %poseLoc, distVal)

        cls.populateCorrectiveTrgList()


    @classmethod
    def addTrg(cls, *args):
        selList = cmds.ls(sl = True)

        bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
        if bsAttrList:
            # Get the highest weight number to query next index
            weightNumList = []
            for bsAttr in bsAttrList:
                if 'weight' in bsAttr:
                    reObj = re.search(r'\d+', bsAttr)
                    weightNum = reObj.group()
                    weightNumList.append(int(weightNum))
            bsIndex = max(weightNumList) + 1

            for sel in selList:
                cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.baseGeo, bsIndex, sel, 1.0))
                bsIndex += 1
        # If blend shape has no weight, start index should be 0
        else:
            for i in range(len(selList)):
                cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.baseGeo, i, selList[i], 1.0))

        cls.populateCorrectiveTrgList()


    @classmethod
    def setToCurPose(cls, *args):
        selLs = cmds.ls(sl = True)
        for sel in selLs:
            triggerLoc = re.sub('_pose', '_trigger', sel)
            triggerPos = cmds.xform(triggerLoc, q = True, t = True, ws = True)
            cmds.xform(sel, t = triggerPos, ws = True)

    @classmethod
    def preInfCnst(cls, *args):
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        for selTrg in selTrgList:
            cmds.setInfinity('%s.%s' %(cls.bsNodeName, selTrg), pri = 'constant')


    @classmethod
    def preInfCyc(cls, *args):
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        for selTrg in selTrgList:
            cmds.setInfinity('%s.%s' %(cls.bsNodeName, selTrg), pri = 'cycleRelative')


    @classmethod
    def postInfCnst(cls, *args):
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        for selTrg in selTrgList:
            cmds.setInfinity('%s.%s' %(cls.bsNodeName, selTrg), poi = 'constant')


    @classmethod
    def postInfCyc(cls, *args):
        selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

        for selTrg in selTrgList:
            cmds.setInfinity('%s.%s' %(cls.bsNodeName, selTrg), poi = 'cycleRelative')



class SdkObject(object):
    sdkWidgets = {}

    def __init__(self, layout, selObj, sdkType, selAttr = ''):
        self.prntLayout = layout
        self.selObj = selObj
        self.sdkType = sdkType
        self.selAttr = selAttr
        self.ui()
        self.popSdkOptMenu()


    def ui(self):
        self.sdkWidgets[self.selObj + 'sdkRowColLo'] = cmds.rowColumnLayout(w = 400, numberOfColumns = 4, columnWidth = [(1, 100), (2, 170), (3, 65), (4, 60)], columnOffset = [(1, 'left', 5), (3, 'left', 25), (4, 'left', 20)], columnAttach = [(4, 'right', 5)], p = self.prntLayout)
        self.sdkWidgets[self.selObj + 'sdkTxt'] = cmds.text(label = self.selObj)
        cmds.popupMenu()
        cmds.menuItem(label = 'Reload', c = self.reloadSdkObj)
        cmds.menuItem(label = 'Select', c = partial(self.selectSdkObj, self.selObj))
        # cmds.menuItem(label = 'Remove', c = partial(self.removeSdkObj, self.sdkWidgets[self.selObj + 'sdkRowColLo']))
        self.sdkWidgets[self.selObj + 'sdkOptMenu'] = cmds.optionMenu()
        self.sdkWidgets[self.selObj + 'sdkStartTxtFld'] = cmds.textField(text = 0)
        cmds.popupMenu()
        cmds.menuItem(label = 'Load Value', c = partial(self.loadVal, self.sdkWidgets[self.selObj + 'sdkStartTxtFld'], self.sdkWidgets[self.selObj + 'sdkTxt'], self.sdkWidgets[self.selObj + 'sdkOptMenu']))
        self.sdkWidgets[self.selObj + 'sdkEndTxtFld'] = cmds.textField(text = 0)
        cmds.popupMenu()
        cmds.menuItem(label = 'Load Value', c = partial(self.loadVal, self.sdkWidgets[self.selObj + 'sdkEndTxtFld'], self.sdkWidgets[self.selObj + 'sdkTxt'], self.sdkWidgets[self.selObj + 'sdkOptMenu']))
        if self.sdkType == 'driver':
            cmds.textField(self.sdkWidgets[self.selObj + 'sdkEndTxtFld'], e = True, text = 1)
        elif self.sdkType == 'driven':
            cmds.textField(self.sdkWidgets[self.selObj + 'sdkEndTxtFld'], e = True, text = 1)


    def popSdkOptMenu(self):
        # Remove already exists menu items
        menuItems = cmds.optionMenu(self.sdkWidgets[self.selObj + 'sdkOptMenu'], q = True, itemListLong = True)
        if menuItems:
            for menu in menuItems:
                cmds.deleteUI(menu)

        if cmds.objectType(self.selObj) == 'blendShape':
            attrList = cmds.listAttr('%s.w' %(self.selObj), multi = True)
        else:
            attrList = cmds.listAttr(self.selObj, k = True)
        for attr in attrList:
            cmds.menuItem(label = attr, p = self.sdkWidgets[self.selObj + 'sdkOptMenu'])

        if self.selAttr:
            cmds.optionMenu(self.sdkWidgets[self.selObj + 'sdkOptMenu'], e = True, value = self.selAttr)

            if cmds.objectType(self.selObj) == 'blendShape':
                self.loadVal(self.sdkWidgets[self.selObj + 'sdkEndTxtFld'], self.sdkWidgets[self.selObj + 'sdkTxt'], self.sdkWidgets[self.selObj + 'sdkOptMenu'])
            else:
                self.loadVal(self.sdkWidgets[self.selObj + 'sdkEndTxtFld'], self.sdkWidgets[self.selObj + 'sdkTxt'], self.sdkWidgets[self.selObj + 'sdkOptMenu'])


    def loadVal(self, txtFldName, objTxtName, optMenuName, *args):
        obj = cmds.text(objTxtName, q = True, label = True)
        attr = cmds.optionMenu(optMenuName, q = True, value = True)
        val = cmds.getAttr('%s.%s' %(obj, attr))
        val = round(val, 3)

        cmds.textField(txtFldName, e = True, text = val)


    def reloadSdkObj(self, *args):
        self.popSdkOptMenu()

    def selectSdkObj(self, selObj, *args):
        cmds.select(selObj, r = True)
