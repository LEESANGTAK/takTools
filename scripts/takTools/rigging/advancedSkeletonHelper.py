from collections import OrderedDict
import pymel.core as pm
import maya.cmds as cmds

class AdvancedSkeletonHelper(object):
    # Static Class Attributes
    FIT_SKELETON_PARENT_NAME = 'FitSkeleton'
    MODEL_POSE_LOC_GRP_NAME = 'modelPose_loc_grp'
    RIG_POSE_LOC_GRP_NAME = 'rigPose_loc_grp'
    MODEL_POSE_LOC_SUFFIX = '_modelPose_loc'
    RIG_POSE_LOC_SUFFIX = '_rigPose_loc'
    CONTROL_SET_NAME = 'ControlSet'
    FK_CONTROL_GROUP_NAME = 'FKSystem'
    IK_CONTROL_GROUP_NAME = 'IKSystem'
    BASE_MODULE_GROUPS_NAME = ['All', 'Model', 'Rig', 'Modules']
    RIG_GROUP_NAME = 'Group'
    MASTER_SET_NAME = 'Sets'

    VROID_SKELETON_MAPPING = OrderedDict([
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

    UNREAL_SKELETON_MAPPING = OrderedDict([
        ('FitSkeleton|Root', 'pelvis'),
        ('Spine1', 'spine_01'),
        ('Spine2', 'spine_02'),
        ('Chest', 'spine_03'),
        ('Neck', 'neck_01'),
        ('Head', 'head'),
        ('Eye', 'eye_r'),
        ('Hip', 'thigh_r'),
        ('Knee', 'calf_r'),
        ('Ankle', 'foot_r'),
        ('Toes', 'ball_r'),
        ('Scapula', 'clavicle_r'),
        ('Shoulder', 'upperarm_r'),
        ('Elbow', 'lowerarm_r'),
        ('Wrist', 'hand_r'),
        ('MiddleFinger1', 'middle_01_r'),
        ('MiddleFinger2', 'middle_02_r'),
        ('MiddleFinger3', 'middle_03_r'),
        ('MiddleFinger4', 'middle_ed_r'),
        ('ThumbFinger1', 'thumb_01_r'),
        ('ThumbFinger2', 'thumb_02_r'),
        ('ThumbFinger3', 'thumb_03_r'),
        ('ThumbFinger4', 'thumb_ed_r'),
        ('IndexFinger1', 'index_01_r'),
        ('IndexFinger2', 'index_02_r'),
        ('IndexFinger3', 'index_03_r'),
        ('IndexFinger4', 'index_ed_r'),
        ('RingFinger1', 'ring_01_r'),
        ('RingFinger2', 'ring_02_r'),
        ('RingFinger3', 'ring_03_r'),
        ('RingFinger4', 'ring_ed_r'),
        ('PinkyFinger1', 'pinky_01_r'),
        ('PinkyFinger2', 'pinky_02_r'),
        ('PinkyFinger3', 'pinky_03_r'),
        ('PinkyFinger4', 'pinky_ed_r')
    ])

    HIK_SKELETON_MAPPING = {
        'Root':0,
        'Pelvis_M':1,
        'Spine1_M':8,
        'Spine2_M':23,
        'Chest_M':24,
        'Neck_M':20,
        'Head_M':15,
        'Scapula_L':18,
        'Scapula_R':19,
        'Shoulder_L':9,
        'Shoulder_R':12,
        'Elbow_L':10,
        'Elbow_R':13,
        'Wrist_L':11,
        'Wrist_R':14,
        'Hip_L':2,
        'Hip_R':5,
        'Knee_L':3,
        'Knee_R':6,
        'Ankle_L':4,
        'Ankle_R':7,
        'Toes_L':16,
        'Toes_R':17,
        'ThumbFinger1_L': 50,
        'ThumbFinger2_L': 51,
        'ThumbFinger3_L': 52,
        'IndexFinger1_L': 54,
        'IndexFinger2_L': 55,
        'IndexFinger3_L': 56,
        'MiddleFinger1_L': 58,
        'MiddleFinger2_L': 59,
        'MiddleFinger3_L': 60,
        'RingFinger1_L': 62,
        'RingFinger2_L': 63,
        'RingFinger3_L': 64,
        'PinkyFinger1_L': 66,
        'PinkyFinger2_L': 67,
        'PinkyFinger3_L': 68,
        'ThumbFinger1_R': 74,
        'ThumbFinger2_R': 75,
        'ThumbFinger3_R': 76,
        'IndexFinger1_R': 78,
        'IndexFinger2_R': 79,
        'IndexFinger3_R': 80,
        'MiddleFinger1_R': 82,
        'MiddleFinger2_R': 83,
        'MiddleFinger3_R': 84,
        'RingFinger1_R': 86,
        'RingFinger2_R': 87,
        'RingFinger3_R': 88,
        'PinkyFinger1_R': 90,
        'PinkyFinger2_R': 91,
        'PinkyFinger3_R': 92,
    }

    HIK_CONTROL_MAPPING = {
        'RootX_M': [1, ('T', 'R')],
        'FKSpine1_M': [8, ('R')],
        'FKSpine2_M': [23, ('R')],
        'FKChest_M': [1000, ('R')],
        'FKNeck_M': [20, ('R')],
        'FKHead_M': [15, ('R')],
        'FKScapula_L': [18, ('R')],
        'FKScapula_R': [19, ('R')],
        'FKShoulder_L': [9, ('R')],
        'FKShoulder_R': [12, ('R')],
        'FKElbow_L': [10, ('R')],
        'FKElbow_R': [13, ('R')],
        'FKWrist_L': [11, ('R')],
        'FKWrist_R': [14, ('R')],
        # 'PoleLeg_L': [3, 'T'],
        # 'PoleLeg_R': [6, 'T'],
        'IKLeg_L': [4, ('T', 'R')],
        'IKLeg_R': [7, ('T', 'R')],
        # 'IKToes_L': [16, ('R')],
        # 'IKToes_R': [17, ('R')],
    }

    HIK_NODE_TYPES = [
        'HIKSolverNode',
        'HIKRetargeterNode',
        'HIKCharacterNode',
        'HIKSkeletonGeneratorNode',
        'HIKControlSetNode',
        'HIKEffectorFromCharacter',
        'HIKSK2State',
        'HIKFK2State',
        'HIKState2FK',
        'HIKState2SK',
        'HIKState2GlobalSK',
        'HIKEffector2State',
        'HIKState2Effector',
        'HIKProperty2State',
        'HIKPinning2State',
        'ComputeGlobal',
        'ComputeLocal',
        'HIKCharacterStateClient',
        'CustomRigDefaultMappingNode',
        'CustomRigRetargeterNode'
    ]

    TWIST_JOINTS_INFO = {
        'Shoulder_L': ['ShoulderPart2_L', 'Elbow_L'],
        'Shoulder_R': ['ShoulderPart2_R', 'Elbow_R'],
        'Elbow_L': ['ElbowPart2_L', 'Wrist_L'],
        'Elbow_R': ['ElbowPart2_R', 'Wrist_R'],
        'Hip_L': ['HipPart2_L', 'Knee_L'],
        'Hip_R': ['HipPart2_R', 'Knee_R'],
        'Knee_L': ['KneePart2_L', 'Ankle_L'],
        'Knee_R': ['KneePart2_R', 'Ankle_R']
    }

    IK_JOINTS_INFO = {
        'Root': 'ik_foot_Root',
        'Ankle_L': 'ik_foot_L',
        'Ankle_R': 'ik_foot_R',
        'Chest_M': 'ik_hand_Root',
        'Wrist_R': 'ik_hand_R',
        'Wrist_L': 'ik_hand_L'
    }

    def __init__(self):
        super(AdvancedSkeletonHelper, self).__init__()

        # Input Attributes
        self.fitJoints = self.__getFitJoints()

        # Output Attributes

        # Private Attributes
        self.__modelPoseLocs = []
        self.__rigPoseLocs = []

    def createModelPoseLocs(self):
        pm.undoInfo(openChunk=True)
        if pm.objExists(self.MODEL_POSE_LOC_GRP_NAME):
            pm.delete(self.MODEL_POSE_LOC_GRP_NAME)

        pm.createNode('transform', n=self.MODEL_POSE_LOC_GRP_NAME)

        for jnt in self.fitJoints:
            if not pm.objExists(jnt):
                continue
            if '4' in jnt.name() or 'End' in jnt.name() or 'Heel' in jnt.name():
                continue
            modelPoseLoc = pm.spaceLocator(n='{0}{1}'.format(jnt.name(), self.MODEL_POSE_LOC_SUFFIX))
            pm.matchTransform(modelPoseLoc, jnt, pos=True, rot=True)
            pm.parent(modelPoseLoc, self.MODEL_POSE_LOC_GRP_NAME)
            self.__modelPoseLocs.append(modelPoseLoc)
        pm.undoInfo(closeChunk=True)

    def createRigPoseLocs(self):
        pm.undoInfo(openChunk=True)
        if pm.objExists(self.RIG_POSE_LOC_GRP_NAME):
            pm.delete(self.RIG_POSE_LOC_GRP_NAME)

        pm.createNode('transform', n=self.RIG_POSE_LOC_GRP_NAME)

        for jnt in self.fitJoints:
            if '4' in jnt.name() or 'End' in jnt.name() or 'Heel' in jnt.name():
                continue
            rigPoseLoc = pm.spaceLocator(n='{0}{1}'.format(jnt.name(), self.RIG_POSE_LOC_SUFFIX))
            pm.matchTransform(rigPoseLoc, jnt, pos=True, rot=True)
            pm.parent(rigPoseLoc, self.RIG_POSE_LOC_GRP_NAME)
            self.__rigPoseLocs.append(rigPoseLoc)
        pm.undoInfo(closeChunk=True)

    def goToRigPoseFit(self):
        rigPoseLocs = self.__getRigPoseLocs()
        for rigPoseLoc in rigPoseLocs:
            jnt = rigPoseLoc.replace(self.RIG_POSE_LOC_SUFFIX, '')
            pm.matchTransform(jnt, rigPoseLoc, pos=True, rot=True)

    def goToModelPoseFit(self):
        modelPoseLocs = self.__getModelPoseLocs()
        for modelPoseLoc in modelPoseLocs:
            jnt = modelPoseLoc.replace(self.MODEL_POSE_LOC_SUFFIX, '')
            pm.matchTransform(jnt, modelPoseLoc, pos=True, rot=True)

    def matchControlToModelPose(self):
        modelPoseLocs = self.__getModelPoseLocs()
        for modelPoseLoc in modelPoseLocs:
            baseName = modelPoseLoc.replace(self.MODEL_POSE_LOC_SUFFIX, '')
            ctrlName = 'FK{0}_R'.format(baseName)
            if not pm.objExists(ctrlName):
                ctrlName = 'FK{0}_M'.format(baseName)
            if pm.objExists(ctrlName):
                pm.matchTransform(ctrlName, modelPoseLoc, pos=True, rot=True)
        mirrorRightToLeft()

    def matchControlToRigPose(self):
        rigPoseLocs = self.__getRigPoseLocs()
        for rigPoseLoc in rigPoseLocs:
            baseName = rigPoseLoc.replace(self.RIG_POSE_LOC_SUFFIX, '')
            ctrlName = 'FK{0}_R'.format(baseName)
            if not pm.objExists(ctrlName):
                ctrlName = 'FK{0}_M'.format(baseName)
            if pm.objExists(ctrlName):
                pm.matchTransform(ctrlName, rigPoseLoc, pos=True, rot=True)
        mirrorRightToLeft()

    def createZeroGroup(self):
        allCtrls = self.__getAllControls()
        for ctrl in allCtrls:
            zeroGrp = pm.createNode('transform', n='{0}_zero'.format(ctrl.name()))
            pm.matchTransform(zeroGrp, ctrl, pos=True, rot=True)
            ctrl.getParent() | zeroGrp
            zeroGrp | ctrl

    def removeZeroGroup(self):
        allCtrls = self.__getAllControls()
        for ctrl in allCtrls:
            zeroGrpName = '{0}_zero'.format(ctrl.name())
            if pm.objExists(zeroGrpName):
                zeroGrp = pm.PyNode(zeroGrpName)
                zeroGrp.getParent() | ctrl
                pm.delete(zeroGrp)

    def setupBase(self):
        radius = pm.pointPosition('Main.ep[6]').x * 1.2
        globalCtrl = pm.circle(n='Global', ch=False, normal=[0, 1, 0], r=radius)[0]
        globalCtrlShape = globalCtrl.getShape()
        globalCtrlShape.overrideEnabled.set(True)
        globalCtrlShape.overrideColor.set(17)
        globalCtrlZero = pm.group(n='Global_zero')
        mainCtrl = pm.PyNode('Main')

        pm.parentConstraint(globalCtrl, mainCtrl.getParent(), mo=True)
        globalCtrl.scale >> mainCtrl.scale
        mainCtrl.sx.setKeyable(False)
        mainCtrl.sy.setKeyable(False)
        mainCtrl.sz.setKeyable(False)

        pm.parent(globalCtrlZero, 'rig')

    def renameRootToPelvis(self):
        fitRoot = pm.PyNode('Root')
        skinRoot = pm.PyNode('Root_M')

        fitRoot.rename('Pelvis')
        skinRoot.rename('Pelvis_M')

    def breakTwistChain(self):
        for parentJoint, childJoints in AdvancedSkeletonHelper.TWIST_JOINTS_INFO.items():
            for childJnt in childJoints:
                if pm.objExists(childJnt):
                    pm.parent(childJnt, parentJoint)

    def createBaseJoints(self):
        rootJnt = pm.createNode('joint', n='Root')
        rootJnt.jointOrientX.set(-90)

        pm.parent(rootJnt, 'DeformationSystem')
        pm.parent('Pelvis_M', rootJnt)
        pm.setAttr('Pelvis_M.segmentScaleCompensate', False)

    def createBaseControls(self):
        if not pm.objExists('Root_ctrl'):
            rootCtrl = pm.circle(n='Root_ctrl', ch=False, normal=(0, 1, 0), r=30)[0]
            rootZero = pm.group(rootCtrl, n=rootCtrl + '_zero')
            pm.parentConstraint(rootCtrl, 'Root')
            pm.parent(rootZero, 'MotionSystem')

        if not pm.objExists('Global'):
            globalCtrl = pm.circle(n='Global', ch=False, normal=(0, 1, 0), r=25)[0]
            globalZero = pm.group(globalCtrl, n=globalCtrl + '_zero')
            pm.parent(globalZero, 'MainSystem')
            pm.parent('Main', globalCtrl)

        skelGrp = pm.PyNode('DeformationSystem')
        skelGrp.inheritsTransform.set(False)
        skelGrp.inheritsTransform.lock()
        channels = ['translate', 'rotate', 'scale']
        axes = ['X', 'Y', 'Z']
        for channel in channels:
            for axis in axes:
                skelGrp.attr(channel+axis).lock()
                skelGrp.attr(channel+axis).setKeyable(False)

        pm.parentConstraint('Root_ctrl', 'Root', mo=True)
        pm.scaleConstraint('Main', 'Root', mo=True)

    def createHikNodeSet(self):
        hikNodes = self.__getHikNodes()
        hikNodesSet = pm.sets(hikNodes, n='HikNodes')
        pm.sets(self.MASTER_SET_NAME, addElement=hikNodesSet)

    @classmethod
    def createHikCharDef(cls, charName):
        if pm.objExists(charName):
            pm.error('{0} is already exists.'.format(charName))

        pm.mel.eval('hikCreateCharacter( "{0}" );'.format(charName))

        for jnt, id in cls.HIK_SKELETON_MAPPING.items():
            if not pm.objExists(jnt):
                continue
            pm.mel.eval('setCharacterObject("{0}", "{1}", {2}, 0);'.format(jnt, charName, id))

    @classmethod
    def createHikCustomRig(cls, charName):
        pm.mel.eval('hikCreateCustomRig( "{0}" );'.format(charName))

        for ctrl, info in cls.HIK_CONTROL_MAPPING.items():
            id = info[0]
            connectTypes = info[1]

            pm.select(ctrl, r=True)
            pm.mel.eval('hikCustomRigAssignEffector {0};'.format(id))

            # Set translate, rotate connections
            customRigMappingNodes = pm.listConnections('{0}.message'.format(ctrl), s=False, type='CustomRigDefaultMappingNode')
            if len(customRigMappingNodes) == 2:
                for customRigMappingNode in customRigMappingNodes:
                    connectType = customRigMappingNode.attr('type').get()
                    connectType = 'T' if connectType == 0 else 'R'
                    if not connectType in connectTypes:
                        pm.delete(customRigMappingNode)
            elif len(customRigMappingNodes) == 1 and len(connectTypes) == 1:
                customRigMappingNodes[0].attr('type').set(connectTypes[0])

    @classmethod
    def cleanupOutliner(cls):
        poseLocGrpName = 'pose_loc_grp'

        hierarchyInfo = {
            'all': ['model', 'rig'],
            'rig': cls.RIG_GROUP_NAME,
            'Main': 'modules',
            'modules': poseLocGrpName,
            poseLocGrpName: [cls.RIG_POSE_LOC_GRP_NAME, cls.MODEL_POSE_LOC_GRP_NAME]
        }

        if not cmds.objExists(poseLocGrpName):
            cmds.group(n=poseLocGrpName, empty=True)

        for grpName in cls.BASE_MODULE_GROUPS_NAME:
            if not cmds.objExists(grpName):
                cmds.group(n=grpName, empty=True)

        for parent, child in hierarchyInfo.items():
            try:
                cmds.parent(child, parent)
            except:
                pass

        cls.connectSetToGroup()

    @classmethod
    def createIKJoints(cls):
        for srcJnt, ikJntName in cls.IK_JOINTS_INFO.items():
            ikJnt = pm.duplicate(srcJnt, po=True, n=ikJntName)
            pm.parentConstraint(srcJnt, ikJnt, mo=False)
            pm.parent(ikJnt, 'Root')
        ikGunJnt = pm.duplicate('Wrist_R', po=True, n='ik_hand_Gun')
        pm.parentConstraint('Wrist_R', ikGunJnt, mo=False)

        pm.parent('ik_foot_L', 'ik_foot_R', 'ik_foot_Root')
        pm.parent('ik_hand_Gun', 'ik_hand_Root')
        pm.parent('ik_hand_R', 'ik_hand_L', 'ik_hand_Gun')

    @classmethod
    def removeSelsFromAsSystem(cls):
        for sel in cmds.ls(sl=True):
            cmds.sets(sel, rm = 'ControlSet')
            cmds.sets(sel, rm = 'AllSet')
            cmds.sets(sel, rm = 'DeformSet')
            cmds.sets(sel, rm = 'Sets')

            cmds.editDisplayLayerMembers('defaultLayer', sel)

    @classmethod
    def matchFitSkeleton(cls):
        if pm.objExists('pelvis'):
            skelMapping = cls.UNREAL_SKELETON_MAPPING
        elif pm.objExists('J_Bip_C_Hips'):
            skelMapping = cls.VROID_SKELETON_MAPPING

        for asJnt, skJnt in skelMapping.items():
            pm.matchTransform(asJnt, skJnt, pos=True)

    @classmethod
    def alignAnkleOriToWorld(cls):
        loc = cmds.spaceLocator(n = 'ankleAlign_loc')
        cmds.delete(cmds.parentConstraint('Ankle', loc, mo = False))
        cmds.xform(loc, ro = [-90, 0, -90], ws = True)
        cmds.delete(cmds.orientConstraint(loc, 'Ankle', mo = False, skip = 'x'))
        cmds.delete(loc)

    @classmethod
    def connectSetToGroup(cls):
        rigGrp = pm.PyNode(cls.RIG_GROUP_NAME)
        masterSet = pm.PyNode(cls.MASTER_SET_NAME)
        pm.addAttr(rigGrp, ln='advancedSet', at='message', keyable=False)
        masterSet.message >> rigGrp.advancedSet

    @classmethod
    def __getHikNodes(cls):
        hikNodes = []
        for hikNodeType in cls.HIK_NODE_TYPES:
            hikNodes.extend(pm.ls(type=hikNodeType))
        return hikNodes

    def __getFitJoints(self):
        fitSkeletonParent = pm.PyNode(self.FIT_SKELETON_PARENT_NAME)
        fitJoints = fitSkeletonParent.getChildren(ad=True, type='joint')
        fitJoints.reverse()  # getChildren command returns ordered from end of hierarchy
        return fitJoints

    def __getModelPoseLocs(self):
        if self.__modelPoseLocs:
            return self.__modelPoseLocs
        else:
            for jnt in self.fitJoints:
                modelPoseLocName = '{0}{1}'.format(jnt.name(), self.MODEL_POSE_LOC_SUFFIX)
                if pm.objExists(modelPoseLocName):
                    self.__modelPoseLocs.append(pm.PyNode(modelPoseLocName))
            return self.__modelPoseLocs

    def __getRigPoseLocs(self):
        if self.__rigPoseLocs:
            return self.__rigPoseLocs
        else:
            for jnt in self.fitJoints:
                rigPoseLocName = '{0}{1}'.format(jnt.name(), self.RIG_POSE_LOC_SUFFIX)
                if pm.objExists(rigPoseLocName):
                    self.__rigPoseLocs.append(pm.PyNode(rigPoseLocName))
            return self.__rigPoseLocs

    def __getAllControls(self):
        allCtrls = []

        fkCtrlGrp = pm.PyNode(self.FK_CONTROL_GROUP_NAME)
        ikCtrlGrp = pm.PyNode(self.IK_CONTROL_GROUP_NAME)

        fkCtrls = [ctrl.getParent() for ctrl in fkCtrlGrp.getChildren(ad=True, type='nurbsCurve')]
        ikCtrls = [ctrl.getParent() for ctrl in ikCtrlGrp.getChildren(ad=True, type='nurbsCurve')]
        allCtrls.extend(fkCtrls)
        allCtrls.extend(ikCtrls)

        return list(set(allCtrls))


def mirrorRightToLeft():
    selectorMelCmd = '''
        source "C:/GoogleDrive/programs_env/maya/modules/AdvancedSkeleton5/AdvancedSkeleton5Files/Selector/biped.mel";
        asSelectorbiped;
        asAlignFK2IK "biped" {"FKIKArm_R"};
        asAlignFK2IK "biped" {"FKIKArm_R"};
        asAlignFK2IK "biped" {"FKIKLeg_R"};
        asAlignFK2IK "biped" {"FKIKLeg_R"};
        asMirror asSelectorbiped;
    '''
    pm.mel.eval(selectorMelCmd)


def setInverseXMovement(ikController):
    """
    ikCtrl = 'IKLeg_R'
    utils.setInverseXMovement(ikCtrl)
    """
    ikCtrl = pm.PyNode(ikController)
    ikCtrlChilds = ikCtrl.getChildren(type='transform')
    pm.parent(ikCtrlChilds, w=True)

    pm.setAttr('{}.sx'.format(ikCtrl.replace('IK', 'IKOffset')), -1)

    pm.parent(ikCtrlChilds, ikCtrl)


def setupFollowAttr(driverTransform, controller):
    """
    driver = 'FKHipBase_R'
    ctrl = 'IKLeg_R'
    utils.setupFollowAttr(driver, ctrl)
    """
    # Driver transforms
    staticTransform = pm.createNode('transform', n='{}Static'.format(controller.replace('IK', 'IKOffset')))
    staticTransformOffset = pm.createNode('transform', n='{}StaticOffset'.format(controller.replace('IK', 'IKOffset')))
    pm.PyNode('IKStatic') | staticTransformOffset | staticTransform
    pm.matchTransform(staticTransformOffset, controller)

    followTransform = pm.createNode('transform', n='{}Follow'.format(controller.replace('IK', 'IKOffset')))
    followTransformOffset = pm.createNode('transform', n='{}FollowOffset'.format(controller.replace('IK', 'IKOffset')))
    pm.PyNode('IKFollow') | followTransformOffset | followTransform
    pm.matchTransform(followTransformOffset, controller)
    pm.parentConstraint(driverTransform, followTransform, mo=True)

    pConst = pm.parentConstraint(staticTransform, followTransform, controller.replace('IK', 'IKOffset'), mo=True)

    # Attribute connections
    controller = pm.PyNode(controller)
    pm.addAttr(controller, ln='follow', at='double', min=0, max=10, keyable=True)

    setRange = pm.createNode('setRange', n='{}SetRangeFollw'.format(controller))
    setRange.oldMaxX.set(10)
    setRange.oldMaxY.set(10)
    setRange.minX.set(0)
    setRange.minY.set(1)
    setRange.maxX.set(1)
    setRange.maxY.set(0)

    controller.attr('follow') >> setRange.valueX
    controller.attr('follow') >> setRange.valueY
    setRange.outValueX >> pConst.attr('{}W1'.format(followTransform))
    setRange.outValueY >> pConst.attr('{}W0'.format(staticTransform))
