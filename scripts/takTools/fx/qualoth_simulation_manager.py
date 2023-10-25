'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Created: 2019/05/13
Updated: 2019/05/28

Description:
Application for simulating the Qualoth.
'''

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from shiboken2 import wrapInstance
import os
import maya.OpenMayaUI as omui
import pymel.core as pm


def main():
    qualothSimulationManager = QualothSimulationManager()
    qualothSimulationManager.show()


class QualothSimulationManager(QMainWindow):
    iconPath = r'C:\GoogleDrive\programs_env\maya\icons\qualoth_icons'
    projDirPath = ''
    aniStartFrame = 0
    simStartFrame = 0
    solverObjs = []
    qualothObjs = []

    def __init__(self):
        super(QualothSimulationManager, self).__init__()
        self.setWindowTitle('Qualoth Simulation Manager')
        self.setWindowIcon(QIcon(os.path.join(self.iconPath, 'qualoth_icon.png')))
        self.setParent(getMayaMainWin())
        self.setWindowFlags(Qt.Window)
        self.solverObjs = getSolverObjs()
        self.qualothObjs = getQualothObjs(self.solverObjs)
        self.setMaximumSize(500, 400)
        self.buildUI()

    def buildUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout()
        centralWidget.setLayout(mainLayout)

        # Project Directory Path Widgets
        projDirLayout = QHBoxLayout()
        mainLayout.addLayout(projDirLayout)
        projDirLayout.addWidget(QLabel('Project Directory Path: '))
        self.projDirLineEidt = QLineEdit()
        projDirLayout.addWidget(self.projDirLineEidt)
        projDirBtn = QPushButton('...')
        projDirLayout.addWidget(projDirBtn)

        # Start Frame Widgets
        startFrameLayout = QHBoxLayout()
        mainLayout.addLayout(startFrameLayout)
        self.aniStartFrameLineEdit = QLineEdit()
        self.aniStartFrameLineEdit.setPlaceholderText('Animation Start Frame')
        startFrameLayout.addWidget(self.aniStartFrameLineEdit)

        # Qualoth Nodes List Widgets
        qualothNodeLayout = QHBoxLayout()
        mainLayout.addLayout(qualothNodeLayout)

        solverLayout = QVBoxLayout()
        qualothNodeLayout.addLayout(solverLayout)
        solverLayout.addWidget(QLabel('Solvers'))
        self.solverListWidget = QListWidget()
        self.solverListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        solverLayout.addWidget(self.solverListWidget)

        qualothLayout = QVBoxLayout()
        qualothNodeLayout.addLayout(qualothLayout)
        qualothLayout.addWidget(QLabel('Qualothes'))
        self.qualothListWidget = QListWidget()
        self.qualothListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        qualothLayout.addWidget(self.qualothListWidget)

        colliderLayout = QVBoxLayout()
        qualothNodeLayout.addLayout(colliderLayout)
        colliderLayout.addWidget(QLabel('Colliders'))
        self.colliderListWidget = QListWidget()
        self.colliderListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        colliderLayout.addWidget(self.colliderListWidget)

        # Action Buttons Widgets
        toolBar = QToolBar()
        toolBar.setIconSize(QSize(32, 32))
        mainLayout.addWidget(toolBar)
        truncateAction = QAction(QIcon(os.path.join(self.iconPath, 'truncate_cache.png')), 'Truncate Cache', self)
        toolBar.addAction(truncateAction)
        createCacheAction = QAction(QIcon(os.path.join(self.iconPath, 'create_cache.png')), 'Create Cache, Press the ESC key to stop', self)
        toolBar.addAction(createCacheAction)
        toolBar.addSeparator()
        localSimStartAction = QAction(QIcon(os.path.join(self.iconPath, 'local_simulation_start.png')), 'Local Simulation Start', self)
        toolBar.addAction(localSimStartAction)
        localSimStopAction = QAction(QIcon(os.path.join(self.iconPath, 'local_simulation_stop.png')), 'Local Simulation Stop', self)
        toolBar.addAction(localSimStopAction)
        toolBar.addSeparator()

        # Connect Signals to Slots
        projDirBtn.clicked.connect(self.setProject)
        self.aniStartFrameLineEdit.returnPressed.connect(self.setFrameRange)
        self.colliderListWidget.itemClicked.connect(lambda item: pm.select(item.text(), r=True))
        self.colliderListWidget.customContextMenuRequested.connect(self.showColliderListMenu)
        self.solverListWidget.itemClicked.connect(self.solverItemClicked)
        self.solverListWidget.customContextMenuRequested.connect(self.showSolverListMenu)
        self.qualothListWidget.itemClicked.connect(lambda item: pm.select(item.text(), r=True))
        self.qualothListWidget.customContextMenuRequested.connect(self.showQualothListMenu)
        truncateAction.triggered.connect(self.truncateCache)
        createCacheAction.triggered.connect(lambda: pm.mel.eval('playButtonForward;'))
        localSimStartAction.triggered.connect(lambda: pm.mel.eval('qlStartLocalSimulation;'))
        localSimStopAction.triggered.connect(lambda: pm.mel.eval('qlStopLocalSimulation;'))

    def setProject(self):
        startSearchDir = self.projDirLineEidt.text() if self.projDirLineEidt.text() else pm.sceneName().dirname()
        self.projDirPath = QFileDialog.getExistingDirectory(self, 'Select Proejct Directory', startSearchDir)
        self.projDirLineEidt.setText(self.projDirPath)
        self.makeDirs()
        self.setQualothCache()

    def makeDirs(self):
        qualothDirPath = os.path.join(self.projDirPath, 'qualoth')
        if not os.path.exists(qualothDirPath):
            os.mkdir(qualothDirPath)
        for solverObj in self.solverObjs:
            solverDir = os.path.join(qualothDirPath, str(solverObj['node'].replace(':', '_')))
            if not os.path.exists(solverDir):
                os.mkdir(solverDir)
            for qualoth in solverObj['qualothes']:
                cacheDir = os.path.join(os.path.join(solverDir, str(qualoth.replace(':', '_'))))
                if not os.path.exists(cacheDir):
                    os.mkdir(cacheDir)

    def setQualothCache(self):
        for solverObj in self.solverObjs:
            for qualoth in solverObj['qualothes']:
                qualoth.cacheFolder.set(os.path.join(self.projDirPath, 'qualoth', str(solverObj['node'].replace(':', '_')), str(qualoth.replace(':', '_'))))
                qualoth.cacheName.set(str(qualoth.replace(':', '_')))

    def setFrameRange(self):
        self.aniStartFrame = int(self.aniStartFrameLineEdit.text())
        self.simStartFrame = self.aniStartFrame-30
        pm.playbackOptions(minTime=self.simStartFrame)

    def populateSolverListWidget(self):
        while self.solverListWidget.count() > 0:
            self.solverListWidget.takeItem(0)
        self.solverListWidget.addItems([str(solverObj['node']) for solverObj in self.solverObjs])

    def solverItemClicked(self, item):
        pm.select(item.text(), r=True)
        self.populateQualothListWidget(item)
        self.populateColliderListWidget(item)

    def populateQualothListWidget(self, item):
        while self.qualothListWidget.count() > 0:
            self.qualothListWidget.takeItem(0)
        for solverObj in self.solverObjs:
            if solverObj['node'].name() == item.text():
                self.qualothListWidget.addItems([str(qualoth) for qualoth in solverObj['qualothes']])

    def populateColliderListWidget(self, item):
        while self.colliderListWidget.count() > 0:
            self.colliderListWidget.takeItem(0)
        for solverObj in self.solverObjs:
            if solverObj['node'].name() == item.text():
                self.colliderListWidget.addItems([str(collider) for collider in solverObj['colliders']])

    def showColliderListMenu(self, pos):
        ColliderMenu = QMenu(self)
        ColliderMenu.addAction('Paint Collision Map', lambda: pm.mel.eval('qlPaintColliderAttribute collisionMap;'))
        ColliderMenu.exec_(self.colliderListWidget.mapToGlobal(pos))



    def showSolverListMenu(self, pos):
        solverMenu = QMenu(self)
        solverMenu.addAction('Load Solvers', self.populateSolverListWidget)
        solverMenu.addAction('Set Initial State', lambda: self.setInitialState(pm.PyNode(self.solverListWidget.currentItem().text())))
        solverMenu.addAction('Reinitialize Solver', lambda: pm.mel.eval('qlReinitializeSolver;'))
        solverMenu.addAction('Set Local Space Simulation', lambda: self.setLocalSpaceSimulation(pm.PyNode(self.solverListWidget.currentItem().text())))
        solverMenu.exec_(self.solverListWidget.mapToGlobal(pos))

    def setInitialState(self, solver):
        for solverObj in self.solverObjs:
            if solverObj['node'] == solver:
                solverObj['node'].active.set(False)
                self.setPoses()
                pm.currentTime(self.simStartFrame)
                self.setSolver(solverObj['node'])
                for qualoth in solverObj['qualothes']:
                    self.setInitialPose(qualoth)

    def setPoses(self):
        selControls = pm.selected(type=pm.nodetypes.Transform)
        if selControls:
            selectBaseAnimationLayer()
            keyAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
            pm.currentTime(self.aniStartFrame)
            for control in selControls:
                for attr in keyAttrs:
                    pm.setKeyframe(control, attribute=attr)
            pm.currentTime(self.simStartFrame)
            for control in selControls:
                for attr in keyAttrs:
                    pm.setKeyframe(control, attribute=attr, v=0)

    def setSolver(self, solver):
        solver.active.set(True)
        solver.startTime.set(self.simStartFrame)

    def setInitialPose(self, qualoth):
        result = QMessageBox.Ok
        if len(os.listdir(qualoth.cacheFolder.get())) > 1:
            result = showInitialPoseWarning(qualoth)
        if result == QMessageBox.Ok:
            for qualothObj in self.qualothObjs:
                if qualothObj['node'] == qualoth:
                    pm.select(qualothObj['dynMesh'], qualothObj['goalMesh'], r=True)
                    pm.mel.eval('qlUpdateInitialPose;')
                    self.showDynMesh(qualoth)

    def setLocalSpaceSimulation(self, solver):
        sels = pm.selected()
        if len(sels) > 1 or not pm.nodetypes.Transform in [type(item) for item in sels]:
            pm.confirmDialog(title='Error', message='Select a transform node that following character.')
            return
        dynMeshes = self.getDynMeshesFromSolver(solver)
        dynMeshParentTransform = dynMeshes[0].getParent()
        pm.parentConstraint(sels[0], dynMeshParentTransform, mo=True)
        pm.select(dynMeshes, r=True)
        pm.mel.eval('qlSetLocalSpace;')
        solver.referenceTransformAccelerationScale.set(0)
        solver.referenceTransformVelocityScale.set(0)
        solver.referenceTransformAngularAccelerationScale.set(0)
        solver.referenceTransformAngularVelocityScale.set(0)

    def getDynMeshesFromSolver(self, solver):
        dynMeshes = []
        for solverObj in self.solverObjs:
            if solverObj['node'] == solver:
                qualothes = solverObj['qualothes']
                for qualoth in qualothes:
                    for qualothObj in self.qualothObjs:
                        if qualothObj['node'] == qualoth:
                            dynMeshes.append(qualothObj['dynMesh'])
        return dynMeshes

    def truncateCache(self):
        pm.select(pm.PyNode(self.solverListWidget.currentItem().text()), r=True)
        pm.mel.eval('qlTruncateCache;')

    def showQualothListMenu(self, pos):
        qualothMenu = QMenu(self)
        qualothMenu.addAction('Set Initial Pose', lambda: self.setInitialPose(pm.PyNode(self.qualothListWidget.currentItem().text())))
        qualothMenu.addAction('Open Cache Directory', lambda: self.openCacheDirectory(pm.PyNode(self.qualothListWidget.currentItem().text())))
        qualothMenu.addSeparator()
        qualothMenu.addAction('Show In Mesh', lambda: self.showInMesh(pm.PyNode(self.qualothListWidget.currentItem().text())))
        qualothMenu.addAction('Show Dynamic Mesh', lambda: self.showDynMesh(pm.PyNode(self.qualothListWidget.currentItem().text())))
        qualothMenu.addAction('Show Out Mesh', lambda: self.showOutMesh(pm.PyNode(self.qualothListWidget.currentItem().text())))
        qualothMenu.addSeparator()
        qualothMenu.addAction('Paint Self Collision Map', lambda: self.paintSelfCollisionMap(pm.PyNode(self.qualothListWidget.currentItem().text())))
        qualothMenu.addSeparator()
        qualothMenu.addAction('Show Goal Mesh', lambda: self.showGoalMesh(pm.PyNode(self.qualothListWidget.currentItem().text())))
        qualothMenu.addAction('Select Goal Constraint', lambda: self.selectGoalConstraint(pm.PyNode(self.qualothListWidget.currentItem().text())))
        qualothMenu.addAction('Paint Goal Weights', lambda: self.paintGoalStrengthMap(pm.PyNode(self.qualothListWidget.currentItem().text())))
        qualothMenu.addSeparator()
        qualothMenu.addAction('Connect Wind Field')
        qualothMenu.exec_(self.qualothListWidget.mapToGlobal(pos))

    def openCacheDirectory(self, qualoth):
        os.startfile(qualoth.cacheFolder.get())

    def paintSelfCollisionMap(self, qualoth):
        for qualothObj in self.qualothObjs:
            if qualothObj['node'] == qualoth:
                pm.select(qualothObj['dynMesh'], r=True)
                pm.mel.eval('qlPaintClothAttribute selfCollisionMap;')

    def showInMesh(self, qualoth):
        for qualothObj in self.qualothObjs:
            if qualothObj['node'] == qualoth:
                qualothObj['goalMesh'].visibility.set(False)
                qualothObj['inMesh'].visibility.set(True)
                qualothObj['dynMesh'].visibility.set(False)
                qualothObj['outMesh'].visibility.set(False)

    def showDynMesh(self, qualoth):
        for qualothObj in self.qualothObjs:
            if qualothObj['node'] == qualoth:
                qualothObj['goalMesh'].visibility.set(False)
                qualothObj['inMesh'].visibility.set(False)
                qualothObj['dynMesh'].visibility.set(True)
                qualothObj['outMesh'].visibility.set(False)

    def showOutMesh(self, qualoth):
        for qualothObj in self.qualothObjs:
            if qualothObj['node'] == qualoth:
                qualothObj['goalMesh'].visibility.set(False)
                qualothObj['inMesh'].visibility.set(False)
                qualothObj['dynMesh'].visibility.set(False)
                qualothObj['outMesh'].visibility.set(True)

    def showGoalMesh(self, qualoth):
        for qualothObj in self.qualothObjs:
            if qualothObj['node'] == qualoth:
                qualothObj['goalMesh'].visibility.set(True)
                qualothObj['inMesh'].visibility.set(False)
                qualothObj['dynMesh'].visibility.set(False)
                qualothObj['outMesh'].visibility.set(False)

    def selectGoalConstraint(self, qualoth):
        for qualothObj in self.qualothObjs:
            if qualothObj['node'] == qualoth:
                pm.select(qualothObj['goal'], r=True)

    def paintGoalStrengthMap(self, qualoth):
        for qualothObj in self.qualothObjs:
            if qualothObj['node'] == qualoth:
                pm.select(qualothObj['goal'], r=True)
                pm.mel.eval('qlPaintGoalConstraintAttribute strengthMap;')


# Utils
def getMayaMainWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaWinPtr), QWidget)


def getSolverObjs():
    solverObjs = []
    solvers = pm.ls(type='qlSolverShape')
    for solver in solvers:
        qualothes = [qualoth.getShape() for qualoth in solver.clothState.connections(d=False)]
        colliders = [collider.getShape().connections(d=False)[0].connections(d=False)[0] for collider in solver.collider.connections()]
        solverObjs.append({'node': solver, 'qualothes': qualothes, 'colliders': colliders})
    return solverObjs


def getQualothObjs(solverObjs):
    qualothObjs = []
    for solverObj in solverObjs:
        for qualoth in solverObj['qualothes']:
            inputMesh = qualoth.inputGeometry.connections()[0].connections(d=False)[0]
            dynMesh = qualoth.outputMesh.connections()[0]
            outMesh = dynMesh.worldMesh.connections()[0].outputGeometry.connections(s=False)[0]
            goalConstraint = qualoth.lastMesh.connections(s=False)[0]
            goalMesh = goalConstraint.inputGoalMesh.connections()[0]
            qualothObjs.append({'node': qualoth, 'inMesh': inputMesh, 'dynMesh': dynMesh, 'outMesh': outMesh, 'goalMesh': goalMesh, 'goal': goalConstraint})
    return qualothObjs


def selectBaseAnimationLayer():
    animLayers = pm.ls(type='animLayer')
    if animLayers:
        for layer in animLayers:
            if layer.name() != 'BaseAnimation':
                pm.mel.eval('animLayerEditorOnSelect "{}" 0;'.format(str(layer)))
            else:
                pm.mel.eval('animLayerEditorOnSelect "{}" 1;'.format(str(layer)))


def showInitialPoseWarning(qualoth):
    numOfCacheFiles = len(os.listdir(qualoth.cacheFolder.get()))
    warningDialog = QMessageBox()
    warningDialog.setWindowTitle('Warning')
    warningDialog.setIcon(QMessageBox.Warning)
    warningDialog.setText("'{}' has {} caches.\nCaches will be deleted!\nAre you sure?".format(qualoth.name(), numOfCacheFiles))
    warningDialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    result = warningDialog.exec_()
    return result
