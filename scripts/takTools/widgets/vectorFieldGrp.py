import sys
from PySide2 import QtWidgets, QtGui
from . import baseWidget

class VectorFieldGrp(baseWidget.BaseWidget):
    def __init__(self, label='', value=[0.0, 0.0, 0.0], parent=None):
        self.__label = label
        self.__valX = value[0]
        self.__valY = value[1]
        self.__valZ = value[2]

        super(VectorFieldGrp, self).__init__(parent)

    @property
    def value(self):
        return (self.__valX, self.__valY, self.__valZ)

    @value.setter
    def value(self, values):
        if not isinstance(values, tuple) or not isinstance(values, list) or len(values) < 3:
            sys.stderr('Values should be a list or a tuple of float vaules.')
        self.__valX, self.__valY, self.__valZ = values
        self.__lineEditX.setText(str(self.__valX))
        self.__lineEditY.setText(str(self.__valY))
        self.__lineEditZ.setText(str(self.__valZ))

    def _createWidgets(self):
        self.__label = QtWidgets.QLabel(self.__label)

        self.__lineEditX = QtWidgets.QLineEdit(str(self.__valX))
        self.__lineEditX.setValidator(QtGui.QDoubleValidator())

        self.__lineEditY = QtWidgets.QLineEdit(str(self.__valY))
        self.__lineEditY.setValidator(QtGui.QDoubleValidator())

        self.__lineEditZ = QtWidgets.QLineEdit(str(self.__valZ))
        self.__lineEditZ.setValidator(QtGui.QDoubleValidator())

    def _layoutWidgets(self):
        self._mainLayout = QtWidgets.QGridLayout(self)
        self._mainLayout.addWidget(self.__label, 0, 0)
        self._mainLayout.addWidget(self.__lineEditX, 0, 1)
        self._mainLayout.addWidget(self.__lineEditY, 0, 2)
        self._mainLayout.addWidget(self.__lineEditZ, 0, 3)

    def _connectWidgets(self):
        self.__lineEditX.textChanged.connect(self.__setValue)
        self.__lineEditY.textChanged.connect(self.__setValue)
        self.__lineEditZ.textChanged.connect(self.__setValue)

    def __setValue(self):
        if self.sender() == self.__lineEditX:
            self.__valX = float(self.__lineEditX.text())
        if self.sender() == self.__lineEditY:
            self.__valY = float(self.__lineEditY.text())
        if self.sender() == self.__lineEditZ:
            self.__valZ = float(self.__lineEditZ.text())
