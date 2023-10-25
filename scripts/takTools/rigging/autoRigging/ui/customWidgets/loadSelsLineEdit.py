from PySide2 import QtCore, QtGui, QtWidgets

import pymel.core as pm

class LoadSelsLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(LoadSelsLineEdit, self).__init__(parent)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showLineEditPopupMenu)

    def showLineEditPopupMenu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.addAction('Load Selections', self.setSelection)
        menu.exec_(self.mapToGlobal(pos))

    def setSelection(self):
        selsStr = ''
        concatenateStr = ','
        sels = pm.selected()

        for sel in sels:
            if sels.index(sel) == len(sels)-1:
                concatenateStr = ''
            selsStr += (sel.name() + concatenateStr)

        self.setText(selsStr)
