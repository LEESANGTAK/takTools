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
#       - It works to controllers or components of a deformer
#       - etc...
#   Contact: https://ta-note.com or chst27@gmail.com
#---------------------------------------------------------------------------------------------------------------


import maya.cmds as cmds
import math


HOLD_JOINT_NAME = 'hold_jnt'

selVtxs = []
selDrivers = []


# Procedure to get the selected vertexs information
def getSelectedVertices(*args):
    global selVtxs
    selVtxs = cmds.filterExpand(cmds.ls(sl=1, fl=1), sm=31)


# Procedure to get the selected drivers information
def getSelectedDrivers(*args):
    global selDrivers
    selDrivers = cmds.ls(sl=1, fl=1)


# This procedure will return name of the skincluster for selected object
def getSkinCluster(geo):
    skinCluster = []
    vertHistory = cmds.listHistory(geo, il=1, pdo=True)
    skinCluster = cmds.ls(vertHistory, type='skinCluster')
    if skinCluster:
        return skinCluster[0]


# Procedure to unhold the joints for selected object
def unlockAllInfluences(skinCluster):
    influences = cmds.skinCluster(skinCluster, q=1, inf=1)
    for inf in influences:
        cmds.setAttr(inf + '.liw', 0)


# Main Procedure which converts deformation information into skincluster weight information
def convert(*args):
    geo = selVtxs[0].split('.')[0]
    skinClst = getSkinCluster(geo)

    # If mesh has no skin cluster bind with a 'hold_jnt'
    if not skinClst:
        if cmds.objExists(HOLD_JOINT_NAME):
            cmds.delete(HOLD_JOINT_NAME)
        cmds.select(cl=1)
        cmds.joint(n=HOLD_JOINT_NAME)
        cmds.select(geo, add=1)
        cmds.SmoothBindSkin()
        skinClst = getSkinCluster(geo)

    unlockAllInfluences(skinClst)

    # Create joints for the drivers
    joints = []
    for i in range(0, len(selDrivers)):
        cmds.select (cl=1)
        jnt = cmds.joint()
        joints.append(jnt)
        jntZeroGrp = cmds.group(n=jnt + '_jnt_grp')  # Group a joint

        # Match a joint's zero group transform to a driver
        driverPos = cmds.xform(selDrivers[i], q=True, t=True, ws=True)
        if driverPos == [0.0, 0.0, 0.0]:
            driverPos = cmds.xform(selDrivers[i], q=True, rp=True, ws=True)
        cmds.xform(jntZeroGrp, t=driverPos, ws=True)

        cmds.select(geo)
        cmds.skinCluster(e=1, dr=4, lw=0, wt=0, ai=joints[i])  # Add a joint to geometry as influence

    numDrivers = len(selDrivers)
    numVtxs = len(selVtxs)
    cmds.progressWindow(title='Convert 2 Skin', minValue=0, maxValue=numDrivers, progress=0, status='Stand by', isInterruptable=True)

    for i in range (0, numDrivers):
        for j in range (0, numVtxs):
            if cmds.progressWindow(query=True, isCancelled=True):
                break

            originalPos = cmds.xform(selVtxs[j], q=1, wd=1, t=1)

            # Get deformed position for a vertex by moving a driver
            driverOrigPos = cmds.xform(selDrivers[i], q=True, t=True, ws=True)
            cmds.xform(selDrivers[i], t=[driverOrigPos[0], driverOrigPos[1], driverOrigPos[2] + 1], ws=True)
            deformPos = cmds.xform(selVtxs[j], q=1, t=1, wd=1)
            cmds.xform(selDrivers[i], t=driverOrigPos, ws=True)

            # Set weight as length of the delta for a contoller
            # Moved just 1 unit so delta length is be weight literally
            difference = [deformPos[0]-originalPos[0], deformPos[1]-originalPos[1], deformPos[2]-originalPos[2]]
            deltaLength = math.sqrt(pow(difference[0], 2) + pow(difference[1], 2) + pow(difference[2], 2))
            cmds.skinPercent(skinClst, selVtxs[j], nrm=1, tv=[joints[i], deltaLength])

        cmds.progressWindow(e=True, progress=i, status=selDrivers[i])

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

    cmds.button(ann ='Select the drivers which deforms the selected vertices. It can be cv, cluster, point...' ,
                l='Get Selected drivers',
                h=40, w=125, c=getSelectedDrivers)

    cmds.setParent('..')
    cmds.separator(h=10)
    cmds.button(ann ='Press the button to Convert. Note:- This will some time according to the number of vertex selected ' ,
                l='CONVERT',
                h=40, c=convert)

    cmds.window('convert2skinWin', e=1, s=0, w=50, h=50)
    cmds.showWindow('convert2skinWin')
