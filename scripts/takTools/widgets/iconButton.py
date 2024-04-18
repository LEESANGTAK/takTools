from PySide2 import QtCore, QtGui, QtWidgets
from . import baseWidget


class IconButton(baseWidget.BaseWidget):
    toggled = QtCore.Signal()
    clicked = QtCore.Signal()

    def __init__(self, icon, iconSize=50, checkable=False, parent=None):
        self.__button = None
        self.__icon = QtGui.QIcon(icon)
        self.__iconSize = iconSize
        self.__checkable = checkable

        super(IconButton, self).__init__(parent)

    @property
    def iconSize(self):
        return self.__iconSize

    @iconSize.setter
    def iconSize(self, val):
        self.__iconSize = val

    def _createWidgets(self):
        self.__button = QtWidgets.QPushButton()

    def _layoutWidgets(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addWidget(self.__button)

    def _connectWidgets(self):
        self.__button.toggled.connect(lambda: self.toggled.emit())
        self.__button.clicked.connect(lambda: self.clicked.emit())

    def _setDefaults(self):
        self.__button.setIcon(self.__icon.pixmap(self.__iconSize, self.__iconSize, QtGui.QIcon.Normal, QtGui.QIcon.Off))
        self.__button.setIconSize(QtCore.QSize(self.__iconSize, self.__iconSize))
        self.__button.setCheckable(self.__checkable)
        self.__button.setStyleSheet("""
            QPushButton {background:rgba(0, 0, 0, 0); border:none;}
            QPushButton::checked{background:rgb(82, 133, 166);}
        """)

    def isChecked(self):
        return self.__button.isChecked()

    def setChecked(self, val):
        self.__button.setChecked(val)

    def enterEvent(self, event):
        self.__button.setIcon(self.__icon.pixmap(self.__iconSize, self.__iconSize, QtGui.QIcon.Active, QtGui.QIcon.Off))
        super(IconButton, self).enterEvent(event)

    def leaveEvent(self, event):
        self.__button.setIcon(self.__icon.pixmap(self.__iconSize, self.__iconSize, QtGui.QIcon.Normal, QtGui.QIcon.Off))
        super(IconButton, self).leaveEvent(event)
