from maya import cmds

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide import QtCore, QtGui, QtWidgets
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2 import QtCore, QtGui, QtWidgets
elif 2025 <= MAYA_VERSION:
    from PySide6 import QtCore, QtGui, QtWidgets

from ..customWidgets import loadSelsLineEdit

import pymel.core as pm

class LimbForm(QtWidgets.QWidget):
    def __init__(self):
        super(LimbForm, self).__init__()

        self.createWidgets()
        self.createLayouts()
        self.createConnections()
        self.setDefaultState()

    def createWidgets(self):
        self.nameLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.limbJntsLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.fkChk = QtWidgets.QCheckBox()
        self.ikChk = QtWidgets.QCheckBox()
        self.fkIkSwitchChk = QtWidgets.QCheckBox()
        self.twistChk = QtWidgets.QCheckBox()
        self.upTwistJntsLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.lowTwistJntsLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.aimAxisSignCb = QtWidgets.QComboBox()
        self.parentGrpLe = loadSelsLineEdit.LoadSelsLineEdit()

    def createLayouts(self):
        formLayout = QtWidgets.QFormLayout(self)
        formLayout.addRow('Name: ', self.nameLe)
        formLayout.addRow('Limb Joints: ', self.limbJntsLe)
        formLayout.addRow('FK: ', self.fkChk)
        formLayout.addRow('IK: ', self.ikChk)
        formLayout.addRow('FK/IK Switch: ', self.fkIkSwitchChk)
        formLayout.addRow('Twist: ', self.twistChk)
        formLayout.addRow('Upper Twist Joints: ', self.upTwistJntsLe)
        formLayout.addRow('Lower Twist Joints: ', self.lowTwistJntsLe)
        formLayout.addRow('Aim Axis Sign: ', self.aimAxisSignCb)
        formLayout.addRow('Parent Space: ', self.parentGrpLe)

    def createConnections(self):
        self.twistChk.stateChanged.connect(self.setTwistJntsLeState)

    def setDefaultState(self):
        self.aimAxisSignCb.addItems(['+', '-'])
        self.fkChk.setCheckState(QtCore.Qt.Checked)
        self.ikChk.setCheckState(QtCore.Qt.Checked)
        self.fkIkSwitchChk.setCheckState(QtCore.Qt.Checked)
        self.setTwistJntsLeState(False)

    def setTwistJntsLeState(self, checked):
        if not checked:
            self.aimAxisSignCb.setDisabled(True)
            LimbForm.setLineEditState(self.upTwistJntsLe, False)
            LimbForm.setLineEditState(self.lowTwistJntsLe, False)
        else:
            self.aimAxisSignCb.setDisabled(False)
            LimbForm.setLineEditState(self.upTwistJntsLe, True)
            LimbForm.setLineEditState(self.lowTwistJntsLe, True)

    @staticmethod
    def setLineEditState(lineEditWidget, enable):
        if enable:
            lineEditWidget.setStyleSheet('')
            lineEditWidget.setDisabled(False)
        else:
            lineEditWidget.clear()
            lineEditWidget.setStyleSheet('background-color: grey;')
            lineEditWidget.setDisabled(True)