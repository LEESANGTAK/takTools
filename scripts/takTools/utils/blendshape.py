import pymel.core as pm


def reConnectBlendTargets(blendShape, searchStr='old_', replaceStr=''):
    """
    Recreate blendshape with old blendshape targets and reconnect target drivers to new blendshape target weights.

    Args:
        blendShape (str): Old blendshape name
        searchStr (str, optional): Search string for old blendshape source transform. Defaults to 'old_'.
        replaceStr (str, optional): Replace string to new blendshape source transform. Defaults to ''.
    """
    blendShape = pm.PyNode(blendShape)
    targets = [target for target in pm.listAttr(blendShape.weight, ) if 'weight' not in target and pm.objExists(target)]
    if len(blendShape.connections(d=False, type='mesh')) > 1:
        oldBaseTransform = blendShape.getBaseObjects()[0].getParent(generations=2)
    else:
        oldBaseTransform = blendShape.getBaseObjects()[0].getParent()
    newBlendshape = pm.blendShape(targets, oldBaseTransform.replace(searchStr, replaceStr), frontOfChain=True, topologyCheck=False)[0]
    for target in targets:
        newBlendshape.attr(target).set(1)
        inputs = blendShape.attr(target).connections(plugs=True)
        if inputs:
            inputs[0] >> newBlendshape.attr(target)


def extractTargets(blendShape, geometry, searchStr='', replaceStr='', prefix='', suffix=''):
    bs = pm.PyNode(blendShape)
    geo = pm.PyNode(geometry)

    targets = pm.listAttr(bs.weight, multi=True)
    for target in targets:
        bs.attr(target).set(1)
        extractedTarget = pm.duplicate(geo, n=prefix + target.replace(searchStr, replaceStr) + suffix)[0]
        pm.parent(extractedTarget, world=True)
        bs.attr(target).set(0)


def setupBlendshapeOutput(name, blendshape):
    """
    Creates locator between blendshape and blend target inputs. And reconnect blend targets.
    This setup is useful for updating blendshape.

    :param name: Mesh name
    :type name: str
    :param blendshape: Blendshape name
    :type blendshape: str
    """
    bs = pm.PyNode(blendshape)
    outBS = pm.spaceLocator(n='{0}_outBS'.format(name))
    targets = pm.listAttr(bs.weight, multi=True)
    for target in targets:
        pm.addAttr(outBS, ln=target, at='double', min=0.0, max=1.0, keyable=True)
        targetInputs = bs.attr(target).inputs(plugs=True)
        outBS.attr(target) >> bs.attr(target)
        if targetInputs:
            targetInputs[0] >> outBS.attr(target)


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
        pm.blendShape(blendShapeName, e=True, ib=True, t=(baseName, targetIndex, inbetween, increment*(id+1)))


def getTargetIndex(blendShapeName, targetName):
    bs = pm.PyNode(blendShapeName)
    for index in bs.weightIndexList():
        if pm.aliasAttr('{}.w[{}]'.format(blendShapeName, index), q=True) == targetName:
            return index
    return -1


def connectExistingTargets(driverObject, blendShapes, targetSearch='', targetReplace=''):
    """
driverObject = 'facial_out_attrs'
blendShapes = ['body_BS', 'eye_BS']
bsUtil.connectExistingTargets(driverObject, blendShapes)
    """
    assert isinstance(blendShapes, list), 'Second argument should be a list of blend shapes.'
    driverObject = pm.PyNode(driverObject)
    blendShapes = [pm.PyNode(blendShape) for blendShape in blendShapes]
    for blendShape in blendShapes:
        bsTargets = pm.listAttr('{}.weight'.format(blendShape), multi=True)
        for bsTarget in bsTargets:
            driverAttr = bsTarget.replace(targetSearch, targetReplace)
            if driverObject.hasAttr(driverAttr):
                driverAttr = driverObject.attr(driverAttr)
                drivenAttr = blendShape.attr(bsTarget)
                bsTargetDriver = drivenAttr.inputs(plugs=True)
                if not bsTargetDriver or bsTargetDriver[0] != driverAttr:
                    driverAttr >> drivenAttr
