##--------------------------------------------------------------------------
##
## ScriptName : SpeedCut 
## Contents   : tool set for speed up maya boolean opeeration
## Author     : Joe Wu
## URL        : http://im3djoe.com
## Since      : 2019/08
## LastUpdate : 2019/08/17 First version for public test
## Version    : 1.0
## 
## Other Note : only test in maya 2018.5 windows enviroment 
##
## Install    : copy and paste script into a python tab in maya script editor
##--------------------------------------------------------------------------


import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as mc
import math
import maya.api.OpenMaya as OpenMaya
import pymel.core as pm
import maya.mel as mel


def preBevelToggle():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    if mc.objExists(beseMesh+'_preBevel'):
        mc.delete(beseMesh+'_preBevel')
        mc.setAttr((beseMesh+'BoolGrp.visibility'),1)
    else:
        preBevelRemoveSymmetry()
        
def preBevelRemoveSymmetry():
	beseMesh = mc.textField("setMeshField", q = True, text = True)
	mc.select(beseMesh+'_bool')
	newNode = mc.duplicate()
	mc.rename(newNode,beseMesh+'_preBevel')
	getSymX = 0
	getSymY = 0
	getSymZ = 0
	if mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
		getSymX =  mc.getAttr(beseMesh+'.symmetryX')
	if mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
		getSymY =  mc.getAttr(beseMesh+'.symmetryY')
	if mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
		getSymZ =  mc.getAttr(beseMesh+'.symmetryZ')  
	mc.setAttr((beseMesh+'BoolGrp.visibility'),0)
	mc.parent(beseMesh+'_preBevel',w=True)
	mc.setAttr((beseMesh+'_preBevel.visibility'),1)
	selPoly = (beseMesh+'_preBevel')

	if getSymX == 1:
		bboxObj = mc.xform(selPoly , q = True, ws =True, bb=True)
		lengthObj=math.sqrt((math.pow(bboxObj[0]-bboxObj[3],2)+math.pow(bboxObj[1]-bboxObj[4],2)+math.pow(bboxObj[2]-bboxObj[5],2))/3)
		closeRange = lengthObj / 100
		bboxSel = mc.xform(selPoly,q = True, ws =True, bb=True)
		midX = (bboxSel[3]+bboxSel[0])/2
		midY = (bboxSel[4]+bboxSel[1])/2
		midZ = (bboxSel[5]+bboxSel[2])/2
		inRangeCv = []
		vNo = mc.polyEvaluate(selPoly, v = True )
		checkPoint = 0
		for i in range(vNo):
			positionV = mc.pointPosition((selPoly +'.vtx[' + str(i) + ']') , w = True)
			length= math.sqrt(math.pow(positionV[checkPoint],2))
			if length <= closeRange:
			   inRangeCv.append((selPoly +'.vtx[' + str(i) + ']'))
		for n in inRangeCv:
			posiV = mc.pointPosition(n , w = True)
			if midX >= 0: 
				mc.move((closeRange * -1.5) , posiV[1], posiV[2], n ,absolute=1)   
			else:
				mc.move( (closeRange * 1.5) , posiV[1], posiV[2], n ,absolute=1) 
		cutPlane= mc.polyCut(selPoly, ws = True, cd = 'X' , df = True , ch =True)
		mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
		mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
		mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
		if midX > 0:
			mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 90) 
			mc.polyMirrorFace(selPoly,cutMesh =1, axis = 0, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
		else:
			mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), -90)
			mc.polyMirrorFace(selPoly,cutMesh =1, axis = 0, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)

	if getSymY == 1:
		bboxObj = mc.xform(selPoly , q = True, ws =True, bb=True)
		lengthObj=math.sqrt((math.pow(bboxObj[0]-bboxObj[3],2)+math.pow(bboxObj[1]-bboxObj[4],2)+math.pow(bboxObj[2]-bboxObj[5],2))/3)
		closeRange = lengthObj / 100
		bboxSel = mc.xform(selPoly,q = True, ws =True, bb=True)
		midX = (bboxSel[3]+bboxSel[0])/2
		midY = (bboxSel[4]+bboxSel[1])/2
		midZ = (bboxSel[5]+bboxSel[2])/2
		inRangeCv = []
		vNo = mc.polyEvaluate(selPoly, v = True )
		checkPoint = 1
		for i in range(vNo):
			positionV = mc.pointPosition((selPoly +'.vtx[' + str(i) + ']') , w = True)
			length= math.sqrt(math.pow(positionV[checkPoint],2))
			if length <= closeRange:
			   inRangeCv.append((selPoly +'.vtx[' + str(i) + ']'))
		for n in inRangeCv:
				posiV = mc.pointPosition(n , w = True)
				if midY >= 0: 
					mc.move(posiV[0], (closeRange  * -1.5) , posiV[2], n ,absolute=1)   
				else:
					mc.move(posiV[0], (closeRange  * 1.5) , posiV[2], n ,absolute=1)   
		cutPlane= mc.polyCut(selPoly, ws = True, cd = 'Y' , df = True , ch =True)
		mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
		mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
		mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
		if midY > 0:
			mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'), -90) 
			mc.polyMirrorFace(selPoly,cutMesh =1, axis = 1, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
		else:
			mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'), 90)
			mc.polyMirrorFace(selPoly,cutMesh =1, axis = 1, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)


	if getSymZ == 1:
		bboxObj = mc.xform(selPoly , q = True, ws =True, bb=True)
		lengthObj=math.sqrt((math.pow(bboxObj[0]-bboxObj[3],2)+math.pow(bboxObj[1]-bboxObj[4],2)+math.pow(bboxObj[2]-bboxObj[5],2))/3)
		closeRange = lengthObj / 100
		bboxSel = mc.xform(selPoly,q = True, ws =True, bb=True)
		midX = (bboxSel[3]+bboxSel[0])/2
		midY = (bboxSel[4]+bboxSel[1])/2
		midZ = (bboxSel[5]+bboxSel[2])/2
		inRangeCv = []
		vNo = mc.polyEvaluate(selPoly, v = True )
		checkPoint = 2
		for i in range(vNo):
			positionV = mc.pointPosition((selPoly +'.vtx[' + str(i) + ']') , w = True)
			length= math.sqrt(math.pow(positionV[checkPoint],2))
			if length <= closeRange:
			   inRangeCv.append((selPoly +'.vtx[' + str(i) + ']'))
		for n in inRangeCv:
			posiV = mc.pointPosition(n , w = True)
			if midZ >= 0: 
				mc.move(posiV[0], posiV[1],(closeRange  * -1.5), n ,absolute=1)   
			else:
				mc.move(posiV[0], posiV[1],(closeRange  * 1.5), n ,absolute=1)   
		cutPlane= mc.polyCut(selPoly, ws = True, cd = 'Z' , df = True , ch =True)
		mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
		mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
		mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
		if midZ > 0:
			mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 0) 
			mc.polyMirrorFace(selPoly,cutMesh =1, axis = 2, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
		else:
			mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 180)
			mc.polyMirrorFace(selPoly,cutMesh =1, axis = 2, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
	mc.select(selPoly)
	mc.BakeNonDefHistory()
	bevelPreviewAdd()
	
		
def bevelPreviewAdd():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    member = beseMesh + '_preBevel'
    mc.select(member)
    #Clean
    softNode = mc.polySoftEdge(angle=0.3)
    mc.rename(softNode,(beseMesh+'_bevelPreviewPolyEdgeSoft'))
    mel.eval("ConvertSelectionToEdges;")
    mc.polySelectConstraint(t=0x8000, m=3, sm=2)
    mc.polySelectConstraint(disable =True)
    selectEdges=mc.ls(sl=1,fl=1)
    if len(selectEdges)>0:
        mel.eval("doDelete;")
    mc.select(member)
    softNode = mc.polySoftEdge(angle=30)
    mc.rename(softNode,(beseMesh+'_bevelPreviewPolyEdgeHard'))
    mc.select(member)
    #Retop
    mc.polySelectConstraint(m=3,t=0x8000,sm=1)
    mc.polySelectConstraint(disable =True)
    triNode = mc.polyTriangulate(member,ch=0) 
    mc.rename(triNode,(beseMesh+'_bevelPreviewPolyTriangulate'))
    quadNode = mc.polyQuad(member,a = 30, kgb = 0 ,ktb = 0, khe= 1, ws = 0, ch = 0)
    mc.rename(quadNode,(beseMesh+'_bevelPreviewPolyQuad'))
    mc.select(member)
    #Bevel
    mc.polySelectConstraint(m=3,t=0x8000,sm=1)
    mc.polySelectConstraint(disable =True)
    hardEdges = mc.ls(sl=1,fl=1)
    mc.DetachComponent()
    mc.select(member)
    mc.ConvertSelectionToFaces()
    sourceFaces = mc.ls(sl=1,fl=1)
    offsetData = mc.floatSliderGrp('offsetSliderPre', q=1, v = 1)
    createSupportNode = mc.polyExtrudeFacet(sourceFaces, constructionHistory =1, keepFacesTogether = 1, divisions = 1, off = offsetData, smoothingAngle = 30)
    faceLockNode = mc.rename(createSupportNode[0], (beseMesh+'_lcokFace'))
    mc.GrowPolygonSelectionRegion()
    shapeExtrude = mc.ls(sl=1,fl=1)
    mc.select(member)
    mc.ConvertSelectionToFaces()
    mc.select(shapeExtrude,d=1 )
    mc.delete()
    mc.select(member)
    mc.polyMergeVertex(d = 0.001, ch = 1)
    mc.setAttr((faceLockNode + ".offset"), offsetData)
    mc.connectControl('offsetSliderPre', (faceLockNode + ".offset")) 
    mc.polySelectConstraint(m=3,t=0x8000,sm=1)
    mc.polySelectConstraint(disable =True)
    softNode = mc.polySoftEdge(angle= 180)
    mc.select(cl=True)


def onPressDraw():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    member =mc.editDisplayLayerMembers((beseMesh+'_BoolResult'),q=True)
    snapMesh = (beseMesh +'_boolShape')
    vpX, vpY, _ = mc.draggerContext('meshPlace', query=True, anchorPoint=True)
    #print(vpX, vpY)
    pos = om.MPoint()
    dir = om.MVector()
    hitpoint = om.MFloatPoint()
    omui.M3dView().active3dView().viewToWorld(int(vpX), int(vpY), pos, dir)
    pos2 = om.MFloatPoint(pos.x, pos.y, pos.z)
    shortestD = 99999999999999999
    getMesh = []
    shortPosition= []
    mesh = snapMesh
    selectionList = om.MSelectionList()
    selectionList.add(snapMesh)
    dagPath = om.MDagPath()
    selectionList.getDagPath(0, dagPath)
    fnMesh = om.MFnMesh(dagPath)
    intersection = fnMesh.closestIntersection(
    om.MFloatPoint(pos2),
    om.MFloatVector(dir),
    None,
    None,
    False,
    om.MSpace.kWorld,
    99999,
    False,
    None,
    hitpoint,
    None,
    None,
    None,
    None,
    None)
    if intersection:
        x = hitpoint.x
        y = hitpoint.y
        z = hitpoint.z
        newName = mc.listRelatives(mesh, p=True )
        #intersection on closet obj, for multi intersections remove distrance check
        distanceBetween = math.sqrt(  ((float(pos2[0]) - hitpoint.x)**2)  + ((float(pos2[1]) - hitpoint.y)**2) + ((float(pos2[2]) - hitpoint.z)**2))
        if (shortestD > distanceBetween):
            shortestD = distanceBetween
            getMesh = newName
            shortPosition = [x, y, z]
    if len(shortPosition) > 0:
        mc.spaceLocator(p=(shortPosition[0],shortPosition[1],shortPosition[2]),n = (getMesh[0]+'_cutterPoint'))


def offPressDraw():
    pointPos = mc.ls(sl=True,fl=True)
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    boolNode = mc.listConnections(mc.listHistory((beseMesh+'_bool'),f=1),type='polyCBoolOp')
    member =mc.editDisplayLayerMembers((beseMesh+'_BoolResult'),q=True)
    snapMesh =[]
    if member != None:
        snapMesh = member[0]
    mc.setToolTo('moveSuperContext')
    snapObj=snapMesh
    mc.CenterPivot()
    mc.geometryConstraint( snapObj , pointPos[0], weight = 1)
    mc.normalConstraint( snapObj , pointPos[0], aimVector =(0, 1, 0) , upVector =(1, 0, 0))
    mc.intSliderGrp('snapGirdSize',e=1, en=1)
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    gridData=  mc.intSliderGrp('snapGirdSize', q = True, v =True)
    mesh = (beseMesh +'_bool')
    bbox= mc.xform(mesh, q=1, ws=1, bb=1)
    length=math.sqrt((math.pow(bbox[0]-bbox[3],2)+math.pow(bbox[1]-bbox[4],2)+math.pow(bbox[2]-bbox[5],2))/3)
    length = int(length *1.1 )
    meshCOORD = mc.objectCenter(mesh,gl=True)
    constructionPlanePos=[]
    meshCOORD = mc.objectCenter(pointPos[0],gl=True)
    if mc.objExists('lineDrawPlane'):
        mc.delete('lineDrawPlane')
    if mc.objExists('drawPlaneGrp'):
        mc.delete('drawPlaneGrp')
    mc.plane(s=length, r=[90,0,0])
    mc.rename('lineDrawPlane')
    mc.group('lineDrawPlane')
    mc.rename('drawPlaneGrp')
    mc.select(pointPos,add=True)
    mc.MatchTransform()
    mc.setAttr("lineDrawPlane.translateY", 0.1)
    mc.delete(pointPos)
    mc.makeLive('lineDrawPlane')
    mc.snapMode(grid=1)
    resizeSnapGrid()
    mc.CVCurveTool()
    mc.curveCVCtx(mc.currentCtx(), e=True, d=1, bez= 0) 
    mc.connectControl('snapGirdRot', 'lineDrawPlane.rotateY')
    
def goPressDraw():
    ctx = 'meshPlace'
    if mc.draggerContext(ctx, exists=True):
        mc.deleteUI(ctx)
    mc.draggerContext(ctx, pressCommand = onPressDraw, rc = offPressDraw, name=ctx, cursor='crossHair')
    mc.setToolTo(ctx)

def goDraw():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    snapMesh = beseMesh + '_bool'
    mc.optionVar(iv = ('inViewMessageEnable', 0))
    mc.makeLive(snapMesh) 
    xrayOn()
    mc.evalDeferred('drawBoxRun()')


def drawBoxRun():
    mc.setToolTo( "CreatePolyCubeCtx" )
    mc.scriptJob ( runOnce=True, event = ["PostToolChanged", xrayOff])
        
       
def xrayOn():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    snapMesh = beseMesh + '_bool'
    mc.displaySurface(snapMesh , x =1)

def xrayOff():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    snapMesh = beseMesh + '_bool'
    mc.displaySurface(snapMesh , x =0)
    mc.makeLive( none=True )
    newCut = mc.ls(sl=1,tr=1)
    mc.select(newCut, r=1)
    mc.evalDeferred('useOwnCutterShape()')
    newCut = mc.ls(sl=1,tr=1)
    mc.setAttr((newCut[0]+".scaleX") ,1.01)
    mc.setAttr((newCut[0]+".scaleY") ,1.01)
    mc.setAttr((newCut[0]+".scaleZ") ,1.01)
  

def boolSymmetryFreeze():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    bakeCutter()
    
    if mc.objExists((beseMesh +'_mirrorGrp')) == 1:
        mc.delete((beseMesh +'_mirrorGrp'))

    selPoly = beseMesh
    getSymX = 0
    getSymY = 0
    getSymZ = 0
    if mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        getSymX =  mc.getAttr(beseMesh+'.symmetryX')
    if mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        getSymY =  mc.getAttr(beseMesh+'.symmetryY')
    if mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        getSymZ =  mc.getAttr(beseMesh+'.symmetryZ')  
    mc.setAttr((selPoly+'.visibility'),1)
    if getSymX == 1:
        bboxObj = mc.xform(selPoly , q = True, ws =True, bb=True)
        lengthObj=math.sqrt((math.pow(bboxObj[0]-bboxObj[3],2)+math.pow(bboxObj[1]-bboxObj[4],2)+math.pow(bboxObj[2]-bboxObj[5],2))/3)
        closeRange = lengthObj / 100
        bboxSel = mc.xform(selPoly,q = True, ws =True, bb=True)
        midX = (bboxSel[3]+bboxSel[0])/2
        midY = (bboxSel[4]+bboxSel[1])/2
        midZ = (bboxSel[5]+bboxSel[2])/2
        inRangeCv = []
        vNo = mc.polyEvaluate(selPoly, v = True )
        checkPoint = 0
        mc.setAttr((selPoly+'.symmetryX'),1)
        for i in range(vNo):
            positionV = mc.pointPosition((selPoly +'.vtx[' + str(i) + ']') , w = True)
            length= math.sqrt(math.pow(positionV[checkPoint],2))
            if length <= closeRange:
               inRangeCv.append((selPoly +'.vtx[' + str(i) + ']'))
        for n in inRangeCv:
            posiV = mc.pointPosition(n , w = True)
            if midX >= 0: 
                mc.move((closeRange * -1.5) , posiV[1], posiV[2], n ,absolute=1)   
            else:
                mc.move( (closeRange * 1.5) , posiV[1], posiV[2], n ,absolute=1) 
        cutPlane= mc.polyCut(selPoly, ws = True, cd = 'X' , df = True , ch =True)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
        if midX > 0:
            mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 90) 
            mc.polyMirrorFace(selPoly,cutMesh =1, axis = 0, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
        else:
            mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), -90)
            mc.polyMirrorFace(selPoly,cutMesh =1, axis = 0, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
    
    if getSymY == 1:
        bboxObj = mc.xform(selPoly , q = True, ws =True, bb=True)
        lengthObj=math.sqrt((math.pow(bboxObj[0]-bboxObj[3],2)+math.pow(bboxObj[1]-bboxObj[4],2)+math.pow(bboxObj[2]-bboxObj[5],2))/3)
        closeRange = lengthObj / 100
        bboxSel = mc.xform(selPoly,q = True, ws =True, bb=True)
        midX = (bboxSel[3]+bboxSel[0])/2
        midY = (bboxSel[4]+bboxSel[1])/2
        midZ = (bboxSel[5]+bboxSel[2])/2
        inRangeCv = []
        vNo = mc.polyEvaluate(selPoly, v = True )
        checkPoint = 1
        for i in range(vNo):
            positionV = mc.pointPosition((selPoly +'.vtx[' + str(i) + ']') , w = True)
            length= math.sqrt(math.pow(positionV[checkPoint],2))
            if length <= closeRange:
               inRangeCv.append((selPoly +'.vtx[' + str(i) + ']'))
        for n in inRangeCv:
                posiV = mc.pointPosition(n , w = True)
                if midY >= 0: 
                    mc.move(posiV[0], (closeRange  * -1.5) , posiV[2], n ,absolute=1)   
                else:
                    mc.move(posiV[0], (closeRange  * 1.5) , posiV[2], n ,absolute=1)   
        cutPlane= mc.polyCut(selPoly, ws = True, cd = 'Y' , df = True , ch =True)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
        if midY > 0:
            mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'), -90) 
            mc.polyMirrorFace(selPoly,cutMesh =1, axis = 1, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
        else:
            mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'), 90)
            mc.polyMirrorFace(selPoly,cutMesh =1, axis = 1, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
    
    
    if getSymZ == 1:
        bboxObj = mc.xform(selPoly , q = True, ws =True, bb=True)
        lengthObj=math.sqrt((math.pow(bboxObj[0]-bboxObj[3],2)+math.pow(bboxObj[1]-bboxObj[4],2)+math.pow(bboxObj[2]-bboxObj[5],2))/3)
        closeRange = lengthObj / 100
        bboxSel = mc.xform(selPoly,q = True, ws =True, bb=True)
        midX = (bboxSel[3]+bboxSel[0])/2
        midY = (bboxSel[4]+bboxSel[1])/2
        midZ = (bboxSel[5]+bboxSel[2])/2
        inRangeCv = []
        vNo = mc.polyEvaluate(selPoly, v = True )
        checkPoint = 2
        for i in range(vNo):
            positionV = mc.pointPosition((selPoly +'.vtx[' + str(i) + ']') , w = True)
            length= math.sqrt(math.pow(positionV[checkPoint],2))
            if length <= closeRange:
               inRangeCv.append((selPoly +'.vtx[' + str(i) + ']'))
        for n in inRangeCv:
            posiV = mc.pointPosition(n , w = True)
            if midZ >= 0: 
                mc.move(posiV[0], posiV[1],(closeRange  * -1.5), n ,absolute=1)   
            else:
                mc.move(posiV[0], posiV[1],(closeRange  * 1.5), n ,absolute=1)   
        cutPlane= mc.polyCut(selPoly, ws = True, cd = 'Z' , df = True , ch =True)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
        mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
        if midZ > 0:
            mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 0) 
            mc.polyMirrorFace(selPoly,cutMesh =1, axis = 2, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
        else:
            mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 180)
            mc.polyMirrorFace(selPoly,cutMesh =1, axis = 2, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
    mc.select(selPoly)
    mc.BakeNonDefHistory()
    mc.setAttr((selPoly+'.visibility'),0)
    mc.setAttr((selPoly+'.symmetryX'),0)
    mc.setAttr((selPoly+'.symmetryY'),0)
    mc.setAttr((selPoly+'.symmetryZ'),0)

def boolSymmetryCut(axis):
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    selPoly = beseMesh
    checkState = mc.radioButtonGrp('symDirButton',q=True, sl = True)
       
    if not mc.attributeQuery('symmetryX', node = selPoly, ex=True ):
        mc.addAttr(selPoly, ln='symmetryX', at = "long" )
        mc.setAttr((selPoly+'.symmetryX'),0)
    if not mc.attributeQuery('symmetryY', node = selPoly, ex=True ):
        mc.addAttr(selPoly, ln='symmetryY', at = "long" )
        mc.setAttr((selPoly+'.symmetryY'),0)
    if not mc.attributeQuery('symmetryZ', node = selPoly, ex=True ):
        mc.addAttr(selPoly, ln='symmetryZ', at = "long" )
        mc.setAttr((selPoly+'.symmetryZ'),0)
    #get selected bbox
    bboxObj = mc.xform(selPoly , q = True, ws =True, bb=True)
    lengthObj=math.sqrt((math.pow(bboxObj[0]-bboxObj[3],2)+math.pow(bboxObj[1]-bboxObj[4],2)+math.pow(bboxObj[2]-bboxObj[5],2))/3)
    closeRange = lengthObj / 100
    bboxSel = mc.xform(selPoly,q = True, ws =True, bb=True)
    midX = (bboxSel[3]+bboxSel[0])/2
    midY = (bboxSel[4]+bboxSel[1])/2
    midZ = (bboxSel[5]+bboxSel[2])/2
    inRangeCv = []
    vNo = mc.polyEvaluate(selPoly, v = True )
    checkPoint = 0
    if axis == 'x' :
        checkPoint = 0
        mc.setAttr((selPoly+'.symmetryX'),1)

    elif axis == 'y' :
        checkPoint = 1
        mc.setAttr((selPoly+'.symmetryY'),1)

    else:
        checkPoint = 2
        mc.setAttr((selPoly+'.symmetryZ'),1)

    for i in range(vNo):
        positionV = mc.pointPosition((selPoly +'.vtx[' + str(i) + ']') , w = True)
        length= math.sqrt(math.pow(positionV[checkPoint],2))
        if length <= closeRange:
           inRangeCv.append((selPoly +'.vtx[' + str(i) + ']'))
        mc.select(inRangeCv, r=True)
    
    # push those point off center a bit then mirror cut
    if axis == 'x' :
        for n in inRangeCv:
            posiV = mc.pointPosition(n , w = True)
            if checkState == 1:
                mc.move((closeRange * -1.5) , posiV[1], posiV[2], n ,absolute=1)   
            else:
                mc.move( (closeRange * 1.5) , posiV[1], posiV[2], n ,absolute=1) 
        cutPlane= mc.polyCut(selPoly, ws = True, cd = 'X' , df = True , ch =True)
        if checkState == 2:
            mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'),-90)
    
    if axis == 'y' :
        for n in inRangeCv:
            posiV = mc.pointPosition(n , w = True)
            if midY >= 0: 
                mc.move(posiV[0], (closeRange  * -1.5) , posiV[2], n ,absolute=1)   
            else:
                mc.move(posiV[0], (closeRange  * 1.5) , posiV[2], n ,absolute=1)   
        cutPlane= mc.polyCut(selPoly, ws = True, cd = 'Y' , df = True , ch =True)
        if checkState == 2:
            mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'),90)
    
    if axis == 'z' :
        for n in inRangeCv:
            posiV = mc.pointPosition(n , w = True)
            if midZ >= 0: 
                mc.move(posiV[0], posiV[1],(closeRange  * -1.5), n ,absolute=1)   
            else:
                mc.move(posiV[0], posiV[1],(closeRange  * 1.5), n ,absolute=1)   
        cutPlane= mc.polyCut(selPoly, ws = True, cd = 'Z' , df = True , ch =True)
        if checkState == 2:
            mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'),180)
    
    mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
    mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
    mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
    mc.select(selPoly)
    mc.FillHole()
    boolSymmetryRestore()
    
def boolSymmetryRestore():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    selPoly = beseMesh
    
    if mc.objExists((beseMesh +'_mirrorGrp')) == 1:
        mc.delete((beseMesh +'_mirrorGrp'))
        
    mc.CreateEmptyGroup()
    mc.rename((beseMesh +'_mirrorGrp'))
    mc.parent((beseMesh +'_mirrorGrp'),(beseMesh +'BoolGrp'))
    
    
    checkSX = mc.getAttr(selPoly+'.symmetryX')
    if checkSX == 1:
        mc.select(selPoly+'_bool*')
        newMesh = mc.ls(sl=1,fl=1,tr =1)
        mc.select(newMesh)
        mc.instance()
        newMesh = mc.ls(sl=1,fl=1,tr =1)
        for n in newMesh:
            mc.xform(n, ws = 1, piv =[0, 0, 0])
            mc.setAttr((n+'.scaleX'),-1)
            parentNode = mc.listRelatives(n, allParents=True )
            if parentNode[0] != (beseMesh +'_mirrorGrp'):
                mc.parent(n,(beseMesh +'_mirrorGrp'))
    
    checkSY = mc.getAttr(selPoly+'.symmetryY')
    if checkSY == 1:
        mc.select(selPoly+'_bool*')
        newMesh = mc.ls(sl=1,fl=1,tr =1)
        mc.select(newMesh)
        mc.instance()
        newMesh = mc.ls(sl=1,fl=1,tr =1)
        for n in newMesh:
            mc.xform(n, ws = 1, piv =[0, 0, 0])
            mc.setAttr((n+'.scaleY'),-1)
            parentNode = mc.listRelatives(n, allParents=True )
            if parentNode[0] != (beseMesh +'_mirrorGrp'):
                mc.parent(n,(beseMesh +'_mirrorGrp'))
    
            
    checkSZ = mc.getAttr(selPoly+'.symmetryZ')
    if checkSZ == 1:
        mc.select(selPoly+'_bool*')
        newMesh = mc.ls(sl=1,fl=1,tr =1)
        mc.select(newMesh)
        mc.instance()
        newMesh = mc.ls(sl=1,fl=1,tr =1)
        for n in newMesh:
            mc.xform(n, ws = 1, piv =[0, 0, 0])
            mc.setAttr((n+'.scaleZ'),-1)
            parentNode = mc.listRelatives(n, allParents=True )
            if parentNode[0] != (beseMesh +'_mirrorGrp'):
                mc.parent(n,(beseMesh +'_mirrorGrp'))
    
    mc.select(cl=1)
    
    
def alignCutterToBase():
    my = mc.ls(sl=True,fl=True)
    bboxMy= mc.xform(my[0], q=1, ws=1, bb=1)
    cenmyList = [((bboxMy[3] + bboxMy[0] ) /2),((bboxMy[4] + bboxMy[1] ) /2),((bboxMy[5] + bboxMy[2] ) /2)]
    movList = []
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    bbox= mc.xform((beseMesh +'_bool'), q=1, ws=1, bb=1)
    
    for i in range(3):
        movX =[]
        minX = bbox[i] 
        cenX =(bbox[i+3] + bbox[i] ) /2
        maxX = bbox[i+3] 
        length= math.sqrt(math.pow(bbox[i]-bbox[i+3],2))
        quarXDis = length /6
        startX = []
        endX  = []
        if minX > maxX:
            startX = maxX + quarXDis
            endX = minX - quarXDis
        else:
            startX = minX + quarXDis
            endX = maxX - quarXDis
        
        if cenmyList[i] >= startX and cenmyList[i] <= endX:
            movX = cenX
        
        elif cenmyList[i] < startX:
            movX = minX
        else:
            movX = maxX
        movList.append(movX)
         
    mc.move(movList[0],movList[1],movList[2],absolute=1)   

def combineSelCutters():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    selList = mc.ls(sl=True,fl=True)
    if len(selList) > 1:
        #bake array 
        for s in selList:
            if mc.objExists(s):
                mc.select(s)
                myType = checkInstType()
                if myType[1] != 'new':
                    instBake()
                    newNode = mc.ls(sl=1,fl=1)
                    selList.append(newNode[0])
    #bug, some transform node does not kill after boolean
        while len(selList) > 1:
            mc.polyCBoolOp(selList[0], selList[1], op=1, ch=1, preserveColor=0, classification=1, name=selList[0])
            mc.DeleteHistory()
            if mc.objExists(selList[1]):
                mc.delete(selList[1])
            mc.rename(selList[0])
            selList.remove(selList[1])
        newCutter = mc.ls(sl=1,fl=1)
        if mc.objExists((beseMesh +'_cutterGrp')) == 0:
            mc.CreateEmptyGroup()
            mc.rename((beseMesh +'_cutterGrp'))
            mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))          
        mc.parent(newCutter,(beseMesh +'_cutterGrp'))
        if not mc.attributeQuery('cutterDir', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='cutterDir',  dt= 'string')
        if not mc.attributeQuery('cutterType', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='cutterType',  dt= 'string')
        mc.setAttr((newCutter[0]+'.cutterDir'),e=True, keyable=True)
        mc.setAttr((newCutter[0]+'.cutterType'),e=True, keyable=True)
        mc.setAttr((newCutter[0]+'.cutterDir'),'x',type="string")
        mc.setAttr((newCutter[0]+'.cutterType'),'custom',type="string")
        
        if not mc.attributeQuery('cutterOp', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='cutterOp',  dt= 'string')
        mc.setAttr((newCutter[0]+'.cutterOp'),e=True, keyable=True)
        mc.setAttr((newCutter[0]+'.cutterOp'),'subs',type="string")
        
        if not mc.attributeQuery('statePanel', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='statePanel', at = "float" )
        if not mc.attributeQuery('panelGap', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='panelGap', at = "float" )
        if not mc.attributeQuery('intPanelGap', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='intPanelGap', at = "float" )
        if not mc.attributeQuery('intScaleX', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='intScaleX', at = "float" )
        if not mc.attributeQuery('stateCap', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='stateCap', at = "float" )
        mc.setAttr((newCutter[0]+'.stateCap'),1)
        mc.setAttr((newCutter[0]+'.statePanel'),0)
        fixBoolNodeConnection()
        shapeNode = mc.listRelatives(newCutter[0], s=True )
        mc.setAttr((shapeNode[0]+'.overrideEnabled'), 1)
        mc.setAttr((shapeNode[0]+'.overrideShading'), 0)
        mc.setAttr((shapeNode[0]+'.overrideColor'), 28)
        mc.select(selList)
    else:
        print 'need more then one cutter!'
    
def recreateBool():
#recreate bool
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    if mc.objExists(beseMesh +'_preBoolBox'):
        mc.delete(beseMesh +'_preBoolBox')
    
    mc.polyCube(w = 0.01, h=0.01, d=0.01 ,sx =1 ,sy= 1, sz= 1)
    mc.rename(beseMesh +'_preBoolBox') 
    mc.polyCBoolOp(beseMesh, (beseMesh +'_preBoolBox') , op= 2, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_bool')) 
        
    boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
    if (boolNode[0] != (beseMesh +'_myBool')):
        mc.rename(boolNode[0],(beseMesh +'_myBool'))
    mc.setAttr((beseMesh + '.visibility'), 0)
    baseShapeNode = mc.listRelatives(beseMesh, f = True)
    
    mc.parent(baseShapeNode,(beseMesh +'BoolGrp'))
    mc.delete(beseMesh)
    mc.rename(beseMesh)
    fullName = mc.ls(sl=True,l=True)
    baseShapeNode = mc.listRelatives(fullName[0], f = True)
    mc.rename(baseShapeNode[0],(beseMesh+'Shape'))
    
    mc.setAttr((beseMesh+'Shape.intermediateObject'), 0)
    mc.setAttr((beseMesh + '.visibility'), 0)
    mc.parent((beseMesh +'_bool'),(beseMesh +'BoolGrp'))
    
    mc.editDisplayLayerMembers( (beseMesh +'_BoolResult'),(beseMesh +'_bool')) # store my selection into the display layer
    mc.setAttr((beseMesh +'_BoolResult.displayType'),2)  
    
def restoreCutter():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    if mc.objExists(beseMesh +'_bakeBaseMesh'):  
        bakeCutter()
    mc.delete(beseMesh+'_bool')   
    mc.delete(beseMesh) 
    mc.parent((beseMesh +'_bakeBaseMesh'),  (beseMesh+'BoolGrp'))
    mc.rename((beseMesh +'_bakeBaseMesh'), beseMesh) 
    baseShape = mc.listRelatives((beseMesh), shapes=True,f=True)
    mc.setAttr((baseShape[0] + '.overrideShading'), 1)
    
    #recreate bool
    recreateBool()
        
    #restore cutters
    mc.select((beseMesh+'_bakeStep'), hi=True)
    mc.select((beseMesh+'_bakeStep'),d=True)
    restoreCutter = mc.ls(sl=1,fl=1,type='transform')
    for r in restoreCutter:
        shapeNode = mc.listRelatives(r, f = True, shapes=True)
        mc.setAttr( (shapeNode[0]+".overrideEnabled") , 1)
        mc.setAttr( (shapeNode[0]+".overrideShading") , 0)
        mc.setAttr( (shapeNode[0]+".castsShadows") , 0)
        mc.setAttr( (shapeNode[0]+".receiveShadows") , 0)
        mc.setAttr( (shapeNode[0]+".primaryVisibility") , 0)
        mc.setAttr( (shapeNode[0]+".visibleInReflections") , 0)
        mc.setAttr( (shapeNode[0]+".visibleInRefractions") , 0)
        mc.select(r)
        fixBoolNodeConnection()
        
        mc.rename(r , r.replace("bake", "box"))
    if mc.objExists((beseMesh +'_cutterGrp')):
        mc.delete(beseMesh +'_cutterGrp')
            
    mc.rename((beseMesh +'_bakeStep'),(beseMesh +'_cutterGrp'))
    getCutters = mc.ls((beseMesh+'_cutterGrp|boxCutter*'),type = 'transform')
    mc.hide(getCutters)
    if len(getCutters)>0:
        mc.select(getCutters[-1])
        mc.showHidden(getCutters[-1])
    showAllCutter()

   

def bakeUnselectCutter():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    
    #store any symmtry
    getSymX = 0
    getSymY = 0
    getSymZ = 0
    if mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        getSymX =  mc.getAttr(beseMesh+'.symmetryX')
    if mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        getSymY =  mc.getAttr(beseMesh+'.symmetryY')
    if mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        getSymZ =  mc.getAttr(beseMesh+'.symmetryZ')  
    
    selectedCutter = mc.ls(sl=1,fl=1)
    #flatten all cutters
    flattenAlllCutter()
    #getList after flattern
    cleanList = []
    for s in selectedCutter:
        if 'ArrayGrp' in s:
            s = s.replace("ArrayGrp", "")
        if mc.objExists(s.split('|')[-1]):
            cleanList.append(s.split('|')[-1])
    mc.select(cleanList)
    
    #disconnect from bool
    for c in cleanList:
        shapeNode = mc.listRelatives(c, f = True, shapes=True)
        if len(shapeNode)>0:
            listConnect = mc.connectionInfo((shapeNode[0]+'.outMesh'), dfs=True )
            if len(listConnect)>0:
                for a in listConnect:
                    mc.disconnectAttr((shapeNode[0]+'.outMesh'), a)
             
            listConnectMa = mc.connectionInfo((shapeNode[0]+'.worldMatrix[0]'), dfs=True )
            if len(listConnectMa)>0:
                for b in listConnectMa:
                    mc.disconnectAttr((shapeNode[0]+'.worldMatrix[0]'), b)
          
    
    # move to temp grp
    if mc.objExists((beseMesh +'_tempStoreGrp')) == 0:
        mc.CreateEmptyGroup()
        mc.rename((beseMesh +'_tempStoreGrp'))
        mc.parent((beseMesh +'_tempStoreGrp'), (beseMesh+'BoolGrp'))
        
    mc.parent(cleanList , (beseMesh +'_tempStoreGrp'))
    
    #step up
    #make bool mesh as new base mesh
    newMesh = mc.duplicate((beseMesh+'_bool'),rr=1)
    mc.delete(beseMesh+'_bool')
    #create Step up Group
    if mc.objExists((beseMesh +'_bakeStep')) == 0:
        mc.CreateEmptyGroup()
        mc.rename((beseMesh +'_bakeStep'))
        mc.parent((beseMesh +'_bakeStep'), (beseMesh+'BoolGrp'))
    mc.setAttr((beseMesh +'_bakeStep.visibility'),0)
        
        
    if mc.objExists((beseMesh +'_bakeBaseMesh')) ==0:    
        #bake base mesh 
        bakeMesh = mc.duplicate(beseMesh, rr=1)
        mc.delete(beseMesh)
        mc.parent(bakeMesh,(beseMesh +'_bakeStep'))
        mc.rename(bakeMesh,(beseMesh +'_bakeBaseMesh'))
        bakeShape = mc.listRelatives((beseMesh +'_bakeBaseMesh'), shapes=True,f=True)
        mc.setAttr((bakeShape[0] + '.overrideShading'), 1)
        mc.rename(newMesh,beseMesh)
    else:
        mc.delete(beseMesh)
        mc.rename(newMesh,beseMesh)
           
    if mc.objExists(beseMesh +'_myBool'):
        mc.delete(beseMesh+'_myBool')
    #reNumber
    mc.select((beseMesh+'_bakeStep'), hi=True)
    mc.select((beseMesh+'_bakeStep'),(beseMesh +'_bakeBaseMesh'),d=True)
    existCutterList = mc.ls(sl=1,fl=1,type='transform')
    
    #start rename old cutters
    mc.select((beseMesh+'_cutterGrp'), hi=True)
    mc.select((beseMesh+'_cutterGrp'),d=True)
    oldCutterList = mc.ls(sl=1,fl=1,type='transform')
    
    initalIndex = len(existCutterList) + 1
    for o in oldCutterList:
        newName = ('bakeCutter' + str(initalIndex))
        mc.rename(o, newName)
        initalIndex += 1
    newList= mc.ls(sl=1,fl=1,type='transform')
    if len(newList)>0:
        mc.parent(newList,(beseMesh +'_bakeStep'))
                
    #unlock connection
    shape = mc.listRelatives(beseMesh, shapes=True,f=True)
    checkConnection = mc.listConnections((shape[0]+'.drawOverride'),c=1,p=1)
    if checkConnection != None:
        mc.disconnectAttr(checkConnection[1],checkConnection[0])
        
    #recreate bool
    recreateBool()
    
    checkPreBoolGrp = mc.ls((beseMesh +'_preBoolBox'), l=True)
    
    if 'BoolGrp' not in checkPreBoolGrp[0]:
        mc.parent(checkPreBoolGrp[0],(beseMesh +'BoolGrp'))
    
    shapeNode = mc.listRelatives((beseMesh+'Shape'), s=True )
    if shapeNode != None:
        if len(shapeNode)>0:
            mc.setAttr((shapeNode[0]+'.intermediateObject'), 0)
            mc.parent((beseMesh+'Shape'),(beseMesh +'BoolGrp'))
            mc.delete(beseMesh)
            mc.rename(beseMesh)
    
    #reconnect selected Cutters
    newCutterList = []
    for c in cleanList:
        mc.select(c)
        fixBoolNodeConnection()
        newC = mc.ls(sl=1)
        newCutterList.append(newC[0])
     
    mc.parent(newCutterList , (beseMesh +'_cutterGrp'))
    if mc.objExists((beseMesh +'_tempStoreGrp')): 
        mc.delete((beseMesh +'_tempStoreGrp'))
    #rebuild symmtry 
    
    if not mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryX', at = "long" )
    mc.setAttr((beseMesh+'.symmetryX'),getSymX)
    if not mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryY', at = "long" )
    mc.setAttr((beseMesh+'.symmetryY'),getSymY)
    if not mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryZ', at = "long" )
    mc.setAttr((beseMesh+'.symmetryZ'),getSymZ)
    
    boolSymmetryRestore()
    mc.select(newCutterList)
        
def bakeCutter():
    #step up
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    #store any symmtry
    getSymX = 0
    getSymY = 0
    getSymZ = 0
    if mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        getSymX =  mc.getAttr(beseMesh+'.symmetryX')
    if mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        getSymY =  mc.getAttr(beseMesh+'.symmetryY')
    if mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        getSymZ =  mc.getAttr(beseMesh+'.symmetryZ')  
    #flatten all cutters
    flattenAlllCutter()    
    #make bool mesh as new base mesh
    newMesh = mc.duplicate((beseMesh+'_bool'),rr=1)
    mc.delete(beseMesh+'_bool')
    #create Step up Group
    if mc.objExists((beseMesh +'_bakeStep')) == 0:
        mc.CreateEmptyGroup()
        mc.rename((beseMesh +'_bakeStep'))
        mc.parent((beseMesh +'_bakeStep'), (beseMesh+'BoolGrp'))
    mc.setAttr((beseMesh +'_bakeStep.visibility'),0)
    
    if mc.objExists((beseMesh +'_bakeBaseMesh')) == 0:    
        #bake base mesh 
        bakeMesh = mc.duplicate(beseMesh, rr=1)
        mc.delete(beseMesh)
        mc.parent(bakeMesh,(beseMesh +'_bakeStep'))
        mc.rename(bakeMesh,(beseMesh +'_bakeBaseMesh'))
        bakeShape = mc.listRelatives((beseMesh +'_bakeBaseMesh'), shapes=True,f=True)
        mc.setAttr((bakeShape[0] + '.overrideShading'), 1)
        mc.rename(newMesh,beseMesh)
    else:
        mc.delete(beseMesh)
        mc.rename(newMesh,beseMesh)
    
    if mc.objExists(beseMesh +'_myBool'):
        mc.delete(beseMesh+'_myBool')
    #reNumber
    mc.select((beseMesh+'_bakeStep'), hi=True)
    mc.select((beseMesh+'_bakeStep'),(beseMesh +'_bakeBaseMesh'),d=True)
    existCutterList = mc.ls(sl=1,fl=1,type='transform')
        
    #start rename old cutters
    mc.select((beseMesh+'_cutterGrp'), hi=True)
    mc.select((beseMesh+'_cutterGrp'),d=True)
    oldCutterList = mc.ls(sl=1,fl=1,type='transform')
    
    initalIndex = len(existCutterList) + 1
    for o in oldCutterList:
        newName = ('bakeCutter' + str(initalIndex))
        mc.rename(o, newName)
        initalIndex += 1
    newList= mc.ls(sl=1,fl=1,type='transform')
    if len(newList)>0:
        mc.parent(newList,(beseMesh +'_bakeStep'))
                
    #unlock connection
    shape = mc.listRelatives(beseMesh, shapes=True,f=True)
    checkConnection = mc.listConnections((shape[0]+'.drawOverride'),c=1,p=1)
    if checkConnection != None:
        mc.disconnectAttr(checkConnection[1],checkConnection[0])
        
    #recreate bool
    recreateBool()
    
    checkPreBoolGrp = mc.ls((beseMesh +'_preBoolBox'), l=True)
    
    if 'BoolGrp' not in checkPreBoolGrp[0]:
        mc.parent(checkPreBoolGrp[0],(beseMesh +'BoolGrp'))
    
    shapeNode = mc.listRelatives((beseMesh+'Shape'), s=True )
    if shapeNode != None:
        if len(shapeNode)>0:
            mc.setAttr((shapeNode[0]+'.intermediateObject'), 0)
            mc.parent((beseMesh+'Shape'),(beseMesh +'BoolGrp'))
            mc.delete(beseMesh)
            mc.rename(beseMesh)
    
    #rebuild symmtry 
    
    if not mc.attributeQuery('symmetryX', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryX', at = "long" )
    mc.setAttr((beseMesh+'.symmetryX'),getSymX)
    if not mc.attributeQuery('symmetryY', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryY', at = "long" )
    mc.setAttr((beseMesh+'.symmetryY'),getSymY)
    if not mc.attributeQuery('symmetryZ', node = beseMesh, ex=True ):
        mc.addAttr(beseMesh, ln='symmetryZ', at = "long" )
    mc.setAttr((beseMesh+'.symmetryZ'),getSymZ)
    boolSymmetryRestore()
    mc.select(cl=True)

    
def flattenAlllCutter():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    mc.select((beseMesh+'_cutterGrp'), hi=True)
    mc.select((beseMesh+'_cutterGrp'),d=True)
    if mc.objExists('bakeCutter*'):
        mc.select('bakeCutter*',d=True)
    selList = mc.ls(sl=1,fl=1,type='transform')
    if len(selList) > 1:
        #bake array 
        for s in selList:
            if mc.objExists(s):
                mc.select(s)
                myType = checkInstType()
                if myType[1] != 'new':
                    instBake()
                    newNode = mc.ls(sl=1,fl=1)
                    selList.append(newNode[0])
    
def instTypeCommandChange():
    checkState = mc.radioButtonGrp('arrayTypeButton',q=True, sl = True)
    if checkState == 1:
        #Lin
        mc.intSliderGrp('instNumSlider', e=1 ,dc = 'instReNew()' )
        mc.button('instXButton', e =True , c = 'instAdd("X")')  
        mc.button('instYButton', e =True , c = 'instAdd("Y")')  
        mc.button('instZButton', e =True , c = 'instAdd("Z")')  
    else:
        #Rad
        mc.intSliderGrp('instNumSlider', e=1 ,dc = 'instRadReNew()' )
        mc.button('instXButton', e =True , c = 'instRadAdd("X")')  
        mc.button('instYButton', e =True , c = 'instRadAdd("Y")')  
        mc.button('instZButton', e =True , c = 'instRadAdd("Z")')  

def instTypeToggle():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    currentSel =mc.ls(sl=1,fl=1)
    if len(currentSel) == 1:
        #case one Linear to Radial
        myType = checkInstType()
        if myType[1] != 'new':
            getNumber = mc.getAttr(myType[0]+'.arrayNumber')
            getDis = mc.getAttr(myType[0]+'.arrayOffset')
            getDir = mc.getAttr(myType[0]+'.arrayDirection')
            
            if myType[1] == 'linear':
                instRemove()
                mc.setAttr((myType[0]+'.arrayType'),'radial',type="string")
                if mc.objExists((beseMesh +'_cutterGrp')) == 0:
                    mc.CreateEmptyGroup()
                    mc.rename((beseMesh +'_cutterGrp'))
                    mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))
                mc.parent(myType[0],(beseMesh +'_cutterGrp'))
                if mc.objExists(myType[0]+'ArrayGrp'):
                    mc.delete(myType[0]+'ArrayGrp')
                
                instRadAdd(getDir)
        
            elif myType[1] == 'radial':
                removeRadArray()
                mc.setAttr((myType[0]+'.arrayType'),'linear',type="string")
                mc.setAttr((myType[0]+'.arrayOffset'),getDis)
        
                #in case cutterGrp will get delete when delete history
                if mc.objExists((beseMesh +'_cutterGrp')) == 0:
                    mc.CreateEmptyGroup()
                    mc.rename((beseMesh +'_cutterGrp'))
                    mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))
                instAdd(getDir)
                mc.floatSliderGrp('disSlider',e=True, v= getDis ) 
    instTypeCommandChange()

def freeResultMesh():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    boolSymmetryFreeze()
    resultMesh = beseMesh +'_bool'
    mc.select(resultMesh)
    mc.duplicate(rr=True)
    mc.rename(beseMesh)
    newNode = mc.ls(sl=True,fl=True)
    shapeNew = mc.listRelatives(newNode[0], s=True )
    mc.parent(w=True)
    mc.layerButton((beseMesh +'_BoolResult'), e=True ,lv=0)
    mc.setAttr((beseMesh +'BoolGrp.visibility'),0)  
    mc.disconnectAttr((beseMesh+'_BoolResult.drawInfo'), (shapeNew[0]+'.drawOverride'))
    mc.editDisplayLayerMembers('defaultLayer',newNode)
    mc.textField("setMeshField", e = True, text = '')
    
def checkInstType():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    arraySample = []
    checkGrp = mc.ls(sl=1,fl=1,l=1)
    if 'ArrayGrp' in checkGrp[0]:
        mc.connectControl('disSlider', (''))
        allChild = mc.listRelatives(checkGrp[0], ad=True)
        getShapeNode = mc.ls(allChild,type ='shape')
        listTransNode = mc.listRelatives(getShapeNode,  p=True )
        arraySample = listTransNode
        checkMaster = mc.getAttr(arraySample[0]+'.arrayMaster')
        checkMasterType = mc.getAttr(arraySample[0]+'.arrayType')
        mc.floatSliderGrp('disSlider',e=True, en= True ) 
        mc.intSliderGrp('instNumSlider',e=True, en= True )
        return (checkMaster,checkMasterType)
    else:
        if mc.attributeQuery('arrayMaster', node = checkGrp[0], ex=True ):
            checkMaster = mc.getAttr(checkGrp[0]+'.arrayMaster')
            checkMasterType = mc.getAttr(checkGrp[0]+'.arrayType')
            if checkMasterType != None:
                return (checkMaster,checkMasterType)
        else:
            return ('new','new')


def removeArrayGrp():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    selCutterCheck = mc.ls(sl=1, fl=1, l=1, type='transform')
    if len(selCutterCheck) == 1 and 'boxCutter' in selCutterCheck[0] and 'ArrayGrp' in selCutterCheck[0]:
        myType = checkInstType()
        mc.select(myType[0])
        if myType[1] == 'radial':
            removeRadArray()
        elif myType[1] == 'linear':
            instRemove()
            mc.parent(myType[0],(beseMesh +'_cutterGrp'))
            mc.delete(myType[0]+'ArrayGrp')
        mc.setAttr((myType[0]+'.arrayType'),'new',type="string")
        mc.setAttr((myType[0]+'.arrayMaster'),'new',type="string")
    
def instLink():
    myType = checkInstType()
    arraySample = myType[0]
    if myType[1] != 'new':
        if myType[1] == 'radial':
            #Rad
            mc.intSliderGrp('instNumSlider', e=1 ,dc = 'instRadReNew()' )
            mc.button('instXButton', e =True , c = 'instRadAdd("X")')  
            mc.button('instYButton', e =True , c = 'instRadAdd("Y")')  
            mc.button('instZButton', e =True , c = 'instRadAdd("Z")')  
            mc.radioButtonGrp('arrayTypeButton',e=True, sl = 2)
            #link
            checkMasterDir = mc.getAttr(arraySample+'.arrayDirection')
            OffsetDir =[]
            
            if checkMasterDir == 'X':
                OffsetDir = 'Y'
            elif checkMasterDir == 'Y':
               OffsetDir = 'X'
            else:   
              OffsetDir = 'X'
            mc.connectControl('instNumSlider', (arraySample+".arrayNumber"))
            mc.floatSliderGrp('disSlider',e=True, en= True ) 
            mc.connectControl('disSlider', (arraySample+".arrayOffset"))
        
        else:
            #Lin
            mc.intSliderGrp('instNumSlider', e=1 ,dc = 'instReNew()' )
            mc.button('instXButton', e =True , c = 'instAdd("X")')  
            mc.button('instYButton', e =True , c = 'instAdd("Y")')  
            mc.button('instZButton', e =True , c = 'instAdd("Z")')  
            mc.radioButtonGrp('arrayTypeButton',e=True, sl = 1)
            mc.connectControl('instNumSlider', (arraySample+".arrayNumber"))
            mc.connectControl('disSlider', (arraySample+".arrayOffset"))
        mc.select((arraySample+'ArrayGrp'))

        
def instRadReNew():
    mc.radioButtonGrp('arrayTypeButton',e=True, sl = 2)
    myType = checkInstType()
    if myType[1] != 'radial':#lin
        instLink()
    removeRadArray()
    checkMaster = myType[0]
    if mc.attributeQuery('arrayDirection', node = checkMaster, ex=True ):
        currentDir = mc.getAttr(checkMaster+'.arrayDirection')
        instRadAdd(currentDir)
    
    
def instRadAdd(direction):
    selCutterCheck = mc.ls(sl=1, fl=1, l=1, type='transform')
    if len(selCutterCheck) == 1 and 'boxCutter' in selCutterCheck[0] :
        mc.radioButtonGrp('arrayTypeButton',e=True, sl = 2)
        myType = checkInstType()
        #cutterOPDate = mc.getAttr(myType[0] +'.cutterOp')
        if myType[1] != 'radial' and myType[1] != 'new':#lin
            instAdd(direction)
        else:    
            beseMesh = mc.textField("setMeshField", q = True, text = True)
            arraySample = mc.ls(sl=1,fl=1)
            if 'boxCutter' in arraySample[0] and len(arraySample)==1:
                removeRadArray()
                arraySample = mc.ls(sl=1,fl=1)
                dir = direction
                if myType[1] == 'new':
                    rNumber = 3
                    rDistance = 1
                else:
                    rNumber = mc.intSliderGrp('instNumSlider', q=True,  v = True)
                    rDistance = mc.floatSliderGrp('disSlider', q=True,  v = True)
                collection =[]
                
                #create Attr
                if not mc.attributeQuery('arrayNumber', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayNumber')
                
                if not mc.attributeQuery('arrayDirection', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayDirection' ,dt= 'string')
                
                if not mc.attributeQuery('arrayType', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayType',dt= 'string')
                
                if not mc.attributeQuery('arrayOffset', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayOffset')    
                
                if not mc.attributeQuery('arrayMaster', node = arraySample[0], ex=True ):
                    mc.addAttr(arraySample[0], ln='arrayMaster'  ,dt= 'string')
                    mc.setAttr((arraySample[0]+'.arrayOffset'),1)
                if not mc.attributeQuery('arrayLength', node = arraySample[0], ex=True ):
                        mc.addAttr(arraySample[0], ln='arrayLength')  
                        
                mc.setAttr((arraySample[0]+'.arrayNumber'),rNumber)
                mc.setAttr((arraySample[0]+'.arrayOffset'),rDistance)
                mc.setAttr((arraySample[0]+'.arrayDirection'),dir,type="string")
                mc.setAttr((arraySample[0]+'.arrayType'),'radial',type="string")
                mc.setAttr((arraySample[0]+'.arrayMaster'),arraySample[0],type="string")
                
                
                bbox= mc.xform(arraySample[0], q=1, ws=1, bb=1)
                length=math.sqrt((math.pow(bbox[0]-bbox[3],2)+math.pow(bbox[1]-bbox[4],2)+math.pow(bbox[2]-bbox[5],2))/3)
                mc.setAttr((arraySample[0]+'.arrayLength'),length)
                
                sourcePivot = mc.xform(arraySample[0], q=1, ws=1 ,rp=1) 
                mc.group()
                mc.rename(arraySample[0]+'_Trans')
                mc.group()
                mc.rename(arraySample[0]+'_Rot')
                
                collection.append((arraySample[0]+'_Rot'))
                rAngle = 360.0 / rNumber 
                
                mc.xform((arraySample[0]+'_Rot') ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
                #inst
                boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
                for i in range(rNumber-1):

                    mc.select((arraySample[0]+'_Rot'))
                    mc.instance()
                    newCutterRot = mc.ls(sl=1,fl=1)
                    collection.append(newCutterRot[0])
                    if dir == 'X':
                        mc.rotate((rAngle*(i)+rAngle), 0 ,0, r=True, ws=True, fo=True)
                    elif dir == 'Y':
                        mc.rotate(0,(rAngle*(i)+rAngle),0, r=True, ws=True, fo=True)
                    else:   
                        mc.rotate(0,0,(rAngle*(i)+rAngle), r=True, ws=True, fo=True)
                    
                    #Bool
                    shapeNode = mc.listRelatives((newCutterRot[0]+'|'+ arraySample[0] +'_Trans|'+arraySample[0]), s=True )
                    nextIndex = get_latest_free_multi_index((boolNode[0]+'.inputPoly'),0)
                    mc.connectAttr( (shapeNode[0]+".worldMatrix[" + str(int(i)+ int(1)) + "]"), ((boolNode[0]+'.inputMat['+str(nextIndex)+']')),f=True)
                    mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(nextIndex)+']')),f=True)
        
                mc.select(collection)
                mc.group()
                mc.rename(arraySample[0]+'ArrayGrp')
                OffsetDir =[]
                
                if dir == 'X':
                    OffsetDir = 'Y'
                elif dir == 'Y':
                   OffsetDir = 'X'
                else:   
                  OffsetDir = 'X'
                #mc.connectAttr( (arraySample[0]+".arrayOffset"), (arraySample[0]+"_Trans.translate" + OffsetDir),f=True)
                cmdTextA = (arraySample[0] + '_Trans.translate' + OffsetDir + '= ' + arraySample[0] + '.arrayLength *' + arraySample[0] + '.arrayOffset;')
                mc.expression( s = cmdTextA, o = (arraySample[0] + '_Trans.translate'), ae = True, uc = all)
                        
                mc.select((arraySample[0]+'ArrayGrp'))
                mc.xform((arraySample[0]+'ArrayGrp') ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
                mc.connectControl('instNumSlider', (arraySample[0]+".arrayNumber"))
                mc.floatSliderGrp('disSlider',e=True, en= True ) 
                mc.connectControl('disSlider', (arraySample[0]+".arrayOffset"))


def removeRadArray():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
    myType = checkInstType()
    if myType[1] == 'radial':
        arraySample = myType[0]
        mc.setAttr( (arraySample+".arrayOffset"),0)
        if mc.objExists(arraySample+'_Rot*'):
            mc.select(arraySample+'_Rot*')
            listRArray = mc.ls(sl=1,fl=1)
            mc.delete(listRArray[1:len(listRArray)])
            mc.parent(arraySample,beseMesh+'_cutterGrp')
            sourcePivot = mc.xform((arraySample+'_Rot'), q=1, ws=1 ,rp=1) 
            mc.select(arraySample)
            mc.move( sourcePivot[0],sourcePivot[1],sourcePivot[2],rpr=True)
            if mc.objExists(arraySample+'ArrayGrp'):
                mc.delete(arraySample+'ArrayGrp')
        if mc.objExists(arraySample+'ArrayGrp'):
            mc.delete(arraySample+'ArrayGrp')
        
        shapeNode = mc.listRelatives(arraySample, s=True )
        listConnect = mc.connectionInfo((shapeNode[0]+'.outMesh'), dfs=True )
        if len(listConnect)>0:
            for a in listConnect:
                mc.disconnectAttr((shapeNode[0]+'.outMesh'), a)
        checkNumber = ''.join([n for n in arraySample.split('|')[-1] if n.isdigit()])    
        mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(checkNumber)+']')),f=True)  
        mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((boolNode[0]+'.inputMat['+str(checkNumber)+']')),f=True)
        mc.select(arraySample) 


def get_latest_free_multi_index( attr_name, start_index ):
    '''Find the latest unconnected multi index starting at the passed in index.'''
    listCuttersIndex = []
    while start_index < 100:
        if mc.connectionInfo( '{}[{}]'.format(attr_name,start_index), sfd=True ):
            listCuttersIndex.append(start_index)
        start_index += 1
    nextIndex = (listCuttersIndex[-1]+1)
    return nextIndex

def get_next_free_multi_index( attr_name, start_index ):
	'''Find the next unconnected multi index starting at the passed in index.'''
	# assume a max of 100 connections
	while start_index < 100:
		if len( mc.connectionInfo( '{}[{}]'.format(attr_name,start_index), sfd=True ) or [] ) == 0:
			return start_index
		start_index += 1

	# No connections means the first index is available
	return 0			

def instBake():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    myType = checkInstType()
    if myType[1] != 'new':
        if myType[1] == 'radial':
            arraySample = myType[0]
            mc.select(arraySample+'ArrayGrp')
            mc.select(arraySample+'_Rot*')
            mc.select((arraySample+'_Rot'),d=1)
            listInstance = mc.ls(sl=1,fl=1, l=1)
            
            mc.select((arraySample+'_Rot'))
            mc.ConvertInstanceToObject()
            
            unInstanceMesh = mc.ls(sl=1,fl=1, l=1)
            mc.select(listInstance)
            mel.eval("pickWalk -d down")
            mc.delete()
            
            for l in listInstance:
                mc.select(unInstanceMesh)
                mc.duplicate()
                mc.select(l,add=1)
                mc.MatchTransform()
                mc.delete(l)
         
            mc.select((arraySample+'ArrayGrp'))
            mc.select(hi=True)
            mc.select((arraySample+'ArrayGrp'),d=True)
            getShapeNode = mc.ls(sl=1,type ='shape')
            mc.select(getShapeNode)
            mel.eval("pickWalk -d up")
            listNew=mc.ls(sl=1,fl=1,l=1)
            mc.parent(listNew,(arraySample+'ArrayGrp'))
            listNew=mc.ls(sl=1,fl=1,l=1)
            
            for n in listNew:
                mc.rename(n,'tempCutter01')
              
            listBake=mc.ls('tempCutter0*',s=1)
            
            while len(listBake) > 1:
                mc.polyCBoolOp(listBake[0], listBake[1], op=1, ch=1, preserveColor=0, classification=1, name=listBake[0])
                mc.DeleteHistory()
                #if mc.objExists(listBake[0]):
                    #mc.delete(listBake[0])
                if mc.objExists(listBake[1]):
                    mc.delete(listBake[1])
                mc.rename(listBake[0])
                listBake.remove(listBake[1])
            #in case cutterGrp will get delete when delete history
            if mc.objExists((beseMesh +'_cutterGrp')) == 0:
                mc.CreateEmptyGroup()
                mc.rename((beseMesh +'_cutterGrp'))
                mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))
            mc.select(listBake)
            useOwnCutterShape()
            mc.rename(arraySample)
            sourcePivot = mc.xform((arraySample+'ArrayGrp'), q=1, ws=1 ,rp=1) 
            mc.xform(arraySample ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
            if mc.objExists(arraySample+'ArrayGrp'):
                mc.delete(arraySample+'ArrayGrp')
            mc.ogs(reset =1)
        else:
            arraySample = myType[0]
            mc.select(arraySample+'ArrayGrp')
            mc.select(hi=True)
            mc.select(arraySample+'ArrayGrp',arraySample,d=1)
            collectInst = mc.ls(sl=1,fl=1,type = 'transform')
            mc.select(collectInst)
            mc.ConvertInstanceToObject()
            collectInst.append(arraySample)
            collectInst.reverse()
            listBake = collectInst
            while len(listBake) > 1:
                mc.polyCBoolOp(listBake[0], listBake[1], op=1, ch=0, preserveColor=0, classification=1, name=listBake[0])
                mc.DeleteHistory()
                mc.rename('tempMergeShape')
                if mc.objExists(listBake[0]):
                    mc.delete(listBake[0])
                if mc.objExists(listBake[1]):
                    mc.delete(listBake[1])
                mc.rename(listBake[0])
                listBake.remove(listBake[1])
                            
            #in case cutterGrp will get delete when delete history
            if mc.objExists((beseMesh +'_cutterGrp')) == 0:
                mc.CreateEmptyGroup()
                mc.rename((beseMesh +'_cutterGrp'))
                mc.parent((beseMesh +'_cutterGrp'),(beseMesh +'BoolGrp'))
            mc.select(listBake)
            useOwnCutterShape()
            mc.rename(listBake[0])
            if mc.objExists(listBake[0]+'ArrayGrp'):
                mc.delete(listBake[0]+'ArrayGrp')
    mc.select(arraySample) 
    fixBoolNodeConnection()

def fixBoolNodeConnection():
    transNode = mc.ls(sl=1,fl=1)
    checkNumber = ''.join([n for n in transNode[0].split('|')[-1] if n.isdigit()]) 
    shapeNode = mc.listRelatives(transNode[0], s=True ,f=True)
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
    if len(shapeNode)>0:
        listConnect = mc.connectionInfo((shapeNode[0]+'.outMesh'), dfs=True )
        if len(listConnect)>0:
            for a in listConnect:
                mc.disconnectAttr((shapeNode[0]+'.outMesh'), a)
        mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(checkNumber)+']')),f=True)  
        
        listConnectMa = mc.connectionInfo((shapeNode[0]+'.worldMatrix[0]'), dfs=True )
        if len(listConnectMa)>0:
            for b in listConnectMa:
                mc.disconnectAttr((shapeNode[0]+'.worldMatrix[0]'), b)
        mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((boolNode[0]+'.inputMat['+str(checkNumber)+']')),f=True)  

def instReNew():
    myType = checkInstType()
    if myType[1] != 'new':
        mc.radioButtonGrp('arrayTypeButton',e=True, sl = 1)
        myType = checkInstType()
        if myType[1] != 'linear':#lin
            instLink()
        instRemove()
        checkMaster = myType[0]
        currentDir = mc.getAttr(checkMaster+'.arrayDirection')
        instAdd(currentDir)       
    

def instRemove():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    boolNode = mc.listConnections(mc.listHistory((beseMesh+'_bool'),f=1),type='polyCBoolOp')
    myType = checkInstType()
    if myType[1] == 'linear':
        arraySample = myType[0]
        listA = mc.listConnections(arraySample,type = 'expression')
        if listA != None:
            listA = set(listA)
            collectInst=[]
            for l in listA:
                checkConnection = mc.connectionInfo( (l+'.output[0]'), dfs=True)
                mesh = checkConnection[0].split(".")[0]
                collectInst.append(mesh)
            mc.delete(collectInst)
        shapeNode = mc.listRelatives(arraySample, s=True )
        listConnect = mc.connectionInfo((shapeNode[0]+'.outMesh'), dfs=True )
        if len(listConnect)>0:
            for a in listConnect:
                mc.disconnectAttr((shapeNode[0]+'.outMesh'), a)
        checkNumber = ''.join([n for n in arraySample.split('|')[-1] if n.isdigit()])    
        mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(checkNumber)+']')),f=True)  
        mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((boolNode[0]+'.inputMat['+str(checkNumber)+']')),f=True)
        mc.select(arraySample)  
            
def instAdd(direction):
    selCutterCheck = mc.ls(sl=1, fl=1, l=1, type='transform')
    if len(selCutterCheck) == 1 and 'boxCutter' in selCutterCheck[0]:
        mc.radioButtonGrp('arrayTypeButton',e=True, sl = 1)
        myType = checkInstType()

        if myType[1] == 'radial':#lin
            instRadAdd(direction)
        else:    
            instRemove()
            dir = direction
            beseMesh = mc.textField("setMeshField", q = True, text = True)
            if len(beseMesh) > 0:
                arraySample = mc.ls(sl=1,fl=1)
                sourcePivot = mc.xform(arraySample[0], q=1, ws=1 ,rp=1) 
                if 'boxCutter' in arraySample[0] and len(arraySample)==1:
                    bbox= mc.xform(arraySample[0], q=1, ws=1, bb=1)
                    myLength = []
                    if dir == 'X':
                        myLength=math.sqrt((math.pow(bbox[0]-bbox[3],2)))
                    if dir == 'Y':
                        myLength=math.sqrt((math.pow(bbox[1]-bbox[4],2)))
                    if dir == 'Z':
                        myLength=math.sqrt((math.pow(bbox[2]-bbox[5],2)))
    
                    getIntNumber = []
                    getDist = []
                    if myType[1] == 'new':
                        getIntNumber = 2
                        getDist = 1.5
                    
                    else:
                        getIntNumber = mc.intSliderGrp('instNumSlider', q=True,  v = True)
                        getDist = mc.floatSliderGrp('disSlider', q=True,  v = True)
    
                    #create Attr
                    if not mc.attributeQuery('arrayNumber', node = arraySample[0], ex=True ):
                        mc.addAttr(arraySample[0], ln='arrayNumber')
                    
                    if not mc.attributeQuery('arrayDirection', node = arraySample[0], ex=True ):
                        mc.addAttr(arraySample[0], ln='arrayDirection' ,dt= 'string')
                    
                    if not mc.attributeQuery('arrayType', node = arraySample[0], ex=True ):
                        mc.addAttr(arraySample[0], ln='arrayType',dt= 'string')
                    
                    if not mc.attributeQuery('arrayLength', node = arraySample[0], ex=True ):
                        mc.addAttr(arraySample[0], ln='arrayLength')  
                        
                    if not mc.attributeQuery('arrayOffset', node = arraySample[0], ex=True ):
                        mc.addAttr(arraySample[0], ln='arrayOffset')    
                    
                    if not mc.attributeQuery('arrayMaster', node = arraySample[0], ex=True ):
                        mc.addAttr(arraySample[0], ln='arrayMaster'  ,dt= 'string')
                        mc.setAttr((arraySample[0]+'.arrayOffset'),1)
                    
                    mc.setAttr((arraySample[0]+'.arrayNumber'),getIntNumber)
                    mc.setAttr((arraySample[0]+'.arrayDirection'),dir,type="string")
                    mc.setAttr((arraySample[0]+'.arrayType'),'linear',type="string")
                    mc.setAttr((arraySample[0]+'.arrayLength'),myLength)
                    mc.setAttr((arraySample[0]+'.arrayMaster'),arraySample[0],type="string")
    
                    dirA = (arraySample[0]+'.translate'+dir)
                    collections=[]  
                    boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')					
                    for i in range(getIntNumber-1):
                        mc.select(arraySample[0])
                        mc.instance()
                        newIns = mc.ls(sl=1,fl=1)
                        collections.append(newIns[0])
                        if not mc.attributeQuery('arrayOrder', node = newIns[0], ex=True ):
                            mc.addAttr(newIns[0], ln='arrayOrder')
                        mc.setAttr((newIns[0]+'.arrayOrder'),(i+1)) 
                        mc.setAttr((arraySample[0] + '.arrayOffset'),getDist)
                        cmdTextA = (newIns[0] + '.translate' + dir + '= ' + arraySample[0] + '.arrayLength *' + arraySample[0] + '.arrayOffset *' +  newIns[0] + '.arrayOrder +'+ dirA +';')
                        mc.expression( s = cmdTextA, o = newIns[0], ae = True, uc = all)
                        #Bool
                        shapeNode = mc.listRelatives(newIns[0], s=True )
                        nextIndex = get_latest_free_multi_index((boolNode[0]+'.inputPoly'),0)
                        mc.connectAttr( (shapeNode[0]+".worldMatrix[" + str(int(i)+ int(1)) + "]"), ((boolNode[0]+'.inputMat['+str(nextIndex)+']')),f=True)
                        mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(nextIndex)+']')),f=True)
        
                        
        
                    mc.select(arraySample[0],collections)
                    
                    parent = mc.listRelatives(arraySample[0], p=True )
                    if not 'ArrayGrp' in parent[0]:
                        mc.group()
                        mc.rename(arraySample[0]+'ArrayGrp')
                    mc.xform((arraySample[0]+'ArrayGrp') ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
                    mc.intSliderGrp('instNumSlider',e=True, en= True ) 
                    mc.connectControl('instNumSlider', (arraySample[0]+".arrayNumber"))
                    mc.floatSliderGrp('disSlider',e=True, en= True ) 
                    mc.connectControl('disSlider', (arraySample[0]+".arrayOffset"))
                    mc.select((arraySample[0]+'ArrayGrp'))
                    #if cutterOPDate == 'subs':
                    #    cutterType("subs")
                    #elif cutterOPDate == 'union':
                    #    cutterType("union")
                    #else:
                    #    cutterType("inter")

def makeDrawBlock():
    mc.ScaleTool()
    curveSel = mc.ls(sl=1,fl=1)
    if len(curveSel) == 1 :
        beseMesh = mc.textField("setMeshField", q = True, text = True)
        if mc.objExists('drawPlaneGrp') == 0:
            if mc.objExists('lineDrawPlane'):
                mc.delete('lineDrawPlane*')
    mc.snapMode(grid=0)
    shapeNode = mc.listRelatives(curveSel[0], f = True, shapes=True)
    checkOpen = mc.getAttr(shapeNode[0]+'.form')
    if checkOpen == 0:
        mc.closeCurve( curveSel[0], ch=True, rpo=True )
            
    mc.select(curveSel)
    mc.duplicate()
    mc.group(w=True)
    mc.rename('tempMirrorGrp')
    
    if mc.objExists('drawPlaneGrp'):
        mc.parent('tempMirrorGrp','drawPlaneGrp')
        mc.FreezeTransformations()
        mc.setAttr('tempMirrorGrp.translateY',-1)
    
    
    else:
        current = mc.textField("camPlane" ,q=True, text = True)
        mesh = (beseMesh +'_bool')
        meshCOORD = mc.objectCenter(mesh,gl=True)
        mc.xform(ws=True,  pivots =[meshCOORD[0],meshCOORD[1],meshCOORD[2]])
        if current == 'front' or current == 'back':
            mc.scale(1,1,-1)
        
        elif  current == 'top' or current == 'buttom':# check y asix
            mc.scale(1,-1,1)
        
        elif  current == 'left' or current == 'right':# check x asix
            mc.scale(-1,1,1)
    
    mc.Ungroup()
    mc.select(curveSel,add=1)
    mc.FreezeTransformations()
    curveSel = mc.ls(sl=1,fl=1)
    mc.select(curveSel)
    loftNode = mc.loft(ch =1, u=1, c= 0, ar= 1, d= 3, ss= 1, rn= 0, po =1, rsn= True)
    list = mc.listConnections(loftNode, type = 'nurbsTessellate')
    
    mc.setAttr((list[0]+'.polygonType'), 1)
    mc.setAttr((list[0]+'.format'), 2)
    mc.setAttr((list[0]+'.uNumber'), 1)
    mc.setAttr((list[0]+'.vNumber'), 1)
    mc.FillHole()
    mc.delete(curveSel)
    mc.rename('drawBlock')
    blockSel = mc.listRelatives(mc.listRelatives(f = True, shapes=True), parent=1 , f=1 )
    mc.CenterPivot()
    mc.polyMergeVertex(blockSel,d = 0.01, am= 1,ch=0)
    mc.polySetToFaceNormal()
    renew = mc.listRelatives(mc.listRelatives(f = True, shapes=True), parent=1 , f=1 )
    mc.DeleteHistory()
    #fix normal direction
    checkNormalMehs = mc.ls(sl=1,fl=1,l=1)
    mc.polyExtrudeFacet(constructionHistory = 1, keepFacesTogether= 1, ltz = 0.001) 
    mc.polySeparate(checkNormalMehs,ch=0)
    testMesh = mc.ls(sl=1,fl=1)
    
    worldFaceA = mc.polyEvaluate(testMesh[0],wa=True)
    worldFaceB = mc.polyEvaluate(testMesh[1],wa=True)
    if worldFaceA > worldFaceB:
        mc.delete(testMesh[1])
    else:
        mc.delete(testMesh[0])
    mc.parent(w=True)
    mc.delete(checkNormalMehs[0])
    mc.rename('drawBlock1')
    newBlock = mc.ls(sl=1,fl=1)
    mc.select(newBlock[0])
    mc.DeleteHistory()
    if mc.objExists('drawPlaneGrp'):
        mc.parent(newBlock[0],'drawPlaneGrp')
        mc.FreezeTransformations() 
        mc.CenterPivot()
        mc.parent(newBlock[0],w=True)
    if mc.objExists('drawPlaneGrp'):
        mc.delete('drawPlaneGrp*')
    if mc.objExists('lineDrawPlane'):
        mc.delete('lineDrawPlane*')
            

def resizeSnapGrid():
    if mc.objExists('lineDrawPlane'):
        gridData=  mc.intSliderGrp('snapGirdSize', q = True, v =True)
        #change gridSize
        mc.makeLive(n=True)
        mc.grid( spacing=10, d= gridData )
        mc.makeLive('lineDrawPlane')
        mc.snapMode(grid=1)


def drawGirdToggle():
    if mc.objExists('lineDrawPlane'):
        mc.delete('lineDrawPlane')
        if mc.objExists('drawPlaneGrp'):
            mc.delete('drawPlaneGrp')
        drawGirdOff()
    else:
        current = mc.textField("camPlane" ,q=True, text = True)
        curPanel = mc.getPanel(wf=1)
        
        if not 'modelPanel' in curPanel:
            curPanel = 'modelPanel4'
        mc.modelEditor( curPanel,e=1, planes=1)
        curCam = mc.modelPanel(curPanel,q=1, cam=1)
        orthoValue = mc.camera(curCam,q=1, o=1)
        if orthoValue ==0:
            camRot = mc.camera(curCam,q=1, rot=1)
            camRotFixed = []
            for i in range(2):
                camRotTemp = camRot[i] / 360
                intOfTemp = int(camRotTemp)
                rotOver = 360 * intOfTemp
                camRotFixed.append( camRot[i] - rotOver)
            
            for i in range(2):
                if camRotFixed[i] < 0 :
            	      camRotFixed[i]= camRotFixed[i] +360;
            
            cameraUsed=[]
            if (camRotFixed[0] >= 45 and camRotFixed[0] < 135):
                cameraUsed = 'buttom'
            elif (camRotFixed[0] >= 225 and camRotFixed[0] < 315):
                cameraUsed = 'top'
            elif (camRotFixed[1] < 45):
                cameraUsed = 'front'
            elif (camRotFixed[1] >= 315 ):
                cameraUsed = 'front'
            elif (camRotFixed[1] >= 45 and camRotFixed[1] < 135):
                cameraUsed = 'right'
            elif (camRotFixed[1] >= 135 and camRotFixed[1] < 225):
                cameraUsed = 'back'
            elif (camRotFixed[1] >= 225 and camRotFixed[1] < 315):
                cameraUsed = 'left'
    
            if len(current) ==0 :
                mc.textField("camPlane" ,e=True, text = cameraUsed)
                drawGirdOn()
            else:
                if current == cameraUsed:
                    if mc.objExists('lineDrawPlane'):
                        mc.delete('lineDrawPlane*')
                        if mc.objExists('tempScaleOffset'):
                            mc.delete('tempScaleOffset*')
                        mc.snapMode(grid=0)
                        mc.MoveTool()
                        drawGirdOff()
                    else:
                        mc.textField("camPlane" ,e=True, text = cameraUsed)
                        drawGirdOn()
                else:
                    if mc.objExists('lineDrawPlane'):
                        mc.delete('lineDrawPlane*')
                        if mc.objExists('tempScaleOffset'):
                            mc.delete('tempScaleOffset*')
                    mc.textField("camPlane" ,e=True, text = cameraUsed)
                    drawGirdOn()

def drawGirdOff():
    mc.connectControl('snapGirdSize', (''))
    mc.intSliderGrp('snapGirdSize',e=1, en=0)
    if mc.objExists('lineDrawPlane'):
        mc.delete('lineDrawPlane*')
        if mc.objExists('tempScaleOffset'):
            mc.delete('tempScaleOffset*')
        mc.snapMode(grid=0)
        mc.MoveTool()

def drawGirdOn():
    mc.intSliderGrp('snapGirdSize',e=1, en=1)
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    gridData=  mc.intSliderGrp('snapGirdSize', q = True, v =True)
    curPanel = mc.getPanel(wf=1)
    if not 'modelPanel' in curPanel:
        curPanel = 'modelPanel4'
    curCam = mc.modelPanel(curPanel,q=1, cam=1)
    cameraPos = mc.xform(curCam,q=1,ws=1,t=1)
    
    mesh = (beseMesh +'_bool')
    bbox= mc.xform(mesh, q=1, ws=1, bb=1)
    length=math.sqrt((math.pow(bbox[0]-bbox[3],2)+math.pow(bbox[1]-bbox[4],2)+math.pow(bbox[2]-bbox[5],2))/3)
    length = int(length *1.1 )
    meshCOORD = mc.objectCenter(mesh,gl=True)
    cameraUsed = mc.textField("camPlane" ,q=True, text = True)
    constructionPlanePos=[]
    if mc.objExists('lineDrawPlane'):
        mc.delete('lineDrawPlane')
    if mc.objExists('drawPlaneGrp'):
        mc.delete('drawPlaneGrp')
    if cameraUsed == 'front' or cameraUsed == 'back':
        if cameraUsed == 'front':
                planePos = bbox[5]
        elif cameraUsed == 'back':
            if (bbox[2] - cameraPos[2]) > 0:
                planePos = bbox[2]
        
        constructionPlanePos = [meshCOORD[0],meshCOORD[1],planePos]   
        mc.plane(s=length, r=[0,0,90])
    
    elif  cameraUsed == 'top' or cameraUsed == 'buttom':# check y asix
        if cameraUsed == 'top':
            planePos = bbox[4]
        elif cameraUsed == 'buttom':    
            planePos = bbox[1]
        constructionPlanePos = [meshCOORD[0],planePos,meshCOORD[2]]   
        mc.plane(s=length, r=[90,0,0])

    elif  cameraUsed == 'left' or cameraUsed == 'right':# check x asix
        if cameraUsed == 'right':
            planePos = bbox[3]
        elif cameraUsed == 'left':
            planePos = bbox[0]
        constructionPlanePos = [planePos,meshCOORD[1],meshCOORD[2]]  
        mc.plane(s=length, r=[0,90,0])
       
    else:# later
        pass
    
    mc.move(constructionPlanePos[0],constructionPlanePos[1],constructionPlanePos[2],absolute=1)
    mc.rename('lineDrawPlane')
    mc.group()
    mc.rename('tempScaleOffset')
    mc.xform(ws=True,  pivots =[meshCOORD[0],meshCOORD[1],meshCOORD[2]])
    mc.setAttr('tempScaleOffset.scaleX', 1.05)
    mc.setAttr('tempScaleOffset.scaleY', 1.05)
    mc.setAttr('tempScaleOffset.scaleZ', 1.05)
    mc.parent('lineDrawPlane',w=True)
    mc.delete('tempScaleOffset')
    mc.makeLive('lineDrawPlane')
    mc.snapMode(grid=1)
    resizeSnapGrid()
    mc.CVCurveTool()
    mc.curveCVCtx(mc.currentCtx(), e=True, d=1, bez= 0) 


def reBuildCutter():# when cutter has too much history and start getting funny, this can rebuild cutter
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    checkSelType = mc.filterExpand(sm=12 )
    if checkSelType != None:
        checkNoCustom = mc.getAttr(newCutter[0]+'.cutterType')
        if checkNoCustom != "custom" :
            QlinkSlider()
            cutterDirData = mc.getAttr(newCutter[0]+'.cutterDir')
            cutterTypeData = mc.getAttr(newCutter[0]+'.cutterType')
            cutterPanelGap = mc.getAttr(newCutter[0]+'.panelGap')
            cutterIntPanelGap = mc.getAttr(newCutter[0]+'.intPanelGap')
            cutterIntScaleX = mc.getAttr(newCutter[0]+'.intScaleX')
            cutterStateCap = mc.getAttr(newCutter[0]+'.stateCap')
            cutterStatePanel = mc.getAttr(newCutter[0]+'.statePanel')
            
            fractionSliderData = mc.floatSliderGrp('fractionSlider', q = True, v =True)
            segmentSliderData=  mc.intSliderGrp('segmentSlider', q = True, v =True)
            depthSliderData=  mc.floatSliderGrp('depthSlider', q = True, v =True)
            gapSliderData =    mc.floatSliderGrp('gapSlider',   q = True, v =True)
            removePanel()
            QBoxBevelRemove()
            QBoxBevel()
            QlinkSlider()
                
            bevelNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyBevel3')
            if bevelNode != None:
                mc.setAttr((bevelNode[0] + '.fraction'), fractionSliderData)
                mc.setAttr((bevelNode[0] + '.segments'), segmentSliderData) 
                mc.setAttr((bevelNode[0] + '.depth'), depthSliderData) 
                
            if cutterStatePanel == 1:
                makeSelPanel()
         
            if cutterStateCap == 0:
                makeSelPanelNoCap()
            else:
                makeSelPanelReCap()
        else:
            print 'function do not supple custom shape!'
    else:
        print 'function ONLY supple obj!'
        
def bevelPreviewSetting():
    checkState = mc.frameLayout( 'bevelPreSettingLayer', q=1, vis = 1)
    if checkState == 1:
        mc.frameLayout( 'bevelPreSettingLayer', e=1 ,vis = 0)
        mc.window("jwSpeedCutWin",e=1, h = 850)
    else:
        mc.frameLayout( 'bevelPreSettingLayer', e=1 ,vis = 1)
        mc.window("jwSpeedCutWin",e=1, h = 1000)

        
def toggleCapPanel():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    myType = checkInstType()
    if myType[1] != 'new':
        newCutter[0] = myType[0]
    checkSelType = mc.filterExpand(sm=12 )
    if checkSelType != None:
        checkBevelType = mc.getAttr(newCutter[0]+'.cutterType')
        checkCapState = mc.getAttr(newCutter[0]+'.stateCap')
        mc.select(newCutter[0])
        if checkBevelType == 'smooth':
            makeSelPanel()
            mc.setAttr((newCutter[0]+'.stateCap'),1)
        else:
            if checkCapState == 0:
                makeSelPanelReCap()
                mc.setAttr((newCutter[0]+'.stateCap'),1)
            else:
                makeSelPanelNoCap()
                mc.setAttr((newCutter[0]+'.stateCap'),0)
       
        #reBuildCutter()#question this will change shape a lot, [] -->  O, rebuild ---> (==)
    else:
        print 'function ONLY supple obj!'            

def makeSelPanelReCap():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    extrudeNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyExtrudeFace')
    if extrudeNode != None:
        mc.delete(extrudeNode)
    mc.polySelectConstraint(mode = 3, type = 0x8000, where =1)
    mc.polySelectConstraint(disable =True)
    holeEdge = mc.ls(sl=True,fl=True)
    if len(holeEdge)>0:
        mc.polyCloseBorder(ch = 0)
    mc.setAttr((newCutter[0]+'.stateCap'),1)
    mc.select(newCutter) 
    if extrudeNode != None:
        makeSelPanel()
    mc.select(newCutter)
    
def makeSelPanelNoCap():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    checkSelType = mc.filterExpand(sm=12 )
    if checkSelType != None:
        #check cutter type, if no Ngon = a box
        #Ngon = bevel or cylider
        mc.polySelectConstraint( mode = 3, type = 0x0008, size = 1)
        mc.polySelectConstraint(disable =True)
        triPolys = mc.polyEvaluate(faceComponent =True)
        #if triPolys == 0: #not sphere, go next
        mc.setAttr((newCutter[0]+'.stateCap'),0)
        mc.polySelectConstraint( mode = 3, type = 0x0008, size = 3)
        mc.polySelectConstraint(disable =True)
        nPolys = mc.ls(sl=True,fl=True)
        deleteList = []
        if len(nPolys) > 0:
            deleteList = nPolys
        else:
            deleteList = (newCutter[0]+'.f[4]',newCutter[0]+'.f[5]')
        
        extrudeNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyExtrudeFace')
        if extrudeNode != None:
            mc.delete(extrudeNode)
            
        gapV = []
        storeX = mc.getAttr( newCutter[0] + '.scaleX')
        gapV = mc.floatSliderGrp('gapSlider', q=True, v = True)
        if gapV == 0:
            gapV = 0.01
            mc.floatSliderGrp('gapSlider', e = True, v=0.01)
        mc.setAttr((newCutter[0]+'.panelGap'),gapV)
        mc.setAttr((newCutter[0]+'.intPanelGap'),gapV)
        mc.setAttr((newCutter[0]+'.intScaleX'),storeX)
        
        mc.delete(deleteList)
        mc.select(newCutter)
        extNode = mc.polyExtrudeFacet( constructionHistory=True, keepFacesTogether = True, smoothingAngle=30, tk = gapV )
        cmdText = (extNode[0] + '.thickness = ' + newCutter[0] + '.intScaleX/' +  newCutter[0] + '.scaleX*' + str(gapV) + '*' + newCutter[0] + '.panelGap/' +  newCutter[0] + '.intPanelGap')
        mc.expression( s = cmdText, o = extNode[0], ae = True, uc = all)
        
        mc.select(newCutter)  
        mc.floatSliderGrp('gapSlider', e = True, en=1)
        mc.connectControl('gapSlider', (newCutter[0]+".panelGap"))  
        mc.select(newCutter)
    else:
        print 'function ONLY supple obj!' 
        
def removePanel():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    checkSelType = mc.filterExpand(sm=12 )
    if checkSelType != None:
        extrudeNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyExtrudeFace')
        if extrudeNode != None:
            mc.delete(extrudeNode)
        mc.polySelectConstraint(mode = 3, type = 0x8000, where =1)
        mc.polySelectConstraint(disable =True)
        holeEdge = mc.ls(sl=True,fl=True)
        if len(holeEdge)>0:
            mc.polyCloseBorder(ch = 0)
        mc.setAttr((newCutter[0]+'.statePanel'),0)
        mc.setAttr((newCutter[0]+'.stateCap'),1)
        mc.select(newCutter)
        mc.connectControl('gapSlider', (''))
        mc.floatSliderGrp('gapSlider', e = True, en=0)
    else:
        print 'function ONLY supple obj!' 
        
def makeSelPanel():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    checkSelType = mc.filterExpand(sm=12 )
    if checkSelType != None:
        extrudeNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyExtrudeFace')
        if extrudeNode != None:
            mc.delete(extrudeNode)
            
        gapV = []
        storeX = mc.getAttr( newCutter[0] + '.scaleX')
        gapV = mc.floatSliderGrp('gapSlider', q=True, v = True)
        if gapV == 0:
            gapV = 0.01
            mc.floatSliderGrp('gapSlider', e = True, v=0.01)
        mc.setAttr((newCutter[0]+'.panelGap'),gapV)
        mc.setAttr((newCutter[0]+'.intPanelGap'),gapV)
        mc.setAttr((newCutter[0]+'.intScaleX'),storeX)
        extNode = mc.polyExtrudeFacet( constructionHistory=True, keepFacesTogether = True, smoothingAngle=30, tk = gapV )
        cmdText = (extNode[0] + '.thickness = ' + newCutter[0] + '.intScaleX/' +  newCutter[0] + '.scaleX*' + str(gapV) + '*' + newCutter[0] + '.panelGap/' +  newCutter[0] + '.intPanelGap')
        mc.expression( s = cmdText, o = extNode[0], ae = True, uc = all)
        
        mc.select(newCutter)  
        mc.floatSliderGrp('gapSlider', e = True, en=1)
        mc.connectControl('gapSlider', (newCutter[0]+".panelGap"))  
        mc.setAttr((newCutter[0]+'.statePanel'),1)

    else:
        print 'function ONLY supple obj!'

    

def hideAllCutter():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    getCutters = mc.ls((beseMesh+'_cutterGrp|boxCutter*'),type = 'transform',l=True)
    mc.hide(getCutters)

def showLastCutter():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    currentOne = mc.ls(sl=True,fl=True)
    getCutters = mc.ls((beseMesh+'_cutterGrp|boxCutter*'),type = 'transform')
    checkVis = []
    
    for g in getCutters:
        checkme = mc.getAttr(g+'.visibility')
        if checkme == 1:
           checkVis.append(g) 
    if len(currentOne) == 1:
        checkSel = mc.getAttr(currentOne[0]+'.visibility')
        mc.hide(getCutters)
        if checkSel == 0:
            mc.setAttr((currentOne[0]+'.visibility'), 1)
        else:
            if len(checkVis) > 1:
                mc.select(currentOne)
                mc.showHidden(currentOne)
            elif len(checkVis) == 1:
                preCutter = 0
                for i in range(len(getCutters)):
                    if getCutters[i] == currentOne[0]:
                        preCutter = i - 1
                mc.select(getCutters[preCutter])
                mc.showHidden(getCutters[preCutter])
            else:
                mc.select(getCutters[-1])
                mc.showHidden(getCutters[-1])
    
    else:
        mc.hide(getCutters)
        mc.select(getCutters[-1])
        mc.showHidden(getCutters[-1])
    mc.setAttr((beseMesh+'_cutterGrp.visibility'), 1)

def showAllCutter():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    getCutters = mc.ls((beseMesh+'_cutterGrp|boxCutter*'),type = 'transform',l=True)
    mc.showHidden(getCutters)
    mc.setAttr((beseMesh+'_cutterGrp.visibility'), 1)

    
def toggleCutters():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    currentSel = mc.ls(sl= True)
    state = mc.getAttr((beseMesh+'_cutterGrp.visibility'))
    if state == 0:
        mc.setAttr((beseMesh+'_cutterGrp.visibility'), 1)
    else:
        mc.setAttr((beseMesh+'_cutterGrp.visibility'), 0)
    mc.select(currentSel)

def QlinkSliderRemove():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    mc.connectControl('fractionSlider', (''))
    mc.connectControl('segmentSlider', (''))
    mc.connectControl('depthSlider', (''))
    mc.connectControl('gapSlider', (''))

    
    mc.floatSliderGrp('fractionSlider',e=True, en= False ) 
    mc.intSliderGrp('segmentSlider',e=True, en= False ) 
    mc.floatSliderGrp('depthSlider',e=True, en= False )
    mc.floatSliderGrp('gapSlider',e=True, en= False )
    
                     
            
def QlinkSlider():
    QlinkSliderRemove()
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    if len(newCutter) < 1:
        newCutter = mc.ls(hl=True)
    if len(newCutter) < 1:
        print 'no cutter Selected'
    else:
        bevelNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyBevel3')
        if bevelNode != None:
            mc.floatSliderGrp('fractionSlider',e=True, en= True ) 
            mc.intSliderGrp('segmentSlider',e=True, en= True ) 
            mc.floatSliderGrp('depthSlider',e=True, en= True ) 
            mc.connectControl('fractionSlider', (bevelNode[0]+".fraction"))
            mc.connectControl('segmentSlider', (bevelNode[0]+".segments"))
            mc.connectControl('depthSlider', (bevelNode[0]+".depth"))
        extrudeNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyExtrudeFace')
        if extrudeNode != None:
            mc.floatSliderGrp('gapSlider',e=True, en= True )
            mc.connectControl('gapSlider', (newCutter[0]+".panelGap"))  


def jwMirror(axis):
    selPoly = mc.filterExpand(sm = 12)
    checkSel = mc.ls(sl=True,fl=True)
    
    #get center cv
    if selPoly == None:
        selPoly = mc.ls(hl=True)
    mc.FreezeTransformations()
    #get selected bbox
    bboxObj = mc.xform(selPoly[0] , q = True, ws =True, bb=True)
    
    #mirror or mirrorCut
    #mirror
    mirrorMode = 0
    
    if axis == 'x' :
        if bboxObj[3] > 0 and bboxObj[0] > 0:
            mirrorMode = 1
        elif  bboxObj[3] < 0 and bboxObj[0] < 0:
            mirrorMode = 1
    
    elif axis == 'y' :
        if bboxObj[4] > 0 and bboxObj[1] > 0:
            mirrorMode = 1
        elif  bboxObj[4] < 0 and bboxObj[1] < 0:
            mirrorMode = 1
    
    elif axis == 'z' :
        if bboxObj[5] > 0 and bboxObj[2] > 0:
            mirrorMode = 1
        elif  bboxObj[5] < 0 and bboxObj[2] < 0:
            mirrorMode = 1
    else:
        pass
                
    if mirrorMode == 1:
        mc.select(selPoly[0])
        cutterMirror(axis)
    #mirrorCut
    else:
        
        lengthObj=math.sqrt((math.pow(bboxObj[0]-bboxObj[3],2)+math.pow(bboxObj[1]-bboxObj[4],2)+math.pow(bboxObj[2]-bboxObj[5],2))/3)
        closeRange = lengthObj / 100
        
        bboxSel = mc.xform(q = True, ws =True, bb=True)
        midX = (bboxSel[3]+bboxSel[0])/2
        midY = (bboxSel[4]+bboxSel[1])/2
        midZ = (bboxSel[5]+bboxSel[2])/2
        inRangeCv = []
        if len(selPoly) == 1:
            vNo = mc.polyEvaluate(selPoly[0], v = True )
            checkPoint = 0
            if axis == 'x' :
                checkPoint = 0
            elif axis == 'y' :
                checkPoint = 1
            else:
                checkPoint = 2
        for i in range(vNo):
            positionV = mc.pointPosition((selPoly[0] +'.vtx[' + str(i) + ']') , w = True)
            length= math.sqrt(math.pow(positionV[checkPoint],2))
            if length <= closeRange:
               inRangeCv.append((selPoly[0] +'.vtx[' + str(i) + ']'))
            mc.select(inRangeCv, r=True)
        
        # push those point off center a bit then mirror cut
        if axis == 'x' :
            for n in inRangeCv:
                posiV = mc.pointPosition(n , w = True)
                if midX >= 0: 
                    mc.move((closeRange * -1.5) , posiV[1], posiV[2], n ,absolute=1)   
                else:
                    mc.move( (closeRange * 1.5) , posiV[1], posiV[2], n ,absolute=1) 
            cutPlane= mc.polyCut(selPoly[0], ws = True, cd = 'X' , df = True , ch =True)
            mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
            mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
            mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
            if midX > 0:
                mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 90) 
                mc.polyMirrorFace(selPoly[0],cutMesh =1, axis = 0, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
            else:
                mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), -90)
                mc.polyMirrorFace(selPoly[0],cutMesh =1, axis = 0, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
        
        if axis == 'y' :
            for n in inRangeCv:
                posiV = mc.pointPosition(n , w = True)
                if midY >= 0: 
                    mc.move(posiV[0], (closeRange  * -1.5) , posiV[2], n ,absolute=1)   
                else:
                    mc.move(posiV[0], (closeRange  * 1.5) , posiV[2], n ,absolute=1)   
            cutPlane= mc.polyCut(selPoly[0], ws = True, cd = 'Y' , df = True , ch =True)
            mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
            mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
            mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
            if midY > 0:
                mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'), -90) 
                mc.polyMirrorFace(selPoly[0],cutMesh =1, axis = 1, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
            else:
                mc.setAttr((cutPlane[0]+'.cutPlaneRotateX'), 90)
                mc.polyMirrorFace(selPoly[0],cutMesh =1, axis = 1, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
        
        if axis == 'z' :
            for n in inRangeCv:
                posiV = mc.pointPosition(n , w = True)
                if midZ >= 0: 
                    mc.move(posiV[0], posiV[1],(closeRange  * -1.5), n ,absolute=1)   
                else:
                    mc.move(posiV[0], posiV[1],(closeRange  * 1.5), n ,absolute=1)   
            cutPlane= mc.polyCut(selPoly[0], ws = True, cd = 'Z' , df = True , ch =True)
            mc.setAttr((cutPlane[0]+'.cutPlaneCenterX'), 0)
            mc.setAttr((cutPlane[0]+'.cutPlaneCenterY'), 0)
            mc.setAttr((cutPlane[0]+'.cutPlaneCenterZ'), 0)
            if midZ > 0:
                mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 0) 
                mc.polyMirrorFace(selPoly[0],cutMesh =1, axis = 2, axisDirection = 1, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
            else:
                mc.setAttr((cutPlane[0]+'.cutPlaneRotateY'), 180)
                mc.polyMirrorFace(selPoly[0],cutMesh =1, axis = 2, axisDirection = 0, mergeMode = 1, mergeThresholdType = 1, mergeThreshold =0.001, mirrorAxis = 0 ,mirrorPosition = 0 ,smoothingAngle= 30 ,flipUVs =0 ,ch = 0)
        mc.select(selPoly[0])
        mc.BakeNonDefHistory()

def cutterMirror(direction):
    listSel = mc.ls(sl=True, fl=True ,l=True)
    if len(listSel) > 0 and 'boxCutter' in listSel[0] and 'ArrayGrp' not in listSel[0]:
        mc.duplicate(rr=True, un=True)
        mc.group()
        if mc.objExists('tempPivot'):
            mc.delete('tempPivot')
        mc.rename('tempPivot')
        beseMesh = mc.textField("setMeshField", q = True, text = True)
        meshCOORD = mc.objectCenter(beseMesh,gl=True)
        mc.xform(ws=True,  pivots =[meshCOORD[0],meshCOORD[1],meshCOORD[2]])
        
        if direction == 'x':
            mc.setAttr( ('tempPivot.scaleX'),-1) 
        if direction == 'y':
            mc.setAttr( ('tempPivot.scaleY'),-1) 
        if direction == 'z':
            mc.setAttr( ('tempPivot.scaleZ'),-1) 
        mc.FreezeTransformations()
        
        mc.select(mc.listRelatives('tempPivot', c=True, f = True, typ='transform'))
        mc.select((beseMesh+'_cutterGrp'), add=True)
        mc.parent()
        listNew = mc.ls(sl=True, fl=True ,l=True)
        boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
        for l in listNew:
            shapeNode = mc.listRelatives(l, f = True, shapes=True)
            nextIndex = get_latest_free_multi_index((boolNode[0]+'.inputPoly'),0)
            mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((boolNode[0]+'.inputMat['+str(nextIndex)+']')),f=True)
            mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(nextIndex)+']')),f=True)
    
        mc.delete('tempPivot')
        for s in listSel:
            mc.setAttr((s+'.visibility'),0)
        mc.select(listNew)

def useOwnCutterShape():    
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    ownCutter = mc.ls(sl=True, fl=True ,l=True)
    if len(ownCutter) == 1 :
        if ('_cutterGrp') in ownCutter[0]:
            print 'shape already been used'
        else:
            mc.parent(ownCutter,(beseMesh+'_cutterGrp'))
            listOldCutter = mc.ls((beseMesh+'_cutterGrp|box*'))
            number = 1
            if len(listOldCutter)>0:
                for l in listOldCutter:
                    checkNumber = ''.join([n for n in l.split('|')[-1] if n.isdigit()])
                    if int(checkNumber) > int(number):
                        number = checkNumber
                        newNumber = int(1)+ int(number)
                        number = newNumber
            newName = 'boxCutter'+str(number)
            mc.rename(newName)
            newCutter = mc.ls(sl=True, fl=True)
            shapeNode = mc.listRelatives(newCutter[0], f = True, shapes=True)
            mc.setAttr( (shapeNode[0]+".overrideEnabled") , 1)
            mc.setAttr( (shapeNode[0]+".overrideShading") , 0)
            mc.setAttr( (shapeNode[0]+".castsShadows") , 0)
            mc.setAttr( (shapeNode[0]+".receiveShadows") , 0)
            mc.setAttr( (shapeNode[0]+".primaryVisibility") , 0)
            mc.setAttr( (shapeNode[0]+".visibleInReflections") , 0)
            mc.setAttr( (shapeNode[0]+".visibleInRefractions") , 0)
            mc.setAttr( (shapeNode[0]+'.overrideColor'), 28)
           
            boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
            if boolNode != None:
                nextIndex = get_latest_free_multi_index((boolNode[0]+'.inputPoly'),0)
                mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((boolNode[0]+'.inputMat['+str(nextIndex)+']')),f=True)
                mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(nextIndex)+']')),f=True)
            
                if not mc.attributeQuery('cutterDir', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='cutterDir',  dt= 'string')
                if not mc.attributeQuery('cutterType', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='cutterType',  dt= 'string')
                mc.setAttr((newCutter[0]+'.cutterDir'),e=True, keyable=True)
                mc.setAttr((newCutter[0]+'.cutterType'),e=True, keyable=True)
                
                if not mc.attributeQuery('statePanel', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='statePanel', at = "float" )
                if not mc.attributeQuery('panelGap', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='panelGap', at = "float" )
                if not mc.attributeQuery('intPanelGap', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='intPanelGap', at = "float" )
                if not mc.attributeQuery('intScaleX', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='intScaleX', at = "float" )
                if not mc.attributeQuery('stateCap', node = newCutter[0], ex=True ):
                    mc.addAttr(newCutter[0], ln='stateCap', at = "float" )
                mc.setAttr((newCutter[0]+'.stateCap'),1)
                mc.setAttr((newCutter[0]+'.statePanel'),0)
                mc.select(newCutter[0])
                mc.setAttr((newCutter[0]+'.cutterType'),'custom' ,type="string")
                mc.select(cl=True)
                showLastCutter()
    else:
        print 'nothing select!'
        
def cutterDulpicate():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    dulCutter = mc.ls(sl=True, fl=True , l=True)
    checkParent = dulCutter[0].split('|')
    if len(checkParent)>2 and 'boxCutter' in dulCutter[0] and 'cutterGrp' in dulCutter[0]: 
        beseMesh = mc.textField("setMeshField", q = True, text = True)
        mc.duplicate(rr = True, un=True)
        number = ''.join([n for n in checkParent[-1] if n.isdigit()])
        newNumber = int(1) + int(number)
        newName = 'boxCutter'+str(newNumber)
        while mc.objExists(newName):
            newNumber = newNumber +1
            newName = 'boxCutter'+str(newNumber)
        mc.rename(newName)
        newCutter = mc.ls(sl=True, fl=True)
        shapeNode = mc.listRelatives(newCutter[0], f = True, shapes=True)
        mc.setAttr( (shapeNode[0]+".overrideEnabled") , 1)
        mc.setAttr( (shapeNode[0]+".overrideShading") , 0)
        mc.setAttr( (shapeNode[0]+".castsShadows") , 0)
        mc.setAttr( (shapeNode[0]+".receiveShadows") , 0)
        mc.setAttr( (shapeNode[0]+".primaryVisibility") , 0)
        mc.setAttr( (shapeNode[0]+".visibleInReflections") , 0)
        mc.setAttr( (shapeNode[0]+".visibleInRefractions") , 0)
        boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
        if boolNode != None:
            nextIndex = get_latest_free_multi_index((boolNode[0]+'.inputPoly'),0)
            mc.connectAttr( (shapeNode[0]+".worldMatrix[0]"), ((boolNode[0]+'.inputMat['+str(nextIndex)+']')),f=True)
            mc.connectAttr( (shapeNode[0]+".outMesh"), ((boolNode[0]+'.inputPoly['+str(nextIndex)+']')),f=True)
            mc.select(newCutter[0])
            QlinkSlider()
            showLastCutter()
    else:
        print 'select geo is not an existing cutter!!'

def QChangeCutterDir():
    selObj = mc.ls(sl=1, fl=1,l=True, type='transform')
    if len(selObj) == 1:
        
        checkMasterDir = []
        checkMasterNumber = []
        checkMasterDis = []
        arraySample = []
        myType = checkInstType()
        if 'ArrayGrp' in selObj[0]:
            myType = checkInstType()
            arraySample = myType[0]
            if myType[1] != 'new':
                checkMasterDir = mc.getAttr(arraySample+'.arrayDirection')
                checkMasterNumber = mc.getAttr(arraySample+'.arrayNumber')
                checkMasterDis = mc.getAttr(arraySample+'.arrayOffset')
                checkMasterType = myType[1]
                if myType[1] == 'radial':
                    removeRadArray()
                else:
                    instRemove()
            selObj = mc.ls(sl=1, fl=1,l=True, type='transform')
	mc.setAttr((selObj[0]+'.rotateX'), 0)
        mc.setAttr((selObj[0]+'.rotateY'), 0)
        mc.setAttr((selObj[0]+'.rotateZ'), 0)        
	cutterDirection = mc.getAttr(selObj[0]+'.cutterDir')
        nextDir = []
        if cutterDirection == 'x':
            nextDir = 'Z'
            mc.setAttr((selObj[0]+'.cutterDir'),'z',type="string")
        elif cutterDirection == 'y':
             nextDir = 'X'
             mc.setAttr((selObj[0]+'.cutterDir'),'x',type="string")
        else:
             nextDir = 'Y'
             mc.setAttr((selObj[0]+'.cutterDir'),'y',type="string")
        parnetGrp = mc.listRelatives(selObj[0], parent =1, f=1)
        mc.group(em=True, name = (selObj[0]+'_offset'),parent = parnetGrp[0])
        newNode = mc.ls(sl=True,fl=True)
        mc.FreezeTransformations()
        sourcePivot = mc.xform(selObj[0], q=1, ws=1 ,rp=1) 
        mc.xform(newNode ,ws=1, piv = (sourcePivot[0],sourcePivot[1],sourcePivot[2]))
        mc.parent(selObj[0],newNode)
        mc.setAttr((newNode[0]+'.rotate' + nextDir), 90)
        newNode = mc.ls(sl=True,fl=True)
        parnetGrpRemove = mc.listRelatives(newNode[0], parent =1, f=1)
        mc.parent(newNode[0],parnetGrp)
        mc.delete(parnetGrpRemove)
        newNode = mc.ls(sl=True,fl=True)
        if myType[1] != 'new':
            if myType[1] == 'radial':
                instRadAdd(checkMasterDir)
            else:
                instAdd(checkMasterDir)
            mc.setAttr((newNode[0]+'.arrayNumber'),checkMasterNumber)
            mc.setAttr((newNode[0]+'.arrayOffset'),checkMasterDis)

def QBoxSmooth():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    if len(newCutter) == 1 and 'boxCutter' in newCutter[0]:
        if 'ArrayGrp' in newCutter[0]:
            myType = checkInstType()
            newCutter[0] = (myType[0])
        #in case gap exist
        extrudeNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyExtrudeFace')
        if extrudeNode != None: 
            removePanel()
        bevelNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyBevel3')
        bevelType = [] 
        getFrac = []
        getSeg = []
        getDep = []
        mc.select(newCutter)
        if bevelNode != None:
            mc.makeIdentity( newCutter, apply=True, scale=True ) 
            #record old setting
            getFrac = mc.getAttr(bevelNode[0]+'.fraction')
            getSeg = mc.getAttr(bevelNode[0]+'.segments')
            getDep = mc.getAttr(bevelNode[0]+'.depth')
            mc.delete(bevelNode)
            mc.DeleteHistory() 
        bevelNodeNew = mc.polyBevel3(newCutter[0], mv = 1, mvt =0.01, fn = 1, fraction = 0.5, offsetAsFraction = 1, autoFit = 1, depth = 1, mitering = 0, miterAlong = 0, chamfer = 1,  segments = 5,  ch = 1)
        if bevelNode != None: 
            mc.setAttr((bevelNodeNew[0]+'.fraction'),getFrac)
            mc.setAttr((bevelNodeNew[0]+'.segments'),getSeg)
            mc.setAttr((bevelNodeNew[0]+'.depth'),getDep)
    QlinkSlider()            
    mc.setAttr((newCutter[0]+'.cutterType'),'smooth',type="string")        
    
def QBoxBevel():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    if len(newCutter) == 1 and 'boxCutter' in newCutter[0]:
        if 'ArrayGrp' in newCutter[0]:
            myType = checkInstType()
            newCutter[0] = (myType[0])
        #in case gap exist
        extrudeNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyExtrudeFace')
        gapV = []
        if extrudeNode != None: 
            gapV = mc.getAttr(extrudeNode[0]+'.localTranslateZ')
            removePanel()
        bevelNode = mc.listConnections(mc.listHistory(newCutter,f=1),type='polyBevel3')
        bevelList = []
        bevelType = [] 
        getFrac = []
        getSeg = []
        getDep = []
        mc.select(newCutter)
        mc.makeIdentity( newCutter, apply=True, scale=True ) 
        if bevelNode != None:
            #record old setting
            getFrac = mc.getAttr(bevelNode[0]+'.fraction')
            getSeg = mc.getAttr(bevelNode[0]+'.segments')
            getDep = mc.getAttr(bevelNode[0]+'.depth')
            mc.delete(bevelNode)
            mc.DeleteHistory() 
        
        mc.select(newCutter)
        mc.polySelectConstraint(mode = 3, type = 0x0008, size=1)
        mc.polySelectConstraint(disable =True)
        triFind = mc.ls(sl=1,fl=1)
        mc.select(newCutter)
        mc.polySelectConstraint(mode = 3, type = 0x0008, size=3)
        mc.polySelectConstraint(disable =True)
        ngonFind = mc.ls(sl=1,fl=1)
        
        if len(triFind) > 0 or len(ngonFind) > 0:
            if len(triFind) > 0:
                mc.select(triFind)
            else:   
                mc.select(ngonFind)
            mc.select(newCutter) 
            mc.ConvertSelectionToFaces()
            mc.select(ngonFind,d=True)
            mc.ConvertSelectionToContainedEdges()
            bevelList = mc.ls(sl=1,fl=1)
        else:#case is cube
            checkNoCustom = mc.getAttr(newCutter[0]+'.cutterType')
            if checkNoCustom == 'custom':
                mc.select(str(newCutter[0] + '.e[4:5]'))
                mc.select(str(newCutter[0] + '.e[8:9]'), add =1 )
                bevelList = mc.ls(sl=1,fl=1)
            else:
                bevelList = str(newCutter[0] + '.e[8:11]')
        
        bevelNodeNew = mc.polyBevel3(bevelList, mv = 1, mvt =0.01, fn = 1, fraction = 0.5, offsetAsFraction = 1, autoFit = 1, depth = 1, mitering = 0, miterAlong = 0, chamfer = 1,  segments = 5,  ch = 1)
        if bevelNode != None: 
            mc.setAttr((bevelNodeNew[0]+'.fraction'),getFrac)
            mc.setAttr((bevelNodeNew[0]+'.segments'),getSeg)
            mc.setAttr((bevelNodeNew[0]+'.depth'),getDep)
        
        if extrudeNode != None:
            makeSelPanel()
        mc.select(newCutter)   
        QlinkSlider()
        instLink()
    else:
        mc.ConvertSelectionToEdges()
        selEdges =mc.filterExpand(ex =1, sm =32)
        if len(selEdges)>0:
            bevelNodeNew = mc.polyBevel3(selEdges, mv = 1, mvt =0.01, fn = 1, fraction = 0.5, offsetAsFraction = 1, autoFit = 1, depth = 1, mitering = 0, miterAlong = 0, chamfer = 1,  segments = 5,  ch = 1)
            newCutter=mc.ls(hl=True)
            mc.select(newCutter)
            QlinkSlider()
    mc.setAttr((newCutter[0]+'.cutterType'),'bevel',type="string")        
        
def QBoxBevelRemove():
    newCutter = mc.ls(sl=True,fl=True,type = 'transform')
    checkSelType = mc.filterExpand(sm=12 )
    if checkSelType != None:
        if 'ArrayGrp' in newCutter[0]:
            myType = checkInstType()
            newCutter[0] = (myType[0])
        checkNoCustom = mc.getAttr(newCutter[0]+'.cutterType')

        mc.makeIdentity( newCutter, apply=True, scale=True )
        shapeNode = mc.listRelatives(newCutter, f = True, shapes=True)
        bevelNode = mc.listConnections(mc.listHistory(shapeNode,f=1),type='polyBevel3')
        if bevelNode != None:
            mc.delete(bevelNode)
            mc.DeleteHistory()
        mc.setAttr((newCutter[0]+'.cutterType'),'none',type="string")
        instLink()


def addBevelDirectionAttr():
    newCutter = mc.ls(sl=True, fl=True)
    mc.setAttr((newCutter[0]+'.cutterDir'),'x',type="string")
    mc.setAttr((newCutter[0]+'.cutterType'),'bevel',type="string")


def onPressCutter():
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    member =mc.editDisplayLayerMembers((beseMesh+'_BoolResult'),q=True)
    snapMesh = (beseMesh +'_boolShape')
    vpX, vpY, _ = mc.draggerContext('meshPlace', query=True, anchorPoint=True)
    #print(vpX, vpY)
    pos = om.MPoint()
    dir = om.MVector()
    hitpoint = om.MFloatPoint()
    omui.M3dView().active3dView().viewToWorld(int(vpX), int(vpY), pos, dir)
    pos2 = om.MFloatPoint(pos.x, pos.y, pos.z)
    shortestD = 99999999999999999
    getMesh = []
    shortPosition= []
    mesh = snapMesh
    selectionList = om.MSelectionList()
    selectionList.add(snapMesh)
    dagPath = om.MDagPath()
    selectionList.getDagPath(0, dagPath)
    fnMesh = om.MFnMesh(dagPath)
    intersection = fnMesh.closestIntersection(
    om.MFloatPoint(pos2),
    om.MFloatVector(dir),
    None,
    None,
    False,
    om.MSpace.kWorld,
    99999,
    False,
    None,
    hitpoint,
    None,
    None,
    None,
    None,
    None)
    if intersection:
        x = hitpoint.x
        y = hitpoint.y
        z = hitpoint.z
        newName = mc.listRelatives(mesh, p=True )
        #intersection on closet obj, for multi intersections remove distrance check
        distanceBetween = math.sqrt(  ((float(pos2[0]) - hitpoint.x)**2)  + ((float(pos2[1]) - hitpoint.y)**2) + ((float(pos2[2]) - hitpoint.z)**2))
        if (shortestD > distanceBetween):
            shortestD = distanceBetween
            getMesh = newName
            shortPosition = [x, y, z]
    if len(shortPosition) > 0:
        mc.spaceLocator(p=(shortPosition[0],shortPosition[1],shortPosition[2]),n = (getMesh[0]+'_cutterPoint'))


def offPressCutter():
    sideNumber = mc.intSliderGrp('cutterSideSlider', q=1,  v = True)
    preRotAngle = []
    if sideNumber == 3:
        preRotAngle = 60
    elif sideNumber == 4:
        preRotAngle = 45
    elif sideNumber == 5:
        preRotAngle = 72
    elif sideNumber == 6:
        preRotAngle = 30 
    
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    boolNode = mc.listConnections(mc.listHistory((beseMesh+'_bool'),f=1),type='polyCBoolOp')
    nextIndex = get_latest_free_multi_index((boolNode[0]+'.inputPoly'),0)
    
    member =mc.editDisplayLayerMembers((beseMesh+'_BoolResult'),q=True)
    snapMesh =[]
    if member != None:
        snapMesh = member[0]
    mc.setToolTo('moveSuperContext')
    newlocator =mc.ls('*_cutterPoint',sl =True)
    if len(newlocator) > 0:
        snapObj=snapMesh
        mc.CenterPivot()
        mc.geometryConstraint( snapObj , newlocator[0], weight = 1)
        mc.normalConstraint( snapObj , newlocator[0], aimVector =(0, 1, 0) , upVector =(1, 0, 0))
        mc.rename('sampleLocCtrl')
        mc.polyCylinder(r = 1, h= 1.5 ,sx= sideNumber, sy =0, sz=0, rcp= 0 , cuv =3 ,ch=1)
        mc.rename('boxCutter'+str(nextIndex))
        newCutter = mc.ls(sl=True, fl=True)
        mc.setAttr( (newCutter[0]+'.rotateY'), preRotAngle)
        mc.makeIdentity((newCutter[0]),apply =1, t = 0, r = 1, s =0, n =0, pn= 1)
        #mc.CenterPivot()
        mc.group()
        mc.rename('sampleLoc')
        mc.xform(ws =True, piv =(0,0,0))
        refTopNode = mc.ls(sl = True,fl =True, type= 'transform')[0]
        mc.parent(refTopNode,'sampleLocCtrl')
        locX = mc.getAttr("sampleLocCtrl.localPositionX")
        locY = mc.getAttr("sampleLocCtrl.localPositionY")
        locZ = mc.getAttr("sampleLocCtrl.localPositionZ")
        mc.setAttr("sampleLoc.translateX", locX)
        mc.setAttr("sampleLoc.translateY", locY)  
        mc.setAttr("sampleLoc.translateZ", locZ)
        mc.setAttr("sampleLoc.rotateX", 0)
        mc.setAttr("sampleLoc.rotateY", 0)  
        mc.setAttr("sampleLoc.rotateZ", 0)  
        transDownNode = mc.listRelatives('sampleLoc', c=True,f=True )
        mc.select(transDownNode)
        mc.parent(w=True)
        mc.delete('sampleLocCtrl*')
        #cutter in position
        #add attr
        shapeNode = mc.listRelatives(newCutter[0], shapes=True ,f =True)
        mc.setAttr( (shapeNode[0]+".overrideEnabled") , 1)
        mc.setAttr( (shapeNode[0]+".overrideShading") , 0)
        mc.setAttr( (shapeNode[0]+".castsShadows") , 0)
        mc.setAttr( (shapeNode[0]+".receiveShadows") , 0)
        mc.setAttr( (shapeNode[0]+".primaryVisibility") , 0)
        mc.setAttr( (shapeNode[0]+".visibleInReflections") , 0)
        mc.setAttr( (shapeNode[0]+".visibleInRefractions") , 0)
        mc.setAttr( (shapeNode[0]+'.overrideColor'), 28)
              
        if not mc.attributeQuery('cutterDir', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='cutterDir',  dt= 'string')
        if not mc.attributeQuery('cutterType', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='cutterType',  dt= 'string')
        mc.setAttr((newCutter[0]+'.cutterDir'),e=True, keyable=True)
        mc.setAttr((newCutter[0]+'.cutterType'),e=True, keyable=True)
        
        if not mc.attributeQuery('cutterOp', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='cutterOp',  dt= 'string')
        mc.setAttr((newCutter[0]+'.cutterOp'),e=True, keyable=True)
        mc.setAttr((newCutter[0]+'.cutterOp'),'subs',type="string")
        
        if not mc.attributeQuery('statePanel', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='statePanel', at = "float" )
        if not mc.attributeQuery('panelGap', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='panelGap', at = "float" )
        if not mc.attributeQuery('intPanelGap', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='intPanelGap', at = "float" )
        if not mc.attributeQuery('intScaleX', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='intScaleX', at = "float" )
        if not mc.attributeQuery('stateCap', node = newCutter[0], ex=True ):
            mc.addAttr(newCutter[0], ln='stateCap', at = "float" )
        mc.setAttr((newCutter[0]+'.stateCap'),1)
        mc.setAttr((newCutter[0]+'.statePanel'),0)
        #group it
        mc.parent(newCutter,(beseMesh+'_cutterGrp'))
        fixBoolNodeConnection()
        addBevelDirectionAttr()
        QlinkSliderRemove()
        showLastCutter()
    
def goPressCutter(boxSide):
    mc.intSliderGrp('cutterSideSlider', e=1,  v = boxSide)
    ctx = 'meshPlace'
    if mc.draggerContext(ctx, exists=True):
        mc.deleteUI(ctx)
    mc.draggerContext(ctx, pressCommand = onPressCutter, rc = offPressCutter, name=ctx, cursor='crossHair')
    mc.setToolTo(ctx)
    


def setCutterBaseMesh():
    beseMesh = mc.ls(sl=True,fl=True,type='transform')
    if 'BoolGrp' in beseMesh[0]:
        removeGrp = beseMesh[0].replace('BoolGrp','')
        mc.textField("setMeshField" , e = True, text =  removeGrp)
    
    elif 'boxCutter' in beseMesh[0] or '_bool' in beseMesh[0] or '_cutterGrp' in beseMesh[0] or '_bakeCutterGrp' in beseMesh[0] or 'cutterBake' in beseMesh[0] or 'bakeCutter' in beseMesh[0] or 'bakeStep' in beseMesh[0]:
        topNode = mel.eval(("rootOf " + beseMesh[0]))
        removeGrp = topNode.replace('BoolGrp','')
        removeGrp = removeGrp.replace('|','')
        mc.textField("setMeshField" , e = True, text =  removeGrp)
    else:    
        mc.textField("setMeshField" , e = True, text =  beseMesh[0])
            
    beseMesh = mc.textField("setMeshField", q = True, text = True)
    if mc.objExists((beseMesh +'_cutterGrp')) == 0:
        mc.CreateEmptyGroup()
        mc.rename((beseMesh +'_cutterGrp'))
    
    if mc.objExists((beseMesh +'_bool')) ==0:
        mc.polyCube(w = 0.01, h=0.01, d=0.01 ,sx =1 ,sy= 1, sz= 1)
        mc.rename(beseMesh +'_preBoolBox') 
        mc.polyCBoolOp(beseMesh, (beseMesh +'_preBoolBox') , op= 2, ch= 1, preserveColor= 0, classification= 1, name= (beseMesh +'_bool')) 
    
    boolNode = mc.listConnections(mc.listHistory((beseMesh +'_bool'),f=1),type='polyCBoolOp')
    if (boolNode[0] != (beseMesh +'_myBool')):
        mc.rename(boolNode[0],(beseMesh +'_myBool'))
    mc.setAttr((beseMesh + '.visibility'), 0)
    baseShapeNode = mc.listRelatives(beseMesh, f = True)
    mc.rename(baseShapeNode , beseMesh+'Shape')
    mc.setAttr((beseMesh+'Shape.intermediateObject'), 0)
    
    if not mc.objExists((beseMesh +'_BoolResult')):
        mc.createDisplayLayer(name = (beseMesh +'_BoolResult'))
    mc.editDisplayLayerMembers( (beseMesh +'_BoolResult'),(beseMesh +'_bool')) # store my selection into the display layer
    mc.setAttr((beseMesh +'_BoolResult.displayType'),2)  
        
    if mc.objExists((beseMesh +'BoolGrp')) == 0:
        mc.select(beseMesh,(beseMesh +'_cutterGrp'),(beseMesh +'_bool'))
        mc.group()
        mc.rename((beseMesh +'BoolGrp'))
    checkGrp = mc.ls((beseMesh +'_cutterGrp'), l=True)
    
    if 'BoolGrp' not in checkGrp[0]:
        mc.parent(checkGrp[0],(beseMesh +'BoolGrp'))
        
    checkPreBoolGrp = mc.ls((beseMesh +'_preBoolBox'), l=True)
    
    if 'BoolGrp' not in checkPreBoolGrp[0]:
        mc.parent(checkPreBoolGrp[0],(beseMesh +'BoolGrp'))
        
    shapeNode = mc.listRelatives((beseMesh+'Shape'), s=True )
    if shapeNode != None:
        if len(shapeNode)>0 or shapeNode != None:
            mc.setAttr((shapeNode[0]+'.intermediateObject'), 0)
            mc.parent((beseMesh+'Shape'),(beseMesh +'BoolGrp'))
            mc.delete(beseMesh)
            mc.rename(beseMesh)
    mc.select(cl=True)


def jwSpeedCutUI():
    if mc.window("jwSpeedCutWin", exists = True):
        mc.deleteUI("jwSpeedCutWin")
    jwSpeedCutWin = mc.window("jwSpeedCutWin",title = "speedCut 1.0",w = 320,h = 780, mxb = False, s = 1 ,bgc = [0.14, 0.17, 0.2  ])
    mc.columnLayout()
    mc.text(l ='')
    mc.rowColumnLayout(nc=7 ,cw=[(1,60),(2, 5),(3,125),(4, 5),(5,50),(6, 5),(7,35)])
    mc.text(l ='BaseMesh')
    mc.text(l ='')
    mc.textField("setMeshField" ,ed =False,w = 100,bgc = [0.2,0.2,0.2])
    mc.text(l ='')
    mc.button('setBaseButton',w = 50, l= "Set", c = 'setCutterBaseMesh()', bgc = [0.24, 0.24, 0.24 ] )
    mc.text(l ='')
    mc.button('freeResultButton',w = 35, l= "Done", c = 'freeResultMesh()', bgc = [0.54, 0.24, 0.24 ] )
    mc.setParent( '..' )
    mc.separator( height=15, style='none' )
    
    mc.rowColumnLayout(nc=9 ,cw=[(1,40),(2,60),(3, 38),(4,5),(5, 38),(6,5),(7,38),(8,5),(9,58)])
    mc.text(l ='Sym',h=20)
    mc.radioButtonGrp('symDirButton', numberOfRadioButtons = 2, sl= 1, labelArray2 = ['+', '-'],cw2 =(30,20))
    
    mc.button( w = 30, l= "X", c = 'boolSymmetryCut("x")', bgc = [0.08,0.08,0.08] )
    mc.text(l ='')
    mc.button(w = 30, l= "Y", c ='boolSymmetryCut("y")', bgc =   [0.08,0.08,0.08])
    mc.text(l ='')
    mc.button(w = 30, l= "Z", c ='boolSymmetryCut("z")', bgc =   [0.08,0.08,0.08] )
    mc.text(l ='')
    mc.button(w = 40, l= "Freeze", c ='boolSymmetryFreeze()', bgc =  [0.54, 0.24, 0.24 ] )
    mc.setParent( '..' )
    mc.separator( height= 15, style='none' )
    
    mc.rowColumnLayout(nc=8 ,cw=[(1,40),(2, 58),(3,5),(4, 58),(5,5),(6,58),(7,5),(8,58)])
    mc.text(l ='Display',h=20)
    mc.iconTextButton('ToggleCutters',  w=40,style='textOnly', l= "Toggle", rpt = True, c = 'toggleCutters()', bgc = [0.24,0.24,0.24 ] )
    mc.text(l ='')
    mc.iconTextButton( w = 40, style='textOnly', l= "All", c = 'showAllCutter()', bgc =   [0.24, 0.24, 0.24] )
    mc.text(l ='')
    mc.iconTextButton( w = 40, style='textOnly', l= "None", c = 'hideAllCutter()', bgc =  [0.24, 0.24, 0.24] )
    mc.text(l ='',h=20)
    mc.iconTextButton( w = 40, style='textOnly', l= "Select", rpt = True, c = 'showLastCutter()', bgc = [0.24,0.24,0.24] )
    mc.setParent( '..' )
    mc.text(l ='')
    mc.separator( height= 5, style='none' )
    mc.text(l ='       ____________________  Cutter Options  _________________')
    mc.separator( height=10, style='none' )
    mc.rowColumnLayout(nc=5, cw=[(1,40),(2,50),(3,5),(4,110),(5,85)])
    mc.columnLayout()
    mc.text(l =' Cutter',h=50)
    mc.setParent( '..' )    
    mc.columnLayout()
    mc.separator( height= 1, style='none' )
    mc.iconTextButton('newCutButton', h= 23 ,w = 50,  style='textOnly', l= "[ * ]", rpt = True, c = 'goPressCutter(4)', bgc = [0.36, 0.6, 0.49] )
    mc.separator( height= 3, style='none' )
    mc.iconTextButton('drawCutButton', h= 23 ,w = 50,  style='textOnly', l= "Draw", rpt = True, c = 'goDraw()', bgc = [0.49,0.6,0.36 ] )
    mc.setParent( '..' ) 
    mc.text(l ='')
    mc.columnLayout()
    mc.rowColumnLayout(nc=5, cw=[(1,30),(2,5),(3,30),(4,5),(5,30)])
    mc.iconTextButton('triButton', w = 30,  style='textOnly', l= "3", rpt = True, c = 'goPressCutter(3)', bgc = [0.36, 0.6, 0.49])
    mc.text(l ='')
    mc.iconTextButton('pentaButton', w = 30,  style='textOnly', l= "5", rpt = True, c = 'goPressCutter(5)', bgc = [0.36, 0.6, 0.49] )
    mc.text(l ='')
    mc.iconTextButton('hexButton', w = 30,  style='textOnly', l= "6", rpt = True, c = 'goPressCutter(6)', bgc = [0.36, 0.6, 0.49] )
    mc.separator( height= 1, style='none' )
    mc.setParent( '..' ) 
    mc.columnLayout()
    mc.iconTextButton('selCutButton', w = 100,  style='textOnly', l= "Selected", rpt = True, c = 'useOwnCutterShape()', bgc = [0.26, 0.56, 0.39] )
    mc.setParent( '..' ) 
    mc.setParent( '..' ) 
    mc.columnLayout()
    mc.iconTextButton('dulCutButton', w = 80,  style='textOnly', l= "Duplicate", rpt = True, c = 'cutterDulpicate()', bgc = [0.24, 0.24, 0.24] )
    mc.separator( height= 4, style='none' )
    mc.iconTextButton('comCutButton', w = 80,  style='textOnly', l= "Combine", rpt = True, c = 'combineSelCutters()', bgc = [0.24, 0.24, 0.24] )
    mc.setParent( '..' )   
    mc.setParent( '..' )
    mc.separator( height= 5, style='none' )
    mc.columnLayout()
    mc.intSliderGrp('cutterSideSlider', en=1,  vis = 0, v = 4,   min = 3,    max = 6, s = 1, cw3 = [35,40,200] , label = "side  " ,field =True )
    mc.setParent( '..' )    
    mc.separator( height= 15, style='none' )
    mc.columnLayout()
    mc.rowColumnLayout(nc=6 ,cw=[(1,40),(2, 80),(3,5),(4, 80),(5,5),(6,80)])
    mc.text(l ='Mirror',h=20)
    mc.button( w = 50, l= "X", c = 'jwMirror("x")', bgc =  [0.20, 0.24, 0.24] )
    mc.text(l ='')
    mc.button(w = 50, l= "Y", c = 'jwMirror("y")', bgc =   [0.20, 0.24, 0.24] )
    mc.text(l ='')
    mc.button(w = 50, l= "Z", c = 'jwMirror("z")', bgc =   [0.20, 0.24, 0.24] )
    mc.setParent( '..' )
    mc.separator( height= 5, style='none' )
    
    mc.rowColumnLayout(nc=6, cw=[(1,40),(2,80),(3,5),(4,80),(5,5),(6,80)])
    mc.text(l ='Rotate',h=20)
    mc.iconTextButton(w = 50, style='textOnly', l= "Toggle",rpt = True, c = 'QChangeCutterDir()', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.iconTextButton(w = 50,style='textOnly' , l= "Align", rpt = True, c = 'alignCutterToBase()', bgc = [0.28,0.28,0.28] )
    mc.text(l ='')
    mc.setParent( '..' )
    mc.separator( height=15, style='none' )
  
    mc.text(l ='       ________________________ Control   _____________________')
    mc.text(l ='')

    mc.rowColumnLayout(nc=3 ,cw=[(1,240),(2,12),(3,30)])
    mc.columnLayout()
    mc.floatSliderGrp('fractionSlider', en=0, v = 0.2, min = 0.001, max = 1,  s = 0.01, cw3 = [55,40,140] , label = " Fraction" ,field =True)
    mc.intSliderGrp('segmentSlider',    en=0, v = 1,   min = 1 ,    max = 10,  fmx = 20, s = 1, cw3 = [55,40,140] , label = "Segments" ,field =True)
    mc.floatSliderGrp('depthSlider',    en=0, v = 1,   min = -1 ,   max = 1, fmn = -3, fmx = 3, s = 1,  cw3 = [55,40,140] , label = "Depth" ,field =True)
    mc.floatSliderGrp('gapSlider',      en=0, v = 0.3, min = 0.01, max = 1,  s = 0.01, cw3 = [55,40,140] , label = "Gap   " ,field =True)
    mc.setParent( '..' )
    mc.text(l ='',h=20)
    mc.button( w = 30, l= "Link", c = 'QlinkSlider()', bgc = [0.08,0.08,0.08] )
    mc.setParent( '..' )
    mc.text(l ='')
    mc.rowColumnLayout(nc=6, cw=[(1,40),(2,80),(3,5),(4,80),(5,5),(6,80)])
    mc.text(l ='Type',h=20)
    mc.button( w = 50, l= "Bevel", c = 'QBoxBevel()', bgc = [0.08,0.08,0.08] )
    mc.text(l ='')
    mc.button(w = 50, l= "Smooth", c = 'QBoxSmooth()', bgc =   [0.08,0.08,0.08])
    mc.text(l ='')
    mc.button(w = 50, l= "X", c = 'QBoxBevelRemove()', bgc =   [0.08,0.08,0.08] )
    mc.setParent( '..' )
    mc.separator( height=5, style='none' )
    mc.rowColumnLayout(nc=6, cw=[(1,40),(2,80),(3,5),(4,80),(5,5),(6,80)])
    mc.text(l ='Panel',h=10)
    mc.button('makePanelButton', w = 50,  l= "Panel/Gap", c = 'toggleCapPanel()', bgc = [0.08,0.08,0.08] )
    mc.text(l ='')
    mc.button('reBuildButton', w = 50, l= "ReBuild", c = 'reBuildCutter()', bgc = [0.08,0.08,0.08] )
    mc.text(l ='')
    mc.button('removePanelButton', w = 50,  l= "X", c = 'removePanel()', bgc = [0.08,0.08,0.08] )
    mc.setParent( '..' )
    mc.separator( height= 5, style='none' )

    mc.text(l ='       _______________________  Pattern  _______________________')
    mc.text(l ='')
    mc.rowColumnLayout(nc=3 ,cw=[(1,240),(2,12),(3,30)])
    mc.columnLayout()
    mc.intSliderGrp('instNumSlider', en=0,  v = 1,   min = 1,    max = 10,  fmx = 20 ,s = 1, cw3 = [35,40,160] , label = "Num  " ,field =True,dc = 'instReNew()' )
    mc.floatSliderGrp('disSlider', en=0,  v = 1,   min = -3,    max = 3,  fmx = 20 ,fmn = -20, s = 0.01, cw3 = [35,40,160] , label = "Dist  ", field =True, )
    mc.setParent( '..' )
    mc.text(l ='',h=5)
    mc.button('instLinkButton', w = 30, l= "Link", c = 'instLink()', bgc = [0.24, 0.20, 0.24] )
    mc.setParent( '..' )
    mc.separator( height=5, style='none' )
    mc.columnLayout()
    mc.rowColumnLayout(nc=8 ,cw=[(1,40),(2, 10),(3,105),(4,45),(5,5),(6,45),(7,5),(8,30)])
    mc.text(l ='Array')
    mc.text(l ='')
    mc.radioButtonGrp('arrayTypeButton', numberOfRadioButtons = 2, sl= 1, labelArray2 = ['Lin', 'Rad'],cc = 'instTypeCommandChange()',cw2 =(50,80))
    mc.button( w = 45, l= "Switch", c = 'instTypeToggle()', bgc = [0.24, 0.20, 0.24] )
    mc.text(l ='')
    mc.button( w = 45, l= "Done", c = 'instBake()', bgc = [0.24, 0.20, 0.24] )
    mc.text(l ='')
    mc.button( w = 30, l= "X", c = 'removeArrayGrp()', bgc = [0.24, 0.20, 0.24] )
    mc.setParent( '..' )
    mc.separator( height=5, style='none' )
    mc.rowColumnLayout(nc=6 ,cw=[(1,40),(2, 78),(3,5),(4, 78),(5,5),(6,78)])
    mc.text(l ='')
    mc.button('instXButton', w = 50, l= "X", c = 'instAdd("X")', bgc = [0.24, 0.20, 0.24] )
    mc.text(l ='')
    mc.button('instYButton', w = 50, l= "Y", c = 'instAdd("Y")', bgc = [0.24, 0.20, 0.24] )
    mc.text(l ='')
    mc.button('instZButton' ,w = 50, l= "Z", c = 'instAdd("Z")', bgc = [0.24, 0.20, 0.24] )
    mc.setParent( '..' )
    
    mc.separator( height=15, style='none' )
    mc.text(l ='       ______________________  Box Draw  _____________________')
    mc.text(l ='')
    mc.rowColumnLayout(nc=9, cw=[(1,40),(2,60),(3,5),(4,60),(5,5),(6,60),(7,5),(8,60),(9,20)])
    mc.text(l ='',h=10)
    mc.button('snapGridVisButton', w = 50,   l= "On/Off", c = 'drawGirdToggle()', bgc = [0.36, 0.6, 0.49] )
    mc.text(l ='')
    mc.button('snapGridPointVisButton', w = 50,   l= "Point", c = 'goPressDraw()', bgc = [0.49, 0.6, 0.36] )
    mc.text(l ='')
    mc.button('cureveDrawButtton', w = 50,  l= "Draw", c = 'mc.CVCurveToolOptions()',bgc = [0.24, 0.24, 0.24] )
    mc.text(l ='')
    mc.button('buildBlockButton', w = 50,   l= "Block",  c = 'makeDrawBlock()', bgc = [0.24, 0.24, 0.24] )
    mc.textField("camPlane" ,ed =False,w = 20,vis=0)
    mc.setParent( '..' )
    mc.separator( height=15, style='none' )    
    mc.columnLayout()
    mc.intSliderGrp('snapGirdSize', en=0, v = 10,  min = 1, max = 50,  fmx=100 ,s = 1, cw3 = [35,40,200] , label = "Grid  " ,field =True, dc ='resizeSnapGrid()')
    mc.intSliderGrp('snapGirdRot',en=0, v = 0,   min = 0, max = 90,  s = 1, cw3 = [35,40,200], label = "Rot   " ,field =True)
    mc.setParent( '..' )
    
    mc.separator( height= 5, style='none' )
    mc.text(l ='       ________________  Bake Cutter Options  _______________')
    mc.separator( height=15, style='none' )
    mc.rowColumnLayout(nc=6, cw=[(1,40),(2,80),(3,5),(4,80),(5,5),(6,80)])
    mc.text(l ='',h=10)
    mc.button('bakeUnSelButton', w = 50,   l= "Unselect", c = 'bakeUnselectCutter()', bgc = [0.1,0.2,0.2] )
    mc.text(l ='')
    mc.button('bakeAllButton', w = 50,   l= "All", c = 'bakeCutter()', bgc = [0.2,0.1,0.1] )
    mc.text(l ='')
    mc.button('bakeRestoreButton', w = 50,  l= "Restore",c = 'restoreCutter()', bgc = [0.08,0.08,0.08] )
    mc.text(l ='')
    mc.setParent( '..' )

    mc.text(l ='       _______________  PreView Boolean Bevel  ______________')
    mc.separator( height=15, style='none' )
    mc.rowColumnLayout(nc=4 ,cw=[(1,40),(2, 185),(3,5),(4, 58)])
    mc.text(l ='',h=20)
    mc.iconTextButton('preBevelButton',  w=40,style='textOnly', l= "On / Off", rpt = True, c = 'preBevelToggle()', bgc = [0.49,0.6,0.36 ] )
    mc.text(l ='',h=20)
    mc.iconTextButton('preBevelSettingButton',  w=40,style='textOnly', l= "Setting", rpt = True, c = 'bevelPreviewSetting()', bgc =[0.24, 0.24, 0.24] )
    mc.text(l ='',h=20)
    mc.setParent( '..' )
    mc.frameLayout( 'bevelPreSettingLayer', labelVisible = 0,vis = 0)
    mc.floatSliderGrp('offsetSliderPre', en=1, v = 0.1, min = 0.001, max = 1, fmx = 10, s = 0.01, cw3 = [55,40,180] , label = "Offset   " ,field =True)
    #mc.intSliderGrp('segmentSliderPre',  en=1, v = 2,   min = 1 ,    max = 5, s = 1,    cw3 = [55,40,180] , label = "Segments" ,field =True)
    #mc.intSliderGrp('miteringSliderPre', en=1, v = 1,   min = 0, max = 3,  s = 1, cw3 = [55,40,180] , label = "  Mitering " ,field =True)
    mc.text(l ='',h=20)
    mc.showWindow(jwSpeedCutWin)
    mc.window("jwSpeedCutWin",e=True,w = 320,h = 770)
    mc.commandEcho( state=False )
jwSpeedCutUI()
