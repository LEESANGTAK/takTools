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
