
'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date:

Description:

Usage:

Requierements:
'''

import maya.cmds as cmds
from functools import partial
import re

class UI(object):
    widgets = {}
    widgets['winName'] = 'cmSdkWin'

    srch = 'lf_'
    rplc = 'rt_'

    @classmethod
    def __init__(cls):
        if cmds.window(cls.widgets['winName'], exists = True):
            cmds.deleteUI(cls.widgets['winName'])
        cls.ui()


    @classmethod
    def ui(cls):
        cmds.window(cls.widgets['winName'], title = 'Copy/Mirror SDK', mnb = False, mxb = False)

        cls.widgets['srcDrvrTabLo'] = cmds.tabLayout(tv = False)
        cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)

        cls.widgets['srcDrvrRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 150), (2, 150)], columnSpacing = [(2, 7)], p = cls.widgets['mainColLo'])
        cls.widgets['srcDrvrObjFrameLo'] = cmds.frameLayout(label = 'Source Driver Objects', p = cls.widgets['srcDrvrRowColLo'])
        cls.widgets['srcDrvrObjTxtScrList'] = cmds.textScrollList(allowMultiSelection = True, sc = Functions.txtScrSelCmd, p = cls.widgets['srcDrvrObjFrameLo'])
        cmds.popupMenu()
        cmds.menuItem(label = 'Load Selected', c = partial(Functions.loadSel, 'txtScrList', cls.widgets['srcDrvrObjTxtScrList']))
        cls.widgets['srcDrvrAttrFrameLo'] = cmds.frameLayout(label = 'Driver Attributes', labelIndent = 25, p = cls.widgets['srcDrvrRowColLo'])
        cls.widgets['srcDrvrAttrTxtScrList'] = cmds.textScrollList(allowMultiSelection = True, p = cls.widgets['srcDrvrAttrFrameLo'])

        cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

        cls.widgets['srcDrvnObjTxtFldBtnGrp'] = cmds.textFieldButtonGrp(label = 'Source Driven Object: ', buttonLabel = 'Load Sel', columnWidth = [(1, 110), (2, 140)], p = cls.widgets['mainColLo'])
        cmds.textFieldButtonGrp(cls.widgets['srcDrvnObjTxtFldBtnGrp'], e = True, bc = partial(Functions.loadSel, 'txtFld', cls.widgets['srcDrvnObjTxtFldBtnGrp']))

        cls.widgets['trgDrvrObjTxtFldBtnGrp'] = cmds.textFieldButtonGrp(label = 'Target Driver Object: ', buttonLabel = 'Load Sel', columnWidth = [(1, 110), (2, 140)], p = cls.widgets['mainColLo'])
        cmds.textFieldButtonGrp(cls.widgets['trgDrvrObjTxtFldBtnGrp'], e = True, bc = partial(Functions.loadSel, 'txtFld', cls.widgets['trgDrvrObjTxtFldBtnGrp']))
        cls.widgets['trgDrvnObjTxtFldBtnGrp'] = cmds.textFieldButtonGrp(label = 'Target Driven Object: ', buttonLabel = 'Load Sel', columnWidth = [(1, 110), (2, 140)], p = cls.widgets['mainColLo'])
        cmds.textFieldButtonGrp(cls.widgets['trgDrvnObjTxtFldBtnGrp'], e = True, bc = partial(Functions.loadSel, 'txtFld', cls.widgets['trgDrvnObjTxtFldBtnGrp']))

        cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

        cmds.text(label = 'Driver Object Search and Replace: ', align = 'left', p = cls.widgets['mainColLo'])
        cls.widgets['drvrObjSrchRplcRCLo'] = cmds.rowColumnLayout(numberOfColumns = 2, p = cls.widgets['mainColLo'])
        cls.widgets['drvrObjSrchTxtFldGrp'] = cmds.textFieldGrp(label = 'Search For: ', columnWidth = [(1, 60), (2, 50)], text = '', p = cls.widgets['drvrObjSrchRplcRCLo'])
        cls.widgets['drvrObjRplcTxtFldGrp'] = cmds.textFieldGrp(label = 'Replace With: ', columnWidth = [(1, 100), (2, 50)], text = '', p = cls.widgets['drvrObjSrchRplcRCLo'])
        cmds.text(label = 'Driver Attribute Search and Replace: ', align = 'left', p = cls.widgets['mainColLo'])
        cls.widgets['drvrAttrSrchRplcRCLo'] = cmds.rowColumnLayout(numberOfColumns = 2, p = cls.widgets['mainColLo'])
        cls.widgets['drvrAttrSrchTxtFldGrp'] = cmds.textFieldGrp(label = 'Search For: ', columnWidth = [(1, 60), (2, 50)], text = '', p = cls.widgets['drvrAttrSrchRplcRCLo'])
        cls.widgets['drvrAttrRplcTxtFldGrp'] = cmds.textFieldGrp(label = 'Replace With: ', columnWidth = [(1, 100), (2, 50)], text = '', p = cls.widgets['drvrAttrSrchRplcRCLo'])

        cmds.text(label = 'Driven Object Search and Replace: ', align = 'left', p = cls.widgets['mainColLo'])
        cls.widgets['drvnObjSrchRplcRCLo'] = cmds.rowColumnLayout(numberOfColumns = 2, p = cls.widgets['mainColLo'])
        cls.widgets['drvnObjSrchTxtFldGrp'] = cmds.textFieldGrp(label = 'Search For: ', columnWidth = [(1, 60), (2, 50)], text = '', p = cls.widgets['drvnObjSrchRplcRCLo'])
        cls.widgets['drvnObjRplcTxtFldGrp'] = cmds.textFieldGrp(label = 'Replace With: ', columnWidth = [(1, 100), (2, 50)], text = '', p = cls.widgets['drvnObjSrchRplcRCLo'])
        cmds.text(label = 'Driven Attribute Search and Replace: ', align = 'left', p = cls.widgets['mainColLo'])
        cls.widgets['drvnAttrSrchRplcRCLo'] = cmds.rowColumnLayout(numberOfColumns = 2, p = cls.widgets['mainColLo'])
        cls.widgets['drvnAttrSrchTxtFldGrp'] = cmds.textFieldGrp(label = 'Search For: ', columnWidth = [(1, 60), (2, 50)], text = '', p = cls.widgets['drvnAttrSrchRplcRCLo'])
        cls.widgets['drvnAttrRplcTxtFldGrp'] = cmds.textFieldGrp(label = 'Replace With: ', columnWidth = [(1, 100), (2, 50)], text = '', p = cls.widgets['drvnAttrSrchRplcRCLo'])

        cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

        cls.widgets['copyBhvrChkBoxGrp'] = cmds.checkBox(p = cls.widgets['mainColLo'], label = 'Copied Behavior', cc = Functions.copyBehaviorCC)
        cls.widgets['mirBhvrChkBoxGrp'] = cmds.checkBox(p = cls.widgets['mainColLo'], label = 'Mirrored Behavior', cc = Functions.mirBehaviorCC)
        cls.widgets['trnsMirChkBoxGrp'] = cmds.checkBoxGrp(numberOfCheckBoxes = 3, label = 'Translate Reverse:' , labelArray3 = ['X', 'Y', 'Z'], columnWidth = [(1, 95), (2, 50), (3, 50), (4, 50)], p = cls.widgets['mainColLo'])
        cls.widgets['rotateMirChkBoxGrp'] = cmds.checkBoxGrp(numberOfCheckBoxes = 3, label = 'Rotate Reverse:' , labelArray3 = ['X', 'Y', 'Z'], columnWidth = [(1, 95), (2, 50), (3, 50), (4, 50)], p = cls.widgets['mainColLo'])

        cmds.button(label = 'Apply', h = 30, c = partial(Functions.main, False), p = cls.widgets['mainColLo'])

        cmds.window(cls.widgets['winName'], e = True, w = 300, h = 150)
        cmds.showWindow(cls.widgets['winName'])



class Functions(object):
    @classmethod
    def main(cls, *args):
        srcDrvrs = cmds.textScrollList(UI.widgets['srcDrvrObjTxtScrList'], q = True, selectItem = True)
        spcfSrcDrvn = cmds.textFieldButtonGrp(UI.widgets['srcDrvnObjTxtFldBtnGrp'], q = True, text = True)
        spcfTrgDrvr = cmds.textFieldButtonGrp(UI.widgets['trgDrvrObjTxtFldBtnGrp'], q = True, text = True)
        spcfTrgDrvn = cmds.textFieldButtonGrp(UI.widgets['trgDrvnObjTxtFldBtnGrp'], q = True, text = True)

        drvrObjSrch = cmds.textFieldGrp(UI.widgets['drvrObjSrchTxtFldGrp'], q = True, text = True)
        drvrObjRplc = cmds.textFieldGrp(UI.widgets['drvrObjRplcTxtFldGrp'], q = True, text = True)
        drvrAttrSrch = cmds.textFieldGrp(UI.widgets['drvrAttrSrchTxtFldGrp'], q = True, text = True)
        drvrAttrRplc = cmds.textFieldGrp(UI.widgets['drvrAttrRplcTxtFldGrp'], q = True, text = True)

        drvnObjSrch = cmds.textFieldGrp(UI.widgets['drvnObjSrchTxtFldGrp'], q = True, text = True)
        drvnObjRplc = cmds.textFieldGrp(UI.widgets['drvnObjRplcTxtFldGrp'], q = True, text = True)
        drvnAttrSrch = cmds.textFieldGrp(UI.widgets['drvnAttrSrchTxtFldGrp'], q = True, text = True)
        drvnAttrRplc = cmds.textFieldGrp(UI.widgets['drvnAttrRplcTxtFldGrp'], q = True, text = True)

        trnsMirXOpt = cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], q = True, value1 = True)
        trnsMirYOpt = cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], q = True, value2 = True)
        trnsMirZOpt = cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], q = True, value3 = True)

        rotateMirXOpt = cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], q = True, value1 = True)
        rotateMirYOpt = cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], q = True, value2 = True)
        rotateMirZOpt = cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], q = True, value3 = True)

        mirBhvrOpt = cmds.checkBox(UI.widgets['mirBhvrChkBoxGrp'], q = True, value = True)
        copyBhvrOpt = cmds.checkBox(UI.widgets['copyBhvrChkBoxGrp'], q = True, value = True)

        trnsMirXVal = 1
        trnsMirYVal = 1
        trnsMirZVal = 1

        if trnsMirXOpt:
            trnsMirXVal = -1
        if trnsMirYOpt:
            trnsMirYVal = -1
        if trnsMirZOpt:
            trnsMirZVal = -1

        rotateMirXVal = 1
        rotateMirYVal = 1
        rotaeMirZVal = 1

        if rotateMirXOpt:
            rotateMirXVal = -1
        if rotateMirYOpt:
            rotateMirYVal = -1
        if rotateMirZOpt:
            rotaeMirZVal = -1

        # Get diver and driven object and attributes.
        drvrAttrList = cmds.textScrollList(UI.widgets['srcDrvrAttrTxtScrList'], q = True, selectItem = True)
        for srcDrvr in srcDrvrs:
            for drvrAttr in drvrAttrList:
                animCrvNodes = cmds.listConnections('%s.%s' %(srcDrvr, drvrAttr), scn = True, d = True, s = False, type='animCurve')
                if animCrvNodes:
                    for animNode in animCrvNodes:
                        conNodes = cmds.listConnections(animNode, scn = True, d = True, s = False)
                        if not conNodes:
                            continue

                        # Process for conected nodes on animation curve node to find target driven object and attributes.
                        if  len(conNodes) == 1 and 'hyperLayout' in str(conNodes):
                            continue
                        # Remove 'hyperLayout' node in conNodes
                        conNodes = cls.rmvHpLoInLs(conNodes)

                        for node in conNodes:
                            if cmds.objectType(node) == 'blendWeighted':
                                dNodes = cmds.listConnections(node, scn = True, d = True, s = False, plugs = True) # Destination nodes
                                # When blendWeighted nodes destination is multiple.
                                if len(dNodes) > 1:
                                    srcDrvn = cls.rmvHpLoInLs(dNodes)[0].split('.')[0]
                                    drvnAttr = cls.rmvHpLoInLs(dNodes)[0].split('.')[-1]
                                else:
                                    srcDrvn = cmds.listConnections(node, scn = True, d = True, s = False, plugs = True)[0].split('.')[0]
                                    drvnAttr = cmds.listConnections(node, scn = True, d = True, s = False, plugs = True)[0].split('.')[-1]
                            elif cmds.objectType(node) == 'transform':
                                srcDrvn = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True, type = 'transform')[0].split('.')[0]
                                drvnAttr = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True, type = 'transform')[0].split('.')[-1]
                            elif cmds.objectType(node) == 'blendShape':
                                srcDrvn = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True)[0].split('.')[0]
                                drvnAttr = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True)[0].split('.')[-1]
                            elif cmds.objectType(node) == 'parentConstraint':
                                srcDrvn = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True, type = 'parentConstraint')[0].split('.')[0]
                                drvnAttr = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True, type = 'parentConstraint')[0].split('.')[-1]
                            elif cmds.objectType(node) == 'joint':
                                srcDrvn = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True, type = 'joint')[0].split('.')[0]
                                drvnAttr = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True, type = 'joint')[0].split('.')[-1]
                            else:
                                srcDrvn = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True)[0].split('.')[0]
                                drvnAttr = cmds.listConnections(animNode, scn = True, d = True, s = False, plugs = True)[0].split('.')[-1]

                        # If specific source driven object exists, process for only specific source driven object.
                        if spcfSrcDrvn and not spcfSrcDrvn in srcDrvn:
                            continue

                        # Search and replace string to define target objects automatically.
                        if drvrObjSrch:
                            trgDrvr = re.sub(drvrObjSrch, drvrObjRplc, srcDrvr)
                        if drvrAttrSrch:
                            drvrAttr = re.sub(drvrAttrSrch, drvrAttrRplc, drvrAttr)
                        if drvnObjSrch:
                            trgDrvn = re.sub(drvnObjSrch, drvnObjRplc, srcDrvn)
                            # When there is no target driven object skip to the next animCurve.
                            if srcDrvn == trgDrvn:
                                continue
                        if drvnAttrSrch:
                            drvnAttr = re.sub(drvnAttrSrch, drvnAttrRplc, drvnAttr)

                        # If specific target object exists, replace target objects.
                        if spcfTrgDrvn:
                            trgDrvn = spcfTrgDrvn
                        if spcfTrgDrvr:
                            trgDrvr = spcfTrgDrvr

                        # Get driver and driven value with animation curve node.
                        drvrVals = cmds.keyframe(animNode, q = True, fc = True)
                        drvnVals = cmds.keyframe(animNode, q = True, vc = True)


                        for i in xrange(len(drvrVals)):
                            drvrVal = drvrVals[i]
                            drvnVal = drvnVals[i]

                            # Set driven key with origianl value.

                            if 'scale' in drvnAttr:
                                cmds.setDrivenKeyframe('%s.%s' %(trgDrvn, drvnAttr), cd = '%s.%s' %(trgDrvr, drvrAttr), dv = drvrVal , v = drvnVal)
                                continue

                            if 'translateX' in drvnAttr:
                                drvnVal = drvnVals[i]  * trnsMirXVal
                            if 'translateY' in drvnAttr:
                                drvnVal = drvnVals[i]  * trnsMirYVal
                            if 'translateZ' in drvnAttr:
                                drvnVal = drvnVals[i]  * trnsMirZVal

                            if 'rotateX' in drvnAttr:
                                drvnVal = drvnVals[i]  * rotateMirXVal
                            if 'rotateY' in drvnAttr:
                                drvnVal = drvnVals[i]  * rotateMirYVal
                            if 'rotateZ' in drvnAttr:
                                drvnVal = drvnVals[i]  * rotaeMirZVal

                            cmds.setDrivenKeyframe('%s.%s' %(trgDrvn, drvnAttr), cd = '%s.%s' %(trgDrvr, drvrAttr), dv = drvrVal , v = drvnVal)

                            # Set driven key with mirrored value.


    @classmethod
    def loadSel(cls, wdgType, wdgName, *args):
        selList = cmds.ls(sl = True)
        if wdgType == 'txtScrList':
            if cmds.textScrollList(wdgName, q = True, allItems = True):
                cmds.textScrollList(wdgName, e = True, removeAll = True)
            cmds.textScrollList(wdgName, e = True, append = selList)

        elif wdgType == 'txtFld':
            cmds.textFieldButtonGrp(wdgName, e = True, text = selList[0])


    @classmethod
    def txtScrSelCmd(cls, *args):
        selItem = cmds.textScrollList(UI.widgets['srcDrvrObjTxtScrList'], q = True, selectItem = True)

        attrs = cmds.listAttr(selItem, keyable = True)

        if cmds.textScrollList(UI.widgets['srcDrvrAttrTxtScrList'], q = True, allItems = True):
            cmds.textScrollList(UI.widgets['srcDrvrAttrTxtScrList'], e = True, removeAll = True)

        # Remove repeated items
        attrs = list(set(attrs))
        attrs.sort()

        cmds.textScrollList(UI.widgets['srcDrvrAttrTxtScrList'], e = True, append = attrs)


    @staticmethod
    def copyBehaviorCC(*args):
        '''
        Copy behavior checkbox change command.
        '''

        copyBhvrOpt = cmds.checkBox(UI.widgets['copyBhvrChkBoxGrp'], q = True, value = True)

        if copyBhvrOpt:
            cmds.checkBox(UI.widgets['mirBhvrChkBoxGrp'], e = True, value = False)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value1 = True)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value2 = False)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value3 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value1 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value2 = True)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value3 = True)
        else:
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value1 = False)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value2 = False)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value3 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value1 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value2 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value3 = False)


    @staticmethod
    def mirBehaviorCC(*args):
        '''
        Mirror behavior checkbox change command.
        '''

        mirBhvrOpt = cmds.checkBox(UI.widgets['mirBhvrChkBoxGrp'], q = True, value = True)

        if mirBhvrOpt:
            cmds.checkBox(UI.widgets['copyBhvrChkBoxGrp'], e = True, value = False)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value1 = True)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value2 = True)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value3 = True)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value1 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value2 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value3 = False)
        else:
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value1 = False)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value2 = False)
            cmds.checkBoxGrp(UI.widgets['trnsMirChkBoxGrp'], e = True, value3 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value1 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value2 = False)
            cmds.checkBoxGrp(UI.widgets['rotateMirChkBoxGrp'], e = True, value3 = False)


    @classmethod
    def rmvHpLoInLs(cls, nodeLs):
        """
        Remove hyperLayout' node in given list.
        """

        cleanLs = []

        for node in nodeLs:
            if cmds.nodeType(node) == 'hyperLayout':
                continue
            else:
                cleanLs.append(node)

        return cleanLs

