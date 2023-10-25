"""
Author: LEE SANGTAK
Contact: chst27@gmail.com
"""

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.XgExternalAPI as xge
import pymel.core as pm
import maya.OpenMayaUI as omui

from shiboken2 import wrapInstance


def getMayaMainWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaWinPtr), QWidget)


class XGenBaker(QDialog):
    def __init__(self):
        super(XGenBaker, self).__init__()
        self.setWindowTitle('XGen Baker')
        self.setParent(getMayaMainWin())
        self.setWindowFlags(Qt.Tool)

        self.collections = xg.palettes()

        self.prepare()
        self.buildUI()


    def prepare(self):
        # Set evaluation mode to DG
        pm.evaluationManager(mode='off')

        pm.setAttr('defaultRenderGlobals.animation', True)
        pm.setAttr('defaultRenderGlobals.useFrameExt', True)
        pm.setAttr('defaultRenderGlobals.putFrameBeforeExt', True)
        pm.setAttr('defaultRenderGlobals.extensionPadding', 4)

        pm.mel.eval('xgmPreview -clean;')

        # Description render setting
        for collection in self.collections:
            descriptions = xg.descriptions(collection)
            for description in descriptions:
                xg.setAttr("renderer", xge.prepForAttribute('Arnold Renderer'), collection, description, "RendermanRenderer")
                xg.setAttr("custom__arnold_rendermode", xge.prepForAttribute(str(1)), collection, description, "RendermanRenderer")
                xg.setAttr("custom__arnold_minPixelWidth", xge.prepForAttribute(str(0.5)), collection, description, "RendermanRenderer")

        pm.refresh(su=True)
        xgg.DescriptionEditor.exportPatches()
        pm.refresh(su=False)


    def buildUI(self):
        mainLayout = QGridLayout(self)
        self.setLayout(mainLayout)

        mainLayout.addWidget(QLabel('Collection:'), 0, 1)
        self.collectionComboBox = QComboBox()
        self.populateCollectionComboBox()
        mainLayout.addWidget(self.collectionComboBox, 0, 2, 1, 3)

        mainLayout.addWidget(QLabel('Save to...'), 1, 1)
        self.savePathLineEdit = QLineEdit()
        mainLayout.addWidget(self.savePathLineEdit, 1, 2, 1, 2)
        browsButton = QPushButton('Brows...')
        mainLayout.addWidget(browsButton, 1, 4)

        startFrame = pm.playbackOptions(q=True, min=True)
        endFrame = pm.playbackOptions(q=True, max=True)
        mainLayout.addWidget(QLabel('Start Frame: '), 2, 1)
        self.startFrameLineEdit = QLineEdit()
        self.startFrameLineEdit.setText(str(startFrame))
        mainLayout.addWidget(self.startFrameLineEdit, 2, 2)
        mainLayout.addWidget(QLabel('End Frame: '), 2, 3)
        self.endFrameLineEdit = QLineEdit()
        self.endFrameLineEdit.setText(str(endFrame))
        mainLayout.addWidget(self.endFrameLineEdit, 2, 4)

        self.expandProceduralsCheckBox = QCheckBox('Expand Procedurals')
        self.setToolTip('When ass file has a bug, check this option.\nThis will increase exporting time and file size.')
        mainLayout.addWidget(self.expandProceduralsCheckBox, 3, 1)

        exportButton = QPushButton('Export Selected Collection')
        mainLayout.addWidget(exportButton, 4, 1, 1, 4)

        # Connections
        browsButton.clicked.connect(self.getSaveFilePath)
        exportButton.clicked.connect(self.exportCollection)


    def populateCollectionComboBox(self):
        for collection in self.collections:
            self.collectionComboBox.addItem(collection)


    def getSaveFilePath(self):
        startSearchDir = self.savePathLineEdit.text() if self.savePathLineEdit.text() else pm.sceneName().dirname()
        savePathLineEdit = QFileDialog.getSaveFileName(self, 'Export Selection', startSearchDir, 'Ass Export (*.ass;*.ass.gz)')
        self.savePathLineEdit.setText(savePathLineEdit[0])


    def exportCollection(self):
        pm.select(self.collectionComboBox.currentText(), r=True)
        expandProceduralsStr = '-expandProcedurals' if self.expandProceduralsCheckBox.checkState() else ''
        pm.mel.eval('''arnoldExportAss
            -f "{0}"
            -boundingBox
            -compressed {expandProcedurals}
            -shadowLinks 1
            -lightLinks 1
            -s
            -startFrame {1}
            -endFrame {2}
            -frameStep 1.0;'''.format(
                self.savePathLineEdit.text(),
                float(self.startFrameLineEdit.text()),
                float(self.endFrameLineEdit.text()),
                expandProcedurals=expandProceduralsStr
            )
        )