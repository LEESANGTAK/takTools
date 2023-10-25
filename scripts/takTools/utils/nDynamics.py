import pymel.core as pm

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

    dynCtrl = pm.PyNode(control)
    solver = pm.PyNode(solver)
    dynNodes = [pm.PyNode(node).getShape() for node in dynamicNodes]

    for attrName in solverAttrsInfo.keys():
        attrLongName = solver + '_' + attrName
        # Add attribute.
        if dynCtrl.hasAttr(attrLongName):
            continue
        else:
            attrType = solverAttrsInfo[attrName]
            if attrType == 'enum':
                pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, en=['--------------------'])
                pm.setAttr('%s.%s' %(dynCtrl, attrLongName), channelBox=True)
            elif attrType == 'bool':
                pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                pm.setAttr('%s.%s' %(dynCtrl, attrLongName))
            elif attrType == 'long':
                pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                pm.setAttr('%s.%s' %(dynCtrl, attrLongName))
            elif attrType == 'double':
                pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                pm.setAttr('%s.%s' %(dynCtrl, attrLongName))

        # Connect attribute.
        if solver.hasAttr(attrName):
            val = solver.attr(attrName).get()
            dynCtrl.attr(attrLongName).set(val)
            dynCtrl.attr(attrLongName) >> solver.attr(attrName)

    for dynNode in dynNodes:
        if dynamicType == 'cloth':
            for attrName in clothDynNodeAttrsInfo.keys():
                attrLongName = dynNode.getTransform() + '_' + attrName
                # Add attribute.
                if dynCtrl.hasAttr(attrLongName):
                    continue
                else:
                    attrType = clothDynNodeAttrsInfo[attrName]
                    if attrType == 'enum':
                        pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, en=[dynNode.getTransform().name()])
                        pm.setAttr('%s.%s' %(dynCtrl, attrLongName), channelBox=True)
                    elif attrType == 'bool':
                        pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        pm.setAttr('%s.%s' %(dynCtrl, attrLongName))
                    elif attrType == 'long':
                        pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        pm.setAttr('%s.%s' %(dynCtrl, attrLongName))
                    elif attrType == 'double':
                        pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        pm.setAttr('%s.%s' %(dynCtrl, attrLongName))

                # Connect attribute.
                if dynNode.hasAttr(attrName):
                    val = dynNode.attr(attrName).get()
                    dynCtrl.attr(attrLongName).set(val)
                    dynCtrl.attr(attrLongName) >> dynNode.attr(attrName)

        elif dynamicType == 'hair':
            for attrName in hairDynNodeAttrsInfo.keys():
                attrLongName = dynNode.getTransform() + '_' + attrName
                # Add attribute.
                if dynCtrl.hasAttr(attrLongName):
                    continue
                else:
                    attrType = hairDynNodeAttrsInfo[attrName]
                    if attrType == 'enum':
                        pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, en=[dynNode.getTransform().name()])
                        pm.setAttr('%s.%s' %(dynCtrl, attrLongName), channelBox=True)
                    elif attrType == 'bool':
                        pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        pm.setAttr('%s.%s' %(dynCtrl, attrLongName))
                    elif attrType == 'short':
                        pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        pm.setAttr('%s.%s' %(dynCtrl, attrLongName))
                    elif attrType == 'double':
                        pm.addAttr(dynCtrl, ln=attrLongName, at=attrType, keyable=True)
                        pm.setAttr('%s.%s' %(dynCtrl, attrLongName))

                # Connect attribute.
                if dynNode.hasAttr(attrName):
                    val = dynNode.attr(attrName).get()
                    dynCtrl.attr(attrLongName).set(val)
                    dynCtrl.attr(attrLongName) >> dynNode.attr(attrName)

            hairEnableAttrName = dynNode.getTransform() + '_enable'
            dynCtrl.attr(hairEnableAttrName) >> dynNode.active
            simMethodCondition = pm.createNode('condition', n='{0}_simMethod_cond'.format(dynNode))
            simMethodCondition.colorIfTrueR.set(1)
            simMethodCondition.colorIfFalseR.set(3)
            dynCtrl.attr(hairEnableAttrName) >> simMethodCondition.firstTerm
            simMethodCondition.outColorR >> dynNode.simulationMethod



def setupWindDirectionObj(solver):
    solver = pm.PyNode(solver)

    # Dag setup
    windObj = pm.cone(ch=False, n='{0}_windDirObj'.format(solver))[0]
    windObj.overrideEnabled.set(True)
    windObj.overrideShading.set(False)
    aimLoc = pm.spaceLocator(n='windDirAim_loc')
    aimLoc.hide()
    windObj | aimLoc
    aimLoc.translateX.set(1)

    # DG setup
    windObjWsMatrixDec = pm.createNode('decomposeMatrix', n='{0}_decMatrix'.format(windObj))
    windVectorNode = pm.createNode('plusMinusAverage', n='windVector_minus')
    windVectorNode.operation.set(2)
    windObj.worldMatrix >> windObjWsMatrixDec.inputMatrix
    aimLoc.getShape().worldPosition >> windVectorNode.input3D[0]
    windObjWsMatrixDec.outputTranslate >> windVectorNode.input3D[1]
    windVectorNode.output3D >> solver.windDirection


def addCollider(solver, colliderGeo):
    solver = pm.PyNode(solver)
    colliderGeo = pm.PyNode(colliderGeo)

    pm.select(colliderGeo, r=True)
    nRgdShp = pm.PyNode(pm.mel.eval('makeCollideNCloth;')[0])
    nRgdShp.thickness.set(0.1)
    nRgdShp.pushOutRadius.set(0.1)
    rigidTrsf = nRgdShp.getParent().rename(colliderGeo.name()+'_nRigid')

    pm.select(rigidTrsf, r=True)
    pm.mel.eval('assignNSolver "%s";' % solver)


def changeSolver(dynamicNode, solver=None):
    if not solver:
        solver = pm.createNode('nucleus')
    else:
        solver = pm.PyNode(solver)

    dynamicNode = pm.PyNode(dynamicNode)
    if dynamicNode.nodeType() == 'transform':
        dynamicNode = dynamicNode.getShape()

    time1 = pm.PyNode('time1')
    time1.outTime.connect(solver.currentTime, f=True)

    solver.startFrame.connect(dynamicNode.startFrame, f=True)

    index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='outputObjects')
    solver.outputObjects[index].connect(dynamicNode.nextState, f=True)

    index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActive')
    dynamicNode.currentState.disconnect()
    dynamicNode.currentState.connect(solver.inputActive[index])

    index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActiveStart')
    dynamicNode.startState.disconnect()
    dynamicNode.startState.connect(solver.inputActiveStart[index])


def changeHairSystem(sourceHairSystem, targetHairSystem):
    sourceHairSystem = pm.PyNode(sourceHairSystem)
    targetHairSystem = pm.PyNode(targetHairSystem)
    sourceHairSystem = sourceHairSystem.getShape() if sourceHairSystem.nodeType() == 'transform' else sourceHairSystem
    targetHairSystem = targetHairSystem.getShape() if targetHairSystem.nodeType() == 'transform' else targetHairSystem

    availableOutputHairId = globalUtil.findMultiAttributeEmptyIndex(str(targetHairSystem), 'outputHair')

    follicles = sourceHairSystem.listConnections(type='follicle', s=False)
    for follicle in follicles:
        targetHairSystem.outputHair[availableOutputHairId] >> follicle.currentPosition
        follicle.outHair >> targetHairSystem.inputHair[availableOutputHairId]
        availableOutputHairId += 1


def attachFollicleToMesh(follicle, mesh, position):
    PLUGIN_NAME = 'nearestPointOnMesh'
    if not pm.pluginInfo(PLUGIN_NAME, q=True, loaded=True):
        pm.loadPlugin(PLUGIN_NAME)

    follicle = pm.PyNode(follicle)
    mesh = pm.PyNode(mesh)
    nearPntOnMesh = pm.createNode(PLUGIN_NAME)

    if follicle.nodeType() == 'transform':
        follicle = follicle.getShape()

    if mesh.nodeType() == 'transform':
        mesh = mesh.getShape(ni=True)

    nearPntOnMesh.inPosition.set(position)
    mesh.worldMesh >> nearPntOnMesh.inMesh
    parmU = nearPntOnMesh.parameterU.get()
    parmV = nearPntOnMesh.parameterV.get()
    pm.delete(nearPntOnMesh)

    follicle.parameterU.set(parmU)
    follicle.parameterV.set(parmV)
    mesh.outMesh >> follicle.inputMesh
    mesh.worldMatrix >> follicle.inputWorldMatrix
    follicle.outTranslate >> follicle.getTransform().translate
    follicle.outRotate >> follicle.getTransform().rotate
