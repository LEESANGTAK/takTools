'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 11/26/2015

Description:
Cut curve with poly or nurbs surface intersection point on the curve.

Usage:
Select curves and surface.

import tak_cutCurveOnIntersection
reload(tak_cutCurveOnIntersection)
tak_cutCurveOnIntersection.cutCrvOnIntersection()
'''


import maya.cmds as cmds
import maya.OpenMaya as OpenMaya


def cutCrvOnIntersection():
	'''
	Main method.
	'''

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
	crvPntWsPos =cmds.pointPosition('%s.un[%f]' %(curve, tempCrvPos), w = True)
	cmds.setAttr('%s.inPosition' %(cpNode), *crvPntWsPos)
	cp = cmds.getAttr('%s.position' %(cpNode))[0]

	# Get distance between curve point and closest point on surface.
	vCp = OpenMaya.MVector(*cp)
	vCrvPntWsPos = OpenMaya.MVector(*crvPntWsPos)
	dist = (vCp - vCrvPntWsPos).length()

	return dist