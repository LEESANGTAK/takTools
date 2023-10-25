
import maya.cmds as cmds
import maya.mel as mel


def setUpQualoth():
	'''
	Setup Qualoth simulation.
	'''

	# Select in order cloth source to simulate, blend shape cloth source, collider geometrys
	# Blend shape cloth source should be skined
	selList = cmds.ls(sl = True)
	simSrc = selList[0]
	bsCloth = selList[1]
	colliders = selList[2:]
	clothName = str(bsCloth).split('_')[0]

	# Create groups
	qualothGrp = cmds.createNode('transform', n = clothName + '_qualoth_grp')
	colliderGrp = cmds.createNode('transform', n = clothName + '_qualoth_collider_grp')
	constraintGrp = cmds.createNode('transform', n = clothName + '_qualoth_cnst_grp')
	cmds.parent(colliderGrp, constraintGrp, qualothGrp)

	# Duplicate simulation source geometry for goal constraint geo
	goalGeo = cmds.duplicate(simSrc, n = clothName + '_cnst')
	cmds.hide(goalGeo)

	# Create qlCloth
	cmds.select(simSrc, r = True)
	clothShp = mel.eval('qlCreateCloth;')
	clothTrnf = cmds.listRelatives(clothShp, p = True)[0]
	clothOut = cmds.rename('%sOut' %clothTrnf, clothName + '_qlOut')
	clothTrnf = cmds.rename(clothTrnf, clothName + '_qlCloth')
	cmds.parent(clothOut, clothTrnf, qualothGrp)

	# Set collider
	for collider in colliders:
		cmds.select(clothOut, collider, r = True)
		colliderShp = mel.eval('qlCreateCollider;')
		colliderPrnt = cmds.listRelatives(colliderShp, p = True)[0]
		colliderOffset = cmds.rename(colliderPrnt + 'Offset', collider + '_qlColliderOffset')
		colliderPrnt = cmds.rename(colliderPrnt, collider + '_qlCollider')
		cmds.parent(collider, colliderOffset, colliderPrnt, colliderGrp)
