import maya.OpenMaya as om

import maya.cmds as cmds
import pymel.core as pm

from takTools.utils import kdTree


SKELETON_SUFFIX = '_sk'
cmds.selectPref(trackSelectionOrder=True)


def createJointsOnSelection():
    cmds.undoInfo(openChunk=True)
    for obj in cmds.ls(sl=True, fl=True):
        jnt = cmds.createNode('joint', n='{0}{1}'.format(obj, SKELETON_SUFFIX))
        try:
            cmds.matchTransform(jnt, obj, pos=True, rot=True)
        except:
            objPos = cmds.xform(obj, q=True, t=True, ws=True)
            cmds.xform(jnt, t=objPos, ws=True)

        cmds.makeIdentity(jnt, apply=True)
    cmds.undoInfo(closeChunk=True)

def jointOnCenter():
    objects = pm.selected(fl=True)
    sumVector = pm.dt.Vector()
    for obj in objects:
        sumVector += pm.dt.Vector(pm.xform(obj, q=True, t=True, ws=True))
    pm.select(cl=True)
    pm.joint(p=sumVector/len(objects))

def jointOnManipulator():
    joint = None

    cmds.setToolTo('Move')
    pos = cmds.manipMoveContext('Move', q=True, p=True)
    # rot = [mel.eval('rad_to_deg(%f);' % rad) for rad in cmds.manipMoveContext('Move', q=True, oa=True)]

    cmds.select(cl=True)
    joint = cmds.createNode('joint')

    cmds.xform(joint, t=pos, ws=True)
    # cmds.xform(joint, ro=rot, ws=True)

    return joint

def fkChainFromSelection(objs):
    # Get start, mid, end point
    numObjs = len(objs)

    startObj = objs[0]
    midObj = objs[numObjs/2]
    endObj = objs[-1]

    startPoint = getWorldPoint(startObj)
    midPoint = getWorldPoint(midObj)
    endPoint = getWorldPoint(endObj)

    # Get plane normal
    normal = getPlaneNormal(startPoint, midPoint, endPoint)

    # Create joints on plane
    joints = []
    for obj in objs:
        objPoint = getWorldPoint(obj)
        closestIntersectPoint = getClosestIntersectionPoint(objPoint, startPoint, normal)
        jnt = cmds.createNode('joint', n='{0}{1}'.format(obj, SKELETON_SUFFIX))
        cmds.xform(jnt, t=(closestIntersectPoint.x, closestIntersectPoint.y, closestIntersectPoint.z), ws=True)
        joints.append(jnt)

    # Orient joints
    numJnts = len(joints)
    for i in range(numJnts):
        curJnt = joints[i]
        curJntPos = cmds.xform(curJnt, q=True, t=True, ws=True)
        curJntVector = om.MVector(*curJntPos)

        if not i == (numJnts-1):
            nextJnt = joints[i+1]
            nextJntPos = cmds.xform(nextJnt, q=True, t=True, ws=True)
            nextJntVector = om.MVector(*nextJntPos)

            aimVector = nextJntVector - curJntVector
            yVector = normal ^ aimVector

            aimVector.normalize()
            yVector.normalize()

            orientMatrix = [
                aimVector.x, aimVector.y, aimVector.z, 0.0,
                yVector.x, yVector.y, yVector.z, 0.0,
                normal.x, normal.y, normal.z, 0.0,
                curJntVector.x, curJntVector.y, curJntVector.z, 1.0
            ]
        else:  # End joint orientation is same as previous one. Just update position.
            orientMatrix[12] = curJntVector.x
            orientMatrix[13] = curJntVector.y
            orientMatrix[14] = curJntVector.z

        cmds.xform(curJnt, matrix=orientMatrix, ws=True)

    # Parent joints
    for i in range(numJnts):
        if i == 0:
            continue
        curJnt = joints[i]
        parentJnt = joints[i-1]
        cmds.parent(curJnt, parentJnt)

    # Freeze transform
    cmds.makeIdentity(joints[0], apply=True)

    return joints

def getClosestIntersectionPoint(sourcePoint, pointOnPlane, normal):
    intersectPoint = om.MPoint()

    # Decide sign depend on direction between normal and toSourcePoint vector
    pointOnPlaneToSourcePointVector = sourcePoint - pointOnPlane
    sign = 1
    if (normal * pointOnPlaneToSourcePointVector) > 1:
        sign = -1

    rayVector = normal * sign  # Ray vector is signed normal vector
    sourceToPlanePointVector = pointOnPlane - sourcePoint

    intersectPoint = sourcePoint + ( rayVector * ( (sourceToPlanePointVector * normal) / (rayVector * normal) ) )

    return intersectPoint

def getPlaneNormal(startPoint, midPoint, endPoint):
    normal = om.MVector()

    startToEndVector = endPoint - startPoint
    startToMidVector = midPoint - startPoint
    normal = startToEndVector ^ startToMidVector

    normal.normalize()

    return normal

def jointsFromCurve(curve=None, count=2, upType='Vector', upVector=[0.0, 1.0, 0.0], upObject=None, chain=True, localAxis=False):
    # Check errors
    if int(count) <= 1:
        raise RuntimeError('Count should be greater than 1.')

    joints = []
    crvFn = getNurbsCurveFn(curve)
    segments = count - 1

    # Get curve length
    crvLength = crvFn.length()

    # Get parameter increment
    increment = crvLength / segments

    # Create joints
    pointOnCrv = om.MPoint()
    for i in range(count):
        parm = crvFn.findParamFromLength(increment * i)
        crvFn.getPointAtParam(parm, pointOnCrv, om.MSpace.kWorld)

        jnt = cmds.createNode('joint', n='{0}_{1:02d}{2}'.format(curve, i+1, SKELETON_SUFFIX))
        joints.append(jnt)

        cmds.xform(jnt, t=(pointOnCrv.x, pointOnCrv.y, pointOnCrv.z), ws=True)

    # Orient joint
    if upType == 'Vector':
        orientJointsUpVector(joints, upVector)
    elif upType == 'Object':
        orientJointsUpObj(joints, upObject)

    # Display local axis
    showHideLocalAxis(joints, localAxis)

    # Parenting depend on chain option
    if chain:
        for i in range(len(joints)):
            if i == 0:
                continue
            cmds.parent(joints[i], joints[i-1])

    # Transfer rotation value to joint orient
    cmds.makeIdentity(joints[0], apply=True)

    return joints

def showHideLocalAxis(joints, state):
    for jnt in joints:
        if state:
            cmds.setAttr('{0}.displayLocalAxis'.format(jnt), True)
        else:
            cmds.setAttr('{0}.displayLocalAxis'.format(jnt), False)

def addJointSegments(startJoint, endJoint, count=2, chain=True):
    allJoints = [startJoint]
    segJoints = []

    # Get aim vector
    startJntVector = getWorldVector(startJoint)
    endJntVector = getWorldVector(endJoint)

    jntToChildVector = endJntVector - startJntVector

    # Create joints
    increment = 1.0/count
    scaler = increment
    for i in range(count-1):
        scaledVector = jntToChildVector * scaler
        segJointVector = startJntVector + scaledVector

        segJnt = cmds.duplicate(startJoint, n='{0}_{1:02d}_seg'.format(startJoint, i+1), po=True)[0]
        cmds.xform(segJnt, t=segJointVector, ws=True)

        segJoints.append(segJnt)
        allJoints.append(segJnt)

        scaler += increment

    allJoints.append(endJoint)

    if chain:
        for i in range(len(allJoints)):
            if i == 0:
                continue
            cmds.parent(allJoints[i], allJoints[i-1])
    else:
        for i in range(len(allJoints)):
            if i == 0:
                continue
            cmds.parent(allJoints[i], startJoint)

    cmds.select(startJoint, r=True)

    return segJoints

def resetJointsOrient(jnt):
    cmds.setAttr('{0}.rotate'.format(jnt), 0, 0, 0)
    cmds.setAttr('{0}.jointOrient'.format(jnt), 0, 0, 0)

def mirrorSkeleton(skeleton, searchStr, replaceStr):
    skeleton = pm.PyNode(skeleton)
    joints = skeleton.getChildren(ad=True, type='joint') + [skeleton]
    pm.undoInfo(openChunk=True)
    for jnt in joints[::-1]:
        mirJnt = pm.PyNode(jnt.replace(searchStr, replaceStr))
        mirJnt.translate.set(-jnt.translate.get())
        mirJnt.rotate.set(jnt.rotate.get())
    pm.undoInfo(closeChunk=True)

def connectSkeletonToOther(driverRoot, drivenRoot, excludeJoints, maintainOffset):
    driverJoints = cmds.listRelatives(driverRoot, type='joint', ad=True)
    if cmds.nodeType(driverRoot) == 'joint':
        driverJoints.append(driverRoot)
        driverJoints = list(set(driverJoints) - set(excludeJoints))
    drivenJoints = cmds.listRelatives(drivenRoot, type='joint', ad=True)
    if cmds.nodeType(drivenRoot) == 'joint':
        drivenJoints.append(drivenRoot)
        drivenJoints = list(set(drivenJoints) - set(excludeJoints))

    kdt = kdTree.KDTree()
    kdt.buildData(driverJoints)
    kdt.buildTree()

    cmds.undoInfo(openChunk=True)
    for drivenJnt in drivenJoints:
        drivenJntPos = cmds.xform(drivenJnt, q=True, t=True, ws=True)
        driverJntData = kdt.searchNearestData(drivenJntPos)
        cmds.parentConstraint(driverJntData['name'], drivenJnt, mo=maintainOffset)
        cmds.scaleConstraint(driverJntData['name'], drivenJnt, mo=maintainOffset)
        cmds.setAttr('{}.segmentScaleCompensate'.format(drivenJnt), False)
    cmds.undoInfo(closeChunk=True)

def disconnect(skelRoot, connectInfo):
    skelRoot = pm.PyNode(skelRoot)
    joints = skelRoot.getChildren(ad=True, type='joint')
    if skelRoot.nodeType() == 'joint':
        joints.append(skelRoot)
    for jnt in joints:
        connectList = []
        for attribute in [channel+axis for channel in 'trs' for axis in 'xyz']:
            drivenAttr = jnt.attr(attribute)
            driverAttr = drivenAttr.inputs(plugs=True)
            if driverAttr:
                driverAttr[0] // drivenAttr
                connectList.append((driverAttr[0], drivenAttr))
        connectInfo[jnt] = connectList

def reconnect(skelRoot, connectInfo):
    skelRoot = pm.PyNode(skelRoot)
    joints = skelRoot.getChildren(ad=True, type='joint')
    if skelRoot.nodeType() == 'joint':
        joints.append(skelRoot)
    for jnt in joints:
        connectList = connectInfo[jnt]
        for connect in connectList:
            connect[0] >> connect[1]


### Utils ###
def orientJointsUpVector(joints, upVector):
    upVector = om.MVector(*upVector)
    numJoints = len(joints)

    for i in range(numJoints):
        curJnt = joints[i]
        currentJntVector = getWorldVector(curJnt)

        if not i == (numJoints-1):
            nextJnt = joints[i+1]
            nextJntVector = getWorldVector(nextJnt)

            aimVector = nextJntVector - currentJntVector
            otherVector = aimVector ^ upVector
            upVector = otherVector ^ aimVector

            aimVector.normalize()
            upVector.normalize()
            otherVector.normalize()

            jntMatrix = [
                aimVector.x, aimVector.y, aimVector.z, 0.0,
                upVector.x, upVector.y, upVector.z, 0.0,
                otherVector.x, otherVector.y, otherVector.z, 0.0,
                currentJntVector.x, currentJntVector.y, currentJntVector.z, 1.0
            ]
        else :  # End joint uses previous joint data except for translation
            jntMatrix[12] = currentJntVector.x
            jntMatrix[13] = currentJntVector.y
            jntMatrix[14] = currentJntVector.z

        cmds.xform(curJnt, matrix=jntMatrix, ws=True)

def orientJointsUpObj(joints, upObject):
    upObjVector = getWorldVector(upObject)
    numJoints = len(joints)

    for i in range(numJoints):
        curJnt = joints[i]
        currentJntVector = getWorldVector(curJnt)

        if not i == (numJoints-1):
            nextJnt = joints[i+1]

            nextJntVector = getWorldVector(nextJnt)
            rawUpVector = upObjVector - currentJntVector

            aimVector = nextJntVector - currentJntVector
            otherVector = aimVector ^ rawUpVector
            upVector = otherVector ^ aimVector

            aimVector.normalize()
            upVector.normalize()
            otherVector.normalize()

            jntMatrix = [
                aimVector.x, aimVector.y, aimVector.z, 0.0,
                upVector.x, upVector.y, upVector.z, 0.0,
                otherVector.x, otherVector.y, otherVector.z, 0.0,
                currentJntVector.x, currentJntVector.y, currentJntVector.z, 1.0
            ]
        else :  # End joint uses previous joint data except for translation
            jntMatrix[12] = currentJntVector.x
            jntMatrix[13] = currentJntVector.y
            jntMatrix[14] = currentJntVector.z

        cmds.xform(curJnt, matrix=jntMatrix, ws=True)

def getDagPath(nodeName):
    dagPath = om.MDagPath()

    sels = om.MSelectionList()
    sels.add(nodeName)

    sels.getDagPath(0, dagPath)

    return dagPath

def getNurbsCurveFn(curve):
    crvFn = None

    crvDagPath = getDagPath(curve)
    if crvDagPath.hasFn(om.MFn.kTransform):
        crvDagPath.extendToShape()
        if crvDagPath.hasFn(om.MFn.kNurbsCurve):
            crvFn = om.MFnNurbsCurve(crvDagPath)
    elif crvDagPath.hasFn(om.MFn.kNurbsCurve):
        crvFn = om.MFnNurbsCurve(crvDagPath)

    return crvFn

def getWorldVector(obj):
    vector = om.MVector()

    translation = cmds.xform(obj, q=True, t=True, ws=True)
    vector = om.MVector(*translation)

    return vector

def getWorldPoint(obj):
    point = om.MPoint()

    translation = cmds.xform(obj, q=True, t=True, ws=True)
    point = om.MPoint(*translation)

    return point

def getParent(obj):
    parent = None

    parents = cmds.listRelatives(obj, parent=True)
    if parents:
        parent = parents[0]

    return parent


def writePose(joints, poseName):
    """
    writePose(joints, 'skinPose')
    writePose(joints, 'buildPose')
    """
    removePose(joints, poseName)
    for jnt in joints:
        pm.addAttr(jnt, ln=poseName, at='matrix')
        poseMatrix = jnt.worldMatrix.get()
        jnt.attr(poseName).set(poseMatrix)

def removePose(joints, poseName):
    for jnt in joints:
        if jnt.hasAttr(poseName): pm.deleteAttr(jnt.attr(poseName))

def setPose(joints, poseName):
    for jnt in joints:
        if jnt.hasAttr(poseName):
            poseMatrix = jnt.attr(poseName).get()
            pm.xform(jnt, matrix=poseMatrix, ws=True)

def alignToWorld(joint, xVector, yVector, zVector):
    """
    jnt = pm.PyNode('Hip')
    alignToWorld(jnt, [0, -1, 0], [0, 0, 1], [-1, 0, 0])
    jnt = pm.PyNode('Shoulder')
    alignToWorld(jnt, [-1, 0, 0], [0, 0, 1], [0, 1, 0])
    """
    wrldPos = joint.getTranslation(space='world')
    mat = [
        xVector[0], xVector[1], xVector[2], 0,
        yVector[0], yVector[1], yVector[2], 0,
        zVector[0], zVector[1], zVector[2], 0,
        wrldPos[0], wrldPos[1], wrldPos[2], 1
    ]
    pm.xform(joint, matrix=mat, ws=True)

def matchControllerToPose(controller, fitJoint, poseName):
    """
    controller = pm.selected()[0]
    fitJoint = pm.PyNode(controller.strip('FK').rsplit('_R',1)[0])
    matchControllerToPose(controller, fitJoint, 'skinPose')
    """
    poseMatrix = fitJoint.attr(poseName).get()
    pm.xform(controller, matrix=poseMatrix, ws=True)
