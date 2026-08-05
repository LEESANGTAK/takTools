import maya.cmds as cmds


def reConnectBlendTargets(blendShape, searchStr='old_', replaceStr=''):
    """
    Recreate blendshape with old blendshape targets and reconnect target drivers to new blendshape target weights.

    Args:
        blendShape (str): Old blendshape name
        searchStr (str, optional): Search string for old blendshape source transform. Defaults to 'old_'.
        replaceStr (str, optional): Replace string to new blendshape source transform. Defaults to ''.
    """
    blendShape = str(blendShape)
    targets = [target for target in cmds.listAttr('{0}.weight'.format(blendShape), multi=True) or [] if 'weight' not in target and cmds.objExists(target)]
    geometry = cmds.blendShape(blendShape, q=True, geometry=True) or []
    if len(geometry) > 1:
        oldBaseTransform = cmds.listRelatives(geometry[0], parent=True, fullPath=False)[0]
    else:
        oldBaseTransform = cmds.listRelatives(geometry[0], parent=True, fullPath=False)[0]

    newBlendshape = cmds.blendShape(targets, oldBaseTransform.replace(searchStr, replaceStr), frontOfChain=True, topologyCheck=False)[0]
    for target in targets:
        cmds.setAttr('{0}.{1}'.format(newBlendshape, target), 1)
        inputs = cmds.listConnections('{0}.{1}'.format(blendShape, target), plugs=True, source=True, destination=False) or []
        if inputs:
            cmds.connectAttr(inputs[0], '{0}.{1}'.format(newBlendshape, target), force=True)


def extractTargets(blendShape, geometry, searchStr='', replaceStr='', prefix='', suffix=''):
    targets = cmds.listAttr('{0}.weight'.format(blendShape), multi=True) or []
    for target in targets:
        cmds.setAttr('{0}.{1}'.format(blendShape, target), 1)
        extractedTarget = cmds.duplicate(geometry, n=prefix + target.replace(searchStr, replaceStr) + suffix)[0]
        cmds.parent(extractedTarget, world=True)
        cmds.setAttr('{0}.{1}'.format(blendShape, target), 0)


def setupBlendshapeOutput(name, blendshape):
    """
    Creates locator between blendshape and blend target inputs. And reconnect blend targets.
    This setup is useful for updating blendshape.

    :param name: Mesh name
    :type name: str
    :param blendshape: Blendshape name
    :type blendshape: str
    """
    outBS = cmds.spaceLocator(n='{0}_outBS'.format(name))[0]
    targets = cmds.listAttr('{0}.weight'.format(blendshape), multi=True) or []
    for target in targets:
        cmds.addAttr(outBS, ln=target, at='double', min=0.0, max=1.0, keyable=True)
        targetInputs = cmds.listConnections('{0}.{1}'.format(blendshape, target), plugs=True, source=True, destination=False) or []
        cmds.connectAttr('{0}.{1}'.format(outBS, target), '{0}.{1}'.format(blendshape, target), force=True)
        if targetInputs:
            cmds.connectAttr(targetInputs[0], '{0}.{1}'.format(outBS, target), force=True)


def addInbetweensInOrder(blendShapeName, targetName, inbetweens, baseName):
    """
    blendShapeName = 'Eyelid_BS'
    targetName = 'Eyelid_Blink1_R'
    inbetweens = cmds.ls(os=True)
    baseName = 'Eye_Geo_Grp'
    bsUtil.addInbetweensInOrder(blendShapeName, targetName, inbetweens, baseName)
    """
    increment = 1.0/(len(inbetweens)+1)
    targetIndex = getTargetIndex(blendShapeName, targetName)
    for id, inbetween in enumerate(inbetweens):
        cmds.blendShape(blendShapeName, e=True, ib=True, t=(baseName, targetIndex, inbetween, increment*(id+1)))


def getTargetIndex(blendShapeName, targetName):
    for index in range(1000):
        alias = cmds.aliasAttr('{}.w[{}]'.format(blendShapeName, index), q=True)
        if alias == targetName:
            return index
        if not alias:
            break
    return -1


def connectExistingTargets(driverObject, blendShapes, targetSearch='', targetReplace=''):
    """
driverObject = 'facial_out_attrs'
blendShapes = ['body_BS', 'eye_BS']
bsUtil.connectExistingTargets(driverObject, blendShapes)
    """
    assert isinstance(blendShapes, list), 'Second argument should be a list of blend shapes.'
    driverObject = str(driverObject)
    for blendShape in blendShapes:
        blendShape = str(blendShape)
        bsTargets = cmds.listAttr('{}.weight'.format(blendShape), multi=True) or []
        for bsTarget in bsTargets:
            driverAttr = bsTarget.replace(targetSearch, targetReplace)
            if cmds.attributeQuery(driverAttr, node=driverObject, exists=True):
                drivenAttr = '{0}.{1}'.format(blendShape, bsTarget)
                driverPlug = '{0}.{1}'.format(driverObject, driverAttr)
                currentInputs = cmds.listConnections(drivenAttr, plugs=True, source=True, destination=False) or []
                if not currentInputs or currentInputs[0] != driverPlug:
                    cmds.connectAttr(driverPlug, drivenAttr, force=True)
