"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Description:
This module contain functions for facial setup.
"""

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import re
from ..common import tak_misc


# Targets that has 'LeftRight' suffix is made as pristine then split to 'Left' side and 'Right' side.
"""
from takTools.rigging import facial
reload(facial)

cmds.undoInfo(openChunk=True)
for grp, targets in facial.ARKIT_TARGETS.items():
    grp = cmds.createNode('transform', n=grp+'_grp')
    facial.createFacialList('src_facial', targets)
    cmds.parent(targets, grp)
cmds.undoInfo(closeChunk=True)
"""
ARKIT_TARGETS = {
    'brow': [
        'browInnerUp',
        'browOuterUpLeftRight',
        'browDownLeftRight',
    ],
    'eye': [
        'eyeBlinkLeftRight',
        'eyeWideLeftRight',
        'eyeLookUpLeftRight',
        'eyeLookDownLeftRight',
        'eyeLookInLeftRight',
        'eyeLookOutLeftRight',
        'eyeSquintLeftRight',
    ],
    'cheek': [
        'cheekSquintLeftRight',
        'cheekPuff'
    ],
    'nose': [
        'noseSneerLeftRight'
    ],
    'mouth': [
        'mouthSmileLeftRight',
        'mouthDimpleLeftRight',
        'mouthFrownLeftRight',
        'mouthStretchLeftRight',
        'mouthUpperUpLeftRight',
        'mouthLowerDownLeftRight',
        'mouthPressLeftRight',
        'mouthShrugUpper',
        'mouthShrugLower',
        'mouthRollUpper',
        'mouthRollLower',
        'mouthFunnel',
        'mouthPucker',
        'mouthLeft',
        'mouthRight',
        'mouthClose'
    ],
    'jaw': [
        'jawOpen',
        'jawLeft',
        'jawRight',
        'jawForward'
    ]
}



def createFacialList(facialGrp, facialList):
    '''facialList = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry', 'eyebrow_sad',
                      'eyelid_blink', 'eyelid_smile', 'eyelid_angry', 'eyelid_sad', 'eyelid_big',
                      'lip_smile', 'lip_frown', 'lip_wide', 'lip_narrow', 'lip_openSmileBig', 'lip_angryBig',
                      'a', 'e', 'i', 'o']'''

    for item in facialList:
        cmds.duplicate(facialGrp, n=item, renameChildren=True, returnRootsOnly=True)

    cmds.select(facialList, r=True)

# Extract facial targets from rigged geo
'''
facialRigGrp = 'rig_face_grp'
targetNameList = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry', 'eyebrow_sad',
    'eyelid_blink', 'eyelid_smile', 'eyelid_angry', 'eyelid_sad', 'eyelid_big',
    'lip_wide', 'lip_narrow', 'lip_smile', 'lip_frown', 'lip_openSmileBig', 'lip_angryBig']
startFrame = 11
increment = 20

extractFacialTargets(facialRigGrp, targetNameList, startFrame, increment)
'''
def extractFacialTargets(facialRigGrp, targetNameList, startFrame, increment):
    cmds.currentTime(startFrame)
    for trgName in targetNameList:
        cmds.duplicate(facialRigGrp, n=trgName, renameChildren=True)
        startFrame += increment
        cmds.currentTime(startFrame)


def extractFacialTargetsWithCtrl(facialGrp, control, lfRtPrefix=['L', 'R']):
    """
    Args:
        facialGrp (str): Facial group that contain facial expressions
        control (str): Facial control curve name
    """
    lfRtAttrs = []
    keyableAttrs = cmds.listAttr(control, keyable=True) or []
    for attrName in keyableAttrs:
        attrFull = '{}.{}'.format(control, attrName)
        if cmds.getAttr(attrFull, lock=True):
            continue
        attrPrefix = attrName.split('_')[0]
        if attrPrefix in lfRtPrefix:
            lfRtAttrs.append(attrName.replace(attrPrefix, ''))
        else:
            cmds.setAttr(attrFull, 1)
            cmds.duplicate(facialGrp, renameChildren=True,
                           name='{ctrlName}_{attrName}'.format(ctrlName=control, attrName=attrName))
            cmds.setAttr(attrFull, 0)

    for lfRtAttr in list(set(lfRtAttrs)):
        for prefix in lfRtPrefix:
            cmds.setAttr('{}.{}'.format(control, prefix + lfRtAttr), 1)
        cmds.duplicate(facialGrp, renameChildren=True, name=control + lfRtAttr)
        for prefix in lfRtPrefix:
            cmds.setAttr('{}.{}'.format(control, prefix + lfRtAttr), 0)


def extractFacialTargets(blendShape, facialGrp):
    trgLs = cmds.listAttr(blendShape + '.w', multi=True)

    for trg in trgLs:
        cmds.setAttr(blendShape + '.' + trg, 1)
        cmds.duplicate(facialGrp, renameChildren=True, n=trg)
        cmds.setAttr(blendShape + '.' + trg, 0)


def connectFacial(facialCtrl, blendshapeNode):
    facialAttrLs = cmds.listAttr(facialCtrl, keyable=True)
    for facialAttr in facialAttrLs:
        facialBsTrgName = re.sub(r'ctrl', facialAttr, facialCtrl)

        if cmds.objExists(blendshapeNode + '.' + facialBsTrgName):
            try:
                cmds.connectAttr(facialCtrl + '.' + facialAttr, blendshapeNode + '.' + facialBsTrgName, f=True)
            except:
                pass

        if 'lip' in facialCtrl:
            if facialAttr in ['a', 'e', 'i', 'o', 'u']:
                try:
                    cmds.connectAttr(facialCtrl + '.' + facialAttr, blendshapeNode + '.' + facialAttr, f=True)
                except:
                    pass

            facialBsTrgName = re.sub(r'ctrl', facialAttr, facialCtrl)
            if 'lip_L' in facialBsTrgName:
                facialBsTrgName = re.sub(r'lip_L', 'lf_lip', facialBsTrgName)
            elif 'lip_R' in facialBsTrgName:
                facialBsTrgName = re.sub(r'lip_R', 'R_lip', facialBsTrgName)

            if cmds.objExists(blendshapeNode + '.' + facialBsTrgName):
                try:
                    cmds.connectAttr(facialCtrl + '.' + facialAttr, blendshapeNode + '.' + facialBsTrgName, f=True)
                except:
                    pass


### Facial Tertiary ###
def createCurveSystem(name, numOfControls):
    """
    Create curve system with selected edge loop

    Parameters:
        name: Rig name
        numOfControls: Number of local controls
    """

    # Convert edges to curve
    rawCurve = cmds.polyToCurve(n=name + '_crv', form=2, degree=1)[0]

    # Create joints with rawCurve
    jnts = []
    numCVs = cmds.getAttr('{}.spans'.format(rawCurve)) + cmds.getAttr('{}.degree'.format(rawCurve))
    for i in range(numCVs):
        cvPos = cmds.pointPosition('{}.cv[{}]'.format(rawCurve, i), w=True)
        cmds.select(cl=True)
        jnt = cmds.joint(p=cvPos, radius=0.25)
        jnts.append(jnt)
    jnts = renameByPosition(name, jnts)

    # Rebuild curve and delete history
    newCrv = cmds.rebuildCurve(rawCurve, spans=numOfControls - 3, degree=3)[0]
    cmds.delete(newCrv, ch=True)

    # Attach cluster to the curve cvs
    newCrvNumCVs = cmds.getAttr('{}.spans'.format(newCrv)) + cmds.getAttr('{}.degree'.format(newCrv))
    clusters = []
    for i in range(newCrvNumCVs):
        clst = cmds.cluster('{}.cv[{}]'.format(newCrv, i))[1]
        clusters.append(clst)
    clusters = renameByPosition(name, clusters, suffix='clst')
    locatorZeroGrps = []
    for clst in clusters:
        cmds.select(clst, r=True)
        locatorZeroGrps.extend(tak_misc.locGrp())
        cmds.setAttr('%s.visibility' % clst, False)

    # Set mirrored behavior for right side
    for locatorZeroGrp in locatorZeroGrps:
        if cmds.getAttr('%s.tx' % locatorZeroGrp) < 0:
            children = cmds.listRelatives(locatorZeroGrp, ad=True, type='transform') or []
            if len(children) >= 3:
                clst, locator, autoGrp = children[0], children[1], children[2]
                cmds.parent(clst, world=True)
                cmds.setAttr('%s.sx' % locatorZeroGrp, -1)
                cmds.parent(clst, locator)

    # Cleanup outliner
    jntGrp = cmds.group(jnts, n=name + '_jnt_grp')
    locGrp = cmds.group(locatorZeroGrps, n=name + '_loc_grp')
    cmds.group(jntGrp, locGrp, newCrv, n=name + '_system_grp')


def renameByPosition(name, transformList, suffix='bnd_jnt'):
    renamedList = []

    nodeType = cmds.nodeType(transformList[0])
    if nodeType == 'joint':
        if '_R' in name:
            transformList.sort(key=lambda x: cmds.getAttr('%s.tx' % x), reverse=True)
        else:
            transformList.sort(key=lambda x: cmds.getAttr('%s.tx' % x))
    else:
        if '_R' in name:
            transformList.sort(key=lambda x: cmds.getAttr('%s.rotatePivotX' % x), reverse=True)
        else:
            transformList.sort(key=lambda x: cmds.getAttr('%s.rotatePivotX' % x))

    for item in transformList:
        renamedList.append(cmds.rename(item, '%s_%02d_%s' % (name, transformList.index(item) + 1, suffix)))

    return renamedList


def mirrorXTransform(src, trg):
    from maya.api import OpenMaya as om
    mSels = om.MSelectionList()
    mSels.add(src)
    dagPath = mSels.getDagPath(0)
    fnTrsf = om.MFnTransform(dagPath)
    srcMat = fnTrsf.transformation().asMatrix()

    mirXMat = om.MMatrix([
        -1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ])

    mirroredMat = srcMat * mirXMat
    cmds.xform(trg, matrix=list(mirroredMat), ws=True)


def createProjectedCurve(locators, nurbsSurface, name='projected_crv'):
    """
    Create curve with projected point on surface with locators.
    Locators order will be cv order.

    Args:
        locators (list<str>): Locator transform names.
        nurbsSurface (str): Nurbs surface transform name.
        name (str, optional): Curve name. Defaults to 'projected_crv'.
    """
    follicles = []
    positions = []
    for locator in locators:
        follicleTransform = createProjectedFollicle(locator, nurbsSurface)
        follicles.append(follicleTransform)
        pos = cmds.xform(follicleTransform, q=True, t=True, ws=True)
        positions.append(pos)

    curve = cmds.curve(d=3, p=positions, n=name)
    curveShape = cmds.listRelatives(curve, shapes=True)[0]

    for i, follicle in enumerate(follicles):
        decMatrix = cmds.createNode('decomposeMatrix', n='%s_decMatrix' % follicle)
        cmds.connectAttr('%s.worldMatrix' % follicle, '%s.inputMatrix' % decMatrix, f=True)
        cmds.connectAttr('%s.outputTranslate' % decMatrix,
                         '%s.controlPoints[%d]' % (curveShape, i), f=True)

    return curve


def createProjectedFollicle(locator, nurbsSurface):
    nurbsSurfaceShape = cmds.listRelatives(nurbsSurface, shapes=True, noIntermediate=True)
    if nurbsSurfaceShape:
        nurbsSurfaceShape = nurbsSurfaceShape[0]
    else:
        nurbsSurfaceShape = nurbsSurface

    locatorShape = cmds.listRelatives(locator, shapes=True)[0]

    # Create nodes
    closestPointOnSurface = cmds.createNode('closestPointOnSurface', n='%s_ClstPntOnSrfc' % locator)
    multiplyDivide = cmds.createNode('multiplyDivide', n='%s_munDiv' % locator)
    follicleShape = cmds.createNode('follicle', n='%s_follicleShape' % locator)
    follicleTransform = cmds.listRelatives(follicleShape, parent=True)[0]

    # Connect nodes
    cmds.connectAttr('%s.worldPosition' % locatorShape, '%s.inPosition' % closestPointOnSurface, f=True)
    cmds.connectAttr('%s.worldSpace' % nurbsSurfaceShape, '%s.inputSurface' % closestPointOnSurface, f=True)

    cmds.connectAttr('%s.parameterU' % closestPointOnSurface, '%s.input1X' % multiplyDivide, f=True)
    cmds.connectAttr('%s.parameterV' % closestPointOnSurface, '%s.input1Y' % multiplyDivide, f=True)
    cmds.connectAttr('%s.minMaxRangeU' % nurbsSurfaceShape, '%s.input2X' % multiplyDivide, f=True)
    cmds.connectAttr('%s.minMaxRangeV' % nurbsSurfaceShape, '%s.input2Y' % multiplyDivide, f=True)
    cmds.setAttr('%s.operation' % multiplyDivide, 2)

    cmds.connectAttr('%s.outputX' % multiplyDivide, '%s.parameterU' % follicleShape, f=True)
    cmds.connectAttr('%s.outputY' % multiplyDivide, '%s.parameterV' % follicleShape, f=True)
    cmds.connectAttr('%s.worldSpace' % nurbsSurfaceShape, '%s.inputSurface' % follicleShape, f=True)

    cmds.connectAttr('%s.outTranslate' % follicleShape, '%s.translate' % follicleTransform, f=True)
    cmds.connectAttr('%s.outRotate' % follicleShape, '%s.rotate' % follicleTransform, f=True)

    return follicleTransform


CURVE = 0
SURFACE = 1
def createFacialJoint(vertex, curve, surface, positionTo=CURVE):
    """
    Create a joint oriented to surface. Position can be changed with option.

    Args:
        vertex (str): Source vertex component (e.g. 'mesh.vtx[0]') to find closest point on curve.
        curve (str): Facial curve transform name.
        surface (str): Skull surface transform name.
        positionTo (int): Nurbs geometry to attach joint. [CURVE, SURFACE]

    Returns:
        str: Created joint name
    """
    joint = None

    curveShape = cmds.listRelatives(curve, shapes=True, noIntermediate=True)
    curveShape = curveShape[0] if curveShape else curve

    surfaceShape = cmds.listRelatives(surface, shapes=True, noIntermediate=True)
    surfaceShape = surfaceShape[0] if surfaceShape else surface

    # Get curve function
    mSels = om.MSelectionList()
    mSels.add(curveShape)
    crvDagPath = mSels.getDagPath(0)
    crvFn = om.MFnNurbsCurve(crvDagPath)

    # Get parameter of closest point on curve from vertex
    vtxPos = cmds.pointPosition(vertex, w=True)
    vtxPnt = om.MPoint(*vtxPos)
    closestPntOnCrvParm = crvFn.closestPoint(vtxPnt, space=om.MSpace.kWorld)[1]

    # Create necessary nodes
    pntOnCrvInfo = cmds.createNode('pointOnCurveInfo')
    closestPntOnSurface = cmds.createNode('closestPointOnSurface')
    normalizeParmDiv = cmds.createNode('multiplyDivide')
    folShape = cmds.createNode('follicle')
    folTrsf = cmds.listRelatives(folShape, parent=True)[0]
    joint = cmds.createNode('joint', n='%s_jnt' % vertex.replace('.', '_').replace('[', '').replace(']', ''))

    # Point on curve info connections
    cmds.connectAttr('%s.worldSpace' % curveShape, '%s.inputCurve' % pntOnCrvInfo, f=True)
    cmds.setAttr('%s.parameter' % pntOnCrvInfo, closestPntOnCrvParm)

    # Closest point on surface connections
    cmds.connectAttr('%s.worldSpace' % surfaceShape, '%s.inputSurface' % closestPntOnSurface, f=True)
    cmds.connectAttr('%s.position' % pntOnCrvInfo, '%s.inPosition' % closestPntOnSurface, f=True)

    # Normalize parameterUV of point on surface with nurbs surface parameterUV max value
    cmds.setAttr('%s.operation' % normalizeParmDiv, 2)
    cmds.connectAttr('%s.parameterU' % closestPntOnSurface, '%s.input1X' % normalizeParmDiv, f=True)
    cmds.connectAttr('%s.parameterV' % closestPntOnSurface, '%s.input1Y' % normalizeParmDiv, f=True)
    cmds.connectAttr('%s.minMaxRangeU' % surfaceShape, '%s.input2X' % normalizeParmDiv, f=True)
    cmds.connectAttr('%s.minMaxRangeV' % surfaceShape, '%s.input2Y' % normalizeParmDiv, f=True)

    # Follicle connections
    cmds.connectAttr('%s.worldSpace' % surfaceShape, '%s.inputSurface' % folShape, f=True)
    cmds.connectAttr('%s.outputX' % normalizeParmDiv, '%s.parameterU' % folShape, f=True)
    cmds.connectAttr('%s.outputY' % normalizeParmDiv, '%s.parameterV' % folShape, f=True)

    # Follicle transform connections depend on option
    if positionTo == CURVE:
        cmds.connectAttr('%s.position' % pntOnCrvInfo, '%s.translate' % folTrsf, f=True)
    elif positionTo == SURFACE:
        cmds.connectAttr('%s.outTranslate' % folShape, '%s.translate' % folTrsf, f=True)
    cmds.connectAttr('%s.outRotate' % folShape, '%s.rotate' % folTrsf, f=True)

    # Parent joint to follicle transform
    cmds.parent(joint, folTrsf)
    cmds.setAttr('%s.translate' % joint, 0, 0, 0)
    cmds.setAttr('%s.rotate' % joint, 0, 0, 0)
    cmds.setAttr('%s.scale' % joint, 1, 1, 1)

    return joint


def buildFacialController(controller, railSurface, minVal, maxVal):
    """ Attach controller to nurbs surface to sliding controller. """
    railSurfaceShape = cmds.listRelatives(railSurface, shapes=True, noIntermediate=True)
    railSurfaceShape = railSurfaceShape[0] if railSurfaceShape else railSurface

    cmds.rebuildSurface(
        railSurface,
        rebuildType=0,
        keepRange=0,
        spansU=2,
        spansV=0,
        degreeU=3,
        degreeV=1
    )
    cmds.delete(railSurface, ch=True)

    pntOnSrfcInfo = cmds.createNode('pointOnSurfaceInfo', n='{}_pntOnSrfcInfo'.format(controller))
    zVecProduct = cmds.createNode('vectorProduct', n='{}_zVec'.format(controller))
    matrixNode = cmds.createNode('fourByFourMatrix', n='{}_matrix'.format(controller))
    decMatrix = cmds.createNode('decomposeMatrix', n='{}_decMatrix'.format(controller))
    anchorGrp = cmds.createNode('transform', n='{}_anchor'.format(controller))
    revGrp = cmds.createNode('transform', n='{}_rev'.format(controller))
    revMul = cmds.createNode('multiplyDivide', n='{}_rev_mul'.format(controller))

    cmds.transformLimits(controller, tx=(minVal, maxVal), etx=(True, True))

    cmds.setAttr('%s.parameterV' % pntOnSrfcInfo, 0.5)
    cmds.setAttr('%s.operation' % zVecProduct, 2)
    cmds.setAttr('%s.normalizeOutput' % zVecProduct, True)
    cmds.setAttr('%s.input2X' % revMul, -1.0)
    cmds.setAttr('%s.input2Y' % revMul, -1.0)
    cmds.setAttr('%s.input2Z' % revMul, -1.0)

    cmds.parent(controller, revGrp)
    cmds.parent(revGrp, anchorGrp)

    if minVal < 0:
        txRemap = cmds.createNode('remapValue', n='{}_tx_remap'.format(controller))
        cmds.setAttr('%s.inputMin' % txRemap, minVal)
        cmds.setAttr('%s.inputMax' % txRemap, maxVal)

        zeroToNegOneRemap = cmds.createNode('remapValue', n='{}_zeroToNegOne_remap'.format(controller))
        cmds.setAttr('%s.inputMin' % zeroToNegOneRemap, 0)
        cmds.setAttr('%s.inputMax' % zeroToNegOneRemap, minVal)

        cmds.connectAttr('%s.tx' % controller, '%s.inputValue' % txRemap, f=True)
        cmds.connectAttr('%s.tx' % controller, '%s.inputValue' % zeroToNegOneRemap, f=True)
        cmds.connectAttr('%s.outValue' % txRemap, '%s.parameterU' % pntOnSrfcInfo, f=True)
    else:
        cmds.connectAttr('%s.tx' % controller, '%s.parameterU' % pntOnSrfcInfo, f=True)

    cmds.connectAttr('%s.worldSpace' % railSurfaceShape, '%s.inputSurface' % pntOnSrfcInfo, f=True)

    cmds.connectAttr('%s.normalizedNormal' % pntOnSrfcInfo, '%s.input1' % zVecProduct, f=True)
    cmds.connectAttr('%s.normalizedTangentU' % pntOnSrfcInfo, '%s.input2' % zVecProduct, f=True)

    cmds.connectAttr('%s.normalizedTangentUX' % pntOnSrfcInfo, '%s.in00' % matrixNode, f=True)
    cmds.connectAttr('%s.normalizedTangentUY' % pntOnSrfcInfo, '%s.in01' % matrixNode, f=True)
    cmds.connectAttr('%s.normalizedTangentUZ' % pntOnSrfcInfo, '%s.in02' % matrixNode, f=True)
    cmds.connectAttr('%s.outputX' % zVecProduct, '%s.in10' % matrixNode, f=True)
    cmds.connectAttr('%s.outputY' % zVecProduct, '%s.in11' % matrixNode, f=True)
    cmds.connectAttr('%s.outputZ' % zVecProduct, '%s.in12' % matrixNode, f=True)
    cmds.connectAttr('%s.normalizedNormalX' % pntOnSrfcInfo, '%s.in20' % matrixNode, f=True)
    cmds.connectAttr('%s.normalizedNormalY' % pntOnSrfcInfo, '%s.in21' % matrixNode, f=True)
    cmds.connectAttr('%s.normalizedNormalZ' % pntOnSrfcInfo, '%s.in22' % matrixNode, f=True)
    cmds.connectAttr('%s.positionX' % pntOnSrfcInfo, '%s.in30' % matrixNode, f=True)
    cmds.connectAttr('%s.positionY' % pntOnSrfcInfo, '%s.in31' % matrixNode, f=True)
    cmds.connectAttr('%s.positionZ' % pntOnSrfcInfo, '%s.in32' % matrixNode, f=True)

    cmds.connectAttr('%s.output' % matrixNode, '%s.inputMatrix' % decMatrix, f=True)

    cmds.connectAttr('%s.outputTranslate' % decMatrix, '%s.translate' % anchorGrp, f=True)
    cmds.connectAttr('%s.outputRotate' % decMatrix, '%s.rotate' % anchorGrp, f=True)

    cmds.connectAttr('%s.translate' % controller, '%s.input1' % revMul, f=True)
    cmds.connectAttr('%s.output' % revMul, '%s.translate' % revGrp, f=True)


def buildZipperLip(vertices):
    __createJoints(vertices)

def __createJoints(vertices):
    skinClst = mel.eval('findRelatedSkinCluster "%s";' % vertices[0].split('.')[0])
    infs = cmds.skinCluster(skinClst, q=True, inf=True)

    for vtx in vertices:
        vtxPos = cmds.pointPosition(vtx, w=True)
        jnt = cmds.createNode('joint', n=vtx.replace('.', '_').replace('[', '').replace(']', '') + 'zip_jnt')
        cmds.setAttr('%s.translate' % jnt, *vtxPos)
        for inf in infs:
            weight = round(cmds.skinPercent(skinClst, vtx, q=True, transform=inf), 10)
            if weight > 0.0:
                cmds.pointConstraint(inf, jnt, mo=True, w=weight)


def connectFACS(facsOut, blendShape, shader):
    actionCodings = cmds.listAttr(facsOut, ud=True) or []
    for ac in actionCodings:
        try:
            cmds.connectAttr('%s.%s' % (facsOut, ac), '%s.%s' % (blendShape, ac), f=True)
        except:
            pass

    # Wrinkle map 0
    cmds.connectAttr('%s.browOuterUpLeft' % facsOut, '%s.wrinkleMap0_WrinkleGroup0X' % shader, f=True)
    cmds.connectAttr('%s.browOuterUpRight' % facsOut, '%s.wrinkleMap0_WrinkleGroup0Y' % shader, f=True)
    cmds.connectAttr('%s.browInnerUpLeft' % facsOut, '%s.wrinkleMap0_WrinkleGroup0Z' % shader, f=True)
    cmds.connectAttr('%s.browInnerUpRight' % facsOut, '%s.wrinkleMap0_WrinkleGroup0W' % shader, f=True)

    cmds.connectAttr('%s.cheekSquintLeft' % facsOut, '%s.wrinkleMap0_WrinkleGroup1X' % shader, f=True)
    cmds.connectAttr('%s.cheekSquintRight' % facsOut, '%s.wrinkleMap0_WrinkleGroup1Y' % shader, f=True)

    cmds.connectAttr('%s.mouthSmileLeft' % facsOut, '%s.wrinkleMap0_WrinkleGroup2X' % shader, f=True)
    cmds.connectAttr('%s.mouthSmileRight' % facsOut, '%s.wrinkleMap0_WrinkleGroup2Y' % shader, f=True)
    cmds.connectAttr('%s.neckTensionLeft' % facsOut, '%s.wrinkleMap0_WrinkleGroup2Z' % shader, f=True)
    cmds.connectAttr('%s.neckTensionRight' % facsOut, '%s.wrinkleMap0_WrinkleGroup2W' % shader, f=True)

    # Wrinkle map 1
    cmds.connectAttr('%s.noseSneerLeft' % facsOut, '%s.wrinkleMap1_WrinkleGroup1X' % shader, f=True)
    cmds.connectAttr('%s.noseSneerRight' % facsOut, '%s.wrinkleMap1_WrinkleGroup1Y' % shader, f=True)

    cmds.connectAttr('%s.mouthStretchLeft' % facsOut, '%s.wrinkleMap1_WrinkleGroup2X' % shader, f=True)
    cmds.connectAttr('%s.mouthStretchRight' % facsOut, '%s.wrinkleMap1_WrinkleGroup2Y' % shader, f=True)
    cmds.connectAttr('%s.mouthPuckerLeft' % facsOut, '%s.wrinkleMap1_WrinkleGroup2Z' % shader, f=True)
    cmds.connectAttr('%s.mouthPuckerRight' % facsOut, '%s.wrinkleMap1_WrinkleGroup2W' % shader, f=True)

    # Wrinkle map 2
    cmds.connectAttr('%s.browDownLeft' % facsOut, '%s.wrinkleMap2_WrinkleGroup0X' % shader, f=True)
    cmds.connectAttr('%s.browDownRight' % facsOut, '%s.wrinkleMap2_WrinkleGroup0Y' % shader, f=True)

    cmds.connectAttr('%s.eyeSquintLeft' % facsOut, '%s.wrinkleMap2_WrinkleGroup1X' % shader, f=True)
    cmds.connectAttr('%s.eyeSquintRight' % facsOut, '%s.wrinkleMap2_WrinkleGroup1Y' % shader, f=True)
    cmds.connectAttr('%s.mouthUpperShrugLeft' % facsOut, '%s.wrinkleMap2_WrinkleGroup1Z' % shader, f=True)
    cmds.connectAttr('%s.mouthUpperShrugRight' % facsOut, '%s.wrinkleMap2_WrinkleGroup1W' % shader, f=True)

    cmds.connectAttr('%s.mouthFrownLeft' % facsOut, '%s.wrinkleMap2_WrinkleGroup2X' % shader, f=True)
    cmds.connectAttr('%s.mouthFrownRight' % facsOut, '%s.wrinkleMap2_WrinkleGroup2Y' % shader, f=True)
    cmds.connectAttr('%s.mouthLowerShrugLeft' % facsOut, '%s.wrinkleMap2_WrinkleGroup2Z' % shader, f=True)
    cmds.connectAttr('%s.mouthLowerShrugRight' % facsOut, '%s.wrinkleMap2_WrinkleGroup2W' % shader, f=True)


def setROMPose(numPose=50):
    for i in range(numPose):
        cmds.currentTime(i * 10)
        cmds.setKeyframe()
