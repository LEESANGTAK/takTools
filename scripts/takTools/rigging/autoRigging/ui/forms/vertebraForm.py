from maya import cmds

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide import QtCore, QtGui, QtWidgets
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2 import QtCore, QtGui, QtWidgets
elif 2025 <= MAYA_VERSION:
    from PySide6 import QtCore, QtGui, QtWidgets

from ..customWidgets import loadSelsLineEdit

class VertebraForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(VertebraForm, self).__init__(parent)

        self.createWidgets()
        self.createLayouts()
        self.createConnections()
        self.setDefaultState()

    def createWidgets(self):
        self.nameLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.jointsLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.parentGrpLe = loadSelsLineEdit.LoadSelsLineEdit()

    def createLayouts(self):
        formLayout = QtWidgets.QFormLayout(self)
        formLayout.addRow('Name: ', self.nameLe)
        formLayout.addRow('Joints: ', self.jointsLe)
        formLayout.addRow('Parent Group: ', self.parentGrpLe)

    def createConnections(self):
        pass

    def setDefaultState(self):
        pass