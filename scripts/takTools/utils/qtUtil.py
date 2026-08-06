import os



from maya import cmds
from maya import OpenMayaUI as omui

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide import QtWidgets, QtGui, QtCore
    from shiboken import wrapInstance
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance
elif 2025 <= MAYA_VERSION:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance


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


def editScriptEditorHorizontal(consoleSide='left'):
    panel = next((item for item in cmds.getPanel(all=True) if "scriptEditorPanel" in item), None)

    if not panel:
        print("Not found script editor panel.")
        return

    ptr = omui.MQtUtil.findControl(panel)
    if not ptr:
        ptr = omui.MQtUtil.findLayout(panel)

    qtpanel = wrapInstance(int(ptr), QtWidgets.QWidget)

    menuBar, mainWidget = qtpanel.children()[1:]

    seww = mainWidget.layout().itemAt(1).widget()
    sewww = seww.children()[-1]

    splitter = sewww.children()[1]

    if splitter.orientation() == QtCore.Qt.Orientation.Vertical:
        script_console = splitter.widget(0)
        script_editor = splitter.widget(1)
        splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        if consoleSide == 'left':
            splitter.insertWidget(0, script_console)
        else:
            splitter.insertWidget(0, script_editor)
    else:
        if consoleSide == 'left':
            script_console = splitter.widget(0)
            script_editor = splitter.widget(1)
        else:
            script_editor = splitter.widget(0)
            script_console = splitter.widget(1)
        splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        splitter.insertWidget(0, script_console)
