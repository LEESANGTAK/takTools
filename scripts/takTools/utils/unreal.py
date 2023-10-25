import pymel.core as pm


def createSingleSkeleton(joints):
    jntInfo = getJntInfo(joints)
    engJnts = createEngineJnts(joints)
    buildHierarchy(engJnts)
    connectMatrix(jntInfo)


def getJntInfo(joints):
    parentInfo = []

    for jnt in joints:
        parentInfo.append({'bndJnt':          jnt,
                           'engJnt':          'eng_'+jnt.name(),
                           'engJntParent':    'eng_'+jnt.getParent(),
                           }
                          )

    return parentInfo


def createEngineJnts(joints):
    newJnts = []

    for oldJnt in joints:
        newJnt = oldJnt.duplicate(n='eng_'+oldJnt.name(), parentOnly=True)[0]
        newJnts.append(newJnt)

    return newJnts


def connectMatrix(jntInfo):
    for info in jntInfo:
        bndJnt = pm.PyNode(info['bndJnt'])
        engJnt = pm.PyNode(info['engJnt'])
        decMatrix = pm.createNode('decomposeMatrix')

        bndJnt.matrix >> decMatrix.inputMatrix
        decMatrix.outputTranslate >> engJnt.translate
        decMatrix.outputRotate >> engJnt.rotate


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
        pm.nodetypes.Joint -- Attach joint pymel object
    """
    attachJnt = None

    joint = pm.PyNode(joint)

    jointParent = joint.getParent()
    attachJnt = pm.duplicate(joint, po=True, n=name)[0]
    pm.parent(attachJnt, world=True)

    attachJnt.rotate.set(0, 0, 0)
    attachJnt.jointOrient.set(0, 0, 0)
    if convertToScene:
        attachJnt.rotateX.set(-90)

    if jointParent:
        pm.parent(attachJnt, jointParent)

    return attachJnt


def createRootJoint(name='Root', convertToScene=True):
    rootJoint = pm.createNode('joint', n=name)
    if convertToScene:
        rootJoint.rotateX.set(-90)


def setupJointScaledVis(meshes, drivingJoints, controller, attribute):
    """
    attr = 'default'

    sels = pm.selected()
    joints = pm.selected(type='joint')
    meshes = list(set(sels) - set(joints))
    ctrl = 'EyeLeft_Blend'
    utils.setupJointScaledVis(meshes, joints, ctrl, attr)


    sels = pm.selected()
    joints = pm.selected(type='joint')
    meshes = list(set(sels) - set(joints))
    ctrl = 'EyeRight_Blend'
    utils.setupJointScaledVis(meshes, joints, ctrl, attr)
    """
    drvJnts = [pm.PyNode(drvJnt) for drvJnt in drivingJoints]
    ctrl = pm.PyNode(controller)

    # Create subJoints
    subJoints = []
    for drvJnt in drvJnts:
        subJnt = pm.duplicate(drvJnt, n='{}_{}'.format(drvJnt, attribute), po=True)[0]
        subJnt.segmentScaleCompensate.set(False)
        drvJnt | subJnt
        subJoints.append(subJnt)

    # Bind meshes with subJoints
    for mesh in meshes:
        pm.skinCluster(subJoints, mesh, tsb=True, bm=0, wd=0, omi=False, mi=1, dr=4.0)

    # Clamp attribute value to prevent zero value
    clamp = pm.createNode('clamp', n='{}_{}_clamp'.format(drvJnt, attribute))
    clamp.minR.set(0.001)
    clamp.minG.set(0.001)
    clamp.minB.set(0.001)
    clamp.maxR.set(1.0)
    clamp.maxG.set(1.0)
    clamp.maxB.set(1.0)
    ctrl.attr(attribute) >> clamp.inputR
    ctrl.attr(attribute) >> clamp.inputG
    ctrl.attr(attribute) >> clamp.inputB

    # Connect clamped value to sub joints scale
    for subJnt in subJoints:
        clamp.outputR >> subJnt.scaleX
        clamp.outputG >> subJnt.scaleY
        clamp.outputB >> subJnt.scaleZ


def publishCustomAttrs(sourceNode, attrPrefix, skeletonRoot, sourceAttrs=[]):
    """
    sourceNode = 'FKEyeball_R'
    attrPrefix = 'Eye_R_'
    skeletonRoot = 'root'
    uUtil.publishCustomAttrs(sourceNode, attrPrefix, skeletonRoot)
    """
    sourceNode = pm.PyNode(sourceNode)
    skeletonRoot = pm.PyNode(skeletonRoot)

    if not sourceAttrs:  # If no sourceAttrs given sourceAttrs is user defined
        sourceAttrs = [attr.attrName() for attr in sourceNode.listAttr(ud=True)]

    pm.undoInfo(openChunk=True)
    for srcAttr in sourceAttrs:
        pubAttr = attrPrefix + srcAttr
        pm.addAttr(skeletonRoot, ln=pubAttr, at='double', keyable=True)
        sourceNode.attr(srcAttr) >> skeletonRoot.attr(pubAttr)
    pm.undoInfo(closeChunk=True)
