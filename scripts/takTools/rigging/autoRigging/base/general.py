import os
import re

import pymel.core as pm

from . import bSkinSaver


def buildSkeletalMesh(modelFile, skeletonFile, skinFile):
    referenceModel(modelFile, skinFile)
    rootJoint = importSkeleton(skeletonFile)
    freezeSkeleton(rootJoint)
    importSkin(skinFile)

def referenceModel(modelFile, skinFile):
    modelNamespace = getNamespaceFromSkinFile(skinFile)
    pm.createReference(modelFile, ns=modelNamespace)

def importSkeleton(skeletonFile):
    rootJoint = None
    newNodes = pm.importFile(skeletonFile, returnNewNodes=True)
    joints = pm.ls(newNodes, type='joint')
    for jnt in joints:
        jntParent = jnt.getParent()
        if jntParent and jntParent.type() != 'joint':
            rootJoint = jnt
            break
        elif not jntParent:
            rootJoint = jnt
            break
    return rootJoint

def freezeSkeleton(rootJoint):
    pm.makeIdentity(rootJoint, apply=True)

def exportSkin(mesh, filePath):
    pm.select(mesh, r=True)
    bSkinSaver.bSaveSkinValues(filePath)

def importSkin(skinFile):
    bSkinSaver.bLoadSkinValues(False, skinFile)

def getNamespaceFromSkinFile(skinFile):
    namespace = ''

    with open(skinFile, 'r') as f:
        fContents = f.read()

    searchObj = re.search(r'(.*):.*', fContents)
    if searchObj:
        namespace = searchObj.group(1)

    return namespace

def createJointChain(joints, suffix):
    newJoints = []

    joints = [pm.PyNode(jnt) for jnt in joints]

    for jnt in joints:
        newJnt = pm.duplicate(jnt, n=jnt + suffix, po=True)[0]
        parentCnst = pm.parentConstraint(newJnt, jnt, mo=True)
        parentCnst.interpType.set(2)
        newJnt.scale >> jnt.scale
        newJoints.append(newJnt)
        pm.parent(newJnt, world=True)

    for jnt in joints:
        jntParent = jnt.getParent()
        if jntParent:
            newJntParent = jntParent + suffix
            if pm.objExists(newJntParent):
                pm.parent(jnt + suffix, newJntParent)

    pm.parent(newJoints[0], world=True)

    return newJoints

def duplicateJoint(jointRoot, suffix):
    newJointRoot = pm.duplicate(jointRoot, returnRootsOnly=True)[0]
    childJnts = newJointRoot.getChildren(ad=True, type='joint')
    for childJnt in childJnts:
        childJnt.rename(childJnt.name() + suffix)
    newJointRoot.rename(jointRoot.name() + suffix)
    return newJointRoot

def createController(drivenObject,
                     controllerName,
                     parentConstreaint=True,
                     pointConstraint=False,
                     orientConstraint=False,
                     scaleConstraint=False,
                     matchRotateOrder=False,
                     parentSpace=None):
    drivenObject = pm.PyNode(drivenObject)

    ctrl = pm.circle(n=controllerName, normal=[1.0, 0.0, 0.0], ch=False)[0]

    if matchRotateOrder:
        ctrl.rotateOrder.set(drivenObject.rotateOrder.get())

    ctrlSpace = pm.group(ctrl, n=ctrl + '_zero')
    pm.group(ctrl, n=ctrl + '_extra')

    pm.matchTransform(ctrlSpace, drivenObject, pos=True, rot=True)

    if parentConstreaint:
        pm.parentConstraint(ctrl, drivenObject, mo=True)
    else:
        if pointConstraint:
            pm.pointConstraint(ctrl, drivenObject, mo=True)
        if orientConstraint:
            pm.orientConstraint(ctrl, drivenObject, mo=True)
    if scaleConstraint:
        ctrl.scale >> drivenObject.scale

    if parentSpace:
        pm.parentConstraint(parentSpace, ctrlSpace, mo=True)

    return ctrl

def getSpaceGrp(obj):
    spaceGrp = None

    obj = pm.PyNode(obj)
    count = 1
    countLimit = 10
    found = False
    while not found:
        if count >= countLimit:
            break
        objParent = obj.getParent(generations=count)
        if 'zero' in objParent.name():
            found = True
            spaceGrp = objParent
        count += 1

    return spaceGrp

def setupCorrectiveJointChain(name, driverJnt, rootVtx, midVtx, endVtx):
    """
    This function setup corrective joint chain.
    Corrective joint chain useful on corner area of organic character like elbow, wrist, etc...

    Parameters:
        name(str): Prefix of corrective chain rig
        rootVtx(pymel.core.general.MeshVertex): Vertex for root joint of chain
        midVtx(pymel.core.general.MeshVertex): Vertex for middle joint of chain
        endVtx(pymel.core.general.MeshVertex): Vertex for end joint of chain
        driverJnt(pymel.core.nodetypes.Joint): Joint that driving joint chain

    Example:
        import pymel.core as pm
        import tak_misc

        # Selection Order: driverJnt -> rootVtx -> midVtx -> endVtx
        sels = pm.ls(os=True, fl=True)
        tak_misc.setupCorrectiveJointChain('Elbow_R_inner_cor_jnt', sels[0], sels[1], sels[2], sels[3])
    """

    pm.select(cl=True)

    # Create joint chain
    rootJnt = name+'_root_cor_jnt'
    midJnt = name+'_mid_cor_jnt'
    endJnt = name+'_end_cor_jnt'
    pm.joint(p=rootVtx.getPosition(space='world'), n=rootJnt)
    pm.joint(p=midVtx.getPosition(space='world'), n=midJnt)
    pm.joint(p=endVtx.getPosition(space='world'), n=endJnt)
    cmds.CompleteCurrentTool()
    pm.select(rootJnt, r=True)
    pm.joint(e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
    pm.orientConstraint(driverJnt, midJnt, mo=True)

    # Create groups
    corJntPosGrp = pm.createNode('transform', n=name+'_corJntPos_grp')
    pm.delete(pm.parentConstraint(midJnt, corJntPosGrp, mo=False))
    corJntGrp = corJntPosGrp.duplicate(n=name+'_corJnt_grp')[0]
    corJntPosGrp.setParent(corJntGrp)
    pm.parent(rootJnt, corJntPosGrp)
    pm.parentConstraint(driverJnt.getParent(), corJntGrp, mo=True)

    # Create locators
    posExtractLoc = pm.spaceLocator(n=name+'_posExtract_loc')
    pm.delete(pm.parentConstraint(midJnt, posExtractLoc, mo=False))
    rotExtractLoc = pm.spaceLocator(n=name+'_rotExtract_loc')
    pm.delete(pm.parentConstraint(endJnt, rotExtractLoc, mo=False))
    rotExtractLoc.setParent(posExtractLoc)
    posExtractLoc.setParent(corJntGrp)
    pm.parentConstraint(driverJnt.getParent(), driverJnt, posExtractLoc, mo=True, skipRotate=['x', 'y', 'z'])
    pm.parentConstraint(driverJnt.getParent(), driverJnt, rotExtractLoc, mo=True, skipRotate=['x', 'y', 'z'])

    # Create nodes
    posNormalDotVpr = pm.createNode('vectorProduct', n=name+'_posNormalDot_vpr')
    normalDotVpr = pm.createNode('vectorProduct', n=name+'_normalDot_vpr')
    normalDotVpr.input1X.set(1)
    intersectionMul = pm.createNode('multiplyDivide', n=name+'_intersection_mul')
    intersectionMul.operation.set(2)
    distMul = pm.createNode('multiplyDivide', n=name+'_dist_mul')
    distMul.input1X.set(1)

    # Connect
    posExtractLoc.translate >> posNormalDotVpr.input1
    rotExtractLoc.translate >> posNormalDotVpr.input2
    rotExtractLoc.translate >> normalDotVpr.input2
    posNormalDotVpr.output >> intersectionMul.input1
    normalDotVpr.output >> intersectionMul.input2
    intersectionMul.output >> distMul.input2
    distMul.output >> corJntPosGrp.translate

