import os
import shutil
from maya.api import OpenMaya as om
from maya import cmds
import pymel.core as pm

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
    guideFileNodes = pm.importFile(FACIAL_GUIDE_FILE, returnNewNodes=True)
    targetMesh = [node.getTransform() for node in guideFileNodes if node.nodeType() == 'mesh'][0]

    # Register guide mesh to target mesh
    sourceUVSet = pm.polyUVSet(sourceMesh, q=True, currentUVSet=True)[0]
    targetUVSet = pm.polyUVSet(targetMesh, q=True, currentUVSet=True)[0]
    pm.transferAttributes(sourceMesh, targetMesh, transferPositions=True, sampleSpace=3, sourceUvSpace=sourceUVSet, targetUvSpace=targetUVSet, searchMethod=3)

    # Create skeleton joints with follicles
    follicleTransforms = []
    for node in guideFileNodes:
        try:
            if node.nodeType() == 'follicle':
                follicleTransforms.append(node.getTransform())
        except:
            pass

    for folTransform in follicleTransforms:
        jnt = pm.createNode('joint', n=folTransform.replace('_fol', ''))
        folPos = folTransform.getTranslation(space='world')
        jnt.setTranslation(folPos, space='world')

    pm.delete(targetMesh)
    pm.delete(follicleTransforms)


def cleanupRawMetaHuman():
    """Separate facial rig from raw metahuman rig.
    """
    # Change up axis z to y
    pm.env.setUpAxis('y')
    toRotateObjects = ['root_drv', 'Lights', 'LOC_world']
    for item in toRotateObjects:
        pm.setAttr('{}.rotate'.format(item), -90, 0, 0)

    # Delete constrains in facial skeleton
    pm.select('DHIhead:spine_04', hi=True)
    for sel in pm.selected(type='joint'):
        constraints = sel.inputs(type='constraint')
        if constraints:
            pm.delete(constraints)

    # Delete facial constroller locator
    pm.select([FACE_GUI_GRP, EYES_AIM_GRP], r=True)
    for sel in pm.selected():
        pm.delete(sel.inputs(type='constraint'))
    pm.delete(CONTROLLER_DRIVE_LOCATOR)

    # Remove namespaces
    namespaces = ['DHIhead', 'DHIbody']
    for ns in namespaces:
        pm.namespace(rm=ns, mergeNamespaceWithRoot=True)

    # Parent head rig group to world
    pm.parent('head_grp', world=True)
    pm.rename('head_grp', 'metaHuman_grp')

    # Delete unusing data
    pm.delete('root_drv', 'root', 'rig', 'PSD')

    # Delete display layers
    for displayLayer in pm.ls(type='displayLayer'):
        pm.delete(displayLayer)

    # Hide unusing LOD groups
    usingLOD = 0
    for i in range(8):
        if i == usingLOD:
            continue
        pm.delete('head_lod{}_grp'.format(i))

    addPrefix()


def addPrefix():
    for jnt in pm.ls(SKELETON_ROOT, dag=True, type='joint'):
        jnt.rename('mh_{}',format(jnt))


# def createTargetAttrsNode():
#     facialTargetAttrs = pm.createNode('transform', n=FACIAL_OUT_ATTRS)
#     for facsAttr in pm.PyNode(FACIAL_OUT_ATTRS).listAttr(ud=True):
#         attrName = facsAttr.attrName()
#         pm.addAttr(facialTargetAttrs, ln=attrName, at='double', min=0, max=1, keyable=True)
#         facsAttr >> facialTargetAttrs.attr(attrName)


def alignMetaHumanToRig(eyeLJoint='Eye_L', eyeRJoint='Eye_R'):
    eyeLJoint = pm.PyNode(eyeLJoint)
    eyeRJoint = pm.PyNode(eyeRJoint)
    metaHumanEyeL = pm.PyNode(SKELETON_EYE_L)
    metaHumanEyeR = pm.PyNode(SKELETON_EYE_R)
    metaHumanSkelRoot = pm.PyNode(SKELETON_ROOT)
    eyesAimGrp = pm.PyNode(EYES_AIM_GRP)

    rigEyesCenterPoint = getCenterPoint(eyeLJoint, eyeRJoint)
    metaHumanEyesCenterPoint = getCenterPoint(metaHumanEyeL, metaHumanEyeR)
    metaHumanEyesCenterToRigEyesCenterVector = rigEyesCenterPoint - metaHumanEyesCenterPoint

    metaHumanSkelRootVector = metaHumanSkelRoot.getTranslation(space='world')
    eyesAimGrpVector = eyesAimGrp.getTranslation(space='world')

    metaHumanSkelRoot.setTranslation(metaHumanSkelRootVector + metaHumanEyesCenterToRigEyesCenterVector, space='world')
    eyesAimGrp.setTranslation(eyesAimGrpVector + metaHumanEyesCenterToRigEyesCenterVector, space='world')

def getCenterPoint(transformA, transformB):
    aWorldVector = transformA.getTranslation(space='world')
    bWorldVector = transformB.getTranslation(space='world')
    centerVector = (aWorldVector + bWorldVector) * 0.5

    return pm.dt.Point(centerVector)


class Part:
    HEAD = 0
    TEETH = 1

def extractTargets(mesh, part):
    """Examples:
from takTools.rigging import metaHuman as mh
reload(mh)

mh.extractTargets('teeth_mesh', mh.Part.TEETH)
    """
    exprCtrl = pm.PyNode(FACIAL_OUT_ATTRS)
    neutralPoints = getPoints(mesh)

    if part == Part.HEAD:
        # Extract face targets
        for faceExpr in EXPRESSION_INFO['faceExpr']:
            exprCtrl.attr(faceExpr).set(1)
            pm.duplicate(mesh, n=faceExpr)
            pm.parent(faceExpr, w=True)
            exprCtrl.attr(faceExpr).set(0)

        # Extract face offset targets
        for faceExprOffsetInfo in EXPRESSION_INFO['faceExprOffset']:
            for expr, offset in faceExprOffsetInfo.items():
                exprCtrl.attr(expr).set(1)

                exprPoints = getPoints(mesh)
                pointsDelta = getDelta(neutralPoints, exprPoints)

                exprCtrl.attr(offset).set(1)
                pm.duplicate(mesh, n=offset)
                pm.parent(offset, w=True)
                exprCtrl.attr(offset).set(0)

                subtractDelta(offset, pointsDelta)

                exprCtrl.attr(expr).set(0)

    elif part == Part.TEETH:
        for faceExpr in EXPRESSION_INFO['teethTongueExpr']:
            exprCtrl.attr(faceExpr).set(1)
            pm.duplicate(mesh, n=faceExpr)
            pm.parent(faceExpr, w=True)
            exprCtrl.attr(faceExpr).set(0)

def combineTargets(neutralMesh, targetMeshes):
    """
from takTools.rigging import metaHuman as mh
reload(mh)

neutralMesh = 'facial_neutral'
targetMeshes = pm.selected()
mh.combineTargets(neutralMesh, targetMeshes)
    """
    firstItem = targetMeshes[0]
    combineTargetName = firstItem.rsplit('L', 1)[0] if firstItem.endswith('L') else firstItem.rsplit('R', 1)[0]
    combinedTarget = pm.duplicate(neutralMesh, n=combineTargetName)
    bs = pm.blendShape(targetMeshes, combinedTarget)[0]
    bs.setWeight(0, 1)
    bs.setWeight(1, 1)
    pm.delete(combinedTarget, ch=True)
    pm.delete(pm.parentConstraint(targetMeshes, combinedTarget, mo=False))

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
    bs = pm.PyNode(blendshape)
    connectExistingTarget(FACIAL_OUT_ATTRS, bs)

    if part == Part.HEAD:
        # Setup offset shape attributes on CTRL_expressions node
        for info in OFFSET_SHAPE_CONNECTION_INFO:
            if pm.PyNode(info['drivenAttr']).isLocked():
                continue

            clamp = pm.createNode('clamp')
            clamp.maxR.set(1)
            multDouble = pm.createNode('multDoubleLinear')

            pm.PyNode(info['driverAttrs'][0]) >> clamp.inputR
            clamp.outputR >> multDouble.input1

            pm.PyNode(info['driverAttrs'][1]) >> multDouble.input2

            multDouble.output >> pm.PyNode(info['drivenAttr'])

def connectExistingTarget(bsOut, bsNode):
    """Connect bsOut attribute to bsNode attribute when attribute same name existing in bsNode

    Args:
        bsOut (str): Node connects to blendshape node
        bsNode (str): Blendshape node

    Examples:
        mh.connectExistingTarget('facial_bsOut', 'deltaBlendshape2')
    """
    bsOut = pm.PyNode(bsOut)
    bsNode = pm.PyNode(bsNode)
    attrs = [attr for attr in bsOut.listAttr(ud=True, keyable=True) if not attr.isLocked()]
    for attr in attrs:
        exprName = attr.attrName()
        if bsNode.hasAttr(exprName):
            attr >> bsNode.attr(exprName)




def importTeethSkeleton():
    pm.importFile(TEETH_SKELETON_FILE)


def attachSampleMesh(sourceMesh, sampleMeshFile):
    guideFileNodes = pm.importFile(sampleMeshFile, returnNewNodes=True)

    sampleMesh = None
    for node in guideFileNodes:
        try:
            if node.nodeType() == 'mesh':
                sampleMesh = node.getTransform()
        except:
            pass
    srcUVSet = pm.polyUVSet(sourceMesh, q=True, currentUVSet=True)[0]
    targetUVSet = pm.polyUVSet(sampleMesh, q=True, currentUVSet=True)[0]
    pm.transferAttributes(sourceMesh, sampleMesh, transferPositions=True, sampleSpace=3, sourceUvSpace=srcUVSet, targetUvSpace=targetUVSet, searchMethod=3)



def setupSDK(jawCtrlAutoGrp='Jaw_ctrl_auto', eyeLCtrlAutoGrp='Eye_L_ctrl_auto', eyeRCtrlAutoGrp='Eye_R_ctrl_auto'):
    facialTargetAttrs = pm.PyNode(FACIAL_OUT_ATTRS)
    pm.importFile(SDK_ASSET_FILE)
    jawSDKInput = pm.PyNode('jawSDK_input')
    jawSDKOutput = pm.PyNode('jawSDK_output')
    eyeLSDKInput = pm.PyNode('eyeLSDK_input')
    eyeLSDKOutput = pm.PyNode('eyeLSDK_output')
    eyeRSDKInput = pm.PyNode('eyeRSDK_input')
    eyeRSDKOutput = pm.PyNode('eyeRSDK_output')
    jawCtrlAutoGrp = pm.PyNode(jawCtrlAutoGrp)
    eyeLCtrlAutoGrp = pm.PyNode(eyeLCtrlAutoGrp)
    eyeRCtrlAutoGrp = pm.PyNode(eyeRCtrlAutoGrp)

    facialTargetAttrs.jawOpen >> jawSDKInput.jawOpen
    facialTargetAttrs.jawLeft >> jawSDKInput.jawLeft
    facialTargetAttrs.jawRight >> jawSDKInput.jawRight
    facialTargetAttrs.jawFwd >> jawSDKInput.jawFwd
    facialTargetAttrs.jawBack >> jawSDKInput.jawBack
    jawSDKOutput.translateX >> jawCtrlAutoGrp.translateX
    jawSDKOutput.translateY >> jawCtrlAutoGrp.translateY
    jawSDKOutput.translateZ >> jawCtrlAutoGrp.translateZ
    jawSDKOutput.rotateX >> jawCtrlAutoGrp.rotateX
    jawSDKOutput.rotateZ >> jawCtrlAutoGrp.rotateZ

    facialTargetAttrs.eyeLookUpL >> eyeLSDKInput.eyeLookUpL
    facialTargetAttrs.eyeLookDownL >> eyeLSDKInput.eyeLookDownL
    facialTargetAttrs.eyeLookLeftL >> eyeLSDKInput.eyeLookLeftL
    facialTargetAttrs.eyeLookRightL >> eyeLSDKInput.eyeLookRightL
    eyeLSDKOutput.rotateX >> eyeLCtrlAutoGrp.rotateZ
    eyeLSDKOutput.rotateY >> eyeLCtrlAutoGrp.rotateY

    facialTargetAttrs.eyeLookUpR >> eyeRSDKInput.eyeLookUpR
    facialTargetAttrs.eyeLookDownR >> eyeRSDKInput.eyeLookDownR
    facialTargetAttrs.eyeLookLeftR >> eyeRSDKInput.eyeLookLeftR
    facialTargetAttrs.eyeLookRightR >> eyeRSDKInput.eyeLookRightR
    eyeRSDKOutput.rotateX >> eyeRCtrlAutoGrp.rotateZ
    eyeRSDKOutput.rotateY >> eyeRCtrlAutoGrp.rotateY


def setupEyeFollowControl(globalCtrl='global_ctrl', headCtrl='Head_ctrl'):
    pm.parentConstraint(globalCtrl, SKELETON_ROOT, mo=True)
    pm.scaleConstraint(globalCtrl, SKELETON_ROOT, mo=True)
    pm.pointConstraint(headCtrl, SKELETON_HEAD, mo=True)
    pm.orientConstraint(headCtrl, SKELETON_HEAD, mo=True)

    globalSpaceLoc = pm.spaceLocator(n='eyesAim_globalSpace_loc')
    globalSpaceLocZeroGrp = pm.group(globalSpaceLoc, n='{0}_zero'.format(globalSpaceLoc))
    pm.matchTransform(globalSpaceLocZeroGrp, EYES_AIM_GRP)
    pm.parentConstraint(globalCtrl, globalSpaceLocZeroGrp, mo=True)

    headSpaceLoc = pm.spaceLocator(n='eyesAim_headSpace_loc')
    headSpaceLocZeroGrp = pm.group(headSpaceLoc, n='{0}_zero'.format(headSpaceLoc))
    pm.matchTransform(headSpaceLocZeroGrp, EYES_AIM_GRP)
    pm.parentConstraint(headCtrl, headSpaceLocZeroGrp, mo=True)

    eyesAimGrp = pm.PyNode(EYES_AIM_GRP)
    oldConst = eyesAimGrp.inputs(type='constraint')
    if oldConst: pm.delete(oldConst)

    eyesAimFollowCtrl = pm.PyNode(EYES_AIM_FOLLOW_CTRL)
    eyesAimConst = pm.parentConstraint(globalSpaceLoc, headSpaceLoc, EYES_AIM_GRP, mo=True)
    revNode = pm.createNode('reverse', name='eyesAimFollowCtrl_rev')
    eyesAimFollowCtrl.ty >> revNode.inputX
    revNode.outputX >> eyesAimConst.eyesAim_globalSpace_locW0
    eyesAimFollowCtrl.ty >> eyesAimConst.eyesAim_headSpace_locW1


def createSculptController(facialSkinJoint):
    """Example:
for skinJnt in pm.selected():
    createSculptController(skinJnt)
    """
    skinJnt = pm.PyNode(facialSkinJoint)

    # Create out joint
    outJnt = pm.duplicate(skinJnt, n=skinJnt.replace('_sk', '_outJnt'))[0]

    # Create controller
    ctrl = pm.circle(ch=False, n=skinJnt.replace('_sk', '_ctrl'))[0]
    ctrlZero = '{0}_zero'.format(ctrl)
    pm.group(ctrl, n=ctrlZero)
    pm.matchTransform(ctrlZero, skinJnt)

    # Redirect connection to out joint
    skinJntTIn = skinJnt.translate.inputs(plugs=True)[0]
    skinJntRIn = skinJnt.rotate.inputs(plugs=True)[0]
    skinJntTIn // skinJnt.translate
    skinJntRIn // skinJnt.rotate

    translatePlus = pm.createNode('plusMinusAverage', n='{0}_translate_plus'.format(skinJnt))
    rotatePlus = pm.createNode('plusMinusAverage', n='{0}_rotate_plus'.format(skinJnt))

    skinJntTIn >> translatePlus.input3D[0]
    skinJntRIn >> rotatePlus.input3D[0]
    ctrl.translate >> translatePlus.input3D[1]
    ctrl.rotate >> rotatePlus.input3D[1]
    translatePlus.output3D >> outJnt.translate
    rotatePlus.output3D >> outJnt.rotate
    outJnt.translate >> skinJnt.translate
    outJnt.rotate >> skinJnt.rotate

    # Scale constraint
    pm.scaleConstraint(outJnt, skinJnt)

    # Lock and hide unusing channels
    unuseChannels = [ch+axis for ch in 'rs' for axis in 'xyz']
    for unuseChannel in unuseChannels:
        ctrl.attr(unuseChannel).lock(True)
        ctrl.attr(unuseChannel).setKeyable(False)


def publishWrinkleMapAttrs(skeletonRoot='Root'):
    skeletonRoot = pm.PyNode(skeletonRoot)
    for wmAttr in pm.PyNode(WRINKLE_MAP_MULT).listAttr(ud=True):
        attrName = wmAttr.attrName()
        pm.addAttr(skeletonRoot, ln=attrName, at='double', keyable=True)
        wmAttr >> skeletonRoot.attr(attrName)


def redirectSourcePathes():
    """Redirect metahuman source file pathes.
    """
    redirectDNAPath()
    redirectShaderPath()

def redirectDNAPath():
    """Copy dna file to current scene data folder. And edit dnaFilePath of embeddedNodeRL4 node.
    """
    dnaNodes = pm.ls(type='embeddedNodeRL4')
    for dnaNode in dnaNodes:
        origFile = dnaNode.dnaFilePath.get()
        rigDir = pm.env.sceneName().dirname()
        targetFile = os.path.join(rigDir, 'data', os.path.basename(origFile))
        try:
            shutil.copy(origFile, targetFile)
        except IOError as io_err:
            os.makedirs(os.path.dirname(targetFile))
            shutil.copy(origFile, targetFile)

        dnaNode.dnaFilePath.set(targetFile)

def redirectShaderPath(targetPath='Z:/maya/plug-ins/metaHuman/SourceAssets/shaders'):
    """Edit shader file directory path to server.

    :param targetPath: Shader directory path on server, defaults to 'Z:/maya/plug-ins/metaHuman/SourceAssets/shaders'
    :type targetPath: str, optional
    """
    for dxShader in pm.ls(type='dx11Shader'):
        origPath = dxShader.shader.get()
        newPath = os.path.join(targetPath, os.path.basename(origPath))
        dxShader.shader.set(newPath)


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

sels = pm.selected()
neuturalMesh = sels[0]
targetMeshes = sels[:-1]
retargetMesh = sels[-1]
mh.connectTargets(neuturalMesh, targetMeshes, retargetMesh, mh.Part.HEAD)

sampleFile = r"C:\GoogleDrive\programs_env\maya\modules\ironRig\resources\metaHuman_head_sampleMesh.ma"
mh.attachSampleMesh('head_retarget_mesh', sampleFile)


# Teeth Setup
mh.extractTargets('teeth_lod0_mesh', mh.Part.TEETH)

sels = pm.selected()
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