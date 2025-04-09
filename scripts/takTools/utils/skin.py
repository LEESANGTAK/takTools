import os
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

import pymel.core as pm
from maya import cmds, mel

from imp import reload
from . import globalUtil; reload(globalUtil)
from . import mesh as meshUtil; reload(meshUtil)
from . import bifrost as bfUtil; reload(bfUtil)
from ..rigging import bSkinSaver as bsk


def bind(jnts, geos, maxInfluence=4):
    """
    Binds geometries with given joints.

    Args:
        jnts (list): Bind joints.
        geos (list): Geometries to bind.
        maxInfluence (int, optional): Number of influeces per point. Defaults to 1.
    """
    geoShpLs = pm.ls(geos, dag=True, ni=True, type=['mesh', 'nurbsCurve', 'nurbsSurface'])

    for geoShp in geoShpLs:
        skinClst = pm.mel.eval('findRelatedSkinCluster("%s");' % geoShp)
        if skinClst:
            pm.select(geoShp, r=True)
            pm.mel.eval('DetachSkin();')
        pm.skinCluster(jnts, geoShp, tsb=True, bm=0, wd=0, omi=False, mi=maxInfluence, dr=4.0)


def reBind(skinMesh):
    tmpDir = pm.internalVar(userTmpDir=True)
    skinFile = exportSkin(skinMesh, tmpDir)
    meshUtil.cleanupMesh(skinMesh)
    importSkin(skinFile)
    os.remove(skinFile)


def getSkinCluster(geo):
    skinClst = None
    skinClst = pm.mel.eval('findRelatedSkinCluster("%s");' % geo)
    if skinClst:
        return pm.PyNode(skinClst)
    return skinClst


def getInfluences(geo):
    infs = None
    skinClst = getSkinCluster(geo)
    if skinClst:
        infs = skinClst.getInfluence()
    return infs


def mirrorSkin(*args):
    sels = cmds.filterExpand(cmds.ls(sl=True), sm=[12, 31, 32, 34])
    if not sels:
        return
    # mesh = cmds.ls(sels, objectsOnly=True)[0]
    # influences = getInfluences(mesh)
    # topInfluence = globalUtil.getTopDagNode(influences)

    # Store current pose
    # pm.select(topInfluence, hi=True)
    # curPose = cmds.dagPose(save=True, selection=True)

    # succeed = goToBindPose(topInfluence)
    # if not succeed:
    #     pm.warning('Go to bind pose process is failed! Mirror skin weights will be performed in current pose.')

    # Mirror skin weights
    cmds.select(sels, r=True)
    cmds.copySkinWeights(mirrorMode='YZ', surfaceAssociation='closestPoint', influenceAssociation=['oneToOne', 'closestJoint'])

    # Restore current pose
    # cmds.dagPose(curPose, restore=True)
    # cmds.delete(curPose)


def copySkin(source, target, components=None):
    """
    Copy source geometry skin weights to target geometry.
    If target geometry has no skin cluster, bind with source influences.

    Args:
        source (str): Source geometry
        target (str): Target geomery
    """
    source = pm.PyNode(source)
    target = pm.PyNode(target)

    srcInfs = getInfluences(source)
    srcJointInfs = [inf for inf in srcInfs if isinstance(inf, pm.nodetypes.Joint)]
    srcGeoInfs = list(set(srcInfs) - set(srcJointInfs))
    srcSkinClst = getSkinCluster(source.name())
    targetMesh = target.node() if isinstance(target, pm.MeshVertex) else target
    trgSkinClst = getSkinCluster(targetMesh.name())

    if not trgSkinClst:
        trgSkinClst = pm.skinCluster(srcJointInfs, targetMesh, dr=4, tsb=True, nw=1)
        pm.skinCluster(trgSkinClst, e=True, ug=True, ai=srcGeoInfs)

    else:
        trgInfs = getInfluences(targetMesh)
        trgJointInfs = [inf for inf in trgInfs if isinstance(inf, pm.nodetypes.Joint)]
        trgGeoInfs = list(set(trgInfs) - set(trgJointInfs))
        addedSrcJointInfs = list(set(srcJointInfs) - set(trgJointInfs))
        addedSrcGeoInfs = list(set(srcGeoInfs) - set(trgGeoInfs))

        for srcJntInf in addedSrcJointInfs:
            pm.skinCluster(trgSkinClst, e=True, dr=4, lw=True, wt=0, ai=srcJntInf)
            pm.setAttr('%s.liw' % srcJntInf, False)
        for srcGeoInf in addedSrcGeoInfs:
            pm.skinCluster(trgSkinClst, e=True, dr=4, lw=True, wt=0, ug=True, ai=srcGeoInf)
            pm.setAttr('%s.liw' % srcGeoInf, False)

    if components:
        pm.select(source, components, r=True)
    else:
        pm.select(source, target, r=True)

    pm.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')

    skinMethod = max(pm.PyNode(srcSkinClst).skinningMethod.get(), 0)  # Prevent the value of skinning method not to be negative
    pm.PyNode(trgSkinClst).skinningMethod.set(skinMethod)
    pm.PyNode(trgSkinClst).useComponents.set(pm.PyNode(srcSkinClst).useComponents.get())

    return trgSkinClst


def copySkinSets(sourceSkinMesh, targetSets):
    for targetSet in targetSets:
        # Filter out meshes and mesh components from set members
        setMembers = cmds.ls(cmds.sets(targetSet, q=True), fl=True)
        meshes = cmds.filterExpand(setMembers, sm=12)
        meshComponents = cmds.filterExpand(setMembers, sm=[31, 32, 33])

        if meshes:
            for mesh in meshes:
                copySkin(sourceSkinMesh, mesh)

        if meshComponents:
            print(meshComponents)
            # Get cpntMeshes transforms from mesh components
            cpntMeshes = list(set(cmds.filterExpand(cmds.ls(meshComponents, o=True), sm=12)))
            # Build mesh and components info
            meshComponentsInfo = []
            for cpntMesh in cpntMeshes:
                meshCpnts = [cpnt for cpnt in meshComponents if cpntMesh in cpnt]
                meshComponentsInfo.append((cpntMesh, meshCpnts))
            # Copy skin weights to each cpntMesh and its components
            for cpntMesh, meshCpnts in meshComponentsInfo:
                copySkin(sourceSkinMesh, cpntMesh, meshCpnts)

    cmds.select(cl=True)

def copySkinOverlapVertices(sourceSkinMesh, targetMesh, searchDistance=0.001):
    overlapVtxs = meshUtil.getOverlapVertices(sourceSkinMesh, targetMesh, searchDistance)
    copySkin(sourceSkinMesh, targetMesh, components=overlapVtxs)


def duplicateSkinMesh():
    sels = cmds.ls(sl=True, fl=True)
    if cmds.nodeType(sels[0]) == "transform":
        for sel in sels:
            dupMesh = cmds.duplicate(sel, n="%s_skin" % sel)[0]
            cmds.parent(dupMesh, w=True)
            copySkin(sel, dupMesh)
    else:
        dupMesh = meshUtil.duplicateFace()
        dupMesh = cmds.rename(dupMesh, "%s_skin" % dupMesh)
        mesh = cmds.listRelatives(sels[0], p=True)[0]
        meshTrsf = cmds.listRelatives(mesh, p=True)[0]
        copySkin(meshTrsf, dupMesh)
    try:
        dupMesh.displayBorders.set(True)
    except:
        pass
    pm.select(dupMesh, r=True)

    return str(dupMesh)


def separateSkinMesh():
    sels = cmds.ls(sl=True, fl=True)

    mesh = list(set(cmds.ls(sels, objectsOnly=True)))[0]
    meshTrsf = cmds.listRelatives(mesh, p=True)[0]

    if not getSkinCluster(meshTrsf):
        cmds.warning('"{}" has no skin cluster.'.format(meshTrsf))
        meshUtil.separateFace(sels)
        return

    tempSkinMesh = cmds.duplicate(meshTrsf, n='temp_skin')[0]
    meshUtil.cleanupMesh(tempSkinMesh)
    copySkin(meshTrsf, tempSkinMesh)

    cmds.select(sels, r=True)
    sepMesh = meshUtil.separateFace()
    cmds.rename(sepMesh, "%s_skin" % sepMesh)
    copySkin(tempSkinMesh, sepMesh)

    meshUtil.cleanupMesh(meshTrsf)
    copySkin(tempSkinMesh, meshTrsf)

    cmds.delete(tempSkinMesh)


def addInfluences():
    sels = pm.selected()
    jnts = pm.ls(sels, type='joint')

    meshes = [item for item in sels if item.getShape()]
    for mesh in meshes:
        skinClst = getSkinCluster(mesh.name())
        influences = getInfluences(mesh)
        for jnt in jnts:
            if not jnt in influences:
                pm.skinCluster(skinClst, e=True, dr=4, lw=True, wt=0, ai=jnt)
                pm.setAttr('%s.liw' % jnt, False)


def getAffectedVertex(inf, minWeight):
    selVtxs = []

    inf = pm.PyNode(inf)
    skinClusters = inf.worldMatrix.listConnections()
    if not skinClusters:
        print('"{}" is not influence.'.format(inf))
        return selVtxs

    cmds.select(cl=True)

    selLs = om.MSelectionList()
    infDagPath = om.MDagPath()

    for skinCluster in skinClusters:
        skinNode = om.MObject()
        componentsSelLs = om.MSelectionList()
        weights = om.MDoubleArray()
        geoDagPath = om.MDagPath()
        vertices = om.MObject()

        # Get skin cluster function
        selLs.add(skinCluster.name())
        selLs.getDependNode(0, skinNode)
        if not skinNode.hasFn(om.MFn.kSkinClusterFilter):
            print("Warning: Selection has no related skin cluster.")
            continue
        skinFn = oma.MFnSkinCluster(skinNode)

        # Get geometry dag path
        selLs.add(inf.name())
        selLs.getDagPath(1, infDagPath)

        # Get affected points
        skinFn.getPointsAffectedByInfluence(infDagPath, componentsSelLs, weights)

        # Get vertices
        if componentsSelLs.length() >= 1:
            selIt = om.MItSelectionList(componentsSelLs)
            i = 0
            while not selIt.isDone():
                if weights[i] >= minWeight:
                    selIt.getDagPath(geoDagPath, vertices)
                i += 1
                selIt.next()
            om.MGlobal.select(geoDagPath, vertices, om.MGlobal.kAddToList)

        selLs.clear()

    selVtxs = cmds.ls(sl=True, fl=True)
    cmds.select(cl=True)

    return selVtxs


def createSkinMeshWithJoints(joints, type='ribbon'):
    jntsLength = 0
    for jnt in joints[1:]:
        jntsLength += abs(jnt.tx.get())

    width = jntsLength*0.05
    if type == 'ribbon':
        profileCurve = pm.curve(degree=1, editPoint=[(0.0, 0.0, -width), (0.0, 0.0, width)], n='profile_crv')
    elif type == 'tube':
        profileCurve = pm.circle(normal=[1, 0, 0], radius=width, n='profile_crv')[0]

    profileCurves = []
    for jnt in joints:
        dupProfileCrv = profileCurve.duplicate()
        pm.xform(dupProfileCrv, matrix=jnt.worldMatrix.get(), ws=True)
        profileCurves.append(dupProfileCrv)

    skinSurface = pm.loft(profileCurves, degree=1, sectionSpans=int(jntsLength/len(joints)), ch=False)
    skinMesh = pm.nurbsToPoly(skinSurface, format=3, polygonType=1, ch=False, n='{0}_skin'.format(joints[0]))

    pm.delete(skinSurface)
    pm.delete([profileCurve] + profileCurves)

    bind(joints[:-1], skinMesh)  # Exclude end joint for binding

    pm.select(skinMesh, r=True)


def updateBindPose(rootJoint):
    """Update bind pose with current joint orient.

    :param rootJoint: Root joint of joint hierarchy
    :type rootJoint: str
    """
    cmds.delete(cmds.dagPose(rootJoint, q=True, bindPose=True))
    cmds.dagPose(cmds.ls(rootJoint, dag=True), n='bindPose', save=True, bindPose=True)


def goToBindPose(rootJoint):
    bindPoses = pm.dagPose(rootJoint, q=True, bindPose=True)

    if len(bindPoses) > 1:
        pm.error('There is more than one bind pose. Please clean up bind poses first.')
        return False
    else:
        bindPose = bindPoses[0]

    try:
        pm.dagPose(bindPose, restore=True, g=True)
        return True
    except:
        return False


def setSolidSkinWeights(sourceVertex):
    pm.select(sourceVertex, r=True)
    pm.mel.eval('artAttrSkinWeightCopy;')
    pm.mel.eval('ConvertSelectionToShell')
    pm.mel.eval('artAttrSkinWeightPaste;')


def editSkinMesh(skinMesh):
    tempSkin = pm.duplicate(skinMesh, n='temp_skin')[0]
    tempSkin.hide()
    skinClst = copySkin(skinMesh, tempSkin)
    cmds.setAttr('{}.envelope'.format(skinClst), 0)
    meshUtil.cleanupMesh(skinMesh)
    pm.select(skinMesh, r=True)
    pm.hudButton('editSkinMeshHUD', s=3, b=4, vis=1, l='Done Edit', bw=80, bsh='roundRectangle', rc=lambda : doneEditSkinMesh(tempSkin, skinMesh))

def doneEditSkinMesh(tempSkin, skinMesh):
    meshUtil.cleanupMesh(skinMesh)
    copySkin(tempSkin, skinMesh)
    pm.delete(tempSkin)
    pm.headsUpDisplay('editSkinMeshHUD', remove=True)


def SSD(geo):
    influences = getInfluences(geo)
    topInfluence = globalUtil.getTopDagNode(influences)
    skinCluster = mel.eval('findRelatedSkinCluster("{}");'.format(geo))
    cmds.skinPercent(skinCluster, str(geo), pruneWeights=0.01)
    cmds.skinCluster(skinCluster, e=True, removeUnusedInfluence=True)
    pm.bakeDeformer(sm=geo, ss=topInfluence, dm=geo, ds=topInfluence, mi=8)


def exportSkin(mesh, outputDir):
    pm.select(mesh, r=True)
    skinFile = '{}/{}.sw'.format(outputDir, mesh)
    bsk.bSaveSkinValues(skinFile)
    return skinFile


def importSkin(skinFile):
    with open(skinFile, 'r') as f:
        fContents = f.readlines()
        mesh = fContents[0].strip('\n')
    if not cmds.objExists(mesh):
        print('"{}" is not exists. Skip importing skin weights.'.format(mesh))
        return False
    pm.select(mesh, r=True)
    bsk.bLoadSkinValues(True, skinFile)


def pruneSkinInfluences(mesh, skinClst, maxInfs):
    if cmds.nodeType(mesh) == 'transform':
        mesh = cmds.listRelatives(mesh, shapes=True, ni=True)[0]

    vertCount = cmds.polyEvaluate(mesh, vertex=True)

    cmds.progressBar('progBar', e=True, min=0, max=vertCount)

    resultMeshWeights = []
    for i in range(vertCount):
        vert = '{}.vtx[{}]'.format(mesh, i)
        infs = cmds.skinPercent(skinClst, vert, q=True, transform=None)
        weights = cmds.skinPercent(skinClst, vert, q=True, v=True)
        infWeightMap = dict(zip(infs, weights))

        sortedItems = sorted(infWeightMap.items(), key=lambda item: item[1], reverse=True)
        prunedItems = sortedItems[:maxInfs] + [(jnt, 0.0) for jnt, w in sortedItems[maxInfs:]]

        totalWeight = sum([item[1] for item in prunedItems])
        prunedItemsNormalizedMap = dict([(jnt, weight/totalWeight) for jnt, weight in prunedItems])

        resultVtxWeights = [prunedItemsNormalizedMap.get(inf) for inf in infs]
        resultMeshWeights.extend(resultVtxWeights)

        cmds.progressBar('progBar', e=True, step=1)

    return resultMeshWeights


def simplifySkin(*args):
    selComponents = cmds.filterExpand(cmds.ls(sl=True, fl=True), sm=[31, 32, 34])
    faces = cmds.polyListComponentConversion(selComponents, toFace=True)
    mesh = cmds.ls(selComponents, objectsOnly=True)[0]

    influences = getInfluences(mesh)
    topInfluence = globalUtil.getTopDagNode(influences)

    # Store current pose
    pm.select(topInfluence, hi=True)
    curPose = cmds.dagPose(save=True, selection=True)

    succeed = goToBindPose(topInfluence)
    if not succeed:
        pm.warning('Go to bind pose process is failed! Rigidfy skin weights will be performed in current pose.')

    cmds.select(faces, r=True)
    dupSkinMesh = duplicateSkinMesh()
    bbox = cmds.exactWorldBoundingBox(dupSkinMesh)
    bboxWidth = abs(bbox[3] - bbox[0])
    bboxHeight = abs(bbox[4] - bbox[1])
    bboxDepth = abs(bbox[5] - bbox[2])
    pinHoleRadius = (bboxWidth + bboxHeight + bboxDepth) / 3
    cageMesh = bfUtil.convertToCageMesh(dupSkinMesh, minHoleRadius=pinHoleRadius, detailSize=0.05, faceCount=100)

    copySkin(dupSkinMesh, cageMesh)
    copySkin(cageMesh, mesh, components=selComponents)

    cmds.delete(dupSkinMesh, cageMesh)

    # Restore current pose
    cmds.dagPose(curPose, restore=True)
    cmds.delete(curPose)

    cmds.selectMode(component=True)
    cmds.select(selComponents, r=True)
