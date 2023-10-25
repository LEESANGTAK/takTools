import pymel.core as pm

def createAssetHierarchy():
    rootGrp = pm.createNode('transform', n='asset')
    for subGrp in ['modeling', 'grooming', 'skeleton', 'rigging']:
        pm.createNode('transform', n=subGrp)
        pm.parent(subGrp, rootGrp)
