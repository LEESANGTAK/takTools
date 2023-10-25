import maya.cmds as cmds

from . import globalUtil


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
