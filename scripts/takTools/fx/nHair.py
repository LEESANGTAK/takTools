from collections import OrderedDict
import random

import maya.cmds as cmds
import maya.mel as mel

from ..common import tak_lib
from ..modeling import tak_cleanUpModel
from ..animation import hairChainBaker
from ..fx import nHair
from ..utils import xgen as xgUtil


cmds.loadPlugin('matrixNodes', quiet=True)

if __name__ == "__main__":
    # set nHair clumpScale
    hairSystemList = cmds.ls(sl=True)
    for hairSystem in hairSystemList:
        cmds.setAttr('%s.clumpWidthScale[1].clumpWidthScale_Position' % hairSystem, 1)
        cmds.setAttr('%s.clumpWidthScale[1].clumpWidthScale_FloatValue' % hairSystem, 1)

    ### Set Pin Number of Hair Constraint ###
    # get hair constraint list
    hairConsts = cmds.listRelatives(c=True, type='transform')
    pin = 0
    # print hairConstraint name and pin number
    for hConst in hairConsts:
        if 'Constraint' in hConst: continue
        print('connectHairConstraint ' + hConst, str(pin) + ';')
        pin += 1

    ### Select Hair Chain Skin Joints ###
    cmds.select(cl=True)
    cmds.select('*skirt*_Ik*_jnt', add=True)
    cmds.select('*skirt*_bakeOut?_jnt', add=True)

    # Select Hairsystem Shape #
    cmds.select('wing*_Line_hairSystemShape')

    # Set to 0 for '_ctr#_zero' group of selected hair block
    selHairBlock = cmds.ls(sl=True)[0]
    prefix = selHairBlock.split('_Block')[0]
    attrList = ['rotateX', 'rotateY', 'rotateZ']
    for i in range(1, 10, 1):
        for attr in attrList:
            try:
                cmds.setAttr('%s.%s' % ('%s_ctr%i_zero' % (prefix, i), attr), 0)
            except:
                break

    # Transfer rotate value of 'hair#_ctr#_crv' attributes to the '_zero group' for selected hair block.
    selList = cmds.ls(sl=True)
    attrList = ['rotateX', 'rotateY', 'rotateZ']
    for sel in selList:
        prefix = sel.split('_Block')[0]
        for i in range(1, 10, 1):
            for attr in attrList:
                try:
                    crvAttrVal = cmds.getAttr('%s.%s' % ('%s_ctr%i_crv' % (prefix, i), attr))
                    if crvAttrVal == 0:
                        continue
                    else:
                        zeroAttrVal = cmds.getAttr('%s.%s' % ('%s_ctr%i_zero' % (prefix, i), attr))
                        setAttrVal = zeroAttrVal + crvAttrVal
                        cmds.setAttr('%s.%s' % ('%s_ctr%i_zero' % (prefix, i), attr), setAttrVal)
                        cmds.setAttr('%s.%s' % ('%s_ctr%i_crv' % (prefix, i), attr), 0)
                except:
                    break

    ### Set to Static and Turn Off Use Nucleus Solver ###
    selLs = [x for x in cmds.ls(sl=True) if cmds.nodeType(x) == 'hairSystem']
    for sel in selLs:
        cmds.setAttr('%s.active' % sel, False)
        cmds.setAttr('%s.simulationMethod' % sel, 1)

    # Transfer translate and rotate value to parent group for moved controls'
    ctrlLs = cmds.ls(sl=True)
    attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
    for ctrl in ctrlLs:
        # Get parent group
        prntGrp = cmds.listRelatives(ctrl, p=True)[0]
        for attr in attrList:
            # Get control's attribute value
            attrVal = cmds.getAttr('%s.%s' % (ctrl, attr))

            # If control's attribute value is default value then skip
            if attrVal == 0.0:
                continue
            else:
                # Get parent group value and add control attribute value
                prntAttrVal = cmds.getAttr('%s.%s' % (prntGrp, attr))
                attrVal = prntAttrVal + attrVal
                # Set parent group value
                cmds.setAttr('%s.%s' % (prntGrp, attr), attrVal)
                # Set 0 value for control
                cmds.setAttr('%s.%s' % (ctrl, attr), 0)

    # Hair Width Scale #
    hairSysShps = cmds.ls(sl=True)
    for hairSysShp in hairSysShps:
        cmds.setAttr("%s.hairWidthScale[0].hairWidthScale_FloatValue" % hairSysShp, 200)
        cmds.setAttr("%s.hairWidthScale[1].hairWidthScale_FloatValue" % hairSysShp, 200)

    # Hairsystem HiarWidthScale #
    hairSystems = cmds.ls(sl=True)

    startHairWidth = 300
    endHairWidth = 400

    for hairSystem in hairSystems:
        cmds.setAttr(hairSystem + '.hairWidthScale[0].hairWidthScale_FloatValue', startHairWidth)
        cmds.setAttr(hairSystem + '.hairWidthScale[1].hairWidthScale_FloatValue', endHairWidth)

    # Set cv[0] head joint weights to 1.0 with falloff
    numOfCvForEdit = 3
    headJnt = 'upperHead_02_bnd_jnt'
    crvs = cmds.ls(sl=True)
    for crv in crvs:
        weights = 1.0
        for id in range(numOfCvForEdit):
            skinCluster = mel.eval('findRelatedSkinCluster "%s";' % crv)
            cmds.skinPercent(skinCluster, '%s.cv[%d]' % (crv, id),
                             transformValue=[(headJnt, weights)], prw=0)
            weights -= 0.25

    # Trim curve from root
    crvs = cmds.ls(sl=True)
    percentage = 0.5
    for crv in crvs:
        crvShape = cmds.listRelatives(crv, shapes=True, noIntermediate=True)[0]
        spans = cmds.getAttr('%s.spans' % crvShape)
        degree = cmds.getAttr('%s.degree' % crvShape)
        numCVs = spans + degree
        endCV = int(random.uniform(0, numCVs * percentage))
        cmds.delete('%s.cv[0:%d]' % (crv, endCV))

    # Select 0~1 CV for selected curves
    selCrvs = cmds.ls(sl=True)
    for crv in selCrvs:
        cmds.select('%s.cv[0]' % crv, '%s.cv[1]' % crv, '%s.cv[2]' % crv, add=True)

    # Attach Follicle to Scalp
    crvTrsfs = cmds.ls(sl=True)
    scalpMeshShape = 'hairDyn_hairBase_scalpShape'

    for crvTrsf in crvTrsfs:
        closestPointOnMesh = cmds.createNode('closestPointOnMesh')
        decMatrix = cmds.createNode('decomposeMatrix')
        cmds.connectAttr('%s.worldMesh[0]' % scalpMeshShape, '%s.inMesh' % closestPointOnMesh, f=True)
        rotatePivot = cmds.getAttr('%s.rotatePivot' % crvTrsf)[0]
        cmds.setAttr('%s.inPosition' % closestPointOnMesh, *rotatePivot)

        parmU = cmds.getAttr('%s.parameterU' % closestPointOnMesh)
        parmV = cmds.getAttr('%s.parameterV' % closestPointOnMesh)

        cmds.delete(closestPointOnMesh, decMatrix)

        # Get follicle connected to the curve transform
        worldMatrix_connections = cmds.listConnections('%s.worldMatrix[0]' % crvTrsf, s=False, d=True, type='follicle') or []
        if not worldMatrix_connections:
            continue
        fol = worldMatrix_connections[0]
        folShape = cmds.listRelatives(fol, shapes=True)[0]

        cmds.setAttr('%s.parameterU' % folShape, parmU)
        cmds.setAttr('%s.parameterV' % folShape, parmV)

        xgUtil.connectFollicleToScalp(folShape, 'hairDyn_hairBase_scalpShape')

        cmds.parent(crvTrsf, world=True)

        folTrsf = cmds.listRelatives(folShape, parent=True)[0]
        cmds.connectAttr('%s.outTranslate' % folShape, '%s.translate' % folTrsf, f=True)
        cmds.connectAttr('%s.outRotate' % folShape, '%s.rotate' % folTrsf, f=True)

        cmds.parent(crvTrsf, folTrsf)

    # Copy hair mesh skin to hair curves
    from takTools.common import tak_misc
    scalpMesh = 'lod02_hair_base'
    sels = cmds.ls(sl=True)
    mesh = [sel for sel in sels if cmds.listRelatives(sel, shapes=True, type='mesh', noIntermediate=True)]
    crvs = [sel for sel in sels if cmds.listRelatives(sel, shapes=True, type='nurbsCurve', noIntermediate=True)]
    cmds.select(mesh + crvs, r=True)
    tak_misc.addInfCopySkin()

    for crv in crvs:
        cmds.select(scalpMesh, '%s.cv[0]' % crv, r=True)
        tak_misc.addInfCopySkin()
    cmds.select(mesh + crvs, r=True)
    cmds.hide()


def addCollider(solver, mesh):
    """
    Args:
        solver (str): Nucleus solver node name
        mesh (str): Mesh transform name to use as collider
    """
    meshParent = cmds.listRelatives(mesh, parent=True)
    meshParentName = meshParent[0] if meshParent else mesh
    colliderGeoName = solver + '_' + meshParentName + '_collider'
    colliderGeo = cmds.duplicate(mesh, n=colliderGeoName)[0]
    cmds.select(colliderGeo, r=True)
    tak_cleanUpModel.allInOne()

    nRgdShpName = mel.eval('makeCollideNCloth;')[0]
    cmds.setAttr('%s.thickness' % nRgdShpName, 0.1)
    cmds.setAttr('%s.pushOutRadius' % nRgdShpName, 0.1)
    nRgdParent = cmds.listRelatives(nRgdShpName, parent=True)[0]
    rigidTrsf = cmds.rename(nRgdParent, colliderGeo + '_nRigid')
    cmds.select(rigidTrsf, r=True)
    mel.eval('assignNSolver "%s";' % solver)

    tak_lib.copySkin(mesh, colliderGeo)
    cmds.parent(colliderGeo, world=True)


def setHairChainDefaultValue():
    hairChainBlockGrps = cmds.ls(sl=True)
    for grp in hairChainBlockGrps:
        hairChainName = grp.rsplit('_Block_GRP')[0]

        # Set nucleus attributes.
        nucName = hairChainName + '_nucleus'
        cmds.setAttr('%s.spaceScale' % nucName, 1)

        # Set endCtr attributes.
        cmds.select('%s*_ctrEnd_crv' % hairChainName, r=True)
        endCtrLs = cmds.ls(sl=True, type='transform')
        for endCtr in endCtrLs:
            cmds.setAttr('%s.waveSize' % endCtr, 0.25)
            cmds.setAttr('%s.Damp' % endCtr, 0.1)
            cmds.setAttr('%s.Friction' % endCtr, 0.1)
            cmds.setAttr('%s.startCurveAttract' % endCtr, 0.25)
            cmds.setAttr('%s.bendResistance' % endCtr, 5)

            # Set hair system attributes.
            hairSysName = endCtr.rsplit('_ctrEnd_crv')[0] + '_hairSystemShape'
            cmds.setAttr('%s.stretchResistance' % hairSysName, 200)
            cmds.setAttr('%s.compressionResistance' % hairSysName, 200)
            cmds.setAttr("%s.hairWidthScale[0].hairWidthScale_FloatValue" % hairSysName, 200)
            cmds.setAttr("%s.hairWidthScale[1].hairWidthScale_FloatValue" % hairSysName, 200)

            # Set sine deformer attributes.
            ikCrvName = endCtr.rsplit('_ctrEnd_crv')[0] + '_splineIKCurveShape'
            sine = cmds.listConnections(ikCrvName, s=True, d=False, type='nonLinear')[0]
            cmds.setAttr('%s.wavelength' % sine, 3)


def addConstraintOnOffAttr(hairChainCtrl, suffix):
    prefix = hairChainCtrl.replace(suffix, '')
    constGrps = cmds.ls('%s_*_const' % prefix)
    constraints = []
    for constGrp in constGrps:
        const = cmds.listConnections('%s.parentInverseMatrix' % constGrp,
                                     s=False, type='constraint') or []
        constraints.extend(const)
    if constraints:
        if not cmds.attributeQuery('Constraint', node=hairChainCtrl, exists=True):
            cmds.addAttr(hairChainCtrl, at='bool', keyable=True, dv=1, ln='Constraint')
    for const in constraints:
        weightAliases = cmds.listAttr('%s.weight' % const, multi=True) or []
        for weight in weightAliases:
            cmds.connectAttr('%s.Constraint' % hairChainCtrl,
                             '%s.%s' % (const, weight), f=True)


def jhHairChainDynSolverSetup(solver):
    attrsToBreak = ['gravity', 'timeScale']
    solverCtrls = cmds.listConnections('%s.startFrame' % solver,
                                       destination=False, type='transform') or []
    solverCtrl = solverCtrls[0]
    for attr in attrsToBreak:
        srcPlug = cmds.listConnections('%s.%s' % (solverCtrl, attr), s=True, d=False, plugs=True)
        if srcPlug:
            cmds.disconnectAttr(srcPlug[0], '%s.%s' % (solverCtrl, attr))
        cmds.deleteAttr('%s.%s' % (solverCtrl, attr))
    cmds.connectAttr('%s.dynamicOn' % solverCtrl, '%s.enable' % solver, f=True)
    cmds.setAttr('%s.gravity' % solver, 9.8)
    cmds.setAttr('%s.timeScale' % solver, 1)
    cmds.setAttr('%s.spaceScale' % solver, 0.05)


def rebuildJhHairChainDynamic(solver, mainCtrl, globalScaleCtrl):
    hairSystems = []

    prefix = mainCtrl.split('_main_ctl')[0]
    oldHairSystemList = cmds.listRelatives(
        '{prefix}_outputCurve'.format(prefix=prefix),
        ad=True, type='hairSystem', shapes=True
    ) or []
    oldHairSystem = oldHairSystemList[0]
    ikCrv = hairChainBaker.getSplineIkCurve(oldHairSystem)
    ikJnts = sorted(hairChainBaker.getJoints(ikCrv))
    bakeCtrls = hairChainBaker.getControls(ikCrv)

    # Remove old dynamic rig
    cmds.delete('{prefix}_folicle'.format(prefix=prefix),
                '{prefix}_outputCurve'.format(prefix=prefix))
    ikCrv = prefix  # ikCrv name = prefix
    ikCrvShape = cmds.listRelatives(ikCrv, shapes=True)
    blendShapeInputs = cmds.listConnections(
        ikCrvShape[0] if ikCrvShape else ikCrv,
        destination=False, type='blendShape', shapes=True
    ) or []
    if blendShapeInputs:
        cmds.delete(blendShapeInputs)

    # Clean up inCrv
    inCrvTransform = cmds.duplicate(ikCrv, n='{prefix}_inCrv'.format(prefix=prefix))[0]
    tak_lib.deleteIntermediateObject(inCrvTransform)
    cmds.delete(inCrvTransform, ch=True)

    # Create dynamic curve
    cmds.select(inCrvTransform, r=True)
    mel.eval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0"};')

    # Get nodes to dynamic
    inCrvShape = cmds.listRelatives(inCrvTransform, shapes=True, noIntermediate=True)[0]
    follicleList = cmds.listConnections('%s.local' % inCrvShape, type='follicle', shapes=True) or []
    follicle = follicleList[0]
    hairSystemList2 = cmds.listConnections('%s.currentPosition' % follicle,
                                           type='hairSystem', shapes=True) or []
    hairSystem = hairSystemList2[0]
    hairSystems.append(hairSystem)
    outCrvList = cmds.listConnections('%s.outCurve' % follicle, type='nurbsCurve', shapes=True) or []
    outCrv = outCrvList[0]

    # Match follicle transform to main control transform
    cmds.setAttr('%s.pointLock' % follicle, 1)
    follicleTransform = cmds.listRelatives(follicle, parent=True)[0]
    cmds.parent(inCrvTransform, world=True)
    cmds.delete(cmds.parentConstraint(mainCtrl, follicleTransform, mo=False))
    cmds.parent(inCrvTransform, follicleTransform)

    bakeLocSpaces = []
    for ctrl in bakeCtrls:
        loc = cmds.spaceLocator(n='{ctrl}_bake_loc'.format(ctrl=ctrl))[0]
        locSpace = cmds.createNode('transform', n='{loc}_spc'.format(loc=loc))
        bakeLocSpaces.append(locSpace)
        cmds.delete(cmds.parentConstraint(ctrl, loc, mo=False))
        cmds.delete(cmds.parentConstraint(ctrl, locSpace, mo=False))

        # Attach bake locator to output curve
        dcpMatrix = cmds.createNode('decomposeMatrix', n='{ctrl}_dcpMatrix'.format(ctrl=ctrl))
        nearPointOnCrv = cmds.createNode('nearestPointOnCurve', n='{ctrl}_nearPntOnCrv'.format(ctrl=ctrl))
        pntOnCrvInfo = cmds.createNode('pointOnCurveInfo', n='{ctrl}_pntOnCrvInfo'.format(ctrl=ctrl))
        cmds.connectAttr('%s.worldMatrix[0]' % locSpace, '%s.inputMatrix' % dcpMatrix, f=True)
        cmds.connectAttr('%s.outputTranslate' % dcpMatrix, '%s.inPosition' % nearPointOnCrv, f=True)
        cmds.connectAttr('%s.worldSpace[0]' % outCrv, '%s.inputCurve' % nearPointOnCrv, f=True)
        cmds.connectAttr('%s.parameter' % nearPointOnCrv, '%s.parameter' % pntOnCrvInfo, f=True)
        cmds.connectAttr('%s.worldSpace[0]' % outCrv, '%s.inputCurve' % pntOnCrvInfo, f=True)
        # Disconnect dcpMatrix from locSpace (was temporary)
        cmds.disconnectAttr('%s.worldMatrix[0]' % locSpace, '%s.inputMatrix' % dcpMatrix)
        cmds.disconnectAttr('%s.parameter' % nearPointOnCrv, '%s.parameter' % pntOnCrvInfo)
        cmds.connectAttr('%s.result.position' % pntOnCrvInfo, '%s.translate' % locSpace, f=True)
        cmds.delete(dcpMatrix, nearPointOnCrv)
        cmds.parent(loc, locSpace)
    bakeLocsGrp = cmds.group(bakeLocSpaces, n='{prefix}_bake_loc_grp'.format(prefix=prefix))

    outCrvTransform = cmds.listRelatives(outCrv, parent=True)[0]
    blendShape = cmds.blendShape(outCrvTransform, ikCrv)[0]
    cmds.setAttr('%s.%s' % (blendShape, outCrvTransform), 1)
    cmds.connectAttr('%s.dynamicOnOff' % mainCtrl, '%s.envelope' % blendShape, f=True)

    # Clean up outliner
    folTrsf = cmds.listRelatives(follicle, parent=True)[0]
    hairSysTrsf = cmds.listRelatives(hairSystem, parent=True)[0]
    outCrvParent2 = cmds.listRelatives(cmds.listRelatives(outCrvTransform, parent=True)[0], parent=True)[0]
    dynRigGrp = cmds.group(folTrsf, hairSysTrsf, outCrvParent2, bakeLocsGrp,
                            n='{prefix}_dyn_rig_grp'.format(prefix=prefix))
    ikCrvParent2 = cmds.listRelatives(cmds.listRelatives(ikCrv, parent=True)[0], parent=True)[0]
    cmds.parent(dynRigGrp, ikCrvParent2)
    cmds.setAttr('%s.visibility' % dynRigGrp, False)

    # Fix double transform
    cmds.setAttr('%s.inheritsTransform' % outCrvTransform, False)
    cmds.setAttr('%s.inheritsTransform' % hairSysTrsf, False)
    cmds.setAttr('%s.inheritsTransform' % bakeLocsGrp, False)

    # Solve global scale issue
    for bakeLocSpace in bakeLocSpaces:
        cmds.connectAttr('%s.scale' % globalScaleCtrl, '%s.scale' % bakeLocSpace, f=True)

    # Add dynamic attributes to main controller
    cmds.addAttr(mainCtrl, at='enum', en='---------------:', ln='dynamicAttrs')
    cmds.setAttr('%s.dynamicAttrs' % mainCtrl, channelBox=True, lock=True)
    dynAttrsInfo = OrderedDict(
        [('stretchResistance', 100),
         ('compressionResistance', 100),
         ('bendResistance', 1),
         ('startCurveAttract', 0.0),
         ('mass', 1.0),
         ('damp', 0.25),
         ('drag', 0.1)])
    for dynAttr, defaultVal in dynAttrsInfo.items():
        cmds.addAttr(mainCtrl, attributeType='double', keyable=True, defaultValue=defaultVal, ln=dynAttr)
        cmds.connectAttr('%s.%s' % (mainCtrl, dynAttr), '%s.%s' % (hairSystem, dynAttr), f=True)

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
    solver = cmds.createNode('nucleus', n='%s_nucleus' % name)

    cmds.connectAttr('time1.outTime', '%s.currentTime' % solver, f=True)
    cmds.connectAttr('%s.%s_startFrame' % (dynControl, name), '%s.startFrame' % solver, f=True)

    hairSystems = cmds.ls('%s*' % name, type='hairSystem')
    for hairSystem in hairSystems:
        cmds.connectAttr('%s.startFrame' % solver, '%s.startFrame' % hairSystem, f=True)
        index = tak_lib.findMultiAttributeEmptyIndex(solver, 'outputObjects')
        cmds.connectAttr('%s.outputObjects[%d]' % (solver, index), '%s.nextState' % hairSystem, f=True)

        index = tak_lib.findMultiAttributeEmptyIndex(solver, 'inputActive')
        cmds.connectAttr('%s.currentState' % hairSystem, '%s.inputActive[%d]' % (solver, index))

        index = tak_lib.findMultiAttributeEmptyIndex(solver, 'inputActiveStart')
        cmds.connectAttr('%s.startState' % hairSystem, '%s.inputActiveStart[%d]' % (solver, index))

    nRigids = cmds.ls('%s*' % name, type='nRigid')
    if nRigids:
        for nRigid in nRigids:
            cmds.connectAttr('%s.startFrame' % solver, '%s.startFrame' % nRigid, f=True)

            index = tak_lib.findMultiAttributeEmptyIndex(solver, 'inputPassive')
            cmds.connectAttr('%s.currentState' % nRigid, '%s.inputPassive[%d]' % (solver, index))

            index = tak_lib.findMultiAttributeEmptyIndex(solver, 'inputPassiveStart')
            cmds.connectAttr('%s.startState' % nRigid, '%s.inputPassiveStart[%d]' % (solver, index))

    cmds.parent(solver, '%s_GRP' % solver)


def recoverHairChainDyn(name):
    """
    When import hairchain if there is no attributes for dynamic on dynamic curve, create attributes and connects

    Parameters:
        name(str): Prefix of hairChain
    """
    dynCtrl = 'dyn_ctr_crv'

    cmds.addAttr(dynCtrl, niceName='[ {0} ]'.format(name), type='enum',
                 enumName='---------------', ln='_{0}_'.format(name))
    cmds.setAttr('%s._%s_' % (dynCtrl, name), channelBox=True)
    cmds.addAttr(dynCtrl, type='enum', enumName='off:classicHair:nHair', ln='{0}_dynamic'.format(name))
    cmds.setAttr('%s.%s_dynamic' % (dynCtrl, name), channelBox=True)
    cmds.addAttr(dynCtrl, keyable=True, at='long', ln='{0}_startFrame'.format(name))

    nucleus = '{0}_nucleus'.format(name)
    endCtrls = cmds.ls('{}*_ctrEnd_crv'.format(name))
    dynamicOffCondition = '{0}_dynamicOff_condition'.format(name)
    nHairCondition = '{0}_nHair_condition'.format(name)

    cmds.connectAttr('%s.%s_startFrame' % (dynCtrl, name), '%s.startFrame' % nucleus, f=True)
    cmds.connectAttr('%s.%s_dynamic' % (dynCtrl, name), '%s.firstTerm' % dynamicOffCondition, f=True)
    cmds.connectAttr('%s.%s_dynamic' % (dynCtrl, name), '%s.firstTerm' % nHairCondition, f=True)

    for endCtrl in endCtrls:
        cmds.connectAttr('%s.%s_dynamic' % (dynCtrl, name), '%s.dynamicType' % endCtrl, f=True)
        cmds.connectAttr('%s.%s_startFrame' % (dynCtrl, name), '%s.startFrame' % endCtrl, f=True)


def assignNewSolver(solver=None, hairSystems=None):
    """
    Assign new nucleus solver to the selected hair systems or given hairSystem list

    Parameters:
        solver: Nucleus node name or None to create new
        hairSystems (list): Hair system list (names or shapes)

    Examples:
        hairSystems = cmds.ls(sl=True)
        assignNewSolver(solver=None, hairSystems=hairSystems)
    """
    if not hairSystems:
        hairSystems = cmds.ls(sl=True)

    # Prepare solver
    if not solver:
        solver = cmds.createNode('nucleus')
    cmds.connectAttr('time1.outTime', '%s.currentTime' % solver, f=True)

    for hairSystem in hairSystems:
        # Resolve to shape if transform
        if cmds.nodeType(hairSystem) == 'transform':
            shapes = cmds.listRelatives(hairSystem, shapes=True)
            if shapes:
                hairSystem = shapes[0]

        cmds.connectAttr('%s.startFrame' % solver, '%s.startFrame' % hairSystem, f=True)

        index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='outputObjects')
        cmds.connectAttr('%s.outputObjects[%d]' % (solver, index),
                         '%s.nextState' % hairSystem, f=True)

        index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActive')
        srcConns = cmds.listConnections('%s.currentState' % hairSystem, s=True, d=False, plugs=True)
        if srcConns:
            cmds.disconnectAttr(srcConns[0], '%s.currentState' % hairSystem)
        cmds.connectAttr('%s.currentState' % hairSystem,
                         '%s.inputActive[%d]' % (solver, index))

        index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActiveStart')
        srcConns = cmds.listConnections('%s.startState' % hairSystem, s=True, d=False, plugs=True)
        if srcConns:
            cmds.disconnectAttr(srcConns[0], '%s.startState' % hairSystem)
        cmds.connectAttr('%s.startState' % hairSystem,
                         '%s.inputActiveStart[%d]' % (solver, index))


def changeHairSystem(sourceHairSystem, targetHairSystem):
    """
    Reassign source hairsystem to the target hairsystem

    Parameters:
        sourceHairSystem (str): Source hairsystem node name
        targetHairSystem (str): Target hairsystem node name
    """
    if cmds.nodeType(sourceHairSystem) != 'hairSystem' or cmds.nodeType(targetHairSystem) != 'hairSystem':
        cmds.error('"hairSystem" node type needed as input')

    availableOutputHairId = tak_lib.findMultiAttributeEmptyIndex(str(targetHairSystem), 'outputHair')

    follicles = cmds.listConnections(sourceHairSystem, type='follicle', s=False) or []
    for follicle in follicles:
        cmds.connectAttr('%s.outputHair[%d]' % (targetHairSystem, availableOutputHairId),
                         '%s.currentPosition' % follicle, f=True)
        cmds.connectAttr('%s.outHair' % follicle,
                         '%s.inputHair[%d]' % (targetHairSystem, availableOutputHairId), f=True)
        availableOutputHairId += 1
