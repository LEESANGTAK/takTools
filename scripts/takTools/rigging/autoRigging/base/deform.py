import pymel.core as pm
import os

import re

from . import bSkinSaver

def build(modelFile, skeletonFile, skinMeshFile, skinFile, correctiveFile=None):
    referenceModel(modelFile)
    importSkeleton(skeletonFile)
    importSkinMesh(skinMeshFile)
    importSkin(skinFile)
    if correctiveFile:
        importCorrective(correctiveFile)
    #copySkinToModel()

def referenceModel(modelFile):
    baseName = os.path.basename(modelFile)
    namespace = os.path.splitext(baseName)[0]
    pm.createReference(modelFile, ns=namespace)

def importSkeleton(skeletonFile):
    rootJoint = None
    newNodes = pm.importFile(skeletonFile, returnNewNodes=True)
    joints = pm.ls(newNodes, type='joint')
    for jnt in joints:
        jntParent = jnt.getParent()
        if jntParent and jntParent.type() != 'joint':
            rootJoint = jnt
            break
        elif not jntParent:
            rootJoint = jnt
            break
    return rootJoint

def importSkinMesh(skinMeshFile):
    pm.importFile(skinMeshFile)

def importSkin(skinFile):
    bSkinSaver.bLoadSkinValues(False, skinFile)

def importCorrective(correctiveFile):
    pm.importFile(correctiveFile)
    # Corrective joint setup

    # Corrective shape setup

def getNamespaceFromSkinFile(skinFile):
    namespace = ''

    with open(skinFile, 'r') as f:
        fContents = f.read()

    searchObj = re.search(r'(.*):.*', fContents)
    if searchObj:
        namespace = searchObj.group(1)

    return namespace
