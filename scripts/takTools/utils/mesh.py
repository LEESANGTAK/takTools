import re

import maya.OpenMaya as om1
import maya.api.OpenMaya as om

import pymel.core as pm
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
        geoFaces = [face for face in sels if geo in face]
        meshFacesInfo[geo] = geoFaces

    # Duplicate meshes and delete unselected faces
    dupMeshes = []
    for mesh, faces in meshFacesInfo.items():
        dupMesh = cmds.duplicate(mesh)[0]
        dupFaces = [face.replace(mesh, dupMesh) for face in faces]

        allFacesSet = set(cmds.ls(f"{dupMesh}.f[*]", fl=True))
        selFacesSet = set(dupFaces)
        delFaces = list(allFacesSet - selFacesSet)
        cmds.delete(delFaces)

        # Remove from object sets
        dupShape = cmds.listRelatives(dupMesh, s=True, ni=True)[0]
        objSetPlugs = cmds.listConnections(dupShape, s=False, type='objectSet', exactType=True, plugs=True)

        if objSetPlugs:
            for objSetPlug in objSetPlugs:
                shapePlug = cmds.listConnections(objSetPlug, d=False, plugs=True)[0]
                cmds.disconnectAttr(shapePlug, objSetPlug)

        pm.parent(dupMesh, world=True)

        dupMeshes.append(dupMesh)

    # Merge duplicated meshes
    if len(dupMeshes) > 1:
        dupMesh = cmds.polyUnite(dupMeshes, ch=False, mergeUVSets=True)[0]
        cmds.delete(dupMeshes)
    else:
        dupMesh = dupMeshes[0]

    return dupMesh


@printElapsedTime
def separateFace(faces=None):
    if not faces:
        faces = cmds.ls(sl=True, fl=True)
    separateedMesh = duplicateFace(faces)
    cmds.delete(faces)
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


def getFaceNormalAtPosition(mesh, position):
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
    mesh = pm.PyNode(mesh)
    preSels = pm.ls(sl=True)
    pm.select(mesh, r=True)
    pm.mel.eval('PolyDisplayReset;')
    pm.select(preSels, r=True)


def restoreReferenceMesh(meshTransform):
    shapes = meshTransform.getShapes()
    for shape in shapes:
        if shape.isIntermediate():
            shape.intermediateObject.set(False)
            if not shape.isReadOnly():
                pm.delete(shape)
        else:
            pm.delete(shape)


def cleanupMesh(mesh):
    mesh = pm.PyNode(mesh)

    pm.editDisplayLayerMembers('defaultLayer', mesh)  # Add to default display layer

    pm.delete(mesh, ch=True)  # Delete inputs

    # Remove attributes except for default channelbox attributes
    for attr in mesh.listAttr(ud=True):
        try:
            pm.deleteAttr(attr)
        except:
            pass

    # Unlock channelbox
    for attr in mesh.listAttr():
        attr.unlock()

    pm.makeIdentity(mesh, apply=True)  # Freeze transformations

    shapes = mesh.getShapes()
    if not shapes:
        return

    # Delete intermediate objects
    for shape in shapes:
        if shape.isIntermediate():
            pm.delete(shape)

    for shape in mesh.getShapes():
        # pm.polyNormalPerVertex(shape, ufn=True)  # Unlock face normal
        resetPolygonDisplay(shape)  # Reset polygon display
        pm.polyMoveVertex(shape, localTranslate=(0, 0, 0))  # Set Vertex local position to default
        shape.rename('{0}Shape'.format(mesh))

    pm.delete(mesh, ch=True)  # Delete construction history


def retopology(mesh, percentage=10, symmetry=False, keepOriginal=True):
    mesh = pm.PyNode(mesh)

    newMesh = pm.polyRetopo(
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
        targetFaceCount=mesh.numFaces()*(percentage*0.01),
        targetFaceCountTolerance=10
    )

    pm.transferAttributes(
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
    pm.delete(newMesh, ch=True)

    matUtil.copyMaterial(mesh, newMesh)

    if not keepOriginal:
        pm.delete(mesh)

    return newMesh


def curveFromEdgeRing(edge, name=''):
    crv = None

    id = nameUtil.idFromComponentName(edge.name())
    edgeIds = [int(id) for id in pm.polySelect(edgeRing=id)]
    edges = [nameUtil.componentNameFromId(id, edge.node(), 'edge') for id in edgeIds]

    edges = [pm.PyNode(edge) for edge in edges]
    editPoints = []

    for edge in edges:
        midPnt = vectorUtil.getCenterVector([edge.getPoint(0, 'world'), edge.getPoint(1, 'world')])
        editPoints.append(midPnt)

    crv = pm.curve(ep=editPoints, d=3, name=name)

    return crv


def duplicateOrigMesh(meshTransform):
    meshTransform = pm.PyNode(meshTransform)

    shapes = meshTransform.getShapes()
    intermediateShapes = [shape for shape in shapes if shape.isIntermediate()]
    unIntermediateShapes = list(set(shapes) - set(intermediateShapes))

    if not intermediateShapes:
        pm.displayWarning('Object has no orig shape to duplicate.')
        return

    # Clean up intermediate shapes
    for shape in intermediateShapes:
        if shape.outputs():  # Keep valid shape that has connection
            continue
        else:
            pm.delete(shape)  # Delete unnecessary intermediate shape

    # Duplicate mesh and display origin shape
    newMeshTransform = pm.duplicate(meshTransform)[0]
    for shape in newMeshTransform.getShapes():
        if shape.isIntermediate():  # Show orig shape
            shape.intermediateObject.set(False)
        else:
            pm.delete(shape)  # Delte displayed shape

    if newMeshTransform.getParent():
        pm.parent(newMeshTransform, world=True)

    # Assign material to new mesh
    materials = matUtil.getMaterials(meshTransform)
    matUtil.assignMaterial(newMeshTransform, materials[0])


def getFaceNormal(face):
    rawFaceNormalInfo = cmds.polyInfo(face, faceNormals = True)[0]
    normalStr = re.match(r'.+:\s(.+)\n', rawFaceNormalInfo).group(1)
    normalStrLs = normalStr.split(' ')
    faceNormal = []

    for normalStr in normalStrLs:
        faceNormal.append(float(normalStr))

    return pm.dt.Vector(faceNormal)


def getVertexMap(mesh):
    mesh = pm.PyNode(mesh)

    vertexMap = {}
    leftVertices = []
    rightVertices = []
    centerVertices = []

    for vtx in mesh.vtx:
        vtxXPos = round(vtx.getPosition().x, 5)
        if vtxXPos > 0:
            leftVertices.append(vtx)
        elif vtxXPos < 0:
            rightVertices.append(vtx)
        else:
            centerVertices.append(vtx)

    for lfVtx in leftVertices:
        minDist = 100000
        symVtx = None
        lfVtxPos = lfVtx.getPosition()
        symVtxPos = pm.dt.Vector(-lfVtxPos.x, lfVtxPos.y, lfVtxPos.z)
        for rtVtx in rightVertices:
            rtVtxPos = rtVtx.getPosition()
            deltaDistance = (rtVtxPos - symVtxPos).length()
            if deltaDistance < minDist:
                minDist = deltaDistance
                symVtx = rtVtx

        vertexMap['{0}'.format(lfVtx.split('.')[-1])] = symVtx.split('.')[-1]

    return vertexMap


def mirror(vertexMap, targetMesh, side='x'):
    for leftVtx, rightVtx in vertexMap.items():
        if side == 'x':
            srcVtxPos = pm.pointPosition('{0}.{1}'.format(targetMesh, leftVtx), l=True)
            targetVtx = '{0}.{1}'.format(targetMesh, rightVtx)
        elif side == '-x':
            srcVtxPos = pm.pointPosition('{0}.{1}'.format(targetMesh, rightVtx), l=True)
            targetVtx = '{0}.{1}'.format(targetMesh, leftVtx)

        pm.xform(targetVtx, os=True, t=[-srcVtxPos[0], srcVtxPos[1], srcVtxPos[2]])


def getSymVertexMap(sourceMesh, symmetryMesh):
    srcMesh = pm.PyNode(sourceMesh)
    symMesh = pm.PyNode(symmetryMesh)

    if len(srcMesh.vtx) != len(symMesh.vtx):
        pm.error('The number of vertices of symmetry mesh must be same as the number of vertices of the source mesh.')

    symPoints = []
    for srcVtx in srcMesh.vtx:
        srcVtxPos = srcVtx.getPosition()
        symPoint = pm.dt.Point(-srcVtxPos[0], srcVtxPos[1], srcVtxPos[2])
        symPoints.append(symPoint)

    symMeshVtxs = [vtx for vtx in symMesh.vtx]
    symVtxMap = []
    for symPoint in symPoints:
        closestVtx = findClosestVtx(symPoint, symMeshVtxs)
        symVtxMap.append(closestVtx.index())
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
    source = pm.PyNode(source)
    target = pm.PyNode(target)

    for index, srcVtx in enumerate(source.vtx):
        srcVtxPos = srcVtx.getPosition(space='object')
        trgVtx = pm.PyNode('{}.vtx[{}]'.format(target, targetVerticesMap[index]))
        trgVtx.setPosition((-srcVtxPos[0], srcVtxPos[1], srcVtxPos[2]), space='object')


def getDeformedMeshes():
    deformedMeshes = []
    geos = [mesh.getTransform() for mesh in pm.ls(type='mesh')]
    for geo in geos:
        shapes = geo.getShapes()
        for shape in shapes:
            if shape.isIntermediateObject():
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
