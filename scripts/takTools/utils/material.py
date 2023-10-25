import os
import json

import pymel.core as pm


def getMaterials(geo):
    geo = pm.PyNode(geo)
    if isinstance(geo, pm.nodetypes.Transform):
        geo = geo.getShape()
    materials = []
    shadingEngines = geo.connections(s=False, type="shadingEngine")
    for shadingEngine in shadingEngines:
        for mat in pm.ls(shadingEngine.connections(), materials=True):
            if not mat.nodeType() == 'displacementShader':
                materials.append(mat)

    return list(set(materials))


def getMaterialsFromShape(shape):
    materials = []

    shadingEngines = shape.connections(d=True, type="shadingEngine")
    for se in shadingEngines:
        materials.extend([mat for mat in pm.ls(se.connections(), materials=True) if not pm.nodeType(mat) == 'displacementShader'])

    return list(set(materials))


def getObjectsWithMaterial(material):
    preSels = pm.ls(sl=True)
    pm.hyperShade(objects=material)
    objects = pm.ls(sl=True)
    pm.select(preSels, r=True)
    return objects


def duplicateMaterial(material):
    preSels = pm.ls(sl=True)
    pm.select(material, r=True)
    pm.hyperShade(duplicate=True)
    dupMaterial = pm.ls(sl=True)[0]
    pm.select(preSels, r=True)
    return dupMaterial


def copyMaterial(source, target):
    sourceMat = getMaterials(source)
    assignMaterial(target, sourceMat[0])


def assignMaterial(geo, material):
    preSels = pm.ls(sl=True)
    pm.select(geo, r=True)
    pm.hyperShade(assign=material)
    pm.select(preSels, r=True)


def assignMaterialToFace(geo):
    material = getMaterials(geo)[0]
    pm.delete(material.connections(s=False, type='shadingEngine'))
    pm.select(geo.faces, r=True)
    pm.hyperShade(assign=material)
    pm.select(geo, r=True)


def transferMaterialReferenceToDeformed(referenceNode):
    refShadingEngines = [node for node in pm.PyNode(referenceNode).nodes() if node.type() == 'shadingEngine']
    for shadingEngine in refShadingEngines:
        assignedObjs = pm.sets(shadingEngine, q=True)
        for obj in assignedObjs:
            if not obj.node().intermediateObject.get():  # In case deformed mesh, skip
                continue
            baseShapeName = obj.node().stripNamespace()
            noNameSpaceObj = obj.stripNamespace()
            objForAssign = noNameSpaceObj.replace(baseShapeName, baseShapeName+'Deformed')
            pm.sets(shadingEngine, forceElement=objForAssign)


def splitMaterial(faces):
    dupMat = None

    shape = faces[0].node()
    mat = getMaterialsFromShape(shape)
    dupMat = duplicateMaterial(mat)
    pm.select(faces, r=True)
    pm.hyperShade(assign=dupMat)

    return dupMat


def setNormalMapIgnoreColorSpaceRule():
    normalMaps = []
    bump2dNodes = pm.ls(type='bump2d')
    for bump2dNode in bump2dNodes:
        fileNodes = bump2dNode.connections(d=False, type='file')
        normalMaps.extend(fileNodes)

    for normalMap in normalMaps:
        normalMap.colorSpace.set('Raw')
        normalMap.ignoreColorSpaceFileRules.set(True)


def exportMaterials(geometries, fileName):
    materials = []
    for geo in geometries:
        materials.extend(getMaterials(geo))
    materials = list(set(materials))  # Remove repeated items

    matAssignInfo = {}
    for mat in materials:
        assignedItems = getObjectsWithMaterial(mat)
        matAssignInfo[mat.name()] = [item.name() for item in assignedItems]

    # Save material assign information
    outputDir = pm.env.sceneName().dirname()
    filePath = os.path.join(outputDir, '{}.json'.format(fileName))
    with open(filePath, 'w') as f:
        json.dump(matAssignInfo, f, indent=4)

    # Export materials
    preSels = pm.selected()
    matFilePath = os.path.join(outputDir, '{}_materials.ma'.format(fileName))
    pm.select(materials, r=True)
    pm.exportSelected(matFilePath, f=True)
    pm.select(preSels, r=True)


def loadMaterials(filePath):
    dir = os.path.dirname(filePath)
    fileName = os.path.basename(filePath)
    matFileName = os.path.splitext(fileName)[0] + '_materials.ma'
    matFilePath = os.path.join(dir, matFileName)
    pm.importFile(matFilePath)

    with open(filePath, 'r') as f:
        matAssignInfo = json.load(f)
    for mat, meshes in matAssignInfo.items():
        for mesh in meshes:
            if not pm.objExists(mesh):
                pm.warning('"{}" is not exists.'.format(mesh))
                continue
            assignMaterial(mesh, mat)
