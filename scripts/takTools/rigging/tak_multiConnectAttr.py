"""
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script used to connect one attribute to the others.

Usage:
1. Copy this script and paste in your scripts folder.

2. In maya python tab, run following code.
import tak_multiConnectAttr
reload(tak_multiConnectAttr)
tak_multiConnectAttr.UI()
"""

import maya.cmds as cmds
from functools import partial
import re


def UI():
    winName = 'multiConnectAttrWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    cmds.window(winName, title='Multi Connect Attribute UI')

    cmds.columnLayout('mainColLay', adj=True)
    cmds.rowColumnLayout('mainRowColLo', numberOfColumns=2, columnSpacing=[(2, 10)])

    cmds.columnLayout('drvrColLay', adj=True)
    cmds.text(label='Driver Node')
    cmds.textField('drvrTxtFld')
    cmds.popupMenu()
    cmds.menuItem(label='Load Selected', c=partial(loadSel, 'drvrTxtFld'))
    cmds.text(label='Attributes')
    cmds.textFieldGrp(
        'drvrAttrsFilterTxtFldGrp',
        label='Search: ',
        columnWidth=[(1, 40)],
        tcc=partial(filterDirverAttrs, 'drvrTxtFld', 'drvrAttrsFilterTxtFldGrp', 'drvrAttrTxtScrLs')
    )
    cmds.textScrollList('drvrAttrTxtScrLs')

    cmds.setParent('mainRowColLo')
    cmds.columnLayout('drvnColLay', adj=True)
    cmds.text(label='Driven Nodes')
    cmds.textScrollList('drvnTxtScrList')
    cmds.popupMenu()
    cmds.menuItem(label='Load Selected', c=partial(loadSel, 'drvnTxtScrList'))
    cmds.menuItem(label='Add Selected', c=partial(addSel, 'drvnTxtScrList'))
    cmds.text(label='Attributes')
    cmds.textFieldGrp(
        'drvnAttrsFilterTxtFldGrp',
        label='Search: ',
        columnWidth=[(1, 40)],
        tcc=partial(filterDrivenAttrs, 'drvnTxtScrList', 'drvnAttrsFilterTxtFldGrp', 'drvnAttrTxtScrLs')
    )
    cmds.textScrollList('drvnAttrTxtScrLs')

    cmds.setParent('mainColLay')
    cmds.separator(h=5, style='none')
    cmds.button(label='Connect Attribute', h=60, c=connectAttr)

    cmds.window(winName, e=True, w=100, h=100)
    cmds.showWindow(winName)


def loadSel(widget, *args):
    selList = cmds.ls(sl=True)

    if widget == 'drvrTxtFld':
        cmds.textField(widget, e=True, text=selList[0])
        loadDriverAllAttrs()

    elif widget == 'drvnTxtScrList':
        txtScrItems = cmds.textScrollList(widget, q=True, allItems=True)
        if txtScrItems:
            cmds.textScrollList(widget, e=True, removeAll=True)
        cmds.textScrollList(widget, e=True, append=selList)
        loadDrivenAllAttrs()


def addSel(widget, *args):
    selList = cmds.ls(sl=True)
    preItems = cmds.textScrollList(widget, q=True, allItems=True)
    addedList = list(set(preItems) - set(selList))
    cmds.textScrollList(widget, e=True, append=addedList)


def connectAttr(*args):
    driver = cmds.textField('drvrTxtFld', q=True, text=True)
    driverAttr = cmds.textScrollList('drvrAttrTxtScrLs', q=True, selectItem=True)[0]
    drivens = cmds.textScrollList('drvnTxtScrList', q=True, allItems=True)
    drivenAttr = cmds.textScrollList('drvnAttrTxtScrLs', q=True, selectItem=True)[0]

    for driven in drivens:
        cmds.connectAttr('%s.%s' % (driver, driverAttr),
                         '%s.%s' % (driven, drivenAttr), f=True)


def loadDriverAllAttrs():
    nodeName = cmds.textField('drvrTxtFld', q=True, text=True)
    cmds.textScrollList('drvrAttrTxtScrLs', e=True, removeAll=True)
    allAttrs = sorted(cmds.listAttr(nodeName), key=lambda s: s.lower())
    cmds.textScrollList('drvrAttrTxtScrLs', e=True, append=allAttrs)


def loadDrivenAllAttrs():
    nodeName = cmds.textScrollList('drvnTxtScrList', q=True, allItems=True)[0]
    cmds.textScrollList('drvnAttrTxtScrLs', e=True, removeAll=True)
    allAttrs = sorted(cmds.listAttr(nodeName), key=lambda s: s.lower())
    cmds.textScrollList('drvnAttrTxtScrLs', e=True, append=allAttrs)


def filterDirverAttrs(drvrTxtFldWdg, drvrAttrsFilterTxtFldGrpWdg, drvrAttrsTxtScrWdg, *args):
    nodeName = cmds.textField(drvrTxtFldWdg, q=True, text=True)
    allAttrs = cmds.listAttr(nodeName)
    matchAttrs = []

    searchStr = cmds.textFieldGrp(drvrAttrsFilterTxtFldGrpWdg, q=True, text=True)
    for attr in allAttrs:
        if re.search(searchStr, attr, re.IGNORECASE):
            matchAttrs.append(attr)
    cmds.textScrollList(drvrAttrsTxtScrWdg, e=True, removeAll=True)
    cmds.textScrollList(drvrAttrsTxtScrWdg, e=True, append=matchAttrs)


def filterDrivenAttrs(drvnNodesTxtScrLsWdg, drvnAttrsFilterTxtFldGrpWdg, drvnAttrsTxtScrWdg, *args):
    nodeName = cmds.textScrollList(drvnNodesTxtScrLsWdg, q=True, allItems=True)[0]
    allAttrs = cmds.listAttr(nodeName, multi=True)
    matchAttrs = []

    searchStr = cmds.textFieldGrp(drvnAttrsFilterTxtFldGrpWdg, q=True, text=True)
    for attr in allAttrs:
        if re.search(searchStr, attr, re.IGNORECASE):
            matchAttrs.append(attr)
    cmds.textScrollList(drvnAttrsTxtScrWdg, e=True, removeAll=True)
    cmds.textScrollList(drvnAttrsTxtScrWdg, e=True, append=matchAttrs)
