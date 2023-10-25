import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

import pymel.core as pm
import maya.cmds as cmds

from . import globalUtil
from . import mesh as meshUtil
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
    tempSkinMesh = pm.duplicate(skinMesh, n='{0}_tempSkin'.format(skinMesh))[0]
    copySkin(skinMesh, tempSkinMesh)
    pm.delete(skinMesh, ch=True)
    copySkin(tempSkinMesh, skinMesh)
    pm.delete(tempSkinMesh)


def getSkinCluster(geo):
    skinClst = pm.mel.eval('findRelatedSkinCluster("%s");' % geo)
    if skinClst:
        return pm.PyNode(skinClst)
    return None


def getInfluences(geo):
    skinClst = getSkinCluster(geo)
    infs = skinClst.getInfluence()
    return infs


def mirrorSkin(geo, searchStr, replaceStr):
    oppInfs = [inf.replace(searchStr, replaceStr) for inf in getInfluences(geo)]
    oppGeo = geo.replace(searchStr, replaceStr)
    srcSkinClst = getSkinCluster(geo)
    trgSkinclst = pm.skinCluster(oppInfs, oppGeo)
    pm.select(geo, oppGeo, r=True)
    pm.copySkinWeights(ss=srcSkinClst, ds=trgSkinclst, mirrorMode='YZ')


def copySkin(source, target, components=None):
    """
    Copy source geometry skin weights to target geometry.
    If target geometry has no skin cluster, bind with source influences.

    Args:
        source (str): Source geometry
        target (str): Target geomery
        components (list, optional): Vertex list. Defaults to None.
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

    pm.PyNode(trgSkinClst).skinningMethod.set(pm.PyNode(srcSkinClst).skinningMethod.get())
    pm.PyNode(trgSkinClst).useComponents.set(pm.PyNode(srcSkinClst).useComponents.get())


def copySkinOverlapVertices(sourceSkinMesh, targetMesh):
    overlapVtxs = meshUtil.getOverlapVertices(sourceSkinMesh, targetMesh)
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
        dupMesh.rename("%s_skin" % dupMesh)
        mesh = cmds.listRelatives(sels[0], p=True)[0]
        meshTrsf = cmds.listRelatives(mesh, p=True)[0]
        copySkin(meshTrsf, dupMesh)
    dupMesh.displayBorders.set(True)
    cmds.select(cl=True)


def separateSkinMesh():
    sels = cmds.ls(sl=True, fl=True)

    mesh = cmds.listRelatives(sels[0], p=True)[0]
    meshTrsf = cmds.listRelatives(mesh, p=True)[0]

    tempSkinMesh = cmds.duplicate(meshTrsf, n='temp_skin')[0]
    meshUtil.cleanupMesh(tempSkinMesh)
    copySkin(meshTrsf, tempSkinMesh)

    cmds.select(sels, r=True)
    sepMesh = meshUtil.separateFace()
    sepMesh.rename("%s_skin" % sepMesh)
    copySkin(tempSkinMesh, sepMesh)

    meshUtil.cleanupMesh(meshTrsf)
    copySkin(tempSkinMesh, meshTrsf)

    cmds.delete(tempSkinMesh)


def addInfluences():
    sels = pm.selected()
    jnts = [item for item in sels if item.nodeType() == 'joint']
    meshes = [item for item in sels if item.getShape()]

    for mesh in meshes:
        skinClst = getSkinCluster(mesh.name())
        influences = getInfluences(mesh)
        for jnt in jnts:
            if not jnt in influences:
                pm.skinCluster(skinClst, e=True, dr=4, lw=True, wt=0, ai=jnt)
                pm.setAttr('%s.liw' % jnt, False)


def getAffectedVertex(inf, minWeight):
    inf = pm.PyNode(inf)
    skinClusters = inf.worldMatrix.listConnections()

    pm.select(cl=True)

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
            continue
        skinFn = oma.MFnSkinCluster(skinNode)

        # Get geometry dag path
        selLs.add(inf.name())
        selLs.getDagPath(1, infDagPath)

        # Get affected points
        skinFn.getPointsAffectedByInfluence(infDagPath, componentsSelLs, weights)

        # Get vertices
        if componentsSelLs.length() >= 1:
            componentsSelLs.getDagPath(0, geoDagPath, vertices)
            om.MGlobal.select(geoDagPath, vertices, om.MGlobal.kAddToList)

        selLs.clear()

    return pm.selected()


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


def updateBindPose(rootJoint):
    """Update bind pose with current joint orient.

    :param rootJoint: Root joint of joint hierarchy
    :type rootJoint: str
    """
    bindPose = pm.dagPose(rootJoint, q=True, bindPose=True)
    bindPoseMembers = pm.dagPose(bindPose, q=True, members=True)
    for bpMember in bindPoseMembers:
        pm.dagPose(bpMember, reset=True, n=bindPose[0])


def setSolidSkinWeights(sourceVertex):
    pm.select(sourceVertex, r=True)
    pm.mel.eval('artAttrSkinWeightCopy;')
    pm.mel.eval('ConvertSelectionToShell')
    pm.mel.eval('artAttrSkinWeightPaste;')


def editSkinMesh(skinMesh):
    # duplicate skin geometry for saving skin weights
    tempMesh = pm.duplicate(skinMesh, n='tempMesh')[0]
    meshUtil.cleanupMesh(tempMesh)
    tempMesh.v.set(False)

    copySkin(skinMesh, tempMesh)
    meshUtil.cleanupMesh(skinMesh)
    pm.select(skinMesh, r=True)
    pm.hudButton('editSkinMeshHUD', s=3, b=4, vis=1, l='Done Edit', bw=80, bsh='roundRectangle', rc=lambda : doneEditSkinMesh(skinMesh, tempMesh))

def doneEditSkinMesh(skinMesh, tempMesh):
    pm.headsUpDisplay('editSkinMeshHUD', remove=True)
    meshUtil.cleanupMesh(skinMesh)
    copySkin(tempMesh, skinMesh)
    pm.delete(tempMesh)


def SSD(geo):
    influences = getInfluences(geo)
    topInfluence = globalUtil.getTopDagNode(influences)
    pm.bakeDeformer(sm=geo, ss=topInfluence, dm=geo, ds=topInfluence, mi=8)


def saveBSkin(outputDir, mesh):
    pm.select(mesh, r=True)
    skinFile = '{}/{}.sw'.format(outputDir, mesh)
    bsk.bSaveSkinValues(skinFile)
    return skinFile


def loadBSkin(skinFile):
    with open(skinFile, 'r') as f:
        fContents = f.readlines()
        mesh = fContents[0]
    pm.select(mesh, r=True)
    bsk.bLoadSkinValues(True, skinFile)
