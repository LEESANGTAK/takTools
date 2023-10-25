'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 05/26/2016

Description:
This script used to transfer maya camera into the 3ds max seamlessly.

Usage:
1. Select a camera you want to export.
2. Run following codes in maya script editor's python tab.
import tak_mayaCamToMax
reload(tak_mayaCamToMax)
tak_mayaCamToMax.mayaCamToMax()
3. Import exported camera fbx file in 3Ds Max.
4. Match render image resolution.
'''



import os
import maya.mel as mel
import maya.cmds as cmds

if not cmds.pluginInfo('fbxmaya', q = True, loaded = True):
	cmds.loadPlugin('fbxmaya')



def mayaCamToMax():
	# Get selected camera.
	oriCam = cmds.ls(sl = True)[0]
	oriCamShp = cmds.listRelatives(oriCam, s = True)[0]

	# Duplicate selected camera.
	dupCam = cmds.duplicate(oriCam, n = oriCam + '_toMaxCam#')[0]
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


	# Disable viewport update to speed up baking process.
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

	# Enable viewport update.
	cmds.refresh(su = False)
	cmds.refresh(f = True)

	# Export the baked camera to FBX format.
	cmds.select(dupCam, r = True)

	curScenePath = cmds.file(q = True, sceneName = True)
	curWorkDir = os.path.dirname(curScenePath)
	filePath = cmds.fileDialog2(fileMode = 0, caption = 'Export Camera', startingDirectory = curWorkDir, fileFilter = '*.fbx')[0]

	mel.eval('FBXExportFileVersion "FBX201800"')
	mel.eval('FBXExportCameras -v true;')
	mel.eval('FBXExportConvertUnitString "cm"')
	mel.eval('FBXExportInputConnections -v 0')

	mel.eval('FBXExport -f "%s" -s' %filePath)


def returnDupCamToOriCam(oriCamShp, dupCamShp):
	'''
	Return duplicated camera shape attributes value to original source camera shape attributes value.
	'''

	oriFitResGate = cmds.getAttr('%s.filmFit' %oriCamShp)
	oriFl = cmds.getAttr('%s.focalLength' %oriCamShp)
	orihorAp = cmds.getAttr('%s.horizontalFilmAperture' %oriCamShp)
	oriverAp = cmds.getAttr('%s.verticalFilmAperture' %oriCamShp)
	camScale = cmds.getAttr('%s.cameraScale' %oriCamShp)
	preScale = cmds.getAttr('%s.preScale' %oriCamShp)
	postScale = cmds.getAttr('%s.postScale' %oriCamShp)

	cmds.setAttr('%s.filmFit' %dupCamShp, oriFitResGate)
	cmds.setAttr('%s.focalLength' %dupCamShp, oriFl)
	cmds.setAttr('%s.horizontalFilmAperture' %dupCamShp, orihorAp)
	cmds.setAttr('%s.verticalFilmAperture' %dupCamShp, oriverAp)
	cmds.setAttr('%s.cameraScale' %dupCamShp, camScale)
	cmds.setAttr('%s.preScale' %dupCamShp, preScale)
	cmds.setAttr('%s.postScale' %dupCamShp, postScale)


def convertDupCamFitRes(dupCamShp):
	'''
	Convert fit resolution to horizontal and modify focalLength to match original look.
	'''

	# If fit resolution gate is not horizontal set to the horizontal.
	curFitResGate = cmds.getAttr('%s.filmFit' %dupCamShp)

	# Camera informations to calculate focal length.
	oriFl = cmds.getAttr('%s.focalLength' %dupCamShp)
	horAp = cmds.getAttr('%s.horizontalFilmAperture' %dupCamShp)
	verAp = cmds.getAttr('%s.verticalFilmAperture' %dupCamShp)
	pxAr = cmds.getAttr('defaultResolution.pixelAspect')
	dvAr = cmds.getAttr('defaultResolution.deviceAspectRatio')
	oriCamScale = cmds.getAttr('%s.cameraScale' %dupCamShp)
	oriPreScale = cmds.getAttr('%s.preScale' %dupCamShp)
	oriPostScale = cmds.getAttr('%s.postScale' %dupCamShp)

	if verAp == 0:
		cmds.error('Vertical aperture is 0.')
	if dvAr == 0:
		cmds.error('Device aspect ratio is 0.')

	# Calculate focal length.
	if curFitResGate == 0:
		# Fill to Horizontal Fit Resolution Gate
		fl = oriFl * max(1, (horAp / verAp) * (pxAr / dvAr))
	elif  curFitResGate == 2:
		# Vertical to Horizontal Fit Resolution Gate
		fl = oriFl * ((horAp / verAp) * (pxAr / dvAr))
	elif  curFitResGate == 3:
		# Overscan to Horizontal Fit Resolution Gate
		fl = oriFl * min(1, (horAp / verAp) * (pxAr / dvAr))
	else:
		fl = oriFl

	# Set attributes.
	cmds.setAttr('%s.cameraScale' %dupCamShp, 1)
	cmds.setAttr('%s.preScale' %dupCamShp, 1)
	cmds.setAttr('%s.postScale' %dupCamShp, 1)
	cmds.setAttr('%s.filmFit' %dupCamShp, 1)
	cmds.setAttr('%s.focalLength' %dupCamShp, (fl * oriPreScale * oriPostScale) / oriCamScale)


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