"""
Author: LEE SANGTAK
Contact: chst27@gmail.com

Description:
This script creates left/right target shape from source shape.
It works on mesh group too, when hierarchy is same between base and source.

Usage:
1. Copy this script and paste in your scripts folder.

2. In maya python tab, run following code.
import tak_LRTarget
reload(tak_LRTarget)
tak_LRTarget.UI()

Requirements:
rampBlendShape.py
AErampBlendShapeTemplate.mel
tak_misc.py
"""

import maya.cmds as cmds
import pymel.core as pm

from ..common import tak_misc

if not cmds.pluginInfo('rampBlendShape', q=True, loaded=True): cmds.loadPlugin('rampBlendShape')


def UI():
    winName = 'LRTargetWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)
    cmds.window(winName, title='L/R Blend Shape Target')

    cmds.formLayout('mainForm', nd=100)

    cmds.tabLayout('mainTab', tv=False)
    cmds.tabLayout('subTab', tv=False, scrollable=True)

    cmds.columnLayout('mainColLay', adj=True)
    cmds.textFieldButtonGrp('baseTexField', label='Base: ', bl='Load Sel', columnWidth=[(1, 50), (2, 150)],
                            bc=lambda: loadSel('baseTexField'))

    cmds.rowColumnLayout('nonSymRowColLay', numberOfColumns=3, columnWidth=[(1, 52), (2, 150), (3, 52)])
    cmds.text(label='No Sym:', ann='No symmetry meshes in base')
    cmds.textScrollList('noSymTexScrList', h=50)
    cmds.button(label='Load Sel', h=5, c=lambda args: loadSel('noSymTexScrList'))

    cmds.setParent('mainColLay')
    cmds.rowColumnLayout('trgRowColLay', numberOfColumns=3, columnWidth=[(1, 52), (2, 150), (3, 52)])
    cmds.text(label='Targets:')
    cmds.textScrollList('trgTexScrList', h=100)
    cmds.button(label='Load Sel', h=5, c=lambda args: loadSel('trgTexScrList'))

    cmds.setParent('mainColLay')
    cmds.separator(h=10, style='in')
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 90), (2, 40)], columnAttach=[(1, 'right', 1)])
    cmds.text(label='Center Falloff: ')
    cmds.floatField('falloffField', minValue=0, maxValue=100, precision=1, value=5.0)
    cmds.text(label='%')

    cmds.setParent('mainColLay')
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 70), (2, 50), (3, 50)], columnAttach=[(1, 'right', 1)])
    cmds.text(label='L/R Prefix: ')
    cmds.textField('lPreTexField', text='')
    cmds.textField('rPreTexField', text='')

    cmds.setParent('mainColLay')
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 70), (2, 50), (3, 50)], columnAttach=[(1, 'right', 1)])
    cmds.text(label='L/R Suffix: ')
    cmds.textField('lSufTexField', text='_L')
    cmds.textField('rSufTexField', text='_R')

    cmds.setParent('mainForm')
    cmds.button('appButton', label='Create L/R', w=90, c=main)
    cmds.button('flipBtn', label='Create Flip', c=flip)
    cmds.button('recoverButton', label='Recover Freezed', w=90, c=recoverFrzedTrg)
    cmds.formLayout('mainForm', e=True,
                    attachForm=[('mainTab', 'top', 5), ('mainTab', 'left', 5), ('mainTab', 'right', 5),
                                ('appButton', 'bottom', 5), ('appButton', 'left', 5), ('flipBtn', 'bottom', 5),
                                ('recoverButton', 'bottom', 5), ('recoverButton', 'right', 5)],
                    attachPosition=[],
                    attachControl=[('mainTab', 'bottom', 5, 'appButton'), ('flipBtn', 'left', 5, 'appButton'),
                                   ('flipBtn', 'right', 5, 'recoverButton')])

    cmds.setParent('mainColLay')
    cmds.checkBox('delHistoryChkbox', label='Delete History', value=True)

    cmds.window(winName, edit=True, w=300, h=325)
    cmds.showWindow(winName)


def loadSel(widgetName):
    sel = cmds.ls(sl=True)
    try:
        cmds.textFieldButtonGrp(widgetName, e=True, text=sel[0])
    except:
        if cmds.textScrollList(widgetName, q=True, allItems=True):
            cmds.textScrollList(widgetName, e=True, removeAll=True)
        cmds.textScrollList(widgetName, e=True, append=sel)


def main(*args):
    baseName = cmds.textFieldButtonGrp('baseTexField', q=True, text=True)
    noSymMeshes = cmds.textScrollList('noSymTexScrList', q=True, allItems=True)
    targetList = cmds.textScrollList('trgTexScrList', q=True, allItems=True)
    centerFalloff = cmds.floatField('falloffField', q=True, v=True)

    for targetName in targetList:
        # Create left/right target by duplicating base
        leftBlendTarget = createLfRtTarget(baseName, targetName, side='left')
        rightBlendTarget = createLfRtTarget(baseName, targetName, side='right')

        baseMeshes = removeNoMesh(cmds.listRelatives(baseName, allDescendents=True, fullPath=True, type='transform'))
        if not baseMeshes:
            baseMeshes = [baseName]
        targetMeshes = removeNoMesh(cmds.listRelatives(targetName, allDescendents=True, fullPath=True, type='transform'))
        if not targetMeshes:
            targetMeshes = [targetName]
        leftTargetMeshes = removeNoMesh(cmds.listRelatives(leftBlendTarget, allDescendents=True, fullPath=True, type='transform'))
        if not leftTargetMeshes:
            leftTargetMeshes = [leftBlendTarget]
        rightTargetMeshes = removeNoMesh(cmds.listRelatives(rightBlendTarget, allDescendents=True, fullPath=True, type='transform'))
        if not rightTargetMeshes:
            rightTargetMeshes = [rightBlendTarget]

        # Calculate and assign vector
        vectorReproduce(baseMeshes, noSymMeshes, targetMeshes, leftTargetMeshes, centerFalloff, side='left')
        vectorReproduce(baseMeshes, noSymMeshes, targetMeshes, rightTargetMeshes, centerFalloff, side='right')

        if cmds.checkBox('delHistoryChkbox', q=True, v=True):
            cmds.delete(leftTargetMeshes, rightTargetMeshes, ch=True)

    cmds.select(cl=True)


def createLfRtTarget(baseName, targetName, side):
    # Get data
    lPrefix = cmds.textField('lPreTexField', q=True, text=True)
    lSuffix = cmds.textField('lSufTexField', q=True, text=True)
    rPrefix = cmds.textField('rPreTexField', q=True, text=True)
    rSuffix = cmds.textField('rSufTexField', q=True, text=True)

    targetPos = cmds.xform(targetName, q=True, ws=True, t=True)
    boundingBox = cmds.exactWorldBoundingBox(targetName)
    posOffset = boundingBox[3] - boundingBox[0]

    # Data table
    lfRtTable = {'left': {'prefix': lPrefix, 'suffix': lSuffix, 'position': (targetPos[0]+posOffset, targetPos[1], targetPos[2])},
                 'right': {'prefix': rPrefix, 'suffix': rSuffix, 'position': (targetPos[0]-posOffset, targetPos[1], targetPos[2])}
                }

    blendTarget = pm.duplicate(baseName, renameChildren=True)[0]
    pm.parent(blendTarget, world=True)
    blendTarget.rename(lfRtTable[side]['prefix'] + targetName + lfRtTable[side]['suffix'])
    blendTarget.setTranslation(lfRtTable[side]['position'], space='world')

    return str(blendTarget)


def removeNoMesh(transformList):
    meshes = []
    if transformList:
        meshes = [item for item in transformList if cmds.listRelatives(item, s=True)]
    return meshes


def vectorReproduce(baseMeshes, noSymMeshes, targetMeshes, outMeshes, centerFalloff, side):
    offset = centerFalloff * 0.01
    noSymOffset = 1000

    for i in range(len(baseMeshes)):
        baseMesh = pm.PyNode(baseMeshes[i])
        targetMesh = pm.PyNode(targetMeshes[i])
        outMesh = pm.PyNode(outMeshes[i])

        rampBS = pm.createNode('rampBlendShape')

        targetMesh.visibility.set(True) # Can't get boundingbox when mesh visibility set to false
        targetGeoBoundingBox = targetMesh.getBoundingBox(space='world')
        rampBS.range.set(targetGeoBoundingBox.width())

        if noSymMeshes:
            isNoSymMesh = baseMesh in noSymMeshes
        else:
            isNoSymMesh = False

        if side == 'left':
            rampBS.weightCurveRamp[0].weightCurveRamp_Position.set(0.5-offset)
            rampBS.weightCurveRamp[1].weightCurveRamp_Position.set(0.5+offset)
            rampBS.weightCurveRamp[2].weightCurveRamp_FloatValue.set(1.0)
            if isNoSymMesh:
                if not isLeftSide(baseMesh):
                    rampBS.envelope.set(0)
                else:
                    rampBS.attr('center').set(-noSymOffset)
                    rampBS.range.set(rampBS.range.get()+(2*noSymOffset))
        elif side == 'right':
            rampBS.weightCurveRamp[0].weightCurveRamp_Position.set(0.5+offset)
            rampBS.weightCurveRamp[1].weightCurveRamp_Position.set(0.5-offset)
            rampBS.weightCurveRamp[2].weightCurveRamp_FloatValue.set(0.0)
            if isNoSymMesh:
                if isLeftSide(baseMesh):
                    rampBS.envelope.set(0)
                else:
                    rampBS.attr('center').set(noSymOffset)
                    rampBS.range.set(rampBS.range.get()+(2*noSymOffset))

        baseMesh.getShape(ni=True).worldMesh >> rampBS.baseGeo
        targetMesh.getShape(ni=True).worldMesh >> rampBS.targetGeo
        rampBS.outGeo >> outMesh.inMesh

        pm.select(targetMesh, outMesh, r=True)
        tak_misc.copyMat()


def isLeftSide(mesh):
    return mesh.getBoundingBox(space='world').center().x > 0.0


def flip(*args):
    pass


def recoverFrzedTrg(*args):
    origFacialGrp = cmds.textFieldButtonGrp('baseTexField', q=True, text=True)
    targetList = cmds.textScrollList('trgTexScrList', q=True, allItems=True)

    for frzedFacialGrp in targetList:
        # Cleanup frzedFacialGrp
        cmds.delete(frzedFacialGrp, ch=True)
        cmds.makeIdentity(frzedFacialGrp, apply=True)
        allChlds = cmds.listRelatives(frzedFacialGrp, ad=True, type='transform')
        for chld in allChlds:
            if 'Base' in chld:
                cmds.delete(chld)

        # Match original facial group to freezed facial group
        origFacialDupGrp = cmds.duplicate(origFacialGrp, rc=True, rr=True)
        cmds.delete(cmds.parentConstraint(frzedFacialGrp, origFacialDupGrp, mo=False))

        origFacialDupMeshes = cmds.listRelatives(origFacialDupGrp, ad=True, type='mesh')
        frzedFacialGrpMeshes = cmds.listRelatives(frzedFacialGrp, ad=True, type='mesh')

        for i in range(len(origFacialDupMeshes)):
            numOfVtx = cmds.polyEvaluate(origFacialDupMeshes[i], vertex=True)
            for vtxId in range(numOfVtx):
                frzedFacialMeshVtxWsPos = cmds.pointPosition(frzedFacialGrpMeshes[i] + '.vtx[' + str(vtxId) + ']',
                                                             world=True)
                cmds.xform(origFacialDupMeshes[i] + '.vtx[' + str(vtxId) + ']', t=frzedFacialMeshVtxWsPos, ws=True)

        cmds.delete(frzedFacialGrp)
        cmds.rename(origFacialDupGrp, frzedFacialGrp)
