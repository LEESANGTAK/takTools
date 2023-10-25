'''
Toolname: Auto Swim
Author: Sang-tak Lee
Contact: chst27@nate.com

Usage: import tak_autoSwim
       tak_autoSwim.UI()
'''


import maya.cmds as cmds
from functools import partial


def UI():
	# check the UI exist
	if cmds.window('autoSwimWin', exists = True): cmds.deleteUI('autoSwimWin')
		
	# create window
	cmds.window('autoSwimWin', title = 'Auto Swim')
	
	# main formLayout
	cmds.formLayout('mainFormLay', nd = 100)
	
	# main tabLayout
	cmds.tabLayout('mainTabLay', tabsVisible = False)
	cmds.tabLayout('subTabLay', tabsVisible = False, scrollable = True)
	
	cmds.columnLayout('mainColLay', adj = True)
		
	cmds.textFieldButtonGrp('conObjTexFielButt', label = 'Control Object: ', buttonLabel = 'Load Sel', bc = partial(loadSel, 'conObjTexFielButt'))
	
	cmds.separator('sep1', h = 20, style = 'in')
	
	cmds.formLayout('trgObjFormLay', nd = 100, h = 170)
	cmds.text('trgObjText', label = 'Target Objects: ', align = 'right')
	cmds.textScrollList('trgObjTexScrList', ams = True)
	cmds.button('trgObjAddButt', l = '+', w = 20, c = partial(trgObjAdd, 'trgObjTexScrList'))
	cmds.button('trgObjDelButt', l = '-', w = 20, c = partial(trgObjDel, 'trgObjTexScrList'))
	
	# arrange the 'trgObjFormLay'
	cmds.formLayout('trgObjFormLay', edit = True, 
                        attachForm = [('trgObjText', 'top', 0), ('trgObjText', 'left', 0), ('trgObjAddButt', 'top', 5), ('trgObjAddButt', 'right', 5), ('trgObjDelButt', 'right', 5), ('trgObjTexScrList', 'bottom', 5), ('trgObjTexScrList', 'top', 5)],
	                attachControl = [('trgObjTexScrList', 'left', 5, 'trgObjText'), ('trgObjTexScrList', 'right', 5, 'trgObjAddButt'), ('trgObjDelButt', 'top', 5, 'trgObjAddButt')])
	
	# parent 'trgObjFormLay' to the 'mainColLay'
	cmds.setParent('mainColLay')
	
	# axis option
	cmds.radioButtonGrp('axisRadButtGrp', numberOfRadioButtons = 3, label = 'Rotate Axis: ', labelArray3 = ['X', 'Y', 'Z'])
	
	# parent 'mainColLay' to the 'subTabLay'
	cmds.setParent('subTabLay')
	
	# parent 'mainTabLay' to the 'mainFormLay'
	cmds.setParent('mainFormLay')
	
	cmds.button('appButt', label = 'Apply', c = app)
	cmds.button('closButt', label = 'Close', c = delWin)
	
	# arrange the 'mainFormLay'
	cmds.formLayout('mainFormLay', e = True, 
	                attachForm = [('mainTabLay', 'top', 5), ('mainTabLay', 'left', 5), ('mainTabLay', 'right', 5), ('appButt', 'left', 5), ('appButt', 'bottom', 5), ('closButt', 'right', 5), ('closButt', 'bottom', 5)],
	                attachPosition = [('appButt', 'right', 2.5, 50), ('closButt', 'left', 2.5, 50)],
	                attachControl = [(('mainTabLay', 'bottom', 5, 'appButt'))])
	
	# resizing the window
	cmds.window('autoSwimWin', e = True, w = 470, h = 300, sizeable = True)
	cmds.showWindow('autoSwimWin')
	
	
# 'Load Sel' button command
def loadSel(textFielButtGrpName):
	conObj = cmds.ls(sl = True)
	cmds.textFieldButtonGrp(textFielButtGrpName, e = True, text = conObj[0])
	
	
# 'trgObjAddButt' button command
def trgObjAdd(texScrLisName, arg = None):
	# get target objects list
	trgObjs = cmds.ls(sl = True)
	
	# get current items in the textScrollList
	itemInList = cmds.textScrollList(texScrLisName, q = True, allItems = True)
	
	# in case that current items exists
	if itemInList:
		# get the items that not in the list
		addList = set(trgObjs) - set(itemInList)
		
		# result list that added addList
		resultList = addList | set(itemInList)
		
		# sorting resultList
		sortedList = sorted(resultList)

		# append to the specified textScrollList
		cmds.textScrollList(texScrLisName, e = True, removeAll = True)
		cmds.textScrollList(texScrLisName, e = True, append = list(sortedList))

	# in case that current items not exists	
	else: 
		trgObjs.sort()
		cmds.textScrollList(texScrLisName, e = True, append = trgObjs)
	
	
# 'trgObjDelButt' button command
def trgObjDel(texScrLisName, arg = None):
	# get selected items
	selItems = cmds.textScrollList(texScrLisName, q = True, selectItem = True)
	
	# remove the items in List
	cmds.textScrollList(texScrLisName, e = True, removeItem = selItems)
	
# 'appButt' button command
def app(*args):
	conObj = cmds.textFieldButtonGrp('conObjTexFielButt', q = True, text = True)
	
	trgObjs = cmds.textScrollList('trgObjTexScrList', q = True, allItems = True)
	
	selectedButt = cmds.radioButtonGrp('axisRadButtGrp', q = True, sl = True)
	if selectedButt == 1: roAxis = 'X'
	elif selectedButt == 2: roAxis = 'Y'
	elif selectedButt == 3: roAxis = 'Z'

	addAttr(conObj, trgObjs)
	addSwimGrp(trgObjs)
	swimExp(conObj, trgObjs, roAxis)


# command that close window
def delWin(*args):
	cmds.deleteUI('autoSwimWin')
    

# add atribute command
def addAttr(conObj, trgObjs):
	attrList = ['speed', 'amplitude', 'delay']
	
	# add master control
	if not cmds.objExists('%s.master_con' %conObj):
		cmds.addAttr(conObj, ln = 'master_con', at = 'enum', en = '---------------')
		cmds.setAttr('%s.master_con' %conObj, e = True, channelBox = True)
	
		# on/off
		cmds.addAttr(conObj, ln = 'on_off', at = 'double', k = True, min = 0, max = 1, dv = 1)
	
		for attr in attrList:
			cmds.addAttr(conObj, ln = attr, at = 'double', k = True, dv = 1)
		
	for trg in trgObjs:
		cmds.addAttr(conObj, ln = trg, at = 'enum', en = '---------------')
		cmds.setAttr('%s.%s' %(conObj,trg), e = True, channelBox = True)
		
		for attr in attrList:
			cmds.addAttr(conObj, ln = '%s_%s' %(trg,attr), at = 'double', k = True, dv = 1)
			
			
# add swim_grp to the target objects
def addSwimGrp(trgObjs):
	for trg in trgObjs:
		objType = cmds.objectType(trg)
		if objType == 'transform':
			cmds.select(trg, r=True)
			swimGrpNode = cmds.duplicate(n='%s_swim_grp' %(trg), po=True)
			cmds.parent(trg, swimGrpNode)
		elif objType == 'joint':
			prnt = cmds.listRelatives(trg, p = True)
			cmds.select(cl = True)
			swimGrpNode = cmds.group(n = '%s_swim_grp' %(trg), em = True)
			pCnst = cmds.parentConstraint(trg, swimGrpNode, mo = False)
			cmds.delete(pCnst)
			cmds.parent(trg, swimGrpNode)
			cmds.parent(swimGrpNode, prnt)
		
		
# create expression
def swimExp(conObj, trgObjs, roAxis):
	for trg in trgObjs:
		cmds.expression(n = '%s_swim_exp' %trg, ae = True, uc = all, s = "// master controls\n $on_off = %s.on_off;\n $masSpeed = %s.speed;\n $masDelay = %s.delay;\n $masAmplitude = %s.amplitude;\n\n $speed = %s.%s_speed;\n $delay = %s.%s_delay;\n $amplitude = %s.%s_amplitude;\n\n %s_swim_grp.rotate%s = (sin((time * $speed * $masSpeed) + $delay + $masDelay) * $amplitude * $masAmplitude) * $on_off;" %(conObj, conObj, conObj, conObj, conObj, trg, conObj, trg, conObj, trg, trg, roAxis))
	