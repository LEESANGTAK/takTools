import os
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

from maya import cmds, mel

from importlib import reload
from . import globalUtil; reload(globalUtil)
from . import mesh as meshUtil; reload(meshUtil)
from . import bifrost as bfUtil; reload(bfUtil)
from ..rigging import bSkinSaver as bsk
from ..rigging import sculptSkinAPI as ssAPI


def removeLockWeightsInputConnection(joints=[]):
    if not joints:
        joints = cmds.ls(type='joint')

    for jnt in joints:
        attr = jnt+'.lockInfluenceWeights'
        if not cmds.objExists(attr):
            continue
        inConnection = cmds.listConnections(attr, s=True, d=False, plugs=True)
        if inConnection:
            cmds.disconnectAttr(inConnection[0], attr)


def bind(jnts, geos, maxInfluence=4):
    """
    Binds geometries with given joints.

    Args:
        jnts (list): Bind joints.
        geos (list): Geometries to bind.
        maxInfluence (int, optional): Number of influeces per point. Defaults to 1.
    """
    removeLockWeightsInputConnection(jnts)

    geoShpLs = cmds.ls(geos, dag=True, ni=True, type=['mesh', 'nurbsCurve', 'nurbsSurface'])

    for geoShp in geoShpLs:
        skinClst = mel.eval('findRelatedSkinCluster("%s");' % geoShp)
        if skinClst:
            cmds.select(geoShp, r=True)
            mel.eval('DetachSkin();')
        cmds.skinCluster(jnts, geoShp, tsb=True, bm=0, wd=0, omi=False, mi=maxInfluence, dr=4.0)


def reBind(skinMesh):
    tmpDir = cmds.internalVar(userTmpDir=True)
    skinFile = exportSkin(skinMesh, tmpDir)
    meshUtil.cleanupMesh(skinMesh)
    importSkin(skinFile)
    os.remove(skinFile)


def getSkinCluster(geo):
    skinClst = None
    skinClst = mel.eval('findRelatedSkinCluster("%s");' % geo)
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

    # Mirror skin weights
    cmds.select(sels, r=True)
    cmds.copySkinWeights(mirrorMode='YZ', surfaceAssociation='closestPoint', influenceAssociation=['closestJoint', 'oneToOne'])


def addInfCopySkin(source=None, targets=None):
    '''
    Add source skin geometry's influences to the target geoemtry if not exists in the target skin geometry.
    And copy skin weights.
    '''

    removeLockWeightsInputConnection()

    # When no source and no targets are given, get the first selected object as source and the rest as targets.
    if not source and not targets:
        sels = cmds.ls(os=True, fl=True)

        # Filter components and geometries
        components = cmds.filterExpand(sels, sm=[28, 31, 32, 34]) or []  # Components that in a object set are filtered also
        geometries = cmds.filterExpand(sels, sm=[9, 10, 12]) or []

        # Get source and targets depends on selection state
        if components and len(geometries) == 1:  # When components are selected as targets
            source = geometries[0]
            targets = components
        elif len(geometries) > 1:  # When geometries are selected as targets
            source = sels[0]
            targets = sels[1:]
            # Store shape visibility state and turn on visibility for targets
            targetsShapeVisInfo = []
            for trgSkinGeo in targets:
                shapes = cmds.listRelatives(trgSkinGeo, s=True, ni=True)
                if shapes:
                    shapeVisStateInfo = {}
                    for shape in shapes:
                        visState = cmds.getAttr(f'{shape}.visibility')
                        shapeVisStateInfo[shape] = visState
                        cmds.setAttr(f'{shape}.visibility', True)
                    targetsShapeVisInfo.append(shapeVisStateInfo)
                else:
                    targets.remove(trgSkinGeo)
                    cmds.warning(f'"{trgSkinGeo}" has no valid shapes. Skip copy skin operation for the "{trgSkinGeo}".')

    # Store shape visibility state and turn on visibility for the source
    srcShape = source if cmds.nodeType(source) == 'mesh' else cmds.listRelatives(source, s=True, ni=True)[0]
    srcShapeVisState = cmds.getAttr('{}.visibility'.format(srcShape))
    cmds.setAttr('{}.visibility'.format(srcShape), True)

    # Check if targets are valid
    if not targets:
        cmds.error('No targets found.')
    if not isinstance(targets, list):
        cmds.error('Targets should be a list')

    # Get source skin cluster and influences
    cmds.select(source, r=True)
    srcSkinClst = mel.eval('findRelatedSkinCluster("%s");' % source)
    srcInfs = cmds.skinCluster(srcSkinClst, q=True, inf=True)

    trgSkinClsts = []
    if components:
        # Get targets info
        componentShapes = list(set(cmds.ls(components, objectsOnly=True)))
        componentObjects = [cmds.listRelatives(shape, parent=True)[0] for shape in componentShapes]
        targetsInfo = {}
        for object in componentObjects:
            objectComponents = [component for component in components if object in component]
            targetsInfo[object] = objectComponents

        for trgSkinGeo, targetComponents in targetsInfo.items():
            trgSkinClst = mel.eval('findRelatedSkinCluster("%s");' % trgSkinGeo)

            # Bind target skin geo with source influences if target skin geo has not a skin cluster
            if not trgSkinClst:
                cmds.skinCluster(srcInfs, trgSkinGeo, mi=4, dr=4, tsb=True, omi=False, nw=1)
                trgSkinClst = mel.eval('findRelatedSkinCluster("%s");' % trgSkinGeo)

            # Add source influences if not in the target influences
            trgInfs = cmds.skinCluster(trgSkinClst, q=True, inf=True)
            for srcInf in srcInfs:
                if srcInf in trgInfs:
                    continue
                cmds.skinCluster(trgSkinClst, e=True, dr=4, lw=True, wt=0, ai=srcInf)
                cmds.setAttr('%s.liw' % srcInf, False)

            # Copy skin weights from source to target components
            cmds.select(source, targetComponents, r=True)
            cmds.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')
            trgSkinClsts.append(trgSkinClst)
    else:
        for trgSkinGeo in targets:
            trgSkinClst = mel.eval('findRelatedSkinCluster("%s");' % trgSkinGeo)

            if not trgSkinClst:
                cmds.skinCluster(srcInfs, trgSkinGeo, mi=4, dr=4, tsb=True, omi=False, nw=1)
                trgSkinClst = mel.eval('findRelatedSkinCluster("%s");' % trgSkinGeo)

            cmds.select(trgSkinGeo, r=True)
            trgInfs = cmds.skinCluster(trgSkinClst, q=True, inf=True)

            for inf in srcInfs:
                if inf in trgInfs:
                    continue
                else:
                    cmds.skinCluster(trgSkinClst, e=True, dr=4, lw=True, wt=0, ai=inf)
                    cmds.setAttr('%s.liw' % inf, False)

            cmds.select(source, trgSkinGeo, r=True)
            cmds.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')

            trgSkinClsts.append(trgSkinClst)

        # Restore targets shapes visiblity state
        for targetVisInfo in targetsShapeVisInfo:
            for trgShape, visState in targetVisInfo.items():
                cmds.setAttr(f'{trgShape}.visibility', visState)

    # Restore source shapes visibility state
    cmds.setAttr(f'{srcShape}.visibility', srcShapeVisState)

    for trgSkinClst in trgSkinClsts:
        srcSkinMethod = max(cmds.getAttr('%s.skinningMethod' % srcSkinClst), 0)
        trgSkinMethod = max(cmds.getAttr('%s.skinningMethod' % trgSkinClst), 0)
        if trgSkinMethod != 2:  # Set skinning method as same as source skin cluster if not Weighted Blended
            cmds.setAttr('%s.skinningMethod' % trgSkinClst, srcSkinMethod)
        srcUseComponent = cmds.getAttr('%s.useComponents' % srcSkinClst)
        cmds.setAttr('%s.useComponents' % trgSkinClst, srcUseComponent)
        srcNormalize = cmds.getAttr('%s.normalizeWeights' % srcSkinClst)
        cmds.setAttr('%s.normalizeWeights' % trgSkinClst, srcNormalize)
        srcMaintainMI = cmds.getAttr('%s.maintainMaxInfluences' % srcSkinClst)
        cmds.setAttr('%s.maintainMaxInfluences' % trgSkinClst, srcMaintainMI)
        srcMI = cmds.getAttr('%s.maxInfluences' % srcSkinClst)
        cmds.setAttr('%s.maxInfluences' % trgSkinClst, srcMI)

    cmds.select(source, targets, r=True)


def copySkin(source, target, components=None):
    """
    Copy source geometry skin weights to target geometry.
    If target geometry has no skin cluster, bind with source influences.

    Args:
        source (str): Source geometry
        target (str): Target geomery
    """
    removeLockWeightsInputConnection()

    srcInfs = getInfluences(source)
    srcJointInfs = [inf for inf in srcInfs if cmds.nodeType(inf) == 'joint']
    srcGeoInfs = list(set(srcInfs) - set(srcJointInfs))
    srcSkinClst = getSkinCluster(source)
    targetMesh = cmds.ls(target, objectsOnly=True)[0] if 'vtx' in target else target
    trgSkinClst = getSkinCluster(targetMesh)

    targetMeshShapeVis = cmds.getAttr(f'{targetMesh}.visibility')
    if not targetMeshShapeVis:
        cmds.setAttr(f'{targetMesh}.visibility', True)

    if not trgSkinClst:
        trgSkinClst = cmds.skinCluster(srcJointInfs, targetMesh, dr=4, tsb=True, nw=1)
        cmds.skinCluster(trgSkinClst, e=True, ug=True, ai=srcGeoInfs)

    else:
        trgInfs = getInfluences(targetMesh)
        trgJointInfs = [inf for inf in trgInfs if cmds.nodeType(inf) == 'joint']
        trgGeoInfs = list(set(trgInfs) - set(trgJointInfs))
        addedSrcJointInfs = list(set(srcJointInfs) - set(trgJointInfs))
        addedSrcGeoInfs = list(set(srcGeoInfs) - set(trgGeoInfs))

        for srcJntInf in addedSrcJointInfs:
            cmds.skinCluster(trgSkinClst, e=True, dr=4, lw=True, wt=0, ai=srcJntInf)
            cmds.setAttr('%s.liw' % srcJntInf, False)
        for srcGeoInf in addedSrcGeoInfs:
            cmds.skinCluster(trgSkinClst, e=True, dr=4, lw=True, wt=0, ug=True, ai=srcGeoInf)
            cmds.setAttr('%s.liw' % srcGeoInf, False)

    if components:
        cmds.select(source, components, r=True)
    else:
        cmds.select(source, target, r=True)

    cmds.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')

    srcSkinMethod = max(cmds.getAttr(f'{srcSkinClst}.skinningMethod'), 0)  # Prevent the value of skinning method not to be negative
    trgSkinMethod = max(cmds.getAttr(f'{trgSkinClst}.skinningMethod'), 0)
    if trgSkinMethod != 2:  # Set skinning method as same as source skin cluster if not Weighted Blended
        cmds.setAttr(f'{trgSkinClst}.skinningMethod', srcSkinMethod)
    cmds.setAttr(f'{trgSkinClst}.useComponents', cmds.getAttr(f'{srcSkinClst}.useComponents'))

    cmds.setAttr(f'{targetMesh}.visibility', targetMeshShapeVis)

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
    if not overlapVtxs:
        cmds.warning('No overlap vertices found between "{}" and "{}". Increase search distance then try again.'.format(sourceSkinMesh, targetMesh))
        return
    copySkin(sourceSkinMesh, targetMesh, components=overlapVtxs)


def duplicateSkinMesh():
    sels = cmds.ls(sl=True, fl=True)
    if cmds.nodeType(sels[0]) == "transform":
        for sel in sels:
            dupMesh = cmds.duplicate(sel, n="%s_skin" % sel)[0]
            try:
                cmds.parent(dupMesh, w=True)
            except:
                pass
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
    cmds.select(dupMesh, r=True)

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
    sepMesh = cmds.rename(sepMesh, "%s_skin" % sepMesh)
    copySkin(tempSkinMesh, sepMesh)

    meshUtil.cleanupMesh(meshTrsf)
    copySkin(tempSkinMesh, meshTrsf)

    cmds.delete(tempSkinMesh)


def mergeSkinMeshes():
    sels = cmds.ls(sl=True, objectsOnly=True)
    skinMeshes = cmds.filterExpand(sels, sm=12)
    if len(skinMeshes) != len([getSkinCluster(mesh) for mesh in skinMeshes if getSkinCluster(mesh)]):
        cmds.warning('All selected meshes must have skin cluster. Please check then try again.')
        return
    dupMeshes = cmds.duplicate(skinMeshes, rc=True)
    mergedSkinMesh = cmds.polyUnite(dupMeshes, ch=False, n='mergedSkin#')[0]
    cmds.polyMergeVertex(mergedSkinMesh, am=True, d=0.01, ch=False)
    cmds.delete(mergedSkinMesh, ch=True)
    cmds.delete(dupMeshes)

    for skinMesh in skinMeshes:
        copySkinOverlapVertices(skinMesh, mergedSkinMesh, 0.1)

    cmds.select(mergedSkinMesh, r=True)


def addInfluences():
    sels = cmds.ls(sl=True)
    jnts = cmds.ls(sels, type='joint')

    removeLockWeightsInputConnection(jnts)

    meshes = [item for item in sels if cmds.listRelatives(item, s=True)]
    for mesh in meshes:
        skinClst = getSkinCluster(mesh)
        influences = getInfluences(mesh)
        for jnt in jnts:
            if not jnt in influences:
                cmds.skinCluster(skinClst, e=True, dr=4, lw=True, wt=0, ai=jnt)
                cmds.setAttr('%s.liw' % jnt, False)


def getAffectedVertex(inf, minWeight):
    selVtxs = []

    skinClusters = cmds.listConnections(f'{inf}.worldMatrix')

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

        # Get influence dag path
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
        profileCurve = cmds.curve(degree=1, editPoint=[(0.0, 0.0, -width), (0.0, 0.0, width)], n='profile_crv')
    elif type == 'tube':
        profileCurve = cmds.circle(normal=[1, 0, 0], radius=width, n='profile_crv')[0]

    profileCurves = []
    for jnt in joints:
        dupProfileCrv = cmds.duplicate(profileCurve)
        cmds.xform(dupProfileCrv, matrix=cmds.getAttr(f'{jnt}.worldMatrix'), ws=True)
        profileCurves.append(dupProfileCrv)

    skinSurface = cmds.loft(profileCurves, degree=1, sectionSpans=int(jntsLength/len(joints)), ch=False)
    skinMesh = cmds.nurbsToPoly(skinSurface, format=3, polygonType=1, ch=False, n='{0}_skin'.format(joints[0]))

    cmds.delete(skinSurface)
    cmds.delete([profileCurve] + profileCurves)

    bind(joints[:-1], skinMesh)  # Exclude end joint for binding

    cmds.select(skinMesh, r=True)


def updateBindPose(rootJoint):
    """Update bind pose with current joint orient.

    :param rootJoint: Root joint of joint hierarchy
    :type rootJoint: str
    """
    parent = cmds.listRelatives(rootJoint, p=True)
    if parent and cmds.nodeType(parent[0]) == 'joint':
        cmds.error('Joint "{}" has parent joint. Please use the root joint of the hierarchy.'.format(rootJoint))
        return

    joints = cmds.ls(rootJoint, dag=True, type='joint')
    bindPoses = cmds.dagPose(rootJoint, q=True, bindPose=True)
    if len(bindPoses) > 1:
        cmds.delete(bindPoses)
        cmds.dagPose(joints, n='bindPose', save=True, bindPose=True)
    else:
        cmds.dagPose(joints, n=bindPoses[0], reset=True)


def goToBindPose(rootJoint):
    bindPoses = cmds.dagPose(rootJoint, q=True, bindPose=True)

    if len(bindPoses) > 1:
        cmds.error('There is more than one bind pose. Please clean up bind poses first.')
        return False
    else:
        bindPose = bindPoses[0]

    try:
        cmds.dagPose(bindPose, restore=True, g=True)
        return True
    except:
        return False


def setSolidSkinWeights(sourceVertex):
    cmds.select(sourceVertex, r=True)
    mel.eval('artAttrSkinWeightCopy;')
    mel.eval('ConvertSelectionToShell')
    mel.eval('artAttrSkinWeightPaste;')


def editSkinMesh(skinMesh):
    tempSkin = cmds.duplicate(skinMesh, n='temp_skin')[0]
    cmds.hide(tempSkin)
    skinClst = copySkin(skinMesh, tempSkin)
    cmds.setAttr('{}.envelope'.format(skinClst), 0)
    meshUtil.cleanupMesh(skinMesh)
    cmds.select(skinMesh, r=True)
    cmds.hudButton('editSkinMeshHUD', s=3, b=4, vis=1, l='Done Edit', bw=80, bsh='roundRectangle', rc=lambda : doneEditSkinMesh(tempSkin, skinMesh))

def doneEditSkinMesh(tempSkin, skinMesh):
    meshUtil.cleanupMesh(skinMesh)
    copySkin(tempSkin, skinMesh)
    cmds.delete(tempSkin)
    cmds.headsUpDisplay('editSkinMeshHUD', remove=True)


def editSkinnedJoints(skinMesh):
    tempSkinFile = exportSkin(skinMesh, cmds.internalVar(userTmpDir=True))
    cmds.select(skinMesh, r=True)
    mel.eval('DetachSkin;')
    cmds.hudButton('editSkinnedJointsHUD', s=3, b=4, vis=1, l='Done Edit', bw=80, bsh='roundRectangle', rc=lambda : doneEditSkinnedJoints(tempSkinFile))

def doneEditSkinnedJoints(tempSkinFile):
    importSkin(tempSkinFile)
    cmds.headsUpDisplay('editSkinnedJointsHUD', remove=True)


def sculptSkinMesh(skinMesh):
    sculptMesh = cmds.duplicate(skinMesh, n='sculptSkin_geo')[0]
    cmds.hide(skinMesh)
    meshUtil.cleanupMesh(sculptMesh)
    cmds.select(sculptMesh, r=True)
    cmds.hudButton('sculptSkinMeshHUD', s=3, b=4, vis=1, l='Done', bw=80, bsh='roundRectangle', rc=lambda : doneEditSculptMesh(skinMesh, sculptMesh))

def doneEditSculptMesh(skinMesh, sculptMesh):
    ssAPI.apply_inverse_weights_all(skinMesh, sculptMesh)
    cmds.setAttr('{}.visibility'.format(skinMesh), 1)
    cmds.delete(sculptMesh)
    cmds.headsUpDisplay('sculptSkinMeshHUD', remove=True)


def SSD(geo):
    influences = getInfluences(geo)
    topInfluence = globalUtil.getTopDagNode(influences)
    skinCluster = mel.eval('findRelatedSkinCluster("{}");'.format(geo))
    cmds.skinPercent(skinCluster, str(geo), pruneWeights=0.01)
    cmds.skinCluster(skinCluster, e=True, removeUnusedInfluence=True)
    cmds.bakeDeformer(sm=geo, ss=topInfluence, dm=geo, ds=topInfluence, mi=8)


def exportSkin(mesh, outputDir):
    cmds.select(mesh, r=True)
    skinFile = '{}/{}.sw'.format(outputDir, mesh)
    bsk.bSaveSkinValues(skinFile)
    return skinFile


def importSkin(skinFile):
    removeLockWeightsInputConnection()

    with open(skinFile, 'r') as f:
        fContents = f.readlines()
        mesh = fContents[0].strip('\n')
    if not cmds.objExists(mesh):
        print('"{}" is not exists. Skip importing skin weights.'.format(mesh))
        return False
    cmds.select(mesh, r=True)
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
    cmds.select(topInfluence, hi=True)
    curPose = cmds.dagPose(save=True, selection=True)

    succeed = goToBindPose(topInfluence)
    if not succeed:
        cmds.warning('Go to bind pose process is failed! Rigidfy skin weights will be performed in current pose.')

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


def conformSkin(*args):
    selFaces = cmds.filterExpand(cmds.ls(sl=True, fl=True), sm=[34])
    if not selFaces:
        cmds.error('Please select faces to conform skin weights.')
        return
    cmds.InvertSelection()
    dupSkinMesh = duplicateSkinMesh()
    cmds.select(selFaces, dupSkinMesh, r=True)
    addInfCopySkin()
    cmds.delete(dupSkinMesh)
    cmds.select(cl=True)
