from PySide2 import QtCore, QtWidgets, QtGui
from . import baseWidget


class CustomLineEdit(QtWidgets.QLineEdit):
    def paintEvent( self, event ):
        painter = QtGui.QPainter(self)

        metrics = QtGui.QFontMetrics(self.font())
        elided  = metrics.elidedText(self.text(), QtCore.Qt.ElideLeft, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)


class TextField(baseWidget.BaseWidget):
    def __init__(self, text='', parent=None):
        super().__init__(parent)

        self.__lineEdit.setText(text)

    def _createWidgets(self):
        self.__lineEdit = CustomLineEdit()

    def _layoutWidgets(self):
        self._mainLayout = QtWidgets.QGridLayout(self)
        self._mainLayout.addWidget(self.__lineEdit, 0, 1)

    def _connectWidgets(self):
        self.__lineEdit.editingFinished.connect(self.__setText)

    def __setText(self):
        self.text = self.__lineEdit.text()

    @property
    def text(self):
        return self.__lineEdit.text()

    @text.setter
    def text(self, text):
        self.__lineEdit.setText(text)

    @property
    def placeHolderText(self):
        return self.__lineEdit.placeholderText()

    @placeHolderText.setter
    def placeHolderText(self, text):
        self.__lineEdit.setPlaceholderText(text)

    def setChangedCommand(self, function):
        self.__lineEdit.textChanged.connect(function)

    def setEnterCommand(self, function):
        self.__lineEdit.editingFinished.connect(function)
