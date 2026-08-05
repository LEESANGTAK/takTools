import os
import re
from maya import cmds, mel
from . import mesh as meshUtil; reload(meshUtil)
from . import skin as skinUtil; reload(skinUtil)
from . import material as matUtil
from . import blendshape as bsUtil; reload(bsUtil)
from collections import OrderedDict

"""
from takTools.utils import vroid as vrUtil
reload(vrUtil)

fbx = r"C:\Users\chst2\Downloads\boy001\boy001\untitled.fbx"
texDir = r"C:\Users\chst2\Downloads\boy001\boy001\textures"
vrUtil.cleanup(fbx, texDir, 'boy001')

fbx = r"C:\Users\chst2\Downloads\untitled.fbx"
texDir = r"C:\Users\chst2\Downloads\textures"
vrUtil.cleanup(fbx, texDir, 'sulrena')

vrUtil.setupHumanIK()
"""

# ------------------------------- Constants ---------------------------------------------
MESHES = ['Face', 'Body', 'Hair']
UNUSING_NODES = ['Light', 'Camera', 'Armature', 'null1']
MAT_INFO = {
    'FaceMouth_00_FACE': '_01.png',
    'EyeIris_00_EYE': '_02.png',
    'EyeHighlight_00_EYE': '_03.png',
    'Face_00_SKIN': '_04.png',
    'EyeWhite_00_EYE': '_06.png',
    'FaceBrow_00_FACE': '_07.png',
    'FaceEyelash_00_FACE': '_08.png',
    'FaceEyeline_00_FACE': '_09.png',
    'Body_00_SKIN': '_10.png',
}

VR_TARGETS_INFO = OrderedDict([
    ('all', ['Fcl_ALL_Neutral',
             'Fcl_ALL_Angry',
             'Fcl_ALL_Fun',
             'Fcl_ALL_Joy',
             'Fcl_ALL_Sorrow',
             'Fcl_ALL_Surprised']),
    ('brow', ['Fcl_BRW_Angry',
              'Fcl_BRW_Fun',
              'Fcl_BRW_Joy',
              'Fcl_BRW_Sorrow',
              'Fcl_BRW_Surprised']),
    ('eye', ['Fcl_EYE_Natural',
             'Fcl_EYE_Angry',
             'Fcl_EYE_Close',
             'Fcl_EYE_Close_L',
             'Fcl_EYE_Close_R',
             'Fcl_EYE_Fun',
             'Fcl_EYE_Highlight_Hide',
             'Fcl_EYE_Iris_Hide',
             'Fcl_EYE_Joy',
             'Fcl_EYE_Joy_L',
             'Fcl_EYE_Joy_R',
             'Fcl_EYE_Sorrow',
             'Fcl_EYE_Spread',
             'Fcl_EYE_Surprised']),
    ('mouth', ['Fcl_MTH_Neutral',
               'Fcl_MTH_Angry',
               'Fcl_MTH_Fun',
               'Fcl_MTH_Joy',
               'Fcl_MTH_Sorrow',
               'Fcl_MTH_Surprised',
               'Fcl_MTH_Close',
               'Fcl_MTH_Up',
               'Fcl_MTH_Down',
               'Fcl_MTH_Large',
               'Fcl_MTH_Small',
               'Fcl_MTH_SkinFung',
               'Fcl_MTH_SkinFung_L',
               'Fcl_MTH_SkinFung_R',
               'Fcl_MTH_A',
               'Fcl_MTH_E',
               'Fcl_MTH_I',
               'Fcl_MTH_O',
               'Fcl_MTH_U']),
    ('teeth', ['Fcl_HA_Fung1',
               'Fcl_HA_Fung1_Low',
               'Fcl_HA_Fung1_Up',
               'Fcl_HA_Fung2',
               'Fcl_HA_Fung2_Low',
               'Fcl_HA_Fung2_Up',
               'Fcl_HA_Fung3',
               'Fcl_HA_Fung3_Low',
               'Fcl_HA_Fung3_Up',
               'Fcl_HA_Short',
               'Fcl_HA_Short_Low',
               'Fcl_HA_Short_Up',
               'Fcl_HA_Hide'])
])

ARKIT_TARGETS = [
    'browInnerUp',
    'browDownLeft',
    'browDownRight',
    'browOuterUpLeft',
    'browOuterUpRight',
    'eyeLookUpLeft',
    'eyeLookUpRight',
    'eyeLookDownLeft',
    'eyeLookDownRight',
    'eyeLookInLeft',
    'eyeLookInRight',
    'eyeLookOutLeft',
    'eyeLookOutRight',
    'eyeBlinkLeft',
    'eyeBlinkRight',
    'eyeSquintLeft',
    'eyeSquintRight',
    'eyeWideLeft',
    'eyeWideRight',
    'cheekPuff',
    'cheekSquintLeft',
    'cheekSquintRight',
    'noseSneerLeft',
    'noseSneerRight',
    'jawOpen',
    'jawForward',
    'jawLeft',
    'jawRight',
    'mouthFunnel',
    'mouthPucker',
    'mouthLeft',
    'mouthRight',
    'mouthRollUpper',
    'mouthRollLower',
    'mouthShrugUpper',
    'mouthShrugLower',
    'mouthClose',
    'mouthSmileLeft',
    'mouthSmileRight',
    'mouthFrownLeft',
    'mouthFrownRight',
    'mouthDimpleLeft',
    'mouthDimpleRight',
    'mouthUpperUpLeft',
    'mouthUpperUpRight',
    'mouthLowerDownLeft',
    'mouthLowerDownRight',
    'mouthPressLeft',
    'mouthPressRight',
    'mouthStretchLeft',
    'mouthStretchRight',
    'tongueOut'
]

HIK_MAPPINGS = [
    ["J_Bip_C_Head", 15],
    ["J_Bip_C_Hips", 1],
    ["J_Bip_C_Neck", 20],
    ["J_Bip_C_Spine", 8],
    ["J_Bip_C_UpperChest", 23],
    ["J_Bip_L_Foot", 4],
    ["J_Bip_L_Hand", 11],
    ["J_Bip_L_Index1", 54],
    ["J_Bip_L_Index2", 55],
    ["J_Bip_L_Index3", 56],
    ["J_Bip_L_Little1", 66],
    ["J_Bip_L_Little2", 67],
    ["J_Bip_L_Little3", 68],
    ["J_Bip_L_LowerArm", 10],
    ["J_Bip_L_LowerLeg", 3],
    ["J_Bip_L_Middle1", 58],
    ["J_Bip_L_Middle2", 59],
    ["J_Bip_L_Middle3", 60],
    ["J_Bip_L_Ring1", 62],
    ["J_Bip_L_Ring2", 63],
    ["J_Bip_L_Ring3", 64],
    ["J_Bip_L_Shoulder", 18],
    ["J_Bip_L_Thumb1", 50],
    ["J_Bip_L_Thumb2", 51],
    ["J_Bip_L_Thumb3", 52],
    ["J_Bip_L_ToeBase", 16],
    ["J_Bip_L_UpperArm", 9],
    ["J_Bip_L_UpperLeg", 2],
    ["J_Bip_R_Foot", 7],
    ["J_Bip_R_Hand", 14],
    ["J_Bip_R_Index1", 78],
    ["J_Bip_R_Index2", 79],
    ["J_Bip_R_Index3", 80],
    ["J_Bip_R_Little1", 90],
    ["J_Bip_R_Little2", 91],
    ["J_Bip_R_Little3", 92],
    ["J_Bip_R_LowerArm", 13],
    ["J_Bip_R_LowerLeg", 6],
    ["J_Bip_R_Middle1", 82],
    ["J_Bip_R_Middle2", 83],
    ["J_Bip_R_Middle3", 84],
    ["J_Bip_R_Ring1", 86],
    ["J_Bip_R_Ring2", 87],
    ["J_Bip_R_Ring3", 88],
    ["J_Bip_R_Shoulder", 19],
    ["J_Bip_R_Thumb1", 74],
    ["J_Bip_R_Thumb2", 75],
    ["J_Bip_R_Thumb3", 76],
    ["J_Bip_R_ToeBase", 17],
    ["J_Bip_R_UpperArm", 12],
    ["J_Bip_R_UpperLeg", 5],
    ["Root", 0]
]

AS_TABLE = OrderedDict([
    ('FitSkeleton|Root', 'J_Bip_C_Hips'),
    ('Spine1', 'J_Bip_C_Spine'),
    ('Spine2', 'J_Bip_C_Chest'),
    ('Chest', 'J_Bip_C_UpperChest'),
    ('Neck', 'J_Bip_C_Neck'),
    ('Head', 'J_Bip_C_Head'),
    ('Eye', 'J_Adj_R_FaceEye'),
    ('Hip', 'J_Bip_R_UpperLeg'),
    ('Knee', 'J_Bip_R_LowerLeg'),
    ('Ankle', 'J_Bip_R_Foot'),
    ('Toes', 'J_Bip_R_ToeBase'),
    ('Scapula', 'J_Bip_R_Shoulder'),
    ('Shoulder', 'J_Bip_R_UpperArm'),
    ('Elbow', 'J_Bip_R_LowerArm'),
    ('Wrist', 'J_Bip_R_Hand'),
    ('MiddleFinger1', 'J_Bip_R_Middle1'),
    ('MiddleFinger2', 'J_Bip_R_Middle2'),
    ('MiddleFinger3', 'J_Bip_R_Middle3'),
    ('MiddleFinger4', 'J_Bip_R_Middle3_end'),
    ('ThumbFinger1', 'J_Bip_R_Thumb1'),
    ('ThumbFinger2', 'J_Bip_R_Thumb2'),
    ('ThumbFinger3', 'J_Bip_R_Thumb3'),
    ('IndexFinger1', 'J_Bip_R_Index1'),
    ('IndexFinger2', 'J_Bip_R_Index2'),
    ('IndexFinger3', 'J_Bip_R_Index3'),
    ('IndexFinger4', 'J_Bip_R_Index3_end'),
    ('RingFinger1', 'J_Bip_R_Ring1'),
    ('RingFinger2', 'J_Bip_R_Ring2'),
    ('RingFinger3', 'J_Bip_R_Ring3'),
    ('RingFinger4', 'J_Bip_R_Ring3_end'),
    ('PinkyFinger1', 'J_Bip_R_Little1'),
    ('PinkyFinger2', 'J_Bip_R_Little2'),
    ('PinkyFinger3', 'J_Bip_R_Little3'),
    ('PinkyFinger4', 'J_Bip_R_Little3_end')
])

FACIAL_BLENDSHAPE = 'facial_bs'
FACIAL_CONTROLLER_FILE = r"C:\GoogleDrive\programs_env\maya\modules\ironRig\controllers\ARKit_controller.ma"
# --------------------------------------------------------------------------------------


# ------------------------------ Model ----------------------------------------
def cleanup(fbxFile, textureDirectory, name, height, flipZ=True):
    mel.eval('FBXImport -f "{0}"'.format(fbxFile.replace('\\', '/')))

    cleanupModel(height, flipZ)
    cleanupOutliner()
    cleanupMaterial(textureDirectory, name)

    cmds.delete(UNUSING_NODES)

    # Delete locators
    locators = []
    for locator in cmds.ls(type='locator', long=True) or []:
        parent = cmds.listRelatives(locator, parent=True, fullPath=True)
        if parent:
            locators.append(parent[0])
    if locators:
        cmds.delete(locators)

    # Delete unnecessary blendshape targets
    blend_targets = cmds.ls('_*', type='transform', long=True) or []
    if blend_targets:
        cmds.delete(blend_targets)


def cleanupModel(height, flipZ):
    yRotate = 0
    if flipZ:
        yRotate = 180

    correctJointName()

    # Make character facing positive z-axis
    skelTopNode = UNUSING_NODES[2]
    cmds.setAttr('{}.rotateY'.format(skelTopNode), yRotate)

    # Modify height
    meshes = meshUtil.getDeformedMeshes()
    curHeight = getHeight(meshes)
    ratio = height / curHeight * cmds.getAttr('{}.scaleY'.format(skelTopNode))
    cmds.setAttr('{}.scale'.format(skelTopNode), ratio, ratio, ratio)

    # Rotate arm joints slightly for the IK
    try:
        cmds.setAttr('J_Bip_R_LowerArm.rz', 1)
        cmds.setAttr('J_Bip_L_LowerArm.rz', -1)
    except:
        cmds.setAttr('J_Bip_LowerArm_R.rz', 1)
        cmds.setAttr('J_Bip_LowerArm_L.rz', -1)

    # Save skin weights
    docDir = os.path.expanduser('~')
    skinFiles = []
    for mesh in meshes:
        skinFile = skinUtil.exportSkin(mesh, docDir)
        skinFiles.append(skinFile)
        cmds.polySoftEdge(mesh, a=180)
        meshUtil.cleanupMesh(mesh)

    # Cleanup skeleton
    cmds.makeIdentity(skelTopNode, apply=True, scale=True)
    root = 'Root'
    cmds.parent(root, world=True)
    rootChild = cmds.listRelatives(root, children=True, fullPath=True) or []
    # Rotate the root joint for the unreal engine
    if rootChild:
        cmds.parent(rootChild, world=True)
    cmds.setAttr('{}.rotate'.format(root), 0, 0, 0)
    cmds.setAttr('{}.jointOrient'.format(root), -90, 0, 0)
    if rootChild:
        cmds.parent(rootChild, root)

    # Freeze joints
    cmds.makeIdentity(root, apply=True)
    for jnt in cmds.ls(type='joint', long=True) or []:
        cmds.setAttr('{}.radius'.format(jnt), 1.0)


    # Restore blendshape
    facialTargets = cmds.ls('Fcl_*', type='transform', long=True) or []
    if cmds.objExists(ARKIT_TARGETS[0]):
        facialTargets += ARKIT_TARGETS
    nullGrp = cmds.createNode('transform', name='null1')
    if facialTargets:
        cmds.parent(facialTargets, nullGrp)
    cmds.setAttr('{}.scale'.format(nullGrp), ratio, ratio, ratio)
    cmds.setAttr('{}.rotate'.format(nullGrp), -90, yRotate, 0)
    cmds.makeIdentity(nullGrp, apply=True)
    cmds.blendShape(facialTargets, MESHES[0], name=FACIAL_BLENDSHAPE)

    # Restore skin weights
    for skinFile in skinFiles:
        skinUtil.importSkin(skinFile)
        os.remove(skinFile)


def correctJointName():
    # Replace fbx ascii name in the joints
    for jnt in cmds.ls(type='joint', long=True) or []:
        newName = jnt.replace('FBXASC046', '_')
        newName = newName.replace('FBXASC044', '_')
        suffix = newName.rsplit('_', 1)[-1]
        if suffix in ['L', 'R']:
            splitNames = newName.split('_')
            newName = '{}_{}_{}'.format('_'.join(splitNames[:2]), suffix, '_'.join(splitNames[2:-1]))
        cmds.rename(jnt, newName)


def getHeight(meshes):
    height = 0.0
    for mesh in meshes:
        bbox = cmds.exactWorldBoundingBox(mesh)
        if bbox:
            curHeight = bbox[4]
        else:
            curHeight = 0.0
        if curHeight > height:
            height = curHeight
    return height


def cleanupOutliner():
    allGrp = cmds.createNode('transform', name='all')
    tmpGrp = cmds.createNode('transform', name='temp_grp')
    mdlGrp = cmds.createNode('transform', name='model')
    geoGrp = cmds.createNode('transform', name='geo_grp')
    skelGrp = cmds.createNode('transform', name='skeleton')
    rigGrp = cmds.createNode('transform', name='rig')
    vroidTargetsGrp = cmds.createNode('transform', name='vroid_targets_grp')
    vroid_targets = cmds.ls('Fcl_*', type='transform', long=True) or []
    if vroid_targets:
        cmds.parent(vroid_targets, vroidTargetsGrp)

    meshes = meshUtil.getDeformedMeshes()
    if meshes:
        cmds.parent(meshes, geoGrp)
    if cmds.objExists('Root'):
        cmds.parent('Root', skelGrp)
    cmds.parent(geoGrp, mdlGrp)
    cmds.parent([mdlGrp, skelGrp, rigGrp], allGrp)
    cmds.parent(vroidTargetsGrp, tmpGrp)

    if cmds.objExists(ARKIT_TARGETS[0]):
        arkitTargetsGrp = cmds.createNode('transform', name='arkit_targets_grp')
        cmds.parent(ARKIT_TARGETS, arkitTargetsGrp)
        cmds.parent(arkitTargetsGrp, tmpGrp)

def cleanupMaterial(textureDirectory, name):
    # Add prefix for textures
    # Some textures starts with invalid character are can not imported in unreal
    textures = [f for f in os.listdir(textureDirectory) if f.endswith('png')]
    for tex in textures:
        if name in tex:
            continue
        oldTexPath = os.path.join(textureDirectory, tex)
        newTexPath = os.path.join(textureDirectory, '{}{}'.format(name, tex))
        os.rename(oldTexPath, newTexPath)

    meshes = meshUtil.getDeformedMeshes()
    materials = []
    for mesh in meshes:
        materials.extend(matUtil.getMaterials(mesh))

    for mat in materials:
        mat_name = mat
        if isinstance(mat, str):
            mat_name = mat
        else:
            try:
                mat_name = mat.name()
            except AttributeError:
                mat_name = mat

        result = re.search(r'N.+?_(\D+.+?)FBX.+', mat_name)

        if result:
            mat_node = mat_name
            if hasattr(mat, 'specularColor'):
                try:
                    mat.specularColor.set(0, 0, 0)
                    mat.reflectedColor.set(0, 0, 0)
                except Exception:
                    pass

            new_mat_name = '{}_{}_MI'.format(name, result.group(1))
            if mat_node != new_mat_name:
                cmds.rename(mat_node, new_mat_name)
            mat_node = new_mat_name

            try:
                rawTexName = MAT_INFO[result.group(1)]
            except KeyError:
                continue

            tex = '{}{}'.format(name, rawTexName)

            fileNode = cmds.shadingNode('file', asTexture=True, name='{}_file'.format(tex))
            place2dNode = cmds.shadingNode('place2dTexture', asUtility=True, name='{}_place2dTexture'.format(tex))

            attrs = [
                ('coverage', 'coverage'),
                ('mirrorU', 'mirrorU'),
                ('mirrorV', 'mirrorV'),
                ('noiseUV', 'noiseUV'),
                ('offset', 'offset'),
                ('outUV', 'uvCoord'),
                ('outUvFilterSize', 'uvFilterSize'),
                ('repeatUV', 'repeatUV'),
                ('rotateFrame', 'rotateFrame'),
                ('rotateUV', 'rotateUV'),
                ('stagger', 'stagger'),
                ('translateFrame', 'translateFrame'),
                ('vertexCameraOne', 'vertexCameraOne'),
                ('vertexUvOne', 'vertexUvOne'),
                ('vertexUvThree', 'vertexUvThree'),
                ('vertexUvTwo', 'vertexUvTwo'),
                ('wrapU', 'wrapU'),
                ('wrapV', 'wrapV'),
            ]
            for src, dst in attrs:
                cmds.connectAttr('{}.{}'.format(place2dNode, src), '{}.{}'.format(fileNode, dst), force=True)

            cmds.setAttr('{}.fileTextureName'.format(fileNode), os.path.join(textureDirectory, tex), type='string')
            cmds.connectAttr('{}.outColor'.format(fileNode), '{}.color'.format(mat_node), force=True)
            cmds.connectAttr('{}.outTransparency'.format(fileNode), '{}.transparency'.format(mat_node), force=True)

    # Set transparency algorithm to the "Alpha Cut" of the viewport 2.0
    cmds.setAttr("hardwareRenderingGlobals.transparencyAlgorithm", 5)
# --------------------------------------------------------------------------------------


# --------------------------------- Rig ------------------------------------------------
# Body #
def setupHumanIK():
    rig_name = "VRoid"

    mel.eval('hikCreateCharacter("{0}")'.format(rig_name))
    mel.eval('hikUpdateCharacterList()')
    mel.eval('hikSelectDefinitionTab()')

    model_root = "Root"
    cmds.select(model_root)

    for joint_setting in HIK_MAPPINGS:
        mel_command = 'setCharacterObject("{0}","{1}", {2}, 0);'.format(joint_setting[0], rig_name, joint_setting[1])
        mel.eval(mel_command)
    # mel.eval("hikCreateControlRig;")


def matchFitSkeleton():
    for asJnt, vrJnt in AS_TABLE.items():
        cmds.matchTransform(asJnt, vrJnt, pos=True)


# Facial #
def setupFacial():
    cmds.file(FACIAL_CONTROLLER_FILE, i=True)
    setupVRFacialAttrs()
    bsUtil.connectExistingTargets('facial_attrs_out', [FACIAL_BLENDSHAPE])
    setupEyelidSDK()


def setupVRFacialAttrs():
    for part, targets in VR_TARGETS_INFO.items():
        cmds.addAttr('facial_global_ctrl', longName=part, attributeType='enum', enumName='---------------:')
        cmds.setAttr('facial_global_ctrl.{}'.format(part), channelBox=True)
        for target in targets:
            cmds.addAttr('facial_global_ctrl', longName=target, attributeType='float', min=0, max=1, keyable=True)
            cmds.addAttr('facial_attrs_out', longName=target, attributeType='float', min=0, max=1, keyable=True)
            cmds.connectAttr('facial_global_ctrl.{}'.format(target), 'facial_attrs_out.{}'.format(target), force=True)


def setupEyelidSDK():
    # Left eyelid SDK
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookUpLeft', value=0, driver='Eye_L.rotateZ', driverValue=0)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookUpLeft', value=1, driver='Eye_L.rotateZ', driverValue=-11)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookDownLeft', value=0, driver='Eye_L.rotateZ', driverValue=0)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookDownLeft', value=1, driver='Eye_L.rotateZ', driverValue=11)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookInLeft', value=0, driver='Eye_L.rotateY', driverValue=0)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookInLeft', value=1, driver='Eye_L.rotateY', driverValue=12)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookOutLeft', value=0, driver='Eye_L.rotateY', driverValue=0)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookOutLeft', value=1, driver='Eye_L.rotateY', driverValue=-12)

    # Right eyelid SDK
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookUpRight', value=0, driver='Eye_R.rotateZ', driverValue=0)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookUpRight', value=1, driver='Eye_R.rotateZ', driverValue=-11)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookDownRight', value=0, driver='Eye_R.rotateZ', driverValue=0)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookDownRight', value=1, driver='Eye_R.rotateZ', driverValue=11)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookInRight', value=0, driver='Eye_R.rotateY', driverValue=0)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookInRight', value=1, driver='Eye_R.rotateY', driverValue=-12)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookOutRight', value=0, driver='Eye_R.rotateY', driverValue=0)
    cmds.setDrivenKeyframe('facial_attrs_out.eyeLookOutRight', value=1, driver='Eye_R.rotateY', driverValue=12)
# --------------------------------------------------------------------------------------