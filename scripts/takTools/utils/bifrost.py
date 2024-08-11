import pymel.core as pm


if not pm.pluginInfo('bifrostGraph', q=True, loaded=True):
    pm.loadPlugin('bifrostGraph')


def convertToCageMesh(mesh, detailSize=0.02, faceCount=500, keepHardEdge=False, symmetry=False):
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
        symmetry=symmetry,
        axisPosition=1,
        axisOffset=0,
        axis=1,
        replaceOriginal=True,
        preprocessMesh=True,
        preserveHardEdges=keepHardEdge,
        topologyRegularity=1.0,
        faceUniformity=0.0,
        anisotropy=0.75,
        targetFaceCount=faceCount,
        targetFaceCountTolerance=10,
    )

    return cageMesh


def showConvertToCageMeshUI():
    def applyBtnCallback(*args):
        meshes = pm.filterExpand(pm.selected(), sm=12)
        dupMeshes = pm.duplicate(meshes, rc=True)
        if len(dupMeshes) > 1:
            mesh = pm.polyUnite(dupMeshes, ch=False)[0]
        else:
            mesh = dupMeshes[0]

        detailSize = pm.floatFieldGrp('detailSizeFloatFld', q=True, v1=True)
        faceCount = pm. intFieldGrp('faceCountIntFld', q=True, v1=True)
        keepHardEdges = pm.checkBoxGrp('retopoOptions', q=True, v1=True)
        symmetry = pm.checkBoxGrp('retopoOptions', q=True, v2=True)
        convertToCageMesh(mesh, detailSize, faceCount, keepHardEdges, symmetry)
        pm.delete(dupMeshes)

    pm.window(title='Create Cage Mesh', mnb=False, mxb=False)
    pm.columnLayout(adj=True, cal='left')

    pm.text(label='Volume Mesh Settings')
    pm.floatFieldGrp('detailSizeFloatFld', label='Detail Size:', v1=0.02, pre=3, columnWidth=[(1, 60)])

    pm.separator()

    pm.text(label='Retopology Settings')
    pm.intFieldGrp('faceCountIntFld', label='Face Count:', v1=500, columnWidth=[(1, 60)])
    pm.checkBoxGrp('retopoOptions', numberOfCheckBoxes=2, label='', labelArray2=['Keep Hard Edges', 'Symmetry'], v1=1, columnWidth=[(1, 10)])

    pm.button(label='Apply', c=applyBtnCallback)

    pm.showWindow()
