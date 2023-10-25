import maya.cmds as cmds
import maya.mel as mel
mel.eval('source channelBoxCommand;')




### Cleanup Advanced Skeleton Bind Joints ###
cmds.select('Root_M', r = True)
cmds.SelectHierarchy()
cmds.DeleteConstraints()

def delHis():
    attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']
    selList = cmds.ls(sl = True)

    for sel in selList:
            # Unlock attribute
            for attr in attrList:
                cmds.setAttr(sel + '.' + str(attr), lock = False)
            # Break connections
            for attr in attrList:
                try:
                    mel.eval('CBdeleteConnection "{0}.{1}";'.format(sel, attr))
                except:
                    cmds.delete('{0}.{1}'.format(sel, attr), inputConnectionsAndNodes = True)
                mel.eval('CBdeleteConnection' + ' %s.%s;' %(sel, attr))
            # Delete construction history
            cmds.select(sel, r = True)
            cmds.delete(ch = True)
    cmds.select(selList, r = True)

# Delete empty transform nodes
trnsNods = cmds.ls(type = 'transform')
delTrns = []
for trns in trnsNods:
    if not cmds.listRelatives(trns, children = True) and not cmds.listConnections(trns):
        cmds.delete(trns)
        delTrns.append(trns)

delHis()

cmds.select('Root_M', r = True)




### Characterization Advanced Skeleton Bind Joints ###
charName = 'masa_skel'
mel.eval('hikCreateCharacter( "%s" );' %charName)
mel.eval('setCharacterObject("Root_M","%s",1,0);' %charName)
mel.eval('setCharacterObject("BackA_M","%s",8,0);' %charName)
mel.eval('setCharacterObject("BackB_M","%s",23,0);' %charName)
mel.eval('setCharacterObject("Chest_M","%s",24,0);' %charName)
mel.eval('setCharacterObject("Neck_M","%s",20,0);' %charName)
mel.eval('setCharacterObject("Head_M","%s",15,0);' %charName)
mel.eval('setCharacterObject("Scapula_L","%s",18,0);' %charName)
mel.eval('setCharacterObject("Scapula_R","%s",19,0);' %charName)
mel.eval('setCharacterObject("Shoulder_L","%s",9,0);' %charName)
mel.eval('setCharacterObject("Shoulder_R","%s",12,0);' %charName)
mel.eval('setCharacterObject("Elbow_L","%s",10,0);' %charName)
mel.eval('setCharacterObject("Elbow_R","%s",13,0);' %charName)
mel.eval('setCharacterObject("Wrist_L","%s",11,0);' %charName)
mel.eval('setCharacterObject("Wrist_R","%s",14,0);' %charName)
mel.eval('setCharacterObject("Hip_L","%s",2,0);' %charName)
mel.eval('setCharacterObject("Hip_R","%s",5,0);' %charName)
mel.eval('setCharacterObject("Knee_L","%s",3,0);' %charName)
mel.eval('setCharacterObject("Knee_R","%s",6,0);' %charName)
mel.eval('setCharacterObject("Ankle_L","%s",4,0);' %charName)
mel.eval('setCharacterObject("Ankle_R","%s",7,0);' %charName)
mel.eval('setCharacterObject("MiddleToe1_L","%s",16,0);' %charName)
mel.eval('setCharacterObject("MiddleToe1_R","%s",17,0);' %charName)

mel.eval('hikToggleLockDefinition();')





### Characterization Advanced Skeleton Controls ###
mel.eval('source channelBoxCommand;')

nameSpace = ''
charName = 'tomo'
mel.eval('hikCreateCharacter( "%s" );' %charName)
mel.eval('setCharacterObject("%sCenter_M","%s",1,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKBackA_M","%s",8,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKBackB_M","%s",23,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKChest_M","%s",24,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKNeck_M","%s",20,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKHead_M","%s",15,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKScapula_L","%s",18,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKScapula_R","%s",19,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKShoulder_L","%s",9,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKShoulder_R","%s",12,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKElbow_L","%s",10,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKElbow_R","%s",13,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKWrist_L","%s",11,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKWrist_R","%s",14,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKHip_L","%s",2,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKHip_R","%s",5,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKKnee_L","%s",3,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKKnee_R","%s",6,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKAnkle_L","%s",4,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKAnkle_R","%s",7,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKMiddleToe1_L","%s",16,0);' %(nameSpace, charName))
mel.eval('setCharacterObject("%sFKMiddleToe1_R","%s",17,0);' %(nameSpace, charName))

# Switch leg IK to FK
cmds.setAttr("%sFKIKLeg_R.FKIKBlend" %nameSpace, 0)
cmds.setAttr("%sFKIKLeg_L.FKIKBlend" %nameSpace, 0)

# Unlock 'Center_M' control scale attribute
mel.eval('CBunlockAttr "%sCenter_M.scaleX";' %nameSpace)
mel.eval('CBunlockAttr "%sCenter_M.scaleY";' %nameSpace)
mel.eval('CBunlockAttr "%sCenter_M.scaleZ";' %nameSpace)

mel.eval('hikToggleLockDefinition();')



### Bake Advanced Skeleton FK Key to IK ###
## Open advance biped selector and choose namespace
cmds.refresh(su = True)
switches = cmds.ls(sl = True)
if ':' in switches[0]:
    nameSpace = switches[0].split(':')[0]
else:
    nameSpace = ''
startFrame = cmds.playbackOptions(q = True, min = True)
endFrame = cmds.playbackOptions(q = True, max = True)
fkIkDic = {"FKIKArm_L": ['IKArm_L', 'PoleArm_L'], "FKIKArm_R": ['IKArm_R', 'PoleArm_R'], "FKIKLeg_L": ['IKLeg_L', 'PoleLeg_L'], "FKIKLeg_R": ['IKLeg_R', 'PoleLeg_R']}

while (startFrame <= endFrame):
    cmds.currentTime(startFrame)
    for switch in switches:
        switch = switch.split(':')[-1]
        # Matching
        mel.eval('asAlignFK2IK "biped" {"%s"};' %switch)
        # Set key
        for ikCtrl in fkIkDic[switch]:
            cmds.setKeyframe(nameSpace + ':' + ikCtrl)
    startFrame += 1
cmds.refresh(su = False)
cmds.refresh(f = True)




### Simplify Curve ####
def smpCrvUi():
    win = 'scWin'
    if cmds.window(win, exists = True):
        cmds.deleteUI(win)
    cmds.window(win, title = 'Procedure Simplify Curve')
    cmds.columnLayout('mainColLo', adj = True)

    cmds.rowColumnLayout('tTolRCLo', numberOfColumns = 3, columnWidth = [(2, 50), (3, 50)], columnSpacing = [(2, 3), (3, 5)], p = 'mainColLo')
    cmds.text(label = 'Time Tolerance Min/Max: ', p = 'tTolRCLo')
    cmds.floatField('tMinFltFld', v = 0.01, precision = 2, p = 'tTolRCLo')
    cmds.floatField('tMaxFltFld', v = 0.05, precision = 2, p = 'tTolRCLo')

    cmds.rowColumnLayout('vTolRCLo', numberOfColumns = 3, columnWidth = [(2, 50), (3, 50)], columnSpacing = [(3, 5)], p = 'mainColLo')
    cmds.text(label = 'Value Tolerance Min/Max: ', p = 'vTolRCLo')
    cmds.floatField('vMinFltFld', v = 0.01, precision = 2, p = 'vTolRCLo')
    cmds.floatField('vMaxFltFld', v = 0.05, precision = 2, p = 'vTolRCLo')

    cmds.button(label = 'Apply', h = 50, c = smpCrv, p = 'mainColLo')
    cmds.window(win, e = True, w = 150, h = 70)
    cmds.showWindow(win)


def smpCrv(*args):
    vTolMin = cmds.floatField('vMinFltFld', q = True, v = True)
    vTolMax = cmds.floatField('vMaxFltFld', q = True, v = True)
    tTolMin = cmds.floatField('tMinFltFld', q = True, v = True)
    tTolMax = cmds.floatField('tMaxFltFld', q = True, v = True)
    while tTolMin <= tTolMax:
        cmds.filterCurve(f = 'simplify', timeTolerance = 0.05)
        tTolMin += 0.01

smpCrvUi()


