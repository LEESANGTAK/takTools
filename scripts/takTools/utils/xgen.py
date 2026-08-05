"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Description:
    Utils for xgen.
"""

import json

from maya import mel
from maya import cmds
import maya.api.OpenMaya as om

import xgenm as xg
import xgenm.xgGlobal as xgg


def connectScalpToPatch(scalp, patch):
    """
    Connect scalp mesh to xgen patch to follow guides to scalp mesh.

    Parameters:
        scalp: string, Scalp mesh name.
        patch: string, Xgen patch name.

    Returns:
        None

    Examples:
        connectScalpToPatch(scalp="hairScalp_geo", patch="hairScalp_geo_teajung_frontHair")
    """

    patchShp = cmds.listRelatives(patch, s=True, fullPath=True)[0]
    cmds.connectAttr('{}.worldMesh'.format(scalp), '{}.geometry'.format(patchShp), force=True)
    cmds.connectAttr('{}.matrix'.format(scalp), '{}.transform'.format(patchShp), force=True)


def connectFollicleToScalp(follicle, scalp):
    """
    Parameters:
        follicle: string, Follicle name.
        scalp: string, Scalp mesh name.

    Returns:
        None

    Examples:
        connectFollicleToScalp(follicle='follicleShape1', scalp='hairScalp_geo')
    """

    cmds.connectAttr('{}.outMesh'.format(scalp), '{}.inputMesh'.format(follicle), force=True)
    cmds.connectAttr('{}.worldMatrix'.format(scalp), '{}.inputWorldMatrix'.format(follicle), force=True)


def attachGuideToScalp():
    xgGuides = cmds.ls(type='xgmSplineGuide', long=True) or []
    for xgGuide in xgGuides:
        xgmMakeGuides = cmds.listConnections('{}.toMakeGuide'.format(xgGuide), s=True, d=False) or []
        if not xgmMakeGuides:
            continue
        xgmMakeGuide = xgmMakeGuides[0]
        cmds.connectAttr('{}.outputMesh'.format(xgmMakeGuide), '{}.inputMesh'.format(xgGuide), force=True)


def exportXgenTextureInfo(mesh, filePath):
    mesh = str(mesh)
    files = cmds.listConnections(mesh, type='file', plugs=True) or []
    connectionInfos = []
    for fileOutput in files:
        meshAttr = cmds.listConnections(fileOutput, s=False, plugs=True)[0]
        connectionInfos.append({
            'fileOutput': str(fileOutput),
            'attr': '_' + meshAttr.split('.')[-1].split('_', 1)[-1],
            'attrType': cmds.getAttr(fileOutput, type=True)
        })
    with open(filePath, 'w') as f:
        json.dump(connectionInfos, f)


def importXgenTextureInfo(mesh, collection, filePath):
    mesh = str(mesh)
    with open(filePath, 'r') as f:
        connectionInfos = json.load(f)

    for info in connectionInfos:
        fileOutput = info['fileOutput']
        attr = collection + info['attr']
        attrType = info['attrType']

        if not cmds.attributeQuery(attr, node=mesh, exists=True):
            if attrType == 'float3':
                cmds.addAttr(mesh, ln=attr, at=attrType)
                cmds.addAttr(mesh, ln=attr+'X', at='float', p=attr)
                cmds.addAttr(mesh, ln=attr+'Y', at='float', p=attr)
                cmds.addAttr(mesh, ln=attr+'Z', at='float', p=attr)
            else:
                cmds.addAttr(mesh, ln=attr, at=attrType)

        cmds.connectAttr(fileOutput, '{}.{}'.format(mesh, attr), force=True)


def createGuideCurves(description, connect=True):
    guideCurvesGrp = description + '_guideCurves'

    guides = cmds.listRelatives(description, ad=True, type='xgmSplineGuide', fullPath=True) or []
    cmds.select(guides, r=True)
    mel.eval('xgmCreateCurvesFromGuidesOption(0, 0, "%s")' % (guideCurvesGrp))

    if connect:
        connectCurvesToGuides(guideCurvesGrp, description)


def connectCurvesToGuides(curveGroup, description, method='override'):
    curveGroup = str(curveGroup)
    description = str(description)

    crvs = cmds.listRelatives(curveGroup, c=True, fullPath=True) or []
    guides = cmds.listRelatives(description, ad=True, type='xgmSplineGuide', fullPath=True) or []

    if method == 'override':
        for crv, guide in zip(crvs, guides):
            makeGuide = cmds.listConnections('{}.inputMesh'.format(guide), d=False, s=True, type='xgmMakeGuide')
            if not makeGuide:
                continue
            makeGuide = makeGuide[0]
            cmds.connectAttr('{}.worldSpace[0]'.format(crv), '{}.override'.format(makeGuide), force=True)
    elif method == 'attach':
        de = xgg.DescriptionEditor
        collection = cmds.listRelatives(description, parent=True, fullPath=True)[0]
        objects = xg.objects(collection, description, True)

        xg.setAttr("useCache", 'True', collection, description, objects[0])
        cmds.select(crvs, r=True)
        mel.eval('xgmFindAttachment -description "{0}" -module "{1}"'.format(description, objects[0]))

        de.refresh('Description')


def findStackedGuides(guides):
    guidePoses = []
    for guide in guides:
        guidePos = cmds.xform(guide, q=True, rp=True, ws=True)
        guidePoses.append(om.MVector(guidePos))

    thresholds = 0.1
    stackedGuides = []
    for i, guidePos in enumerate(guidePoses):
        for j, nextGuidePos in enumerate(guidePoses[i+1:]):
            if (nextGuidePos - guidePos).length() <= thresholds:
                stackedGuides.extend([guides[i], guides[i+1+j]])

    return list(set(stackedGuides))


def createGuidesCurveForUE(curves=[]):
    attr_name = 'groom_guide'

    # get curves from selection
    if not curves:
        curves = cmds.ls(sl=True, dag=True, type='nurbsCurve')

    # create new group
    guides_group = cmds.createNode('transform', name='guides')

    # tag group as groom_guide
    cmds.addAttr(guides_group, longName=attr_name, attributeType='short', defaultValue=1, keyable=True)

    # forces Maya's alembic to export curves as one group.
    cmds.addAttr(guides_group, longName='riCurves', attributeType='bool', defaultValue=1, keyable=True)

    # add attribute scope
    # forces Maya's alembic to export data as GeometryScope::kConstantScope
    cmds.addAttr(guides_group, longName='{}_AbcGeomScope'.format(attr_name), dataType='string', keyable=True)
    cmds.setAttr('{}.{}_AbcGeomScope'.format(guides_group, attr_name), 'con', type='string')

    # parent curves under guides group
    for crv in curves:
        crvTransform = cmds.listRelatives(crv, p=True)
        cmds.parent(crv, guides_group, shape=True, relative=True)
        # Delete empty curve transform
        cmds.delete(crvTransform)

