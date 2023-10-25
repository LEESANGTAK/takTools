"""
Author: LEE SANGTAK
Contact: chst27@gmail.com
"""

import glob
import os
import re
from collections import OrderedDict
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import pymel.core as pm
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import tak_b2Pipeline_add
import tak_b2Pipeline_xgen


def getMayaMainWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaWinPtr), QWidget)


def setupShot(relDirPath):
    shotInfoFile = glob.glob(relDirPath+'/*.xml')[0]
    with open(shotInfoFile, 'r') as f:
        shotInfoFileContents = f.read()
        fps = re.search(r'<fps>(\w+)</fps>', shotInfoFileContents).group(1)
        startFrame = re.search(r'<stFrame>(\d+)</stFrame>', shotInfoFileContents).group(1)
        endFrame = re.search(r'<edFrame>(\d+)</edFrame>', shotInfoFileContents).group(1)

        pm.currentUnit(time=fps)
        pm.playbackOptions(minTime=startFrame)
        pm.playbackOptions(maxTime=endFrame)


class AttachAbcToXGen(QDialog):
    xgenAssets = OrderedDict([
        ('masamiHair', 'P:/1801_A71/4.Asset/prp/masamiHair/mdl/release/r001/prp_masamiHair_mdl_r001.ma'),
        ('tomokoHair', 'P:/1801_A71/4.Asset/prp/tomokoHair/mdl/release/r001/prp_tomokoHair_mdl_r001.ma'),
        ('girlAhair', 'P:/1801_A71/4.Asset/prp/girlAhair/mdl/release/r001/prp_girlAhair_mdl_r001.ma'),
        ('girlBhair', 'P:/1801_A71/4.Asset/prp/girlBhair/mdl/release/r001/prp_girlBhair_mdl_r001.ma'),
        ('sadakoHair', 'P:/1801_A71/4.Asset/prp/sadakoHair/mdl/release/r001/prp_sadakoHair_mdl_r001.ma'),
        ('youshouSadakoHair', 'P:/1801_A71/4.Asset/prp/youshouSadakoHair/mdl/release/r001/prp_youshouSadakoHair_mdl_r001.ma'),
        ('oldmanHair', 'P:/1801_A71/4.Asset/prp/oldmanHair/mdl/release/r001/prp_oldmanHair_mdl_r001.ma'),
        ('ryujiHair', 'P:/1801_A71/4.Asset/prp/ryujiHair/mdl/release/r001/prp_ryujiHair_mdl_r001.ma'),
        ('youichiHair', 'P:/1801_A71/4.Asset/prp/youichiHair/mdl/release/r001/prp_youichiHair_mdl_r001.ma'),
        ('shizukoHair', 'P:/1801_A71/4.Asset/prp/shizukoHair/mdl/release/r001/prp_shizukoHair_mdl_r001.ma'),
        ('doctorHair', 'P:/1801_A71/4.Asset/prp/doctorHair/mdl/release/r001/prp_doctorHair_mdl_r001.ma'),
        ('reikoHair', 'P:/1801_A71/4.Asset/prp/reikoHair/mdl/release/r001/prp_reikoHair_mdl_r001.ma'),
        ('shizukoLongHair', 'P:/1801_A71/4.Asset/prp/shizukoLongHair/mdl/release/r003/prp_shizukoLongHair_mdl_r003.ma'),
        ('doctorHair', 'P:/1801_A71/4.Asset/prp/doctorHair/mdl/release/r001/prp_doctorHair_mdl_r001.ma'),
        ('reikoHair', 'P:/1801_A71/4.Asset/prp/reikoHair/mdl/release/r001/prp_reikoHair_mdl_r001.ma'),
        ('dollHair', 'P:/1801_A71/4.Asset/prp/dollHair/mdl/release/r001/prp_dollHair_mdl_r001.ma'),
        ('taejungHair', 'P:/1703_STH/4.Asset/prp/taejungHair/mdl/release/r001/prp_taejungHair_mdl_r001.ma'),
        ('taejungDamagedHair', 'P:/1703_STH/4.Asset/prp/taejungDamagedHair/mdl/release/r001/prp_taejungDamagedHair_mdl_r001.ma'),
        ('GmanHair', 'P:/1703_STH/4.Asset/prp/GmanHair/mdl/release/r001/prp_GmanHair_mdl_r001.ma'),
        ('GmanDamagedHair', 'P:/1703_STH/4.Asset/prp/GmanDamagedHair/mdl/release/r001/prp_GmanDamagedHair_mdl_r001.ma'),
        ('hwajaHair', 'P:/1703_STH/4.Asset/prp/hwajaHair/mdl/release/r001/prp_hwajaHair_mdl_r001.ma'),
        ('invisibleHair', 'P:/1703_STH/4.Asset/prp/invisibleHair/mdl/release/r001/prp_invisibleHair_mdl_r001.ma'),
        ('mightyEyebrows', 'P:/1703_STH/4.Asset/prp/mightyEyebrows/mdl/release/r001/prp_mightyEyebrows_mdl_r001.ma')
    ])

    def __init__(self):
        super(AttachAbcToXGen, self).__init__()
        self.setWindowTitle('Attach Alembic to XGen')
        self.setParent(getMayaMainWin())
        self.setWindowFlags(Qt.Tool)

        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        # XGen asset widget
        xgAssetWidget = QWidget()
        xgAssetLayout = QHBoxLayout()
        xgAssetWidget.setLayout(xgAssetLayout)

        xgAssetLayout.addWidget(QLabel('XGen Asset: '))

        self.xgenAssetComboBox = QComboBox()
        self.xgenAssetComboBox.addItems(self.xgenAssets.keys())
        xgAssetLayout.addWidget(self.xgenAssetComboBox)

        mainLayout.addWidget(xgAssetWidget)

        # Namespace widget
        namespaceWidget = QWidget()
        mainLayout.addWidget(namespaceWidget)
        namespaceWidgetLayout = QHBoxLayout(namespaceWidget)

        namespaceWidgetLayout.addWidget(QLabel('Namespace: '))

        self.namespaceLineEdit = QLineEdit()
        namespaceWidgetLayout.addWidget(self.namespaceLineEdit)

        # Cache widgets
        cacheGrpBox = QGroupBox('Caches')
        cacheGrpBox.setStyleSheet('QGroupBox::title {subcontrol-origin: margin; left: 10px; bottom: 5px; padding: 0px 5px 0px 5px;} QGroupBox {font-size: 15px; font: bold; border: 1px solid gray; border-radius: 6px; margin-top: 6px; margin-bottom: 10px}')
        cacheGrpBoxLayout = QVBoxLayout()
        cacheGrpBox.setLayout(cacheGrpBoxLayout)

        # Release directory widget
        relDirLayout = QHBoxLayout()

        relDirLayout.addWidget(QLabel('Release Directory Path: '))

        self.relDirLineEdit = QLineEdit()
        relDirLayout.addWidget(self.relDirLineEdit)

        relDirBrowsBtn = QPushButton('Brows...')
        relDirLayout.addWidget(relDirBrowsBtn)

        cacheGrpBoxLayout.addLayout(relDirLayout)

        # Scalp cache widgets
        scalpCacheLayout = QHBoxLayout()

        scalpCacheLayout.addWidget(QLabel('Scalp Cache Path: '))

        self.scalpCacheLineEdit = QLineEdit()
        scalpCacheLayout.addWidget(self.scalpCacheLineEdit)

        scalpCacheBrowsBtn = QPushButton('Brows...')
        scalpCacheLayout.addWidget(scalpCacheBrowsBtn)

        cacheGrpBoxLayout.addLayout(scalpCacheLayout)

        # Curve cache widgets
        cacheGrpBoxLayout.addWidget(QLabel('Curve Caches Path: '))

        curveCacheBrowsBtn = QPushButton('Brows...')
        cacheGrpBoxLayout.addWidget(curveCacheBrowsBtn)

        self.curveCacheList = QListWidget()
        cacheGrpBoxLayout.addWidget(self.curveCacheList)

        mainLayout.addWidget(cacheGrpBox)

        # Attach button
        attachBtn = QPushButton('Run')
        mainLayout.addWidget(attachBtn)

        # Connect
        relDirBrowsBtn.clicked.connect(self.getRelDirPath)
        scalpCacheBrowsBtn.clicked.connect(self.getScalpCachePath)
        curveCacheBrowsBtn.clicked.connect(self.getCurveCachePaths)
        attachBtn.clicked.connect(self.attachAbcToXGen)

    def getRelDirPath(self):
        startSearchDir = self.relDirLineEdit.text() if self.relDirLineEdit.text() else pm.sceneName().dirname()
        relDir = QFileDialog.getExistingDirectory(self, 'Select Release Directory', startSearchDir)
        self.relDirLineEdit.setText(relDir)

    def getScalpCachePath(self):
        startSearchDir = self.relDirLineEdit.text() if self.relDirLineEdit.text() else pm.sceneName().dirname()
        scalpPath = QFileDialog.getOpenFileName(self, 'Select Scalp Alembic File', startSearchDir, 'Alembic File (*.abc)')
        self.scalpCacheLineEdit.setText(scalpPath[0])

    def getCurveCachePaths(self):
        # Remove existing items
        while self.curveCacheList.count() > 0:
            self.curveCacheList.takeItem(0)

        startSearchDir = self.relDirLineEdit.text() if self.relDirLineEdit.text() else pm.sceneName().dirname()
        curvePath = QFileDialog.getOpenFileNames(self, 'Select Curve Alembic File', startSearchDir, 'Alembic File (*.abc)')
        self.curveCacheList.addItems(curvePath[0])

    def attachAbcToXGen(self):
        selectedXgAsset = self.xgenAssetComboBox.currentText()
        namespace = self.namespaceLineEdit.text()
        if namespace in pm.namespaceInfo(lon=True) or namespace == '':
            self.namespaceLineEdit.clear()
            self.namespaceLineEdit.setFocus()
            self.namespaceLineEdit.setPlaceholderText('Please enter unique namespace')
            return
        abcNamespace = namespace+'_abc'
        xgMayaFilePath = self.xgenAssets.get(selectedXgAsset)
        relDirPath = self.relDirLineEdit.text()
        scalpCachePath = self.scalpCacheLineEdit.text()

        if not pm.objExists(namespace+'RN'):
            scalpMeshes = [mesh for mesh in pm.createReference(xgMayaFilePath, namespace=namespace).nodes() if isinstance(mesh, pm.nodetypes.Mesh)]

        setupShot(relDirPath)

        # Handling scalp alembic cache
        if not pm.objExists(abcNamespace+'RN'):
            pm.createReference(scalpCachePath, namespace=abcNamespace)
            for mesh in scalpMeshes:
                pm.blendShape(mesh.swapNamespace(abcNamespace), mesh, origin='world', weight=(0, 1.0))
        else:
            fRef = pm.FileReference(abcNamespace+'RN')
            fRef.replaceWith(scalpCachePath)

        # Handling hair curve alembic caches
        for i in range(self.curveCacheList.count()):
            buffer = tak_b2Pipeline_add.fileNameIntoBuffer(os.path.basename(self.curveCacheList.item(i).text())).split(',')
            tak_b2Pipeline_xgen.setGuideAnimationCache(namespace, buffer[7], str(self.curveCacheList.item(i).text()))