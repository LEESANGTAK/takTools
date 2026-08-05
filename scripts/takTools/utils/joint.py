import maya.api.OpenMaya as om

import maya.cmds as cmds


def getRootJoints(joints):
    rootJnts = []
    for jnt in joints:
        if cmds.nodeType(cmds.listRelatives(jnt, p=True)[0]) != 'joint':
            rootJnts.append(jnt)
    return rootJnts


def orientJoint(aimObj, upObj, jnt):
    aimObjPos = cmds.xform(aimObj, q=True, t=True, ws=True)
    upObjPos = cmds.xform(upObj, q=True, t=True, ws=True)
    jntPos = cmds.xform(jnt, q=True, t=True, ws=True)

    aimVec = om.MPoint(aimObjPos) - om.MPoint(jntPos)
    upVec = om.MPoint(upObjPos) - om.MPoint(jntPos)
    remainVec = aimVec.cross(upVec)
    rightUpVec = remainVec.cross(aimVec)

    aimVec.normalize()
    rightUpVec.normalize()
    remainVec.normalize()

    jntMatrix = om.MMatrix(
        aimVec.x, aimVec.y, aimVec.z, 0,
        rightUpVec.x, rightUpVec.y, rightUpVec.z, 0,
        remainVec.x, remainVec.y, remainVec.z, 0,
        jntPos[0], jntPos[1], jntPos[2], 1
    )

    cmds.xform(jnt, matrix=jntMatrix, ws=True)


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
    centerPos = om.MPoint(cmds.xform(centerObj, q=True, t=True, ws=True))
    upPos = om.MPoint(cmds.xform(upObj, q=True, t=True, ws=True))

    for jnt in jnts:
        jntPos = om.MPoint(cmds.xform(jnt, q=True, t=True, ws=True))

        aimVec = centerPos - jntPos
        upVec = upPos - jntPos
        otherVec = upVec.cross(aimVec)
        upVec = aimVec.cross(otherVec)

        aimVec.normalize()
        upVec.normalize()
        otherVec.normalize()

        jntMatrix = om.MMatrix(
            aimVec.x, aimVec.y, aimVec.z, 0,
            otherVec.x, otherVec.y, otherVec.z, 0,
            upVec.x, upVec.y, upVec.z, 0,
            jntPos[0], jntPos[1], jntPos[2], 1
        )

        cmds.xform(jnt, matrix=jntMatrix, ws=True)


def getUnusedJnt(jnts):
    unUsedJnts = []

    # Get all joints in hierarchy
    allJnts = []
    for jnt in jnts:
        allJnts.append(jnt)
        childJnts = cmds.listRelatives(jnt, ad=True, type='joint')
        allJnts.extend(childJnts)

    for jnt in allJnts:
        skinClst = cmds.listConnections(f'{jnt}.worldMatrix', s=False)
        childJnt = cmds.listRelatives(jnt, type='joint')
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

    allChildJnts = cmds.ls(rootJnt, dag=True, type='joint')
    for childJnt in allChildJnts:
        if not cmds.listRelatives(childJnt, type='joint'):
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
        newJnt = cmds.duplicate(oldJnt, n=oldJnt+'_skin', parentOnly=True)[0]
        cmds.parent(newJnt, world=True)
        newJnts.append(newJnt)

        cmds.parentConstraint(oldJnt, newJnt)
        cmds.connectAttr(f'{oldJnt}.scale', f'{newJnt}.scale')

    return newJnts


def buildHierarchy(jntInfo):
    for info in jntInfo:
        try:
            cmds.parent(info['skinJnt'], info['skinJntParent'])
        except:
            pass


def createJointChain(joints, suffix):
    newJoints = []

    for jnt in joints:
        newJnt = cmds.duplicate(jnt, n=jnt + suffix, po=True)[0]
        parentCnst = cmds.parentConstraint(newJnt, jnt, mo=True)
        cmds.setAttr(f'{parentCnst}.interpType', 2)
        cmds.connectAttr(f'{newJnt}.scale', f'{jnt}.scale')
        newJoints.append(newJnt)
        cmds.parent(newJnt, world=True)

    for jnt in joints:
        jntParent = cmds.listRelatives(jnt, p=True)[0]
        if jntParent:
            newJntParent = jntParent + suffix
            if cmds.objExists(newJntParent):
                cmds.parent(jnt + suffix, newJntParent)

    cmds.parent(newJoints[0], world=True)

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
        import tak_misc

        # Selection Order: driverJnt -> rootVtx -> midVtx -> endVtx
        sels = cmds.ls(os=True, fl=True)
        tak_misc.setupCorrectiveJointChain('Elbow_R_inner_cor_jnt', sels[0], sels[1], sels[2], sels[3])
    """

    cmds.select(cl=True)

    # Create joint chain
    rootJnt = name+'_root_cor_jnt'
    midJnt = name+'_mid_cor_jnt'
    endJnt = name+'_end_cor_jnt'
    cmds.joint(p=rootVtx.getPosition(space='world'), n=rootJnt)
    cmds.joint(p=midVtx.getPosition(space='world'), n=midJnt)
    cmds.joint(p=endVtx.getPosition(space='world'), n=endJnt)
    cmds.CompleteCurrentTool()
    cmds.select(rootJnt, r=True)
    cmds.joint(e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
    cmds.orientConstraint(driverJnt, midJnt, mo=True)

    # Create groups
    corJntPosGrp = cmds.createNode('transform', n=name+'_corJntPos_grp')
    cmds.delete(cmds.parentConstraint(midJnt, corJntPosGrp, mo=False))
    corJntGrp = cmds.duplicate(corJntPosGrp, n=name+'_corJnt_grp')[0]
    cmds.parent(corJntPosGrp, corJntGrp)
    cmds.parent(rootJnt, corJntPosGrp)
    cmds.parentConstraint(cmds.listRelatives(driverJnt, p=True)[0], corJntGrp, mo=True)

    # Create locators
    posExtractLoc = cmds.spaceLocator(n=name+'_posExtract_loc')
    cmds.delete(cmds.parentConstraint(midJnt, posExtractLoc, mo=False))
    rotExtractLoc = cmds.spaceLocator(n=name+'_rotExtract_loc')
    cmds.delete(cmds.parentConstraint(endJnt, rotExtractLoc, mo=False))
    cmds.parent(rotExtractLoc, posExtractLoc)
    cmds.parent(posExtractLoc, corJntGrp)
    cmds.parentConstraint(cmds.listRelatives(driverJnt, p=True)[0], driverJnt, posExtractLoc, mo=True, skipRotate=['x', 'y', 'z'])
    cmds.parentConstraint(cmds.listRelatives(driverJnt, p=True)[0], driverJnt, rotExtractLoc, mo=True, skipRotate=['x', 'y', 'z'])

    # Create nodes
    posNormalDotVpr = cmds.createNode('vectorProduct', n=name+'_posNormalDot_vpr')
    normalDotVpr = cmds.createNode('vectorProduct', n=name+'_normalDot_vpr')
    cmds.setAttr(f'{normalDotVpr}.inputX', 1)
    intersectionMul = cmds.createNode('multiplyDivide', n=name+'_intersection_mul')
    cmds.setAttr(f'{intersectionMul}.operation', 2)
    distMul = cmds.createNode('multiplyDivide', n=name+'_dist_mul')
    cmds.setAttr(f'{distMul}.input1X', 1)

    # Connect
    cmds.connectAttr(f'{posExtractLoc}.translate', f'{posNormalDotVpr}.input1')
    cmds.connectAttr(f'{rotExtractLoc}.translate', f'{posNormalDotVpr}.input2')
    cmds.connectAttr(f'{rotExtractLoc}.translate', f'{normalDotVpr}.input2')
    cmds.connectAttr(f'{posNormalDotVpr}.output', f'{intersectionMul}.input1')
    cmds.connectAttr(f'{normalDotVpr}.output', f'{intersectionMul}.input2')
    cmds.connectAttr(f'{intersectionMul}.output', f'{distMul}.input2')
    cmds.connectAttr(f'{distMul}.output', f'{corJntPosGrp}.translate')


def transferRotation(joint):
    jori = cmds.getAttr(f'{joint}.jointOrient')[0]
    jrot = cmds.getAttr(f'{joint}.rotate')[0]
    cmds.setAttr(f'{joint}.jointOrient', *[joVal+jrVal for joVal, jrVal in zip(jori, jrot)])
    cmds.setAttr(f'{joint}.rotate', 0, 0, 0)


def createOnCenter(objects):
    bb = om.MBoundingBox()
    for obj in objects:
        objPoint = om.MPoint(cmds.xform(obj, q=True, t=True, ws=True))
        bb.expand(objPoint)
    jnt = cmds.createNode('joint')
    cmds.xform(jnt, t=(bb.center.x, bb.center.y, bb.center.z), ws=True)
