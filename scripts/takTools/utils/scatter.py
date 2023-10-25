import pymel.core as pm


def follicleOnVertices(mesh):
    follicles = []
    for pnt in mesh.getPoints(space='world'):
        fol = pm.createNode('follicle')
        folTrsf = fol.getTransform()
        follicles.append(folTrsf)
        uv = mesh.getUVAtPoint(pnt)
        fol.parameterU.set(uv[0])
        fol.parameterV.set(uv[1])

        mesh.outMesh >> fol.inputMesh
        mesh.worldMatrix >> fol.inputWorldMatrix
        fol.outTranslate >> folTrsf.t
        fol.outRotate >> folTrsf.r
    return follicles


def duplicateToFollicles(source, follicles, instance=True, parent=False):
    for fol in follicles:
        dupObj = pm.duplicate(source, instanceLeaf=instance)[0]
        pm.matchTransform(dupObj, fol)
        if parent: pm.parent(dupObj, fol)



