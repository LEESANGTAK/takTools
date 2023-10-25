'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:

Usage:
'''



import maya.cmds as cmds



def ui():
	winName = 'bakeCamAEWin'
	
	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Bake Camera For After Effects', mnb = False, mxb = False)
	cmds.columnLayout('mainColLo', adj = True)
	cmds.text(label = 'Select a camera to bake.\n')
	cmds.intFieldGrp('compWIntFldGrp', label = 'AE Comp Width: ', numberOfFields = 1)
	cmds.intFieldGrp('compHIntFldGrp', label = 'AE Comp Height: ', numberOfFields = 1)

	fillAECompWidthHeightIntFld()

	cmds.button(label = 'Apply', h = 25, c = bakeCamForAE)
	cmds.window(winName, e = True, w = 300, h = 50)
	cmds.showWindow(winName)


def fillAECompWidthHeightIntFld():
	'''
	Fill compWIntFldGrp, compHIntFldGrp with current scene width height resolution.
	'''

	curWidthRes = cmds.getAttr('defaultResolution.width')
	curHeightRes = cmds.getAttr('defaultResolution.height')

	cmds.intFieldGrp('compWIntFldGrp', e = True, v1 = curWidthRes)
	cmds.intFieldGrp('compHIntFldGrp', e = True, v1 = curHeightRes)


def bakeCamForAE(*args):
	# Get selected camera.
	oriCam = cmds.ls(sl = True)[0]
	oriCamShp = cmds.listRelatives(oriCam, s = True)[0]

	# Duplicate selected camera.
	dupCam = cmds.duplicate(oriCam, n = oriCam + '_toAE_cam#')[0]
	dupCamShp = cmds.listRelatives(dupCam, s = True)[0]

	# Move dupCam to the world space if placing in the local space.
	if (cmds.listRelatives(dupCam, p = True) == None):
		pass
	else:
		cmds.parent(dupCam, world = True)
	
	# Unlock attribures.
	camTrsfAttrs = cmds.listAttr(dupCam, keyable = True)
	camShpAttrs = cmds.listAttr(dupCamShp, keyable = True)
	for camAttr in camTrsfAttrs:
		cmds.setAttr('%s.%s' %(dupCam, camAttr), lock = False)
	for camShpAttr in camShpAttrs:
		cmds.setAttr('%s.%s' %(dupCamShp, camShpAttr), lock = False)

	# Disable viewport update
	cmds.refresh(su = True)

	# Bake camera animation.
	minFrame = cmds.playbackOptions(q = True, min = True)
	maxFrame = cmds.playbackOptions(q = True, max = True)
	cmds.currentTime(minFrame)

	while minFrame <= maxFrame:
		returnDupCamToOriCam(oriCamShp, dupCamShp)
		convertDupCamFitRes(dupCamShp)
		bakeCam(oriCam, dupCam, dupCamShp)
		minFrame += 1
		cmds.currentTime(minFrame)

	# Enable viewport update
	cmds.refresh(su = False)
	cmds.refresh(f = True)

	# render and cmera settting
	compW = cmds.intFieldGrp('compWIntFldGrp', q = True, v1 = True)
	compH = cmds.intFieldGrp('compHIntFldGrp', q = True, v1 = True)
	cmds.setAttr('defaultResolution.width', compW)
	cmds.setAttr('defaultResolution.height', compH)


def returnDupCamToOriCam(oriCamShp, dupCamShp):
	'''
	Return duplicated camera shape attributes value to original source camera shape attributes value.
	'''

	oriFitResGate = cmds.getAttr('%s.filmFit' %oriCamShp)
	oriFl = cmds.getAttr('%s.focalLength' %oriCamShp)
	orihorAp = cmds.getAttr('%s.horizontalFilmAperture' %oriCamShp)
	oriverAp = cmds.getAttr('%s.verticalFilmAperture' %oriCamShp)

	cmds.setAttr('%s.filmFit' %dupCamShp, oriFitResGate)
	cmds.setAttr('%s.focalLength' %dupCamShp, oriFl)
	cmds.setAttr('%s.horizontalFilmAperture' %dupCamShp, orihorAp)
	cmds.setAttr('%s.verticalFilmAperture' %dupCamShp, oriverAp)


def convertDupCamFitRes(dupCamShp):
	'''
	Convert fit resolution to vertical and modify focalLength to match original look.
	'''

	# If fit resolution gate is not vertical set to the vertical.
	curFitResGate = cmds.getAttr('%s.filmFit' %dupCamShp)

	# Camera informations to calculate focal length.
	oriFl = cmds.getAttr('%s.focalLength' %dupCamShp)
	horAp = cmds.getAttr('%s.horizontalFilmAperture' %dupCamShp)
	verAp = cmds.getAttr('%s.verticalFilmAperture' %dupCamShp)
	pxAr = cmds.getAttr('defaultResolution.pixelAspect')
	dvAr = cmds.getAttr('defaultResolution.deviceAspectRatio')

	# Calculate focal length.
	if curFitResGate == 0:
		# Fill to Vertical Fit Resolution Gate
		fl = oriFl / min(1, (horAp / verAp) * (pxAr / dvAr))
	elif  curFitResGate == 1:
		# Horizontal to Vertical Fit Resolution Gate
		fl = oriFl / ((horAp / verAp) * (pxAr / dvAr))
	elif  curFitResGate == 3:
		# Overscan to Vertical Fit Resolution Gate
		fl = oriFl / max(1, (horAp / verAp) * (pxAr / dvAr))
	else:
		fl = oriFl

	# Set attributes.
	cmds.setAttr('%s.filmFit' %dupCamShp, 2)
	cmds.setAttr('%s.focalLength' %dupCamShp, fl)


def bakeCam(oriCam, dupCam, dupCamShp):
	# Constriant dupCam with original camera.
	prntCnst = cmds.parentConstraint(oriCam, dupCam, mo = False)

	trsfKeyAttrLs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']
	shpKeyAttrLs = ['fl', 'cap', 'lsr']

	for trsfAttr in trsfKeyAttrLs:
		cmds.setKeyframe('%s.%s' %(dupCam, trsfAttr))
	for shpAttr in shpKeyAttrLs:
		cmds.setKeyframe('%s.%s' %(dupCamShp, shpAttr))

	# Delete parent constraint of baked camera.
	cmds.delete(prntCnst)