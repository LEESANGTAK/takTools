'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

usage:
import tak_matchTransform
tak_matchTransform.UI()
'''

import maya.cmds as cmds
import pymel.core as pm


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
    cmds.checkBox('mirrorXChkbox', label='mirrorX')
    cmds.button('matchButton', label='Match!', c=match, h=50)

    cmds.window('mtWin', e=True, w=150, h=10)
    cmds.showWindow('mtWin')


def match(*args):
    sels = pm.selected()
    srcTrsfs = sels[0:-1]
    trgTrsf = sels[-1]

    translateOpt = cmds.checkBoxGrp('optChkGrp', q=True, v1=True)
    rotateOpt = cmds.checkBoxGrp('optChkGrp', q=True, v2=True)
    scaleOpt = cmds.checkBoxGrp('optChkGrp', q=True, v3=True)
    pivotOpt = cmds.checkBoxGrp('optChkGrp', q=True, v4=True)
    mirror = cmds.checkBox('mirrorXChkbox', q=True, v=True)

    for srcTrsf in srcTrsfs:
        if mirror:
            trgWsMatrix = trgTrsf.worldMatrix.get()
            mirrorXMatrix = [
                -1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1
            ]
            trgWsMatrix *= pm.datatypes.Matrix(mirrorXMatrix)
            pm.xform(srcTrsf, matrix=trgWsMatrix, ws=True)
        else:
            pm.matchTransform(srcTrsf, trgTrsf, pos=translateOpt, rot=rotateOpt, scl=scaleOpt, piv=pivotOpt)
