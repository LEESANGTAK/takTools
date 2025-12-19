import os
import json
from PIL import Image

from maya import cmds
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


def exportMaterials(geo, outputDir):
    geo = pm.PyNode(geo)
    materials = []
    materials.extend(getMaterials(geo))
    materials = list(set(materials))  # Remove repeated items

    matAssignInfo = {}
    for mat in materials:
        assignedItems = getObjectsWithMaterial(mat)
        matAssignInfo[mat.name()] = [item.name() for item in assignedItems]

    # Save material assign information
    filePath = '{}/{}.mats'.format(outputDir, geo.name())
    with open(filePath, 'w') as f:
        json.dump(matAssignInfo, f, indent=4)


def importMaterials(filePath):
    with open(filePath, 'r') as f:
        matAssignInfo = json.load(f)

    for mat, meshes in matAssignInfo.items():
        if not pm.objExists(mat):
            mat = pm.shadingNode('blinn', n=mat, asShader=True)
        for mesh in meshes:
            if not pm.objExists(mesh):
                pm.warning('"{}" is not exists.'.format(mesh))
                continue
            assignMaterial(mesh, mat)


def atlasTextures(meshes, atlasImageWidthHeight=4096, atlasImagePath='', type='diffuse'):
    # Calculate the size of the rows and columns
    rowColumnSize = 0
    numMeshes = len(meshes)
    if 2 <= numMeshes <= 4:
        rowColumnSize = 2
    elif 5 <= numMeshes <= 9:
        rowColumnSize = 3
    elif 10 <= numMeshes <= 16:
        rowColumnSize = 4

    # Calculate the scale value that scales down a texture
    scaleValue = 1.0/rowColumnSize
    imgWidthHeight = atlasImageWidthHeight * scaleValue

    atlasImage = Image.new('RGBA', (atlasImageWidthHeight, atlasImageWidthHeight), (0, 0, 0, 1))

    # Resize and layout images
    for row in range(rowColumnSize):
        for col in range(rowColumnSize):
            meshIndex = (row * rowColumnSize) + col

            if not cmds.objExists(meshes[meshIndex]):
                continue

            try:
                meshes[meshIndex]
            except IndexError:
                atlasImage.save(atlasImagePath)
                return

            material = getMaterials(meshes[meshIndex])[0]
            print('Material:', material)

            if type == 'diffuse':
                imgPath = getDiffuseTexturePath(str(material))
            elif type == 'normal':
                imgPath = getNormalTexturePath(str(material))

            print('Image Path:', imgPath)

            if not imgPath:
                continue

            image = Image.open(imgPath)
            image = image.resize((int(imgWidthHeight), int(imgWidthHeight)), Image.LANCZOS)

            pivotX = imgWidthHeight * col
            pivotY = imgWidthHeight * ((rowColumnSize-1) - row)  # Image's origin is top-left but UV's origin is bottom-left
            atlasImage.paste(image, (int(pivotX), int(pivotY)))

    atlasImage.save(atlasImagePath)


def getDiffuseTexturePath(material):
    imgPath = None
    texture = cmds.listConnections(f'{material}.color', type='file')
    print('Texture:', texture)
    if texture:
        imgPath = cmds.getAttr(f'{texture[0]}.fileTextureName')
    return imgPath


def getNormalTexturePath(material):
    imgPath = None
    bump2dNode = cmds.listConnections(material, type='bump2d')
    if bump2dNode:
        texture = cmds.listConnections(bump2dNode[0], type='file')
        if texture:
            imgPath = cmds.getAttr(f'{texture[0]}.fileTextureName')
    return imgPath
