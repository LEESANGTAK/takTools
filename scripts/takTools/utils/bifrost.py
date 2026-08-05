from maya import cmds
from . import mesh as meshUtil
from . import material as matUtil

try:
    if not cmds.pluginInfo('bifrostGraph', q=True, loaded=True):
        cmds.loadPlugin('bifrostGraph')
except RuntimeError:
    pass


def _bounding_box_size(node):
    bbox = cmds.exactWorldBoundingBox(node)
    return bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2]


def convertToCageMesh(meshes, thickening=0.5, faceCount=500, symmetry=False, delHistory=True):
    dupMeshes = cmds.duplicate(meshes, rc=True)
    try:
        cmds.parent(dupMeshes, world=True)
    except RuntimeError:
        pass

    if len(dupMeshes) > 1:
        mesh = cmds.polyUnite(dupMeshes, ch=False)[0]
    else:
        mesh = dupMeshes[0]

    width, height, depth = _bounding_box_size(mesh)
    minHoleRadius = min(width, height, depth) / 4.0

    bfGraph = cmds.createNode('bifrostGraphShape')

    cmds.vnnNode(bfGraph, '/input', createOutputPort=('inMesh', 'Object'))
    cmds.vnnNode(bfGraph, '/output', createInputPort=('outMeshes', 'array<Object>'))

    cmds.vnnCompound(bfGraph, '/', addNode='BifrostGraph,Geometry::Converters,mesh_to_volume')
    cmds.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('volume_mode', '0'))
    cmds.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('thickening', str(thickening)))
    cmds.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('store_level_set', '1'))
    cmds.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('store_fog_density', '0'))
    cmds.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('min_hole_radius', '0.01'))

    cmds.vnnCompound(bfGraph, '/', addNode='BifrostGraph,Geometry::Converters,volume_to_mesh')
    cmds.vnnNode(bfGraph, '/volume_to_mesh', createInputPort=('volumes.volume', 'auto'))

    cmds.vnnConnect(bfGraph, '/input.inMesh', '/mesh_to_volume.mesh')
    cmds.vnnConnect(bfGraph, '/mesh_to_volume.volume', '/volume_to_mesh.volumes.volume')
    cmds.vnnConnect(bfGraph, '/volume_to_mesh.meshes', '/output.outMeshes')
    cmds.connectAttr('{0}.worldMesh[0]'.format(mesh), '{0}.inMesh'.format(bfGraph), force=True)

    cmds.vnnNode(bfGraph, '/input', createOutputPort=('offset', 'float'))
    cmds.vnnConnect(bfGraph, '/input.offset', '/mesh_to_volume.offset')

    cmds.vnnNode(bfGraph, '/input', createOutputPort=('thickening', 'float'))
    cmds.vnnConnect(bfGraph, '/input.thickening', '/mesh_to_volume.thickening')
    cmds.setAttr('{0}.thickening'.format(bfGraph), thickening)

    cmds.vnnNode(bfGraph, '/input', createOutputPort=('min_hole_radius', 'float'))
    cmds.vnnConnect(bfGraph, '/input.min_hole_radius', '/mesh_to_volume.min_hole_radius')
    cmds.setAttr('{0}.min_hole_radius'.format(bfGraph), minHoleRadius)

    cmds.addAttr(bfGraph, longName='faceCount', attributeType='long', keyable=True)
    cmds.setAttr('{0}.faceCount'.format(bfGraph), faceCount)
    cmds.addAttr(bfGraph, longName='symmetry', attributeType='bool', keyable=True)
    cmds.setAttr('{0}.symmetry'.format(bfGraph), symmetry)

    skinCageName = '{0}_cage'.format(mesh)

    bfGeoToMaya = cmds.createNode('bifrostGeoToMaya')
    cageMesh = cmds.createNode('mesh')
    cageParent = cmds.listRelatives(cageMesh, parent=True, fullPath=True)[0]
    cmds.rename(cageParent, skinCageName)

    cmds.connectAttr('{0}.outMeshes'.format(bfGraph), '{0}.bifrostGeo'.format(bfGeoToMaya), force=True)
    cmds.connectAttr('{0}.mayaMesh[0]'.format(bfGeoToMaya), '{0}.inMesh'.format(skinCageName), force=True)

    cmds.select(skinCageName, r=True)
    cmds.hyperShade(assign='lambert1')

    if int(cmds.about(v=True)) >= 2024:
        retopo = cmds.polyRetopo(
            skinCageName,
            ch=False,
            symmetry=symmetry,
            axisPosition=1,
            axisOffset=0,
            axis=1,
            replaceOriginal=True,
            preprocessMesh=True,
            preserveHardEdges=True,
            topologyRegularity=1.0,
            faceUniformity=1.0,
            anisotropy=0.5,
            targetFaceCount=faceCount,
            targetFaceCountTolerance=10,
        )[0]
        cmds.connectAttr('{0}.symmetry'.format(bfGraph), '{0}.symmetry'.format(retopo), force=True)
    else:
        retopo = cmds.polyRetopo(
            skinCageName,
            ch=False,
            replaceOriginal=True,
            preprocessMesh=True,
            preserveHardEdges=True,
            topologyRegularity=1.0,
            faceUniformity=1.0,
            anisotropy=0.5,
            targetFaceCount=faceCount,
            targetFaceCountTolerance=10,
        )[0]

    cmds.connectAttr('{0}.faceCount'.format(bfGraph), '{0}.targetFaceCount'.format(retopo), force=True)

    cmds.hide(mesh, bfGraph)
    cmds.select(cmds.listRelatives(bfGraph, parent=True, fullPath=True)[0], r=True)

    if delHistory:
        cmds.delete(skinCageName, ch=True)
        cmds.delete(cmds.listRelatives(bfGraph, parent=True, fullPath=True)[0])
        cmds.delete(mesh)

    cmds.setAttr('{0}.overrideEnabled'.format(skinCageName), 1)
    cmds.setAttr('{0}.overrideColor'.format(skinCageName), 17)

    cmds.select(skinCageName, r=True)

    return skinCageName


def showConvertToCageMeshUI(parent=None, *args):
    def applyBtnCallback(*args):
        meshes = cmds.filterExpand(cmds.ls(sl=True), sm=12)
        faceMeshes = None
        if not meshes:
            faceMeshes = meshUtil.duplicateFace()

        srcMeshes = meshes or faceMeshes

        thickening = cmds.floatField('thickeningFloatFld', q=True, value=True)
        faceCount = cmds.intFieldGrp('faceCountIntFld', q=True, value1=True)
        symmetry = cmds.checkBoxGrp('retopoOptions', q=True, value1=True)
        delHistory = cmds.checkBoxGrp('retopoOptions', q=True, value2=True)

        convertToCageMesh(srcMeshes, thickening, faceCount, symmetry, delHistory)

        if faceMeshes:
            cmds.delete(faceMeshes)

    winName = 'cageMeshWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    cmds.window(winName, title='Create Cage Mesh', mnb=False, mxb=False)
    if parent:
        cmds.window(winName, e=True, p=parent)

    cmds.columnLayout(adj=True, cal='left')

    cmds.frameLayout(label='Volume Mesh Settings')
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.text(label='Thickening: ', ann='Controls the thickness of the generated volume mesh.')
    cmds.floatField('thickeningFloatFld', v=0.5, min=0.1, pre=3)

    cmds.setParent('..')
    cmds.setParent('..')

    cmds.separator(style='in')

    cmds.frameLayout(label='Retopology Settings')
    cmds.intFieldGrp('faceCountIntFld', label='Face Count:', v1=500, columnWidth=[(1, 60)])
    cmds.checkBoxGrp('retopoOptions', numberOfCheckBoxes=2, label='', labelArray2=['Symmetry', 'Delete History'], v2=False, columnWidth=[(1, 5), (2, 70)])

    cmds.setParent('..')
    cmds.separator(style='in')

    cmds.button(label='Apply', c=applyBtnCallback)

    cmds.showWindow(winName)


def quadrangulate(mesh):
    bfGraph = cmds.createNode('bifrostGraphShape')

    cmds.vnnNode(bfGraph, '/input', createOutputPort=('inMesh', 'Object'))
    cmds.vnnNode(bfGraph, '/output', createInputPort=('outMesh', 'Object'))

    cmds.vnnCompound(bfGraph, '/', addNode='BifrostGraph,TKCM::Modeling_Toolbox,quadrangulate_mesh')

    cmds.vnnConnect(bfGraph, '/input.inMesh', '/quadrangulate_mesh.mesh')
    cmds.vnnConnect(bfGraph, '/quadrangulate_mesh.new_mesh', '/output.outMesh')

    cmds.connectAttr('{0}.worldMesh[0]'.format(mesh), '{0}.inMesh'.format(bfGraph), force=True)
    bfGeoToMaya = cmds.createNode('bifrostGeoToMaya')
    quadMesh = cmds.createNode('mesh')
    cmds.connectAttr('{0}.outMesh'.format(bfGraph), '{0}.bifrostGeo'.format(bfGeoToMaya), force=True)
    cmds.connectAttr('{0}.mayaMesh[0]'.format(bfGeoToMaya), '{0}.inMesh'.format(quadMesh), force=True)

    cmds.delete(quadMesh, ch=True)
    matUtil.copyMaterial(mesh, quadMesh)

    cmds.delete(cmds.listRelatives(bfGraph, parent=True, fullPath=True))
    cmds.delete(mesh)

    cmds.rename(cmds.listRelatives(quadMesh, parent=True, fullPath=True)[0], mesh)
