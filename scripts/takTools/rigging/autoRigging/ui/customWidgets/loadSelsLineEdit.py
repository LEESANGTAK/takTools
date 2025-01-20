from maya import cmds
import pymel.core as pm

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide import QtCore, QtGui, QtWidgets
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2 import QtCore, QtGui, QtWidgets
elif 2025 <= MAYA_VERSION:
    from PySide6 import QtCore, QtGui, QtWidgets


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
