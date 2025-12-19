import pymel.core as pm
import maya.cmds as cmds

from . import globalUtil
from . import mesh as meshUtil


def replaceAllUVSets(source, target):
    # Delete all uv sets of target
    oldUVSets = cmds.polyUVSet(target, q=True, allUVSets=True)
    for oldUVSet in oldUVSets:
        try:
            cmds.polyUVSet(target, uvSet=oldUVSet, delete=True)
        except:
            pass

    # Transfer all uv sets from source to target
    cmds.transferAttributes(source, target, transferPositions=0, transferNormals=0, transferUVs=2, transferColors=0, sampleSpace=0, searchMethod=3, flipUVs=0, colorBorders=1)

    cmds.delete(target, ch=True)


def connectUVSets(source, target):
    logicalUVSetIndices = globalUtil.getLogicalIndices(source, 'uvSet')
    j = 0
    for i in logicalUVSetIndices:
        cmds.connectAttr('{0}.uvSet[{1}]'.format(source, i), '{0}.uvSet[{1}]'.format(target, j), f=True)
        j += 1


def connectReferenceUVsetToDeformed(referenceMesh):
    deformedOrig = None
    intermediateObjects = [shape for shape in cmds.listRelatives(referenceMesh, s=True) if cmds.getAttr('{0}.intermediateObject'.format(shape))]

    if len(intermediateObjects) >= 2:
        refIntermediateObject = [shape for shape in intermediateObjects if not 'Orig' in shape][0]
        deformedOrig = [shape for shape in intermediateObjects if 'Orig' in shape][0]
    else:
        refIntermediateObject = intermediateObjects[0]

    deformedShape = cmds.listRelatives(referenceMesh, s=True, ni=True)[0]

    if deformedOrig:
        connectUVSets(refIntermediateObject, deformedOrig)
    else:
        connectUVSets(refIntermediateObject, deformedShape)


def createLightMapUVSet(lightMapUVSetName='LightMapUV'):
    cleanupNeedObjs = []
    for sel in pm.selected():
        allUVSets = pm.polyUVSet(sel.getShape(), q=True, allUVSets=True)
        if len(allUVSets) > 1:
            cleanupNeedObjs.append(sel)
        pm.polyCopyUV(sel, uvSetNameInput=allUVSets[0], uvSetName=lightMapUVSetName, createNewMap=True, ch=True)
        pm.polyUVSet(sel.getShape(), currentUVSet=True, uvSet=allUVSets[0])
    if cleanupNeedObjs:
        pm.warning('{} are need to clean up UV Sets.'.format(cleanupNeedObjs))


def normalizeCardUVs(selections):
    # Get a mesh and dupMesh from selections
    mesh = None
    dupMesh = None
    faces = cmds.filterExpand(selections, sm=34)
    if faces:
        mesh = [cmds.listRelatives(shape, p=True)[0] for shape in list(set(cmds.ls(faces, objectsOnly=True)))][0]
        dupMesh = meshUtil.duplicateFace(faces)
    else:
        mesh = selections[0]
        dupMesh = cmds.duplicate(mesh)[0]

    # Normalize uvs for separated card meshes
    cards = cmds.filterExpand(cmds.polySeparate(dupMesh), sm=12)
    for card in cards:
        cmds.select(card, r=True)
        cmds.polyNormalizeUV(normalizeType=1, preserveAspectRatio=False, centerOnTile=False)
    normalizedUVsMesh = cmds.filterExpand(cmds.polyUnite(dupMesh), sm=12)[0]

    # Transfer uvs from separated card meshes to original mesh
    target = faces or mesh
    cmds.transferAttributes(normalizedUVsMesh, target,
        sampleSpace=0,
        transferPositions=False,
        transferNormals=False,
        transferColors=False,
        transferUVs=True,
        searchMethod=3
    )

    # Clean up
    cmds.delete(mesh, normalizedUVsMesh, ch=True)
    cmds.delete(normalizedUVsMesh)
    if cmds.objExists(dupMesh):
        cmds.delete(dupMesh)

    cmds.select(mesh, r=True)


def atlasUVs(meshes):
    # Calculate the size of the rows and columns
    rowColumnSize = 0
    numMeshes = len(meshes)
    if 2 <= numMeshes <= 4:
        rowColumnSize = 2
    elif 5 <= numMeshes <= 9:
        rowColumnSize = 3
    elif 10 <= numMeshes <= 16:
        rowColumnSize = 4

    # Calculate the scale value that scales down a mesh's UV
    scaleValue = 1.0/rowColumnSize

    # Resize and layout UVs
    for row in range(rowColumnSize):
        for col in range(rowColumnSize):
            meshIndex = (row * rowColumnSize) + col
            uValue = scaleValue * col
            vValue = scaleValue * row

            if not cmds.objExists(meshes[meshIndex]):
                continue

            try:
                cmds.select(f'{meshes[meshIndex]}.map[*]', r=True)
            except IndexError:
                return

            cmds.polyEditUV(pu=0, pv=0, su=scaleValue, sv=scaleValue)
            cmds.polyEditUV(pu=0, pv=0, u=uValue, v=vValue)
