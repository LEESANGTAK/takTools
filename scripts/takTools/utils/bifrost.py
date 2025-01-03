from maya import cmds
import pymel.core as pm
from . import mesh as meshUtil

try:
    if not pm.pluginInfo('bifrostGraph', q=True, loaded=True):
        pm.loadPlugin('bifrostGraph')
except:
    cmds.warning('Failed to load bifrostGraph plug-in.')


def convertToCageMesh(meshes, minHoleRadius=10.0, detailSize=0.02, faceCount=1000, symmetry=False, delHistory=True):
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
    mesh.worldMesh >> bfGraph.inMesh

    # Add attributes to control retopo mesh
    pm.vnnNode(bfGraph, "/input", createOutputPort=("offset", "float"))
    pm.vnnConnect(bfGraph, "/input.offset", "/mesh_to_volume.offset")

    pm.vnnNode(bfGraph, "/input", createOutputPort=("min_hole_radius", "float"))
    pm.vnnConnect(bfGraph, "/input.min_hole_radius", "/mesh_to_volume.min_hole_radius")
    bfGraph.min_hole_radius.set(minHoleRadius)

    pm.vnnNode(bfGraph, "/input", createOutputPort=("detail_size", "float"))
    pm.vnnConnect(bfGraph, "/input.detail_size", "/mesh_to_volume.detail_size")
    bfGraph.detail_size.set(detailSize)

    pm.addAttr(ln='faceCount', at='long', keyable=True)
    bfGraph.faceCount.set(faceCount)
    pm.addAttr(ln='symmetry', at='bool', keyable=True)
    bfGraph.symmetry.set(symmetry)

    # Convert to maya mesh
    skinCageName = '{}_cage'.format(mesh)

    bfGeoToMaya = pm.createNode('bifrostGeoToMaya')
    cageMesh = pm.createNode('mesh')
    cageMesh.getParent().rename(skinCageName)

    bfGraph.outMeshes >> bfGeoToMaya.bifrostGeo
    bfGeoToMaya.mayaMesh[0] >> cageMesh.inMesh

    pm.hyperShade(cageMesh, assign='lambert1')

    # Retopologize maya mesh
    retopo = pm.polyRetopo(
        cageMesh,
        ch=False,
        symmetry=symmetry,
        axisPosition=1,
        axisOffset=0,
        axis=1,
        replaceOriginal=True,
        preprocessMesh=True,
        preserveHardEdges=False,
        topologyRegularity=1.0,
        faceUniformity=1.0,
        anisotropy=0.75,
        targetFaceCount=faceCount,
        targetFaceCountTolerance=10,
    )[0]

    bfGraph.symmetry >> retopo.symmetry
    bfGraph.faceCount >> retopo.targetFaceCount

    pm.hide(mesh, bfGraph)
    pm.select(bfGraph.getParent())

    if delHistory:
        # Clean up temp nodes
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

        pm.select(cageMesh.getParent(), r=True)

    return skinCageName


def showConvertToCageMeshUI(parent=None, *args):
    def applyBtnCallback(*args):
        meshes = pm.filterExpand(pm.selected(), sm=12)
        if not meshes:
            meshes = meshUtil.duplicateFace()
        minHoleRadius = pm.floatField('minHoleRadiusFloatFld', q=True, v=True)
        detailSize = pm.floatField('detailSizeFloatFld', q=True, v=True)
        faceCount = pm. intFieldGrp('faceCountIntFld', q=True, v1=True)
        symmetry = pm.checkBoxGrp('retopoOptions', q=True, v1=True)
        delHistory = pm.checkBoxGrp('retopoOptions', q=True, v2=True)
        convertToCageMesh(meshes, minHoleRadius, detailSize, faceCount, symmetry, delHistory)

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
    pm.checkBoxGrp('retopoOptions', numberOfCheckBoxes=2, label='', labelArray2=['Symmetry', 'Delete History'], v2=True, columnWidth=[(1, 5), (2, 70)])

    pm.setParent('..')
    pm.separator(style='in')

    pm.button(label='Apply', c=applyBtnCallback)

    pm.showWindow(winName)
