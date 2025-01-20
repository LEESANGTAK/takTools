from functools import partial

from maya import cmds

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide import QtCore, QtWidgets
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2 import QtCore, QtWidgets
elif 2025 <= MAYA_VERSION:
    from PySide6 import QtCore, QtWidgets

from . import baseWidget


class IntField(baseWidget.BaseWidget):
    textChanged = QtCore.Signal(int)
    editingFinished = QtCore.Signal(int)

    def __init__(self, value=0, minValue=-1000000, maxValue=100000, step=1, parent=None):
        self.__value = value
        self.__minValue = minValue
        self.__maxValue = maxValue
        self.__step = step

        super(IntField, self).__init__(parent)

    def _createWidgets(self):
        self.__lineEdit = QtWidgets.QLineEdit(str(self.__value))

    def _layoutWidgets(self):
        self._mainLayout = QtWidgets.QGridLayout(self)
        self._mainLayout.addWidget(self.__lineEdit, 0, 1)

    def _connectWidgets(self):
        self.__lineEdit.textChanged.connect(partial(self.textChanged, self.value))
        self.__lineEdit.editingFinished.connect(self.__editingFinished)

    def __editingFinished(self):
        self.__setValue()
        self.editingFinished.emit(self.value)

    def __setValue(self):
        try:
            self.value = int(float(self.__lineEdit.text()))
        except ValueError as e:
            self.value = 0

    @property
    def value(self):
        self.value = int(self.__lineEdit.text())
        return self.__value

    @value.setter
    def value(self, val):
        self.__value = max(min(val, self.__maxValue), self.__minValue)
        self.__lineEdit.setText(str(self.__value))

    @property
    def minValue(self):
        return self.__minValue

    @minValue.setter
    def minValue(self, val):
        self.__minValue = val

    @property
    def maxValue(self):
        return self.__maxValue

    @maxValue.setter
    def maxValue(self, val):
        self.__maxValue = val

    @property
    def step(self):
        return self.__step

    @step.setter
    def step(self, val):
        self.__step = val
