import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from ..rigging import tak_cleanUpRig



# UI
def UI():
    # check the window exists
    if cmds.window('asWin', exists = True): cmds.deleteUI('asWin')

    # create the window
    cmds.window('asWin', title = 'Tools For Advanced Skeleton', mnb = False, mxb = False)

    cmds.columnLayout(adj = True, rs = 1)
    cmds.text(label = '# Before Rebuild #')
    cmds.button(label = 'Delete Skin Pose', c = delSkinPose)
    cmds.button(label = 'Remove custom nodes from advanced skeleton "Sets", "jointLayer"', c = rmvCustomRigNodesFromSets)
    cmds.text(label = 'Delete Custom Connections to Advanced Skeleton Rig')
    cmds.button(label = 'Unlock All Geometries Transform', c = tak_cleanUpRig.unlockGeoTrsf)
    cmds.button(label = 'Match Fit Joint to The Skin Pose Locator', c = fitJntToSkinPose)
    cmds.separator()
    cmds.text(label = '# Before Build #')
    cmds.button(label = 'Transfer Orient To Rotate', c = transferOrientToRotate)
    cmds.button(label = 'Align Ankle Joint Orientation to World', c = alignAnkleOriToWorld)
    cmds.button(label = 'Go to The Build Pose For Fit Joint', c = fitJntToBuildPose)
    # cmds.button(label = 'Create Skin Pose Locator', c = createSkinPoseLoc)
    cmds.separator()
    cmds.text(label = '# After Build #')
    cmds.button('conMatch', label = 'Match the Controls to Skin Pose Locator', c = conMatch)
    cmds.button('selSkinPosCtrl', label = 'Select Controls to Make Skin Pose', c = selSkinPosCtrl)
    cmds.button('clnOutl', label = 'Clean Up Outliner', c = clnOutl)

    cmds.window('asWin', e = True, w = 250, h = 100)
    cmds.showWindow('asWin')





def createSkinPoseLoc(*args):
    jntList = ['Scapula', 'Shoulder', 'Elbow', 'Wrist', 'Hip', 'Knee', 'Ankle', 'MiddleToe1', 'MiddleToe2', 'Heel']
    if not cmds.objExists('skinPose_loc_grp'):
        cmds.createNode('transform', n = 'skinPose_loc_grp')
        cmds.setAttr('skinPose_loc_grp.visibility', 0)
    # make skinPose loc
    for i in range(len(jntList)):
        # check the jnt existing
        result = cmds.objExists(jntList[i])
        if result:
            if cmds.objExists(jntList[i] + '_skinPose_loc'):
                cmds.delete(jntList[i] + '_skinPose_loc')
                locName = cmds.spaceLocator(n = jntList[i] + '_skinPose_loc')
                cmds.select(jntList[i], r = True)
                cmds.select(locName, tgl = True)
                cmds.parentConstraint(mo = False)
                cmds.select(locName, r = True)
                cmds.delete(cn = True)
                cmds.parent(locName, 'skinPose_loc_grp')
            else:
                locName = cmds.spaceLocator(n = jntList[i] + '_skinPose_loc')
                cmds.select(jntList[i], r = True)
                cmds.select(locName, tgl = True)
                cmds.parentConstraint(mo = False)
                cmds.select(locName, r = True)
                cmds.delete(cn = True)
                cmds.parent(locName, 'skinPose_loc_grp')
        else:
            continue





def fitJntToSkinPose(*args):
    jntList = ['Scapula', 'Shoulder', 'Elbow', 'Wrist', 'Hip', 'Knee', 'Ankle', 'MiddleToe1', 'MiddleToe2', 'Heel']

    for jnt in jntList:
        if cmds.objExists(jnt):
            cmds.delete(cmds.parentConstraint(jnt + '_skinPose_loc', jnt, mo = False))
        else:
            pass






def fitJntToBuildPose(*args):
    jntList = ['Scapula', 'Shoulder', 'Elbow', 'Wrist', 'Hip', 'Knee', 'Ankle', 'MiddleToe1', 'MiddleToe2', 'Heel']

    for jnt in jntList:
        if cmds.objExists(jnt):
            chkJntOri(jnt)
            chkRoVal(jnt)
            chkTrsVal(jnt)

    createSkinPoseLoc()

    # set joint's rotation to default value
    cmdList = ["cmds.setAttr('Scapula.rotate',  90, 151.253, 61.253),",
                "cmds.setAttr('Shoulder.rotate',  0, -5, 0),",
                "cmds.setAttr('Elbow.rotate',  0, 10, 0),",
                "cmds.setAttr('Wrist.rotate',  0, -5, 0),",
                "cmds.setAttr('Hip.rotate',  0, 0, 179.493),",
                "cmds.setAttr('Knee.rotate', 0, 0, 2.707),",
                "cmds.setAttr('Ankle.rotate', -0.019, 0, -2.199),",
                "cmds.setAttr('MiddleToe1.translateZ', 0),",
                "cmds.setAttr('MiddleToe2.translateZ', 0),",
                "cmds.setAttr('Heel.translateZ', 0),"]
    cmd = ""
    for i in range(len(jntList)):
        # check the jnt existing
        result = cmds.objExists(jntList[i])
        if result:
            cmd += cmdList[i]
        else:
            continue
    eval(cmd)

    # Align scapula joint to the world.
    scplWrldPos = cmds.xform('Scapula', q = True, t = True, ws = True)
    scplAlnLoc = cmds.spaceLocator(n = 'Scapula_align_loc', p = scplWrldPos)
    cmds.xform(scplAlnLoc, ws = True, ro = [0, 180, 0 ])
    cmds.delete(cmds.orientConstraint(scplAlnLoc, 'Scapula', mo = False))
    cmds.delete(scplAlnLoc)



def chkJntOri(jnt):
    if jnt in ['MiddleToe1', 'MiddleToe2', 'Heel']:
        pass
    else:
        joX = cmds.getAttr("%s.jointOrientX" %jnt)
        if "e-" in str(joX):
            joX = 0
        if joX != 0:
            cmds.select(jnt)
            cmds.error("%s.jointOrientX is not 0." %jnt)

        joY = cmds.getAttr("%s.jointOrientY" %jnt)
        if "e-" in str(joY):
            joY = 0
        if joY != 0:
            cmds.select(jnt)
            cmds.error("%s.jointOrientY is not 0." %jnt)

        joZ = cmds.getAttr("%s.jointOrientZ" %jnt)
        if "e-" in str(joZ):
            joZ = 0
        if joZ != 0:
            cmds.select(jnt)
            cmds.error("%s.jointOrientZ is not 0." %jnt)


def chkRoVal(jnt):
    """
    Check rotate values that should be 0.
    """

    if jnt == "Elbow":
        joRX = cmds.getAttr("%s.rotateX" %jnt)
        if "e-" in str(joRX):
            joRX = 0
        if joRX != 0:
            cmds.select("Elbow")
            cmds.error("Elbow.rotateX should be 0.")

        joRZ = cmds.getAttr("%s.rotateZ" %jnt)
        if "e-" in str(joRZ):
            joRZ = 0
        if joRZ != 0:
            cmds.select("Elbow")
            cmds.error("Elbow.rotateZ should be 0.")

    elif jnt == "Knee":
        joRX = cmds.getAttr("%s.rotateX" %jnt)
        if "e-" in str(joRX):
            joRX = 0
        if int(cmds.getAttr("Knee.rotateX")) != 0:
            cmds.select("Knee")
            cmds.error("Knee.rotateX should be 0.")

        joRY = cmds.getAttr("%s.rotateY" %jnt)
        if "e-" in str(joRY):
            joRY = 0
        if joRY != 0:
            cmds.select("Knee")
            cmds.error("Knee.rotateY should be 0.")


def chkTrsVal(jnt):
    '''
    Check translate values that should have 0.
    '''

    if jnt in ['Shoulder', 'Elbow', 'Wrist', 'Knee', 'Ankle', 'MiddleToe2']:
        joTY = cmds.getAttr("%s.translateY" %jnt)
        if "e-" in str(joTY):
            joTY = 0
        if not joTY == 0:
            cmds.select(jnt)
            cmds.error('%s.translateY should be 0.' %jnt)

        joTZ = cmds.getAttr("%s.translateZ" %jnt)
        if "e-" in str(joTZ):
            joTZ = 0
        if not joTZ == 0:
            cmds.select(jnt)
            cmds.error('%s.translateZ should be 0.' %jnt)

    elif jnt in ['MiddleToe1', 'Heel']:
        joTZ = cmds.getAttr("%s.translateZ" %jnt)
        if "e-" in str(joTZ):
            joTZ = 0
        if not joTZ == 0:
            cmds.select(jnt)
            cmds.error('%s.translateZ should be 0.' %jnt)





# match controls to the skin pose locators
def conMatch(*args):
    # delKeys()

    matchList = ['Scapula', 'Shoulder', 'Elbow', 'Wrist']

    for x in matchList:
        result = cmds.objExists(x + '_skinPose_loc')
        if result:
            cmds.select(x + '_skinPose_loc')
            cmds.select('FK' + x + '_R', tgl = True)
            cmds.parentConstraint(mo = False)
            cmds.select('FK' + x + '_R', r = True)
            cmds.delete(cn = True)
        else:
            continue

    if cmds.objExists('Ankle_skinPose_loc'):
        cmds.delete(cmds.pointConstraint('Ankle_skinPose_loc', 'IKLeg_R', mo = False))
    # Mtach "IKLeg_R" orientation.
    if cmds.objExists('MiddleToe2_skinPose_loc'):
        cmds.delete(cmds.aimConstraint("MiddleToe2_skinPose_loc", "IKLeg_R", mo = False, aimVector = [0, 0, 1], upVector = [0, 1, 0], worldUpType = "vector", worldUpVector = [0, 1, 0], skip = ["x", "z"]))

    # FK/IK match and mirror pose.
    melCmdLs = ['source "AdvancedSkeleton/Selector/biped.mel";asSelectorbiped;',
                'asAlignFK2IK "biped" {"FKIKArm_R"};',
                'asAlignIK2FK "biped" {"FKIKLeg_R"};',
                'asMirror asSelectorbiped;',
                'setAttr -lock true "Fingers_L.sx";',
                'setAttr -lock true "Fingers_R.sx";',
                'setAttr -lock true "Fingers_L.sy";',
                'setAttr -lock true "Fingers_R.sy";',
                'setAttr -lock true "Fingers_L.sz";',
                'setAttr -lock true "Fingers_R.sz";']

    for melCmd in melCmdLs:
        try:
            mel.eval(melCmd)
        except:
            pass


def delKeys(*args):
    # Go to the first frame
    # firstFrame = cmds.playbackOptions(q = True, min = True)
    cmds.currentTime(1)

    # If advanced skeleton is used launch advanced skeleton selector and select all controls in the control set.
    if cmds.objExists('Sets'):
        mel.eval('source "AdvancedSkeleton/Selector/biped.mel";asSelectorbiped;')
        mel.eval('asSelect "biped" {"ControlSet"};')
    if cmds.objExists('FKRoot_M'):
        cmds.select('FKRoot_M', add = True)

    # Delete keys
    ctrlList = cmds.ls(sl = True)
    cmds.select(ctrlList, r = True)
    mel.eval('doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","0","animationList","0","noOptions","0","0" };')

    # Set default value.
    for ctrl in ctrlList:
        attrLs = cmds.listAttr(ctrl, keyable = True)
        if attrLs:
            for attr in attrLs:
                if 'translate' in attr or 'rotate' in attr:
                    try:
                        cmds.setAttr('%s.%s' %(ctrl, attr), 0)
                    except:
                        pass

    # If advanced skeleton is used run reset pose.
    if cmds.objExists('Sets'):
        mel.eval("asGoToBuildPose asSelectorbiped;")





# select cnt to make skin pose
def selSkinPosCtrl(*args):
    skinPosConLs = ['FKScapula_R', 'FKShoulder_R', 'FKElbow_R', 'FKWrist_R', 'FKScapula_L', 'FKShoulder_L', 'FKElbow_L', 'FKWrist_L', 'PoleLeg_L', 'PoleLeg_R', 'IKLeg_R', 'IKLeg_L', 'PoleArm_R', 'PoleArm_L', 'IKArm_R', 'IKArm_L', 'FKHip_R', 'FKKnee_R', 'FKAnkle_R', 'FKHip_L', 'FKKnee_L', 'FKAnkle_L',]
    cmds.select(cl = True)
    for con in skinPosConLs:
        try:
            cmds.select(con, add = True)
        except:
            pass





# clean up outliner
def clnOutl(*args):
    if not cmds.objExists('Geometry'):
        cmds.createNode('transform', n = 'Geometry')
        cmds.parent('Geometry', 'Group')
    if not cmds.objExists('wip_GRP'):
        cmds.createNode('transform', n = 'wip_GRP')
        cmds.setAttr('wip_GRP.visibility', False)
    if not cmds.objExists('rig'):
        cmds.createNode('transform', n = 'rig')
        cmds.parent('rig', 'root')
    if not cmds.objExists('lod01_GRP'):
        cmds.createNode('transform', n = 'lod01_GRP')
        cmds.parent('lod01_GRP', 'Geometry')
    if not cmds.objExists('lod02_GRP'):
        cmds.createNode('transform', n = 'lod02_GRP')
        cmds.parent('lod02_GRP', 'Geometry')
    if not cmds.objExists('extra_ctrl_grp'):
        cmds.createNode('transform', n = 'extra_ctrl_grp')
        cmds.parent('extra_ctrl_grp', 'Sub')

    fingerCtrls = ['Fingers_L', 'Fingers_R']
    for fingerCtrl in fingerCtrls:
        cmds.setAttr(fingerCtrl + '.scale', lock = True)

    cmds.parent('Group', 'rig')
    if cmds.objExists('skinPose_loc_grp') and cmds.objExists('wip_GRP'):
        try:
            cmds.parent('skinPose_loc_grp', 'wip_GRP')
        except:
            print('skinPose_loc_grp is already in wip_GRP')





def alignAnkleOriToWorld(*args):
    loc = cmds.spaceLocator(n = 'ankleAlign_loc')
    cmds.delete(cmds.parentConstraint('Ankle', loc, mo = False))
    cmds.xform(loc, ro = [-90, 0, -90], ws = True)
    cmds.delete(cmds.orientConstraint(loc, 'Ankle', mo = False, skip = 'x'))
    cmds.delete(loc)





def rmvCustomRigNodesFromSets(*args):
    cmds.select('extra*_grp', 'misc*_grp', r=True, hi=True)
    if cmds.objExists('facial*_grp'):
        cmds.select('facial*_grp', add = True, hi = True)

    customRigNodes = cmds.ls(sl = True)

    cmds.sets(customRigNodes, rm = 'ControlSet')
    cmds.sets(customRigNodes, rm = 'AllSet')
    cmds.sets(customRigNodes, rm = 'DeformSet')

    cmds.editDisplayLayerMembers('defaultLayer', customRigNodes)





def delSkinPose(*args):
    '''
    Delete skin pose that constraint controls offset group.
    '''

    mel.eval('source "AdvancedSkeleton/Selector/biped.mel";')
    mel.eval('delSkinPose 1;')


def transferOrientToRotate(*args):
    for jnt in pm.selected():
        jntOrient = jnt.jointOrient.get()
        jntRotate = jnt.rotate.get()
        jnt.jointOrient.set([0, 0, 0])
        jnt.rotate.set([sum(i) for i in zip(jntOrient, jntRotate)])


def alignArmIkCtrls():
    armIkAlignTo = {
        'IKArm_L': 'FKWrist_L',
        'IKArm_R': 'FKWrist_R'
    }

    for armIk, alignObj in armIkAlignTo.iteritems():
        # Convert string to pymel node
        armIk = pm.PyNode(armIk)
        alignObj = pm.PyNode(alignObj)

        # Parent armIk child nodes to the world space
        armIkChilds = armIk.getChildren(type=['transform', 'ikHandle'])
        pm.parent(armIkChilds, world=True)

        alignTrsfName = armIk.name()+'_align'
        if pm.objExists(alignTrsfName):
            alignTrsf = pm.PyNode(alignTrsfName)
            alignTrsf.getChildren()[0].rotate.set(0, 0, 0)
        else:
            # Make align transform node
            alignTrsf = pm.createNode('transform', n=alignTrsfName)
            pm.matchTransform(alignTrsf, armIk)
            armIk.getParent(generations=2) | alignTrsf
            alignTrsf | armIk.getParent(generations=1)

            # Get aligned matrix
            alignObjMtrx = alignObj.getMatrix(worldSpace=True)
            if armIk.name() == 'IKArm_L':
                alignedMtrx = [
                    -alignObjMtrx(2, 0), -alignObjMtrx(2, 1), -alignObjMtrx(2, 2), 0,
                    alignObjMtrx(0, 0), alignObjMtrx(0, 1), alignObjMtrx(0, 2), 0,
                    -alignObjMtrx(1, 0), -alignObjMtrx(1, 1), -alignObjMtrx(1, 2), 0,
                    alignObjMtrx(3, 0), alignObjMtrx(3, 1), alignObjMtrx(3, 2), 1
                ]
            elif armIk.name() == 'IKArm_R':
                alignedMtrx = [
                    -alignObjMtrx(2, 0), -alignObjMtrx(2, 1), -alignObjMtrx(2, 2), 0,
                    -alignObjMtrx(0, 0), -alignObjMtrx(0, 1), -alignObjMtrx(0, 2), 0,
                    alignObjMtrx(1, 0), alignObjMtrx(1, 1), alignObjMtrx(1, 2), 0,
                    alignObjMtrx(3, 0), alignObjMtrx(3, 1), alignObjMtrx(3, 2), 1
                ]

            # Assign matrix to the align transform
            pm.xform(alignTrsf, matrix=alignedMtrx, worldSpace=True)

        pm.parent(armIkChilds, armIk)


def alignLegIkCtrls():
    legIkAlignTo = {
        'IKLeg_L': 'IKLegFootRoll_L',
        'IKLeg_R': 'IKLegFootRoll_R'
    }

    for legIk, alignObj in legIkAlignTo.iteritems():
        # Convert string to pymel node
        legIk = pm.PyNode(legIk)
        alignObj = pm.PyNode(alignObj)

        # Parent legIk child nodes to the world space
        legIkChilds = legIk.getChildren(type='transform')
        pm.parent(legIkChilds, world=True)

        alignTrsfName = legIk.name()+'_align'
        if pm.objExists(alignTrsfName):
            alignTrsf = pm.PyNode(alignTrsfName)
            alignTrsf.getChildren()[0].rotate.set(0, 0, 0)
        else:
            # Make align transform node
            alignTrsf = pm.createNode('transform', n=legIk.name()+'_align')
            pm.matchTransform(alignTrsf, legIk)
            legIk.getParent(generations=2) | alignTrsf
            alignTrsf | legIk.getParent(generations=1)

            alignObjMatrix = alignObj.getMatrix(worldSpace=True)
            pm.xform(alignTrsf, matrix=alignObjMatrix, worldSpace=True)

        pm.parent(legIkChilds, legIk)
