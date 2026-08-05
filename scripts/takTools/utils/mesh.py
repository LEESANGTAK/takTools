import re

import maya.api.OpenMaya as om

from maya import cmds, mel

from . import globalUtil
from . import name as nameUtil
from . import vector as vectorUtil
from . import material as matUtil
from .decorators import printElapsedTime


def duplicateFace(faces=None):
    dupMesh = None

    # Get selected faces
    if not faces:
        sels = cmds.ls(sl=True, fl=True)
        if not sels:
            return dupMesh

        faces = []
        # Filter faces
        filteredFaces = cmds.filterExpand(sels, sm=34)
        if filteredFaces:
            faces.extend(filteredFaces)

        # Filter vertices and edges then convert to faces
        vtxsEdges = cmds.filterExpand(sels, sm=[31, 32])
        if vtxsEdges:
            convertedFaces = cmds.polyListComponentConversion(vtxsEdges, toFace=True)
            faces.extend(convertedFaces)

    # Get mesh faces info
    meshes = list(set(cmds.ls(faces, objectsOnly=True)))
    geos = [cmds.listRelatives(mesh, p=True)[0] for mesh in meshes]
    meshFacesInfo = {}
    for geo in geos:
        geoFaces = [face for face in faces if geo in face]
        meshFacesInfo[geo] = geoFaces

    # Duplicate meshes and delete unselected faces
    dupMeshes = []
    for mesh, faces in meshFacesInfo.items():
        dupMesh = cmds.duplicate(mesh, rc=True)[0]
        dupFaces = [face.replace(mesh, dupMesh) for face in faces]

        allFacesSet = set(cmds.ls(f"{dupMesh}.f[*]", fl=True))
        selFacesSet = set(cmds.ls(dupFaces, fl=True))
        delFaces = list(allFacesSet - selFacesSet)
        cmds.delete(delFaces)

        # Remove from object sets
        dupShape = cmds.listRelatives(dupMesh, s=True, ni=True)[0]
        objSetPlugs = cmds.listConnections(dupShape, s=False, type='objectSet', exactType=True, plugs=True)

        if objSetPlugs:
            for objSetPlug in objSetPlugs:
                shapePlug = cmds.listConnections(objSetPlug, d=False, plugs=True)[0]
                cmds.disconnectAttr(shapePlug, objSetPlug)

        cmds.parent(dupMesh, world=True)

        dupMeshes.append(dupMesh)

    # Merge duplicated meshes
    if len(dupMeshes) > 1:
        dupMesh = cmds.polyUnite(dupMeshes, ch=False, mergeUVSets=True)[0]
        for item in dupMeshes:
            if cmds.objExists(item):
                cmds.delete(item)
    else:
        dupMesh = dupMeshes[0]

    cleanupMesh(dupMesh)

    cmds.select(dupMesh, r=True)

    return dupMesh


@printElapsedTime
def separateFace(faces=None):
    if not faces:
        faces = cmds.ls(sl=True, fl=True)
    separateedMesh = duplicateFace(faces)
    cmds.delete(faces)
    cmds.select(separateedMesh, r=True)

    return separateedMesh


def getPoint(mesh, vtxID):
    dagPath = globalUtil.getDagPath(mesh)
    meshVtxIt = om.MItMeshVertex(dagPath)
    while not meshVtxIt.isDone():
        if meshVtxIt.index() == vtxID:
            return meshVtxIt.position()
        meshVtxIt.next()


def getPoints(mesh):
    dagPath = globalUtil.getDagPath(mesh)
    fnMesh = om.MFnMesh(dagPath)
    return fnMesh.getPoints()


def getNormalAtPosition(mesh, position):
    meshFn = om.MFnMesh(globalUtil.getDagPath(mesh))
    point = om.MPoint(position)
    normal = meshFn.getClosestNormal(point, space=om.MSpace.kWorld)
    return normal[0]


def getClosestPointUV(mesh, position):
    """Get closest uv from given mesh and position.

    Args:
        mesh (str): Mesh name.
        position (list): XYZ position value.

    Returns:
        tuple: U and V value.
    """
    closestUV = None

    meshFn = om.MFnMesh(globalUtil.getDagPath(mesh))
    point = om.MPoint(position)
    closestPnt = meshFn.getClosestPoint(point, om.MSpace.kWorld)[0]
    closestUV = meshFn.getUVAtPoint(closestPnt, om.MSpace.kWorld)[:2]

    return closestUV


def getClosestVertexPoint(mesh, point):
    meshVtxIt = om.MItMeshVertex(globalUtil.getDagPath(mesh))
    maxDist = 100000
    closestVertexPoint = om.MPoint()
    while not meshVtxIt.isDone():
        deltaVec = meshVtxIt.position() - point
        if deltaVec.length() < maxDist:
            closestVertexPoint = meshVtxIt.position()
            maxDist = deltaVec.length()
        meshVtxIt.next()
    return closestVertexPoint


def getFarthestVertexPoint(mesh, point):
    meshVtxIt = om.MItMeshVertex(globalUtil.getDagPath(mesh))
    minDist = 0.0001
    farthestVertexPoint = om.MPoint()
    while not meshVtxIt.isDone():
        deltaVec = meshVtxIt.position() - point
        if deltaVec.length() > minDist:
            farthestVertexPoint = meshVtxIt.position()
            minDist = deltaVec.length()
        meshVtxIt.next()
    return farthestVertexPoint


def getClosestVertices(source, target):
    """Get closest vertices of target mesh from source mesh.

    Args:
        source (str): Source mesh name.
        target (str): Target mesh name.

    Returns:
        list: Closest target vertices name.
    """
    srcDagPath = globalUtil.getDagPath(source)
    trgDagPath = globalUtil.getDagPath(target)

    srcVtxIt = om.MItMeshVertex(srcDagPath)
    trgMeshFn = om.MFnMesh(trgDagPath)

    closestVerticesId = []
    while not srcVtxIt.isDone():
        srcVtxWsPnt = srcVtxIt.position(om.MSpace.kWorld)

        result = trgMeshFn.getClosestPoint(srcVtxWsPnt, om.MSpace.kWorld)  # result is (closestPointID, faceID)
        trgVtxIds = trgMeshFn.getPolygonVertices(result[1])
        closestTrgVtxId = None
        minDist = 99999999.0

        for trgVtxId in trgVtxIds:
            vtxWsPos = trgMeshFn.getPoint(trgVtxId, om.MSpace.kWorld)
            trgVtxToSrcVtxDist = vtxWsPos.distanceTo(srcVtxWsPnt)

            if trgVtxToSrcVtxDist < 0.00001:
                closestTrgVtxId = trgVtxId
                break

            if trgVtxToSrcVtxDist < minDist:
                minDist = trgVtxToSrcVtxDist
                closestTrgVtxId = trgVtxId

        closestVerticesId.append(closestTrgVtxId)

        srcVtxIt.next()

    closestVertices = [nameUtil.componentNameFromId(id, trgDagPath.partialPathName(), 'vertex') for id in closestVerticesId]
    return closestVertices


def getOverlapVertices(source, target, searchDist=0.001):
    """Get overlaped vertices of target mesh from source mesh.

    Args:
        source (str): Source mesh name.
        target (str): Target mesh name.
        searchDist (float, optional): Search distance. Defaults to 0.1.

    Returns:
        list: Overlaped vertices name.
    """
    srcDagPath = globalUtil.getDagPath(source)
    trgDagPath = globalUtil.getDagPath(target)

    srcMeshFn = om.MFnMesh(srcDagPath)
    trgGeoIt = om.MItGeometry(trgDagPath)

    trgLocalToWorldMatrix = om.MFloatMatrix(trgDagPath.inclusiveMatrix())
    overlapVerticesId = []
    while not trgGeoIt.isDone():
        trgVtxWsPnt = om.MFloatPoint(trgGeoIt.position()) * trgLocalToWorldMatrix
        trgVtxWsNormal = om.MFloatVector(trgGeoIt.normal()) * trgLocalToWorldMatrix

        results = srcMeshFn.closestIntersection(trgVtxWsPnt, trgVtxWsNormal, om.MSpace.kWorld, searchDist, True)
        if results:
            closestPnt = results[0]
            if not closestPnt.isEquivalent(om.MFloatPoint.kOrigin):
                overlapVerticesId.append(trgGeoIt.index())
        trgGeoIt.next()

    overlapVertices = [nameUtil.componentNameFromId(id, trgDagPath.partialPathName(), 'vertex') for id in overlapVerticesId]
    return overlapVertices


def resetPolygonDisplay(mesh):
    mesh = str(mesh)
    preSels = cmds.ls(sl=True)
    cmds.select(mesh, r=True)
    mel.eval('PolyDisplayReset;')
    if preSels:
        cmds.select(preSels, r=True)
    else:
        cmds.select(clear=True)


def restoreReferenceMesh(meshTransform):
    meshTransform = str(meshTransform)
    shapes = cmds.listRelatives(meshTransform, s=True, fullPath=True) or []
    for shape in shapes:
        intermediate = cmds.getAttr('{}.intermediateObject'.format(shape))
        if intermediate:
            cmds.setAttr('{}.intermediateObject'.format(shape), False)
            try:
                is_ref = cmds.referenceQuery(shape, isNodeReferenced=True)
            except RuntimeError:
                is_ref = False

            if not is_ref:
                cmds.delete(shape)
        else:
            cmds.delete(shape)


def cleanupMesh(mesh):
    mesh = str(mesh)

    cmds.editDisplayLayerMembers('defaultLayer', mesh)  # Add to default display layer

    cmds.delete(mesh, ch=True)  # Delete inputs

    # Remove attributes except for default channelbox attributes
    for attr in cmds.listAttr(mesh, ud=True) or []:
        try:
            cmds.deleteAttr(attr)
        except RuntimeError:
            pass

    # Unlock channelbox
    for attr in cmds.listAttr(mesh) or []:
        try:
            cmds.setAttr(attr, lock=False)
        except RuntimeError:
            pass

    cmds.makeIdentity(mesh, apply=True)  # Freeze transformations

    shapes = cmds.listRelatives(mesh, s=True, fullPath=True) or []
    if not shapes:
        return

    # Delete intermediate objects
    for shape in shapes:
        if cmds.getAttr('{}.intermediateObject'.format(shape)):
            cmds.delete(shape)

    shapes = cmds.listRelatives(mesh, s=True, fullPath=True) or []
    for shape in shapes:
        resetPolygonDisplay(shape)  # Reset polygon display
        cmds.polyMoveVertex(shape, localTranslate=(0, 0, 0))  # Set Vertex local position to default
        shape_base = shape.split('|')[-1]
        cmds.rename(shape, '{0}Shape'.format(mesh))

    cmds.delete(mesh, ch=True)  # Delete construction history


def retopology(mesh, percentage=10, symmetry=False, keepOriginal=True):
    mesh = str(mesh)
    faceCount = cmds.polyEvaluate(mesh, face=True)

    newMesh = cmds.polyRetopo(
        mesh,
        caching=1,
        constructionHistory=0,
        symmetry=symmetry,
        axisPosition=1,
        axisOffset=0,
        axis=1,
        replaceOriginal=0,
        preprocessMesh=1,
        preserveHardEdges=0,
        topologyRegularity=0.5,
        faceUniformity=0,
        anisotropy=0.75,
        targetFaceCount=faceCount * (percentage * 0.01),
        targetFaceCountTolerance=10
    )

    cmds.transferAttributes(
        mesh, newMesh,
        transferPositions=0,
        transferNormals=0,
        transferUVs=2,
        transferColors=0,
        sampleSpace=0,
        sourceUvSpace="map1",
        targetUvSpace="map1",
        searchMethod=3,
        flipUVs=0,
        colorBorders=1
    )
    cmds.delete(newMesh, ch=True)

    matUtil.copyMaterial(mesh, newMesh)

    if not keepOriginal:
        cmds.delete(mesh)

    return newMesh


def curveFromEdgeRing(edge, name=''):
    edge = str(edge)
    edgeNode = edge.split('.')[0]
    edgeId = nameUtil.idFromComponentName(edge)
    edgeIds = [int(id) for id in cmds.polySelect(edgeRing=edgeId)]
    edges = [nameUtil.componentNameFromId(id, edgeNode, 'edge') for id in edgeIds]

    editPoints = []
    for edgeComp in edges:
        verts = cmds.ls(cmds.polyListComponentConversion(edgeComp, toVertex=True), fl=True) or []
        if len(verts) < 2:
            continue

        pt0 = cmds.pointPosition(verts[0], w=True)
        pt1 = cmds.pointPosition(verts[1], w=True)
        midPnt = vectorUtil.getCenterVector([pt0, pt1])
        editPoints.append(midPnt)

    crv = cmds.curve(ep=editPoints, d=3, name=name)
    return crv


def duplicateOrigMesh(meshTransform):
    meshTransform = str(meshTransform)

    shapes = cmds.listRelatives(meshTransform, s=True, fullPath=True) or []
    intermediateShapes = [shape for shape in shapes if cmds.getAttr('{}.intermediateObject'.format(shape))]

    if not intermediateShapes:
        cmds.warning('Object has no orig shape to duplicate.')
        return

    # Clean up intermediate shapes
    for shape in intermediateShapes:
        if cmds.listConnections(shape, s=False, d=True):  # Keep valid shape that has connection
            continue
        else:
            cmds.delete(shape)  # Delete unnecessary intermediate shape

    # Duplicate mesh and display origin shape
    newMeshTransform = cmds.duplicate(meshTransform)[0]
    shapes = cmds.listRelatives(newMeshTransform, s=True, fullPath=True) or []
    for shape in shapes:
        if cmds.getAttr('{}.intermediateObject'.format(shape)):  # Show orig shape
            cmds.setAttr('{}.intermediateObject'.format(shape), False)
            cmds.rename(shape, '{0}Shape'.format(newMeshTransform.split('|')[-1]))
        else:
            cmds.delete(shape)  # Delete displayed shape

    if cmds.listRelatives(newMeshTransform, p=True):
        cmds.parent(newMeshTransform, world=True)

    # Assign material to new mesh
    materials = matUtil.getMaterials(meshTransform)
    matUtil.assignMaterial(newMeshTransform, materials[0])


def getFaceNormal(face):
    rawFaceNormalInfo = cmds.polyInfo(face, faceNormals=True)[0]
    normalStr = re.match(r'.+:\s(.+)\n', rawFaceNormalInfo).group(1)
    normalStrLs = normalStr.split(' ')
    faceNormal = [float(normalStr) for normalStr in normalStrLs]
    return om.MVector(faceNormal)


def getVertexMap(mesh):
    mesh = str(mesh)

    vertexMap = {}
    leftVertices = []
    rightVertices = []
    centerVertices = []

    vertices = cmds.ls('{}.vtx[*]'.format(mesh), fl=True) or []
    for vtx in vertices:
        vtxXPos = round(cmds.pointPosition(vtx, w=True)[0], 5)
        if vtxXPos > 0:
            leftVertices.append(vtx)
        elif vtxXPos < 0:
            rightVertices.append(vtx)
        else:
            centerVertices.append(vtx)

    for lfVtx in leftVertices:
        minDist = 100000
        symVtx = None
        lfVtxPos = om.MPoint(cmds.pointPosition(lfVtx, w=True))
        symVtxPos = om.MPoint(-lfVtxPos.x, lfVtxPos.y, lfVtxPos.z)
        for rtVtx in rightVertices:
            rtVtxPos = om.MPoint(cmds.pointPosition(rtVtx, w=True))
            deltaDistance = rtVtxPos.distanceTo(symVtxPos)
            if deltaDistance < minDist:
                minDist = deltaDistance
                symVtx = rtVtx

        vertexMap['{0}'.format(lfVtx.split('.')[-1])] = symVtx.split('.')[-1]

    return vertexMap


def mirror(vertexMap, targetMesh, side='x'):
    for leftVtx, rightVtx in vertexMap.items():
        if side == 'x':
            srcVtxPos = cmds.pointPosition('{0}.{1}'.format(targetMesh, leftVtx), l=True)
            targetVtx = '{0}.{1}'.format(targetMesh, rightVtx)
        elif side == '-x':
            srcVtxPos = cmds.pointPosition('{0}.{1}'.format(targetMesh, rightVtx), l=True)
            targetVtx = '{0}.{1}'.format(targetMesh, leftVtx)

        cmds.xform(targetVtx, os=True, t=[-srcVtxPos[0], srcVtxPos[1], srcVtxPos[2]])


def getSymVertexMap(sourceMesh, symmetryMesh):
    sourceMesh = str(sourceMesh)
    symmetryMesh = str(symmetryMesh)

    srcVertices = cmds.ls('{}.vtx[*]'.format(sourceMesh), fl=True) or []
    symVertices = cmds.ls('{}.vtx[*]'.format(symmetryMesh), fl=True) or []

    if len(srcVertices) != len(symVertices):
        cmds.error('The number of vertices of symmetry mesh must be same as the number of vertices of the source mesh.')

    symPoints = []
    for srcVtx in srcVertices:
        srcVtxPos = cmds.pointPosition(srcVtx, w=True)
        symPoint = om.MPoint(-srcVtxPos[0], srcVtxPos[1], srcVtxPos[2])
        symPoints.append(symPoint)

    symVtxMap = []
    symMeshVtxs = list(symVertices)
    for symPoint in symPoints:
        closestVtx = findClosestVtx(symPoint, symMeshVtxs)
        symVtxMap.append(int(closestVtx.split('[')[-1].strip(']')))
        symMeshVtxs.remove(closestVtx)

    return symVtxMap


def findClosestVtx(searchPoint, vertices):
    minDist = 1000000
    closestVtx = None
    for vtx in vertices:
        vtxPoint = vtx.getPosition()
        searchPntToVtxDist = (vtxPoint - searchPoint).length()
        if searchPntToVtxDist < minDist:
            minDist = searchPntToVtxDist
            closestVtx = vtx
    return closestVtx


def symmeterizeMesh(targetVerticesMap, source, target):
    source = str(source)
    target = str(target)

    for index, srcVtxIndex in enumerate(targetVerticesMap):
        srcVtx = '{0}.vtx[{1}]'.format(source, index)
        srcVtxPos = cmds.pointPosition(srcVtx, o=True)
        trgVtx = '{0}.vtx[{1}]'.format(target, srcVtxIndex)
        cmds.xform(trgVtx, os=True, t=(-srcVtxPos[0], srcVtxPos[1], srcVtxPos[2]))


def getDeformedMeshes():
    deformedMeshes = []
    meshes = cmds.ls(type='mesh', long=True) or []
    for mesh in meshes:
        geo = cmds.listRelatives(mesh, p=True, fullPath=True)
        if not geo:
            continue
        geo = geo[0]
        shapes = cmds.listRelatives(geo, s=True, fullPath=True) or []
        for shape in shapes:
            if cmds.getAttr('{}.intermediateObject'.format(shape)):
                deformedMeshes.append(geo)
    return list(set(deformedMeshes))


def moveToOrigin(meshes):
    # Get the bottom center point of the bounding box with meshes
    bbox = getBoundingBox(meshes)
    ctPnt = bbox.center
    minPnt = bbox.min
    botCtPnt = om.MPoint(ctPnt.x, minPnt.y, ctPnt.z)

    # Get a delta from meshes bottom center point to world origin point
    origPnt = om.MPoint(0, 0, 0)
    botToOrigDelta = origPnt - botCtPnt

    # Move vertices
    for mesh in meshes:
        meshDag = globalUtil.getDagPath(mesh)
        vtxIt = om.MItMeshVertex(meshDag)
        while not vtxIt.isDone():
            pnt = vtxIt.position(space=om.MSpace.kWorld)
            vtxIt.setPosition(pnt + botToOrigDelta, space=om.MSpace.kWorld)
            vtxIt.next()


def getBoundingBox(meshes):
    bbox = om.MBoundingBox()

    for mesh in meshes:
        meshDag = globalUtil.getDagPath(mesh)
        vtxIt = om.MItMeshVertex(meshDag)
        while not vtxIt.isDone():
            pnt = vtxIt.position(space=om.MSpace.kWorld)
            bbox.expand(pnt)
            vtxIt.next()

    return bbox


def toggleDeformers(mesh=''):
    history = cmds.listHistory(mesh, pruneDagObjects=True)
    deformers = cmds.ls(history, type="geometryFilter")

    if deformers:
        for dfm in deformers:
            curEnv = cmds.getAttr('{}.envelope'.format(dfm))
            reverseEnv = int(not curEnv)
            cmds.setAttr('{}.envelope'.format(dfm), reverseEnv)
            print('"{}": {} {}'.format(mesh, dfm, reverseEnv))
    else:
        print("No deformers found on {}.".format(mesh))


def setAverageNormalBorder(meshes):
    """Set average vertex normal for border edges of given meshes."""
    # Create a temporary mesh for averaging normals
    tempMeshes = cmds.duplicate(meshes)
    combinedTempMesh = cmds.polyUnite(tempMeshes, ch=False)[0]
    cmds.polyMergeVertex(combinedTempMesh, d=0.001, ch=False)
    cmds.polyAverageNormal(combinedTempMesh)

    # Get border edges
    borderEdgesInfo = {}
    for mesh in meshes:
        borderEdgesInfo[mesh] = getBorderEdges(mesh)

    # Convert border edges to border vertices info
    borderVerticesInfo = {}
    for mesh, borderEdges in borderEdgesInfo.items():
        borderVertices = []
        for borderEdge in borderEdges:
            borderVertices.extend(cmds.ls(cmds.polyListComponentConversion(borderEdge, toVertex=True), fl=True))
        borderVerticesInfo[mesh] = list(set(borderVertices))

    # Use Maya API to set the vertex normal
    for mesh, borderVertices in borderVerticesInfo.items():
        dagPath = globalUtil.getDagPath(mesh)
        meshFn = om.MFnMesh(dagPath)
        for borderVtx in borderVertices:
            borderVtxPos = cmds.pointPosition(borderVtx, w=True)
            normal = getNormalAtPosition(combinedTempMesh, borderVtxPos)
            vtxIndex = int(borderVtx.split('.vtx[')[-1].strip(']'))
            meshFn.setVertexNormal(normal, vtxIndex, om.MSpace.kWorld)

    cmds.delete(meshes, ch=True)
    cmds.delete(combinedTempMesh)


def getBorderEdges(mesh):
    selection_list = om.MSelectionList()
    selection_list.add(mesh)

    try:
        dag_path = selection_list.getDagPath(0)
        border_edge_indices = []

        edge_iter = om.MItMeshEdge(dag_path)
        while not edge_iter.isDone():
            if edge_iter.onBoundary():
                border_edge_indices.append(edge_iter.index())
            edge_iter.next()

        if border_edge_indices:
            mesh_name = dag_path.partialPathName()
            border_edge_components = [f'{mesh_name}.e[{index}]' for index in border_edge_indices]
        else:
            print("Cannot find border edges.")

        return border_edge_components

    except Exception as e:
        om.MGlobal.displayError(f"Error occurred: {e}")
        return None
