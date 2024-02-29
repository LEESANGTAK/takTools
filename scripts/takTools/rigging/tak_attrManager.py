'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 06/15/2016

Description:
	Attribute manager that can add new attribute.
	You can add multiple attribute by using comma between names.
	e.g.) attr1, attr2, ...

	And reorder, alias, set min/max for selected attribute in channelbox.

Requirements:
	CGM Toolbox

Usage:
	import tak_attrManager
	reload(tak_attrManager)
	tak_attrManager.ui()
'''


import maya.cmds as cmds
import re
from functools import partial
from . import jlr_sort_attributes as sortAttr
from takTools.utils import globalUtil as gUtil


def ui():
	win = 'attrManagerWin'

	if cmds.window(win, exists = True):
		cmds.deleteUI(win)

	cmds.window(win, title = 'Attribute Manager')

	cmds.columnLayout('mainColLo', adj = True)
	cmds.optionMenu('typeOptMenu', label = 'Type: ', cc=typeCC)
	cmds.menuItem(label = 'Float')
	cmds.menuItem(label = 'Integer')
	cmds.menuItem(label = 'Boolean')
	cmds.menuItem(label = 'Enum')
	cmds.menuItem(label = 'Divider')
	cmds.textFieldGrp('nameTxtFldGrp', label = 'Name: ', columnWidth = [(1, 35), (2, 200)])
	cmds.rowLayout(nc=3)
	cmds.checkBox('keyableChkbox', l='Keyable', v=True)
	cmds.checkBox('minMaxChkbox', l='Min/Max', v=True, cc=minMaxCC)
	cmds.checkBox('multiChkbox', l='Multi')
	cmds.setParent('..')
	cmds.floatFieldGrp('minMaxFloatFldGrp', label='Min/Max: ', numberOfFields=2, v2=1.0, columnWidth = [(1, 50)])
	cmds.textFieldGrp('enumTxtFldGrp', label = 'Items: ', columnWidth = [(1, 35), (2, 200)], vis=False)

	cmds.button(label = 'Add', c = addAttr)

	cmds.separator(h = 5, style = 'in')

	cmds.rowColumnLayout('minMaxRowColLo', numberOfColumns = 5, columnWidth = [(2, 30), (5, 30)], columnOffset = [(2, 'left', 5),(5, 'right', 5)])
	cmds.text(label = 'Min/Max: ', align = 'left')
	cmds.checkBox('minChkBox', label = '', v = True)
	cmds.floatField('minFloatFld', v = 0)
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Value From Channelbox', c = partial(loadValFromChBox, 'minFloatFld'))
	cmds.floatField('maxFloatFld', v = 1)
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Value From Channelbox', c = partial(loadValFromChBox, 'maxFloatFld'))
	cmds.checkBox('maxChkBox', label = '', v = True)
	cmds.setParent('..')
	cmds.button(label = 'Set Min/Max', w = 100, c = setMinMax)

	cmds.separator(h = 5, style = 'in')

	cmds.rowColumnLayout('upDnRowColLo', numberOfColumns = 2, columnWidth = [(1, 120), (2, 120)])
	cmds.text(label = 'Reorder Attrs', align = 'left')
	cmds.text(label = '')
	cmds.button(label = 'Up', c = moveUpSelAttrs)
	cmds.button(label = 'Down', c = moveDownSelAttrs)
	cmds.setParent('..')

	cmds.separator(h = 5, style = 'in')

	cmds.textFieldGrp('aliasTxtFldGrp', label = 'New Name:', columnWidth = [(1, 55), (2, 180)])
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Selected Attributes', c=partial(loadAttr, 'aliasTxtFldGrp'))
	cmds.button(label = 'Alias Name', w = 100, c = aliasAttr)

	cmds.separator(h = 5, style = 'in')

	cmds.rowLayout('cloneAttrsLayout', nc=3)
	cmds.textFieldGrp('sourceTxtFldGrp', label='Source:', columnWidth = [(1, 40), (2, 70)])
	cmds.textFieldGrp('targetTxtFldGrp', label='Target:', columnWidth = [(1, 40), (2, 70)])
	cmds.checkBoxGrp('unrealChkBoxGrp', numberOfCheckBoxes=1, label1='Unreal', v1=True)
	cmds.setParent('..')
	cmds.rowLayout(numberOfColumns=3)
	cmds.textFieldGrp('prefixTxtFldGrp', label='Prefix:', columnWidth = [(1, 30), (2, 50)])
	cmds.textFieldGrp('clonAttrsTxtFldGrp', label = 'Attributes:', columnWidth = [(1, 55), (2, 100)])
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Selected Attribute', c=partial(loadAttr, 'clonAttrsTxtFldGrp'))
	cmds.textFieldGrp('suffixTxtFldGrp', label='Suffix:', columnWidth = [(1, 30), (2, 50)])
	cmds.setParent('..')
	cmds.button(label = 'Clone Attributes', w = 100, c = cloneAttributes)

	cmds.window(win, e = True, w = 50, h = 50)
	cmds.showWindow(win)


def typeCC(*args):
	dataType = cmds.optionMenu('typeOptMenu', q=True, value=True)
	if dataType == 'Enum':
		cmds.textFieldGrp('enumTxtFldGrp', e=True, vis=True)
		cmds.checkBox('multiChkbox', e=True, vis=False)
		cmds.checkBox('minMaxChkbox', e=True, vis=False)
		cmds.floatFieldGrp('minMaxFloatFldGrp', e=True, vis=False)
	elif dataType in ['Float', 'Integer']:
		cmds.checkBox('multiChkbox', e=True, vis=True)
		cmds.checkBox('minMaxChkbox', e=True, vis=True)
		cmds.floatFieldGrp('minMaxFloatFldGrp', e=True, vis=True)
		cmds.textFieldGrp('enumTxtFldGrp', e=True, vis=False)
	else:
		cmds.checkBox('multiChkbox', e=True, vis=False)
		cmds.checkBox('minMaxChkbox', e=True, vis=False)
		cmds.floatFieldGrp('minMaxFloatFldGrp', e=True, vis=False)
		cmds.textFieldGrp('enumTxtFldGrp', e=True, vis=False)


def minMaxCC(*args):
	onMinMax = cmds.checkBox('minMaxChkbox', q=True, v=True)
	if onMinMax:
		cmds.floatFieldGrp('minMaxFloatFldGrp', e=True, vis=True)
	else:
		cmds.floatFieldGrp('minMaxFloatFldGrp', e=True, vis=False)


def addAttr(*args):
	'''
	Add attributes on selected object.
	'''

	attrLs = re.findall(r'\w+', cmds.textFieldGrp('nameTxtFldGrp', q = True, text = True))
	attrType = cmds.optionMenu('typeOptMenu', q = True, value = True)
	isKeyable = cmds.checkBox('keyableChkbox', q=True, v=True)
	hasMinMax = cmds.checkBox('minMaxChkbox', q=True, v=True)
	isMulti = cmds.checkBox('multiChkbox', q=True, v=True)
	minValue = cmds.floatFieldGrp('minMaxFloatFldGrp', q=True, v1=True)
	maxValue = cmds.floatFieldGrp('minMaxFloatFldGrp', q=True, v2=True)
	enumItems = re.findall(r'\w+', cmds.textFieldGrp('enumTxtFldGrp', q = True, text = True))

	selObjs = cmds.ls(sl = True)

	for selObj in selObjs:
		for attr in attrLs:
			if attrType == 'Divider':
				cmds.addAttr(selObj, ln = attr, at = 'enum', en = '---------------:', keyable=True)
				# cmds.setAttr('%s.%s' %(selObj, attr), channelBox = True)
			elif attrType == 'Boolean':
				cmds.addAttr(selObj, ln = attr, at = 'bool', keyable = True)
				# cmds.setAttr('%s.%s' %(selObj, attr), channelBox = True)
			elif attrType == 'Enum':
				cmds.addAttr(selObj, ln = attr, at = 'enum', en=':'.join(enumItems), keyable = True, dv = 0)
			elif attrType == 'Integer':
				if hasMinMax:
					cmds.addAttr(selObj, ln = attr, at = 'long', keyable = True, min=minValue, max=maxValue, dv = 0, multi=isMulti)
				else:
					cmds.addAttr(selObj, ln = attr, at = 'long', keyable = True, dv = 0, multi=isMulti)
			elif attrType == 'Float':
				if hasMinMax:
					cmds.addAttr(selObj, ln = attr, at = 'double', keyable = True, min=minValue, max=maxValue, dv = 0, multi=isMulti)
				else:
					cmds.addAttr(selObj, ln = attr, at = 'double', keyable = True, dv = 0, multi=isMulti)

			if not isKeyable:
				cmds.setAttr('{}.{}'.format(selObj, attr), channelBox=True)

	# Clear name text field.
	cmds.textFieldGrp('nameTxtFldGrp', e = True, text = '')
	cmds.textFieldGrp('enumTxtFldGrp', e=True, text = '')


def moveUpSelAttrs(*args):
	'''
	Move up for selected attributes.
	'''

	sortAttr.move_up_attribute()


def moveDownSelAttrs(*args):
	'''
	Move down for selected attributes.
	'''

	sortAttr.move_down_attribute()


def setMinMax(*args):
	selObjList = cmds.ls(sl = True)
	selAttrList = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
	minVal = cmds.floatField('minFloatFld', q = True, v = True)
	maxVal =  cmds.floatField('maxFloatFld', q = True, v = True)
	minChkOpt = cmds.checkBox('minChkBox', q = True, v = True)
	maxChkOpt = cmds.checkBox('maxChkBox', q = True, v = True)

	for obj in selObjList:
		userDefAttrs = cmds.listAttr(obj, ud = True)
		for attr in selAttrList:
			# If user defined attributes exists do the following.
			if userDefAttrs and attr in userDefAttrs:
				if minChkOpt:
					cmds.addAttr('%s.%s' %(obj, attr), e = True, hasMinValue = True, min = minVal)
				elif not minChkOpt:
					cmds.addAttr('%s.%s' %(obj, attr), e = True, hasMinValue = False)
				if maxChkOpt:
					cmds.addAttr('%s.%s' %(obj, attr), e = True, hasMaxValue = True, max = maxVal)
				elif not maxChkOpt:
					cmds.addAttr('%s.%s' %(obj, attr), e = True, hasMaxValue = False)

			# If there is no user defined attributes do the following.
			else:
				if attr == 'tx':
					cmds.transformLimits(obj, tx = (minVal, maxVal), etx = (minChkOpt, maxChkOpt))
				elif attr == 'ty':
					cmds.transformLimits(obj, ty = (minVal, maxVal), ety = (minChkOpt, maxChkOpt))
				elif attr == 'tz':
					cmds.transformLimits(obj, tz = (minVal, maxVal), etz = (minChkOpt, maxChkOpt))
				elif attr == 'rx':
					cmds.transformLimits(obj, rx = (minVal, maxVal), erx = (minChkOpt, maxChkOpt))
				elif attr == 'ry':
					cmds.transformLimits(obj, ry = (minVal, maxVal), ery = (minChkOpt, maxChkOpt))
				elif attr == 'rz':
					cmds.transformLimits(obj, rz = (minVal, maxVal), erz = (minChkOpt, maxChkOpt))
				elif attr == 'sx':
					cmds.transformLimits(obj, sx = (minVal, maxVal), esx = (minChkOpt, maxChkOpt))
				elif attr == 'sy':
					cmds.transformLimits(obj, sy = (minVal, maxVal), esy = (minChkOpt, maxChkOpt))
				elif attr == 'sz':
					cmds.transformLimits(obj, sz = (minVal, maxVal), esz = (minChkOpt, maxChkOpt))


def aliasAttr(*args):
	selAttr = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)[0]
	replace = cmds.textFieldGrp('aliasTxtFldGrp', q = True, text = True)

	selList = cmds.ls(sl = True)

	for sel in selList:
		# cmds.aliasAttr(replace, '%s.%s' %(sel, selAttr))
		# cmds.addAttr('%s.%s' %(sel, selAttr), e=True, nn=replace)
		cmds.renameAttr('%s.%s' %(sel, selAttr), replace)

	cmds.select(selList, r = True)


def loadAttr(textFieldGrpName, *args):
	selAttrs = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
	cmds.textFieldGrp(textFieldGrpName, e = True, text = ' '.join(selAttrs))


def loadValFromChBox(floatFldName, *args):
	'''
	Fill float field with selected attribute's value in channelbox.
	'''

	sel = cmds.ls(sl = True)[0]
	selAttr = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)[0]
	selAttrVal = cmds.getAttr(sel + '.' + selAttr)

	cmds.floatField(floatFldName, e = True, v = selAttrVal)


def cloneAttributes(*args):
	sourceObj = cmds.textFieldGrp('sourceTxtFldGrp', q=True, text=True)
	targetObj = cmds.textFieldGrp('targetTxtFldGrp', q=True, text=True)
	unreal = cmds.checkBoxGrp('unrealChkBoxGrp', q=True, v1=True)
	attrs = cmds.textFieldGrp('clonAttrsTxtFldGrp', q=True, text=True).split(' ')
	prefix = cmds.textFieldGrp('prefixTxtFldGrp', q=True, text=True)
	suffix = cmds.textFieldGrp('suffixTxtFldGrp', q=True, text=True)

	for attr in attrs:
		gUtil.cloneAttribute(sourceObj, targetObj, attr, prefix, suffix, unreal, True)
