from PySide2 import QtWidgets
from . import textField


class TextFieldGrp(textField.TextField):
    def __init__(self, text='', label=''):
        super(TextFieldGrp, self).__init__(text)

        self.label = label

    def _createWidgets(self):
        super(TextFieldGrp, self)._createWidgets()
        self.__label = QtWidgets.QLabel()

    def _layoutWidgets(self):
        super(TextFieldGrp, self)._layoutWidgets()
        self._mainLayout.addWidget(self.__label, 0, 0)

    @property
    def label(self):
        return self.__label.text()

    @label.setter
    def label(self, text):
        self.__label.setText(text)
