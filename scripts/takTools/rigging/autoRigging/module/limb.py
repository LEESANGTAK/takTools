import os

import pymel.core as pm
import maya.api.OpenMaya as om

from ..base import general
from ..base import module
from ..base import controller

from ..utils import globalUtil


def build(
        name,
        limbJoints,
        upTwistJoints,
        lowTwistJoints,
        aimAxisSign,
        parentSapce=None,
    ):

    moduleObj = module.Module(name)

    limbJoints = [pm.PyNode(jnt) for jnt in limbJoints]
    upTwistJoints = [pm.PyNode(jnt) for jnt in upTwistJoints]
    lowTwistJoints = [pm.PyNode(jnt) for jnt in lowTwistJoints]

    # Create out joints
    outJoints = createDrivingJoints(limbJoints, suffix='_outJnt')

    # Build
    fkJoints, fkCtrls, fkRigGrp = buildFK(name, outJoints)
    ikJoints, ikCtrls, ikRigGrp = buildIK(name, outJoints)
    twistRigGrp, clstCtrlGrp = setupTwist(name, outJoints, upTwistJoints, lowTwistJoints, aimAxisSign)
    switchCtrl, choiceNodes = setupSwitch(name, fkJoints, ikJoints, outJoints)
    setupFkIkSwitchCallback(switchCtrl, choiceNodes, outJoints, fkCtrls, ikCtrls)

    pm.group(fkRigGrp, ikRigGrp, moduleObj.outGrp, twistRigGrp, general.getSpaceGrp(switchCtrl), n=name + '_rig_grp')

    # Fk/Ik visibility
    fkIkVisReverseNode = pm.createNode('reverse', n=name + '_fkIkRigVis_reverse')
    switchCtrl.fkIk >> fkIkVisReverseNode.inputX
    fkIkVisReverseNode.outputX >> fkRigGrp.visibility
    switchCtrl.fkIk >> ikRigGrp.visibility

    # Bend controller visibility
    pm.addAttr(switchCtrl, at='bool', ln='bendCtrlVis', keyable=True)
    switchCtrl.bendCtrlVis >> clstCtrlGrp.visibility

    # Cleanup outliner
    pm.parent(outJoints[0], moduleObj.outGrp)
    pm.parent(switchCtrl.spaceGrp, moduleObj.ctrlGrp)

    moduleObj.outGrp.hide()
    moduleObj.systemGrp.hide()

def buildFK(name, outJoints):
    fkJoints = []
    fkCtrls = []

    # create joint chain
    newJoints = createDrivingJoints(outJoints, '_fk')
    pm.parent(newJoints[0], world=True)
    fkJoints.extend(newJoints)
    pm.makeIdentity(fkJoints[0], apply=True)

    # create controller
    for fkJnt in fkJoints:
        jntRotateOrder = fkJnt.rotateOrder.get()
        ctrl = controller.Controller(fkJnt.replace('_outJnt_fk', '_fk_ctrl'), shape='cube', scale=1)
        ctrl.createGroups(space=True, extra=True)
        ctrl.transform.rotateOrder.set(jntRotateOrder)

        pm.matchTransform(ctrl.spaceGrp, fkJnt, pos=True, rot=True)
        ctrl.connectTo(fkJnt, parent=True)
        fkCtrls.append(ctrl)

    # setup fk hierarchy
    for i in xrange(len(fkCtrls)):
        if i == 0:
            continue
        preCtrl = fkCtrls[i-1]
        curCtrl = fkCtrls[i]
        preCtrl.transform | curCtrl.spaceGrp

    # cleanup outliner
    fkSystemGrp = pm.group(fkJoints[0], n=name + '_fkSystem_grp')
    fkSystemGrp.visibility.set(False)
    fkCtrlGrp = pm.group(fkCtrls[0].spaceGrp, n=name + '_fkCtrl_grp')
    fkGrp = pm.group(fkSystemGrp, fkCtrlGrp, n=name + '_fk_grp')

    return fkJoints, fkCtrlGrp, fkGrp

def buildIK(name, outJoints):
    ikJoints = []
    ikCtrls = []

    # create jonit chain
    newJoints = createDrivingJoints(outJoints, '_ik')
    pm.parent(newJoints[0], world=True)
    ikJoints.extend(newJoints)
    pm.makeIdentity(ikJoints[0], apply=True)

    # setup joint driving system
    ikStartJoint = ikJoints[0]
    ikEndJoint = ikJoints[-1]
    ikHandle = pm.ikHandle(startJoint=ikStartJoint, endEffector=ikEndJoint, n=name + '_ik')[0]

    # create controller
    ikCtrl = controller.Controller('{0}_ctrl'.format(ikHandle), shape='cube', scale=1)
    ikCtrl.createGroups(space=True, extra=True)
    ikCtrls.append(ikCtrl)

    pm.matchTransform(ikCtrl.spaceGrp, ikEndJoint, pos=True, rot=True)
    pm.pointConstraint(ikCtrl.transform, ikHandle)
    pm.orientConstraint(ikCtrl.transform, ikJoints[2], mo=True)

    polePos = getPoleVectorPosition(*newJoints)
    poleCtrl = controller.Controller('{0}_poleVector_ctrl'.format(name), shape='locator', scale=1)
    poleCtrl.createGroups()
    pm.xform(poleCtrl.spaceGrp, t=polePos, ws=True)
    pm.poleVectorConstraint(poleCtrl.transform, ikHandle)
    ikCtrls.append(poleCtrl)

    poleLine = buildPoleVectorLine(ikJoints[1], poleCtrl.transform)

    # cleanup outliner
    ikSystemGrp = pm.group(ikJoints[0], ikHandle, n=name + '_ikSystem_grp')
    ikSystemGrp.visibility.set(False)
    ikCtrlGrp = pm.group([ikCtrl.spaceGrp for ikCtrl in ikCtrls], poleLine, n=name + '_ikCtrl_grp')
    ikGrp = pm.group(ikSystemGrp, ikCtrlGrp, n=name + '_ik_grp')

    return ikJoints, ikCtrlGrp, ikGrp

def buildPoleVectorLine(midJoint, poleVectorControl):
    poleLine = None

    midJntDec = pm.createNode('decomposeMatrix', n='{0}_dec'.format(midJoint))
    poleCtrlDec = pm.createNode('decomposeMatrix', n='{0}_dec'.format(poleVectorControl))
    poleLine = pm.curve(n='{0}_line'.format(poleVectorControl), d=1, p=[(0, 0, 0), (0, 1, 0)])
    poleLine.inheritsTransform.set(False)
    poleLine.template.set(True)

    midJoint.worldMatrix >> midJntDec.inputMatrix
    poleVectorControl.worldMatrix >> poleCtrlDec.inputMatrix
    midJntDec.outputTranslate >> poleLine.controlPoints[0]
    poleCtrlDec.outputTranslate >> poleLine.controlPoints[1]

    return poleLine

def setupSwitch(name, fkJoints, ikJoints, outJoints):
    choiceNodes = []

    ctrl = controller.Controller('{0}_fkIk_ctrl'.format(name), shape='gear', scale=1)
    ctrl.createGroups()
    pm.parentConstraint(outJoints[1], ctrl.spaceGrp, mo=False)
    pm.addAttr(ctrl.transform, longName='fkIk', at='enum', en=['fk', 'ik'], keyable=True)

    for i in xrange(len(outJoints)):
        outJnt = outJoints[i]
        pm.delete(outJnt.listConnections(d=False, type='constraint'))
        outJntParent = outJnt.getParent()
        outJntRotateOrder = outJnt.rotateOrder.get()
        fkJnt = fkJoints[i]
        ikJnt = ikJoints[i]

        choiceNode = pm.createNode('choice', n=outJnt + '_spaceChoice')
        multMtxNode = pm.createNode('multMatrix', n=outJnt + '_worldToLocal_multMtx')
        decMtxNode = pm.createNode('decomposeMatrix', n=outJnt + '_spaceDecMtx')
        decMtxNode.inputRotateOrder.set(outJntRotateOrder)

        ctrl.transform.fkIk >> choiceNode.selector
        fkJnt.worldMatrix >> choiceNode.input[0]
        ikJnt.worldMatrix >> choiceNode.input[1]
        choiceNode.output >> multMtxNode.matrixIn[0]
        if outJntParent:
            outJntParent.worldInverseMatrix >> multMtxNode.matrixIn[1]
        multMtxNode.matrixSum >> decMtxNode.inputMatrix
        decMtxNode.outputTranslate >> outJnt.translate
        decMtxNode.outputRotate >> outJnt.jointOrient
        decMtxNode.outputScale >> outJnt.scale

        choiceNodes.append(choiceNode)

        pm.delete(pm.listConnections(outJnt, type='constraint', d=False))

    return ctrl, choiceNodes

def setupTwist(name, limbOutJoints, limbSkelJoints, upTwistJoints, lowTwistJoints, aimAxisSign):
    # create jonit chain
    upTwistJoints = [limbSkelJoints[0]] + upTwistJoints + [limbSkelJoints[1]]
    newUpTwistJoints = createTwistJoints(upTwistJoints)
    pm.parent(newUpTwistJoints[0], world=True)
    pm.makeIdentity(newUpTwistJoints[0], apply=True)
    newUpTwistJoints[-1].jointOrient.set(0, 0, 0)  # Orient end joint
    pm.parent(newUpTwistJoints[0], limbOutJoints[0])

    lowTwistJoints = [limbSkelJoints[1]] + lowTwistJoints + [limbSkelJoints[2]]
    newLowTwistJoints = createTwistJoints(lowTwistJoints)
    pm.parent(newLowTwistJoints[0], world=True)
    pm.makeIdentity(newLowTwistJoints[0], apply=True)
    newLowTwistJoints[-1].jointOrient.set(0, 0, 0)
    pm.parent(newLowTwistJoints[0], limbOutJoints[1])

    # Create curve
    outJoint1Pos = pm.xform(limbOutJoints[0], q=True, t=True, ws=True)
    outJoint2Pos = pm.xform(limbOutJoints[1], q=True, t=True, ws=True)
    outJoint3Pos = pm.xform(limbOutJoints[2], q=True, t=True, ws=True)

    upCurve = pm.curve(d=3, editPoint=[outJoint1Pos, outJoint2Pos], n=name + '_up_crv')
    lowCurve = pm.curve(d=3, editPoint=[outJoint2Pos, outJoint3Pos], n=name + '_low_crv')

    # Build splineIk
    upTwistIkhandle, upEffector = pm.ikHandle(
        name=name + '_up_ikh',
        solver='ikSplineSolver',
        createCurve=False,
        parentCurve=False,
        startJoint=newUpTwistJoints[0],
        endEffector=newUpTwistJoints[-1],
        curve=upCurve,
        rootOnCurve=True,
    )
    lowTwistIkhandle, lowEffector = pm.ikHandle(
        name=name + '_low_ikh',
        solver='ikSplineSolver',
        createCurve=False,
        parentCurve=False,
        startJoint=newLowTwistJoints[0],
        endEffector=newLowTwistJoints[-1],
        curve=lowCurve,
        rootOnCurve=True,
    )

    # Connect upper handle twist attribute
    outJnt0DecMtx = pm.createNode('decomposeMatrix', n=limbOutJoints[0].name() + '_decMtx')
    outJnt1DecMtx = pm.createNode('decomposeMatrix', n=limbOutJoints[1].name() + '_decMtx')
    outJnt0QuatToEuler = pm.createNode('quatToEuler', n=limbOutJoints[0].name() + '_quatToEuler')
    outJnt1QuatToEuler = pm.createNode('quatToEuler', n=limbOutJoints[1].name() + '_quatToEuler')
    upTwistAddDouble = pm.createNode('addDoubleLinear', n=name + '_upTwist_addDouble')
    upTwistSignMultDouble = pm.createNode('multDoubleLinear', n=name + '_upTwistSign_multDouble')
    upTwistSignMultDouble.input2.set(aimAxisSign)

    limbOutJoints[0].matrix >> outJnt0DecMtx.inputMatrix
    limbOutJoints[1].matrix >> outJnt1DecMtx.inputMatrix

    outJnt0DecMtx.outputQuatX >> outJnt0QuatToEuler.inputQuatX
    outJnt0DecMtx.outputQuatW >> outJnt0QuatToEuler.inputQuatW
    outJnt1DecMtx.outputQuatX >> outJnt1QuatToEuler.inputQuatX
    outJnt1DecMtx.outputQuatW >> outJnt1QuatToEuler.inputQuatW

    outJnt0QuatToEuler.outputRotateX >> upTwistAddDouble.input1
    outJnt1QuatToEuler.outputRotateX >> upTwistAddDouble.input2

    upTwistAddDouble.output >> upTwistSignMultDouble.input1
    upTwistSignMultDouble.output >> upTwistIkhandle.twist

    # Connect lower handle twist attribute
    outJnt2DecMtx = pm.createNode('decomposeMatrix', n=limbOutJoints[2].name() + '_decMtx')
    outJnt2QuatToEuler = pm.createNode('quatToEuler', n=limbOutJoints[2].name() + '_quatToEuler')
    lowTwistSignMultDouble = pm.createNode('multDoubleLinear', n=name + 'lowTwistSign_multDouble')
    lowTwistSignMultDouble.input2.set(aimAxisSign)

    limbOutJoints[2].matrix >> outJnt2DecMtx.inputMatrix
    outJnt2DecMtx.outputQuatX >> outJnt2QuatToEuler.inputQuatX
    outJnt2DecMtx.outputQuatW >> outJnt2QuatToEuler.inputQuatW

    outJnt2QuatToEuler.outputRotateX >> lowTwistSignMultDouble.input1
    lowTwistSignMultDouble.output >> lowTwistIkhandle.twist

    # Connect curve to out joints
    clstGrp, clstCtrlGrp = connectCurvesToOutJoints(name, upCurve, lowCurve, limbOutJoints)

    # Setup stretch
    upScaleCrv = setupStretch(upCurve)
    lowScaleCrv = setupStretch(lowCurve)

    # Connect to skeleton
    for i in xrange(len(newUpTwistJoints)):
        pm.delete(pm.listConnections(upTwistJoints[i], type='constraint', d=False))
        pm.parentConstraint(newUpTwistJoints[i], upTwistJoints[i], mo=True)
        pm.connectAttr('{0}.scale'.format(newUpTwistJoints[i]), '{0}.scale'.format(upTwistJoints[i]), f=True)

    for i in xrange(len(newLowTwistJoints)):
        pm.delete(pm.listConnections(lowTwistJoints[i], type='constraint', d=False))
        pm.parentConstraint(newLowTwistJoints[i], lowTwistJoints[i], mo=True)
        pm.connectAttr('{0}.scale'.format(newLowTwistJoints[i]), '{0}.scale'.format(lowTwistJoints[i]), f=True)

    pm.delete(pm.listConnections(lowTwistJoints[-1], type='constraint', d=False))
    pm.parentConstraint(limbOutJoints[-1], lowTwistJoints[-1], mo=True)
    pm.connectAttr('{0}.scale'.format(limbOutJoints[-1]), '{0}.scale'.format(lowTwistJoints[-1]), f=True)

    # Clenup outliner
    crvGrp = pm.group(upCurve, lowCurve, n=name + '_crv_grp')
    scaleCrvGrp = pm.group(upScaleCrv, lowScaleCrv, n=name + '_scaleCrv_grp')
    crvGrp.inheritsTransform.set(False)
    ikHandleGrp = pm.group(upTwistIkhandle, lowTwistIkhandle, n=name + '_ikHandle_grp')

    twistSystemGrp = pm.group(crvGrp, scaleCrvGrp, ikHandleGrp, clstGrp, n=name + '_twist_system_grp')
    twistSystemGrp.visibility.set(False)
    twistRigGrp = pm.group(twistSystemGrp, clstCtrlGrp, n=name + '_twist_rig_grp')

    return twistRigGrp, clstCtrlGrp

def setupFkIkSwitchCallback(
        switchController,
        choiceNodes,
        outJoints,
        fkControllers,
        ikControllers
    ):
    fkIkSwitchCtrlHub = pm.createNode('transform', n='fkIkSwitchCtrlHub')

    pm.addAttr(fkIkSwitchCtrlHub, at='message', ln=switchController.name())
    switchController.message >> fkIkSwitchCtrlHub.attr(switchController.name())
    for choiceNode in choiceNodes:
        pm.addAttr(switchController, at='message', ln=choiceNode.name())
        choiceNode.message >> switchController.attr(choiceNode.name())
    for skinJoint in outJoints:
        pm.addAttr(switchController, at='message', ln=skinJoint.name())
        skinJoint.message >> switchController.attr(skinJoint.name())
    for fkController in fkControllers:
        pm.addAttr(switchController, at='message', ln=fkController.name())
        fkController.message >> switchController.attr(fkController.name())
    for ikController in ikControllers:
        pm.addAttr(switchController, at='message', ln=ikController.name())
        ikController.message >> switchController.attr(ikController.name())

    scriptNodeContents = '''
import pymel.core as pm
import maya.api.OpenMaya as om

def getPoleVectorPosition(start, mid, end):
    startPos = pm.xform(start, q=True, rp=True, ws=True)
    midPos = pm.xform(mid, q=True, rp=True, ws=True)
    endPos = pm.xform(end, q=True, rp=True, ws=True)

    # convert the rawPos to the vector
    startVector = om.MVector(startPos[0], startPos[1], startPos[2])
    midVector = om.MVector(midPos[0], midPos[1], midPos[2])
    endVector = om.MVector(endPos[0], endPos[1], endPos[2])

    # calculate the pole vector position
    startToEndCenter = startVector + ((endVector - startVector) / 2)
    poleVector = midVector - startToEndCenter
    polePos = midVector + (poleVector * 2)

    return polePos

def matchWithMatrix(controller, matrix, choiceNodes, switchVal):
    if controller.connections(d=False, type='animCurve'):
        print 'match controller with setkey'
        time = pm.currentTime()
        for choiceNode in choiceNodes:
            choiceNode.selector.setKey(t=time, v=switchVal)
        ctrlParent = controller.getParent()
        localMtx = matrix * ctrlParent.worldInverseMatrix.get()
        controller.tx.setKey(t=time, v=localMtx.translate.x)
        controller.ty.setKey(t=time, v=localMtx.translate.y)
        controller.tz.setKey(t=time, v=localMtx.translate.z)
        eulerRotation = localMtx.rotate.asEulerRotation()
        rotateX = pm.util.degrees(eulerRotation.x)
        rotateY = pm.util.degrees(eulerRotation.y)
        rotateZ = pm.util.degrees(eulerRotation.z)
        controller.rx.setKey(t=time, v=rotateX)
        controller.ry.setKey(t=time, v=rotateY)
        controller.rz.setKey(t=time, v=rotateZ)
    else:
        pm.xform(controller, matrix=matrix, ws=True)

def matchFkIk():
    sel = pm.selected()[0]

    if sel.hasAttr('fkIk'):
        switchCtrl = sel
    else:
        return False

    switchVal = switchCtrl.fkIk.get()

    outJnt1SpaceChoice = switchCtrl.{outJoint1SpaceChoice}.get()
    outJnt2SpaceChoice = switchCtrl.{outJoint2SpaceChoice}.get()
    outJnt3SpaceChoice = switchCtrl.{outJoint3SpaceChoice}.get()

    outJnt1 = switchCtrl.{outJoint1}.get()
    outJnt2 = switchCtrl.{outJoint2}.get()
    outJnt3 = switchCtrl.{outJoint3}.get()

    fkCtrl1 = switchCtrl.{outFkCtrl1}.get()
    fkCtrl2 = switchCtrl.{outFkCtrl2}.get()
    fkCtrl3 = switchCtrl.{outFkCtrl3}.get()
    ikCtrl = switchCtrl.{outIkCtrl}.get()
    poleVectorCtrl = switchCtrl.{outPoleVectorCtrl}.get()

    outJnt1WsMtx = outJnt1.worldMatrix.get()
    outJnt2WsMtx = outJnt2.worldMatrix.get()
    outJnt3WsMtx = outJnt3.worldMatrix.get()
    poleVectorPos = getPoleVectorPosition(outJnt1, outJnt2, outJnt3)

    outJnt1SpaceChoice.selector.set(switchVal)
    outJnt2SpaceChoice.selector.set(switchVal)
    outJnt3SpaceChoice.selector.set(switchVal)

    if switchVal == 0:  # ik to fk
        matchWithMatrix(fkCtrl1, outJnt1WsMtx, [outJnt1SpaceChoice], switchVal)
        matchWithMatrix(fkCtrl2, outJnt2WsMtx, [outJnt2SpaceChoice], switchVal)
        matchWithMatrix(fkCtrl3, outJnt3WsMtx, [outJnt3SpaceChoice], switchVal)
    elif switchVal ==1:  # fk to ik
        choiceNodes = [outJnt1SpaceChoice, outJnt2SpaceChoice, outJnt3SpaceChoice]
        matchWithMatrix(ikCtrl, outJnt3WsMtx, choiceNodes, switchVal)
        if poleVectorCtrl.connections(d=False, type='animCurve'):
            print 'match pole vector controller with setkey'
            time = pm.currentTime()
            ctrlParent = poleVectorCtrl.getParent()
            ctrlParentWsPos = pm.xform(ctrlParent, q=True, t=True, ws=True)
            ctrlParentWsVector = pm.datatypes.Vector(ctrlParentWsPos)
            localPoleVectorPos = poleVectorPos - ctrlParentWsVector
            poleVectorCtrl.tx.setKey(t=time, v=localPoleVectorPos.x)
            poleVectorCtrl.ty.setKey(t=time, v=localPoleVectorPos.y)
            poleVectorCtrl.tz.setKey(t=time, v=localPoleVectorPos.z)
        else:
            pm.xform(poleVectorCtrl, t=(poleVectorPos.x, poleVectorPos.y, poleVectorPos.z), ws=True)

# Attach script job to 'fkIk' attributes
fkIkSwitchCtrlHubs = pm.ls('*fkIkSwitchCtrlHub', recursive=True)
for fkIkSwitchCtrlHub in fkIkSwitchCtrlHubs:
    fkIkCtrlAttrs = fkIkSwitchCtrlHub.listAttr(ud=True)
    for fkIkCtrlAttr in fkIkCtrlAttrs:
        fkIkCtrl = fkIkCtrlAttr.get()
        pm.scriptJob(kws=True, attributeChange=[fkIkCtrl.fkIk, matchFkIk])
    '''.format(
        outJoint1SpaceChoice=choiceNodes[0],
        outJoint2SpaceChoice=choiceNodes[1],
        outJoint3SpaceChoice=choiceNodes[2],
        outJoint1=outJoints[0],
        outJoint2=outJoints[1],
        outJoint3=outJoints[2],
        outFkCtrl1=fkControllers[0],
        outFkCtrl2=fkControllers[1],
        outFkCtrl3=fkControllers[2],
        outIkCtrl=ikControllers[0],
        outPoleVectorCtrl=ikControllers[1]
    )

    scriptNodeName = 'fkIkMatchScriptNode'
    pm.scriptNode(beforeScript=scriptNodeContents, scriptType=1, sourceType='python', n=scriptNodeName)
    pm.scriptNode(scriptNodeName, executeBefore=True)


# Utils #
def getPoleVectorPosition(start, mid, end):
    startPos = pm.xform(start, q=True, rp=True, ws=True)
    midPos = pm.xform(mid, q=True, rp=True, ws=True)
    endPos = pm.xform(end, q=True, rp=True, ws=True)

    # convert the rawPos to the vector
    startVector = om.MVector(startPos[0], startPos[1], startPos[2])
    midVector = om.MVector(midPos[0], midPos[1], midPos[2])
    endVector = om.MVector(endPos[0], endPos[1], endPos[2])

    # calculate the pole vector position
    startToEndCenter = startVector + ((endVector - startVector) / 2)
    poleVector = midVector - startToEndCenter
    polePos = midVector + (poleVector * 2)

    return (polePos.x, polePos.y, polePos.z)

def connectCurvesToOutJoints(name, upCurve, lowCurve, outJoints):
    clst1, clst1Handle = pm.cluster('{0}.cv[0]'.format(upCurve.name()), n=name + '_crv_clst1')
    clst2, clst2Handle = pm.cluster('{0}.cv[1:2]'.format(upCurve.name()), n=name + '_crv_clst2')
    clst3, clst3Handle = pm.cluster(['{0}.cv[3]'.format(upCurve.name()), '{0}.cv[0]'.format(lowCurve.name())], n=name + '_crv_clst3')
    clst4, clst4Handle = pm.cluster('{0}.cv[1:2]'.format(lowCurve.name()), n=name + '_crv_clst4')
    clst5, clst5Handle = pm.cluster('{0}.cv[3]'.format(lowCurve.name()), n=name + '_crv_clst5')

    clst1Space = pm.createNode('transform', n=clst1.name() + '_zero')
    clst2Space = pm.createNode('transform', n=clst2.name() + '_zero')
    clst3Space = pm.createNode('transform', n=clst3.name() + '_zero')
    clst4Space = pm.createNode('transform', n=clst4.name() + '_zero')
    clst5Space = pm.createNode('transform', n=clst5.name() + '_zero')

    pm.matchTransform(clst2Space, clst2Handle, pos=True)
    pm.matchTransform(clst2Space, outJoints[0], rot=True)
    pm.matchTransform(clst4Space, clst4Handle, pos=True)
    pm.matchTransform(clst4Space, outJoints[2], rot=True)

    # Create cluster controllers
    clst2Ctrl = general.createController(clst2Space, clst2.name() + '_ctrl')
    clst2CtrlSpaceGrp = general.getSpaceGrp(clst2Ctrl)
    clst3Ctrl = general.createController(clst3Space, clst3.name() + '_ctrl')
    clst3CtrlSpaceGrp = general.getSpaceGrp(clst3Ctrl)
    clst4Ctrl = general.createController(clst4Space, clst4.name() + '_ctrl')
    clst4CtrlSpaceGrp = general.getSpaceGrp(clst4Ctrl)

    pm.parentConstraint(outJoints[0], clst1Space, mo=False)
    pm.parentConstraint(outJoints[0], clst2CtrlSpaceGrp, mo=True)
    pm.pointConstraint(outJoints[1], clst3CtrlSpaceGrp, mo=False)
    clst3CtrlOriCnst = pm.orientConstraint(outJoints[0], outJoints[1], clst3CtrlSpaceGrp, mo=False)
    clst3CtrlOriCnst.interpType.set(2)
    pm.parentConstraint(outJoints[1], clst4CtrlSpaceGrp, mo=True)
    pm.parentConstraint(outJoints[2], clst5Space, mo=False)

    clst1Space | clst1Handle
    clst2Space | clst2Handle
    clst3Space | clst3Handle
    clst4Space | clst4Handle
    clst5Space | clst5Handle

    # Cleanup outliner
    clstGrp = pm.group(clst1Space, clst2Space, clst3Space, clst4Space, clst5Space, n=name + '_clst_grp')
    clstCtrlGrp = pm.group(clst2CtrlSpaceGrp, clst3CtrlSpaceGrp, clst4CtrlSpaceGrp, n=name + '_bendCtrl_grp')

    return clstGrp, clstCtrlGrp

def setupStretch(stretchCurve):
    scaleCrv = pm.duplicate(stretchCurve, n=stretchCurve.name() + '_scaleCrv')[0]
    ikHandle = stretchCurve.worldSpace.connections(type='ikHandle')[0]
    startJoint = ikHandle.startJoint.get()
    endJoint = ikHandle.endEffector.get().getParent()
    allStartChildJnts = startJoint.getChildren(ad=True, type='joint')
    allStartChildJnts.append(startJoint)
    allStartChildJnts.reverse()
    scaleJnts = []
    for jnt in allStartChildJnts:
        if jnt == endJoint:
            scaleJnts.append(jnt)
            break
        scaleJnts.append(jnt)

    stretchCrvInfo = pm.createNode('curveInfo', n=stretchCurve.name() + '_crvInfo')
    scaleCrvInfo = pm.createNode('curveInfo', n=scaleCrv.name() + '_crvInfo')
    scaleRatioDiv = pm.createNode('multiplyDivide', n=stretchCrvInfo.name() + '_stretchRatio_Div')
    scaleRatioDiv.operation.set(2)

    stretchCurve.worldSpace >> stretchCrvInfo.inputCurve
    scaleCrv.worldSpace >> scaleCrvInfo.inputCurve
    stretchCrvInfo.arcLength >> scaleRatioDiv.input1X
    scaleCrvInfo.arcLength >> scaleRatioDiv.input2X

    for jnt in scaleJnts:
        scaleRatioDiv.outputX >> jnt.scaleX

    return scaleCrv

def createDrivingJoints(joints, suffix):
    newJoints = []
    joints = [pm.PyNode(jnt) for jnt in joints]

    for jnt in joints:
        pm.delete(jnt.connections(type='constraint', d=False))
        newJnt = pm.duplicate(jnt, n='{0}{1}'.format(jnt, suffix), po=True)[0]
        parentCnst = pm.parentConstraint(newJnt, jnt, mo=True)
        parentCnst.interpType.set(2)
        newJnt.s >> jnt.s
        newJoints.append(newJnt)

    for i in xrange(len(newJoints)):
        if i == 0:
            continue
        newJoints[i-1] | newJoints[i]

    return newJoints


def createTwistJoints(joints):
    twistJoints = []
    joints = [pm.PyNode(jnt) for jnt in joints]

    for jnt in joints:
        newJnt = pm.duplicate(jnt, n='{0}_twist'.format(jnt), po=True)[0]
        twistJoints.append(newJnt)

    for i in xrange(len(twistJoints)):
        if i == 0:
            continue
        twistJoints[i-1] | twistJoints[i]

    return twistJoints
