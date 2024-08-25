"""
Author: Sang-tak Lee
Website: https://tak.ta-note.com
Updated: 11/21/2020

Usage:
import tak_group
tak_group.UI()
"""

import maya.cmds as cmds
import pymel.core as pm
from functools import partial

from ..common import tak_misc



def UI():
    if cmds.window('grpWin', exists=True): cmds.deleteUI('grpWin')
    cmds.window('grpWin', title='Make Group')

    cmds.columnLayout(rs=5, adj=True)

    cmds.rowLayout(nc=2, rowAttach=[(2, 'top', 0)])
    cmds.textScrollList('mainTrgTexScrLis', allowMultiSelection=True, w=200, sc=partial(sel, 'mainTrgTexScrLis'))
    cmds.columnLayout(rs=5)
    cmds.button('addButton', label='+', w=20, c=loadSel)
    cmds.button('delButton', label='-', w=20, c=delSel)

    cmds.setParent('..')
    cmds.setParent('..')
    cmds.optionMenu('suffixOptMenu', label='Suffix: ', cc=suffixOptChangeCmd)
    cmds.menuItem(label='_zero')
    cmds.menuItem(label='_auto')
    cmds.menuItem(label='_extra')
    cmds.menuItem(label='custom')
    cmds.textFieldGrp('customSuffixTxtFldGrp', label='Custom Suffix: ', columnWidth=[(1, 75), (2, 70)], enable=False)

    cmds.checkBox('locGrpChkBox', label='Locator Groups', cc=lambda val: cmds.checkBox('negateScaleXChkBox', e=True, vis=val))
    cmds.checkBox('ctrlGrpChkBox', label='Control Groups', cc=lambda val: cmds.checkBox('negateScaleXChkBox', e=True, vis=val))
    cmds.checkBox('negateScaleXChkBox', label='Negate ScaleX', vis=False)
    cmds.checkBox('revGrpChkBox', label='Reverse Group')
    cmds.checkBox('spaceGrpChkBox', label='Space Group')
    cmds.checkBox('moduleGrpChkBox', label='Module Groups', cc=lambda val: cmds.columnLayout('moduleDataColLo', e=True, vis=val))

    cmds.columnLayout('moduleDataColLo', adj=True, vis=False)
    cmds.textFieldGrp('moduleNameTxtFldGrp', label="Module Name: ", cw=[(1, 80), (2, 100)])
    cmds.textFieldGrp('parentSpaceTxtFldGrp', label="parent Space: ", cw=[(1, 80), (2, 100)])
    cmds.popupMenu()
    cmds.menuItem(label='Load Sel', c=lambda x: textFldGrpLoadSel('parentSpaceTxtFldGrp'))

    cmds.setParent('..')
    cmds.rowLayout(nc=2, columnWidth2=[110, 110], columnAttach=[(1, 'both', 0), (2, 'both', 0)])
    cmds.button('appButton', label='Apply', c=app)
    cmds.button('closButton', label='Close', c=clos)

    cmds.window('grpWin', edit=True, w=100, h=100)
    cmds.showWindow('grpWin')


def suffixOptChangeCmd(*args):
    suffix = cmds.optionMenu('suffixOptMenu', q=True, v=True)
    if suffix == 'custom':
        cmds.textFieldGrp("customSuffixTxtFldGrp", e=True, enable=True)
    else:
        cmds.textFieldGrp("customSuffixTxtFldGrp", e=True, text="")
        cmds.textFieldGrp("customSuffixTxtFldGrp", e=True, enable=False)


def loadSel(*args):
    selList = cmds.ls(sl=True)
    items = cmds.textScrollList('mainTrgTexScrLis', q=True, allItems=True)
    if items:
        cmds.textScrollList('mainTrgTexScrLis', e=True, removeAll=True)
    cmds.textScrollList('mainTrgTexScrLis', e=True, append=selList)


def textFldGrpLoadSel(widget):
    sels = cmds.ls(sl=True)
    if sels:
        cmds.textFieldGrp(widget, e=True, text=sels[0])


# delButton
def delSel(*args):
    selItem = cmds.textScrollList('mainTrgTexScrLis', q=True, selectItem=True)
    cmds.textScrollList('mainTrgTexScrLis', e=True, removeItem=selItem)


# apply button
def app(*args):
    # get target list
    trgList = cmds.textScrollList('mainTrgTexScrLis', q=True, allItems=True)

    # get suffix
    suffix = cmds.optionMenu('suffixOptMenu', q=True, v=True)
    if suffix == 'custom':
        suffix = cmds.textFieldGrp('customSuffixTxtFldGrp', q=True, text=True)

    locGrpOpt = cmds.checkBox('locGrpChkBox', q=True, value=True)
    ctrlGrpOpt = cmds.checkBox('ctrlGrpChkBox', q=True, value=True)
    negateScaleXOpt = cmds.checkBox('negateScaleXChkBox', q=True, value=True)
    revGrpOpt = cmds.checkBox('revGrpChkBox', q=True, value=True)
    spaceGrpOpt = cmds.checkBox('spaceGrpChkBox', q=True, value=True)
    moduleGrpOpt = cmds.checkBox('moduleGrpChkBox', q=True, value=True)

    if moduleGrpOpt:
        moduleName = cmds.textFieldGrp('moduleNameTxtFldGrp', q=True, text=True)
        parentSpace = cmds.textFieldGrp('parentSpaceTxtFldGrp', q=True, text=True)
        createModuleGroups(moduleName, parentSpace)
    else:
        for trg in trgList:
            if locGrpOpt:
                locGrp(trg, negateScaleXOpt)
            elif ctrlGrpOpt:
                ctrlGrp(trg, negateScaleXOpt)
            elif revGrpOpt:
                revGrp(trg)
            elif spaceGrpOpt:
                spaceGroup(trg)
            else:
                tak_misc.doGroup(trg, suffix)


# close button
def clos(*args):
    cmds.deleteUI('grpWin')


def sel(texScLiName):
    # get selected items in specified textScrollList
    selItems = cmds.textScrollList(texScLiName, q=True, selectItem=True)

    if selItems:
        cmds.select(cl=True)
        for item in selItems:
            cmds.select(item, add=True)


def revGrp(sel):
    """
    Create reverse group that subtract control transform.
    """
    revGrp = cmds.createNode('transform', n='%s_rev' % sel)
    cmds.parent(revGrp, sel)
    for attr in ['X', 'Y', 'Z']:
        cmds.setAttr('%s.translate%s' % (revGrp, attr), 0)
        cmds.setAttr('%s.rotate%s' % (revGrp, attr), 0)
        cmds.setAttr('%s.scale%s' % (revGrp, attr), 1)
    selParent = cmds.listRelatives(sel, p=True)[0]
    cmds.parent(revGrp, selParent)
    cmds.parent(sel, revGrp)

    mulNode = cmds.createNode('multiplyDivide', n=sel + '_rev_mul')
    inputList = ['input2X', 'input2Y', 'input2Z']
    for input in inputList:
        cmds.setAttr('{0}.{1}'.format(mulNode, input), -1)
    cmds.connectAttr('{0}.translate'.format(sel), '{0}.input1'.format(mulNode), f=True)
    cmds.connectAttr('{0}.output'.format(mulNode), '{0}.translate'.format(revGrp), f=True)


def createModuleGroups(moduleName, parentSpace):
    moduleGrp = pm.group(n=moduleName + '_module', empty=True)

    if parentSpace:
        parentSpace = pm.PyNode(parentSpace)
        pm.matchTransform(moduleGrp, parentSpace, pos=True, rot=True)
        pm.parentConstraint(parentSpace, moduleGrp, mo=True)
        parentSpace.scale >> moduleGrp.scale

    geoGrp = pm.group(n=moduleName + '_geo_grp', empty=True)
    outGrp = pm.group(n=moduleName + '_out_grp', empty=True)
    sysGrp = pm.group(n=moduleName + '_sys_grp', empty=True)
    blbxGrp = pm.group(n=moduleName + '_blbx_grp', empty=True)
    noTransGrp = pm.group(n=moduleName + '_noTrans_grp', empty=True)
    ctrlGrp = pm.group(n=moduleName + '_ctrl_grp', empty=True)

    pm.parent(geoGrp, outGrp, sysGrp, moduleGrp)
    pm.parent(blbxGrp, ctrlGrp, sysGrp)
    pm.parent(noTransGrp, blbxGrp)

    for grp in [geoGrp, noTransGrp]:
        grp.inheritsTransform.set(False)
        grp.translate.set([0, 0, 0])
        grp.rotate.set([0, 0, 0])
        grp.scale.set([1, 1, 1])

def locGrp(obj, negateScaleX=False):
    parent = cmds.listRelatives(obj, parent=True)

    loc = cmds.spaceLocator(n=obj + '_loc')[0]
    cmds.matchTransform(loc, obj, pos=True, rot=True, scl=True)

    zeroGrp = cmds.duplicate(loc, po=True, n=loc + "_zero")[0]
    autoGrp = cmds.duplicate(loc, po=True, n=loc + "_auto")[0]

    cmds.parent(autoGrp, zeroGrp)
    cmds.parent(loc, autoGrp)
    if negateScaleX:
        cmds.setAttr('{}.scaleX'.format(zeroGrp), -1)
    cmds.parent(obj, loc)

    if parent:
        cmds.parent(zeroGrp, parent)

    return zeroGrp


def ctrlGrp(obj, negateScaleX=False):
    zeroGrp = cmds.createNode('transform', n='{}_zero'.format(obj))
    autoGrp = cmds.createNode('transform', n='{}_auto'.format(obj))
    extraGrp = cmds.createNode('transform', n='{}_extra'.format(obj))

    for grp in [zeroGrp, autoGrp, extraGrp]:
        cmds.matchTransform(grp, obj)

    chainParent(zeroGrp, autoGrp, extraGrp)

    if negateScaleX:
        cmds.setAttr('{}.scaleX'.format(zeroGrp))

    cmds.parent(obj, extraGrp)


def spaceGroup(obj):
    obj = pm.PyNode(obj)
    group = pm.group(n="%s_space" % obj, empty=True)

    pm.parentConstraint(obj, group)
    obj.scale >> group.scale


def chainParent(*args):
    objects = sum([item if isinstance(item, list) else [item] for item in args], [])
    objects.reverse()
    for i, parentObj in enumerate(objects):
        if i == 0:
            continue
        cmds.parent(objects[i-1], parentObj)
