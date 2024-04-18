from PySide2 import QtWidgets
from . import intField


class IntFieldGrp(intField.IntField):
    def __init__(self, label='Int Field Grp:', value=0, minValue=-1000000, maxValue=1000000, step=1, parent=None):
        super(IntFieldGrp, self).__init__(value, minValue, maxValue, step, parent)

        self.label = label

    def _createWidgets(self):
        super(IntFieldGrp, self)._createWidgets()
        self.__label = QtWidgets.QLabel()

    def _layoutWidgets(self):
        super(IntFieldGrp, self)._layoutWidgets()
        self._mainLayout.addWidget(self.__label, 0, 0)

    @property
    def label(self):
        return self.__label.text()

    @label.setter
    def label(self, text):
        self.__label.setText(text)
