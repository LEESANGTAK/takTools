"""
Author: Tak
Mail: chst27@gmail.com
Website: https://tak.ta-note.com
Description: Add segment to selected joint chain.
"""

import pymel.core as pm

import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

from PySide2 import QtWidgets, QtCore


def addJointSegments(count):
    segJoints = []

    # Check Errors
    if count < 2:
        return segJoints

    sels = pm.selected()
    if not sels or not isinstance(sels[0], pm.nodetypes.Joint):
        pm.displayWarning('Select a joint.')
        return segJoints
    baseJnt = sels[0]

    child = baseJnt.getChildren()
    if not child or not isinstance(child[0], pm.nodetypes.Joint):
        pm.displayWarning('Has no child joint or child object is not a joint.')
        return segJoints
    endJnt = child[0]

    # Get aim vector
    baseJntWorldVector = pm.datatypes.Vector(pm.xform(baseJnt, q=True, t=True, ws=True))
    childJntWorldVector = pm.datatypes.Vector(pm.xform(endJnt, q=True, t=True, ws=True))

    baseToChildVector = childJntWorldVector - baseJntWorldVector

    # Create joints
    increment = 1.0/count
    scaler = increment
    preJnt = baseJnt
    for i in range(count-1):
        scaledVector = baseToChildVector * scaler
        segJointVector = baseJntWorldVector + scaledVector

        segJnt = baseJnt.duplicate(n='{0}_{1:02d}_seg'.format(baseJnt.name(), i), po=True)[0]
        segJoints.append(segJnt)
        pm.xform(segJnt, t=segJointVector, ws=True)
        preJnt | segJnt

        preJnt = segJnt
        scaler += increment

    preJnt | endJnt

    return segJoints


def getMayaMainWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaWinPtr), QtWidgets.QWidget)

class AddJointSegmentsUI(QtWidgets.QDialog):
    def __init__(self, parent=getMayaMainWin()):
        super(AddJointSegmentsUI, self).__init__(parent)
        self.setWindowTitle('Add Joint Segments')
        self.setWindowFlags(QtCore.Qt.Tool)

        self.baseJnt = None
        self.endJnt = None
        self.segJoints = None

        self.initSuccess = self.initialize()
        if self.initSuccess:
            self.createWidgets()
            self.createLayouts()
            self.createConnections()

    def initialize(self):
        sels = pm.selected()
        if not sels or not isinstance(sels[0], pm.nodetypes.Joint):
            pm.displayWarning('Select a joint.')
            return False
        self.baseJnt = sels[0]

        child = self.baseJnt.getChildren()
        if not child or not isinstance(child[0], pm.nodetypes.Joint):
            pm.displayWarning('Has no child joint or child object is not a joint.')
            return False
        self.endJnt = child[0]

        return True

    def createWidgets(self):
        self.countLabel = QtWidgets.QLabel('Segment Count:')
        self.countLe = QtWidgets.QLineEdit('1')
        self.countLe.setFixedWidth(25)
        self.countSlider = CustomSlider()
        self.countSlider.setFixedWidth(200)
        self.countSlider.setOrientation(QtCore.Qt.Horizontal)
        self.countSlider.setMinimum(1)
        self.countSlider.setMaximum(50)

    def createLayouts(self):
        mainLayout = QtWidgets.QHBoxLayout(self)
        mainLayout.addWidget(self.countLabel)
        mainLayout.addWidget(self.countLe)
        mainLayout.addWidget(self.countSlider)

    def createConnections(self):
        self.countLe.editingFinished.connect(self.setCountSlider)
        self.countSlider.valueChanged.connect(self.addJointSegments)

    def setCountSlider(self):
        countStr = self.countLe.text()
        self.countSlider.setValue(int(countStr))

    def addJointSegments(self, value):
        self.countLe.setText(str(value))

        if self.segJoints:
            self.baseJnt | self.endJnt
            pm.delete(self.segJoints)

        pm.select(self.baseJnt, r=True)
        self.segJoints = addJointSegments(value)
        pm.select(cl=True)


class CustomSlider(QtWidgets.QSlider):
    focused = QtCore.Signal()

    def __init__(self):
        super(CustomSlider, self).__init__()

    def focusInEvent(self, event):
        super(CustomSlider, self).focusInEvent(event)
        self.focused.emit()
