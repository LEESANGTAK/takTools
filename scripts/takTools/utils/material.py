import json
from maya import cmds


def _getShapes(node):
    shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
    if not shapes and cmds.nodeType(node) == 'mesh':
        shapes = [node]
    return shapes


def getMaterials(geo):
    shapes = _getShapes(geo)
    materials = []
    for shape in shapes:
        shadingEngines = cmds.listConnections(shape, type='shadingEngine', s=False, d=True) or []
        for shadingEngine in shadingEngines:
            mats = cmds.ls(cmds.listConnections(shadingEngine) or [], materials=True) or []
            for mat in mats:
                if cmds.nodeType(mat) != 'displacementShader':
                    materials.append(mat)

    return list(set(materials))


def getMaterialsFromShape(shape):
    materials = []
    shadingEngines = cmds.listConnections(shape, type='shadingEngine', d=True) or []
    for se in shadingEngines:
        mats = cmds.ls(cmds.listConnections(se) or [], materials=True) or []
        materials.extend([mat for mat in mats if cmds.nodeType(mat) != 'displacementShader'])

    return list(set(materials))


def getObjectsWithMaterial(material):
    preSels = cmds.ls(sl=True)
    objects = cmds.hyperShade(objects=material) or []
    if preSels:
        cmds.select(preSels, r=True)
    return objects


def duplicateMaterial(material):
    preSels = cmds.ls(sl=True)
    cmds.select(material, r=True)
    dupMaterials = cmds.hyperShade(duplicate=True) or []
    if preSels:
        cmds.select(preSels, r=True)
    return dupMaterials[0] if dupMaterials else None


def copyMaterial(source, target):
    sourceMat = getMaterials(source)
    if sourceMat:
        assignMaterial(target, sourceMat[0])


def assignMaterial(geo, material):
    preSels = cmds.ls(sl=True)
    cmds.select(geo, r=True)
    cmds.hyperShade(assign=material)
    if preSels:
        cmds.select(preSels, r=True)


def assignMaterialToFace(geo):
    material = getMaterials(geo)[0]
    shadingEngines = cmds.listConnections(material, type='shadingEngine', s=False, d=True) or []
    for se in shadingEngines:
        cmds.delete(se)
    target = '{}.f[*]'.format(geo.split('|')[-1]) if '.' not in geo else geo
    cmds.select(target, r=True)
    cmds.hyperShade(assign=material)
    cmds.select(geo, r=True)


def transferMaterialReferenceToDeformed(referenceNode):
    refNodes = cmds.listRelatives(referenceNode, allDescendents=True, fullPath=True) or []
    refShadingEngines = [node for node in refNodes if cmds.nodeType(node) == 'shadingEngine']
    for shadingEngine in refShadingEngines:
        assignedObjs = cmds.sets(shadingEngine, q=True) or []
        for obj in assignedObjs:
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            if not shapes or not cmds.getAttr('{}.intermediateObject'.format(shapes[0])):
                continue
            baseShapeName = obj.split(':')[-1]
            objForAssign = obj.replace(baseShapeName, baseShapeName+'Deformed')
            if cmds.objExists(objForAssign):
                cmds.sets(shadingEngine, forceElement=objForAssign)


def splitMaterial(faces):
    shape = faces[0].split('.')[0] if isinstance(faces[0], str) else faces[0]
    mat = getMaterialsFromShape(shape)
    dupMat = duplicateMaterial(mat[0] if mat else None)
    cmds.select(faces, r=True)
    if dupMat:
        cmds.hyperShade(assign=dupMat)
    return dupMat


def setNormalMapIgnoreColorSpaceRule():
    normalMaps = []
    bump2dNodes = cmds.ls(type='bump2d') or []
    for bump2dNode in bump2dNodes:
        fileNodes = cmds.listConnections(bump2dNode, d=False, type='file') or []
        normalMaps.extend(fileNodes)

    for normalMap in normalMaps:
        cmds.setAttr('{}.colorSpace'.format(normalMap), 'Raw', type='string')
        cmds.setAttr('{}.ignoreColorSpaceFileRules'.format(normalMap), True)


def exportMaterials(geo, outputDir):
    materials = list(set(getMaterials(geo)))
    matAssignInfo = {}
    for mat in materials:
        assignedItems = getObjectsWithMaterial(mat)
        matAssignInfo[mat] = assignedItems

    filePath = '{}/{}.mats'.format(outputDir, geo.split('|')[-1])
    with open(filePath, 'w') as f:
        json.dump(matAssignInfo, f, indent=4)


def importMaterials(filePath):
    with open(filePath, 'r') as f:
        matAssignInfo = json.load(f)

    for mat, meshes in matAssignInfo.items():
        if not cmds.objExists(mat):
            mat = cmds.shadingNode('blinn', n=mat, asShader=True)
        for mesh in meshes:
            if not cmds.objExists(mesh):
                cmds.warning('"{}" is not exists.'.format(mesh))
                continue
            assignMaterial(mesh, mat)
