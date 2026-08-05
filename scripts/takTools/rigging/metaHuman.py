import os
import shutil
from maya.api import OpenMaya as om
from maya import cmds
import maya.mel as mel

# Skeleton joints
SKELETON_ROOT = 'mh_spine_04'
SKELETON_HEAD = 'mh_head'
SKELETON_EYE_L = 'mh_FACIAL_L_Eye'
SKELETON_EYE_R = 'mh_FACIAL_R_Eye'

# Controllers
CONTROLLER_DRIVE_LOCATOR = 'LOC_world'
FACE_GUI_GRP = 'GRP_faceGUI'
EYES_AIM_GRP = 'GRP_C_eyesAim'
EYES_AIM_FOLLOW_CTRL = 'CTRL_eyesAimFollowHead'

# Outputs
FACIAL_OUT_ATTRS = 'CTRL_expressions'
WRINKLE_MAP_MULT = 'FRM_WMmultipliers'

# File paths
FACIAL_GUIDE_FILE = r"C:\GoogleDrive\programs_env\maya\modules\ironRig\guides\facial.ma"
TEETH_SKELETON_FILE = r"C:\GoogleDrive\programs_env\maya\modules\ironRig\skeletons\metahuman_teethTongue.ma"
FACIAL_SAMPLE_FILE = r"C:\GoogleDrive\programs_env\maya\modules\ironRig\resources\metaHuman_face_sampleMesh.ma"
SDK_ASSET_FILE = r"C:\GoogleDrive\programs_env\maya\modules\ironRig\assets\metahumanSDK_asset.ma"

EXPRESSION_INFO = {
    'faceExpr': [
        'browDownL',
        'browDownR',
        'browLateralL',
        'browLateralR',
        'browRaiseInL',
        'browRaiseInR',
        'browRaiseOuterL',
        'browRaiseOuterR',
        'earUpL',
        'earUpR',
        'eyeBlinkL',
        'eyeBlinkR',
        'eyeWidenL',
        'eyeWidenR',
        'eyeSquintInnerL',
        'eyeSquintInnerR',
        'eyeCheekRaiseL',
        'eyeCheekRaiseR',
        'eyeFaceScrunchL',
        'eyeFaceScrunchR',
        'eyeUpperLidUpL',
        'eyeUpperLidUpR',
        'eyeRelaxL',
        'eyeRelaxR',
        'eyeLowerLidUpL',
        'eyeLowerLidUpR',
        'eyeLowerLidDownL',
        'eyeLowerLidDownR',
        'eyeLookUpL',
        'eyeLookUpR',
        'eyeLookDownL',
        'eyeLookDownR',
        'eyeLookLeftL',
        'eyeLookLeftR',
        'eyeLookRightL',
        'eyeLookRightR',
        'noseWrinkleL',
        'noseWrinkleR',
        'noseNostrilDepressL',
        'noseNostrilDepressR',
        'noseNostrilDilateL',
        'noseNostrilDilateR',
        'noseNostrilCompressL',
        'noseNostrilCompressR',
        'noseNasolabialDeepenL',
        'noseNasolabialDeepenR',
        'mouthCheekSuckL',
        'mouthCheekSuckR',
        'mouthCheekBlowL',
        'mouthCheekBlowR',
        'mouthLipsBlowL',
        'mouthLipsBlowR',
        'mouthLeft',
        'mouthRight',
        'mouthUp',
        'mouthDown',
        'mouthUpperLipRaiseL',
        'mouthUpperLipRaiseR',
        'mouthLowerLipDepressL',
        'mouthLowerLipDepressR',
        'mouthCornerPullL',
        'mouthCornerPullR',
        'mouthStretchL',
        'mouthStretchR',
        'mouthDimpleL',
        'mouthDimpleR',
        'mouthCornerDepressL',
        'mouthCornerDepressR',
        'mouthPressUL',
        'mouthPressUR',
        'mouthPressDL',
        'mouthPressDR',
        'mouthLipsPurseUL',
        'mouthLipsPurseUR',
        'mouthLipsPurseDL',
        'mouthLipsPurseDR',
        'mouthLipsTowardsUL',
        'mouthLipsTowardsUR',
        'mouthLipsTowardsDL',
        'mouthLipsTowardsDR',
        'mouthFunnelUL',
        'mouthFunnelUR',
        'mouthFunnelDL',
        'mouthFunnelDR',
        'mouthUpperLipBiteL',
        'mouthUpperLipBiteR',
        'mouthLowerLipBiteL',
        'mouthLowerLipBiteR',
        'mouthLipsTightenUL',
        'mouthLipsTightenUR',
        'mouthLipsTightenDL',
        'mouthLipsTightenDR',
        'mouthLipsPressL',
        'mouthLipsPressR',
        'mouthSharpCornerPullL',
        'mouthSharpCornerPullR',
        'mouthStickyUC',
        'mouthStickyUINL',
        'mouthStickyUINR',
        'mouthStickyUOUTL',
        'mouthStickyUOUTR',
        'mouthStickyDC',
        'mouthStickyDINL',
        'mouthStickyDINR',
        'mouthStickyDOUTL',
        'mouthStickyDOUTR',
        'mouthLipsStickyLPh1',
        'mouthLipsStickyLPh2',
        'mouthLipsStickyLPh3',
        'mouthLipsStickyRPh1',
        'mouthLipsStickyRPh2',
        'mouthLipsStickyRPh3',
        'mouthLipsPushUL',
        'mouthLipsPushUR',
        'mouthLipsPushDL',
        'mouthLipsPushDR',
        'mouthLipsPullUL',
        'mouthLipsPullUR',
        'mouthLipsPullDL',
        'mouthLipsPullDR',
        'mouthLipsThinUL',
        'mouthLipsThinUR',
        'mouthLipsThinDL',
        'mouthLipsThinDR',
        'mouthLipsThickUL',
        'mouthLipsThickUR',
        'mouthLipsThickDL',
        'mouthLipsThickDR',
        'mouthCornerSharpenUL',
        'mouthCornerSharpenUR',
        'mouthCornerSharpenDL',
        'mouthCornerSharpenDR',
        'mouthCornerRounderUL',
        'mouthCornerRounderUR',
        'mouthCornerRounderDL',
        'mouthCornerRounderDR',
        'mouthUpperLipTowardsTeethL',
        'mouthUpperLipTowardsTeethR',
        'mouthLowerLipTowardsTeethL',
        'mouthLowerLipTowardsTeethR',
        'mouthUpperLipShiftLeft',
        'mouthUpperLipShiftRight',
        'mouthLowerLipShiftLeft',
        'mouthLowerLipShiftRight',
        'mouthUpperLipRollInL',
        'mouthUpperLipRollInR',
        'mouthUpperLipRollOutL',
        'mouthUpperLipRollOutR',
        'mouthLowerLipRollInL',
        'mouthLowerLipRollInR',
        'mouthLowerLipRollOutL',
        'mouthLowerLipRollOutR',
        'mouthCornerUpL',
        'mouthCornerUpR',
        'mouthCornerDownL',
        'mouthCornerDownR',
        'mouthCornerWideL',
        'mouthCornerWideR',
        'mouthCornerNarrowL',
        'mouthCornerNarrowR',
        'jawOpen',
        'jawLeft',
        'jawRight',
        'jawFwd',
        'jawBack',
        'jawClenchL',
        'jawClenchR',
        'jawChinRaiseDL',
        'jawChinRaiseDR',
        'jawChinRaiseUL',
        'jawChinRaiseUR',
        'jawChinCompressL',
        'jawChinCompressR',
        'neckStretchL',
        'neckStretchR',
        'neckSwallowPh1',
        'neckSwallowPh2',
        'neckSwallowPh3',
        'neckSwallowPh4',
        'neckMastoidContractL',
        'neckMastoidContractR',
        'neckThroatDown',
        'neckThroatUp',
        'neckDigastricDown',
        'neckDigastricUp',
        'neckThroatExhale',
        'neckThroatInhale'
    ],
    'faceExprOffset': [
        {'eyeBlinkL': 'eyeLidPressL'},
        {'eyeBlinkR': 'eyeLidPressR'},
        {'noseWrinkleL': 'noseWrinkleUpperL'},
        {'noseWrinkleR': 'noseWrinkleUpperR'},
        {'mouthStretchL': 'mouthStretchLipsCloseL'},
        {'mouthStretchR': 'mouthStretchLipsCloseR'},
        {'jawOpen': 'mouthLipsTogetherUL'},
        {'jawOpen': 'mouthLipsTogetherUR'},
        {'jawOpen': 'mouthLipsTogetherDL'},
        {'jawOpen': 'mouthLipsTogetherDR'},
        {'jawOpen': 'jawOpenExtreme'}
    ],
    'teethTongueExpr': [
        'tongueUp',
        'tongueDown',
        'tongueLeft',
        'tongueRight',
        'tongueOut',
        'tongueIn',
        'tongueRollUp',
        'tongueRollDown',
        'tongueRollLeft',
        'tongueRollRight',
        'tongueTipUp',
        'tongueTipDown',
        'tongueTipLeft',
        'tongueTipRight',
        'tongueWide',
        'tongueNarrow',
        'tonguePress',
        'teethUpU',
        'teethUpD',
        'teethDownU',
        'teethDownD',
        'teethLeftU',
        'teethLeftD',
        'teethRightU',
        'teethRightD',
        'teethFwdU',
        'teethFwdD',
        'teethBackU',
        'teethBackD'
    ]
}
OFFSET_SHAPE_CONNECTION_INFO = [
    {
        'driverAttrs': ['CTRL_L_mouth_stretch.ty', 'CTRL_L_mouth_stretchLipsClose.ty'],
        'drivenAttr': '{0}.mouthStretchLipsCloseL'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_R_mouth_stretch.ty', 'CTRL_R_mouth_stretchLipsClose.ty'],
        'drivenAttr': '{0}.mouthStretchLipsCloseR'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_L_eye_blink.ty', 'CTRL_L_eye_lidPress.ty'],
        'drivenAttr': '{0}.eyeLidPressL'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_R_eye_blink.ty', 'CTRL_R_eye_lidPress.ty'],
        'drivenAttr': '{0}.eyeLidPressR'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_L_nose.ty', 'CTRL_L_nose_wrinkleUpper.ty'],
        'drivenAttr': '{0}.noseWrinkleUpperL'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_R_nose.ty', 'CTRL_R_nose_wrinkleUpper.ty'],
        'drivenAttr': '{0}.noseWrinkleUpperR'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_C_jaw.ty', 'CTRL_R_mouth_lipsTogetherU.ty'],
        'drivenAttr': '{0}.mouthLipsTogetherUR'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_C_jaw.ty', 'CTRL_L_mouth_lipsTogetherU.ty'],
        'drivenAttr': '{0}.mouthLipsTogetherUL'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_C_jaw.ty', 'CTRL_R_mouth_lipsTogetherD.ty'],
        'drivenAttr': '{0}.mouthLipsTogetherDR'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_C_jaw.ty', 'CTRL_L_mouth_lipsTogetherD.ty'],
        'drivenAttr': '{0}.mouthLipsTogetherDL'.format(FACIAL_OUT_ATTRS),
    },
    {
        'driverAttrs': ['CTRL_C_jaw.ty', 'CTRL_C_jaw_openExtreme.ty'],
        'drivenAttr': '{0}.jawOpenExtreme'.format(FACIAL_OUT_ATTRS),
    },
]


def createFacialSkeleton(sourceMesh):
    """Create facial skeleton with facial guide mesh.
    """
    # Import guide file
    guideFileNodes = cmds.file(FACIAL_GUIDE_FILE, i=True, returnNewNodes=True)
    targetMesh = None
    for node in guideFileNodes:
        try:
            if cmds.nodeType(node) == 'mesh':
                parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
                if parents:
                    targetMesh = parents[0]
                    break
        except Exception:
            pass

    # Register guide mesh to target mesh
    sourceUVSet = cmds.polyUVSet(sourceMesh, q=True, currentUVSet=True)[0]
    targetUVSet = cmds.polyUVSet(targetMesh, q=True, currentUVSet=True)[0]
    cmds.transferAttributes(sourceMesh, targetMesh, transferPositions=True, sampleSpace=3, sourceUvSpace=sourceUVSet, targetUvSpace=targetUVSet, searchMethod=3)

    # Create skeleton joints with follicles
    follicleTransforms = []
    for node in guideFileNodes:
        try:
            if cmds.nodeType(node) == 'follicle':
                parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
                if parents:
                    follicleTransforms.append(parents[0])
        except Exception:
            pass

    for folTransform in follicleTransforms:
        jnt = cmds.createNode('joint', name=folTransform.replace('_fol', ''))
        folPos = cmds.xform(folTransform, q=True, ws=True, t=True)
        cmds.xform(jnt, ws=True, t=folPos)

    if targetMesh:
        cmds.delete(targetMesh)
    if follicleTransforms:
        cmds.delete(follicleTransforms)


def cleanupRawMetaHuman():
    """Separate facial rig from raw metahuman rig.
    """
    # Change up axis z to y
    try:
        mel.eval('setUpAxis "y"')
    except Exception:
        pass
    toRotateObjects = ['root_drv', 'Lights', 'LOC_world']
    for item in toRotateObjects:
        try:
            cmds.setAttr('{}.rotate'.format(item), -90, 0, 0)
        except Exception:
            pass

    # Delete constrains in facial skeleton
    joints = cmds.ls('DHIhead:spine_04', dag=True, type='joint') or []
    for sel in joints:
        constraints = cmds.listConnections(sel, source=True, destination=False, type='constraint') or []
        if constraints:
            cmds.delete(constraints)

    # Delete facial constroller locator
    try:
        cmds.select([FACE_GUI_GRP, EYES_AIM_GRP], r=True)
        sels = cmds.ls(selection=True) or []
        for sel in sels:
            cons = cmds.listConnections(sel, source=True, destination=False, type='constraint') or []
            if cons:
                cmds.delete(cons)
    except Exception:
        pass
    try:
        cmds.delete(CONTROLLER_DRIVE_LOCATOR)
    except Exception:
        pass

    # Remove namespaces
    namespaces = ['DHIhead', 'DHIbody']
    for ns in namespaces:
        try:
            cmds.namespace(removeNamespace=ns, mergeNamespaceWithRoot=True)
        except Exception:
            try:
                cmds.namespace(rm=ns, mergeNamespaceWithRoot=True)
            except Exception:
                pass

    # Parent head rig group to world
    try:
        cmds.parent('head_grp', world=True)
    except Exception:
        pass
    try:
        cmds.rename('head_grp', 'metaHuman_grp')
    except Exception:
        pass

    # Delete unusing data
    try:
        cmds.delete('root_drv', 'root', 'rig', 'PSD')
    except Exception:
        pass

    # Delete display layers
    for displayLayer in cmds.ls(type='displayLayer') or []:
        try:
            cmds.delete(displayLayer)
        except Exception:
            pass

    # Hide unusing LOD groups
    usingLOD = 0
    for i in range(8):
        if i == usingLOD:
            continue
        try:
            cmds.delete('head_lod{}_grp'.format(i))
        except Exception:
            pass

    addPrefix()


def addPrefix():
    for jnt in cmds.ls(SKELETON_ROOT, dag=True, type='joint') or []:
        try:
            short = jnt.split('|')[-1]
            cmds.rename(jnt, 'mh_{}'.format(short))
        except Exception:
            pass


# def createTargetAttrsNode():
#     facialTargetAttrs = cmds.createNode('transform', name=FACIAL_OUT_ATTRS)
#     for attrName in cmds.listAttr(FACIAL_OUT_ATTRS, userDefined=True) or []:
#         cmds.addAttr(facialTargetAttrs, longName=attrName, attributeType='double', min=0, max=1, keyable=True)
#         # example: cmds.connectAttr('{}.{}'.format(sourceNode, attrName), '{}.{}'.format(facialTargetAttrs, attrName), force=True)


def alignMetaHumanToRig(eyeLJoint='Eye_L', eyeRJoint='Eye_R'):
    rigEyesCenterPoint = getCenterPoint(eyeLJoint, eyeRJoint)
    metaHumanEyesCenterPoint = getCenterPoint(SKELETON_EYE_L, SKELETON_EYE_R)
    metaHumanEyesCenterToRigEyesCenterVector = rigEyesCenterPoint - metaHumanEyesCenterPoint

    try:
        metaHumanSkelRootPos = cmds.xform(SKELETON_ROOT, q=True, ws=True, t=True)
        eyesAimGrpPos = cmds.xform(EYES_AIM_GRP, q=True, ws=True, t=True)
        metaHumanSkelRootVector = om.MVector(metaHumanSkelRootPos)
        eyesAimGrpVector = om.MVector(eyesAimGrpPos)

        newRootPos = metaHumanSkelRootVector + metaHumanEyesCenterToRigEyesCenterVector
        newEyesAimPos = eyesAimGrpVector + metaHumanEyesCenterToRigEyesCenterVector

        cmds.xform(SKELETON_ROOT, ws=True, t=(newRootPos.x, newRootPos.y, newRootPos.z))
        cmds.xform(EYES_AIM_GRP, ws=True, t=(newEyesAimPos.x, newEyesAimPos.y, newEyesAimPos.z))
    except Exception:
        pass

def getCenterPoint(transformA, transformB):
    aWorld = cmds.xform(transformA, q=True, ws=True, t=True)
    bWorld = cmds.xform(transformB, q=True, ws=True, t=True)
    aVec = om.MVector(aWorld)
    bVec = om.MVector(bWorld)
    centerVector = (aVec + bVec) * 0.5
    return centerVector


class Part:
    HEAD = 0
    TEETH = 1

def extractTargets(mesh, part):
    """Examples:
from takTools.rigging import metaHuman as mh
reload(mh)

mh.extractTargets('teeth_mesh', mh.Part.TEETH)
    """
    exprCtrl = FACIAL_OUT_ATTRS
    neutralPoints = getPoints(mesh)

    if part == Part.HEAD:
        # Extract face targets
        for faceExpr in EXPRESSION_INFO['faceExpr']:
            try:
                cmds.setAttr('{}.{}'.format(exprCtrl, faceExpr), 1)
            except Exception:
                pass
            try:
                cmds.duplicate(mesh, name=faceExpr)
                cmds.parent(faceExpr, world=True)
            except Exception:
                pass
            try:
                cmds.setAttr('{}.{}'.format(exprCtrl, faceExpr), 0)
            except Exception:
                pass

        # Extract face offset targets
        for faceExprOffsetInfo in EXPRESSION_INFO['faceExprOffset']:
            for expr, offset in faceExprOffsetInfo.items():
                try:
                    cmds.setAttr('{}.{}'.format(exprCtrl, expr), 1)
                except Exception:
                    pass

                exprPoints = getPoints(mesh)
                pointsDelta = getDelta(neutralPoints, exprPoints)

                try:
                    cmds.setAttr('{}.{}'.format(exprCtrl, offset), 1)
                except Exception:
                    pass
                try:
                    cmds.duplicate(mesh, name=offset)
                    cmds.parent(offset, world=True)
                except Exception:
                    pass
                try:
                    cmds.setAttr('{}.{}'.format(exprCtrl, offset), 0)
                except Exception:
                    pass

                subtractDelta(offset, pointsDelta)

                try:
                    cmds.setAttr('{}.{}'.format(exprCtrl, expr), 0)
                except Exception:
                    pass

    elif part == Part.TEETH:
        for faceExpr in EXPRESSION_INFO['teethTongueExpr']:
            try:
                cmds.setAttr('{}.{}'.format(exprCtrl, faceExpr), 1)
            except Exception:
                pass
            try:
                cmds.duplicate(mesh, name=faceExpr)
                cmds.parent(faceExpr, world=True)
            except Exception:
                pass
            try:
                cmds.setAttr('{}.{}'.format(exprCtrl, faceExpr), 0)
            except Exception:
                pass

def combineTargets(neutralMesh, targetMeshes):
    """
from takTools.rigging import metaHuman as mh
reload(mh)

neutralMesh = 'facial_neutral'
targetMeshes = cmds.ls(sl=True)
mh.combineTargets(neutralMesh, targetMeshes)
    """
    firstItem = targetMeshes[0]
    combineTargetName = firstItem.rsplit('L', 1)[0] if firstItem.endswith('L') else firstItem.rsplit('R', 1)[0]
    combinedTarget = cmds.duplicate(neutralMesh, name=combineTargetName)[0]
    bsNode = cmds.blendShape(targetMeshes, combinedTarget)[0]
    try:
        cmds.setAttr('{}.w[0]'.format(bsNode), 1)
    except Exception:
        pass
    try:
        cmds.setAttr('{}.w[1]'.format(bsNode), 1)
    except Exception:
        pass
    # delete construction history
    try:
        hist = cmds.listHistory(combinedTarget) or []
        if hist:
            cmds.delete(hist)
    except Exception:
        pass
    # remove temporary parent constraint
    try:
        cons = cmds.parentConstraint(targetMeshes, combinedTarget, mo=False)
        if cons:
            cmds.delete(cons)
    except Exception:
        pass

def getPoints(geo):
    dagPath = getDagPath(geo)
    meshFn = om.MFnMesh(dagPath)

    return meshFn.getPoints()

def getDelta(neutralPoints, deformedPoints):
    pointsDelta = om.MVectorArray()

    numPoints = len(neutralPoints)
    pointsDelta.setLength(numPoints)

    for i in range(numPoints):
        pointsDelta[i] = deformedPoints[i] - neutralPoints[i]

    return pointsDelta

def subtractDelta(geo, pointsDelta):
    dagPath = getDagPath(geo)
    vertIt = om.MItMeshVertex(dagPath)
    while not vertIt.isDone():
        vertIt.setPosition(vertIt.position() - pointsDelta[vertIt.index()])
        vertIt.next()

def getDagPath(geo):
    sels = om.MSelectionList()
    sels.add(geo)
    return sels.getDagPath(0)



def connectTargets(blendshape, part):
    """
    Examples:
        bs = 'blendShape2'
        mh.connectTargets(bs, mh.Part.HEAD)
    """
    bs = blendshape
    connectExistingTarget(FACIAL_OUT_ATTRS, bs)

    if part == Part.HEAD:
        # Setup offset shape attributes on CTRL_expressions node
        for info in OFFSET_SHAPE_CONNECTION_INFO:
            # info['drivenAttr'] is like 'node.attr'
            try:
                drivenNode, drivenAttr = info['drivenAttr'].split('.', 1)
            except Exception:
                continue
            try:
                if cmds.getAttr('{}.{}'.format(drivenNode, drivenAttr), lock=True):
                    continue
            except Exception:
                pass

            clamp = cmds.createNode('clamp')
            try:
                cmds.setAttr('{}.maxR'.format(clamp), 1)
            except Exception:
                pass
            multDouble = cmds.createNode('multDoubleLinear')

            # connect driverAttrs[0] -> clamp.inputR
            try:
                src = info['driverAttrs'][0]
                cmds.connectAttr(src, '{}.inputR'.format(clamp), force=True)
            except Exception:
                pass
            try:
                cmds.connectAttr('{}.outputR'.format(clamp), '{}.input1'.format(multDouble), force=True)
            except Exception:
                pass

            try:
                src2 = info['driverAttrs'][1]
                cmds.connectAttr(src2, '{}.input2'.format(multDouble), force=True)
            except Exception:
                pass

            try:
                cmds.connectAttr('{}.output'.format(multDouble), '{}.{}'.format(drivenNode, drivenAttr), force=True)
            except Exception:
                pass

def connectExistingTarget(bsOut, bsNode):
    """Connect bsOut attribute to bsNode attribute when attribute same name existing in bsNode

    Args:
        bsOut (str): Node connects to blendshape node
        bsNode (str): Blendshape node

    Examples:
        mh.connectExistingTarget('facial_bsOut', 'deltaBlendshape2')
    """
    # bsOut and bsNode are node names
    outNode = bsOut
    node = bsNode
    attrs = cmds.listAttr(outNode, userDefined=True, keyable=True) or []
    for attr in attrs:
        try:
            if cmds.getAttr('{}.{}'.format(outNode, attr), lock=True):
                continue
        except Exception:
            pass
        try:
            if cmds.attributeQuery(attr, node=node, exists=True):
                cmds.connectAttr('{}.{}'.format(outNode, attr), '{}.{}'.format(node, attr), force=True)
        except Exception:
            pass




def importTeethSkeleton():
    try:
        cmds.file(TEETH_SKELETON_FILE, i=True)
    except Exception:
        pass


def attachSampleMesh(sourceMesh, sampleMeshFile):
    guideFileNodes = cmds.file(sampleMeshFile, i=True, returnNewNodes=True)

    sampleMesh = None
    for node in guideFileNodes:
        try:
            if cmds.nodeType(node) == 'mesh':
                parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
                if parents:
                    sampleMesh = parents[0]
                    break
        except Exception:
            pass
    if sampleMesh:
        srcUVSet = cmds.polyUVSet(sourceMesh, q=True, currentUVSet=True)[0]
        targetUVSet = cmds.polyUVSet(sampleMesh, q=True, currentUVSet=True)[0]
        cmds.transferAttributes(sourceMesh, sampleMesh, transferPositions=True, sampleSpace=3, sourceUvSpace=srcUVSet, targetUvSpace=targetUVSet, searchMethod=3)



def setupSDK(jawCtrlAutoGrp='Jaw_ctrl_auto', eyeLCtrlAutoGrp='Eye_L_ctrl_auto', eyeRCtrlAutoGrp='Eye_R_ctrl_auto'):
    facialTargetAttrs = FACIAL_OUT_ATTRS
    try:
        cmds.file(SDK_ASSET_FILE, i=True)
    except Exception:
        pass
    jawSDKInput = 'jawSDK_input'
    jawSDKOutput = 'jawSDK_output'
    eyeLSDKInput = 'eyeLSDK_input'
    eyeLSDKOutput = 'eyeLSDK_output'
    eyeRSDKInput = 'eyeRSDK_input'
    eyeRSDKOutput = 'eyeRSDK_output'
    jawCtrlAutoGrp = jawCtrlAutoGrp
    eyeLCtrlAutoGrp = eyeLCtrlAutoGrp
    eyeRCtrlAutoGrp = eyeRCtrlAutoGrp

    def safeConnect(src, dst):
        try:
            cmds.connectAttr(src, dst, force=True)
        except Exception:
            pass

    safeConnect('{}.jawOpen'.format(facialTargetAttrs), '{}.jawOpen'.format(jawSDKInput))
    safeConnect('{}.jawLeft'.format(facialTargetAttrs), '{}.jawLeft'.format(jawSDKInput))
    safeConnect('{}.jawRight'.format(facialTargetAttrs), '{}.jawRight'.format(jawSDKInput))
    safeConnect('{}.jawFwd'.format(facialTargetAttrs), '{}.jawFwd'.format(jawSDKInput))
    safeConnect('{}.jawBack'.format(facialTargetAttrs), '{}.jawBack'.format(jawSDKInput))
    safeConnect('{}.translateX'.format(jawSDKOutput), '{}.translateX'.format(jawCtrlAutoGrp))
    safeConnect('{}.translateY'.format(jawSDKOutput), '{}.translateY'.format(jawCtrlAutoGrp))
    safeConnect('{}.translateZ'.format(jawSDKOutput), '{}.translateZ'.format(jawCtrlAutoGrp))
    safeConnect('{}.rotateX'.format(jawSDKOutput), '{}.rotateX'.format(jawCtrlAutoGrp))
    safeConnect('{}.rotateZ'.format(jawSDKOutput), '{}.rotateZ'.format(jawCtrlAutoGrp))

    safeConnect('{}.eyeLookUpL'.format(facialTargetAttrs), '{}.eyeLookUpL'.format(eyeLSDKInput))
    safeConnect('{}.eyeLookDownL'.format(facialTargetAttrs), '{}.eyeLookDownL'.format(eyeLSDKInput))
    safeConnect('{}.eyeLookLeftL'.format(facialTargetAttrs), '{}.eyeLookLeftL'.format(eyeLSDKInput))
    safeConnect('{}.eyeLookRightL'.format(facialTargetAttrs), '{}.eyeLookRightL'.format(eyeLSDKInput))
    safeConnect('{}.rotateX'.format(eyeLSDKOutput), '{}.rotateZ'.format(eyeLCtrlAutoGrp))
    safeConnect('{}.rotateY'.format(eyeLSDKOutput), '{}.rotateY'.format(eyeLCtrlAutoGrp))

    safeConnect('{}.eyeLookUpR'.format(facialTargetAttrs), '{}.eyeLookUpR'.format(eyeRSDKInput))
    safeConnect('{}.eyeLookDownR'.format(facialTargetAttrs), '{}.eyeLookDownR'.format(eyeRSDKInput))
    safeConnect('{}.eyeLookLeftR'.format(facialTargetAttrs), '{}.eyeLookLeftR'.format(eyeRSDKInput))
    safeConnect('{}.eyeLookRightR'.format(facialTargetAttrs), '{}.eyeLookRightR'.format(eyeRSDKInput))
    safeConnect('{}.rotateX'.format(eyeRSDKOutput), '{}.rotateZ'.format(eyeRCtrlAutoGrp))
    safeConnect('{}.rotateY'.format(eyeRSDKOutput), '{}.rotateY'.format(eyeRCtrlAutoGrp))


def setupEyeFollowControl(globalCtrl='global_ctrl', headCtrl='Head_ctrl'):
    try:
        cmds.parentConstraint(globalCtrl, SKELETON_ROOT, mo=True)
    except Exception:
        pass
    try:
        cmds.scaleConstraint(globalCtrl, SKELETON_ROOT, mo=True)
    except Exception:
        pass
    try:
        cmds.pointConstraint(headCtrl, SKELETON_HEAD, mo=True)
    except Exception:
        pass
    try:
        cmds.orientConstraint(headCtrl, SKELETON_HEAD, mo=True)
    except Exception:
        pass

    globalSpaceLoc = cmds.spaceLocator(name='eyesAim_globalSpace_loc')[0]
    globalSpaceLocZeroGrp = cmds.group(globalSpaceLoc, name='{}_zero'.format(globalSpaceLoc))
    try:
        cmds.matchTransform(globalSpaceLocZeroGrp, EYES_AIM_GRP)
    except Exception:
        pass
    try:
        cmds.parentConstraint(globalCtrl, globalSpaceLocZeroGrp, mo=True)
    except Exception:
        pass

    headSpaceLoc = cmds.spaceLocator(name='eyesAim_headSpace_loc')[0]
    headSpaceLocZeroGrp = cmds.group(headSpaceLoc, name='{}_zero'.format(headSpaceLoc))
    try:
        cmds.matchTransform(headSpaceLocZeroGrp, EYES_AIM_GRP)
    except Exception:
        pass
    try:
        cmds.parentConstraint(headCtrl, headSpaceLocZeroGrp, mo=True)
    except Exception:
        pass

    oldConst = cmds.listConnections(EYES_AIM_GRP, type='constraint', source=True, destination=False) or []
    if oldConst:
        try:
            cmds.delete(oldConst)
        except Exception:
            pass

    eyesAimFollowCtrl = EYES_AIM_FOLLOW_CTRL
    try:
        eyesAimConst = cmds.parentConstraint(globalSpaceLoc, headSpaceLoc, EYES_AIM_GRP, mo=True)
    except Exception:
        eyesAimConst = None
    revNode = cmds.createNode('reverse', name='eyesAimFollowCtrl_rev')
    try:
        cmds.connectAttr('{}.ty'.format(eyesAimFollowCtrl), '{}.inputX'.format(revNode), force=True)
    except Exception:
        pass
    try:
        if eyesAimConst:
            # parentConstraint returns constraint node name; find its name
            if isinstance(eyesAimConst, (list, tuple)):
                eyesAimConst = eyesAimConst[0]
            cmds.connectAttr('{}.outputX'.format(revNode), '{}.eyesAim_globalSpace_locW0'.format(eyesAimConst), force=True)
            cmds.connectAttr('{}.ty'.format(eyesAimFollowCtrl), '{}.eyesAim_headSpace_locW1'.format(eyesAimConst), force=True)
    except Exception:
        pass


def createSculptController(facialSkinJoint):
    """Example:
for skinJnt in cmds.ls(sl=True):
    createSculptController(skinJnt)
    """
    skinJnt = facialSkinJoint

    # Create out joint
    outJnt = cmds.duplicate(skinJnt, name=skinJnt.replace('_sk', '_outJnt'))[0]

    # Create controller
    ctrl = cmds.circle(ch=False, name=skinJnt.replace('_sk', '_ctrl'))[0]
    ctrlZero = '{0}_zero'.format(ctrl)
    cmds.group(ctrl, name=ctrlZero)
    try:
        cmds.matchTransform(ctrlZero, skinJnt)
    except Exception:
        pass

    # Redirect connection to out joint
    skinJntTIn = (cmds.listConnections('{}.translate'.format(skinJnt), plugs=True, source=True, destination=False) or [None])[0]
    skinJntRIn = (cmds.listConnections('{}.rotate'.format(skinJnt), plugs=True, source=True, destination=False) or [None])[0]

    translatePlus = cmds.createNode('plusMinusAverage', name='{0}_translate_plus'.format(skinJnt))
    rotatePlus = cmds.createNode('plusMinusAverage', name='{0}_rotate_plus'.format(skinJnt))

    try:
        if skinJntTIn:
            cmds.connectAttr(skinJntTIn, '{}.input3D[0]'.format(translatePlus), force=True)
    except Exception:
        pass
    try:
        if skinJntRIn:
            cmds.connectAttr(skinJntRIn, '{}.input3D[0]'.format(rotatePlus), force=True)
    except Exception:
        pass
    try:
        cmds.connectAttr('{}.translate'.format(ctrl), '{}.input3D[1]'.format(translatePlus), force=True)
    except Exception:
        pass
    try:
        cmds.connectAttr('{}.rotate'.format(ctrl), '{}.input3D[1]'.format(rotatePlus), force=True)
    except Exception:
        pass
    try:
        cmds.connectAttr('{}.output3D'.format(translatePlus), '{}.translate'.format(outJnt), force=True)
    except Exception:
        pass
    try:
        cmds.connectAttr('{}.output3D'.format(rotatePlus), '{}.rotate'.format(outJnt), force=True)
    except Exception:
        pass
    try:
        cmds.connectAttr('{}.translate'.format(outJnt), '{}.translate'.format(skinJnt), force=True)
    except Exception:
        pass
    try:
        cmds.connectAttr('{}.rotate'.format(outJnt), '{}.rotate'.format(skinJnt), force=True)
    except Exception:
        pass

    # Scale constraint
    try:
        cmds.scaleConstraint(outJnt, skinJnt)
    except Exception:
        pass

    # Lock and hide unusing channels
    unuseChannels = [ch+axis for ch in 'rs' for axis in 'xyz']
    for unuseChannel in unuseChannels:
        try:
            cmds.setAttr('{}.{}'.format(ctrl, unuseChannel), lock=True)
        except Exception:
            pass
        try:
            cmds.setAttr('{}.{}'.format(ctrl, unuseChannel), keyable=False)
        except Exception:
            pass


def publishWrinkleMapAttrs(skeletonRoot='Root'):
    skRoot = skeletonRoot
    wmAttrs = cmds.listAttr(WRINKLE_MAP_MULT, userDefined=True) or []
    for attrName in wmAttrs:
        try:
            cmds.addAttr(skRoot, longName=attrName, attributeType='double', keyable=True)
        except Exception:
            pass
        try:
            cmds.connectAttr('{}.{}'.format(WRINKLE_MAP_MULT, attrName), '{}.{}'.format(skRoot, attrName), force=True)
        except Exception:
            pass


def redirectSourcePathes():
    """Redirect metahuman source file pathes.
    """
    redirectDNAPath()
    redirectShaderPath()

def redirectDNAPath():
    """Copy dna file to current scene data folder. And edit dnaFilePath of embeddedNodeRL4 node.
    """
    dnaNodes = cmds.ls(type='embeddedNodeRL4') or []
    sceneName = ''
    try:
        sceneName = cmds.file(q=True, sn=True)
    except Exception:
        sceneName = cmds.file(q=True, sceneName=True) or ''
    rigDir = os.path.dirname(sceneName) if sceneName else ''
    for dnaNode in dnaNodes:
        try:
            origFile = cmds.getAttr('{}.dnaFilePath'.format(dnaNode))
        except Exception:
            continue
        targetFile = os.path.join(rigDir, 'data', os.path.basename(origFile))
        try:
            shutil.copy(origFile, targetFile)
        except IOError:
            try:
                os.makedirs(os.path.dirname(targetFile))
                shutil.copy(origFile, targetFile)
            except Exception:
                pass

        try:
            cmds.setAttr('{}.dnaFilePath'.format(dnaNode), targetFile, type='string')
        except Exception:
            pass

def redirectShaderPath(targetPath='Z:/maya/plug-ins/metaHuman/SourceAssets/shaders'):
    """Edit shader file directory path to server.

    :param targetPath: Shader directory path on server, defaults to 'Z:/maya/plug-ins/metaHuman/SourceAssets/shaders'
    :type targetPath: str, optional
    """
    for dxShader in cmds.ls(type='dx11Shader') or []:
        try:
            origPath = cmds.getAttr('{}.shader'.format(dxShader))
            newPath = os.path.join(targetPath, os.path.basename(origPath))
            cmds.setAttr('{}.shader'.format(dxShader), newPath, type='string')
        except Exception:
            pass


def connectFaceControlBoard(topNode):
    """
    topNode = 'Hi:Face_ControlBoard_CtrlRig'
    connectFaceControlBoard(topNode)
    """
    faceCtrlNodes = cmds.listRelatives(topNode, type='transform')
    chs = [ch + axis for ch in 'trs' for axis in 'xyz']

    for ctrlNode in faceCtrlNodes:
        trgCtrl = ctrlNode.replace('Hi:', '')
        for ch in chs:
            try:
                cmds.connectAttr('{}.{}'.format(ctrlNode, ch), '{}.{}'.format(trgCtrl, ch), f=True)
            except:
                pass


def disconnectFaceControlBoard(topNode):
    """
    topNode = 'Hi:Face_ControlBoard_CtrlRig'
    disconnectFaceControlBoard(topNode)
    """
    faceCtrlNodes = cmds.listRelatives(topNode, type='transform')
    chs = [ch + axis for ch in 'trs' for axis in 'xyz']

    for ctrlNode in faceCtrlNodes:
        trgCtrl = ctrlNode.replace('Hi:', '')
        for ch in chs:
            try:
                connections = cmds.listConnections('{}.{}'.format(ctrlNode, ch), plugs=True, source=False)
                if connections:
                    for connection in connections:
                        cmds.disconnectAttr('{}.{}'.format(ctrlNode, ch), connection)
            except:
                pass


'''
from takTools.rigging import metaHuman as mh
reload(mh)


# Create skeleton
mh.createFacialSkeleton(sourceMesh='Head_mesh')
mh.importTeethSkeleton()


# Global Setup
mh.createTargetAttrsNode()
mh.alignMetaHumanToRig(eyeLJoint='eye_LF', eyeRJoint='eye_RT')
mh.setupSDK(jawCtrlAutoGrp='FKExtraJaw_M', eyeLCtrlAutoGrp='FKExtraEye_L', eyeRCtrlAutoGrp='FKExtraEye_R')
mh.setupEyeFollowControl(globalCtrl='Main', headCtrl='FKHead_M')


# Head Setup
mh.extractTargets('head_lod0_mesh', mh.Part.HEAD)

sels = cmds.ls(sl=True)
neuturalMesh = sels[0]
targetMeshes = sels[:-1]
retargetMesh = sels[-1]
mh.connectTargets(neuturalMesh, targetMeshes, retargetMesh, mh.Part.HEAD)

sampleFile = r"C:\GoogleDrive\programs_env\maya\modules\ironRig\resources\metaHuman_head_sampleMesh.ma"
mh.attachSampleMesh('head_retarget_mesh', sampleFile)


# Teeth Setup
mh.extractTargets('teeth_lod0_mesh', mh.Part.TEETH)

sels = cmds.ls(sl=True)
neuturalMesh = sels[0]
targetMeshes = sels[:-1]
retargetMesh = sels[-1]
mh.connectTargets(neuturalMesh, targetMeshes, retargetMesh, mh.Part.TEETH)

sampleMeshFile = r"C:\GoogleDrive\programs_env\maya\modules\ironRig\resources\metaHuman_tongue_sampleMesh.ma"
mh.attachSampleMesh('teeth_retarget_mesh', sampleMeshFile)

sampleMeshFile = r"C:\GoogleDrive\programs_env\maya\modules\ironRig\resources\metaHuman_teeth_sampleMesh.ma"
mh.attachSampleMesh('teeth_retarget_mesh', sampleMeshFile)


# Cleanup
mh.redirectSourcePathes()
mh.publishWrinkleMapAttrs(skeletonRoot='Root')
'''