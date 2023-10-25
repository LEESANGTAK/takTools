"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Description:
    Utils for xgen.
"""

import json

from maya import mel
import pymel.core as pm

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

    patchShp = pm.listRelatives(patch)[0]
    pm.connectAttr(scalp + ".worldMesh", patchShp + ".geometry")
    pm.connectAttr(scalp + ".matrix", patchShp + ".transform")


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

    pm.connectAttr(scalp + ".outMesh", follicle + ".inputMesh", f=True)
    pm.connectAttr(scalp + ".worldMatrix", follicle + ".inputWorldMatrix", f=True)


def attachGuideToScalp():
    xgGuides = pm.ls(type='xgmSplineGuide')
    for xgGuide in xgGuides:
        xgmMakeGuide = xgGuide.toMakeGuide.connections()[0]
        xgmMakeGuide.outputMesh.connect(xgGuide.inputMesh, f=True)


def exportXgenTextureInfo(mesh, filePath):
    files = mesh.connections(type='file', plugs=True)
    connectionInfos = []
    for file in files:
        meshAttr = file.connections(s=False, plugs=True)[0]
        connectionInfos.append({
            'fileOutput': str(file),
            'attr': '_' + meshAttr.split('.')[-1].split('_', 1)[-1],
            'attrType': meshAttr.type()
        })
    with open(filePath, 'w') as f:
        json.dump(connectionInfos, f)


def importXgenTextureInfo(mesh, collection, filePath):
    with open(filePath, 'r') as f:
        connectionInfos = json.load(f)

    for info in connectionInfos:
        fileOutput = info['fileOutput']
        attr = collection + info['attr']
        attrType = info['attrType']

        if not mesh.hasAttr(attr):
            if attrType == 'float3':
                mesh.addAttr(attr, at=attrType)
                mesh.addAttr(attr+'X', at='float', p=attr)
                mesh.addAttr(attr+'Y', at='float', p=attr)
                mesh.addAttr(attr+'Z', at='float', p=attr)
            else:
                mesh.addAttr(attr, at=attrType)

        pm.Attribute(fileOutput) >> mesh.attr(attr)


def createGuideCurves(description, connect=True):
    guideCurvesGrp = description + '_guideCurves'

    desc = pm.PyNode(description)
    guides = desc.getChildren(ad=True, type='xgmSplineGuide')
    pm.select(guides, r=True)
    pm.mel.eval('xgmCreateCurvesFromGuidesOption(0, 0, "%s")' % (guideCurvesGrp))

    if connect:
        connectCurvesToGuides(guideCurvesGrp, description)


def connectCurvesToGuides(curveGroup, description, method='override'):
    curveGroup = str(curveGroup)
    description = str(description)

    crvs = pm.listRelatives(curveGroup)
    guides = pm.listRelatives(description, ad=True, type='xgmSplineGuide')

    if method == 'override':
        for crv, guide in zip(crvs, guides):
            makeGuide = guide.inputMesh.connections(d=False, type='xgmMakeGuide')[0]
            crv.worldSpace >> makeGuide.override
    elif method == 'attach':
        de = xgg.DescriptionEditor
        collection = str(pm.listRelatives(description, parent=True)[0])
        objects = xg.objects(collection, description, True)

        xg.setAttr("useCache", 'True', collection, description, objects[0])
        pm.select(crvs, r=True)
        mel.eval('xgmFindAttachment -description "{0}" -module "{1}"'.format(description, objects[0]))

        de.refresh('Description')


def findStackedGuides(guides):
    guidePoses = []
    for guide in guides:
        guidePos = pm.xform(guide, q=True, rp=True, ws=True)
        guidePoses.append(pm.dt.Vector(guidePos))

    thresholds = 0.1
    stackedGuides = []
    for i, guidePos in enumerate(guidePoses):
        for j, nextGuidePos in enumerate(guidePoses[i+1:]):
            if (nextGuidePos - guidePos).length() <= thresholds:
                stackedGuides.extend([guides[i], guides[i+1+j]])

    return list(set(stackedGuides))
