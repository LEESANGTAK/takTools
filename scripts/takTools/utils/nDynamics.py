import maya.cmds as cmds
import maya.mel as mel

from collections import OrderedDict

from . import globalUtil
from ..common import tak_lib


def addDynamicAttrs(control, solver, dynamicNodes, dynamicType):
    """Adds dynamic attributes to the controller.

    Args:
        control (str): Control name to add dynamic attributes.
        solver (str): Nuclues solver name.
        dynamicNodes (list): nCloth or hairSystem Nodes.
        dynamicType (str): Dynamic type. ['cloth', 'hair']
    """
    solverAttrsInfo = OrderedDict([
        ('dyn', 'enum'),
        ('enable', 'bool'),
        ('startFrame', 'double'),
        ('subSteps', 'long'),
    ])
    clothDynNodeAttrsInfo = OrderedDict([
        ('dynNode', 'enum'),
        ('isDynamic', 'bool'),
        ('selfCollide', 'double'),
        ('stretchResistance', 'double'),
        ('compressionResistance', 'double'),
        ('bendResistance', 'double'),
        ('inputMeshAttract', 'double'),
        ('pointMass', 'double'),
        ('drag', 'double'),
        ('damp', 'double'),
    ])
    hairDynNodeAttrsInfo = OrderedDict([
        ('dynNode', 'enum'),
        ('enable', 'bool'),
        ('stretchResistance', 'double'),
        ('compressionResistance', 'double'),
        ('bendResistance', 'double'),
        ('startCurveAttract', 'double'),
        ('mass', 'double'),
        ('drag', 'double'),
        ('damp', 'double'),
    ])

    dynCtrl = control
    solver = solver
    dynNodes = []
    for node in dynamicNodes:
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True)
        if shapes:
            dynNodes.append(shapes[0])
        else:
            dynNodes.append(node)

    for attrName in solverAttrsInfo.keys():
        attrLongName = solver + '_' + attrName
        # Add attribute.
        if cmds.attributeQuery(attrLongName, node=dynCtrl, exists=True):
            continue
        else:
            attrType = solverAttrsInfo[attrName]
            if attrType == 'enum':
                cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, en='--------------------')
                cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), channelBox=True)
            elif attrType == 'bool':
                cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), 0)
            elif attrType == 'long':
                cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), 0)
            elif attrType == 'double':
                cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), 0)

        # Connect attribute.
        if cmds.attributeQuery(attrName, node=solver, exists=True):
            val = cmds.getAttr('%s.%s' % (solver, attrName))
            cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), val)
            cmds.connectAttr('%s.%s' % (dynCtrl, attrLongName), '%s.%s' % (solver, attrName), f=True)

    for dynNode in dynNodes:
        # Get transform name for use as label
        dynNodeTransform = cmds.listRelatives(dynNode, parent=True, fullPath=False)
        dynNodeTransformName = dynNodeTransform[0] if dynNodeTransform else dynNode

        if dynamicType == 'cloth':
            for attrName in clothDynNodeAttrsInfo.keys():
                attrLongName = dynNodeTransformName + '_' + attrName
                # Add attribute.
                if cmds.attributeQuery(attrLongName, node=dynCtrl, exists=True):
                    continue
                else:
                    attrType = clothDynNodeAttrsInfo[attrName]
                    if attrType == 'enum':
                        cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, en=dynNodeTransformName)
                        cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), channelBox=True)
                    elif attrType == 'bool':
                        cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), 0)
                    elif attrType == 'long':
                        cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), 0)
                    elif attrType == 'double':
                        cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), 0)

                # Connect attribute.
                if cmds.attributeQuery(attrName, node=dynNode, exists=True):
                    val = cmds.getAttr('%s.%s' % (dynNode, attrName))
                    cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), val)
                    cmds.connectAttr('%s.%s' % (dynCtrl, attrLongName), '%s.%s' % (dynNode, attrName), f=True)

        elif dynamicType == 'hair':
            for attrName in hairDynNodeAttrsInfo.keys():
                attrLongName = dynNodeTransformName + '_' + attrName
                # Add attribute.
                if cmds.attributeQuery(attrLongName, node=dynCtrl, exists=True):
                    continue
                else:
                    attrType = hairDynNodeAttrsInfo[attrName]
                    if attrType == 'enum':
                        cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, en=dynNodeTransformName)
                        cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), channelBox=True)
                    elif attrType == 'bool':
                        cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), 0)
                    elif attrType == 'short':
                        cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), 0)
                    elif attrType == 'double':
                        cmds.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), 0)

                # Connect attribute.
                if cmds.attributeQuery(attrName, node=dynNode, exists=True):
                    val = cmds.getAttr('%s.%s' % (dynNode, attrName))
                    cmds.setAttr('%s.%s' % (dynCtrl, attrLongName), val)
                    cmds.connectAttr('%s.%s' % (dynCtrl, attrLongName), '%s.%s' % (dynNode, attrName), f=True)

            hairEnableAttrName = dynNodeTransformName + '_enable'
            cmds.connectAttr('%s.%s' % (dynCtrl, hairEnableAttrName), '%s.active' % dynNode, f=True)
            simMethodCondition = cmds.createNode('condition', n='{0}_simMethod_cond'.format(dynNode))
            cmds.setAttr('%s.colorIfTrueR' % simMethodCondition, 1)
            cmds.setAttr('%s.colorIfFalseR' % simMethodCondition, 3)
            cmds.connectAttr('%s.%s' % (dynCtrl, hairEnableAttrName), '%s.firstTerm' % simMethodCondition, f=True)
            cmds.connectAttr('%s.outColorR' % simMethodCondition, '%s.simulationMethod' % dynNode, f=True)


def setupWindDirectionObj(solver):
    # Dag setup
    windObj = cmds.cone(ch=False, n='{0}_windDirObj'.format(solver))[0]
    cmds.setAttr('%s.overrideEnabled' % windObj, True)
    cmds.setAttr('%s.overrideShading' % windObj, False)
    aimLoc = cmds.spaceLocator(n='windDirAim_loc')[0]
    cmds.setAttr('%s.visibility' % aimLoc, False)
    cmds.parent(aimLoc, windObj)
    cmds.setAttr('%s.translateX' % aimLoc, 1)

    # DG setup
    windObjWsMatrixDec = cmds.createNode('decomposeMatrix', n='{0}_decMatrix'.format(windObj))
    windVectorNode = cmds.createNode('plusMinusAverage', n='windVector_minus')
    cmds.setAttr('%s.operation' % windVectorNode, 2)
    cmds.connectAttr('%s.worldMatrix' % windObj, '%s.inputMatrix' % windObjWsMatrixDec, f=True)

    aimLocShape = cmds.listRelatives(aimLoc, shapes=True)[0]
    cmds.connectAttr('%s.worldPosition' % aimLocShape, '%s.input3D[0]' % windVectorNode, f=True)
    cmds.connectAttr('%s.outputTranslate' % windObjWsMatrixDec, '%s.input3D[1]' % windVectorNode, f=True)
    cmds.connectAttr('%s.output3D' % windVectorNode, '%s.windDirection' % solver, f=True)


def addCollider(solver, colliderGeo):
    cmds.select(colliderGeo, r=True)
    nRgdShpName = mel.eval('makeCollideNCloth;')[0]
    cmds.setAttr('%s.thickness' % nRgdShpName, 0.1)
    cmds.setAttr('%s.pushOutRadius' % nRgdShpName, 0.1)
    nRgdParent = cmds.listRelatives(nRgdShpName, parent=True)[0]
    rigidTrsf = cmds.rename(nRgdParent, colliderGeo + '_nRigid')

    cmds.select(rigidTrsf, r=True)
    mel.eval('assignNSolver "%s";' % solver)


def changeSolver(dynamicNode, solver=None):
    if not solver:
        solver = cmds.createNode('nucleus')

    nodeType = cmds.nodeType(dynamicNode)
    if nodeType == 'transform':
        shapes = cmds.listRelatives(dynamicNode, shapes=True)
        if shapes:
            dynamicNode = shapes[0]

    cmds.connectAttr('time1.outTime', '%s.currentTime' % solver, f=True)
    cmds.connectAttr('%s.startFrame' % solver, '%s.startFrame' % dynamicNode, f=True)

    index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='outputObjects')
    cmds.connectAttr('%s.outputObjects[%d]' % (solver, index), '%s.nextState' % dynamicNode, f=True)

    index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActive')
    connections = cmds.listConnections('%s.currentState' % dynamicNode, s=True, d=False, plugs=True)
    if connections:
        cmds.disconnectAttr(connections[0], '%s.currentState' % dynamicNode)
    cmds.connectAttr('%s.currentState' % dynamicNode, '%s.inputActive[%d]' % (solver, index))

    index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActiveStart')
    connections = cmds.listConnections('%s.startState' % dynamicNode, s=True, d=False, plugs=True)
    if connections:
        cmds.disconnectAttr(connections[0], '%s.startState' % dynamicNode)
    cmds.connectAttr('%s.startState' % dynamicNode, '%s.inputActiveStart[%d]' % (solver, index))


def changeHairSystem(sourceHairSystem, targetHairSystem):
    # Get shape nodes if transforms were passed
    if cmds.nodeType(sourceHairSystem) == 'transform':
        shapes = cmds.listRelatives(sourceHairSystem, shapes=True)
        if shapes:
            sourceHairSystem = shapes[0]
    if cmds.nodeType(targetHairSystem) == 'transform':
        shapes = cmds.listRelatives(targetHairSystem, shapes=True)
        if shapes:
            targetHairSystem = shapes[0]

    availableOutputHairId = globalUtil.findMultiAttributeEmptyIndex(str(targetHairSystem), 'outputHair')

    follicles = cmds.listConnections(sourceHairSystem, type='follicle', s=False) or []
    for follicle in follicles:
        cmds.connectAttr('%s.outputHair[%d]' % (targetHairSystem, availableOutputHairId),
                         '%s.currentPosition' % follicle, f=True)
        cmds.connectAttr('%s.outHair' % follicle,
                         '%s.inputHair[%d]' % (targetHairSystem, availableOutputHairId), f=True)
        availableOutputHairId += 1


def attachFollicleToMesh(follicle, mesh, position):
    PLUGIN_NAME = 'nearestPointOnMesh'
    if not cmds.pluginInfo(PLUGIN_NAME, q=True, loaded=True):
        cmds.loadPlugin(PLUGIN_NAME)

    # Resolve shapes
    if cmds.nodeType(follicle) == 'transform':
        shapes = cmds.listRelatives(follicle, shapes=True)
        if shapes:
            follicle = shapes[0]

    if cmds.nodeType(mesh) == 'transform':
        # Get non-intermediate shape
        shapes = cmds.listRelatives(mesh, shapes=True, noIntermediate=True)
        if shapes:
            mesh = shapes[0]

    nearPntOnMesh = cmds.createNode(PLUGIN_NAME)
    cmds.setAttr('%s.inPosition' % nearPntOnMesh, *position)
    cmds.connectAttr('%s.worldMesh' % mesh, '%s.inMesh' % nearPntOnMesh, f=True)
    parmU = cmds.getAttr('%s.parameterU' % nearPntOnMesh)
    parmV = cmds.getAttr('%s.parameterV' % nearPntOnMesh)
    cmds.delete(nearPntOnMesh)

    cmds.setAttr('%s.parameterU' % follicle, parmU)
    cmds.setAttr('%s.parameterV' % follicle, parmV)
    cmds.connectAttr('%s.outMesh' % mesh, '%s.inputMesh' % follicle, f=True)
    cmds.connectAttr('%s.worldMatrix' % mesh, '%s.inputWorldMatrix' % follicle, f=True)

    follicleTransform = cmds.listRelatives(follicle, parent=True)[0]
    cmds.connectAttr('%s.outTranslate' % follicle, '%s.translate' % follicleTransform, f=True)
    cmds.connectAttr('%s.outRotate' % follicle, '%s.rotate' % follicleTransform, f=True)
