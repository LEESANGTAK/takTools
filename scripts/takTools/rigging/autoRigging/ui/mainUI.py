from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

from . import skeletonWidget
from . import buildWidget
from . import utilsWidget


def getMayaMainWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mayaWinPtr), QtWidgets.QWidget)

class MainUI(QtWidgets.QDialog):
    TOOL_NAME = 'Tak Auto Rigger'
    VERSION = '1.0.0'

    uiInstance = None

    def __init__(self, parent=getMayaMainWin()):
        super(MainUI, self).__init__(parent)

        self.geometry = None
        self.setWindowTitle('{0} - {1}'.format(MainUI.TOOL_NAME, MainUI.VERSION))

        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    def createWidgets(self):
        self.skeletonWidget = skeletonWidget.SkeletonWidget()
        self.buildWidget = buildWidget.BuildWidget()
        self.utilsWidget = utilsWidget.UtilWidget()

        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.addTab(self.skeletonWidget, 'Skeleton')
        self.tabWidget.addTab(self.buildWidget, 'Build')
        self.tabWidget.addTab(self.utilsWidget, 'Utils')

    def createLayouts(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.mainLayout.addWidget(self.tabWidget)

    def createConnections(self):
        print('Create connections.')

    ### Methods for Publish ###
    @classmethod
    def showUI(cls):
        if not cls.uiInstance:
            cls.uiInstance = MainUI()

        if cls.uiInstance.isHidden():
            cls.uiInstance.show()
        else:
            cls.uiInstance.raise_()
            cls.uiInstance.activateWindow()

    def showEvent(self, event):
        super(MainUI, self).showEvent(event)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, event):
        if isinstance(self, MainUI):  # When run code closeEvent() method queued. Calling closeEvent() method after dialog deleted an error occurred. So instance checking needed.
            super(MainUI, self).closeEvent(event)

            self.geometry = self.saveGeometry()
