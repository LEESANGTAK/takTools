#--------------------------------------------------------------------------------------------------------------
#	SCRIPT:	All_Deformer_2_SkinCluster
#	AUTHOR:	Praveen V, Sr.Rigging Artist, Paprikaas Animation Studio, Bangalore
#	E-Mail:	praveenact@yahoo.com
#
# This script can Convert all kind deformers into skincluster .
# The skinned weight result will be very much near to the deformer deformation.
#
# Use:
#   import All_Deformers_2_SkinCluster as ad2sc
#   ad2sc.showGUI()
#
# Notice:
#   Refactored by Sangtak Lee
#       - Renamed variables and functions to meaningfull
#       - Added some comments
#       - It works correctly with progress window
#       - Prevent causes bugs
#       - etc...
#   Contact: https://ta-note.com or chst27@gmail.com
#---------------------------------------------------------------------------------------------------------------


import maya.cmds as cmds
import math


HOLD_JOINT_NAME = 'hold_jnt'

selVtxs = []
selCtrls = []


# Procedure to get the selected vertexs information
def getSelectedVertices(*args):
    global selVtxs
    selVtxs = cmds.filterExpand(cmds.ls(sl=1, fl=1), sm=31)


# Procedure to get the selected controls information
def getSelectedControllers(*args):
    global selCtrls
    selCtrls = cmds.ls(sl=1, fl=1, type='transform')


# This procedure will return name of the skincluster for selected object
def getSkinCluster(geo):
    skinCluster = []
    vertHistory = cmds.listHistory(geo, il=1, pdo=True)
    skinCluster = cmds.ls(vertHistory, type='skinCluster')
    if skinCluster:
        return skinCluster[0]


# Procedure to unhold the joints for selected object
def unlockAllInfluences(skinCluster):
    influences = cmds.skinCluster (skinCluster, q=1, inf=1)
    for inf in influences:
        cmds.setAttr(inf + '.liw', 0)


# Main Procedure which converts deformation information into skincluster weight information
def convert(*args):
    Base_GeoNm = selVtxs[0].split('.')
    skinClst = getSkinCluster(Base_GeoNm[0])

    if(skinClst == None):
        if cmds.objExists(HOLD_JOINT_NAME):
            cmds.delete(HOLD_JOINT_NAME)
        cmds.select(cl=1)
        cmds.joint(n=HOLD_JOINT_NAME)
        cmds.select(Base_GeoNm[0],add=1)
        cmds.SmoothBindSkin()
        skinClst = getSkinCluster(Base_GeoNm[0])

    unlockAllInfluences(skinClst)
    joints = []

    # Create joints for the controllers
    for i in range(0, len(selCtrls)):
        cmds.select (cl=1)
        joints.append(cmds.joint(n=selCtrls[i] + '_jnt'))
        jntZeroGrp = cmds.group(n=selCtrls[i] + '_jnt_grp')  # Group a joint
        cmds.delete(cmds.parentConstraint(selCtrls[i], jntZeroGrp))  # Match a joint's zero group transform to a controller
        cmds.select(Base_GeoNm[0])
        cmds.skinCluster(e=1, dr=4, lw=0, wt=0, ai=joints[i])  # Add a joint to geometry as influence

    numCtrls = len(selCtrls)
    numVtxs = len(selVtxs)
    cmds.progressWindow(title='Convert 2 Skin', minValue=0, maxValue=numCtrls, progress=0, status='Stand by', isInterruptable=True)

    for i in range (0,numCtrls):
        for j in range (0,numVtxs):
            if cmds.progressWindow(query=True, isCancelled=True):
                break

            originalPos = cmds.xform(selVtxs[j], q=1, wd=1, t=1)

            # Get deformed position for a vertex
            ctrlOrigTz = cmds.getAttr(selCtrls[i] + '.tz')
            cmds.setAttr(selCtrls[i] + '.tz', -1)
            deformPos = cmds.xform(selVtxs[j], q=1, wd=1, t=1)
            cmds.setAttr(selCtrls[i] + '.tz', ctrlOrigTz)

            # Calculate weight for a controller using basis function depend on delta between deformed vertex and original vertex
            difference = [deformPos[0]-originalPos[0], deformPos[1]-originalPos[1], deformPos[2]-originalPos[2]]
            wtValue = math.sqrt (pow(difference[0] ,2) + pow(difference[1] ,2) + pow(difference[2] ,2))

            cmds.skinPercent(skinClst, selVtxs[j], nrm=1, tv=[joints[i],wtValue])

        cmds.progressWindow(e=True, progress=i, status=selCtrls[i])

    cmds.progressWindow(endProgress=1)


# The Main Window Procedure
def showGUI(*args):
    if cmds.window('convert2skinWin', exists=True):
        cmds.deleteUI('convert2skinWin', window=True)

    cmds.window('convert2skinWin', t='All_Deformer_2_Skin', tlb=True)

    cmds.columnLayout(adj=1)

    cmds.rowLayout(numberOfColumns=2, columnWidth=[(1,125), (2,125)])
    cmds.button(ann ='Select the vertices which is need to be Converted' ,
                l='Get Selected Vertices',
                h=40, w=125, c=getSelectedVertices)

    cmds.button(ann ='Select the controllers which deforms the selected vertices' ,
                l='Get Selected Controllers',
                h=40, w=125, c=getSelectedControllers)

    cmds.setParent('..')
    cmds.separator(h=10)
    cmds.button(ann ='Press the button to Convert. Note:- This will some time according to the number of vertex selected ' ,
                l='CONVERT',
                h=40, c=convert)

    cmds.window('convert2skinWin', e=1, s=0, w=50, h=50)
    cmds.showWindow('convert2skinWin')
