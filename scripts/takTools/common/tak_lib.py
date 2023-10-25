'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 07/29/2015

Description:
This module is collection of functions in common usage.
'''
import os
import pprint
import re

import maya.OpenMaya as OpenMaya
import maya.api.OpenMaya as om2
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


def showHUD(widgetName, title, sectionNum = 2, blockNum = 0):
    '''
    This function find available block and display hud.
    '''

    allHuds = cmds.headsUpDisplay(listHeadsUpDisplays = True)

    hudsInSection = []
    for hud in allHuds:
        if cmds.headsUpDisplay(hud, q = True, s = True) == sectionNum:
            hudsInSection.append(hud)

    if hudsInSection:
        invalidBlocks = []
        for hud in hudsInSection:
            invalidBlock = cmds.headsUpDisplay(hud, q = True, b = True)
            invalidBlocks.append(invalidBlock)

        blockNum = max(invalidBlocks) + 1

    cmds.headsUpDisplay(widgetName, s = sectionNum, b = blockNum, blockSize = 'medium', label = title, labelFontSize = 'large')


def loadSel(wdgType, wdgName, *args):
    '''
    Fill the text field with selected object.
    '''

    sel = cmds.ls(sl = True)[0]

    eval('cmds.%s("%s", e = True, text = sel)' %(wdgType, wdgName))


def populateTxtScrList(wdgType, wdgName, *args):
    '''
    Description:
    Populate text scroll list with selected objects.

    Arguments:
    wdgType(string), wdgName(string)

    Returns:
    Nothing
    '''

    selList = cmds.ls(sl = True, fl = True)

    items = eval('cmds.%s("%s", q = True, allItems = True)' %(wdgType, wdgName))
    if items:
        eval('cmds.%s("%s", e = True, removeAll = True)' %(wdgType, wdgName))

    eval('cmds.%s("%s", e = True, append = %s)' %(wdgType, wdgName, selList))


def matchConSel(driver, driven):
    '''
    Match curve shape of target to source.
    Select source and then target.
    '''

    # get number of cvs of source
    degs = cmds.getAttr('%s.degree' %driver)
    spans = cmds.getAttr('%s.spans' %driver)
    cvs = degs + spans

    for i in range(cvs):
        # get worldspace translate value of each cv
        cvTr = cmds.xform('%s.cv[%d]' %(driver, i), q = True, t = True, ws = True)

        # set opposite control's cvs
        cmds.xform('%s.cv[%d]' %(driven, i), t = (cvTr[0], cvTr[1], cvTr[2]), ws = True)


def parentShpInPlace(src, trg):
    '''
    Parent source transform's shape to target transform node with no transition of the shape.
    '''

    # Keep source object for match target's shape
    srcTmp = cmds.duplicate(src, n = src + '_tmp')[0]

    # Get source object's shape
    srcShp = cmds.listRelatives(src, s = True)[0]

    # Parent shape to the target transform node
    cmds.parent(srcShp, trg, s = True, r = True)

    # Match shape with source object
    matchConSel(srcTmp, trg)

    cmds.delete(srcTmp)


def getAllDeformers(geo):
    '''
    Description:
        Retrive all deformers assigned to the geometry.

    Arguments:
        geo (str): Geometry name.

    Returns:
        deformers (list<str>): List of deformer names.
    '''

    MAYA_VERSION = int(cmds.about(version=True))

    if MAYA_VERSION >= 2022:
        DEFORMER_TYPES = ['skinCluster', 'blendShape', 'cluster', 'ffd', 'wrap', 'nonLinear', 'sculpt', 'softMod', 'jiggle', 'wire']
        deformers = cmds.ls(cmds.listHistory(geo), type=['skinCluster', 'blendShape'])
        return deformers
    else:
        allDfmSets = cmds.listSets(object=geo, type=2, extendToShape=True)
        if allDfmSets:
            deformers = [cmds.listConnections(x + '.usedBy')[0] for x in allDfmSets if not 'tweak' in x]
            return deformers

    return None


def setAllDefEnvlope(geo, envVal):
    '''
    Description:
        All deformers that associate with geometry set envelope to 0 or 1.

    Arguments:
        geo(string), Geometry name.
        envVal(integer), Envelope value of deformer.

    Returns:
        None
    '''

    hierMeshLs = cmds.listRelatives(geo, ad = True, type = 'mesh', path=True)

    deformerTypeLs = ['skinCluster', 'blendShape', 'cluster', 'ffd', 'wrap', 'nonLinear', 'sculpt', 'softMod', 'jiggle', 'wire']
    deformerLs = []

    if hierMeshLs:
        for mesh in hierMeshLs:
            allConnections = cmds.listHistory(mesh)
            for deformerType in deformerTypeLs:
                findDeformer = cmds.ls(allConnections, type = deformerType)
                if findDeformer:
                    deformerLs.extend(findDeformer)

        for dfm in deformerLs:
            cmds.setAttr(dfm + '.envelope', envVal)


def isUniqeName(obj):
    '''
    Description:
    Check given object is uniqe or not.

    Arguments:
    obj(string)

    Returns:
    True/False
    '''

    if len(cmds.ls(obj)) == 1:
        return True
    else:
        return False


def getMatFromSel(obj):
    """ Get material From selected object """

    shapeName = cmds.listRelatives(obj, ni=True, path=True, s=True)

    if shapeName:
        sgName = cmds.listConnections(shapeName[0], d=True, type="shadingEngine")
        matName = [mat for mat in cmds.ls(cmds.listConnections(sgName), materials=True) if not cmds.nodeType(mat) == 'displacementShader']

        return list(set(matName))


def getSelAttrsNiceName():
    '''
    Get nice name of selected attributes in channelbox.
    '''

    sel = cmds.ls(sl = True)[-1]

    rawSelAttrs = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
    niceSelAttrs = []

    if rawSelAttrs:
        for rawAttr in rawSelAttrs:
            niceSelAttrs.append(cmds.attributeQuery(rawAttr, longName = True, node = sel))
        return niceSelAttrs
    else:
        return None


def findShadingEngine(startNode):
    destinationNodes = cmds.listConnections(startNode, s = False, scn = True)

    resultShadingEngine = ''

    if destinationNodes:
        for node in destinationNodes:
            if cmds.nodeType(node) == 'shadingEngine':
                resultShadingEngine = node
            else:
                pass

        if resultShadingEngine:
            return resultShadingEngine
        else:
            for node in destinationNodes:
                result = findShadingEngine(node)
                if result:
                    return result


def unlockChannelBoxAttr(transformNode):
    mel.eval('source channelBoxCommand;')

    attrList = ['translate', 'rotate', 'scale']
    axisList = ['X', 'Y', 'Z']

    for attr in attrList:
        for axis in axisList:
            cmds.setAttr('%s.%s%s' %(transformNode, attr, axis), keyable = True)
            mel.eval('CBunlockAttr "%s.%s%s";' %(transformNode, attr, axis))

    cmds.setAttr('%s.visibility' %transformNode, keyable = True)
    mel.eval('CBunlockAttr "%s.visibility";' %transformNode)


def loadPath(wdgName):
    '''
    Fill folder path textFieldGrp.
    '''
    curScenePath = cmds.file(q = True, sceneName = True)
    curWorkDir = os.path.dirname(curScenePath)
    fldrPath = cmds.fileDialog2(dialogStyle = 1, fileMode = 2, startingDirectory = curWorkDir)[0]
    cmds.textFieldButtonGrp(wdgName, e = True, text = fldrPath)


def rmvEndInt(name):
    '''
    Remove integer that end of the name.
    '''

    newName = re.sub(r"(\d+)$", r"", name)
    cmds.rename(name, newName)

    return newName


def printLs(parm_list):
    for item in parm_list:
        print(item)


def getOverlappedVertices(source, target, searchRadius=5.0):
    '''
    Description
        Get overlapped target mesh's vertices from source mesh.

    Retruns
        closestVtxs: string list - Target mesh's closest vertices.
    '''

    selLs = om2.MSelectionList()
    selLs.add(source)
    selLs.add(target)

    srcDagPath = selLs.getDagPath(0)
    trgDagPath = selLs.getDagPath(1)

    trgVtxIt = om2.MItMeshVertex(trgDagPath)

    srcMeshFn = om2.MFnMesh(srcDagPath)

    overlappedVerticesId = []
    while not trgVtxIt.isDone():
        trgVtxWsPnt = trgVtxIt.position(om2.MSpace.kWorld)
        trgVtxNormal = trgVtxIt.getNormal()

        intersectPoint = srcMeshFn.closestIntersection(
            om2.MFloatPoint(trgVtxWsPnt),
            om2.MFloatVector(trgVtxNormal),
            om2.MSpace.kWorld,
            searchRadius,
            True
        )[0]

        if not intersectPoint.isEquivalent(om2.MFloatPoint(0, 0, 0, 1)):
            overlappedVerticesId.append(trgVtxIt.index())

        trgVtxIt.next()

    # Get vertices name.
    trgDagPathFullName = trgDagPath.fullPathName()
    overlappedVertices = []
    for vtxId in overlappedVerticesId:
        vtxName = trgDagPathFullName + '.vtx[' + str(vtxId) + ']'
        overlappedVertices.append(vtxName)

    return overlappedVertices


def rmvRepeatItem(parm_list):
    """ Remove repeated item in the given list """
    return list(set(parm_list))


def findMultiAttributeEmptyIndex(node, attribute):
    """
    Find available index of multi attribute
    Args:
        node: Node or node name
        attribute (string): Attribute name

    Returns:
        Available index
    """
    node = pm.PyNode(node)

    id = 0

    while node.attr(attribute)[id].isConnected():
        id += 1

    return id


def searchMethods(obj, *args):
    """
    Print out methods that includes all search strings

    Args:
        obj: Object
        *args: Search strings. Not case sensitive

    Examples:
        tak_lib.searchMethods(obj, 'get', 'name')
    """
    methods = dir(obj)
    origMethods = methods

    for searchStr in args:
        methods = [method for method in methods if re.search(searchStr, method, re.IGNORECASE)]

    if origMethods == methods or not methods:
        print('Not found')
    else:
        pprint.pprint(methods)


def searchAttributes(obj, *args):
    """
    Print out methods that includes all search strings

    Args:
        obj: Object
        *args: Search strings. Not case sensitive

    Examples:
        tak_lib.searchAttributes(obj, 'get', 'name')
    """
    attributes = obj.listAttr()
    origAttributes = attributes

    for searchStr in args:
        attributes = [attr for attr in attributes if re.search(searchStr, attr.name(), re.IGNORECASE)]

    if origAttributes == attributes or not attributes:
        print('Not found')
    else:
        pprint.pprint(attributes)


def getMDagPath(node):
    """
    Args:
        node(str): Node name

    Returns:
        MDagPath
    """
    mSelLs = OpenMaya.MSelectionList()
    mSelLs.add(node)

    mDagPath = OpenMaya.MDagPath()

    mSelLs.getDagPath(0, mDagPath)

    return mDagPath


def swapOrderString(type="number"):
    """
    Swap ordered string for selected two objects.

    Parameters:
        type(str): Order string type. Available type is 'number' or 'alphabet'.
    """
    firstOrderStr = None
    secOrderStr = None

    sels = pm.selected()
    if type == "number":
        firstOrderStr = re.search(r"_(\d+)_", sels[0].name()).group(1)
        secOrderStr = re.search(r"_(\d+)_", sels[1].name()).group(1)
    elif type == "alphabet":
        firstOrderStr = re.search(r"_(\D)_", sels[0].name()).group(1)
        secOrderStr = re.search(r"_(\D)_", sels[1].name()).group(1)

    sels[0].rename(sels[0].replace(firstOrderStr, "tempStr"))
    sels[1].rename(sels[1].replace(secOrderStr, firstOrderStr))
    sels[0].rename(sels[0].replace("tempStr", secOrderStr))


def matchTransformToFace(transform, face):
    """
    transform(pymel.core.nodetypes.Transform): Transform pymel node
    face(pymel.core.general.MeshFace): A face

    Example:
        import pymel.core as pm

        sels = pm.ls(os=True) # Select transform and a face
        matchTransformToFace(sels[0], sels[1])
    """
    points = face.getPoints()

    # Vectors for build matrix
    vectorX = points[1] - points[0]
    vectorX.normalize()
    vectorY = face.getNormal()
    vectorZ = vectorX ^ vectorY
    position = pm.datatypes.Vector()
    for point in points:
        position += point
    position = position/len(points)

    # Build matrix
    matrixData = [[vectorX.x, vectorX.y, vectorX.z, 0],
                    [vectorY.x, vectorY.y, vectorY.z, 0],
                    [vectorZ.x, vectorZ.y, vectorZ.z, 0],
                    [position.x, position.y, position.z, 1]]
    matrix = pm.datatypes.Matrix(matrixData)

    transform.setMatrix(matrix)


def getInputNodes(start, inputNodes, nodeType=None):
    """
    Parameters:
        start<str>: Node or Node.Attribute name
        inputNodes<list>: Empty list
        nodeType<str>: Specific node type
    """
    startNode = pm.PyNode(start)
    nodes = startNode.connections(d=False, scn=True)
    if nodes:
        for node in nodes:
            if nodeType:
                if node.type() == nodeType:
                    inputNodes.append(node)
            else:
                inputNodes.append(node)
            getInputNodes(str(node), inputNodes, nodeType)

    return sorted(list(set(inputNodes)), key=type)


def duplicateRename(node, prefix='', suffix='', srchStr='', rplcStr=''):
    addStrDupNode = pm.duplicate(node, n=prefix + node + suffix, returnRootsOnly=True)[0]
    subStrDupNodeName = re.sub(srchStr, rplcStr, addStrDupNode.name())
    dupNode = cmds.rename(addStrDupNode.name(), subStrDupNodeName)

    try:
        pm.parent(dupNode, world=True)
    except:
        pass

    dupObjChldLs = pm.listRelatives(dupNode, type='transform', ad=True, path=True)
    if dupObjChldLs:
        for chldObj in dupObjChldLs:
            chldObjBaseName = chldObj.split('|')[-1]
            addName = cmds.rename(chldObj.name(), prefix + chldObjBaseName + suffix)
            subName = re.sub(srchStr, rplcStr, addName)
            cmds.rename(addName, subName)

    return pm.PyNode(dupNode)


def setDefaultTransform(transformNode):
    attrs = ['translate', 'rotate', 'scale']
    axises = ["X", "Y", "Z"]
    for attr in attrs:
        for axis in axises:
            transformNode.attr(attr+axis).set(1) if attr == 'scale' else transformNode.attr(attr+axis).set(0)


def deleteIntermediateObject(transformNode):
    itmdShapes = pm.ls(transformNode, dag=True, s=True, io=True)
    for shape in itmdShapes:
        if shape.intermediateObject.get():
            pm.delete(shape)


def copySkinByName(target, prefix="", srchStr="", rplcStr="", copyMatOpt=False):
    """
    Copy skined source geometry/group to destination geometry/group by matching name.

    Parameters:
        target: string, Destination geometry or group.
        prefix: string, Prefix attached to source.
        srchStr: string, Search string on destination.
        rplcStr: string, Replace string for source.
        copyMatOpt: boolean, Copy material option.

    Returns:
        None

    Examples:
        tak_lib.copySkinByName(target='lod02_GRP', srchStr='lod02_', rplcStr='old_lod02_', copyMatOpt=False)
        tak_lib.copySkinByName(target='temp_lod02_hair_bottom', srchStr='temp_', rplcStr='')
        tak_lib.copySkinByName(target='lod03_GRP', prefix='photoBook_001:') # Copy skin 'photoBook_001:lod03_GRP -> lod03_GRP'.
        tak_lib.copySkinByName(target='lod02_GRP', prefix='old_', copyMatOpt=True) # Copy skin and material 'old_lod02_GRP -> lod02_GRP.'
    """

    dstGeos = [x for x in cmds.listRelatives(target, ad=True, type='shape') if not cmds.getAttr(x + '.intermediateObject')]

    nonMatchGeos = []

    for dstGeo in dstGeos:
        srcGeo = prefix + re.sub(srchStr, rplcStr, dstGeo)

        print(">>> Source Geometry: " + srcGeo)
        print(">>> Destination Geometry: " + dstGeo)

        if cmds.objExists(srcGeo):
            copySkin(srcGeo, dstGeo)
            if copyMatOpt: copyMat()
        else:
            nonMatchGeos.append(dstGeo)

    if nonMatchGeos:
        cmds.select(nonMatchGeos, r=True)
        OpenMaya.MGlobal.displayWarning("Selected geometries didn't found matching source geometry.")
    else:
        cmds.select(cl=True)
        OpenMaya.MGlobal.displayInfo('All geometries copied skin successfully.')


def copySkin(source, target):
    source = pm.PyNode(source)
    target = pm.PyNode(target)

    srcInfs = getInfluences(source)
    srcJointInfs = [inf for inf in srcInfs if isinstance(inf, pm.nodetypes.Joint)]
    srcGeoInfs = list(set(srcInfs) - set(srcJointInfs))
    srcSkinClst = pm.mel.eval('findRelatedSkinCluster("%s");' % source.name())
    targetMesh = target.node() if isinstance(target, pm.MeshVertex) else target
    trgSkinClst = pm.mel.eval('findRelatedSkinCluster("%s");' % targetMesh.name())

    if not trgSkinClst:
        trgSkinClst = pm.skinCluster(srcJointInfs, targetMesh, dr=4, tsb=True, nw=1)
        pm.skinCluster(trgSkinClst, e=True, ug=True, ai=srcGeoInfs)

    else:
        trgInfs = getInfluences(targetMesh)
        trgJointInfs = [inf for inf in trgInfs if isinstance(inf, pm.nodetypes.Joint)]
        trgGeoInfs = list(set(trgInfs) - set(trgJointInfs))
        addedSrcJointInfs = list(set(srcJointInfs) - set(trgJointInfs))
        addedSrcGeoInfs = list(set(srcGeoInfs) - set(trgGeoInfs))

        pm.skinCluster(trgSkinClst, e=True, ai=addedSrcJointInfs)
        pm.skinCluster(trgSkinClst, e=True, ug=True, ai=addedSrcGeoInfs)

    pm.select(source, target, r=True)
    cmds.CopySkinWeights()

    pm.PyNode(trgSkinClst).skinningMethod.set(pm.PyNode(srcSkinClst).skinningMethod.get())
    pm.PyNode(trgSkinClst).useComponents.set(pm.PyNode(srcSkinClst).useComponents.get())


def copyMat(source, target):
    srcShape = source.getShape()
    trgShape = target.getShape()
    srcShadingGrp = srcShape.listConnections(s=False, type='shadingEngine')[0]
    pm.sets(srcShadingGrp, forceElement=trgShape)


def getInfluences(skinGeo):
    skClu = pm.mel.eval('findRelatedSkinCluster("%s");' % skinGeo)
    infls = pm.skinCluster(skClu, q=True, inf=True)
    return infls


def constraintWithMatrix(driver, driven, maintainOffset=True, translateAxes=['x','y','z'], rotateAxes=['x','y','z'], scaleAxes=[]):
    driver = pm.PyNode(driver)
    driven = pm.PyNode(driven)

    multMtx = pm.createNode('multMatrix', n=driver.name()+'_multMtx')
    decMtx = pm.createNode('decomposeMatrix', n=driver.name()+'_decMtx')

    if maintainOffset:
        offsetMtx = driven.worldMatrix.get() * driver.worldInverseMatrix.get()  # Parent to driver
        multMtx.matrixIn[0].set(offsetMtx)
        driver.worldMatrix >> multMtx.matrixIn[1]
        if driven.getParent(): driven.getParent().worldInverseMatrix >> multMtx.matrixIn[2]
    else:
        driver.worldMatrix >> multMtx.matrixIn[0]
        if driven.getParent(): driven.getParent().worldInverseMatrix >> multMtx.matrixIn[1]

    multMtx.matrixSum >> decMtx.inputMatrix

    for axis in translateAxes:
        decMtx.attr('outputTranslate'+axis.capitalize()) >> driven.attr('translate'+axis.capitalize())
    for axis in rotateAxes:
        decMtx.attr('outputRotate'+axis.capitalize()) >> driven.attr('rotate'+axis.capitalize())
    for axis in scaleAxes:
        decMtx.attr('outputScale'+axis.capitalize()) >> driven.attr('scale'+axis.capitalize())


def interpolateRotation(driverA, driverB, driven, driverAw, driverBw):
    driverA = pm.PyNode(driverA)
    driverB = pm.PyNode(driverB)
    driven = pm.PyNode(driven)
    blendNode = pm.createNode('animBlendNodeAdditiveRotation')

    driverA.rotate >> blendNode.inputA
    driverB.rotate >> blendNode.inputB
    blendNode.output >> driven.rotate

    blendNode.weightA.set(driverAw)
    blendNode.weightB.set(driverBw)


def copySDK(drivenObj, searchStr, replaceStr, inverseAttrs=[]):
    drivenObj = pm.PyNode(drivenObj)

    animNodes = list(set(drivenObj.listHistory(type='animCurve')))
    print(animNodes)
    for animNode in animNodes:
        inputPlug = animNode.connections(d=False, plugs=True)[0]
        # outputPlug = animNode.connections(s=False, plugs=True)[0]
        splitStrs = animNode.name().rsplit('_', 1)
        outputPlug = pm.PyNode('{0}.{1}'.format(splitStrs[0], splitStrs[1]))

        dupAnimNode = animNode.duplicate(n=animNode.replace(searchStr, replaceStr))[0]

        if inverseAttrs:
            for invAttr in inverseAttrs:
                if invAttr in outputPlug.name():
                    [dupAnimNode.setValue(id, -dupAnimNode.getValue(id)) for id in range(dupAnimNode.numKeys())]

        pm.PyNode(inputPlug.replace(searchStr, replaceStr)) >> dupAnimNode.input
        dupAnimNode.output >> pm.PyNode(outputPlug.replace(searchStr, replaceStr))
