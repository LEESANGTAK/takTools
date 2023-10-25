import pymel.core as pm

from rigging import autoRigging as ar

pm.newFile(f=True)

modelFile = 'R:/SB_Art/3_Character/Monster/Boss/ProtoType03ArmL/Model/Boss_ProtoType03ArmL_Model.ma'
skeletonFile = 'R:/SB_Art/3_Character/Monster/Boss/ProtoType03ArmL/Skeleton/Boss_ProtoType03ArmL_Skeleton.ma'
skinFile = 'R:/SB_Art/3_Character/Monster/Boss/ProtoType03ArmL/Skeleton/Boss_ProtoType03ArmL_Skin.weights'

ar.base.general.setupForBuild(
    'ArmL',
    modelFile,
    skeletonFile,
    skinFile,
)

limbJoints = ['Shoulder_L', 'Elbow_L', 'Wrist_L']
upTwistJoints = ['Shoulder_L', 'ShoulderPart1_L', 'ShoulderPart2_L', 'Elbow_L']
lowTwistJoints = ['Elbow_L', 'ElbowPart1_L', 'ElbowPart2_L', 'Wrist_L']

ar.module.limb.build(
    'ArmL',
    limbJoints,
    upTwistJoints,
    lowTwistJoints,
    -1,
    parentSapce=None,
)


handRootJnt = 'Wrist_L'
ar.module.simpleFK.build(
    name='handL',
    rootJoint=handRootJnt,
    parentSapce='Wrist_L_result',
)







import pymel.core as pm

from rigging import autoRigging as ar

pm.newFile(f=True)

modelFile = 'R:/SB_Art/3_Character/Monster/Boss/ProtoType03ArmR/Model/Boss_ProtoType03ArmR_Model.ma'
skeletonFile = 'R:/SB_Art/3_Character/Monster/Boss/ProtoType03ArmR/Skeleton/Boss_ProtoType03ArmR_Skeleton.ma'
skinFile = 'R:/SB_Art/3_Character/Monster/Boss/ProtoType03ArmR/Skeleton/Boss_ProtoType03ArmR_Skin.weights'

ar.base.general.setupForBuild(
    'ArmR',
    modelFile,
    skeletonFile,
    skinFile,
)

limbJoints = ['Shoulder_R', 'Elbow_R', 'Wrist_R']
upTwistJoints = ['Shoulder_R', 'ShoulderPart1_R', 'ShoulderPart2_R', 'Elbow_R']
lowTwistJoints = ['Elbow_R', 'ElbowPart1_R', 'ElbowPart2_R', 'Wrist_R']

ar.module.limb.build(
    'ArmR',
    limbJoints,
    upTwistJoints,
    lowTwistJoints,
    1,
    parentSapce=None,
)


handRootJnt = 'Wrist_R'
ar.module.simpleFK.build(
    name='handR',
    rootJoint=handRootJnt,
    parentSapce='Wrist_R_result',
)
