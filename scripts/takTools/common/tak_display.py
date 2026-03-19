"""
Author: Sangtak Lee
Contact: https://ta-note.com

Description:
Display, color, and viewport related utility functions.
Separated from tak_misc.py for better organization.
"""

from functools import partial

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from . import tak_lib


def Wire():
    selList = cmds.ls(sl=True)
    selListShape = cmds.listRelatives(selList, s=True, c=True)
    for sel in selListShape:
        if cmds.getAttr('%s.overrideEnabled' % (sel)):
            cmds.setAttr('%s.overrideShading' % (sel), 1)
            cmds.setAttr('%s.overrideEnabled' % (sel), 0)
        else:
            cmds.setAttr('%s.overrideEnabled' % (sel), 1)
            cmds.setAttr('%s.overrideShading' % (sel), 0)
            cmds.setAttr('%s.overrideColor' % (sel), 1)


def wireOnOff():
    wsaState = cmds.displayPref(q=True, wsa=True)
    if wsaState in ['full', 'reduced']:
        cmds.displayPref(wsa='none')
    else:
        cmds.displayPref(wsa='full')


def iso():
    selList = cmds.ls(sl=True)
    if selList:
        cmds.InvertSelection()
    invSel = cmds.ls(sl=True)

    curPanel = cmds.getPanel(withFocus=True)
    curIsoState = cmds.isolateSelect(curPanel, q=True, state=True)

    if curIsoState:
        cmds.headsUpDisplay('isoDisplay', remove=True)
        cmds.isolateSelect(curPanel, state=False)
        mel.eval('isoSelectAutoAddNewObjs %s false;' % curPanel)
        cmds.select(cl=True)
    else:
        tak_lib.showHUD('isoDisplay', 'Isolate Mode')
        cmds.isolateSelect(curPanel, state=True)
        mel.eval('isoSelectAutoAddNewObjs %s true;' % curPanel)

        cmds.select(selList, r=True)
        cmds.isolateSelect(curPanel, addSelected=True)

        if invSel:
            cmds.select(invSel, r=True)
            cmds.isolateSelect(curPanel, removeSelected=True)

        cmds.select(cl=True)


def isoAdd():
    curPanel = cmds.getPanel(withFocus=True)
    cmds.isolateSelect(curPanel, addSelected=True)


def isoRmv():
    curPanel = cmds.getPanel(withFocus=True)
    cmds.isolateSelect(curPanel, removeSelected=True)


def hideShowViewPoly():
    curPanel = cmds.getPanel(withFocus=True)
    state = cmds.modelEditor(curPanel, q=True, polymeshes=True)
    if state:
        cmds.modelEditor(curPanel, e=True, polymeshes=False)
    else:
        cmds.modelEditor(curPanel, e=True, polymeshes=True)


def hideShowViewJnt():
    curPanel = cmds.getPanel(withFocus=True)
    state = cmds.modelEditor(curPanel, q=True, joints=True)
    if state:
        cmds.modelEditor(curPanel, e=True, joints=False)
    else:
        cmds.modelEditor(curPanel, e=True, joints=True)


def hideShowViewCrv():
    curPanel = cmds.getPanel(withFocus=True)
    state = cmds.modelEditor(curPanel, q=True, nurbsCurves=True)
    if state:
        cmds.modelEditor(curPanel, e=True, nurbsCurves=False)
    else:
        cmds.modelEditor(curPanel, e=True, nurbsCurves=True)


def hideShowViewWire():
    curPanel = cmds.getPanel(withFocus=True)
    state = cmds.modelEditor(curPanel, q=True, sel=True)
    if state:
        cmds.modelEditor(curPanel, e=True, sel=False)
    else:
        cmds.modelEditor(curPanel, e=True, sel=True)


def hideShowViewMdl():
    curPanel = cmds.getPanel(withFocus=True)
    state = cmds.modelEditor(curPanel, q=True, clipGhosts=True)
    if state:
        cmds.modelEditor(curPanel, e=True, allObjects=False)
        cmds.modelEditor(curPanel, e=True, polymeshes=True)
    else:
        cmds.modelEditor(curPanel, e=True, allObjects=True)


def turnOffShp():
    selList = cmds.ls(sl=True)
    for sel in selList:
        shp = cmds.listRelatives(sel, s=True)[0]
        cmds.setAttr("%s.visibility" % (shp), False)


def drawJntStyle():
    if cmds.window('JSWin', exists=True):
        cmds.deleteUI('JSWin')
    cmds.window('JSWin', title='Draw Joint Style', maximizeButton=False, minimizeButton=False)
    cmds.columnLayout()
    cmds.optionMenu('jsOptMenu', label='Draw Style: ', cc=djsChangeCmd)
    cmds.menuItem(label='None')
    cmds.menuItem(label='Bone')
    cmds.showWindow('JSWin')


def djsChangeCmd(*args):
    opt = cmds.optionMenu('jsOptMenu', q=True, v=True)
    if opt == 'None': opt = 2
    if opt == 'Bone': opt = 0
    selList = cmds.ls(sl=True)
    for sel in selList:
        if cmds.objectType(sel) == 'joint':
            cmds.setAttr('%s.drawStyle' % sel, opt)


class SelHilightTogg:
    switch = 0

    def UI(self):
        win = 'selHilTog'
        if cmds.window(win, exists=True):
            cmds.deleteUI(win)
        cmds.window(win, title='Selection Hilighting', maximizeButton=False, minimizeButton=False)
        cmds.columnLayout(adj=True)
        cmds.button(label='On/Off', c=self.onOff)
        cmds.showWindow(win)

    def onOff(self, *args):
        curPanel = cmds.getPanel(withFocus=True)
        if SelHilightTogg.switch:
            cmds.modelEditor(curPanel, e=True, sel=False)
            self.switch = 0
        else:
            cmds.modelEditor(curPanel, e=True, sel=True)
            self.switch = 1


def setShapeColorRGB():
    cmds.colorEditor()
    if cmds.colorEditor(query=True, result=True):
        values = cmds.colorEditor(query=True, rgb=True)
    else:
        return

    for sel in pm.selected():
        shapes = sel.getShapes()
        if shapes:
            for shape in shapes:
                shape.overrideEnabled.set(True)
                shape.overrideRGBColors.set(True)
                shape.overrideColorRGB.set(values)


def setJntColorUI():
    winName = 'setJntCol'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    cmds.window(winName, title='Wire Color Override', maximizeButton=False, minimizeButton=False)
    cmds.columnLayout(columnAttach=('both', 5), backgroundColor=[.2, .2, .2], adj=True)
    colorSwatchMenu = cmds.gridLayout(aec=False, numberOfRowsColumns=(10, 3), cwh=(40, 24),
                                      backgroundColor=[.2, .2, .2])
    colorSwatchesList = [1, 2, 3,
                         11, 24, 21,
                         12, 10, 25,
                         4, 13, 20,
                         8, 30, 9,
                         5, 6, 18,
                         15, 29, 28,
                         7, 27, 19,
                         23, 26, 14,
                         17, 22, 16]

    for i in colorSwatchesList:
        colorBuffer = cmds.colorIndex(i, q=True)
        cmds.canvas(('%s%i' % ('colorCanvas_', i)), rgb=colorBuffer, pc=partial(setJntColor, i))

    cmds.window(winName, e=True, w=10, h=10)
    cmds.showWindow(winName)


def setJntColor(color, *args):
    selList = cmds.ls(sl=True)
    for x in selList:
        shps = cmds.listRelatives(x, s=True)
        if shps:
            for shp in shps:
                cmds.setAttr('%s|%s.overrideEnabled' % (x, shp), 1)
                cmds.setAttr('%s|%s.overrideColor' % (x, shp), int(color))
        else:
            cmds.setAttr('%s.overrideEnabled' % (x), 1)
            cmds.setAttr('%s.overrideColor' % (x), int(color))


def displayType():
    if cmds.window('dtWin', exists=True):
        cmds.deleteUI('dtWin')
    cmds.window('dtWin', title='Display Type', maximizeButton=False, minimizeButton=False)
    cmds.columnLayout()
    cmds.optionMenu('dtOptMenu', label='Display Type: ', cc=dtChangeCmd)
    cmds.menuItem(label='Normal')
    cmds.menuItem(label='Template')
    cmds.menuItem(label='Reference')
    cmds.showWindow('dtWin')


def dtChangeCmd(*args):
    opt = cmds.optionMenu('dtOptMenu', q=True, v=True)
    if opt == 'Normal':
        opt = 0
    elif opt == 'Template':
        opt = 1
    elif opt == 'Reference':
        opt = 2
    selList = cmds.ls(sl=True)
    for sel in selList:
        if cmds.nodeType(sel) == 'joint':
            cmds.setAttr('%s.overrideEnabled' % sel, 1)
            cmds.setAttr('%s.overrideDisplayType' % sel, opt)
        else:
            shps = cmds.listRelatives(sel, s=True)
            for shp in shps:
                try:
                    cmds.setAttr('%s.overrideEnabled' % shp, 1)
                except:
                    pass
                try:
                    cmds.setAttr('%s.overrideDisplayType' % shp, opt)
                except:
                    cmds.error('Same shape name exists.')


def lineWidth():
    if cmds.window('lwWin', exists=True):
        cmds.deleteUI('lwWin')
    cmds.window('lwWin', title='Line Width', maximizeButton=False, minimizeButton=False)
    cmds.columnLayout(adj=True)
    cmds.floatSliderGrp('lwFSlider', label='Line Width: ', field=True, minValue=1.0, maxValue=10.0, fieldMinValue=1.0,
                        fieldMaxValue=20.0, value=1.0, step=0.1, dc=changeLineWidth)
    cmds.window('lwWin', e=True, w=200, h=20)
    cmds.showWindow('lwWin')


def changeLineWidth(*args):
    lwVal = cmds.floatSliderGrp('lwFSlider', q=True, v=True)
    cmds.displayPref(lineWidth=lwVal)


def useDfltMat():
    curPanel = cmds.getPanel(withFocus=True)
    curUdmState = cmds.modelEditor(curPanel, q=True, udm=True)
    if curUdmState:
        cmds.modelEditor(curPanel, e=True, udm=False)
    else:
        cmds.modelEditor(curPanel, e=True, udm=True)


def combinedTexture(*args):
    selObjs = cmds.ls(sl=True)

    for obj in selObjs:
        shaderNode = tak_lib.getMatFromSel(obj)[0]
        if cmds.objExists(shaderNode):
            materialInfoNode = cmds.ls(cmds.listConnections(shaderNode), type='materialInfo')[-1]
            try:
                cmds.connectAttr('%s.message' % shaderNode, '%s.texture' % materialInfoNode, nextAvailable=True)
            except:
                pass
