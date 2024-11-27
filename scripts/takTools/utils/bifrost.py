from maya import cmds
import pymel.core as pm


if not pm.pluginInfo('bifrostGraph', q=True, loaded=True):
    pm.loadPlugin('bifrostGraph')


def convertToCageMesh(meshes, minHoleRadius=25, detailSize=0.02, faceCount=1000, keepHardEdge=False, symmetry=False):
    dupMeshes = pm.duplicate(meshes, rc=True)

    # When multiple meshes are given then combine meshes before processing
    if len(dupMeshes) > 1:
        mesh = pm.polyUnite(dupMeshes, ch=False)[0]
    else:
        mesh = dupMeshes[0]

    # It takes long time and produce desatisfiying result when set too low or too high values
    detailSize = max(detailSize, 0.01)
    minHoleRadius = min(minHoleRadius, 50)

    # Build bifrost graph node
    bfGraph = pm.createNode('bifrostGraphShape')

    ## Create input and output
    pm.vnnNode(bfGraph, '/input', createOutputPort=('inMesh', 'Object'))
    pm.vnnNode(bfGraph, '/output', createInputPort=('outMeshes', 'array<Object>'))

    ## Create a mesh_to_volume node and set parameters
    pm.vnnCompound(bfGraph, '/', addNode='BifrostGraph,Geometry::Converters,mesh_to_volume')
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('volume_mode', '0'))  # Set to solid mode
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('store_level_set', '1'))  # This produce more fitted mesh to the input mesh
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('store_fog_density', '0'))
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('min_hole_radius', str(minHoleRadius)))
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('detail_size', str(detailSize)))

    ## Create a volume_to_mesh node and add a input port
    pm.vnnCompound(bfGraph, '/', addNode='BifrostGraph,Geometry::Converters,volume_to_mesh')
    pm.vnnNode(bfGraph, '/volume_to_mesh', createInputPort=('volumes.volume', 'auto'))

    ## Connect nodes
    pm.vnnConnect(bfGraph, '/input.inMesh', '/mesh_to_volume.mesh')
    pm.vnnConnect(bfGraph, '/mesh_to_volume.volume', '/volume_to_mesh.volumes.volume')
    pm.vnnConnect(bfGraph, '/volume_to_mesh.meshes', '/output.outMeshes')

    # Convert to maya mesh
    skinCageName = '{}_cage'.format(mesh)

    bfGeoToMaya = pm.createNode('bifrostGeoToMaya')
    cageMesh = pm.createNode('mesh')
    cageMesh.getParent().rename(skinCageName)

    mesh.outMesh >> bfGraph.inMesh
    bfGraph.outMeshes >> bfGeoToMaya.bifrostGeo
    bfGeoToMaya.mayaMesh[0] >> cageMesh.inMesh

    # Clean up temp nodes
    pm.delete(cageMesh, ch=True)
    pm.delete(bfGraph.getParent())

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
        faceUniformity=1.0,
        anisotropy=0.75,
        targetFaceCount=faceCount,
        targetFaceCountTolerance=10,
    )

    pm.delete(dupMeshes)

    return cageMesh


def showConvertToCageMeshUI(parent=None, *args):
    def applyBtnCallback(*args):
        meshes = pm.filterExpand(pm.selected(), sm=12)
        minHoleRadius = pm.floatField('minHoleRadiusFloatFld', q=True, v=True)
        detailSize = pm.floatField('detailSizeFloatFld', q=True, v=True)
        faceCount = pm. intFieldGrp('faceCountIntFld', q=True, v1=True)
        keepHardEdges = pm.checkBoxGrp('retopoOptions', q=True, v2=True)
        symmetry = pm.checkBoxGrp('retopoOptions', q=True, v2=True)
        convertToCageMesh(meshes, minHoleRadius, detailSize, faceCount, keepHardEdges, symmetry)

    winName = 'cageMeshWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    cmds.window(winName, title='Create Cage Mesh', mnb=False, mxb=False)
    if parent:
        cmds.window(winName, e=True, p=parent)

    pm.columnLayout(adj=True, cal='left')

    pm.frameLayout(label='Volume Mesh Settings')
    pm.rowColumnLayout(numberOfColumns=2)
    pm.text(label='Min Hole Radius: ', ann='Minimize holes of the volume. \nHigher value produce more solid mesh. \nThis is suitable for making solid mesh from a shell mesh like a shirts or shoes.')
    pm.floatField('minHoleRadiusFloatFld', v=0.0, min=0.0, pre=1)
    pm.text(label='Detail Size: ', ann='When this value set to higher the resulting mesh will be more closed to the input mesh.')
    pm.floatField('detailSizeFloatFld', v=0.02, min=0.01, pre=3)

    pm.setParent('..')
    pm.setParent('..')

    pm.separator(style='in')

    pm.frameLayout(label='Retopology Settings')
    pm.intFieldGrp('faceCountIntFld', label='Face Count:', v1=1000, columnWidth=[(1, 60)])
    pm.checkBoxGrp('retopoOptions', numberOfCheckBoxes=2, label='', labelArray2=['Keep Hard Edges', 'Symmetry'], v1=0, columnWidth=[(1, 10)])

    pm.setParent('..')
    pm.separator(style='in')

    pm.button(label='Apply', c=applyBtnCallback)

    pm.showWindow(winName)
