'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 07/26/2015

Description:
This script is for to control ortho graphic view display problem when working with large scale scene.

Usage:
import tak_orthoCam
reload(tak_orthoCam)
orthoView.UI()
'''


import maya.cmds as cmds
import maya.mel as mel


class UI(object):
	widgets = {}
	widgets['win'] = 'orthoViewWin'


	@classmethod
	def __init__(cls):
		# Check if window already exists
		if cmds.window(cls.widgets['win'], exists = True):
			cmds.deleteUI(cls.widgets['win'])

		cls.ui()


	@classmethod
	def ui(cls):
		cmds.window(cls.widgets['win'], title = 'Ortho Graphic View UI', mnb = False, mxb = False)

		cls.widgets['mainClLo'] = cmds.columnLayout(adj = True)

		cmds.button(label = 'Perspective View', h = 30, c = cls.persView, p = cls.widgets['mainClLo'])

		cmds.separator(h = 5, style = 'in')

		cls.widgets['frBkRoClLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 70), (2, 70)], columnSpacing = [(2, 5)], p = cls.widgets['mainClLo'])
		cmds.button(label = 'Front View', c = cls.frontView, p = cls.widgets['frBkRoClLo'])
		cmds.button(label = 'Back View', c = cls.backView, p = cls.widgets['frBkRoClLo'])

		cmds.separator(h = 5, style = 'in', p = cls.widgets['mainClLo'])

		cls.widgets['rtLfRoClLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 70), (2, 70)], columnSpacing = [(2, 5)], p = cls.widgets['mainClLo'])
		cmds.button(label = 'Right View', c = cls.rightView, p = cls.widgets['rtLfRoClLo'])
		cmds.button(label = 'Left View', c = cls.leftView, p = cls.widgets['rtLfRoClLo'])

		cmds.separator(h = 5, style = 'in', p = cls.widgets['mainClLo'])

		cls.widgets['topBtmRoClLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 70), (2, 70)], columnSpacing = [(2, 5)], p = cls.widgets['mainClLo'])
		cmds.button(label = 'Top View', c = cls.topView, p = cls.widgets['topBtmRoClLo'])
		cmds.button(label = 'Bottom View', c = cls.bottomView, p = cls.widgets['topBtmRoClLo'])

		cmds.window(cls.widgets['win'], e = True, w= 100, h = 100)
		cmds.showWindow(cls.widgets['win'])


	@staticmethod
	def getCurCam():
		curPanel = cmds.getPanel(wf = True)
		curCam = cmds.modelPanel(curPanel, q = True, cam = True)
		curCamShp = cmds.listRelatives(curCam, s = True)[0]
		return curCam, curCamShp


	@staticmethod
	def setCam(cam, camShp, t, r, pers = False):
		# Set camera shape
		cmds.setAttr('%s.nearClipPlane' %camShp, 5)
		cmds.setAttr('%s.farClipPlane' %camShp, 3000)
		cmds.setAttr('%s.focalLength' %camShp, 80)

		if not pers:
			cmds.setAttr('%s.orthographic' %camShp, True)
			cmds.setAttr('%s.orthographicWidth' %camShp, 200)
		elif pers:
			cmds.setAttr('%s.orthographic' %camShp, False)

			cmds.viewLookAt(cam)

		# Set camera transform
		cmds.setAttr('%s.translateX' %cam, t[0])
		cmds.setAttr('%s.translateY' %cam, t[1])
		cmds.setAttr('%s.translateZ' %cam, t[2])
		cmds.setAttr('%s.rotateX' %cam, r[0])
		cmds.setAttr('%s.rotateY' %cam, r[1])
		cmds.setAttr('%s.rotateZ' %cam, r[2])


	@classmethod
	def persView(cls, *args):
		# Get the current working camera
		curCam, curCamShp = cls.getCurCam()

		# Set the camera
		cls.setCam(curCam, curCamShp, t = [200, 300, 200], r = [-37, 45, 0], pers = True)

		mel.eval('FrameSelected;')


	@classmethod
	def frontView(cls, *args):
		# Get the current working camera
		curCam, curCamShp = cls.getCurCam()

		# Set the camera
		cls.setCam(curCam, curCamShp, t = [0, 80, 200], r = [0, 0, 0])

		mel.eval('FrameSelected;')


	@classmethod
	def backView(cls, *args):
		# Get the current working camera
		curCam, curCamShp = cls.getCurCam()

		# Set the camera
		cls.setCam(curCam, curCamShp, t = [0, 80, -200], r = [0, 180, 0])

		mel.eval('FrameSelected;')


	@classmethod
	def rightView(cls, *args):
		# Get the current working camera
		curCam, curCamShp = cls.getCurCam()

		# Set the camera
		cls.setCam(curCam, curCamShp, t = [200, 80, 0], r = [0, 90, 0])

		mel.eval('FrameSelected;')


	@classmethod
	def leftView(cls, *args):
		# Get the current working camera
		curCam, curCamShp = cls.getCurCam()

		# Set the camera
		cls.setCam(curCam, curCamShp, t = [-200, 80, 0], r = [0, -90, 0])

		mel.eval('FrameSelected;')


	@classmethod
	def topView(cls, *args):
		# Get the current working camera
		curCam, curCamShp = cls.getCurCam()

		# Set the camera
		cls.setCam(curCam, curCamShp, t = [0, 200, 0], r = [-90, 0, 0])

		mel.eval('FrameSelected;')


	@classmethod
	def bottomView(cls, *args):
		# Get the current working camera
		curCam, curCamShp = cls.getCurCam()

		# Set the camera
		cls.setCam(curCam, curCamShp, t = [0, -200, 0], r = [90, 0, 0])

		mel.eval('FrameSelected;')