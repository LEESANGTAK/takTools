from PySide2 import QtWidgets

from ..customWidgets import loadSelsLineEdit

class BaseForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(BaseForm, self).__init__(parent)

        self.createWidgets()
        self.createLayouts()
        self.setDefault()

    def createWidgets(self):
        self.modelLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.skeletonLe = loadSelsLineEdit.LoadSelsLineEdit()
        self.zAxisUpChk = QtWidgets.QCheckBox()
        self.rootCtrlChk = QtWidgets.QCheckBox()
        self.ctrlShapeCb = QtWidgets.QComboBox()

    def createLayouts(self):
        formLayout = QtWidgets.QFormLayout(self)

        formLayout.addRow('Model: ', self.modelLe)
        formLayout.addRow('Skeleton: ', self.skeletonLe)
        formLayout.addRow('Z-Axis Up: ', self.zAxisUpChk)
        formLayout.addRow('Root Control: ', self.rootCtrlChk)
        formLayout.addRow('Control Shape: ', self.ctrlShapeCb)

    def setDefault(self):
        self.zAxisUpChk.setChecked(True)
        self.ctrlShapeCb.addItems(['circleY', 'pentagon'])