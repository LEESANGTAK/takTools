from maya.api import OpenMaya as om
import pymel.core as pm

from ..utils import globalUtil
from ..utils import skin as skinUtil
from ..base import general
from ..base import module
from ..base import controller


def build(
    name,
    joints,
    numControls,
    stretch=True,
    twist=True,
    roll=True,
    thickness=False,
    slide=False,
    fk=False,
    wave=False,
    dynamic=False,
    globalControl=False,
    parentGrp=False
):
    startJoint = pm.PyNode(joints[0])
    endJoint = pm.PyNode(joints[-1])

    moduleObj = module.Module(name)

    outJoints = createOutJoints(startJoint, endJoint)
    moduleObj.outGrp | outJoints[0]

    ikJoints, ikControls = buildIK(name, moduleObj, outJoints, startJoint, numControls, stretch, slide, twist, roll, thickness, wave, dynamic, parentGrp)

    if fk:
        cleanupOutJoints(outJoints)
        fkJoints, fkControls = buildFK(name, moduleObj, outJoints)
        setupSwitch(outJoints, ikJoints, fkJoints, ikControls, fkControls)
        fkControls[0].transform.fkIk.set(1)

    if globalControl:
        buildGlobalControl(name, moduleObj, startJoint)


def buildIK(name, moduleObj, outJoints, startJoint, numControls, stretch, slide, twist, roll, thickness, wave, dynamic, parentGrp):
    # Create curve
    joints = startJoint.getChildren(ad=True, type='joint')
    joints.append(startJoint)
    joints.reverse()
    spans = numControls - 1
    crv = createCurveWithJoints(name, joints, spans)

    ikJoints = duplicateJointChain(outJoints, '_ik')
    for i in range(len(ikJoints)):
        pm.parentConstraint(ikJoints[i], outJoints[i], mo=False)
        ikJoints[i].scale >> outJoints[i].scale

    # Create ikHandle
    ikHandle = pm.ikHandle(name=name + '_ikh', solver='ikSplineSolver', sj=ikJoints[0], ee=ikJoints[-1], curve=crv, createCurve=False, parentCurve=False)[0]

    # Create curve joints
    crvJoints = []
    j = 0
    for i in range(len(crv.cv)):
        if i in [1, len(crv.cv)-2]: continue
        crvJnt = pm.createNode('joint', n='{0}_{1:02d}_crvJnt'.format(crv, j))
        pm.xform(crvJnt, t=crv.cv[i].getPosition(), ws=True)
        crvJoints.append(crvJnt)
        j += 1
    orientCurveJoints(crvJoints, ikJoints)
    bindCurve(crv, crvJoints)
    crvJntGrp = pm.group(crvJoints, n='{0}_crvJnt_grp'.format(crv))

    # Create Controllers
    ikControls = []
    ctrlColor = 'skyBlue'
    for crvJnt in crvJoints:
        ctrlObj = controller.Controller(name='{0}_{1:02d}_ik_ctrl'.format(name, crvJoints.index(crvJnt)), shape='cube', color=ctrlColor)
        ctrlObj.createGroups(space=True, auto=True, extra=True)
        ctrlObj.lockHide(['scale', 'visibility'], ['X', 'Y', 'Z'])

        if crvJoints.index(crvJnt) == len(crvJoints)-1:
            ctrlObj.setColor('lightRed')

        ctrlObj.matchTo(crvJnt, position=True, orientation=True)

        ctrlObj.connectTo(crvJnt, method='constraint', parent=True)
        ikControls.append(ctrlObj)

    # Setup stretch
    if stretch:
        scaleCrv = setupStretch(crv, ikJoints, ikControls[-1].transform)
        pm.parent(scaleCrv, moduleObj.systemGrp)

    # Setup slide
    if slide:
        setupSlide(ikHandle, ikControls[-1].transform)

    # Setup twist
    if twist:
        setupTwist(ikHandle, ikControls[-1].transform)
        setTwist(ikHandle, ikControls)

    # Setup roll
    if roll:
        setupRoll(ikHandle, ikControls[-1].transform)

    # Setup thickness
    if thickness:
        setupThickness(ikJoints, ikControls[-1].transform)

    # Setup wave
    if wave:
        setupWave(name, crv, ikControls[-1], moduleObj)

    # Setup dynamic
    if dynamic:
        dynCrv = setupDynamic(name, crv, ikControls[-1], ikHandle, moduleObj)
        setupBakeLocators(dynCrv, ikControls, moduleObj, ikJoints)

    # Create skin mesh
    skinMesh = skinUtil.createSkinMeshWithJoints(name, joints)

    # Cleanup outliner
    pm.parent(skinMesh, moduleObj.geoGrp)
    pm.parent(ikJoints[0], ikHandle, crvJntGrp, moduleObj.systemGrp)
    pm.parent(crv, moduleObj.noTransformGrp)
    pm.parent([ctrlObj.spaceGrp for ctrlObj in ikControls], moduleObj.ctrlGrp)
    moduleObj.geoGrp.hide()
    moduleObj.outGrp.hide()
    moduleObj.systemGrp.hide()

    setupHybridIK(ikControls)

    if parentGrp:
        pm.parent(moduleObj.topGrp, parentGrp)

    pm.select(skinMesh, r=True)

    return ikJoints, ikControls

def orientCurveJoints(crvJoints, outJoints):
    for crvJnt in crvJoints:
        crvJntPos = pm.xform(crvJnt, q=True, rp=True, ws=True)
        closestOutJnt = findClosestJnt(crvJntPos, outJoints)
        pm.matchTransform(crvJnt, closestOutJnt, rot=True)

def bindCurve(crv, crvJoitns):
    skinClst = pm.skinCluster(crvJoitns, crv, mi=1, dr=4.0, tsb=True, omi=False, nw=True)

def createOutJoints(startJoint, endJoint):
    outJoints = []

    startJointChildJnts = startJoint.getChildren(ad=True, type='joint')
    startJointChildJnts.reverse()
    validJoints = [startJoint]
    for jnt in startJointChildJnts:
        if jnt == endJoint:
            validJoints.append(jnt)
            break
        validJoints.append(jnt)

    outJoints = general.createJointChain(validJoints, '_outJnt')

    for i in range(len(outJoints)):
        pm.parentConstraint(outJoints[i], validJoints[i], mo=True)

    return outJoints

def createCurveWithJoints(name, joints, spans):
    crv = None

    editPoints = [pm.xform(jnt, q=True, t=True, ws=True) for jnt in joints]
    crv = pm.curve(d=3, editPoint=editPoints, n=name + '_crv')
    crv = pm.rebuildCurve(crv, spans=spans, keepRange=0, ch=False, replaceOriginal=True)[0]

    return crv

def findClosestJnt(clstPos, outJoints):
    closestJnt = None

    clstPnt = pm.datatypes.Point(clstPos)
    minDist = 10000000000.0
    for outJnt in outJoints:
        outJntPnt = pm.datatypes.Point(pm.xform(outJnt, q=True, t=True, ws=True))
        delta = outJntPnt - clstPnt
        if delta.length() < minDist:
            closestJnt = outJnt
            minDist = delta.length()

    return closestJnt

def setupStretch(curve, outJoints, controller):
    scaleCrv = pm.duplicate(curve, n=curve.name() + '_scale')[0]
    crvInfo = pm.createNode('curveInfo', n=curve.name() + '_curveInfo')
    scaleCrvInfo = pm.createNode('curveInfo', n=scaleCrv.name() + '_curveInfo')
    stretchRatioDiv = pm.createNode('multiplyDivide', n=curve.name() + '_stretchRatio_div')
    stretchRatioDiv.operation.set(2)
    stertchOnOffBlend = pm.createNode('blendColors', n='{0}_stertchOnOff_blend'.format(curve.name()))
    stertchOnOffBlend.color2R.set(1)

    pm.addAttr(controller, longName='stretchOnOff', attributeType='double', min=0.0, max=1.0, dv=0.0, keyable=True)

    # Animation layer will cause problem when default value is not 0
    minGrowVal = -10.0
    pm.addAttr(controller, longName='grow', attributeType='double', min=minGrowVal, max=0.0, dv=0.0, keyable=True)
    growValNormalize = pm.createNode('multDoubleLinear', n=curve.name() + '_growValNormalize')
    growValNormalize.input2.set(1.0/minGrowVal)
    growReverse = pm.createNode('reverse', n='{0}_growRev'.format(curve.name()))
    growValMult = pm.createNode('multDoubleLinear', n=curve.name() + '_growValMult')

    zeroScalePreventCond = pm.createNode('condition', n='{0}_zeroScalePrevent_cond'.format(curve.name()))
    zeroScalePreventCond.colorIfTrueR.set(0.001)

    curve.worldSpace >> crvInfo.inputCurve
    scaleCrv.worldSpace >> scaleCrvInfo.inputCurve

    crvInfo.arcLength >> stretchRatioDiv.input1X
    scaleCrvInfo.arcLength >> stretchRatioDiv.input2X

    controller.stretchOnOff >> stertchOnOffBlend.blender
    controller.grow >> growValNormalize.input1
    growValNormalize.output >> growReverse.inputX

    stretchRatioDiv.outputX >> stertchOnOffBlend.color1R
    stertchOnOffBlend.outputR >> growValMult.input1

    growReverse.outputX >> zeroScalePreventCond.firstTerm
    growReverse.outputX >> zeroScalePreventCond.colorIfFalseR
    zeroScalePreventCond.outColorR >> growValMult.input2

    for outJnt in outJoints:
        growValMult.output >> outJnt.scaleX

    return scaleCrv

def setupSlide(ikHandle, controller):
        minVal = -10.0
        slideValToOffsetRemap = pm.createNode('remapValue', n='{0}_slideValToOffset_remap'.format(controller))
        slideValToOffsetRemap.inputMin.set(minVal)
        slideValToOffsetRemap.inputMax.set(0.0)
        slideValToOffsetRemap.outputMin.set(1.0)
        slideValToOffsetRemap.outputMax.set(0.0)
        pm.addAttr(controller, longName='slide', attributeType='double', min=minVal, max=0.0, dv=0.0, keyable=True)

        controller.slide >> slideValToOffsetRemap.inputValue
        slideValToOffsetRemap.outValue >> ikHandle.offset

def setupTwist(ikHandle, controller):
    pm.addAttr(controller, ln='twist', at='double', dv=0, keyable=True)
    controller.twist >> ikHandle.twist

def setupRoll(ikHandle, controller):
    pm.addAttr(controller, ln='roll', at='double', dv=0, keyable=True)
    controller.roll >> ikHandle.roll

def setupThickness(outJoints, controller):
    pm.addAttr(controller, ln='thickness', at='double', min=0, dv=1, keyable=True)
    for jnt in outJoints:
        controller.thickness >> jnt.scaleY
        controller.thickness >> jnt.scaleZ

def setupWave(name, curve, endCtrl, module):
    # Nodes setup
    crv = pm.duplicate(curve, n='{0}_wave_crv'.format(name))[0]

    blendshape = pm.blendShape(crv, curve, origin='local', frontOfChain=True)[0]
    blendshape.attr(crv.name()).set(1)

    sine, sineHandle = pm.nonLinear(crv, type='sine')
    sineHandle.rename('{0}_sineHandle'.format(name))
    sine.dropoff.set(-1)
    sine.highBound.set(0)

    numCVs = crv.numCVs()
    startPosition = pm.xform(crv.cv[0], q=True, t=True, ws=True)
    endPosition = pm.xform(crv.cv[numCVs-1], q=True, t=True, ws=True)

    aimVector = pm.datatypes.Point(endPosition) - pm.datatypes.Point(startPosition)
    scale = aimVector.length()

    aimVector.normalize()
    sceneUpVector = pm.datatypes.Vector(0.0, 1.0, 0.0)
    rightVector = aimVector ^ sceneUpVector
    otherVector = aimVector ^ rightVector

    matrixList = [
        otherVector.x, otherVector.y, otherVector.z, 0.0,
        -aimVector.x, -aimVector.y, -aimVector.z, 0.0,
        rightVector.x, rightVector.y, rightVector.z, 0.0,
        startPosition[0], startPosition[1], startPosition[2], 1.0
    ]
    sineHandleMatrix = pm.datatypes.Matrix(matrixList)

    pm.xform(sineHandle, matrix=sineHandleMatrix, ws=True)

    sineHandle.scale.set(scale, scale, scale)
    sineHandle.shear.set(0, 0, 0)

    addWaveAttrs(endCtrl.transform)

    sineHandleSpace = pm.createNode('transform', n='{0}_zero'.format(sineHandle.name()))
    pm.matchTransform(sineHandleSpace, sineHandle, pos=True, rot=True, scale=True)
    pm.parent(sineHandle, sineHandleSpace)

    # DG
    endCtrl.transform.waveOnOff >> sine.envelope
    endCtrl.transform.waveOnOff >> blendshape.attr(crv.name())
    endCtrl.transform.waveAmplitude >> sineHandle.amplitude
    endCtrl.transform.waveLength >> sineHandle.wavelength
    endCtrl.transform.waveOffset >> sineHandle.offset
    endCtrl.transform.waveOrient >> sineHandle.rotateY

    # DAG
    pm.parent(crv, sineHandleSpace, module.systemGrp)

def addWaveAttrs(waveCtrl):
    ATTRIBUTES_INFO=[
        {'waveOnOff': {'type': 'double', 'keyable': True}},
        {'waveAmplitude': {'type': 'double', 'keyable': True}},
        {'waveLength': {'type': 'double', 'keyable': True}},
        {'waveOffset': {'type': 'double', 'keyable': True}},
        {'waveOrient': {'type': 'double', 'keyable': True}},
    ]
    # Add dvider
    pm.addAttr(waveCtrl, ln='wave', at='enum', en='---------------:')
    pm.setAttr('{}.{}'.format(waveCtrl, 'wave'), channelBox=True)

    # Add attributes
    for attrInfo in ATTRIBUTES_INFO:
        for attrName, attrProperties in attrInfo.items():
            pm.addAttr(waveCtrl, ln=attrName, at=attrProperties['type'], keyable=attrProperties['keyable'])

    # Set default value
    waveCtrl.waveOnOff.setRange(0, 1)
    waveCtrl.waveAmplitude.set(0.1)
    waveCtrl.waveLength.set(1)

def setupDynamic(name, curve, endCtrl, ikHandle, module):
    # Nodes setup
    timeNode = pm.PyNode('time1')

    rebuildCrv = pm.createNode('rebuildCurve', n='{0}_rebuildCrv'.format(curve))
    rebuildCrv.degree.set(1)
    rebuildCrv.smooth.set(-3)
    rebuildCrv.endKnots.set(1)
    rebuildCrv.keepRange.set(0)
    rebuildCrv.keepControlPoints.set(True)
    rebuildCrv.keepEndPoints.set(True)
    rebuildCrv.keepTangents.set(False)
    rebuildCrvShape = pm.createNode('nurbsCurve', n='{0}_rebuildCrvShape'.format(curve))

    nucleus = getNucleus(name)
    nucleus.spaceScale.set(0.05)

    hairSystem = pm.createNode('hairSystem')
    hairSystem.getTransform().rename('{0}_hairSystem'.format(name))
    hairSystem.active.set(1)
    hairSystem.hairsPerClump.set(1)
    hairSystem.clumpWidth.set(0)
    hairSystem.stretchResistance.set(200)
    hairSystem.compressionResistance.set(200)
    hairSystem.stiffnessScale[1].stiffnessScale_FloatValue.set(1)

    follicle = pm.createNode('follicle', n='{0}_follicle'.format(name))
    follicle.restPose.set(1)
    follicle.startDirection.set(1)
    follicle.degree.set(3)

    dynCrv =  pm.duplicate(curve, n='{0}_dyn_crv'.format(name))[0]

    addDynAttrs(endCtrl.transform)

    enableCond = pm.createNode('condition', n='{0}_dynEnable_cond')
    enableCond.secondTerm.set(1)
    enableCond.colorIfTrueR.set(3)

    # DG
    timeNode.outTime >> nucleus.currentTime
    timeNode.outTime >> hairSystem.currentTime

    nucleus.startFrame >> hairSystem.startFrame

    outputObjectsId = globalUtil.findMultiAttributeEmptyIndex(nucleus, 'outputObjects')
    nucleus.outputObjects[outputObjectsId] >> hairSystem.nextState

    inputActiveId = globalUtil.findMultiAttributeEmptyIndex(nucleus, 'inputActive')
    hairSystem.currentState >> nucleus.inputActive[inputActiveId]

    inputActiveStartId = globalUtil.findMultiAttributeEmptyIndex(nucleus, 'inputActiveStart')
    hairSystem.startState >> nucleus.inputActiveStart[inputActiveStartId]

    hairSystem.outputHair[0] >> follicle.currentPosition
    follicle.outHair >> hairSystem.inputHair[0]

    curve.worldSpace >> rebuildCrv.inputCurve
    rebuildCrv.outputCurve >> rebuildCrvShape.create
    rebuildCrvShape.local >> follicle.startPosition
    curve.getTransform().worldMatrix >> follicle.startPositionMatrix

    follicle.outCurve >> dynCrv.create

    dynCrv.worldSpace >> ikHandle.inCurve

    endCtrl.transform.enable >> nucleus.enable
    endCtrl.transform.enable >> hairSystem.active
    endCtrl.transform.enable >> enableCond.firstTerm
    enableCond.outColorR >> hairSystem.simulationMethod

    endCtrl.transform.startFrame >> nucleus.startFrame
    endCtrl.transform.subSteps >> nucleus.subSteps
    endCtrl.transform.bendResistance >> hairSystem.bendResistance
    endCtrl.transform.stiffness >> hairSystem.stiffness
    endCtrl.transform.damp >> hairSystem.damp
    endCtrl.transform.drag >> hairSystem.drag
    endCtrl.transform.startCurveAttract >> hairSystem.startCurveAttract
    endCtrl.transform.attractionDamp >> hairSystem.attractionDamp

    # Cleanup DAG
    pm.parent(follicle.getTransform(), module.systemGrp)
    pm.parent(rebuildCrvShape.getTransform(), nucleus, hairSystem, dynCrv, module.noTransformGrp)

    return dynCrv


def setupBakeLocators(dynCrv, ikControls, moduleObj, joints):
    crvDag = globalUtil.getDagPath(dynCrv.name())
    crvFn = om.MFnNurbsCurve(crvDag)

    for ikCtrl in ikControls:
        ctrlPos = ikCtrl.transform.getTranslation(space='world')
        closestPoint, param = crvFn.closestPoint(om.MPoint(ctrlPos), space=om.MSpace.kWorld)
        pointOnCrvInfo = pm.createNode('pointOnCurveInfo', n='{}_pntOnCrvInfo'.format(ikCtrl))
        dynCrv.worldSpace >> pointOnCrvInfo.inputCurve
        pointOnCrvInfo.parameter.set(param)
        bakeLoc = pm.spaceLocator(n='{}_bake_loc'.format(ikCtrl))
        bakeLocAnchor = pm.group(bakeLoc, n='{}_anchor'.format(bakeLoc))
        pointOnCrvInfo.result.position >> bakeLocAnchor.translate

        closestJnt = globalUtil.findClosestJoint(pm.xform(bakeLocAnchor, q=True, rp=True, ws=True), joints)
        if closestJnt == joints[-1]:
            closestJnt = joints[-1].getParent()
        pm.orientConstraint(closestJnt, bakeLocAnchor, mo=False)

        pm.parent(bakeLocAnchor, moduleObj.noTransformGrp)


def getNucleus(name):
    nucleusNode = None

    nucleusNodes = pm.ls(type='nucleus')
    for node in nucleusNodes:
        if node.name() == name:
            nucleusNode = node
            break

    if not nucleusNode:
        nucleusNode = pm.createNode('nucleus', n='{0}_nucleus'.format(name))

    return nucleusNode

def addDynAttrs(dynCtrl):
    ATTRIBUTES_INFO=[
        {'enable': {'type': 'bool', 'keyable': True}},
        {'startFrame': {'type': 'long', 'keyable': True}},
        {'subSteps': {'type': 'long', 'keyable': True}},
        {'bendResistance': {'type': 'double', 'range':[0, 1000], 'keyable': True}},
        {'stiffness': {'type': 'double', 'range':[0, 1000], 'keyable': True}},
        {'damp': {'type': 'double', 'range':[0, 1000], 'keyable': True}},
        {'drag': {'type': 'double', 'range':[0, 1000], 'keyable': True}},
        {'startCurveAttract': {'type': 'double', 'range':[0, 1000], 'keyable': True}},
        {'attractionDamp': {'type': 'double', 'range':[0, 1], 'keyable': True}},
    ]

    # Add dvider
    pm.addAttr(dynCtrl, ln='dynamic', at='enum', en='---------------:')
    pm.setAttr('{}.{}'.format(dynCtrl, 'dynamic'), channelBox=True)

    # Add attributes
    for attrInfo in ATTRIBUTES_INFO:
        for attrName, attrProperties in attrInfo.items():
            if attrProperties.has_key('range'):
                pm.addAttr(dynCtrl, ln=attrName, at=attrProperties['type'], min=attrProperties['range'][0], max=attrProperties['range'][1], keyable=attrProperties['keyable'])
            else:
                pm.addAttr(dynCtrl, ln=attrName, at=attrProperties['type'], keyable=attrProperties['keyable'])

    # Set default value
    dynCtrl.enable.set(False)
    dynCtrl.startFrame.set(100000)
    dynCtrl.subSteps.set(3)
    dynCtrl.bendResistance.set(0.1)
    dynCtrl.stiffness.set(0.1)
    dynCtrl.damp.set(0.1)
    dynCtrl.drag.set(0.05)
    dynCtrl.startCurveAttract.set(0.0)
    dynCtrl.attractionDamp.set(1.0)

def setupHybridIK(controls):
    for i in range(len(controls)):
        curCtrl = controls[i]
        if i == 0:
            continue
        parentCtrl = controls[i-1]
        pm.parent(curCtrl.spaceGrp, parentCtrl.spaceGrp)
        pm.matchTransform(curCtrl.spaceGrp, parentCtrl.transform, pivots=True)
        pm.orientConstraint(parentCtrl.transform, curCtrl.spaceGrp, mo=True)

def setTwist(ikHandle, controls):
    ikHandle.dTwistControlEnable.set(True)
    ikHandle.dWorldUpType.set(4)
    ikHandle.dWorldUpAxis.set(4)
    ikHandle.dWorldUpVectorY.set(0)
    ikHandle.dWorldUpVectorZ.set(-1)
    ikHandle.dWorldUpVectorEndY.set(0)
    ikHandle.dWorldUpVectorEndZ.set(-1)
    controls[0].transform.worldMatrix >> ikHandle.dWorldUpMatrix
    controls[-1].transform.worldMatrix >> ikHandle.dWorldUpMatrixEnd


def buildFK(name, moduleObj, outJoints):
    fkJoints = duplicateJointChain(outJoints, '_fk')
    fkCtrls = attachFKControls(name, fkJoints)

    pm.parent(fkJoints[0], moduleObj.systemGrp)
    pm.parent(fkCtrls[0].spaceGrp, moduleObj.ctrlGrp)

    return fkJoints, fkCtrls


def duplicateJointChain(joints, suffix):
    fkJoints = []
    for jnt in joints:
        fkJnt = pm.duplicate(jnt, n=jnt.name().replace('_outJnt', suffix), po=True)[0]
        fkJoints.append(fkJnt)
    for i in range(len(fkJoints)):
        if i == 0:
            continue
        fkJoints[i-1] | fkJoints[i]
    return fkJoints


def attachFKControls(name, fkJoints):
    fkCtrls = []

    i = 0
    for fkJnt in fkJoints:
        if globalUtil.isEndItem(fkJnt, fkJoints):
            break
        ctrl = controller.Controller('{0}_{1:02d}_fk_ctrl'.format(name, i), 'circleX')
        ctrl.createGroups(space=True, auto=True, extra=True)
        ctrl.matchTo(fkJnt, position=True, orientation=True)
        ctrl.connectTo(fkJnt, parent=True, scale=True)
        ctrl.transform.visibility.setKeyable(False)
        fkCtrls.append(ctrl)
        i += 1

    for i in range(len(fkCtrls)):
        if i == 0:
            continue
        fkCtrls[i-1].transform | fkCtrls[i].spaceGrp

    return fkCtrls


def setupSwitch(outJoints, ikJoints, fkJoints, ikControls, fkControls):
    baseCtrl = ikControls[-1]
    otherCtrls = ikControls[:-1] + fkControls

    # Add proxy switch attribute to all controls
    fkIkAttrName = 'fkIk'
    pm.addAttr(baseCtrl.transform, ln=fkIkAttrName, at='enum', en=['fk', 'ik'], keyable=True)
    for ctrl in otherCtrls:
        pm.addAttr(ctrl.transform, ln=fkIkAttrName, proxy='{0}.{1}'.format(baseCtrl.transform, fkIkAttrName))

    for i in range(len(outJoints)):
        outJnt = outJoints[i]
        transChoice = pm.createNode('choice', n='{0}_trans_choice'.format(outJnt))
        rotateChoice = pm.createNode('choice', n='{0}_rotate_choice'.format(outJnt))
        scaleChoice = pm.createNode('choice', n='{0}_scale_choice'.format(outJnt))

        fkJoints[i].translate >> transChoice.input[0]
        ikJoints[i].translate >> transChoice.input[1]
        baseCtrl.transform.fkIk >> transChoice.selector
        fkJoints[i].rotate >> rotateChoice.input[0]
        ikJoints[i].rotate >> rotateChoice.input[1]
        baseCtrl.transform.fkIk >> rotateChoice.selector
        fkJoints[i].scale >> scaleChoice.input[0]
        ikJoints[i].scale >> scaleChoice.input[1]
        baseCtrl.transform.fkIk >> scaleChoice.selector

        transChoice.output >> outJnt.translate
        rotateChoice.output >> outJnt.rotate
        scaleChoice.output >> outJnt.scale

    revNode = pm.createNode('reverse')
    baseCtrl.transform.fkIk >> revNode.inputX
    baseCtrl.transform.fkIk >> ikControls[0].spaceGrp.visibility
    revNode.outputX >> fkControls[0].spaceGrp.visibility


def cleanupOutJoints(outJoints):
    for jnt in outJoints:
        constraints = jnt.connections(d=False, type='constraint')
        pm.delete(constraints)
        scaleConnections = jnt.scale.inputs(connections=True, plugs=True)
        scaleConnections[0][1] // scaleConnections[0][0]


def buildGlobalControl(name, moduleObj, startJoint):
    globalCtrlObj = controller.Controller('{0}_global_ctrl'.format(name), shape='cube', scale=2.0, color='yellow')
    globalCtrlObj.createGroups()
    globalCtrlObj.matchTo(startJoint, position=True, orientation=True)

    pm.parent(moduleObj.topGrp, globalCtrlObj.transform)

