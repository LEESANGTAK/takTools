from maya import cmds

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide import QtCore, QtGui, QtWidgets
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2 import QtCore, QtGui, QtWidgets
elif 2025 <= MAYA_VERSION:
    from PySide6 import QtCore, QtGui, QtWidgets

from ..customWidgets import loadSelsLineEdit

class SimpleFKForm(QtWidgets.QWidget):
    def __init__(self):
        super(SimpleFKForm, self).__init__()

        self.createWidgets()
        self.createLayouts()

    def createWidgets(self):
        self.nameLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.jointsLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.attachToLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.parentGrpLe = loadSelsLineEdit.LoadSelsLineEdit()

    def createLayouts(self):
        formLayout = QtWidgets.QFormLayout(self)
        formLayout.addRow('Name: ', self.nameLe)
        formLayout.addRow('Joints: ', self.jointsLe)
        formLayout.addRow('Attach To: ', self.attachToLe)
        formLayout.addRow('Parent Group: ', self.parentGrpLe)
