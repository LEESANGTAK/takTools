import json
from maya import cmds


def createSingleSkeleton(joints):
    jntInfo = getJntInfo(joints)
    engJnts = createEngineJnts(joints)
    buildHierarchy(engJnts)
    connectMatrix(jntInfo)


def getJntInfo(joints):
    parentInfo = []

    for jnt in joints:
        jntName = jnt if isinstance(jnt, str) else str(jnt)
        parent = cmds.listRelatives(jntName, parent=True) or []
        parentName = parent[0] if parent else ''
        parentInfo.append({'bndJnt': jntName,
                           'engJnt': 'eng_' + jntName,
                           'engJntParent': 'eng_' + parentName if parentName else ''})

    return parentInfo


def createEngineJnts(joints):
    newJnts = []

    for oldJnt in joints:
        oldName = oldJnt if isinstance(oldJnt, str) else str(oldJnt)
        newJnt = cmds.duplicate(oldName, name='eng_'+oldName, parentOnly=True)[0]
        newJnts.append(newJnt)

    return newJnts


def connectMatrix(jntInfo):
    for info in jntInfo:
        bndJnt = info['bndJnt']
        engJnt = info['engJnt']
        decMatrix = cmds.createNode('decomposeMatrix')
        try:
            cmds.connectAttr('{}.worldMatrix[0]'.format(bndJnt), '{}.inputMatrix'.format(decMatrix), force=True)
        except Exception:
            try:
                cmds.connectAttr('{}.matrix'.format(bndJnt), '{}.inputMatrix'.format(decMatrix), force=True)
            except Exception:
                pass
        try:
            cmds.connectAttr('{}.outputTranslate'.format(decMatrix), '{}.translate'.format(engJnt), force=True)
        except Exception:
            pass
        try:
            cmds.connectAttr('{}.outputRotate'.format(decMatrix), '{}.rotate'.format(engJnt), force=True)
        except Exception:
            pass


def buildHierarchy(jntInfo):
    for info in jntInfo:
        try:
            info['engJntParent'] | info['engJnt']
        except:
            pass


def createAttachJoint(joint, name, convertToScene=True):
    """
    Create joint for attaching weapon, prop, etc...

    Arguments:
        joint {string} -- Source joint to create attach joint
        name {string} -- Attach joint name

    Keyword Arguments:
        convertToScene {bool} -- Import option state in unreal engine. (default: {True})

    Returns:
        Joint -- Attach joint object
    """
    attachJnt = None

    jointName = joint if isinstance(joint, str) else str(joint)
    parents = cmds.listRelatives(jointName, parent=True) or []
    jointParent = parents[0] if parents else None
    attachJnt = cmds.duplicate(jointName, parentOnly=True, name=name)[0]
    try:
        cmds.parent(attachJnt, world=True)
    except Exception:
        pass
    try:
        cmds.setAttr('{}.rotate'.format(attachJnt), 0, 0, 0)
    except Exception:
        pass
    try:
        cmds.setAttr('{}.jointOrient'.format(attachJnt), 0, 0, 0)
    except Exception:
        pass
    if convertToScene:
        try:
            cmds.setAttr('{}.rotateX'.format(attachJnt), -90)
        except Exception:
            pass
    if jointParent:
        try:
            cmds.parent(attachJnt, jointParent)
        except Exception:
            pass

    return attachJnt


def createRootJoint(name='Root', convertToScene=True):
    rootJoint = cmds.createNode('joint', name=name)
    if convertToScene:
        try:
            cmds.setAttr('{}.rotateX'.format(rootJoint), -90)
        except Exception:
            pass


def setupJointScaledVis(meshes, drivingJoints, controller, attribute):
    """
    attr = 'default'

    sels = cmds.ls(sl=True)
    joints = cmds.ls(sl=True, type='joint')
    meshes = list(set(sels) - set(joints))
    ctrl = 'EyeLeft_Blend'
    utils.setupJointScaledVis(meshes, joints, ctrl, attr)


    sels = cmds.ls(sl=True)
    joints = cmds.ls(sl=True, type='joint')
    meshes = list(set(sels) - set(joints))
    ctrl = 'EyeRight_Blend'
    utils.setupJointScaledVis(meshes, joints, ctrl, attr)
    """
    drvJnts = [drvJnt if isinstance(drvJnt, str) else str(drvJnt) for drvJnt in drivingJoints]
    ctrl = controller if isinstance(controller, str) else str(controller)

    # Create subJoints
    subJoints = []
    for drvJnt in drvJnts:
        subJnt = cmds.duplicate(drvJnt, name='{}_{}'.format(drvJnt, attribute), parentOnly=True)[0]
        try:
            cmds.setAttr('{}.segmentScaleCompensate'.format(subJnt), False)
        except Exception:
            pass
        try:
            cmds.parent(subJnt, drvJnt)
        except Exception:
            pass
        subJoints.append(subJnt)

    # Bind meshes with subJoints
    for mesh in meshes:
        try:
            cmds.skinCluster(subJoints, mesh, tsb=True, bindMethod=0, maximumInfluences=1, dropoffRate=4.0, omi=False)
        except Exception:
            try:
                cmds.skinCluster(subJoints, mesh, tsb=True, bm=0, wd=0, omi=False, mi=1, dr=4.0)
            except Exception:
                pass

    # Clamp attribute value to prevent zero value
    clamp = cmds.createNode('clamp', name='{}_{}_clamp'.format(drvJnt, attribute))
    try:
        cmds.setAttr('{}.minR'.format(clamp), 0.001)
        cmds.setAttr('{}.minG'.format(clamp), 0.001)
        cmds.setAttr('{}.minB'.format(clamp), 0.001)
        cmds.setAttr('{}.maxR'.format(clamp), 1.0)
        cmds.setAttr('{}.maxG'.format(clamp), 1.0)
        cmds.setAttr('{}.maxB'.format(clamp), 1.0)
    except Exception:
        pass
    try:
        cmds.connectAttr('{}.{}'.format(ctrl, attribute), '{}.inputR'.format(clamp), force=True)
        cmds.connectAttr('{}.{}'.format(ctrl, attribute), '{}.inputG'.format(clamp), force=True)
        cmds.connectAttr('{}.{}'.format(ctrl, attribute), '{}.inputB'.format(clamp), force=True)
    except Exception:
        pass

    # Connect clamped value to sub joints scale
    for subJnt in subJoints:
        try:
            cmds.connectAttr('{}.outputR'.format(clamp), '{}.scaleX'.format(subJnt), force=True)
            cmds.connectAttr('{}.outputG'.format(clamp), '{}.scaleY'.format(subJnt), force=True)
            cmds.connectAttr('{}.outputB'.format(clamp), '{}.scaleZ'.format(subJnt), force=True)
        except Exception:
            pass


def publishCustomAttrs(sourceNode, attrPrefix, skeletonRoot, sourceAttrs=[]):
    """
    sourceNode = 'FKEyeball_R'
    attrPrefix = 'Eye_R_'
    skeletonRoot = 'root'
    uUtil.publishCustomAttrs(sourceNode, attrPrefix, skeletonRoot)
    """
    src = sourceNode if isinstance(sourceNode, str) else str(sourceNode)
    skRoot = skeletonRoot if isinstance(skeletonRoot, str) else str(skeletonRoot)

    if not sourceAttrs:
        sourceAttrs = cmds.listAttr(src, userDefined=True) or []
    try:
        cmds.undoInfo(openChunk=True)
    except Exception:
        pass
    for srcAttr in sourceAttrs:
        pubAttr = attrPrefix + srcAttr
        try:
            cmds.addAttr(skRoot, longName=pubAttr, attributeType='double', keyable=True)
        except Exception:
            try:
                cmds.addAttr(skRoot, ln=pubAttr, at='double', keyable=True)
            except Exception:
                pass
        try:
            cmds.connectAttr('{}.{}'.format(src, srcAttr), '{}.{}'.format(skRoot, pubAttr), force=True)
        except Exception:
            pass
    try:
        cmds.undoInfo(closeChunk=True)
    except Exception:
        pass


def connectToUESkeleton(maSkeletonRoot, ueSkeletonRoot, forceFrontXAxis=False):
    """
    from takTools.utils import unreal as ueUtil; reload(ueUtil)

    sels = cmds.ls(sl=True)
    maSkelRoot = sels[0]
    ueSkelRoot = sels[1]
    ueUtil.connectToUESkeleton(maSkelRoot, ueSkelRoot)
    """
    maJnts = cmds.ls(maSkeletonRoot, dag=True, type="joint") or []
    ueJnts = cmds.ls(ueSkeletonRoot, dag=True, type="joint") or []

    for ueJnt, maJnt in zip(ueJnts, maJnts):
        try:
            ueJntWM = cmds.xform(ueJnt, q=True, matrix=True, worldSpace=True)
        except Exception:
            ueJntWM = None

        maJntWM = ueJntWM
        if forceFrontXAxis and ueJntWM:
            try:
                rows = [ueJntWM[0:4], ueJntWM[4:8], ueJntWM[8:12], ueJntWM[12:16]]
                newRows = [rows[1], rows[2], rows[0], rows[3]]
                maJntWM = [val for row in newRows for val in row]
            except Exception:
                maJntWM = ueJntWM

        if maJntWM:
            try:
                cmds.xform(maJnt, matrix=maJntWM, worldSpace=True)
            except Exception:
                pass

        try:
            cmds.parentConstraint(ueJnt, maJnt, maintainOffset=True)
        except Exception:
            pass
        try:
            cmds.scaleConstraint(ueJnt, maJnt, maintainOffset=True)
        except Exception:
            pass


def importMatrix(filePath):

    with open(filePath, "r") as f:
        data = json.load(f)

    fps = data["fps"]
    timeUnit = "film"
    if fps == 25:
        timeUnit = "pal"
    elif fps == 30:
        timeUnit = "ntsc"
    cmds.currentUnit(time=timeUnit)

    startFrame = data["startFrame"]
    endFrame = data["endFrame"]
    try:
        cmds.playbackOptions(min=startFrame)
        cmds.playbackOptions(max=endFrame)
    except Exception:
        pass

    try:
        cmds.refresh(suspend=True)
    except Exception:
        pass
    curFrame = cmds.currentTime(q=True)
    transf = cmds.createNode("transform", name=data["name"])
    for i in range(startFrame, endFrame+1):
        try:
            cmds.currentTime(i)
            cmds.xform(transf, matrix=data[str(i)], worldSpace=True)
            cmds.setKeyframe(transf)
        except Exception:
            pass
    try:
        cmds.currentTime(curFrame)
    except Exception:
        pass
    try:
        cmds.refresh(suspend=False)
    except Exception:
        pass
