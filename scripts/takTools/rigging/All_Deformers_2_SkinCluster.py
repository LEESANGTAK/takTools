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
#       - Improved performance x10
#       - etc...
#   Contact: https://ta-note.com or chst27@gmail.com
#---------------------------------------------------------------------------------------------------------------


import maya.cmds as cmds
import math
import time


HOLD_JOINT_NAME = 'hold_jnt'
MIN_WEIGHT = 0.01

selVtxs = []
selDrivers = []


# Procedure to get the selected vertexs information
def getSelectedVertices(*args):
    global selVtxs
    selVtxs = cmds.filterExpand(cmds.ls(sl=1, fl=1), sm=31)
    cmds.textScrollList('verticesTxtScrLs', e=True, removeAll=True)
    for vtx in selVtxs:
        cmds.textScrollList('verticesTxtScrLs', e=True, append=vtx)


# Procedure to get the selected drivers information
def getSelectedDrivers(*args):
    global selDrivers
    selDrivers = cmds.ls(sl=True, fl=True)

    # Since weights are constantly normalized from start to end of the process, weights of a center joint can be asymmetry
    # To prevent this sort drivers from bounds of the bounding box to center
    bbox = cmds.exactWorldBoundingBox(selDrivers)
    bboxCenter = [(bbox[0]+bbox[3])*0.5, (bbox[1]+bbox[4])*0.5, (bbox[2]+bbox[5])*0.5]
    distFromCenterMap = {}
    for driver in selDrivers:
        driverPos = cmds.xform(driver, q=True, t=True, ws=True)
        if driverPos == [0.0, 0.0, 0.0]:
            driverPos = cmds.xform(driver, q=True, rp=True, ws=True)
        distFromCenter = math.sqrt(math.pow(driverPos[0]-bboxCenter[0], 2) + math.pow(driverPos[1]-bboxCenter[1], 2) + math.pow(driverPos[2]-bboxCenter[2], 2))
        distFromCenterMap[driver] = distFromCenter
    sortedDrivers = dict(sorted(distFromCenterMap.items(), key=lambda item: item[1], reverse=True))
    selDrivers = list(sortedDrivers.keys())

    cmds.textScrollList('driversTxtScrLs', e=True, removeAll=True)
    for driver in selDrivers:
        cmds.textScrollList('driversTxtScrLs', e=True, append=driver)

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


def correctDeformersOrder(geometry, skinCluster):
    history = cmds.listHistory(geometry, pruneDagObjects=True)
    deformers = cmds.ls(history, type="geometryFilter")
    if not deformers[0] == skinCluster:
        # First move skincluster to below the first deformer
        cmds.reorderDeformers(deformers[0], skinCluster, geometry)
        # Then swap order to place skin cluster as top
        cmds.reorderDeformers(skinCluster, deformers[0], geometry)


# Main Procedure which converts deformation information into skincluster weight information
def convert(*args):
    startTime = time.time()

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
    correctDeformersOrder(geo, skinClst)
    unlockAllInfluences(skinClst)

    # Create joints for the drivers
    joints = []
    for i in range(0, len(selDrivers)):
        cmds.select (cl=1)
        jnt = cmds.joint()
        joints.append(jnt)

        # Match a joint position to a driver
        driverPos = cmds.xform(selDrivers[i], q=True, t=True, ws=True)
        if driverPos == [0.0, 0.0, 0.0]:
            driverPos = cmds.xform(selDrivers[i], q=True, rp=True, ws=True)
        cmds.xform(jnt, t=driverPos, ws=True)

        cmds.select(geo)
        cmds.skinCluster(e=1, dr=4, lw=0, wt=0, ai=joints[i])  # Add a joint to geometry as influence

    numDrivers = len(selDrivers)
    cmds.progressWindow(title='Convert 2 Skin', minValue=0, maxValue=numDrivers, progress=0, status='Stand by', isInterruptable=True)

    # Get vertices original positions
    vtxsOrigPos = [cmds.xform(vtx, q=True, t=True, ws=True) for vtx in selVtxs]
    for i in range(0, numDrivers):
        # Get vertices deformed positions
        driverOrigPos = cmds.xform(selDrivers[i], q=True, t=True, ws=True)
        cmds.xform(selDrivers[i], t=[driverOrigPos[0], driverOrigPos[1], driverOrigPos[2] + 1], ws=True)
        vtxsDefPos = [cmds.xform(vtx, q=True, t=True, ws=True) for vtx in selVtxs]
        cmds.xform(selDrivers[i], t=driverOrigPos, ws=True)

        # Set weights for a driver
        for j, (vtxOrigPos, vtxDefPos) in enumerate(zip(vtxsOrigPos, vtxsDefPos)):
            delta = [vtxDefPos[0]-vtxOrigPos[0], vtxDefPos[1]-vtxOrigPos[1], vtxDefPos[2]-vtxOrigPos[2]]
            weight = math.sqrt(pow(delta[0], 2) + pow(delta[1], 2) + pow(delta[2], 2))  # Since we move a driver 1 unit the weight for a vertex is same as distance of delta
            if weight < MIN_WEIGHT:
                continue
            cmds.skinPercent(skinClst, selVtxs[j], nrm=1, tv=[joints[i], weight])

        cmds.progressWindow(e=True, progress=i, status=selDrivers[i])
    cmds.progressWindow(endProgress=1)

    elapsedTime = time.time() - startTime
    print('"{}()" takes time to run {}s.'.format(convert.__name__, round(elapsedTime, 2)))


# The Main Window Procedure
def showGUI(parent=None, *args):
    if cmds.window('convert2skinWin', exists=True):
        cmds.deleteUI('convert2skinWin', window=True)

    cmds.window('convert2skinWin', t='All_Deformer_2_Skin', tlb=True, p=parent)

    cmds.columnLayout(adj=1)

    cmds.rowLayout(numberOfColumns=2, columnWidth=[(1,125), (2,125)])
    cmds.columnLayout(adj=True)
    cmds.button(ann ='Select the vertices which is need to be converted.' ,
                l='Get Selected Vertices',
                h=40, w=125, c=getSelectedVertices)
    cmds.textScrollList('verticesTxtScrLs', allowMultiSelection=True, selectCommand=lambda : selectObjects('verticesTxtScrLs'), doubleClickCommand=lambda : selectAllObjects('verticesTxtScrLs'))

    cmds.setParent('..')
    cmds.columnLayout(adj=True)
    cmds.button(ann ='Select the drivers which deforms the selected vertices.\nIt can be CVs, points of a lattice, clusters, locators ...' ,
                l='Get Selected drivers',
                h=40, w=125, c=getSelectedDrivers)
    cmds.textScrollList('driversTxtScrLs', allowMultiSelection=True, selectCommand=lambda : selectObjects('driversTxtScrLs'), doubleClickCommand=lambda : selectAllObjects('driversTxtScrLs'))

    cmds.setParent('..')
    cmds.setParent('..')
    cmds.separator(h=10)
    cmds.button(ann ='Press the button to Convert. Note:- This will some time according to the number of vertex selected.' ,
                l='CONVERT',
                h=40, c=convert)

    cmds.window('convert2skinWin', e=1, s=0, w=50, h=50)
    cmds.showWindow('convert2skinWin')


def selectObjects(textScrollListWidget):
    selectedItems = cmds.textScrollList(textScrollListWidget, q=True, selectItem=True)
    cmds.select(selectedItems, r=True)


def selectAllObjects(textScrollListWidget):
    allItems = cmds.textScrollList(textScrollListWidget, q=True, allItems=True)
    cmds.select(allItems, r=True)
