from maya import cmds
from maya.api import OpenMaya as om


def follicleOnVertices(meshName):
    follicles = []
    selList = om.MSelectionList()
    selList.add(meshName)
    mDagPath = selList.getDagPath(0)
    mFnMesh = om.MFnMesh(mDagPath)
    points = mFnMesh.getPoints(om.MSpace.kWorld)

    for i in range(len(points)):
        pnt = points[i]
        fol = cmds.createNode('follicle')
        folTrsf = cmds.listRelatives(fol, parent=True)[0]
        follicles.append(folTrsf)
        uv = mFnMesh.getUVAtPoint(pnt)
        cmds.setAttr('{}.parameterU'.format(fol), uv[0])
        cmds.setAttr('{}.parameterV'.format(fol), uv[1])

        cmds.connectAttr('{}.outMesh'.format(meshName), '{}.inputMesh'.format(fol))
        cmds.connectAttr('{}.worldMatrix'.format(meshName), '{}.inputWorldMatrix'.format(fol))
        cmds.connectAttr('{}.outTranslate'.format(fol), '{}.t'.format(folTrsf))
        cmds.connectAttr('{}.outRotate'.format(fol), '{}.r'.format(folTrsf))

    return follicles


def duplicateToFollicles(source, follicles, instance=True, parent=False):
    for fol in follicles:
        dupObj = cmds.duplicate(source, instanceLeaf=instance)[0]
        cmds.matchTransform(dupObj, fol)
        if parent: cmds.parent(dupObj, fol)



