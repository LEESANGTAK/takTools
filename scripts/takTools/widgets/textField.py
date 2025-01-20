from maya import cmds

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide import QtCore, QtWidgets
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2 import QtCore, QtWidgets
elif 2025 <= MAYA_VERSION:
    from PySide6 import QtCore, QtWidgets

from . import baseWidget


class TextField(baseWidget.BaseWidget):
    def __init__(self, parent=None):
        super(TextField, self).__init__(parent)

    def _createWidgets(self):
        self._lineEdit = QtWidgets.QLineEdit()
        self._lineEdit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def _layoutWidgets(self):
        self._mainLayout = QtWidgets.QGridLayout(self)
        self._mainLayout.addWidget(self._lineEdit, 0, 1)

    def _connectWidgets(self):
        self._lineEdit.editingFinished.connect(self._setText)
        self._lineEdit.customContextMenuRequested.connect(self._showPopupMenu)

    def _setText(self):
        self.text = self._lineEdit.text()

    def _showPopupMenu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setToolTipsVisible(True)
        loadSelAction = menu.addAction('Load Selection', self._loadSelection)
        loadSelAction.setToolTip('Fill text with current selection in the scene.')
        menu.exec_(self._lineEdit.mapToGlobal(pos))

    def _loadSelection(self):
        sels = cmds.ls(sl=True, fl=True)
        self._lineEdit.setText(','.join(sels))

    @property
    def text(self):
        return self._lineEdit.text()

    @text.setter
    def text(self, text):
        self._lineEdit.setText(text)

    @property
    def placeHolderText(self):
        return self._lineEdit.placeholderText()

    @placeHolderText.setter
    def placeHolderText(self, text):
        self._lineEdit.setPlaceholderText(text)

    def setChangedCommand(self, function):
        self._lineEdit.textChanged.connect(function)

    def setFinishedCommand(self, function):
        self._lineEdit.editingFinished.connect(function)
