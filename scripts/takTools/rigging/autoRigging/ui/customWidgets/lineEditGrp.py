from PySide2 import QtGui, QtCore, QtWidgets


class LineEditGrp(QtWidgets.QWidget):
    def __init__(self, label=None, buttonIcon=None, columnsWidth=None, parent=None):
        super(LineEditGrp, self).__init__(parent)

        self.label = label
        self.buttonIcon = buttonIcon
        self.columnsWidth = columnsWidth

        self.createWidgets()
        self.createLayouts()

        self.setButtonIcon(self.buttonIcon)
        self.setColumnsWidth(self.columnsWidth)

    def createWidgets(self):
        self.labelWidget = QtWidgets.QLabel(self.label)
        self.lineEditWidget = QtWidgets.QLineEdit()
        self.buttonWidget = QtWidgets.QPushButton()

    def createLayouts(self):
        mainLayout = QtWidgets.QHBoxLayout(self)
        mainLayout.addWidget(self.labelWidget)
        mainLayout.addWidget(self.lineEditWidget)
        mainLayout.addWidget(self.buttonWidget)

    def setLabel(self, label):
        self.label = label
        self.labelWidget.setText(self.label)

    def setButtonIcon(self, buttonIcon):
        self.buttonIcon = buttonIcon
        self.buttonWidget.setIcon(QtGui.QIcon(self.buttonIcon))

    def setColumnsWidth(self, columnsWidth):
        if not columnsWidth:
            return False

        self.labelWidget.setFixedWidth(columnsWidth[0])
        self.lineEditWidget.setFixedWidth(columnsWidth[1])
        self.buttonWidget.setFixedWidth(columnsWidth[2])
