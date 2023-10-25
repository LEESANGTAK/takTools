"""
Author: Tak
Mail: chst27@gmail.com
Website: https://tak.ta-note.com
Description: Searching maya resource images.
"""

from PySide2 import QtWidgets, QtGui, QtCore

import maya.OpenMayaUI as omui
import maya.cmds as cmds

from shiboken2 import wrapInstance


def getMayaResourceImages():
    images = []

    images = cmds.resourceManager(nameFilter='*.png')

    return images

def getMayaWin():
    mayaWin = None

    mayaWinPtr = omui.MQtUtil.mainWindow()
    mayaWin = wrapInstance(long(mayaWinPtr), QtWidgets.QWidget)

    return mayaWin


class TakMayaResourceBrowser(QtWidgets.QDialog):
    TITLE = 'Tak Maya Resource Browser'
    VERSION = '1.0.1'
    instance = None

    def __init__(self, parent=getMayaWin()):
        super(TakMayaResourceBrowser, self).__init__(parent)

        self.setWindowTitle('{0} - {1}'.format(TakMayaResourceBrowser.TITLE, TakMayaResourceBrowser.VERSION))
        self.setWindowFlags(QtCore.Qt.Tool)
        self.resize(550, 500)

        self.mayaResourceImages = getMayaResourceImages()
        self.geo = None

        self.buildUI()
        self.populateImageList()
        self.connectWidgets()

    def buildUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)

        self.searchLe = QtWidgets.QLineEdit()
        self.searchLe.setPlaceholderText('Search...')
        mainLayout.addWidget(self.searchLe)

        self.imageList = QtWidgets.QListWidget()
        self.imageList.setViewMode(QtWidgets.QListWidget.IconMode)
        self.imageList.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.imageList.setIconSize(QtCore.QSize(50, 50))
        self.imageList.setGridSize(QtCore.QSize(100, 50))
        mainLayout.addWidget(self.imageList)

    def populateImageList(self):
        self.imageList.clear()

        for image in self.mayaResourceImages:
            imageItem = ImageItem(image)
            self.imageList.addItem(imageItem)

    def connectWidgets(self):
        self.searchLe.editingFinished.connect(self.showMatchingImages)
        self.imageList.currentItemChanged.connect(self.printImagename)

    def printImagename(self, item):
        print(item.text())

    def showMatchingImages(self):
        text = self.searchLe.text()
        matchingImages = self.getMatchingImages(text)

        if matchingImages:
            self.imageList.clear()
            for image in matchingImages:
                imageItem = ImageItem(image)
                self.imageList.addItem(imageItem)
        elif text and not matchingImages:
            self.imageList.clear()
        else:
            self.populateImageList()

    def getMatchingImages(self, searchStr):
        images = []

        searchStr = searchStr.lower()
        self.mayaResourceImages

        for image in self.mayaResourceImages:
            if searchStr in image.lower():
                images.append(image)

        return images

    @classmethod
    def showUI(cls):
        if not cls.instance:
            cls.instance = TakMayaResourceBrowser()
        if cls.instance.isHidden():
            cls.instance.show()
        else:
            cls.instance.raise_()
            cls.instance.activateWindow()

    def showEvent(self, event):
        if self.geo:
            super(TakMayaResourceBrowser, self).showEvent(event)
            self.restoreGeometry(self.geo)

    def closeEvent(self, event):
        if isinstance(self, TakMayaResourceBrowser):
            super(TakMayaResourceBrowser, self).closeEvent(event)
            self.geo = self.saveGeometry()


class ImageItem(QtWidgets.QListWidgetItem):
    def __init__(self, image):
        super(ImageItem, self).__init__()

        self.setText(image)
        self.setIcon(QtGui.QIcon(':{0}'.format(image)))
        self.setToolTip(image)
