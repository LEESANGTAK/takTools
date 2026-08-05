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
import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel


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

    selLs = om.MSelectionList()
    selLs.add(source)
    selLs.add(target)

    srcDagPath = selLs.getDagPath(0)
    trgDagPath = selLs.getDagPath(1)

    trgVtxIt = om.MItMeshVertex(trgDagPath)

    srcMeshFn = om.MFnMesh(srcDagPath)

    overlappedVerticesId = []
    while not trgVtxIt.isDone():
        trgVtxWsPnt = trgVtxIt.position(om.MSpace.kWorld)
        trgVtxNormal = trgVtxIt.getNormal()

        intersectPoint = srcMeshFn.closestIntersection(
            om.MFloatPoint(trgVtxWsPnt),
            om.MFloatVector(trgVtxNormal),
            om.MSpace.kWorld,
            searchRadius,
            True
        )[0]

        if not intersectPoint.isEquivalent(om.MFloatPoint(0, 0, 0, 1)):
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
    id = 0

    while cmds.listConnections(f'{node}.{attribute}[{id}]'):
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
    mSelLs = om.MSelectionList()
    mSelLs.add(node)
    return mSelLs.getDagPath(0)


def swapOrderString(type="number"):
    """
    Swap ordered string for selected two objects.

    Parameters:
        type(str): Order string type. Available type is 'number' or 'alphabet'.
    """
    firstOrderStr = None
    secOrderStr = None

    sels = cmds.ls(sl=True)
    if type == "number":
        firstOrderStr = re.search(r"_(\d+)_", sels[0]).group(1)
        secOrderStr = re.search(r"_(\d+)_", sels[1]).group(1)
    elif type == "alphabet":
        firstOrderStr = re.search(r"_(\D)_", sels[0]).group(1)
        secOrderStr = re.search(r"_(\D)_", sels[1]).group(1)

    cmds.rename(sels[0], sels[0].replace(firstOrderStr, "tempStr"))
    cmds.rename(sels[1], sels[1].replace(secOrderStr, firstOrderStr))
    cmds.rename(sels[0], sels[0].replace("tempStr", secOrderStr))


def matchTransformToFace(transform, face):
    mesh_name = cmds.listRelatives(cmds.ls(face, objectsOnly=True)[0], p=True)[0]

    face_index = None
    match = re.search(r'f\[(\d+)\]', face)
    if match:
        face_index = int(match.group(1))

    face_info = cmds.polyInfo(face, faceToVertex=True)
    verts = [int(v) for v in face_info[0].split()[2:]]
    points = []
    for vert in verts:
        pos = cmds.pointPosition('%s.vtx[%d]' % (mesh_name, vert), w=True)
        points.append(om.MVector(pos[0], pos[1], pos[2]))

    position = om.MVector()
    for point in points:
        position += point
    position /= len(points)

    selection = om.MSelectionList()
    selection.add(mesh_name)
    dag_path = selection.getDagPath(0)
    fn_mesh = om.MFnMesh(dag_path)

    normal = fn_mesh.getPolygonNormal(face_index, om.MSpace.kWorld)
    normal.normalize()

    vectorX = points[1] - points[0]
    if vectorX.length() == 0.0:
        vectorX = points[-1] - points[0]
    vectorX.normalize()

    vectorZ = vectorX ^ normal
    vectorZ.normalize()

    vectorY = normal

    matrix = [
        vectorX.x, vectorX.y, vectorX.z, 0,
        vectorY.x, vectorY.y, vectorY.z, 0,
        vectorZ.x, vectorZ.y, vectorZ.z, 0,
        position.x, position.y, position.z, 1,
    ]

    cmds.xform(transform, ws=True, matrix=matrix)


def getInputNodes(start, inputNodes, nodeType=None):
    """
    Parameters:
        start<str>: Node or Node.Attribute name
        inputNodes<list>: Empty list
        nodeType<str>: Specific node type
    """
    nodes = cmds.listConnections(start, d=False, scn=True)
    if nodes:
        for node in nodes:
            if nodeType:
                if cmds.nodeType(node) == nodeType:
                    inputNodes.append(node)
            else:
                inputNodes.append(node)
            getInputNodes(str(node), inputNodes, nodeType)

    return sorted(list(set(inputNodes)), key=type)


def duplicateRename(node, prefix='', suffix='', srchStr='', rplcStr=''):
    addStrDupNode = cmds.duplicate(node, n=prefix + node + suffix, returnRootsOnly=True)[0]
    subStrDupNodeName = re.sub(srchStr, rplcStr, addStrDupNode)
    dupNode = cmds.rename(addStrDupNode, subStrDupNodeName)

    try:
        cmds.parent(dupNode, world=True)
    except:
        pass

    dupObjChldLs = cmds.listRelatives(dupNode, type='transform', ad=True, path=True)
    if dupObjChldLs:
        for chldObj in dupObjChldLs:
            chldObjBaseName = chldObj.split('|')[-1]
            addName = cmds.rename(chldObj, prefix + chldObjBaseName + suffix)
            subName = re.sub(srchStr, rplcStr, addName)
            cmds.rename(addName, subName)

    return dupNode


def setDefaultTransform(transformNode):
    attrs = ['translate', 'rotate', 'scale']
    axises = ["X", "Y", "Z"]
    for attr in attrs:
        for axis in axises:
            transformNode.attr(attr+axis).set(1) if attr == 'scale' else transformNode.attr(attr+axis).set(0)


def deleteIntermediateObject(transformNode):
    itmdShapes = cmds.ls(transformNode, dag=True, s=True, io=True)
    for shape in itmdShapes:
        if cmds.objExists(f'{shape}.intermediateObject'):
            cmds.delete(shape)


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
    srcInfs = getInfluences(source)
    srcJointInfs = [inf for inf in srcInfs if cmds.nodeType(inf, 'joint')]
    srcGeoInfs = list(set(srcInfs) - set(srcJointInfs))
    srcSkinClst = mel.eval('findRelatedSkinCluster("%s");' % source)
    targetMesh = cmds.ls(target, objectsOnly=True)[0] if 'vtx' in target else target
    trgSkinClst = mel.eval('findRelatedSkinCluster("%s");' % targetMesh)

    if not trgSkinClst:
        trgSkinClst = cmds.skinCluster(srcJointInfs, targetMesh, dr=4, tsb=True, nw=1)
        cmds.skinCluster(trgSkinClst, e=True, ug=True, ai=srcGeoInfs)

    else:
        trgInfs = getInfluences(targetMesh)
        trgJointInfs = [inf for inf in trgInfs if cmds.nodeType(inf) == 'joint']
        trgGeoInfs = list(set(trgInfs) - set(trgJointInfs))
        addedSrcJointInfs = list(set(srcJointInfs) - set(trgJointInfs))
        addedSrcGeoInfs = list(set(srcGeoInfs) - set(trgGeoInfs))

        cmds.skinCluster(trgSkinClst, e=True, ai=addedSrcJointInfs)
        cmds.skinCluster(trgSkinClst, e=True, ug=True, ai=addedSrcGeoInfs)

    cmds.select(source, target, r=True)
    cmds.CopySkinWeights()

    cmds.setAttr(f'{trgSkinClst}.skinningMethod', cmds.getAttr(f'{srcSkinClst}.skinningMethod'))
    cmds.setAttr(f'{trgSkinClst}.useComponents', cmds.getAttr(f'{srcSkinClst}.useComponents'))


def copyMat(source, target):
    srcShape = source.getShape()
    trgShape = target.getShape()
    srcShadingGrp = srcShape.listConnections(s=False, type='shadingEngine')[0]
    cmds.sets(srcShadingGrp, forceElement=trgShape)


def getInfluences(skinGeo):
    skClu = mel.eval('findRelatedSkinCluster("%s");' % skinGeo)
    infls = cmds.skinCluster(skClu, q=True, inf=True)
    return infls


def constraintWithMatrix(driver, driven, maintainOffset=True, translateAxes=['x','y','z'], rotateAxes=['x','y','z'], scaleAxes=[]):
    multMtx = cmds.createNode('multMatrix', n=driver.name()+'_multMtx')
    decMtx = cmds.createNode('decomposeMatrix', n=driver.name()+'_decMtx')

    if maintainOffset:
        offsetMtx = cmds.getAttr(f'{driven}.worldMatrix') * cmds.getAttr(f'{driver}.worldInverseMatrix')  # Parent to driver
        cmds.setAttr(f'{multMtx}.matrixIn[0]', type='matrix', *offsetMtx)
        cmds.connectAttr(f'{driver}.worldMatrix', f'{multMtx}.matrixIn[1]', f=True)
        if cmds.listRelatives(driven, p=True): cmds.connectAttr(f'{cmds.listRelatives(driven, p=True)[0]}.worldInverseMatrix', f'{multMtx}.matrixIn[2]', f=True)
    else:
        cmds.connectAttr(f'{driver}.worldMatrix', f'{multMtx}.matrixIn[0]', f=True)
        if cmds.listRelatives(driven, p=True): cmds.connectAttr(f'{cmds.listRelatives(driven, p=True)[0]}.worldInverseMatrix', f'{multMtx}.matrixIn[1]', f=True)

    cmds.connectAttr(f'{multMtx}.matrixSum', f'{decMtx}.inputMatrix', f=True)

    for axis in translateAxes:
        cmds.connectAttr(f'{decMtx}.outputTranslate{axis.capitalize()}', f'{driven}.translate{axis.capitalize()}', f=True)
    for axis in rotateAxes:
        cmds.connectAttr(f'{decMtx}.outputRotate{axis.capitalize()}', f'{driven}.rotate{axis.capitalize()}', f=True)
    for axis in scaleAxes:
        cmds.connectAttr(f'{decMtx}.outputScale{axis.capitalize()}', f'{driven}.scale{axis.capitalize()}', f=True)


def interpolateRotation(driverA, driverB, driven, driverAw, driverBw):
    blendNode = cmds.createNode('animBlendNodeAdditiveRotation')

    cmds.connectAttr(f'{driverA}.rotate', f'{blendNode}.inputA')
    cmds.connectAttr(f'{driverB}.rotate', f'{blendNode}.inputB')
    cmds.connectAttr(f'{blendNode}.output', f'{driven}.rotate')

    cmds.setAttr(f'{blendNode}.weightA', driverAw)
    cmds.setAttr(f'{blendNode}.weightB', driverBw)


def copySDK(drivenObj, searchStr, replaceStr, inverseAttrs=[]):
    animNodes = list(set(cmds.listHistory(drivenObj, type='animCurve')))

    for animNode in animNodes:
        inputPlug = cmds.listConnections(animNode, d=False, plugs=True)[0]
        splitStrs = animNode.rsplit('_', 1)
        outputPlug = '{0}.{1}'.format(splitStrs[0], splitStrs[1])

        dupAnimNode = cmds.duplicate(animNode, n=animNode.replace(searchStr, replaceStr))[0]

        if inverseAttrs:
            for invAttr in inverseAttrs:
                if invAttr in outputPlug:
                    numKeyframes = len(cmds.keyframe(dupAnimNode, q=True))
                    for id in range(numKeyframes):
                        srcValue = cmds.keyframe(dupAnimNode, q=True, index=(id,), valueChange=True)[0]
                        cmds.keyframe(dupAnimNode, e=True, index=(id,), valueChange=-srcValue)

        cmds.connectAttr(inputPlug.replace(searchStr, replaceStr), f'{dupAnimNode}.input')
        cmds.connectAttr(f'{dupAnimNode}.output', outputPlug.replace(searchStr, replaceStr))
