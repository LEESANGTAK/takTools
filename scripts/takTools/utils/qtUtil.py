import os
from PySide2 import QtCore, QtGui, QtWidgets

import pymel.core as pm


class ScreenCapture(QtWidgets.QDialog):
    """
    sc = ScreenCapture()
    sc.show()
    """
    def __init__(self, parent=None):
        super(ScreenCapture, self).__init__(parent)

        self.startPos = None
        self.lastSelRectWidth = None

        self.capturedPixmap = None
        self.desktopPixmap = None
        self.selectedRect = QtCore.QRect()

        self.setGeometry(QtWidgets.QApplication.desktop().geometry())
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.captureDesktop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.desktopPixmap)

        pen = QtGui.QPen(QtCore.Qt.red, 3)
        painter.setPen(pen)

        path = QtGui.QPainterPath()
        path.addRect(self.rect())
        path.addRect(self.selectedRect)
        painter.fillPath(path, QtGui.QColor.fromRgb(255, 255, 255, 100))

        painter.drawRect(self.selectedRect)

    def mousePressEvent(self, event):
        posInWin = self.window().mapFromGlobal(event.globalPos())
        self.startPos = posInWin
        self.selectedRect.setTopLeft(posInWin)

    def mouseMoveEvent(self, event):
        posInWin = self.window().mapFromGlobal(event.globalPos())

        if event.modifiers() == QtCore.Qt.Key_Escape:
            self.ignore()

        if event.modifiers() == QtCore.Qt.ShiftModifier:
            width = posInWin.x() - self.startPos.x()
            squareBtmRightPos = QtCore.QPoint(self.startPos.x()+width, self.startPos.y()+width)
            self.selectedRect.setBottomRight(squareBtmRightPos)
            self.lastSelRectWidth = width
        elif event.modifiers() == (QtCore.Qt.ShiftModifier | QtCore.Qt.AltModifier):
            topLeftPos = QtCore.QPoint(posInWin.x()-self.lastSelRectWidth, posInWin.y()-self.lastSelRectWidth)
            self.selectedRect.setTopLeft(topLeftPos)
            self.selectedRect.setBottomRight(posInWin)
            self.startPos = topLeftPos
        else:
            self.selectedRect.setBottomRight(posInWin)

        self.update()

    def mouseReleaseEvent(self, event):
        self.capturedPixmap = self.desktopPixmap.copy(self.selectedRect.normalized())
        self.capturedPixmap.save('D:/test.png', 'PNG')
        self.accept()

    def captureDesktop(self):
        screenGeometry = QtCore.QRect(QtWidgets.QApplication.primaryScreen().virtualGeometry())
        self.desktopPixmap = QtGui.QPixmap.grabWindow(
            QtWidgets.QApplication.desktop().winId(),
            screenGeometry.x(),
            screenGeometry.y(),
            screenGeometry.width(),
            screenGeometry.height(),
        )


def duplicateImage(imagePath, suffix='_copy'):
    folder = os.path.dirname(imagePath)
    origFileName, ext = os.path.splitext(os.path.basename(imagePath))
    newFileName = '{}{}{}'.format(origFileName, suffix, ext)
    newImagePath = os.path.join(folder, newFileName)

    qimg = QtGui.QImage(imagePath)
    qimg.save(newImagePath, ext.strip('.'))


def editScriptEditorHorizontal():
    panel = None
    allPanels = pm.getPanel(all=True)
    for item in allPanels:
        if "scriptEditorPanel" in item:
            panel = item

    if not panel:
        print("Not found script editor panel.")
        return

    qtpanel = panel.asQtObject()

    menuBar, mainWidget = qtpanel.children()[1:]

    seww = mainWidget.layout().itemAt(1).widget()
    sewww = seww.children()[-1]

    splitter = sewww.children()[1]
    splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)

    script_console = splitter.widget(0)
    script_editor = splitter.widget(1)

    splitter.insertWidget(0, script_editor)

    se_splitter = script_editor.children()[1]

    editor = se_splitter.children()[1]
    tabWidget = editor.children()[1]

    tabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
