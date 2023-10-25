from PySide2 import QtCore, QtGui, QtWidgets

from ..customWidgets import loadSelsLineEdit

class SplineForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SplineForm, self).__init__(parent)

        self.createWidgets()
        self.createLayouts()
        self.createConnections()
        self.setDefaultState()

    def createWidgets(self):
        self.nameLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.jointsLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.numCtrlLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.stretchChkBox = QtWidgets.QCheckBox()
        self.slideChkBox = QtWidgets.QCheckBox()
        self.twistChkBox = QtWidgets.QCheckBox()
        self.rollChkBox = QtWidgets.QCheckBox()
        self.thickChkBox = QtWidgets.QCheckBox()
        self.waveChkBox = QtWidgets.QCheckBox()
        self.dynamicChkBox = QtWidgets.QCheckBox()
        self.fkChkBox = QtWidgets.QCheckBox()
        self.globalChkBox = QtWidgets.QCheckBox()
        self.parentGrpLe = loadSelsLineEdit.LoadSelsLineEdit()

    def createLayouts(self):
        formLayout = QtWidgets.QFormLayout(self)
        formLayout.addRow('Name: ', self.nameLe)
        formLayout.addRow('Joints: ', self.jointsLe)
        formLayout.addRow('Number of Controls: ', self.numCtrlLe)
        formLayout.addRow('Stretch: ', self.stretchChkBox)
        formLayout.addRow('Slide: ', self.slideChkBox)
        formLayout.addRow('Twist: ', self.twistChkBox)
        formLayout.addRow('Roll: ', self.rollChkBox)
        formLayout.addRow('Thickness: ', self.thickChkBox)
        formLayout.addRow('Wave: ', self.waveChkBox)
        formLayout.addRow('Dynamic: ', self.dynamicChkBox)
        formLayout.addRow('FK: ', self.fkChkBox)
        formLayout.addRow('Global: ', self.globalChkBox)
        formLayout.addRow('Parent Group: ', self.parentGrpLe)

    def createConnections(self):
        self.numCtrlLe.editingFinished.connect(self.setMinNumCtrls)

    def setDefaultState(self):
        self.stretchChkBox.setChecked(True)
        self.twistChkBox.setChecked(True)
        self.rollChkBox.setChecked(True)
        self.waveChkBox.setChecked(True)
        self.numCtrlLe.setText('4')

    def setMinNumCtrls(self):
        val = self.numCtrlLe.text()
        if int(val) < 3:
            self.numCtrlLe.setText('3')
