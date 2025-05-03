'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

usage:
import tak_matchTransform
tak_matchTransform.UI()
'''

import maya.cmds as cmds
import pymel.core as pm
from maya.api import OpenMaya as om


ROTATE_ORDER_INFO = {
    0: 'xyz',
    1: 'yzx',
    2: 'zxy',
    3: 'xzy',
    4: 'yxz',
    5: 'zyx'
}

def UI():
    if cmds.window('mtWin', exists=True): cmds.deleteUI('mtWin')

    cmds.window('mtWin', title='Match Transform', mnb=False, mxb=False)

    cmds.columnLayout(adj=True)
    cmds.checkBoxGrp(
        'optChkGrp',
        numberOfCheckBoxes=4,
        labelArray4=['Translate', 'Rotate', 'Scale', 'Pivot'],
        vertical=True,
        v1=False,
        v2=False,
        v3=False,
        v4=False
    )
    cmds.checkBox('mirrorWorldXChkbox', label='Mirror World X')
    cmds.checkBox('mirrorLocalXChkbox', label='Mirror Local X')
    cmds.button('matchButton', label='Match!', c=match, h=50)

    cmds.window('mtWin', e=True, w=150, h=10)
    cmds.showWindow('mtWin')


def match(*args):
    sels = pm.selected()
    srcTrsfs = sels[0:-1]
    target = sels[-1]

    translateOpt = cmds.checkBoxGrp('optChkGrp', q=True, v1=True)
    rotateOpt = cmds.checkBoxGrp('optChkGrp', q=True, v2=True)
    scaleOpt = cmds.checkBoxGrp('optChkGrp', q=True, v3=True)
    pivotOpt = cmds.checkBoxGrp('optChkGrp', q=True, v4=True)
    mirrorWorldX = cmds.checkBox('mirrorWorldXChkbox', q=True, v=True)
    mirrorLocalX = cmds.checkBox('mirrorLocalXChkbox', q=True, v=True)

    if pm.filterExpand(target, sm=12):  # check if target is a mesh node
        # Match transform to the mesh using uv pin node
        for srcTrsf in srcTrsfs:
            pm.select(target, srcTrsf, r=True)
            cmds.UVPin()

        # Clean up the uv pin node
        for srcTrsf in srcTrsfs:
            uvPinPlug = cmds.listConnections(srcTrsf+'.offsetParentMatrix', plugs=True)[0]
            offsetParentMtx = cmds.getAttr(srcTrsf+'.offsetParentMatrix')
            cmds.xform(srcTrsf.name(), matrix=offsetParentMtx)
            cmds.setAttr(srcTrsf+'.scale', 1, 1, 1)

            cmds.disconnectAttr(uvPinPlug, srcTrsf+'.offsetParentMatrix')
            cmds.setAttr(srcTrsf+'.offsetParentMatrix', [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0], type='matrix')
            cmds.delete(cmds.ls(uvPinPlug, objectsOnly=True))

    else:  # check if target is a transform node
        for srcTrsf in srcTrsfs:
            if mirrorWorldX:
                tempLoc = pm.spaceLocator()
                pm.matchTransform(tempLoc, target)

                tmpTrgLocWsMtx = pm.xform(tempLoc, q=True, matrix=True, ws=True)
                mirrorXMatrix = [
                    -1, 0, 0, 0,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    0, 0, 0, 1
                ]
                tmpSrcWsMtx = pm.datatypes.Matrix(tmpTrgLocWsMtx) * pm.datatypes.Matrix(mirrorXMatrix)
                pm.xform(tempLoc, matrix=tmpSrcWsMtx, ws=True)

                pm.matchTransform(srcTrsf, tempLoc)
                pm.delete(tempLoc)
            elif mirrorLocalX:
                tempLoc = pm.spaceLocator()
                pm.matchTransform(tempLoc, target)

                tmpTrgLocWsMtx = pm.xform(tempLoc, q=True, matrix=True, ws=True)
                mirrorXMatrix = [
                    -1, 0, 0, 0,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    0, 0, 0, 1
                ]
                tmpSrcWsMtx = pm.datatypes.Matrix(tmpTrgLocWsMtx) * pm.datatypes.Matrix(mirrorXMatrix)
                pm.xform(tempLoc, matrix=tmpSrcWsMtx, ws=True)

                pm.matchTransform(srcTrsf, tempLoc)
                pm.delete(tempLoc)

                pm.setAttr('{}.scale'.format(srcTrsf), 1, 1, 1)
                pm.setAttr('{}.rotate'.format(srcTrsf), target.rotateX.get(), -target.rotateY.get(), -target.rotateZ.get())
            else:
                pm.matchTransform(srcTrsf, target, pos=translateOpt, rot=rotateOpt, scl=scaleOpt, piv=pivotOpt)
