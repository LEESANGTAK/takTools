"""
Author: Sangtak Lee
Contact: https://ta-note.com

Description:
Mirror related utility functions.
Separated from tak_misc.py for better organization.
"""

import re

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from ..modeling import tak_cleanUpModel


def mirJntUi():
    if cmds.window('mjWin', exists=True):
        cmds.deleteUI('mjWin')
    cmds.window('mjWin', title='Mirror Joint', maximizeButton=False, minimizeButton=False)

    cmds.columnLayout('mainColLay', adj=True)

    cmds.checkBox('mirFuncChkBox', label='Behavior')
    cmds.checkBox('inverseScaleXChkBox', label='Inverse X-Axis')

    cmds.separator(h=10, style='in')

    cmds.textFieldGrp('srchTxtFldGrp', label='Search For: ', columnWidth=[(1, 70), (2, 50)], text='_L')
    cmds.textFieldGrp('rplcTxtFldGrp', label='Replace With: ', columnWidth=[(1, 70), (2, 50)], text='_R')

    cmds.button(label='Mirror', h=50, c=mirrorJnt)

    cmds.window('mjWin', e=True, w=100, h=100)
    cmds.showWindow('mjWin')


def mirrorJnt(*args):
    mirFuncOpt = cmds.checkBox('mirFuncChkBox', q=True, v=True)
    invScaleX = cmds.checkBox('inverseScaleXChkBox', q=True, v=True)
    srchStr = cmds.textFieldGrp('srchTxtFldGrp', q=True, text=True)
    rplcStr = cmds.textFieldGrp('rplcTxtFldGrp', q=True, text=True)

    joints = cmds.ls(sl=True, type='joint')
    cmds.select(cl=True)

    tempJnt = cmds.createNode('joint', n='tmp_root_jnt')
    for srcJnt in joints:
        parentSrcJnt = cmds.listRelatives(srcJnt, parent=True)
        cmds.parent(srcJnt, tempJnt)

        if invScaleX:
            cmds.select(srcJnt, r=True)
            miredJnt = cmds.mirrorJoint(mirrorYZ=True, mirrorBehavior=mirFuncOpt, searchReplace=(srchStr, rplcStr))
            mirrorYZPlane(srcJnt, miredJnt)
        else:
            cmds.select(srcJnt, r=True)
            miredJnt = cmds.mirrorJoint(mirrorYZ=True, mirrorBehavior=mirFuncOpt, searchReplace=(srchStr, rplcStr))

        if parentSrcJnt:
            cmds.parent([srcJnt, miredJnt[0]], parentSrcJnt[0])
        else:
            cmds.parent([srcJnt, miredJnt[0]], w=True)

    cmds.delete(tempJnt)


def mirrorYZPlane(src, trg):
    src = pm.PyNode(src)

    srcMat = src.worldMatrix.get()
    worldXInvMat = [
        -1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]

    trgMat = srcMat * pm.dt.Matrix(worldXInvMat)
    pm.xform(trg, matrix=trgMat, ws=True)


def mirObjUi():
    '''
    Mirror object ui.
    '''

    winName = 'mirObjWin'

    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    cmds.window(winName, title='Mirror Object', maximizeButton=False, minimizeButton=False)

    cmds.columnLayout('mainColLo', adj=True)
    cmds.radioButtonGrp('typeRadBtnGrp', label='Type: ', labelArray2=['Mesh', 'Control'], numberOfRadioButtons=2,
                        columnWidth=[(1, 70), (2, 70)], select=1, cc=typeRadBtnGrpCC)

    cmds.columnLayout('mirBehaviorColLo', adj=True, visible=False)
    cmds.checkBox('mirBehaviorChkBox', label='Mirror Behavior')
    cmds.setParent('|')

    cmds.textFieldGrp('srchTxtFldGrp', label='Search for: ', text='_L', columnWidth=[1, 70])
    cmds.textFieldGrp('rplcTxtFldGrp', label='Replace with', text='_R', columnWidth=[1, 70])
    cmds.button(label='Apply', h=50, c=mirrorObj)

    cmds.window(winName, e=True, w=100, h=100)
    cmds.showWindow(winName)


def typeRadBtnGrpCC(*args):
    """Obtaining the Selection Type to determine layout visibility"""
    selType = cmds.radioButtonGrp('typeRadBtnGrp', q=True, select=True)
    cmds.columnLayout('mirBehaviorColLo', e=True, visible=selType==2)


def mirrorObj(*args):
    # Options
    selType = cmds.radioButtonGrp('typeRadBtnGrp', q=True, select=True)
    mirBehaviorOpt = cmds.checkBox('mirBehaviorChkBox', q=True, v=True)
    srchTxt = cmds.textFieldGrp('srchTxtFldGrp', q=True, text=True)
    rplcTxt = cmds.textFieldGrp('rplcTxtFldGrp', q=True, text=True)

    selList = cmds.ls(sl=True)

    for each in selList:
        dupObjLs = []

        newName = re.sub(srchTxt, rplcTxt, each)

        # Duplicate
        dupObjLs.extend(cmds.duplicate(each, n=newName, renameChildren=True))

        if selType == 1:  # In case selected object is mesh.
            # Filp duplicated object to opposite x side.
            cmds.select(cmds.listRelatives(newName, s=False))
            tak_cleanUpModel.allInOne()

            if not cmds.getAttr('%s.inheritsTransform' % newName):
                cmds.setAttr('%s.inheritsTransform' % newName, 1)

            cmds.select(newName, r=True)
            mel.eval('doGroup 0 1 1;')
            groupName = cmds.ls(sl=True)
            cmds.setAttr("%s.scaleX" % (groupName[0]), -1)

            cmds.parent(newName, w=True)
            cmds.delete(groupName)
            cmds.makeIdentity(newName, apply=True, pn=True)

            # Parent to the same parent node of each
            eachPrnt = cmds.listRelatives(each, p=True)
            if eachPrnt:
                cmds.parent(newName, eachPrnt)

            # Rename child objects
            newChldLs = cmds.listRelatives(newName, ad=True, type='transform')
            if newChldLs:
                for chld in newChldLs:
                    newName = re.sub(srchTxt, rplcTxt, chld)
                    try:
                        newName = re.match(r'(.*)(\\d+)', newName).group(1)
                    except:
                        pass
                    cmds.rename(chld, newName)
                    dupObjLs.append(newName)

            cmds.select(dupObjLs, r=True)
            tak_cleanUpModel.allInOne()
            try:
                cmds.parent(dupObjLs, world=True)
            except:
                pass

        elif selType == 2:  # In case selected object is control.
            if mirBehaviorOpt:
                cmds.select(cl=True)
                tmp1Jnt = cmds.joint()
                cmds.CompleteCurrentTool()
                cmds.delete(cmds.parentConstraint(each, tmp1Jnt, mo=False))

                miredJnt = cmds.mirrorJoint(tmp1Jnt, mirrorYZ=True, mirrorBehavior=True)
                cmds.delete(cmds.parentConstraint(miredJnt, newName, mo=False))

                cmds.delete(tmp1Jnt, miredJnt)

            else:
                cmds.select(newName, r=True)
                mel.eval('doGroup 0 1 1;')
                groupName = cmds.ls(sl=True)
                cmds.setAttr("%s.scaleX" % (groupName[0]), -1)

                cmds.parent(newName, w=True)
                cmds.delete(groupName)

            # Rename child objects
            newChldLs = cmds.listRelatives(newName, ad=True, type='transform')
            if newChldLs:
                for chld in newChldLs:
                    newName = re.sub(srchTxt, rplcTxt, chld)
                    # Clear int if exists.
                    try:
                        newName = re.match(r'(.*)(\\d+)', newName).group(1)
                    except:
                        pass
                    cmds.rename(chld, newName)


def mirCtrlShapeUi():
    winName = 'mirConWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    cmds.window(winName, title='Mirror Controls UI', maximizeButton=False, minimizeButton=False)

    cmds.columnLayout('mainClLo', adj=True)
    cmds.textFieldGrp('srchTxtFld', label='Search: ', text='_L', columnWidth=[(1, 50), (2, 50)])
    cmds.textFieldGrp('rplcTxtFld', label='Replace: ', text='_R', columnWidth=[(1, 50), (2, 50)])
    cmds.button(label='Apply', h=30, c=mirCtrlShape)

    cmds.window(winName, e=True, w=100, h=50)
    cmds.showWindow(winName)


def mirCtrlShape(*args):
    srch = cmds.textFieldGrp('srchTxtFld', q=True, text=True)
    rplc = cmds.textFieldGrp('rplcTxtFld', q=True, text=True)

    cons = cmds.ls(sl=True)
    for con in cons:
        symCtrl = re.sub(srch, rplc, con)
        conPos = cmds.xform(con, q=True, t=True, ws=True)
        cmds.xform(symCtrl, t=[-conPos[0], conPos[1], conPos[2]], ws=True)
        symCtrlShps = cmds.listRelatives(symCtrl, ad=True, type='nurbsCurve')
        shpList = cmds.listRelatives(con, ad=True, type='nurbsCurve')
        for i in range(len(shpList)):
            degs = cmds.getAttr('%s.degree' % shpList[i])
            spans = cmds.getAttr('%s.spans' % shpList[i])
            cvs = degs + spans
            for ii in range(cvs):
                cvTr = cmds.xform('%s.cv[%d]' % (shpList[i], ii), q=True, t=True, ws=True)
                cmds.xform('%s.cv[%d]' % (symCtrlShps[i], ii), t=(cvTr[0] * -1, cvTr[1], cvTr[2]), ws=True)


def mirConSel(*args):
    sels = cmds.ls(sl=True)
    src = sels[0]
    trg = sels[1]

    shpList = cmds.listRelatives(src, s=True)
    trgCtrlShps = cmds.listRelatives(trg, s=True)
    for i in range(len(shpList)):
        degs = cmds.getAttr('%s.degree' % shpList[i])
        spans = cmds.getAttr('%s.spans' % shpList[i])
        cvs = degs + spans
        for ii in range(cvs):
            cvTr = cmds.xform('%s.cv[%d]' % (shpList[i], ii), q=True, t=True, ws=True)
            cmds.xform('%s.cv[%d]' % (trgCtrlShps[i], ii), t=(cvTr[0] * -1, cvTr[1], cvTr[2]), ws=True)


def mirrorCtrlsUI():
    winName = 'mirCtrlWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)
    cmds.window(winName, title='Mirror Controls', maximizeButton=False, minimizeButton=False)

    cmds.columnLayout('mainColLo', adj=True, p=winName)
    cmds.optionMenu('searchStrOpMenu', label='Search For: ')
    cmds.menuItem(label='L')
    cmds.menuItem(label='R')
    cmds.menuItem(label='_L')
    cmds.menuItem(label='_R')
    cmds.optionMenu('replaceStrOpMenu', label='Replace With: ')
    cmds.menuItem(label='L')
    cmds.menuItem(label='R')
    cmds.menuItem(label='_L')
    cmds.menuItem(label='_R')
    cmds.checkBox('bhvrChkBox', label='Behavior', p='mainColLo')
    cmds.checkBox('inverseScaleChkBox', label='Inversed Scale', p='mainColLo')
    cmds.button(label='Apply', c=mirrorCtrls, p='mainColLo')

    cmds.window(winName, e=True, w=100, h=50)
    cmds.showWindow(winName)


def mirrorCtrls(*args):
    selList = cmds.ls(sl=True)
    srchStr = cmds.optionMenu('searchStrOpMenu', q=True, value=True)
    rplcStr = cmds.optionMenu('replaceStrOpMenu', q=True, value=True)
    bhvrOpt = cmds.checkBox('bhvrChkBox', q=True, v=True)
    inverseOpt = cmds.checkBox('inverseScaleChkBox', q=True, v=True)

    for sel in selList:
        trg = re.sub(srchStr, rplcStr, sel)
        chAttrs = cmds.listAttr(sel, keyable=True)
        for chAttr in chAttrs:
            value = cmds.getAttr('%s.%s' % (sel, chAttr))
            cmds.setAttr('%s.%s' % (trg, chAttr), value)


def mirrorObject(obj, axis='x'):
    xMirrorMatrix = pm.datatypes.Matrix(
        -1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    )
    yMirrorMatrix = pm.datatypes.Matrix(
        1, 0, 0, 0,
        0, -1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    )
    zMirrorMatrix = pm.datatypes.Matrix(
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, -1, 0,
        0, 0, 0, 1
    )

    matrixDict = {
        'x': xMirrorMatrix,
        'y': yMirrorMatrix,
        'z': zMirrorMatrix
    }

    obj = pm.PyNode(obj)
    objWsMtx = obj.worldMatrix.get()
    mirMtx = objWsMtx * matrixDict.get(axis)

    pm.xform(obj, matrix=mirMtx, worldSpace=True)
