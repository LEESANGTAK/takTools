#--------------------------------------------------------------------------------------------------------------
#	SCRIPT:	All_Deformer_2_SkinCluster
#	AUTHOR:	Praveen V, Sr.Rigging Artist, Paprikaas Animation Studio, Bangalore
#	E-Mail:	praveenact@yahoo.com
#
# This script can Convert all kind deformers into skincluster .
# The skinned weight result will be very much near to the deformer deformation.
#
# Use:  Run ---------> All_Deformer_2_SkinCluster
#---------------------------------------------------------------------------------------------------------------

#  Importing necessary module

import maya.cmds as cmds
import maya.mel as mel
import math

selVex = []
selCtr = []


# Procedure to get the selected vertexs information

def vp_selVex(*args):
    global selVex
    selVex = cmds.ls(sl=1,fl=1)
    #print selVex
    return selVex

# Procedure to get the selected controls information

def vp_selCtr(*args):
    global selCtr
    selCtr = cmds.ls(sl=1,fl=1)
    #print selCtr
    return selCtr

# This procedure will return name of the skincluster for selected object

def vp_SknFrmGeo (geo):
    skinCluster = []
    vertHistory = cmds.listHistory(geo, il=1, pdo=True)
    skinCluster = cmds.ls(vertHistory, type='skinCluster')
    if skinCluster:
        return skinCluster[0]

# Procedure to unhold the joints for selected object

def vp_holdAllJnt (skinCluster, onOff=0):
    influences = cmds.skinCluster (skinCluster, q=1, inf=1)
    for inf in influences:
        cmds.setAttr(inf + '.liw', onOff)

# Main Procedure which converts deformation information into skincluster weight information

def vp_w2sConvert(*args):
    Base_GeoNm = selVex[0].split('.')

    Base_GeoSkn = vp_SknFrmGeo(Base_GeoNm[0])
    #print Base_GeoSkn

    if(Base_GeoSkn == None):
        if cmds.objExists('vp_hold'):
            cmds.delete('vp_hold')
        cmds.select(cl=1)
        cmds.joint(n='vp_hold')
        cmds.select(Base_GeoNm[0],add=1)
        cmds.SmoothBindSkin()
        Base_GeoSkn = vp_SknFrmGeo(Base_GeoNm[0])

    vp_holdAllJnt(Base_GeoSkn, onOff=0)
    jntNam = []

    for i in range (0,len(selCtr)):
        cmds.select (cl=1)
        jntNam.append (cmds.joint(n=selCtr[i]+'_jnt'))
        tmp_grp = cmds.group (n=selCtr[i]+'_jnt_Grp')
        cmds.delete(cmds.parentConstraint(selCtr[i],tmp_grp))
        cmds.select(Base_GeoNm[0])
        cmds.skinCluster(e=1,dr=4,lw=0,wt=0,ai=jntNam[i])

    amount = 0
    amountPlus = 100/len(selCtr)

    cmds.progressWindow (title = 'Converting 2 Skin',
                progress = amount,
                status = 'Converting : 0%',
                isInterruptable = True)

    for i in range (0,len(selCtr)):
        for j in range (0,len(selVex)):

            if cmds.progressWindow(query=True, isCancelled=True):
                break

            originalPos = cmds.xform(selVex[j], q=1, wd=1, t=1)
            cmds.setAttr(selCtr[i] + '.tz', -1)

            deformPos = cmds.xform(selVex[j], q=1, wd=1, t=1)
            cmds.setAttr(selCtr[i] + '.tz', 0)

            difference = [ deformPos[0]-originalPos[0], deformPos[1]-originalPos[1], deformPos[2]-originalPos[2] ]
            wtValue = math.sqrt (pow(difference[0] ,2) + pow(difference[1] ,2) + pow(difference[2] ,2))

            cmds.skinPercent (Base_GeoSkn,selVex[j], nrm=1, tv=[jntNam[i],wtValue])

        if cmds.progressWindow(query=1, progress = 1) == len(selCtr):
            break

        amount += amountPlus
        cmds.progressWindow ( edit=1, progress=amount, status=('converted : ' + str(amount) + '%'))
        cmds.pause(seconds=1)

    cmds.progressWindow(endProgress=1)
    mel.eval('print "--------------> Converted";')


# The Main Window Procedure

def All_Deformer_2_SkinCluster():

    if cmds.window('wire2skinWin', exists=True):
        cmds.deleteUI('wire2skinWin',window=True)

    cmds.window('wire2skinWin',t='All_Deformer_2_Skin')

    cmds.columnLayout(adj=1)

    cmds.rowLayout(numberOfColumns=2,columnWidth=[(1,125),(2,125)])
    cmds.button(ann ='Select the vertexs which is need to be Converted' ,
                l='     Select The Vertexs',
                h=40,w=125,bgc=(1,0.424,0.343),c=vp_selVex)

    cmds.button(ann ='Select the Deformers which deforms the selected vertexs' ,
                l='     Select The Controls',
                h=40,w=125,bgc=(1,0.424,0.343),c=vp_selCtr)

    cmds.setParent('..')

    cmds.button(ann ='Press the button to Convert. Note:- This will some time according to the number of vertex selected ' ,
                l='-----------    CONVERT    ------------',
                h=40,bgc=(1,0.424,0.343),c=vp_w2sConvert)

    cmds.window('wire2skinWin',e=1,s=0,w=258,h=106)
    cmds.showWindow('wire2skinWin')

All_Deformer_2_SkinCluster()

