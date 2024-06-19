import pymel.core as pm


if not pm.pluginInfo('bifrostGraph', q=True, loaded=True):
    pm.loadPlugin('bifrostGraph')


def convertToCageMesh(mesh, detailSize=0.02, faceCount=1000, keepOriginal=True):
    # It takes long time and produce not good result when below 0.01 value for the detail size
    detailSize = max(detailSize, 0.01)

    # Build bifrost graph node
    bfGraph = pm.createNode('bifrostGraphShape')

    pm.vnnNode(bfGraph, '/input', createOutputPort=('inMesh', 'Object'))
    pm.vnnNode(bfGraph, '/output', createInputPort=('outMeshes', 'array<Object>'))

    pm.vnnCompound(bfGraph, '/', addNode='BifrostGraph,Geometry::Converters,mesh_to_volume')
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('volume_mode', '1'))
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('store_level_set', '1'))
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('store_fog_density', '0'))
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('detail_size', str(detailSize)))
    pm.vnnCompound(bfGraph, '/', addNode='BifrostGraph,Geometry::Converters,volume_to_mesh')
    pm.vnnNode(bfGraph, '/volume_to_mesh', createInputPort=('volumes.volume', 'auto'))

    pm.vnnConnect(bfGraph, '/input.inMesh', '/mesh_to_volume.mesh')
    pm.vnnConnect(bfGraph, '/mesh_to_volume.volume', '/volume_to_mesh.volumes.volume')
    pm.vnnConnect(bfGraph, '/volume_to_mesh.meshes', '/output.outMeshes')

    # Convert to cage mesh
    skinCageName = '{}_cage'.format(mesh)
    # mesh = pm.duplicate(mesh)[0]

    bfGeoToMaya = pm.createNode('bifrostGeoToMaya')
    cageMesh = pm.createNode('mesh')
    cageMesh.getParent().rename(skinCageName)

    mesh.outMesh >> bfGraph.inMesh
    bfGraph.outMeshes >> bfGeoToMaya.bifrostGeo
    bfGeoToMaya.mayaMesh[0] >> cageMesh.inMesh

    pm.delete(cageMesh, ch=True)
    pm.delete(bfGraph.getParent())

    if not keepOriginal:
        pm.delete(mesh)

    # Clean up cage mesh
    largestArea = 0.0
    try:
        meshes = pm.polySeparate(cageMesh, ch=False)
        # Find cage mesh in separated meshes
        for mesh in meshes:
            bb = meshes[0].boundingBox()
            volumeArea = bb.width() * bb.height() * bb.depth()
            if volumeArea > largestArea:
                cageMesh = mesh
                largestArea = volumeArea

        pm.parent(cageMesh, w=True)
        pm.delete(skinCageName)
        cageMesh.rename(skinCageName)
    except:
        pass

    pm.hyperShade(cageMesh, assign='lambert1')

    # Retopologize
    pm.polyRetopo(
        cageMesh,
        ch=False,
        replaceOriginal=True,
        preserveHardEdges=True,
        topologyRegularity=1.0,
        faceUniformity=1.0,
        anisotropy=0.75,
        targetFaceCountTolerance=10,
        targetFaceCount=faceCount
    )

    return cageMesh


def showConvertToCageMeshUI():
    def applyBtnCallback(*args):
        mesh = pm.selected()[0]
        detailSize = pm.floatFieldGrp('detailSizeFloatFld', q=True, v1=True)
        faceCount = pm. intFieldGrp('faceCountIntFld', q=True, v1=True)
        keepOrig = pm.checkBoxGrp('keepOrigChkbox', q=True, v1=True)
        convertToCageMesh(mesh, detailSize, faceCount, keepOrig)

    pm.window(title='Create Cage Mesh', mnb=False, mxb=False)
    pm.columnLayout(adj=True)
    pm.floatFieldGrp('detailSizeFloatFld', label='Detail Size:', v1=0.01, pre=3, columnWidth=[(1,80)])
    pm.intFieldGrp('faceCountIntFld', label='Face Count:', v1=1000, columnWidth=[(1,80)])
    pm.checkBoxGrp('keepOrigChkbox', label='Keep Original', v1=True, columnWidth=[(1,80)])
    pm.button(label='Apply', c=applyBtnCallback)
    pm.showWindow()
