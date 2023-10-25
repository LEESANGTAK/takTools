'''
Author: Sang-tak Lee
Website: https://tak.ta-note.com
Updated: 11/22/2020

Description:
This script help to create range of motion easily.
'''

import maya.cmds as cmds
import pymel.core as pm


class UI(object):
	widgets = {}
	winName = 'romWin'

	@classmethod
	def __init__(cls):
		if cmds.window(cls.winName, exists = True):
			cmds.deleteUI(cls.winName)

		cls.ui()


	@classmethod
	def ui(cls):
		cmds.window(cls.winName, title = 'Create Range Of Motion', mnb = False, mxb = False)

		cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)

		cmds.rowColumnLayout(nc=2)
		cmds.text(label='Start Time: ')
		cls.widgets['startTimeIntFld'] = cmds.intField(v=0)
		cmds.text(label='Interval: ')
		cls.widgets['intervalIntFld'] = cmds.intField(v=10)
		cmds.setParent('..')

		cls.widgets['txRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['txChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'TranslateX Min/Max: ')
		cls.widgets['txMinIntFld'] = cmds.intField(v = -3)
		cls.widgets['txMaxIntFld'] = cmds.intField(v = 3)
		cmds.setParent('..')

		cls.widgets['tyRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['tyChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'TranslateY Min/Max: ')
		cls.widgets['tyMinIntFld'] = cmds.intField(v = -3)
		cls.widgets['tyMaxIntFld'] = cmds.intField(v = 3)
		cmds.setParent('..')

		cls.widgets['tzRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['tzChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'TranslateZ Min/Max: ')
		cls.widgets['tzMinIntFld'] = cmds.intField(v = -3)
		cls.widgets['tzMaxIntFld'] = cmds.intField(v = 3)
		cmds.setParent('..')

		cmds.separator(style = 'in', h = 5)

		cls.widgets['rxRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['rxChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'RotateX Min/Max: ')
		cls.widgets['rxMinIntFld'] = cmds.intField(v = -90)
		cls.widgets['rxMaxIntFld'] = cmds.intField(v = 90)
		cmds.setParent('..')

		cls.widgets['ryRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['ryChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'RotateY Min/Max: ')
		cls.widgets['ryMinIntFld'] = cmds.intField(v = -90)
		cls.widgets['ryMaxIntFld'] = cmds.intField(v = 90)
		cmds.setParent('..')

		cls.widgets['rzRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['rzChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'RotateZ Min/Max: ')
		cls.widgets['rzMinIntFld'] = cmds.intField(v = -90)
		cls.widgets['rzMaxIntFld'] = cmds.intField(v = 90)
		cmds.setParent('..')

		cmds.separator(style = 'in', h = 5)

		cls.widgets['bsRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 3, columnOffset = [(1, 'left', 5), (2, 'left', 5), (3, 'right', 5)])
		cls.widgets['bsChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'Blend Shape: ')
		cls.widgets['bsTxtFld'] = cmds.textField()
		cmds.setParent('..')

		cmds.separator(style = 'in', h = 5)

		cmds.button(label = 'Apply', h = 50, c = Functions.apply)

		cmds.window(cls.winName, e = True, w = 150, h = 150)
		cmds.showWindow(cls.winName)


class Functions(object):
	@staticmethod
	def apply(*args):
		# get option state
		startTime = cmds.intField(UI.widgets['startTimeIntFld'], q=True, v=True)
		interval = cmds.intField(UI.widgets['intervalIntFld'], q=True, v=True)
		txOpt = cmds.checkBox(UI.widgets['txChkBox'], q = True, v = True)
		tyOpt = cmds.checkBox(UI.widgets['tyChkBox'], q = True, v = True)
		tzOpt = cmds.checkBox(UI.widgets['tzChkBox'], q = True, v = True)
		rxOpt = cmds.checkBox(UI.widgets['rxChkBox'], q = True, v = True)
		ryOpt = cmds.checkBox(UI.widgets['ryChkBox'], q = True, v = True)
		rzOpt = cmds.checkBox(UI.widgets['rzChkBox'], q = True, v = True)
		bsOpt = cmds.checkBox(UI.widgets['bsChkBox'], q = True, v = True)

		if bsOpt:
			bs = cmds.textField(UI.widgets['bsTxtFld'], q=True, tx=True)
			Functions.romBS(bs)
			return

		selList = cmds.ls(sl = True)

		cmds.currentTime(startTime)

		if (txOpt + tyOpt + tzOpt + rxOpt + ryOpt + rzOpt) == 0:  # In case options are enabled nothing
			cmds.select(selList, r=True)
			for i in xrange(50):
				cmds.setKeyframe()
				curTime = cmds.currentTime(q=True)
				cmds.currentTime(curTime + interval)
		else:
			for sel in selList:
				cmds.select(sel, r = True)
				defaultTx = cmds.getAttr('{0}.tx'.format(sel))
				defaultTy = cmds.getAttr('{0}.ty'.format(sel))
				defaultTz = cmds.getAttr('{0}.tz'.format(sel))
				defaultRx = cmds.getAttr('{0}.rx'.format(sel))
				defaultRy = cmds.getAttr('{0}.ry'.format(sel))
				defaultRz = cmds.getAttr('{0}.rz'.format(sel))

				if txOpt:
					txMin = cmds.intField(UI.widgets['txMinIntFld'], q = True, v = True)
					txMax = cmds.intField(UI.widgets['txMaxIntFld'], q = True, v = True)
					curFrame = cmds.currentTime(q = True)
					Functions.setKeyframe(sel, 'translateX', curFrame, defaultTx, txMin, txMax, interval)

				if tyOpt:
					tyMin = cmds.intField(UI.widgets['tyMinIntFld'], q = True, v = True)
					tyMax = cmds.intField(UI.widgets['tyMaxIntFld'], q = True, v = True)
					curFrame = cmds.currentTime(q = True)
					Functions.setKeyframe(sel, 'translateY', curFrame, defaultTy, tyMin, tyMax, interval)

				if tzOpt:
					tzMin = cmds.intField(UI.widgets['tzMinIntFld'], q = True, v = True)
					tzMax = cmds.intField(UI.widgets['tzMaxIntFld'], q = True, v = True)
					curFrame = cmds.currentTime(q = True)
					Functions.setKeyframe(sel, 'translateZ', curFrame, defaultTz, tzMin, tzMax, interval)

				if rxOpt:
					rxMin = cmds.intField(UI.widgets['rxMinIntFld'], q = True, v = True)
					rxMax = cmds.intField(UI.widgets['rxMaxIntFld'], q = True, v = True)
					curFrame = cmds.currentTime(q = True)
					Functions.setKeyframe(sel, 'rotateX', curFrame, defaultRx, rxMin, rxMax, interval)

				if ryOpt:
					ryMin = cmds.intField(UI.widgets['ryMinIntFld'], q = True, v = True)
					ryMax = cmds.intField(UI.widgets['ryMaxIntFld'], q = True, v = True)
					curFrame = cmds.currentTime(q = True)
					Functions.setKeyframe(sel, 'rotateY', curFrame, defaultRy, ryMin, ryMax, interval)

				if rzOpt:
					rzMin = cmds.intField(UI.widgets['rzMinIntFld'], q = True, v = True)
					rzMax = cmds.intField(UI.widgets['rzMaxIntFld'], q = True, v = True)
					curFrame = cmds.currentTime(q = True)
					Functions.setKeyframe(sel, 'rotateZ', curFrame, defaultRz, rzMin, rzMax, interval)

		endTime = cmds.currentTime(q = True)
		cmds.playbackOptions(minTime = startTime)
		cmds.playbackOptions(maxTime = endTime)


	@staticmethod
	def setKeyframe(node, attr, curFrame, defaultVal, minVal, maxVal, interval):
		if not cmds.getAttr('{0}.{1}'.format(node, attr), keyable=True):
			return

		cmds.setKeyframe(v = defaultVal, at = attr)
		cmds.currentTime(curFrame + interval*1)
		cmds.setKeyframe(v = defaultVal+minVal, at = attr)
		cmds.currentTime(curFrame + interval*2)
		cmds.setKeyframe(v = defaultVal, at = attr)
		cmds.currentTime(curFrame + interval*3)
		cmds.setKeyframe(v = defaultVal+maxVal, at = attr)
		cmds.currentTime(curFrame + interval*4)
		cmds.setKeyframe(v = defaultVal, at = attr)

	@staticmethod
	def romBS(blendshape):
		bs = pm.PyNode(blendshape)
		startTime = pm.playbackOptions(q=True, min=True) + 1
		targets = pm.listAttr(bs.weight, multi=True)
		for i, t in enumerate(targets):
			targetTime = startTime + i
			pm.setKeyframe('{0}.{1}'.format(bs, t), time=targetTime-1, v=0)
			pm.setKeyframe('{0}.{1}'.format(bs, t), time=targetTime, v=1)
			pm.setKeyframe('{0}.{1}'.format(bs, t), time=targetTime+1, v=0)