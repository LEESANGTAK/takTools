from PySide2 import QtCore, QtGui, QtWidgets

from ..customWidgets import loadSelsLineEdit


class SingleJointsForm(QtWidgets.QWidget):
    def __init__(self):
        super(SingleJointsForm, self).__init__()

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
