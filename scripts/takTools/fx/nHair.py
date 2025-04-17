from collections import OrderedDict
import random

import maya.cmds as cmds
import pymel.core as pm

from ..common import tak_lib
from ..modeling import tak_cleanUpModel
from ..animation import hairChainBaker
from ..fx import nHair
from ..utils import xgen as xgUtil


pm.loadPlugin('matrixNodes')

if __name__ == "__main__":
    # set nHair clumpScale
    hairSystemList = cmds.ls(sl = True)
    for hairSystem in hairSystemList:
        cmds.setAttr('%s.clumpWidthScale[1].clumpWidthScale_Position' %hairSystem, 1)
        cmds.setAttr('%s.clumpWidthScale[1].clumpWidthScale_FloatValue' %hairSystem, 1)

    ### Set Pin Number of Hair Constraint ###
    # get hair constraint list
    hairConsts = cmds.listRelatives(c = True, type = 'transform')
    pin = 0
    # print hairConstraint name and pin number
    for hConst in hairConsts:
            if 'Constraint' in hConst: continue
            print('connectHairConstraint ' + hConst, str(pin) + ';')
            pin += 1

    ### Select Hair Chain Skin Joints ###
    cmds.select(cl = True)
    cmds.select('*skirt*_Ik*_jnt', add = True)
    cmds.select('*skirt*_bakeOut?_jnt', add = True)

    # Select Hairsystem Shape #
    cmds.select('wing*_Line_hairSystemShape')

    # Set to 0 for '_ctr#_zero' group of selected hair block
    selHairBlock = cmds.ls(sl = True)[0]
    prefix = selHairBlock.split('_Block')[0]
    attrList = ['rotateX', 'rotateY', 'rotateZ']
    for i in range(1, 10, 1):
        for attr in attrList:
            try:
                cmds.setAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr), 0)
            except:
                break

    # Transfer rotate value of 'hair#_ctr#_crv' attributes to the '_zero group' for selected hair block.
    selList = cmds.ls(sl = True)
    attrList = ['rotateX', 'rotateY', 'rotateZ']
    for sel in selList:
        prefix = sel.split('_Block')[0]
        for i in range(1, 10, 1):
            for attr in attrList:
                try:
                    crvAttrVal = cmds.getAttr('%s.%s' %('%s_ctr%i_crv' %(prefix, i), attr))
                    if crvAttrVal == 0:
                        continue
                    else:
                        zeroAttrVal = cmds.getAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr))
                        setAttrVal = zeroAttrVal + crvAttrVal
                        cmds.setAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr), setAttrVal)
                        cmds.setAttr('%s.%s' %('%s_ctr%i_crv' %(prefix, i), attr), 0)
                except:
                    break

    ### Set to Static and Turn Off Use Nucleus Solver ###
    selLs = [x for x in cmds.ls(sl = True) if cmds.nodeType(x) == 'hairSystem']
    for sel in selLs:
        cmds.setAttr('%s.active' %sel, False)
        cmds.setAttr('%s.simulationMethod' %sel, 1)

    # Transfer translate and rotate value to parent group for moved controls'
    ctrlLs = cmds.ls(sl = True)
    attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    for ctrl in ctrlLs:
        # Get parent gorup
        prntGrp = cmds.listRelatives(ctrl, p = True)[0]
        for attr in attrList:
            # Get control's attribute value
            attrVal = cmds.getAttr('%s.%s' %(ctrl, attr))

            # If control's attribute value is default value then skip
            if attrVal == 0.0:
                continue
            else:
                # Get parent group value and add control attribute value
                prntAttrVal = cmds.getAttr('%s.%s' %(prntGrp, attr))
                attrVal = prntAttrVal + attrVal
                # Set parent group value
                cmds.setAttr('%s.%s' %(prntGrp, attr), attrVal)
                # Set 0 value for control
                cmds.setAttr('%s.%s' %(ctrl, attr), 0)

    # Hair Width Scale #
    hairSysShps = cmds.ls(sl = True)
    for hairSysShp in hairSysShps:
        cmds.setAttr("%s.hairWidthScale[0].hairWidthScale_FloatValue" %hairSysShp, 200)
        cmds.setAttr("%s.hairWidthScale[1].hairWidthScale_FloatValue" %hairSysShp, 200)

    # Hairsystem HiarWidthScale #
    hairSystems = cmds.ls(sl = True)

    startHairWidth = 300
    endHairWidth = 400

    for hairSystem in hairSystems:
        cmds.setAttr(hairSystem + '.hairWidthScale[0].hairWidthScale_FloatValue', startHairWidth)
        cmds.setAttr(hairSystem + '.hairWidthScale[1].hairWidthScale_FloatValue', endHairWidth)

    # Set cv[0] head joint weights to 1.0 with falloff
    import pymel.core as pm
    numOfCvForEdit = 3
    headJnt = 'upperHead_02_bnd_jnt'
    crvs = pm.selected()
    for crv in crvs:
        weights = 1.0
        for id in range(numOfCvForEdit):
            skinCluster = pm.mel.eval('findRelatedSkinCluster "%s";' % crv.name())
            pm.skinPercent(skinCluster, crv.cv[id], transformValue=[(headJnt, weights)], prw=0)
            weights -= 0.25

    # Trim curve from root
    crvs = pm.selected()
    percentage = 0.5
    for crv in crvs:
        numCVs = crv.getShape().numCVs()
        endCV = int(random.uniform(0, numCVs*percentage))
        pm.delete(crv.getShape().cv[0:endCV])


    # Select 0~1 CV for selected curves
    selCrvs = pm.selected()
    for crv in selCrvs:
        pm.select(crv.cv[0], crv.cv[1], crv.cv[2], add=True)


    # Attach Follicle to Scalp
    crvTrsfs = pm.selected()
    scalpMesh = pm.PyNode('hairDyn_hairBase_scalpShape')

    for crvTrsf in crvTrsfs:
        closestPointOnMesh = pm.createNode('closestPointOnMesh')
        decMatrix = pm.createNode('decomposeMatrix')
        scalpMesh.worldMesh[0] >> closestPointOnMesh.inMesh
        # crvTrsf.worldMatrix[0] >> decMatrix.inputMatrix
        # decMatrix.outputTranslate >> closestPointOnMesh.inPosition
        crvTrsf.rotatePivot >> closestPointOnMesh.inPosition

        parmU = closestPointOnMesh.parameterU.get()
        parmV = closestPointOnMesh.parameterV.get()

        pm.delete(closestPointOnMesh, decMatrix)

        fol = crvTrsf.worldMatrix[0].connections()[0].getShape()
        fol.parameterU.set(parmU)
        fol.parameterV.set(parmV)

        xgUtil.connectFollicleToScalp(fol.name(), 'hairDyn_hairBase_scalpShape')

        pm.parent(crvTrsf, w=True)

        folTrsf = fol.getTransform()
        fol.outTranslate >> folTrsf.translate
        fol.outRotate >> folTrsf.rotate

        pm.parent(crvTrsf, folTrsf)


    # Copy hair mesh skin to hair curves
    from takTools.common import tak_misc
    scalpMesh = pm.PyNode('lod02_hair_base')
    sels = pm.selected()
    mesh = [sel for sel in sels if isinstance(sel.getShape(), pm.nodetypes.Mesh)]
    crvs = [sel for sel in sels if isinstance(sel.getShape(), pm.nodetypes.NurbsCurve)]
    pm.select(mesh, crvs, r=True)
    tak_misc.addInfCopySkin()

    for crv in crvs:
        pm.select(scalpMesh, crv.cv[0], r=True)
        tak_misc.addInfCopySkin()
    pm.select(mesh, crvs, r=True)
    pm.hide()


def addCollider(solver, mesh):
    colliderGeo = mesh.duplicate(n=solver.name()+'_'+mesh.getParent().name()+'_collider')[0]
    pm.select(colliderGeo, r=True)
    tak_cleanUpModel.allInOne()

    nRgdShp = pm.PyNode(pm.mel.eval('makeCollideNCloth;')[0])
    nRgdShp.thickness.set(0.1)
    nRgdShp.pushOutRadius.set(0.1)
    rigidTrsf = nRgdShp.getParent().rename(colliderGeo.name()+'_nRigid')
    pm.select(rigidTrsf, r=True)
    pm.mel.eval('assignNSolver "%s";' % solver)

    tak_lib.copySkin(mesh, colliderGeo)
    colliderGeo.setParent(world=True)


def setHairChainDefaultValue():
    hairChainBlockGrps = cmds.ls(sl = True)
    for grp in hairChainBlockGrps:
        hairChainName = grp.rsplit('_Block_GRP')[0]

        # Set nucleus attributes.
        nucName = hairChainName + '_nucleus'
        cmds.setAttr('%s.spaceScale' %nucName, 1)

        # Set endCtr attributes.
        cmds.select('%s*_ctrEnd_crv' %hairChainName, r = True)
        endCtrLs = cmds.ls(sl = True, type = 'transform')
        for endCtr in endCtrLs:
            cmds.setAttr('%s.waveSize' %endCtr, 0.25)
            cmds.setAttr('%s.Damp' %endCtr, 0.1)
            cmds.setAttr('%s.Friction' %endCtr, 0.1)
            cmds.setAttr('%s.startCurveAttract' %endCtr, 0.25)
            cmds.setAttr('%s.bendResistance' %endCtr, 5)

            # Set hair system attributes.
            hairSysName = endCtr.rsplit('_ctrEnd_crv')[0] + '_hairSystemShape'
            cmds.setAttr('%s.stretchResistance' %hairSysName, 200)
            cmds.setAttr('%s.compressionResistance' %hairSysName, 200)
            cmds.setAttr("%s.hairWidthScale[0].hairWidthScale_FloatValue" %hairSysName, 200)
            cmds.setAttr("%s.hairWidthScale[1].hairWidthScale_FloatValue" %hairSysName, 200)

            # Set sine deformer attributes.
            ikCrvName = endCtr.rsplit('_ctrEnd_crv')[0] + '_splineIKCurveShape'
            sine = cmds.listConnections(ikCrvName, s = True, d = False, type = 'nonLinear')[0]
            cmds.setAttr('%s.wavelength' %sine, 3)


def addConstraintOnOffAttr(hairChainCtrl, suffix):
    prefix = hairChainCtrl.replace(suffix, '')
    constGrps = pm.ls('%s_*_const' % (prefix))
    constraints = []
    for constGrp in constGrps:
        const = constGrp.parentInverseMatrix.connections(s=False, type='constraint')
        constraints.extend(const)
    if constraints:
        if not hairChainCtrl.hasAttr('Constraint'):
            hairChainCtrl.addAttr('Constraint', at='bool', keyable=True, dv=1)
    for const in constraints:
        [hairChainCtrl.Constraint >> weight for weight in const.getWeightAliasList()]


def jhHairChainDynSolverSetup(solver):
    attrsToBreak = ['gravity', 'timeScale']
    solverCtrl = solver.startFrame.connections(destination=False, type='transform')[0]
    for attr in attrsToBreak:
        solverCtrl.attr(attr) // solver.attr(attr)
        solverCtrl.attr(attr).delete()
    solverCtrl.dynamicOn >> solver.enable
    solver.gravity.set(9.8)
    solver.timeScale.set(1)
    solver.spaceScale.set(0.05)


def rebuildJhHairChainDynamic(solver, mainCtrl, globalScaleCtrl):
    hairSystems = []

    prefix = mainCtrl.split('_main_ctl')[0]
    oldHairSystem = pm.listRelatives('{prefix}_outputCurve'.format(prefix=prefix), ad=True, type='hairSystem', shapes=True)[0]
    ikCrv = hairChainBaker.getSplineIkCurve(oldHairSystem)
    ikJnts = sorted(hairChainBaker.getJoints(ikCrv))
    bakeCtrls = hairChainBaker.getControls(ikCrv)

    # Remove old dynamic rig
    pm.delete('{prefix}_folicle'.format(prefix=prefix), '{prefix}_outputCurve'.format(prefix=prefix))
    ikCrv = pm.PyNode(prefix)
    pm.delete(ikCrv.getShape().connections(destination=False, type='blendShape', shapes=True))

    # Clean up inCrv
    inCrvTransform = ikCrv.duplicate(n='{prefix}_inCrv'.format(prefix=prefix))[0]
    tak_lib.deleteIntermediateObject(inCrvTransform)
    pm.delete(inCrvTransform, ch=True)
    # tak_lib.setDefaultTransform(inCrvTransform)

    # Create dynamic curve
    pm.select(inCrvTransform, r=True)
    pm.mel.eval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0"};')

    # Get nodes to dynamic
    follicle = inCrvTransform.getShape().local.connections(type='follicle', shapes=True)[0]
    hairSystem = follicle.currentPosition.connections(type='hairSystem', shapes=True)[0]
    hairSystems.append(hairSystem)
    outCrv = follicle.outCurve.connections(type='nurbsCurve', shapes=True)[0]

    # Match follicle transform to main control transform
    follicle.pointLock.set(1)
    inCrvTransform.setParent(world=True)
    pm.delete(pm.parentConstraint(mainCtrl, follicle.getParent(), mo=False))
    follicle.getParent() | inCrvTransform

    bakeLocSpaces = []
    for ctrl in bakeCtrls:
        loc = pm.spaceLocator(n='{ctrl}_bake_loc'.format(ctrl=ctrl.name()))
        locSpace = pm.createNode('transform', n='{loc}_spc'.format(loc=loc.name()))
        bakeLocSpaces.append(locSpace)
        pm.delete(pm.parentConstraint(ctrl, loc, mo=False))
        pm.delete(pm.parentConstraint(ctrl, locSpace, mo=False))

        # Attach bake locator to output curve
        dcpMatrix = pm.createNode('decomposeMatrix', n='{ctrl}_dcpMatrix'.format(ctrl=ctrl.name()))
        nearPointOnCrv = pm.createNode('nearestPointOnCurve', n='{ctrl}_nearPntOnCrv'.format(ctrl=ctrl.name()))
        pntOnCrvInfo = pm.createNode('pointOnCurveInfo', n='{ctrl}_pntOnCrvInfo'.format(ctrl=ctrl.name()))
        locSpace.worldMatrix[0] >> dcpMatrix.inputMatrix
        dcpMatrix.outputTranslate >> nearPointOnCrv.inPosition
        outCrv.worldSpace[0] >> nearPointOnCrv.inputCurve
        nearPointOnCrv.parameter >> pntOnCrvInfo.parameter
        outCrv.worldSpace[0] >> pntOnCrvInfo.inputCurve
        locSpace.worldMatrix[0] // dcpMatrix.inputMatrix
        nearPointOnCrv.parameter // pntOnCrvInfo.parameter
        pntOnCrvInfo.result.position >> locSpace.translate
        pm.delete(dcpMatrix, nearPointOnCrv)
        locSpace | loc
    bakeLocsGrp = pm.group(bakeLocSpaces, n='{prefix}_bake_loc_grp'.format(prefix=prefix))

    blendShape = pm.blendShape(outCrv, ikCrv)[0]
    blendShape.attr(outCrv.name()).set(1)
    mainCtrl.dynamicOnOff >> blendShape.envelope

    # Clean up outliner
    dynRigGrp = pm.group(follicle.getParent(), hairSystem.getParent(), outCrv.getParent(2), bakeLocsGrp, n='{prefix}_dyn_rig_grp'.format(prefix=prefix))
    ikCrv.getParent().getParent() | dynRigGrp
    dynRigGrp.visibility.set(False)

    # Fix double transform
    outCrv.getParent().inheritsTransform.set(False)
    hairSystem.getParent().inheritsTransform.set(False)
    bakeLocsGrp.inheritsTransform.set(False)

    # Solve global scale issue
    for bakeLocSpace in bakeLocSpaces:
        globalScaleCtrl.scale >> bakeLocSpace.scale

    # Add dynamic attributes to main controller
    mainCtrl.addAttr('dynamicAttrs', at='enum', en='---------------:')
    mainCtrl.dynamicAttrs.set(channelBox = True, lock=True)
    dynAttrsInfo = OrderedDict(
        [('stretchResistance',100),
        ('compressionResistance',100),
        ('bendResistance',1),
        ('startCurveAttract',0.0),
        ('mass',1.0),
        ('damp',0.25),
        ('drag',0.1)])
    for dynAttr, defaultVal in dynAttrsInfo.items():
        mainCtrl.addAttr(dynAttr, attributeType='double', keyable=True, defaultValue=defaultVal)
        mainCtrl.attr(dynAttr) >> hairSystem.attr(dynAttr)

    nHair.assignNewSolver(solver=solver, hairSystems=hairSystems)

def assignSolverToHairChain(name, dynControl):
    """
    Rebuild broken hair chain dynamic system
    Args:
        name: Prefix of 'Block_GRP'
        dynControl: Dynamic controller

    Returns:
        None

    Examples:
        assignSolverToHairChain('coat_bottom', 'dyn_ctr_crv')
    """
    time = pm.PyNode('time1')
    solver = pm.createNode('nucleus', n='%s_nucleus' % name)
    dynControl = pm.PyNode(dynControl)

    time.outTime >> solver.currentTime
    dynControl.attr('%s_startFrame' % name) >> solver.startFrame

    hairSystems = pm.ls('%s*' % name, type='hairSystem')
    for hairSystem in hairSystems:
        solver.startFrame >> hairSystem.startFrame
        index = tak_lib.findMultiAttributeEmptyIndex(solver.name(), 'outputObjects')
        solver.outputObjects[index] >> hairSystem.nextState

        index = tak_lib.findMultiAttributeEmptyIndex(solver.name(), 'inputActive')
        hairSystem.currentState >> solver.inputActive[index]

        index = tak_lib.findMultiAttributeEmptyIndex(solver.name(), 'inputActiveStart')
        hairSystem.startState >> solver.inputActiveStart[index]

    nRigids = pm.ls('%s*' % name, type='nRigid')
    if nRigids:
        for nRigid in nRigids:
            solver.startFrame >> nRigid.startFrame

            index = tak_lib.findMultiAttributeEmptyIndex(solver.name(), 'inputPassive')
            nRigid.currentState >> solver.inputPassive[index]

            index = tak_lib.findMultiAttributeEmptyIndex(solver.name(), 'inputPassiveStart')
            nRigid.startState >> solver.inputPassiveStart[index]

    solver.setParent('%s_GRP' % solver.name())


def recoverHairChainDyn(name):
    """
    When import hairchain if there is no attributes for dynamic on dynamic curve, create attributes and connects

    Parameters:
        name(str): Prefix of hairChain
    """
    dynCtrl = pm.PyNode('dyn_ctr_crv')

    dynCtrl.addAttr('_{0}_'.format(name), niceName='[ {0} ]'.format(name), type='enum', enumName='---------------')
    dynCtrl.setAttr('_{0}_'.format(name), channelBox=True)
    dynCtrl.addAttr('{0}_dynamic'.format(name), type='enum', enumName=['off', 'classicHair', 'nHair'])
    dynCtrl.setAttr('{0}_dynamic'.format(name), channelBox=True)
    dynCtrl.addAttr('{0}_startFrame'.format(name), keyable=True, type='long')

    nucleus = pm.PyNode('{0}_nucleus'.format(name))
    endCtrls = pm.ls('{}*_ctrEnd_crv'.format(name))
    dynamicOffCondition = pm.PyNode('{0}_dynamicOff_condition'.format(name))
    nHairCondition = pm.PyNode('{0}_nHair_condition'.format(name))
    dynCtrlDynamicAttr = dynCtrl.attr('{0}_dynamic'.format(name))
    dynCtrlStartFrameAttr = dynCtrl.attr('{0}_startFrame'.format(name))

    dynCtrlStartFrameAttr >> nucleus.startFrame
    dynCtrlDynamicAttr >> dynamicOffCondition.firstTerm
    dynCtrlDynamicAttr >> nHairCondition.firstTerm

    for endCtrl in endCtrls:
        dynCtrlDynamicAttr >> endCtrl.dynamicType
        dynCtrlStartFrameAttr >> endCtrl.startFrame


def assignNewSolver(solver=None, hairSystems=None):
    """
    Assign new nucleus solver to the selected hair systems or given hairSystem list

    Parameters:
        solver: Nucleus node or nucleus node name
        hairSystems (list): Hair system list

    Examples:
        hairSystems = pm.selected()
        assignNewSolver(solver=None, hairSystems=hairSystems)
    """
    if not hairSystems:
        hairSystems = pm.ls(sl=True)

    # Prepare solver
    if not solver:
        solver = pm.createNode('nucleus')
    solver = pm.PyNode(solver)
    time1 = pm.PyNode('time1')
    time1.outTime.connect(solver.currentTime, f=True)

    for hairSystem in hairSystems:
        hairSystem = pm.PyNode(hairSystem)
        if type(hairSystem) == pm.nodetypes.Transform:
            hairSystem = hairSystem.getShape()

        solver.startFrame.connect(hairSystem.startFrame, f=True)

        index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='outputObjects')
        solver.outputObjects[index].connect(hairSystem.nextState, f=True)

        index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActive')
        hairSystem.currentState.disconnect()
        hairSystem.currentState.connect(solver.inputActive[index])

        index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActiveStart')
        hairSystem.startState.disconnect()
        hairSystem.startState.connect(solver.inputActiveStart[index])


def changeHairSystem(sourceHairSystem, targetHairSystem):
    """
    Reassign source hairsystem to the target hairsystem

    Parameters:
        sourceHairSystem(pymel.core.nodetypes.HairSystem): Source hairsystem
        targetHairSystem(pymel.core.nodetypes.HairSystem): Target hairsystem
    """

    if not isinstance(sourceHairSystem, pm.nodetypes.HairSystem) or not isinstance(targetHairSystem, pm.nodetypes.HairSystem):
        pm.error('"pymel.core.nodetypes.HairSystem" type needed as input')

    availableOutputHairId = tak_lib.findMultiAttributeEmptyIndex(str(targetHairSystem), 'outputHair')

    follicles = sourceHairSystem.listConnections(type='follicle', s=False)
    for follicle in follicles:
        targetHairSystem.outputHair[availableOutputHairId] >> follicle.currentPosition
        follicle.outHair >> targetHairSystem.inputHair[availableOutputHairId]
        availableOutputHairId += 1
