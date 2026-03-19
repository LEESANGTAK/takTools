"""
Author: Sangtak Lee
Contact: https://ta-note.com

Description:
Skin weight related utility functions.
Separated from tak_misc.py for better organization.
"""

from imp import reload

import os
import re
from functools import partial

import maya.OpenMaya as OpenMaya
import maya.api.OpenMaya as om

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from . import tak_lib
from ..utils import skin as skinUtil; reload(skinUtil)


def TransSkinWeights():
    selList = mel.eval('string $selList[] = `ls -sl`;')
    src = mel.eval('string $source = $selList[0];')
    trgs = selList[1:]

    for trg in trgs:
        # get the source's shape
        srcShape = cmds.listRelatives(src, c=True, s=True, ni=True)[0]
        # get skin cluster of the source
        skClu = mel.eval('findRelatedSkinCluster($source);')
        jnts = cmds.skinCluster(skClu, q=True, inf=True)
        # get the target shape
        trgShape = cmds.listRelatives(trg, c=True, s=True, path=True, ni=True)[0]
        # bind target shape with joints of the source
        print('jnts: ', jnts)
        print('trgShape: ', trgShape)
        desSkClu = cmds.skinCluster(jnts, trgShape, mi=3, dr=4.5, tsb=True, omi=False, nw=1)[0]
        # copy skin weights from the source to the target
        cmds.copySkinWeights(ss=skClu, ds=desSkClu, sa='closestPoint', ia='oneToOne', nm=True)
        print('Skin weights transfered from %s to %s.' % (src, trg))
    print('#' * 50)
    print('Transfer skin weights job is done.')
    print('#' * 50)
    cmds.select(selList)


def addInfUI():
    winName = 'addInfWin'

    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    cmds.window(winName, title='Add Influences', maximizeButton=False, minimizeButton=False)

    cmds.columnLayout('addInfMainColLo', adj=True)

    cmds.rowColumnLayout('addInfListRoColLo', numberOfColumns=2, columnWidth=[(1, 150), (2, 150)],
                         columnSpacing=[(2, 10)], p='addInfMainColLo')
    cmds.frameLayout('infFrameLo', label='Influences', p='addInfListRoColLo')
    cmds.textScrollList('infTxtScrLs', p='infFrameLo')
    cmds.popupMenu()
    cmds.menuItem(label='Load Selected', c=partial(tak_lib.populateTxtScrList, 'textScrollList', 'infTxtScrLs'))
    cmds.frameLayout('geoFrameLo', label='Geometry', p='addInfListRoColLo')
    cmds.textScrollList('geoTxtScrLs', p='geoFrameLo')
    cmds.popupMenu()
    cmds.menuItem(label='Load Selected', c=partial(tak_lib.populateTxtScrList, 'textScrollList', 'geoTxtScrLs'))

    cmds.checkBox('useGeoChkBox', label='Use Geometry', p='addInfMainColLo')
    cmds.checkBox('lockWeightsChkBox', label='Lock Weights', v=True, p='addInfMainColLo')
    cmds.button(label='Apply', h=50, c=addInf, p='addInfMainColLo')

    cmds.window(winName, e=True, w=300, h=100)
    cmds.showWindow(winName)


def addInf(*args):
    infs = cmds.textScrollList('infTxtScrLs', q=True, allItems=True)
    geos = cmds.textScrollList('geoTxtScrLs', q=True, allItems=True)
    useGeoOpt = cmds.checkBox('useGeoChkBox', q=True, v=True)
    lockWeightsOpt = cmds.checkBox('lockWeightsChkBox', q=True, v=True)

    for geo in geos:
        # Get skin cluster
        skinClst = mel.eval('findRelatedSkinCluster("%s");' % geo)

        if not skinClst:
            cmds.select(cl=True)
            tmpBndJnt = cmds.joint(n=geo + '_jnt')
            cmds.skinCluster(tmpBndJnt, geo, mi=4, dr=4, tsb=True, omi=False, nw=1)
            skinClst = mel.eval('findRelatedSkinCluster("%s");' % geo)

        # Get influences that assigned to geo
        infsAssignGeo = cmds.skinCluster(skinClst, q=True, inf=True)

        for inf in infs:
            if inf in infsAssignGeo:
                continue
            else:
                cmds.skinCluster(skinClst, e=True, dr=4, ug=useGeoOpt, lw=lockWeightsOpt, wt=0, ai=inf)
                cmds.setAttr('%s.liw' % inf, False)

        if useGeoOpt:
            cmds.setAttr('%s.useComponents' % skinClst, 1)
            vtxNumber = cmds.polyEvaluate(geo, vertex=True)
            cmds.skinPercent(skinClst, '%s.vtx[%d:%d]' % (geo, 0, vtxNumber - 1), transformValue=[(inf, 1)])

            cmds.select(geo, r=True)
            mel.eval('removeUnusedInfluences;')

            cmds.delete(tmpBndJnt)


def selAffectedVertex():
    """Select vertices affected by the selected joint."""
    sels = cmds.ls(sl=True)
    jnt = sels[-1]
    geos = sels[:-1]
    if not geos:
        # If no geo selected, find skinned geos
        skinClusters = cmds.listConnections(jnt, type='skinCluster') or []
        for sc in skinClusters:
            shapes = cmds.skinCluster(sc, q=True, geometry=True) or []
            for shape in shapes:
                transform = cmds.listRelatives(shape, parent=True)
                if transform:
                    geos.append(transform[0])

    vtxs = []
    for geo in geos:
        skinClst = mel.eval('findRelatedSkinCluster("%s");' % geo)
        if not skinClst:
            continue
        numVtx = cmds.polyEvaluate(geo, v=True)
        for i in range(numVtx):
            vtx = '%s.vtx[%d]' % (geo, i)
            weight = cmds.skinPercent(skinClst, vtx, transform=jnt, q=True)
            if weight > 0.0:
                vtxs.append(vtx)
    cmds.select(vtxs, r=True)


def selInflu():
    """Select skin joints from selected mesh."""
    sels = cmds.ls(sl=True)
    allInfs = []
    for sel in sels:
        skinClst = mel.eval('findRelatedSkinCluster("%s");' % sel)
        if skinClst:
            infs = cmds.skinCluster(skinClst, q=True, inf=True)
            allInfs.extend(infs)
    cmds.select(list(set(allInfs)), r=True)


def addInfCopySkin(source=None, targets=None):
    '''
    Add source skin geometry's influences to the target geoemtry if not exists in the target skin geometry.
    And copy skin weights.
    '''

    skinUtil.removeLockWeightsInputConnection()

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


def smoothSkinBind():
    selLs = cmds.ls(sl=True)
    jntLs = cmds.ls(selLs, type='joint')
    geoShpLs = cmds.ls(selLs, dag=True, ni=True, type=['mesh', 'nurbsCurve', 'nurbsSurface'])

    for geoShp in geoShpLs:
        skinClst = mel.eval('findRelatedSkinCluster("%s");' % geoShp)
        if skinClst:
            cmds.select(geoShp, r=True)
            cmds.DetachSkin()
        geoTrsf = cmds.listRelatives(geoShp, p=True)[0]
        if cmds.nodeType(geoTrsf) != "transform":
            continue
        cmds.skinCluster(jntLs, geoTrsf, mi=1, dr=4, tsb=True, omi=False, nw=1)


def copySkinByName(dst, prefix="", srchStr="", rplcStr="", copyMatOpt=False):
    """
    Copy skined source geometry/group to destination geometry/group by matching name.
    """
    from . import tak_misc  # Lazy import to avoid circular dependency

    dstGeos = [x for x in cmds.listRelatives(dst, ad=True, type='shape') if not cmds.getAttr(x + '.intermediateObject')]

    nonMatchGeos = []

    for dstGeo in dstGeos:
        if srchStr or rplcStr:
            srcGeo = re.sub(srchStr, rplcStr, dstGeo)
        elif prefix:
            srcGeo = prefix + dstGeo

        print(">>> Source Geometry: " + srcGeo)
        print(">>> Destination Geometry: " + dstGeo)

        if cmds.objExists(srcGeo):
            cmds.select(srcGeo, dstGeo, r=True)
            try:
                addInfCopySkin()
            except:
                pass

            if copyMatOpt:
                tak_misc.copyMat()
        else:
            nonMatchGeos.append(dstGeo)

    if nonMatchGeos:
        cmds.select(nonMatchGeos, r=True)
        OpenMaya.MGlobal.displayWarning("Selected geometries didn't found matching source geometry.")
    else:
        cmds.select(cl=True)
        OpenMaya.MGlobal.displayInfo('All geometries copied skin successfully.')


def copyUvRiggedMesh(source, target):
    """
    Copy source mesh uv to rigged target mesh
    """
    targetShapes = target.getChildren(shapes=True)
    targetOrigShapes = [shape for shape in targetShapes if shape.isIntermediate()]
    for targetOrigShape in targetOrigShapes:
        targetOrigShape.intermediateObject.set(False)
        pm.transferAttributes(
            source,
            targetOrigShape,
            transferPositions=0,
            transferNormals=0,
            transferUVs=2,
            transferColors=0,
            sampleSpace=0,
            searchMethod=3
        )
        pm.delete(targetOrigShape, ch=True)
        targetOrigShape.intermediateObject.set(True)


def editDfmMemberUI():
    winName = 'editDfmMemberWin'

    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    cmds.window(winName, title='Edit Deformer Membership', maximizeButton=False, minimizeButton=False)

    cmds.columnLayout(adj=True)

    cmds.textFieldButtonGrp('dfmTxtFldBtnGrp', label='Deformer: ', buttonLabel='Load Sel',
                            columnWidth=[(1, 60), (2, 100)],
                            bc=partial(tak_lib.loadSel, 'textFieldButtonGrp', 'dfmTxtFldBtnGrp'))

    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 70), (2, 70), (3, 70)], columnSpacing=[(2, 5), (3, 5)])
    cmds.button(label='Select', c=partial(editDfmMember, 'select'))
    cmds.button(label='Add', c=partial(editDfmMember, 'add'))
    cmds.button(label='Remove', c=partial(editDfmMember, 'remove'))

    cmds.window(winName, e=True, w=100, h=50)
    cmds.showWindow(winName)


def editDfmMember(mode, *args):
    deformerName = cmds.textFieldButtonGrp('dfmTxtFldBtnGrp', q=True, text=True)
    sels = cmds.ls(sl=True, fl=True)

    try:
        deformerObjSets = cmds.listConnections(deformerName, s=False, d=True, type='objectSet')
        if not deformerObjSets:
            cmds.error('"{}" has no object set'.format(deformerName))
        elif len(deformerObjSets) > 1:
            cmds.error('"{}" has more than one object sets'.format(deformerName))

        if mode == 'select':
            cmds.select(deformerObjSets[0], r=True)
        elif mode == 'add':
            cmds.sets(sels, add=deformerObjSets[0])
        elif mode == 'remove':
            cmds.sets(sels, remove=deformerObjSets[0])

    except:  # This is for the deformers that use component tag.
        if mode == 'select':
            components = cmds.deformer(deformerName, q=True, components=True)
            cmds.select(components, r=True)
        elif mode == 'add':
            cmds.componentTag(sels, tn=deformerName, m='add')
        elif mode == 'remove':
            cmds.componentTag(sels, tn=deformerName, m='remove')
