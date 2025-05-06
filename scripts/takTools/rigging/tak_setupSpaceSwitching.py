'''
Author: Tak
Website: https://ta-note.com
Updated: 12/18/2020
'''


from maya import cmds
from functools import partial

from ..common import tak_mayaUiUtils


def ui():
    winName = 'setSpcSwc'

    if cmds.window(winName, exists = True):
        cmds.deleteUI(winName)

    cmds.window(winName, title = 'Set Up space Switching', mnb = False, mxb = False)

    cmds.columnLayout(adj = True, rs = 3)

    cmds.rowColumnLayout(numberOfColumns = 2, columnOffset = [2, 'left', 5])
    cmds.frameLayout(label = 'Objects', w = 150)
    cmds.textScrollList('objTxtScrLs', sc = partial(tak_mayaUiUtils.txtScrLsSC, 'objTxtScrLs'), allowMultiSelection = True)
    cmds.popupMenu()
    cmds.menuItem(label = 'Load Sels', c = partial(tak_mayaUiUtils.populateTxtScrList,'textScrollList', 'objTxtScrLs'))

    cmds.setParent('..') # Move to parent layout that is rowColumnLayout.
    cmds.frameLayout(label = 'Target spaces', w = 150)
    cmds.textScrollList('trgSpcTxtScrLs', sc = partial(tak_mayaUiUtils.txtScrLsSC, 'trgSpcTxtScrLs'), allowMultiSelection = True)
    cmds.popupMenu()
    cmds.menuItem(label = 'Load Sels', c = partial(tak_mayaUiUtils.populateTxtScrList,'textScrollList', 'trgSpcTxtScrLs'))

    cmds.setParent('..') # Move to parent layout that is rowColumnLayout.
    cmds.setParent('..') # Move to parent layout that is columnLayout.
    cmds.checkBoxGrp('cnstChkBoxGrp', label = 'Constraint: ', numberOfCheckBoxes = 3, v1 = True, labelArray3 = ['Parent', 'Point', 'Orient'], columnAlign = [1, 'left'], columnWidth = [(1, 70), (2, 80), (3, 80), (4, 80)], on1 = prntCnstChkBoxOn, on2 = posOriCnstChkBoxOn, on3 = posOriCnstChkBoxOn)

    cmds.checkBox('setupScriptNodeChkBox', label = 'Setup Script Node', value = False)

    cmds.button(label = 'Apply', c = main, h = 30)

    cmds.window(winName, e = True, w = 300, h = 100)
    cmds.showWindow(winName)


def main(*args):
    trgSpcs = cmds.textScrollList('trgSpcTxtScrLs', q = True, allItems = True)
    objs = cmds.textScrollList('objTxtScrLs', q = True, allItems = True)
    prntCnstOpt = cmds.checkBoxGrp('cnstChkBoxGrp', q = True, v1 = True)
    pntCnstOpt = cmds.checkBoxGrp('cnstChkBoxGrp', q = True, v2 = True)
    oriCnstOpt = cmds.checkBoxGrp('cnstChkBoxGrp', q = True, v3 = True)
    setupScriptNodeOpt = cmds.checkBox('setupScriptNodeChkBox', q = True, v = True)

    spcLocGrp = 'space_loc_grp'
    if not cmds.objExists(spcLocGrp):
        spcLocGrp = cmds.createNode('transform', n = spcLocGrp)
        cmds.setAttr('%s.visibility' %spcLocGrp, False)

    for obj in objs:
        spcLocs = []
        for trgSpc in trgSpcs:
            spcLoc = '%s_%s_space_loc' %(obj, trgSpc)
            if cmds.objExists(spcLoc):
                spcLocs.append(spcLoc) # When locator is already exists, just append to the locator list.
                pass
            else:
                # Create locators on object position.
                cmds.spaceLocator(n = spcLoc)[0]
                # cmds.delete(cmds.parentConstraint(obj, spcLoc, mo = False)) # Match locator to object's transform.
                cmds.matchTransform(spcLoc, obj)
                spcLocs.append(spcLoc)

            spcLocZero = cmds.createNode('transform', n='{spcLoc}_zero'.format(spcLoc=spcLoc))
            cmds.matchTransform(spcLocZero, spcLoc)
            cmds.parent(spcLoc, spcLocZero)
            cmds.parent(spcLocZero, spcLocGrp)

            # Constraint locator with target space.
            if prntCnstOpt:
                cmds.parentConstraint(trgSpc, spcLocZero, mo = True)
            if pntCnstOpt:
                cmds.pointConstraint(trgSpc, spcLocZero, mo = True)
            if oriCnstOpt:
                cmds.orientConstraint(trgSpc, spcLocZero, mo = True)


        # Create spaces group that driven by locators.
        spcsGrp = obj + '_space'
        if not cmds.objExists(spcsGrp):
            objPrnt = cmds.listRelatives(obj, p = True)
            spcsGrp = cmds.createNode('transform', n = obj + '_space')
            cmds.delete(cmds.parentConstraint(obj, spcsGrp, mo = False)) # Match spcsGrp's transform to the object.
            cmds.parent(obj, spcsGrp)
            if objPrnt:
                cmds.parent(spcsGrp, objPrnt[0])

        # Constraint spaces group with locators.
        prntCnst = None
        pntCnst = None
        oriCnst = None
        if prntCnstOpt:
            prntCnst = cmds.parentConstraint(spcLocs, spcsGrp, mo = False)[0]
        if pntCnstOpt:
            pntCnst = cmds.pointConstraint(spcLocs, spcsGrp, mo = False)[0]
        if oriCnstOpt:
            oriCnst = cmds.orientConstraint(spcLocs, spcsGrp, mo = False)[0]

        ### Add attributes ###
        # Add divider.
        if not cmds.objExists(obj + '.spaceSwitch'):
            cmds.addAttr(obj, ln = 'spaceSwitch', at = 'enum', en = '---------------:')
            cmds.setAttr('%s.%s' %(obj, 'spaceSwitch'), channelBox = True)

        # Add space switching atributes.
        cnsts = cmds.listRelatives(spcsGrp, type = 'constraint')
        spaces = ':'.join(trgSpcs) + ':'

        for cnst in cnsts:
            cnstType = cmds.nodeType(cnst)
            if cnstType == 'parentConstraint' and prntCnstOpt:
                cmds.addAttr(obj, ln = "parentspace", nn = "Parent space", at = "enum", en = spaces, keyable = True)
            if cnstType == 'pointConstraint' and pntCnstOpt:
                cmds.addAttr(obj, ln = "positionspace", nn = "Position Space", at = "enum", en = spaces, keyable = True)
            if cnstType == 'orientConstraint' and oriCnstOpt:
                cmds.addAttr(obj, ln = "orientspace", nn = "Orient space", at = "enum", en = spaces, keyable = True)

    if setupScriptNodeOpt:
        setupScriptNode(
            objs,
            trgSpcs,
            cnsts,
            spcsGrp,
            spcLocs,
            prntCnst,
            prntCnstOpt,
            pntCnst,
            pntCnstOpt,
            oriCnst,
            oriCnstOpt
        )
    else:
        # Set up set driven key for constraint.
        for obj in objs:
            spcLocs = []
            for trgSpc in trgSpcs:
                spcLoc = '%s_%s_space_loc' %(obj, trgSpc)
                if cmds.objExists(spcLoc):
                    spcLocs.append(spcLoc)

            spcsGrp = obj + '_space'
            cnsts = cmds.listRelatives(spcsGrp, type = 'constraint')
            for cnst in cnsts:
                if cnstType == 'parentConstraint' and prntCnstOpt:
                    spaceAttr = '%s.%s' % (obj, 'parentspace')
                elif cnstType == 'pointConstraint' and pntCnstOpt:
                    spaceAttr = '%s.%s' % (obj, 'positionspace')
                elif cnstType == 'orientConstraint' and oriCnstOpt:
                    spaceAttr = '%s.%s' % (obj, 'orientspace')
                else:
                    continue

                # Set driven key for constraint weights.
                for i in range(len(trgSpcs)):
                    for j, spcLoc in enumerate(spcLocs):
                        value = i == j
                        cmds.setDrivenKeyframe('%s.%sW%i' % (cnst, spcLoc, j), v=value, cd = spaceAttr, dv = i)

def setupScriptNode(objs, trgSpcs, cnsts, spcsGrp, spcLocs, prntCnst, prntCnstOpt, pntCnst, pntCnstOpt, oriCnst, oriCnstOpt):
    for obj in objs:
        # Add spaces to the object and connect to constraint weights.
        for trgSpc in trgSpcs:
            defaultVal = 0
            if trgSpcs.index(trgSpc) == 0: # Set first target value to 1.
                defaultVal = 1
            if prntCnstOpt:
                cmds.addAttr(obj, ln = trgSpc + '_parentspace', at = 'short', keyable = False, min = 0, max = 1, dv = defaultVal)
                cmds.setAttr(obj+'.%s' % trgSpc + '_parentspace', e=True, channelBox=True)
                prntCnstWeights = cmds.parentConstraint(prntCnst, q = True, weightAliasList = True)
                for prntCnstW in prntCnstWeights:
                    if trgSpc in prntCnstW:
                        cmds.connectAttr(obj + '.' + trgSpc + '_parentspace', prntCnst + '.' + prntCnstW, f = True)
                        break
            if pntCnstOpt:
                cmds.addAttr(obj, ln = trgSpc + '_positionspace', at = 'short', keyable = False, min = 0, max = 1, dv = defaultVal)
                cmds.setAttr(obj+'.%s' % trgSpc + '_positionspace', e=True, channelBox=True)
                pntCnstWeights = cmds.pointConstraint(pntCnst, q = True, weightAliasList = True)
                for pntCnstW in pntCnstWeights:
                    if trgSpc in pntCnstW:
                        cmds.connectAttr(obj + '.' + trgSpc + '_positionspace', pntCnst + '.' + pntCnstW, f = True)
                        break
            if oriCnstOpt:
                cmds.addAttr(obj, ln = trgSpc + '_orientspace', at = 'short', keyable = False, min = 0, max = 1, dv = defaultVal)
                cmds.setAttr(obj+'.%s' % trgSpc + '_orientspace', e=True, channelBox=True)
                oriCnstWeights = cmds.orientConstraint(oriCnst, q = True, weightAliasList = True)
                for oriCnstW in oriCnstWeights:
                    if trgSpc in oriCnstW:
                        cmds.connectAttr(obj + '.' + trgSpc + '_orientspace', oriCnst + '.' + oriCnstW, f = True)
                        break

        # Add constraint offset attributes and connect.
        for cnst in cnsts:
            cnstType = cmds.nodeType(cnst)
            if cnstType == 'parentConstraint' and prntCnstOpt:
                for attrName in ['offsetTranslate', 'offsetRotate']:
                    addVectorAttr(obj, name=attrName, type='double', keyable=False)
                    for i in range(len(trgSpcs)):
                        if 'Translate' in attrName:
                            cmds.connectAttr('%s.%s' % (obj, attrName), '%s.target[%d].targetOffsetTranslate' % (cnst, i))
                        if 'Rotate' in attrName:
                            cmds.connectAttr('%s.%s' % (obj, attrName), '%s.target[%d].targetOffsetRotate' % (cnst, i))
            if cnstType == 'pointConstraint' and pntCnstOpt:
                addVectorAttr(obj, name='offsetTranslate', type='double', keyable=False)
                cmds.connectAttr('%s.%s' % (obj, 'offsetTranslate'), '%s.offset' % cnst)
            if cnstType == 'orientConstraint' and oriCnstOpt:
                addVectorAttr(obj, name='offsetRotate', type='double', keyable=False)
                cmds.connectAttr('%s.%s' % (obj, 'offsetRotate'), '%s.offset' % cnst)

        # Create driver and driven objects message attributes and connect
        cmds.addAttr(obj, ln='spacesGrp', at='message')
        cmds.connectAttr('%s.message' % spcsGrp, '%s.spacesGrp' % obj)
        for spcLoc in spcLocs:
            cmds.addAttr(obj, ln=spcLoc, at='message')
            cmds.connectAttr('%s.message' % spcLoc, '%s.%s' % (obj, spcLoc))

        # Connect space switching objects to spaceSwitchAttrObjs's message attribute.
        # This set up is for namespace handling when referenced to a scene.
        spcSwchAttrObjsNode = 'spaceSwitchAttrObjsInfo'
        if not cmds.objExists(spcSwchAttrObjsNode):
            cmds.createNode('transform', n = spcSwchAttrObjsNode)
        if not cmds.objExists(spcSwchAttrObjsNode + '.' + obj):
            cmds.addAttr(spcSwchAttrObjsNode, at = 'message', ln = obj)
            cmds.connectAttr(obj + '.message', spcSwchAttrObjsNode + '.' + obj)

    # Create script node
    scriptNodeName = 'spaceSwitchMatchTrsfExpr'

    if cmds.objExists(scriptNodeName):
        cmds.scriptNode(scriptNodeName, executeBefore = True)
    else:
        exprStr = '''import maya.cmds as cmds
import pymel.core as pm

def spaceSwitchMatchTrsf():
    sels = cmds.ls( sl = True )
    for sel in sels:
        spacesGrp = pm.listConnections('%s.spacesGrp' % sel)[0]
        spacesGrpPreMat = spacesGrp.worldMatrix.get()

        # Get selected attribute.
        rawSelAttr = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
        selAttrName = cmds.attributeQuery(rawSelAttr, longName = True, node = sel)  # selAttrName is parentspace or positionspace or orientspace
        selAttrFullName = '%s.%s' % (sel, selAttrName)

        # Get slected space name.
        selspace = cmds.getAttr(selAttrFullName, asString = True)

        # space weight attribute name depend on selected attribute.
        selspaceWeightAttr = '%s.%s_%s' % (sel, selspace, selAttrName)

        # Set weight and set key
        udAttrs = ['%s.%s' % (sel, udAttr) for udAttr in cmds.listAttr(sel, ud = True)]
        for udAttr in udAttrs:
            if selAttrFullName == udAttr:
                continue

            if selAttrName in udAttr and selspaceWeightAttr == udAttr:
                cmds.setAttr(selspaceWeightAttr, 1)
            elif selAttrName in udAttr and selspaceWeightAttr != udAttr:
                cmds.setAttr(udAttr, 0)

            if selAttrName in udAttr:
                cmds.setKeyframe(udAttr)
                cmds.keyTangent(udAttr, itt='stepnext', ott='step')

        # Calulate offset to driver locator
        driverLoc = None
        for udAttr in cmds.listAttr(sel, ud=True):
            if selspace+'_space_loc' in udAttr:
                driverLoc = pm.listConnections('%s.%s' % (sel, udAttr))[0]
                break
        offsetMat = spacesGrpPreMat * driverLoc.worldMatrix.get().inverse()
        # if spacesGrp.getParent():
        #     offsetMat = offsetMat * spacesGrp.getParent().worldMatrix.get().inverse()
        offsetTranslate = offsetMat.translate
        offsetRotate = pm.util.degrees(offsetMat.rotate.asEulerRotation())

        # Set offset and set key
        for udAttr in udAttrs:
            if 'offsetTranslate' in udAttr:
                try:
                    cmds.setAttr(udAttr, offsetTranslate.x, offsetTranslate.y, offsetTranslate.z)
                    cmds.setKeyframe(udAttr)
                except:
                    pass
                cmds.keyTangent(udAttr, itt='stepnext', ott='step')
            elif 'offsetRotate' in udAttr:
                try:
                    cmds.setAttr(udAttr, offsetRotate.x, offsetRotate.y, offsetRotate.z)
                    cmds.setKeyframe(udAttr)
                except:
                    pass
                cmds.keyTangent(udAttr, itt='stepnext', ott='step')


# Attach script job to the objects containing space switch attribute.
spaceSwitchAttrObjInfos = cmds.ls('*spaceSwitchAttrObjsInfo', r = True)

for spaceSwitchAttrObjInfo in spaceSwitchAttrObjInfos:
    spaceSwitchAttrObjs = cmds.listAttr(spaceSwitchAttrObjInfo, ud = True)
    for spaceSwitchAttrObj in spaceSwitchAttrObjs:
        spaceSwitchAttrObj = cmds.listConnections(spaceSwitchAttrObjInfo + '.' + spaceSwitchAttrObj, s = True, d = False)[0]
        udAttrs = cmds.listAttr(spaceSwitchAttrObj, ud = True)
        for udAttr in udAttrs:
            if udAttr == 'parentspace' or udAttr == 'positionspace' or udAttr == 'orientspace':
                cmds.scriptJob(kws = True, ac = [spaceSwitchAttrObj + '.' + udAttr, spaceSwitchMatchTrsf])
'''

        cmds.scriptNode(beforeScript = exprStr, scriptType = 1, sourceType = 'python', n = scriptNodeName)
        cmds.scriptNode(scriptNodeName, executeBefore = True)

    spaceEnumAttrs = ['parentspace', 'positionspace', 'orientspace']
    for obj in objs:
        for attr in spaceEnumAttrs:
            try:
                cmds.setAttr('{0}.{1}'.format(obj, attr), channelBox=True)
            except:
                pass


def prntCnstChkBoxOn(*args):
    cmds.checkBoxGrp('cnstChkBoxGrp', e = True, v2 = False)
    cmds.checkBoxGrp('cnstChkBoxGrp', e = True, v3 = False)


def posOriCnstChkBoxOn(*args):
    cmds.checkBoxGrp('cnstChkBoxGrp', e = True, v1 = False)


def addVectorAttr(obj, name, type, keyable):
    cmds.addAttr(obj, ln=name, at=type+'3', keyable=keyable)
    cmds.addAttr(obj, ln=name+'X', at=type, keyable=keyable, p=name)
    cmds.addAttr(obj, ln=name+'Y', at=type, keyable=keyable, p=name)
    cmds.addAttr(obj, ln=name+'Z', at=type, keyable=keyable, p=name)

    cmds.setAttr('%s.%s' %(obj, name), e=True, channelBox=True)
    cmds.setAttr('%s.%s' %(obj, name+'X'), e=True, channelBox=True)
    cmds.setAttr('%s.%s' %(obj, name+'Y'), e=True, channelBox=True)
    cmds.setAttr('%s.%s' %(obj, name+'Z'), e=True, channelBox=True)
