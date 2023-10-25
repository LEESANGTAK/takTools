"""
------------------------------------------
hairTools.py
Author: David Bokser
email: me@davidbokser.com

Website : http://www.davidbokser.com
------------------------------------------

Helps create multi-level hair curves along a poly mesh, with tools
for styling and trimming.

Usage:
import modeling.hairTools.hairTools as hairTools
hairTools.hairballUI()

COPYRIGHT DAVID BOKSER 2010-2013.
================================================================

11/19/2015
Modified by Sang-tak Lee
"""

import maya.cmds as cmds
import maya.mel as mel
import copy
import random
import maya.OpenMaya as OpenMaya

def hairballUI():
	winName = 'hairBallWin'
	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)
	cmds.window(winName, title="Hair Guide Curve Tools", widthHeight=(200, 55) )

	cmds.scrollLayout( 'scrollLayout' )
	cmds.columnLayout( adjustableColumn=True )
	cmds.frameLayout( label='Create with Tube', labelAlign='center', borderStyle='etchedIn' )
	cmds.columnLayout( adjustableColumn=True )
	cmds.button( label='Create Center Curve', command=createCenterCurve, ann = 'Select a polygon tube object. If fail select border edge loop.')
	densityField = cmds.floatSliderGrp( label='Threshold', cw3=[80, 80, 120], precision=2, field=True, value = 1.5, fs=.01, minValue=.01, maxValue=1.0, fmx=200.0 )
	layerField = cmds.intSliderGrp( label='Layers', cw3=[80, 80, 120], field=True, value = 2, minValue=1, maxValue=15, fmx=200 )
	twistField = cmds.floatSliderGrp( label='Curl', cw3=[80, 80, 120], precision=2, field=True, value = 0, fs=.01, minValue=-1.0, maxValue=1.0, fmx=5.0, fmn=-5.0 )
	cmds.button( label='Create Curves with Settings', command='''
import maya.cmds as cmds
import modeling.hairTools
hairTools.makeHair(cmds.ls(sl=True, fl=True), cmds.floatSliderGrp("%s", q=True, value=True), cmds.intSliderGrp("%s", q=True, v=True), cmds.floatSliderGrp("%s", q=True, value=True))
''' % (densityField, layerField, twistField), ann = 'Select a polygon tube object. If fail select border edge loop.')
	cmds.setParent( '..' )
	cmds.setParent( '..' )

	cmds.frameLayout( label='Noise & Smooth', labelAlign='center', borderStyle='etchedIn' )
	cmds.columnLayout( adjustableColumn = True)
	rand1Field = cmds.floatSliderGrp( label='Start', cw3=[80, 80, 120], precision=2, field=True, value = .1, fs=.1, minValue=0, maxValue=5.0, fmx=200.0 )
	rand2Field = cmds.floatSliderGrp( label='Middle', cw3=[80, 80, 120], precision=2, field=True, value = .4, fs=.1, minValue=0, maxValue=5.0, fmx=200.0 )
	rand3Field = cmds.floatSliderGrp( label='End', cw3=[80, 80, 120], precision=2, field=True, value = .6, fs=.1, minValue=0, maxValue=5.0, fmx=200.0 )
	cmds.button( label='Noise Curve with Settings', command='''
import maya.cmds as cmds
import modeling.hairTools
hairTools.randomizeHair(cmds.ls(sl=True), [cmds.floatSliderGrp("%s", q=True, value=True), cmds.floatSliderGrp("%s", q=True, v=True), cmds.floatSliderGrp("%s", q=True, v=True)])
	''' % (rand1Field, rand2Field, rand3Field))
	cmds.button( label='Smooth Curve', command='cmds.SmoothHairCurves()', ann = 'Select curve(s).')
	cmds.setParent( '..' )
	cmds.setParent( '..' )

	cmds.frameLayout( label='Trim', labelAlign='center', borderStyle='etchedIn' )
	cmds.columnLayout( adjustableColumn = True)
	cmds.button( label='Cut Curve with Scalp', command=cutCrvOnIntersection, ann = 'Select curves and select a poly or nurbs scalp.')
	cmds.button( label='Snap Curve Start Point to Scalp', command=snapToScalp, ann = 'Select curves and select a poly or nurbs scalp.')
	minTrimField = cmds.floatSliderGrp( label='Min Length', cw3=[80, 80, 120], precision=2, field=True, value = .75, fs=.1, minValue=0.1, maxValue=1.0 )
	percentTrimField = cmds.floatSliderGrp( label='Percent to Trim', cw3=[80, 80, 120], precision=2, field=True, value = .5, fs=.1, minValue=0.1, maxValue=1.0 )
	cmds.button( label='Cut from End Tip with Settings', command='''
import maya.cmds as cmds
import modeling.hairTools
hairTools.trimHair(cmds.ls(sl=True, fl = True), cmds.floatSliderGrp("%s", q=True, value=True), cmds.floatSliderGrp("%s", q=True, value=True))
	''' % (minTrimField, percentTrimField), ann = 'Select curve(s).')
	cmds.setParent( '..' )
	cmds.setParent( '..' )

	cmds.showWindow( winName )

	cmds.window(winName, e=True, w=305, h=420)

def makeHair(selList, density, layers, twist=0.0):
	if len(selList) > 1:
		firstLoop = selList
	else:
		sel = selList[0]
		cmds.select('%s.e[3]' %sel)
		cmds.polySelectSp(loop = True)
		firstLoop = cmds.ls(sl = True, fl = True)
		cmds.hide(sel)

	firstLoop = cmds.ls(cmds.polyListComponentConversion(firstLoop, fe=True, fv=True, tv=True), fl=True)

	# DO A LITTLE ERROR CHECKING TO SEE IF WE GOT WHAT WE NEED
	neighbor = getNeighboringEdgeloops(firstLoop)
	if len(neighbor) != len(firstLoop):
		mel.eval('warning "Selected edgeloop is not a border loop. Please select a border loop and try again."')
		return None

	# CREATE THE HULL CURVES
	if twist < 0:
		numIntermediates = round((twist*-1)/.1)-1
	else:
		numIntermediates = round(twist/.1)-1
	if numIntermediates < 0:
		numIntermediates = 0
	hullCurves = makeHullCurves(firstLoop, numIntermediates)

	twist /= numIntermediates + 1.0

	objName = firstLoop[0].split('.')[0]

	# CREATE ALL THE HAIR CURVES
	allHairCurves = []
	for i in range(layers):
		for curve in hullCurves:
			s = (i+1)/(layers*1.0)
			cmds.setAttr(curve+'.scale', s, s, s, type='double3')
		allHairCurves += makeHairCurves(hullCurves, density, twist)

	# DO SOME SPRING CLEANING
	cmds.delete(hullCurves)
	for i in range(len(allHairCurves)):
		curveNum = str(i+1)
		allHairCurves[i] = cmds.rename(allHairCurves[i], '%s_%sCRV' % (objName, curveNum))

	if len(allHairCurves) > 0:
		hairGrp = cmds.rename(cmds.group(allHairCurves), objName + '_hairCurves')
	else:
		mel.eval('warning "No hair curves made. Perhaps Density value is too high."')


def makeHullCurves(firstLoop, numIntermediates=0):
	verts = cmds.ls(cmds.polyListComponentConversion(firstLoop, fe=True, fv=True, tv=True), fl=True)

	edgeVerts = orderEdgeloopVerts(verts)
	firstVert = edgeVerts[0]
	dirVert = edgeVerts[1]

	obj = verts[0].split('.')[0]
	numObjVerts = cmds.polyEvaluate(obj, vertex=True)

	numEdges = int(numObjVerts / len(edgeVerts))

	if numObjVerts%len(edgeVerts) != 0:
		mel.eval('warning("Number of verts in edge loops must be the same throughout mesh.")')
		return False

	usedVerts = []
	edgeCurves = []
	edgeLoops = []
	usedVertOrder = []
	for i in range(numEdges):
		# MAKE CURVES
		currentEdge = makeCurveFromVerts(edgeVerts)[0]
		if i != 0 and numIntermediates != 0:
			edgeCurves += makeIntermediateCurves(edgeCurves[-1], currentEdge, numIntermediates)
		edgeCurves.append(currentEdge)

		# KEEP TRACK OF USED VERTS
		for vert in edgeVerts:
			if vert not in usedVerts:
				usedVerts.append(vert)
		usedVertOrder.append(copy.copy(usedVerts))

		# GET NEXT LOOP
		edgeLoops.append(edgeVerts)
		neighbors = cmds.ls(getNeighboringEdgeloops(edgeVerts), fl=True)
		edgeVerts = []
		for vert in neighbors:
			if vert not in usedVerts:
				edgeVerts.append(vert)
		if len(edgeVerts):
			firstVert = findCorrespondingVertInLoop(firstVert, edgeVerts)
			dirVert = findCorrespondingVertInLoop(dirVert, edgeVerts)
			edgeVerts = orderEdgeloopVerts(edgeVerts, start=firstVert, direction=dirVert)

	return edgeCurves

def makeIntermediateCurves(curve1, curve2, numIntermediates=1, close=True):
	cShape1 = cmds.listRelatives(curve1, shapes=True)[0]
	cShape2 = cmds.listRelatives(curve2, shapes=True)[0]

	nucmdsV1 = cmds.getAttr(cShape1+'.spans') + cmds.getAttr(cShape1+'.degree')
	nucmdsV2 = cmds.getAttr(cShape2+'.spans') + cmds.getAttr(cShape2+'.degree')

	if nucmdsV1 != nucmdsV2:
		mel.eval('warning "Number of CVs between curves are not equal. Can\'t create intermediate curves"')
		return []

	step = 1.0/(numIntermediates+1)
	allCurves = []
	for p in range(1, int(numIntermediates)+1):
		points = []
		for i in range(cmds.getAttr(cShape1+'.spans')):
			p1 = cmds.pointPosition('%s.cv[%i]' % (curve1,i))
			p2 = cmds.pointPosition('%s.cv[%i]' % (curve2,i))
			v = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
			p3 = (p1[0]+(v[0]*step*p), p1[1]+(v[1]*step*p), p1[2]+(v[2]*step*p))
			points.append(p3)
		allCurves += makeCurveFromPoints(points, close)
		allCurves[-1] = cmds.rename(allCurves[-1], 'intCurve1')
	return allCurves

def orderEdgeloopVerts(verts, start=None, direction=None):
	'''
	Orders a list of verts in an edge loop.
	Assumes the verts are actually in an edge loop,
	otherwise will freeze Maya, so be WARNED!!
	'''
	allEdgeVerts = copy.copy(verts)

	orderedVerts = []
	if not start:
		start = verts.pop(0)
	else:
		if start in verts:
			verts.remove(start)
		else:
			mel.eval('warning("given start vert is not in edge verts, using default")')
			start = verts.pop(0)
	if direction and direction in verts:
		verts.remove(direction)
	else:
		adjacentVerts = cmds.ls(cmds.polyListComponentConversion(cmds.polyListComponentConversion(start, fv=True, te=True), fe=True, tv=True),fl=True)
		for vert in adjacentVerts:
			if vert in verts:
				direction = vert
		verts.remove(direction)

	orderedVerts.append(start)
	orderedVerts.append(direction)

	while len(verts) > 1:
		adjacentVerts = cmds.ls(cmds.polyListComponentConversion(cmds.polyListComponentConversion(orderedVerts[-1], fv=True, te=True), fe=True, tv=True), fl=True)
		for vert in adjacentVerts:
			if vert in verts:
				orderedVerts.append(vert)
				verts.remove(orderedVerts[-1])

	orderedVerts.append(verts[0])
	return orderedVerts

def makeCurveFromVerts(verts, close=True):
	p = []
	for vert in verts:
		p.append(cmds.pointPosition(vert))

	return makeCurveFromPoints(p, close)

def makeCurveFromPoints(p, close=True):
	curve = cmds.curve(p=p, d=3)
	if close:
		curve = cmds.closeCurve(curve, ps=0, rpo=1, bb=0.5, bki=0, p=0.1)
	curve = cmds.rebuildCurve(curve, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=0, s=4, d=3, tol=0.000129167)

	cmds.xform(curve, centerPivots=True)

	return curve

def getNeighboringEdgeloops(edgeLoop):
	'''
	Get the neighboring edge loop.
	Takes in and returns verts, not edges
	'''
	expandedVerts = cmds.ls(cmds.polyListComponentConversion(cmds.polyListComponentConversion(edgeLoop, fv=True, te=True), fe=True, tv=True), fl=True)
	expandedEdgeVerts = cmds.ls(edgeLoop, fl=True)

	for vert in expandedEdgeVerts:
		if vert in expandedVerts:
			expandedVerts.remove(vert)

	return cmds.ls(expandedVerts, fl=True)

def findCorrespondingVertInLoop(vert, edgeLoop):
	'''
	Finds a vert on the edgeLoop whose edge is shared with the given vert
	'''
	nearestVerts = cmds.ls(cmds.polyListComponentConversion(cmds.polyListComponentConversion(vert, fv=True, te=True), fe=True, tv=True), fl=True)
	for vert in nearestVerts:
		if vert in edgeLoop:
			return vert

	return None

def makeHairCurves(hullCurves, d, twist = 0.0):
	'''
	Populate a hull with hair curves based on arclen of the biggest curve
	'''
	largestArclen = 0
	for curve in hullCurves:
		arclen = cmds.arclen(curve)
		if arclen > largestArclen:
			largestArclen = arclen

	nucmdsurves = largestArclen / (d * 1.0)

	allCurves = []
	for i in range(int(nucmdsurves)):
		allCurves.append(makeHairCurve(hullCurves, i/nucmdsurves, twist))

	return allCurves

def makeHairCurve(hullCurves, u, twist=0.0):
	'''
	Create a curve through a series of hull curves by u parameter
	'''
	p = []
	i = 0
	for hull in hullCurves:
		p.append(cmds.pointPosition('%s.u[%f]' % (hull, (u+(twist*i))%1.0 ) ))
		i+=1

	curve = cmds.curve(p=p, d=3)
	curve = cmds.rebuildCurve(curve, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=0, s=4, d=3, tol=0.000129167)

	cmds.xform(curve, centerPivots=True)

	return curve

def randomizeHair(curves, rMult = []):
	'''
	random.randomizes the cvs on a set of selected curves.
	Takes in an array that will be multiplied against the random.random value
	so that the user has more control of random.randomization along the curve.
	'''

	# FIND THE MAX NUMBER OF CVS
	longestCVCount = 0
	for curve in curves:
		nucmdsV = cmds.getAttr( curve+'.degree' ) + cmds.getAttr( curve+'.spans' )
		if nucmdsV > longestCVCount:
			longestCVCount = nucmdsV

	# GET MULT MODIFIER VALUES FOR EACH CV
	numMult = len(rMult)-1
	nucmdsVSplit = longestCVCount / numMult
	cvMult = []
	for i in range(longestCVCount):
		p = i/nucmdsVSplit
		m = (i%nucmdsVSplit)/(nucmdsVSplit*1.0)
		try:
			dif = rMult[p+1] - rMult[p]
		except:
			dif = rMult[p]
		cvMult.append( (m*dif)+rMult[p] )

	for curve in curves:
		nucmdsV = cmds.getAttr( curve+'.degree' ) + cmds.getAttr( curve+'.spans' )
		for i in range(nucmdsV):
			rx = cvMult[i] * (random.random() - .5)
			ry = cvMult[i] * (random.random() - .5)
			rz = cvMult[i] * (random.random() - .5)
			cmds.move(rx, ry, rz, '%s.cv[%i]' % (curve, i), r=True)

def trimHair(curves, min, percent):
	'''
	random.randomly trim hair curves for more variation in length
	'''

	selCrvs = copy.copy(curves)

	percentOfCurves = int(len(curves) * percent)
	for i in range(percentOfCurves):
		activeCurve = curves.pop(int(random.random()*len(curves)))
		r = (random.random() * (1.0 - min)) + min
		cmds.delete(cmds.detachCurve('%s.u[%f]' % (activeCurve, r), ch=False, cos=True, rpo=True)[0])

	cmds.select(selCrvs)

def createCenterCurve(*args):
	selList = cmds.ls(sl = True, fl = True)
	if len(selList) > 1:
		firstLoop = selList
	else:
		sel = selList[0]
		cmds.select('%s.e[3]' %sel)
		cmds.polySelectSp(loop = True)
		firstLoop = cmds.ls(sl = True, fl = True)

	firstLoop = cmds.ls(cmds.polyListComponentConversion(firstLoop, fe=True, fv=True, tv=True), fl=True)

	# DO A LITTLE ERROR CHECKING TO SEE IF WE GOT WHAT WE NEED
	neighbor = getNeighboringEdgeloops(firstLoop)
	if len(neighbor) != len(firstLoop):
		mel.eval('warning "Selected edgeloop is not a border loop. Please select a border loop and try again."')
		return None

	# CREATE THE HULL CURVEs
	hullCurves = makeHullCurves(firstLoop)

	objName = firstLoop[0].split('.')[0]

	# CREATE ALL THE HAIR CURVES
	for curve in hullCurves:
		s = 0
		cmds.setAttr(curve+'.scale', s, s, s, type='double3')
	hairCurve = makeHairCurve(hullCurves, .5)

	# DO SOME SPRING CLEANING
	cmds.delete(hullCurves)
	hairCurve = cmds.rename(hairCurve, '%s_CenterCRV' % objName)

	cmds.select(hairCurve, r = True)
	return hairCurve

def trimFromBeginning(inputCurves, shortestLength):
	newCurves = []
	for obj in inputCurves:
		parent = cmds.listRelatives(obj, parent=True)
		r = random.random()*(1-shortestLength)
		obj = cmds.rebuildCurve(obj,  ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=0, s = 10, d = 3, tol = 0)[0]
		curves = cmds.detachCurve( '%s.u[%f]' % (obj, r), ch=0, cos=True, rpo=1 )
		cmds.delete(curves[-1])
		cmds.rebuildCurve(curves[0], ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt= 0, s = 0, d = 3, tol = 0)
		curves[0] = cmds.rename(curves[0], obj)
		if parent:
			curves[0] = cmds.parent(curves[0], parent)[0]

		newCurves.append(curves[0])

	return newCurves

def snapBaseToScalp(curves, scalp, mult=[.7, .4, .1]):
	import cgm.lib.distance as bbDistanceLib

	for obj in curves:
		currentPos = cmds.pointPosition(obj+'.cv[0]')
		newPos = bbDistanceLib.returnClosestPointOnMeshInfoFromPos(currentPos, scalp)['position']
		relPos = [newPos[0]-currentPos[0], newPos[1]-currentPos[1], newPos[2]-currentPos[2]]
		cmds.move(newPos[0], newPos[1], newPos[2], obj+'.cv[0]', a=True)
		cmds.move(relPos[0]*mult[0], relPos[1]*mult[0], relPos[2]*mult[0], obj+'.cv[1]', r=True)
		cmds.move(relPos[0]*mult[1], relPos[1]*mult[1], relPos[2]*mult[1], obj+'.cv[2]', r=True)
		cmds.move(relPos[0]*mult[2], relPos[1]*mult[2], relPos[2]*mult[2], obj+'.cv[3]', r=True)

def pushCVOutFromScalp(cvs, scalp, pushMult = 1.5):
	import cgm.lib.distance as bbDistanceLib
	sel = cmds.ls(sl=True)
	for obj in cvs:
		currentPos = cmds.pointPosition(obj)
		newPos = bbDistanceLib.returnClosestPointOnMeshInfoFromPos(currentPos, scalp)['position']
		relPos = [newPos[0]-currentPos[0], newPos[1]-currentPos[1], newPos[2]-currentPos[2]]
		cmds.move(relPos[0]*pushMult, relPos[1]*pushMult, relPos[2]*pushMult, obj, r=True)
	cmds.select(sel)

def pushCurveOutFromScalp(curves, scalp, pushMult = 1.5):
	import cgm.lib.distance as bbDistanceLib
	sel = cmds.ls(sl=True)

	for obj in curves:
		for shape in cmds.listRelatives(obj,shapes=True,fullPath=True):
			cvList = (cmds.ls([shape+'.cv[*]'],flatten=True))

		for cv in cvList:
			currentPos = cmds.pointPosition(cv)
			newPos = bbDistanceLib.returnClosestPointOnMeshInfoFromPos(currentPos, scalp)['position']
			relPos = [newPos[0]-currentPos[0], newPos[1]-currentPos[1], newPos[2]-currentPos[2]]
			cmds.move(relPos[0]*pushMult, relPos[1]*pushMult, relPos[2]*pushMult, cv, r=True)

	cmds.select(sel)

def averageCV(amount=1.0):
	for cv in cmds.ls(sl=True,fl=True):
		num = int(cv.split('.cv[')[-1].split(']')[0])
		baseObj = cv.split('.')[0]
		pos1 = cmds.pointPosition('%s.cv[%i]' % (baseObj, num+1))
		pos2 = cmds.pointPosition('%s.cv[%i]' % (baseObj, num-1))
		pos3 = cmds.pointPosition('%s.cv[%i]' % (baseObj, num))
		average = [(pos1[0]+pos2[0]+pos3[0])/3, (pos1[1]+pos2[1]+pos3[1])/3, (pos1[2]+pos2[2]+pos3[2])/3]
		relAvg = [average[0]-pos3[0], average[1]-pos3[1], average[2]-pos3[2]]
		cmds.move(relAvg[0]*amount, relAvg[1]*amount, relAvg[2]*amount, cv, r=True)

def createInterpolatedCurve(curve1, curve2, v):
	interpolatedCurve = cmds.duplicate(curve1, rr=True, rc=True)[0]

	for shape in cmds.listRelatives(curve2,shapes=True,fullPath=True):
		cvList = (cmds.ls([shape+'.cv[*]'],flatten=True))

	cmds.rebuildCurve(interpolatedCurve, ch=0, rpo=1, rt= 0, end = 1, kr = 0, kcp = 0, kep = 1, kt = 0, s = len(cvList)-3, d = 3, tol = 0)
	for i in range(len(cvList)):
		pos1 = cmds.pointPosition('%s.cv[%i]' % (interpolatedCurve,i))
		pos2 = cmds.pointPosition('%s.cv[%i]' % (curve2,i))
		newPos = ((pos2[0]-pos1[0])*v+pos1[0], (pos2[1]-pos1[1])*v+pos1[1], (pos2[2]-pos1[2])*v+pos1[2])
		cmds.move(newPos[0], newPos[1], newPos[2], '%s.cv[%i]' % (interpolatedCurve,i), a=True)

	return interpolatedCurve

def createRandomInterpolatedCurves(curves, nucmdsurves):
	newCurves = []
	for i in range(nucmdsurves):
		curve1, curve2 = random.sample(curves,2)
		newCurve = createInterpolatedCurve(curve1, curve2, random.uniform(.3, .7))
		newCurves.append(newCurve)

	return newCurves


def cutCrvOnIntersection(*args):
	selList = cmds.ls(sl = True)
	curves = selList[0:-1]
	surface = selList[-1]

	# Define input surface type.
	srfcShp = cmds.listRelatives(surface, s = True)[0]
	if cmds.objectType(srfcShp) == 'mesh':
		cpNodeType = 'closestPointOnMesh'
	elif cmds.objectType(srfcShp) == 'nurbsSurface':
		cpNodeType = 'closestPointOnSurface'

	# Create "closestPointOnMesh" or "closestPointOnSurface" node depend on surface type.
	cpNode = cmds.createNode(cpNodeType, n = 'temp_cpNode')

	# Connect surface to cpNode(closet point node).
	if cpNodeType == 'closestPointOnMesh':
		cmds.connectAttr('%s.worldMesh[0]' %(srfcShp), '%s.inMesh' %(cpNode), f = True)
	if cpNodeType == 'closestPointOnSurface':
		cmds.connectAttr('%s.worldSpace[0]' %(srfcShp), '%s.inputSurface' %(cpNode), f = True)

	errorCrvList = []

	# Show progress window.
	if cmds.window('progWin', exists = True):
		cmds.deleteUI('progWin')
	cmds.window('progWin', title = 'Working...')
	cmds.columnLayout()
	cmds.progressBar('progBar', minValue = 0, maxValue = len(curves), width = 300, isMainProgressBar = True, beginProgress = True, isInterruptable = True)
	cmds.window('progWin', e = True, w = 300, h = 10)
	cmds.showWindow('progWin')

	for curve in curves:
		# Progress window.
		if cmds.progressBar('progBar', q = True, isCancelled = True):
			print('Cutting curve job is cancelled.')
			break
		cmds.progressBar('progBar', e = True, step = 1)

		# Initialize variables.
		tempCrvPos = 0
		tempCrvPosList = [tempCrvPos]
		increment = 0.5
		tolerance = 0.005
		maxCalNum = 3000
		calCount = 1

		dist = calDist(curve, tempCrvPos, cpNode)

		# While distance is greater than tolerance, increse tempCrvPos and calculate again.
		while dist > tolerance:
			tempCrvPos += increment

			# If already calculate temporary curve point, skip it.
			if tempCrvPos in tempCrvPosList:
				continue
			else:
				# If calulate number reaches to maximun calulate number, break.
				if calCount == maxCalNum:
					print('%s is not intersecting curve.' %(curve))
					errorCrvList.append(curve)
					break
				dist = calDist(curve, tempCrvPos, cpNode)
				tempCrvPosList.append(tempCrvPos)
				calCount += 1

			# If temporary curve position reaches to maxium value at 1, reset the value and decrease increment to more dense searching.
			if tempCrvPos >= 1:
				tempCrvPos = 0
				increment = increment / 2

		if not calCount == maxCalNum:
			# If distance is less than tolerance, cut curve and go to the next curve.
			cmds.select('%s.un[%f]' %(curve, tempCrvPos))
			cmds.detachCurve(rpo = True)

	# Remove progress window.
	cmds.progressBar('progBar', e = True, endProgress = True)
	cmds.deleteUI('progWin')

	cmds.delete(cpNode)
	cmds.select(errorCrvList, r = True)


def calDist(curve, tempCrvPos, cpNode):
	'''
	Calculate distance between temporary position on curve and closest point on surface.
	'''

	# Get a temporary curve position and closest point on surface between curve and surface.
	crvPntWsPos = cmds.pointPosition('%s.un[%f]' %(curve, tempCrvPos), w = True)
	cmds.setAttr('%s.inPosition' %(cpNode), *crvPntWsPos)
	cp = cmds.getAttr('%s.position' %(cpNode))[0]

	# Get distance between curve point and closest point on surface.
	vCp = OpenMaya.MVector(*cp)
	vCrvPntWsPos = OpenMaya.MVector(*crvPntWsPos)
	dist = (vCp - vCrvPntWsPos).length()

	return dist


def snapToScalp(*args):
	selList = cmds.ls(sl = True)
	curves = selList[0:-1]
	surface = selList[-1]

	# Define input surface type.
	srfcShp = cmds.listRelatives(surface, s = True)[0]
	if cmds.objectType(srfcShp) == 'mesh':
		cpNodeType = 'closestPointOnMesh'
	elif cmds.objectType(srfcShp) == 'nurbsSurface':
		cpNodeType = 'closestPointOnSurface'

	# Create "closestPointOnMesh" or "closestPointOnSurface" node depend on surface type.
	cpNode = cmds.createNode(cpNodeType, n = 'temp_cpNode')

	# Connect surface to cpNode(closet point node).
	if cpNodeType == 'closestPointOnMesh':
		cmds.connectAttr('%s.worldMesh[0]' %(srfcShp), '%s.inMesh' %(cpNode), f = True)
	if cpNodeType == 'closestPointOnSurface':
		cmds.connectAttr('%s.worldSpace[0]' %(srfcShp), '%s.inputSurface' %(cpNode), f = True)

	# Show progress window.
	if cmds.window('progWin', exists = True):
		cmds.deleteUI('progWin')
	cmds.window('progWin', title = 'Working...')
	cmds.columnLayout()
	cmds.progressBar('progBar', minValue = 0, maxValue = len(curves), width = 300, isMainProgressBar = True, beginProgress = True, isInterruptable = True)
	cmds.window('progWin', e = True, w = 300, h = 10)
	cmds.showWindow('progWin')

	for curve in curves:
		# Progress window.
		if cmds.progressBar('progBar', q = True, isCancelled = True):
			print('Cutting curve job is cancelled.')
			break
		cmds.progressBar('progBar', e = True, step = 1)

		# Get curve's start point world position.
		crvStartPntPos = cmds.pointPosition('%s.cv[0]' %curve, w = True)

		# Get closest point on surface.
		cmds.setAttr('%s.inPosition' %(cpNode), *crvStartPntPos)
		cp = cmds.getAttr('%s.position' %(cpNode))[0]

		# Set curve's start point to closest point on surface.
		cmds.xform('%s.cv[0]' %curve, ws = True, t = cp)

	# Remove progress window.
	cmds.progressBar('progBar', e = True, endProgress = True)
	cmds.deleteUI('progWin')

	cmds.delete(cpNode)