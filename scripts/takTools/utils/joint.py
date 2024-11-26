import maya.api.OpenMaya as om

import pymel.core as pm
import maya.cmds as cmds


def getRootJoints(joints):
    rootJnts = []
    for jnt in joints:
        if jnt.getParent().nodeType() != 'joint':
            rootJnts.append(jnt)
    return rootJnts


def orientJoint(aimObj, upObj, jnt):
    aimObjPos = pm.xform(aimObj, q=True, t=True, ws=True)
    upObjPos = pm.xform(upObj, q=True, t=True, ws=True)
    jntPos = pm.xform(jnt, q=True, t=True, ws=True)

    aimVec = pm.datatypes.Point(aimObjPos) - pm.datatypes.Point(jntPos)
    upVec = pm.datatypes.Point(upObjPos) - pm.datatypes.Point(jntPos)
    remainVec = aimVec.cross(upVec)
    rightUpVec = remainVec.cross(aimVec)

    aimVec.normalize()
    rightUpVec.normalize()
    remainVec.normalize()

    jntMatrix = pm.datatypes.Matrix(
        aimVec.x, aimVec.y, aimVec.z, 0,
        rightUpVec.x, rightUpVec.y, rightUpVec.z, 0,
        remainVec.x, remainVec.y, remainVec.z, 0,
        jntPos[0], jntPos[1], jntPos[2], 1
    )

    pm.xform(jnt, matrix=jntMatrix, ws=True)


def jointOrientWithGeometry(joint, upObject, geometry):
    sels = om.MSelectionList()
    sels.add(joint)
    sels.add(upObject)
    sels.add(geometry)

    jntDag = sels.getDagPath(0)
    upObjDag = sels.getDagPath(1)
    geoDag = sels.getDagPath(2)

    jntWsMtx = om.MTransformationMatrix(jntDag.inclusiveMatrix())
    jntVec = jntWsMtx.translation(om.MSpace.kWorld)

    upObjWsMtx = om.MTransformationMatrix(upObjDag.inclusiveMatrix())
    upObjVec = upObjWsMtx.translation(om.MSpace.kWorld)

    geoDag.extendToShape(0)
    meshFn = om.MFnMesh(geoDag)

    aimVec = upObjVec - jntVec
    normalVec = meshFn.getClosestNormal(om.MPoint(jntVec), om.MSpace.kWorld)[0]
    biNormalVec = normalVec ^ aimVec
    tangentVec = biNormalVec ^ normalVec

    tangentVec.normalize()
    biNormalVec.normalize()
    normalVec.normalize()

    matrix = [
        tangentVec.x, tangentVec.y, tangentVec.z, 0,
        normalVec.x, normalVec.y, normalVec.z, 0,
        biNormalVec.x, biNormalVec.y, biNormalVec.z, 0,
        jntVec.x, jntVec.y, jntVec.z, 1
    ]

    alignedTrsfMtx = om.MTransformationMatrix(om.MMatrix(matrix))
    jntTrsfFn = om.MFnTransform(jntDag)
    jntTrsfFn.setTransformation(alignedTrsfMtx)


def radialJointOrient(centerObj, upObj, jnts):
    centerPos = pm.datatypes.Point(pm.xform(centerObj, q=True, t=True, ws=True))
    upPos = pm.datatypes.Point(pm.xform(upObj, q=True, t=True, ws=True))

    for jnt in jnts:
        jntPos = pm.datatypes.Point(pm.xform(jnt, q=True, t=True, ws=True))

        aimVec = centerPos - jntPos
        upVec = upPos - jntPos
        otherVec = upVec.cross(aimVec)
        upVec = aimVec.cross(otherVec)

        aimVec.normalize()
        upVec.normalize()
        otherVec.normalize()

        jntMatrix = pm.datatypes.Matrix(
            aimVec.x, aimVec.y, aimVec.z, 0,
            otherVec.x, otherVec.y, otherVec.z, 0,
            upVec.x, upVec.y, upVec.z, 0,
            jntPos[0], jntPos[1], jntPos[2], 1
        )

        pm.xform(jnt, matrix=jntMatrix, ws=True)


def getUnusedJnt(jnts):
    unUsedJnts = []

    # Get all joints in hierarchy
    allJnts = []
    for jnt in jnts:
        allJnts.append(jnt)
        childJnts = jnt.getChildren(ad=True, type='joint')
        allJnts.extend(childJnts)

    for jnt in allJnts:
        skinClst = jnt.worldMatrix.connections(s=False)
        childJnt = jnt.getChildren(type='joint')
        if not skinClst and not childJnt:
            unUsedJnts.append(jnt)

    return unUsedJnts


def getEndJoints(rootJnt):
    endJnts = []
    childJnts = cmds.listRelatives(rootJnt, ad=True, type='joint')
    for childJnt in childJnts:
        if not cmds.listRelatives(childJnt, type='joint'):
            endJnts.append(childJnt)
    return endJnts


def getJointsExceptEnd(rootJnt):
    joints = []

    rootJnt = pm.PyNode(rootJnt)
    allChildJnts = pm.ls(rootJnt, dag=True, type='joint')
    for childJnt in allChildJnts:
        if not childJnt.getChildren(type='joint'):
            continue
        joints.append(childJnt)

    return joints


def createSingleSkeleton(joints):
    jntInfo = getJntInfo(joints)
    createSkinJnts(joints)
    buildHierarchy(jntInfo)


def getJntInfo(joints):
    parentInfo = []

    for jnt in joints:
        parentInfo.append(
            {
                'motionJnt': jnt,
                'skinJnt': jnt.name()+'_skin',
                'skinJntParent': jnt.getParent()+'_skin'
            }
        )

    return parentInfo


def createSkinJnts(joints):
    newJnts = []

    for oldJnt in joints:
        newJnt = oldJnt.duplicate(n=oldJnt.name()+'_skin', parentOnly=True)[0]
        pm.parent(newJnt, world=True)
        newJnts.append(newJnt)

        pm.parentConstraint(oldJnt, newJnt)
        oldJnt.s >> newJnt.s

    return newJnts


def buildHierarchy(jntInfo):
    for info in jntInfo:
        try:
            pm.parent(info['skinJnt'], info['skinJntParent'])
        except:
            pass


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


def transferRotation(joint):
    joint.jointOrient.set(joint.jointOrient.get() + joint.rotate.get())
    joint.rotate.set(0, 0, 0)


def createOnCenter(objects):
    bb = om.MBoundingBox()
    for obj in objects:
        objPoint = om.MPoint(cmds.xform(obj, q=True, t=True, ws=True))
        bb.expand(objPoint)
    jnt = cmds.createNode('joint')
    cmds.xform(jnt, t=(bb.center.x, bb.center.y, bb.center.z), ws=True)
