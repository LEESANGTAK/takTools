from PySide2 import QtCore, QtWidgets
from . import textFieldGrp


class TextFieldButtonGrp(textFieldGrp.TextFieldGrp):
    clicked = QtCore.Signal()

    def __init__(self, text='', label='', buttonLabel=''):
        super(TextFieldButtonGrp, self).__init__(text, label)

        self.buttonLabel = buttonLabel

    def _createWidgets(self):
        super(TextFieldButtonGrp, self)._createWidgets()
        self.__button = QtWidgets.QPushButton()

    def _layoutWidgets(self):
        super(TextFieldButtonGrp, self)._layoutWidgets()
        self._mainLayout.addWidget(self.__button, 0, 2)

    def _connectWidgets(self):
        super(TextFieldButtonGrp, self)._connectWidgets()
        self.__button.clicked.connect(lambda: self.clicked.emit())

    @property
    def buttonLabel(self):
        return self.__button.text()

    @buttonLabel.setter
    def buttonLabel(self, text):
        self.__button.setText(text)
