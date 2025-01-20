from maya import cmds

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide import QtWidgets
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2 import QtWidgets
elif 2025 <= MAYA_VERSION:
    from PySide6 import QtWidgets


from . import floatField


class FloatFieldGrp(floatField.FloatField):
    def __init__(self, label='Float Field Grp:', value=0.0, minValue=-1000000.0, maxValue=1000000.0, step=1.0, parent=None):
        super(FloatFieldGrp, self).__init__(value, minValue, maxValue, step, parent)

        self.label = label

    def _createWidgets(self):
        super(FloatFieldGrp, self)._createWidgets()
        self.__label = QtWidgets.QLabel()

    def _layoutWidgets(self):
        super(FloatFieldGrp, self)._layoutWidgets()
        self._mainLayout.addWidget(self.__label, 0, 0)

    @property
    def label(self):
        return self.__label.text()

    @label.setter
    def label(self, text):
        self.__label.setText(text)
