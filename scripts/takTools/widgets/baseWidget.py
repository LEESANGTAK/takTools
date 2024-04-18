from PySide2 import QtWidgets


class BaseWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(BaseWidget, self).__init__(parent)

        self._createWidgets()
        self._layoutWidgets()
        self._connectWidgets()
        self._setDefaults()

    def _createWidgets(self):
        pass

    def _layoutWidgets(self):
        pass

    def _connectWidgets(self):
        pass

    def _setDefaults(self):
        pass

    @property
    def width(self):
        return 'Not available'

    @width.setter
    def width(self, val):
        self.setFixedWidth(val)

    @property
    def height(self):
        return 'Not available'

    @height.setter
    def height(self, val):
        self.setFixedHeight(val)

    @property
    def annotation(self):
        return self.toolTip()

    @annotation.setter
    def annotation(self, text):
        self.setToolTip(text)
