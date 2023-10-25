import maya.cmds as cmds
import pymel.core as pm

from PySide2 import QtCore, QtGui, QtWidgets

from ..base import general
from ..utils import skeleton


class SkeletonWidget(QtWidgets.QWidget):
    instance = None

    def __init__(self):
        super(SkeletonWidget, self).__init__()

        self.crv = None
        self.crvJnts = None

        self.segStartJnt = None
        self.segEndJnt = None
        self.segJnts = None

        self.uiGeo = None

        self.createWidgets()
        self.createLayouts()
        self.createConnections()
        self.setDefault()

    def createWidgets(self):
        self.createJntBtn = QtWidgets.QPushButton('Create Joints on Selection')
        self.jntOnCenterBtn = QtWidgets.QPushButton('Joint on Center')
        self.jntOnManipBtn = QtWidgets.QPushButton('Joint on Manipulator')

        self.jntsFromObjBtn = QtWidgets.QPushButton('FK Chain from Selection')

        self.upTypeLe = QtWidgets.QLabel('Up Type: ')
        self.upTypeCb = QtWidgets.QComboBox()
        self.upTypeCb.addItems(['Vector', 'Object'])
        self.crvUpObjLe = LoadSelLineEditGrp('Up Object: ')
        self.upVectorXLe = QtWidgets.QLineEdit(str(0.0))
        self.upVectorYLe = QtWidgets.QLineEdit(str(0.0))
        self.upVectorZLe = QtWidgets.QLineEdit(str(1.0))
        self.crvChainChkBox = QtWidgets.QCheckBox('Chain')
        self.crvLocalAxisChkBox = QtWidgets.QCheckBox('Local Axis')
        self.crvNumJointsSlider = IntSliderGrp('Number of Joints: ', min=2, max=60)

        self.segChainChkBox = QtWidgets.QCheckBox('Chain')
        self.numSegSlider = IntSliderGrp('Number of Segments: ', min=1)

        self.jntSizeSlider = FloatSliderGrp('Joint Size: ')
        self.resetOrientBtn = QtWidgets.QPushButton('Reset Joints Orient')

        self.srcSkelSearchLabel = QtWidgets.QLabel('Source Skeleton Search: ')
        self.srcSkelSearchLE = QtWidgets.QLineEdit('_LF')
        self.oppSkelReplaceLabel = QtWidgets.QLabel('Opposite Skeleton Replace: ')
        self.oppSkelReplaceLE = QtWidgets.QLineEdit('_RT')
        self.mirrorSkelBtn = QtWidgets.QPushButton('Mirror Skeleton Selection')

        self.maintainOffsetChkBox = QtWidgets.QCheckBox('Maintain Offset')
        self.driverSkelLabel = QtWidgets.QLabel('Driver Skeleton Root: ')
        self.driverSkelLE = QtWidgets.QLineEdit()
        self.drivenSkelLabel = QtWidgets.QLabel('Driven Skeleton Root: ')
        self.drivenSkelLE = QtWidgets.QLineEdit()
        self.excludeJointsLabel = QtWidgets.QLabel('Exclude Joints: ')
        self.excludeJointsLE = QtWidgets.QLineEdit(placeholderText='joint1, joint2, ...')
        self.connectSkelBtn = QtWidgets.QPushButton('Connect Skeleton')

        self.constSkelLabel = QtWidgets.QLabel('Skeleton Root: ')
        self.constSkelLE = QtWidgets.QLineEdit()
        self.disconSkelBtn = QtWidgets.QPushButton('Disconnect')
        self.reconSkelBtn = QtWidgets.QPushButton('Reconnect')

        self.poseList = QtWidgets.QListWidget()
        self.savePoseBtn = QtWidgets.QPushButton('Save Pose')
        self.removePoseBtn = QtWidgets.QPushButton('Remove Pose')

    def createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)

        mainLayout.addWidget(self.createJntBtn)
        mainLayout.addWidget(self.jntOnCenterBtn)
        mainLayout.addWidget(self.jntOnManipBtn)
        mainLayout.addWidget(self.jntsFromObjBtn)

        mainLayout.addWidget(Separator())

        crvUpTypeLo = QtWidgets.QHBoxLayout()
        crvUpTypeLo.addWidget(self.upTypeLe)
        crvUpTypeLo.addWidget(self.upTypeCb)
        mainLayout.addLayout(crvUpTypeLo)

        crvUpVectorLo = QtWidgets.QHBoxLayout()
        crvUpVectorLo.addWidget(self.upVectorXLe)
        crvUpVectorLo.addWidget(self.upVectorYLe)
        crvUpVectorLo.addWidget(self.upVectorZLe)
        mainLayout.addLayout(crvUpVectorLo)

        mainLayout.addWidget(self.crvUpObjLe)

        crvChkBoxLayout = QtWidgets.QHBoxLayout()
        crvChkBoxLayout.addWidget(self.crvChainChkBox)
        crvChkBoxLayout.addWidget(self.crvLocalAxisChkBox)
        mainLayout.addLayout(crvChkBoxLayout)

        mainLayout.addWidget(self.crvNumJointsSlider)

        mainLayout.addWidget(Separator())

        mainLayout.addWidget(self.segChainChkBox)
        mainLayout.addWidget(self.numSegSlider)

        mainLayout.addWidget(Separator())

        mainLayout.addWidget(self.jntSizeSlider)
        mainLayout.addWidget(self.resetOrientBtn)

        mainLayout.addWidget(Separator())

        mirrorSkelLayout = QtWidgets.QHBoxLayout()
        mirrorSkelLayout.addWidget(self.srcSkelSearchLabel)
        mirrorSkelLayout.addWidget(self.srcSkelSearchLE)
        mirrorSkelLayout.addWidget(self.oppSkelReplaceLabel)
        mirrorSkelLayout.addWidget(self.oppSkelReplaceLE)
        mainLayout.addLayout(mirrorSkelLayout)
        mainLayout.addWidget(self.mirrorSkelBtn)

        mainLayout.addWidget(Separator())

        connectSkelLayout = QtWidgets.QVBoxLayout()
        driverDrivenLayout = QtWidgets.QHBoxLayout()
        connectSkelLayout.addWidget(self.maintainOffsetChkBox)
        driverDrivenLayout.addWidget(self.driverSkelLabel)
        driverDrivenLayout.addWidget(self.driverSkelLE)
        driverDrivenLayout.addWidget(self.drivenSkelLabel)
        driverDrivenLayout.addWidget(self.drivenSkelLE)
        excludeJointsLayout = QtWidgets.QHBoxLayout()
        excludeJointsLayout.addWidget(self.excludeJointsLabel)
        excludeJointsLayout.addWidget(self.excludeJointsLE)
        connectSkelLayout.addLayout(driverDrivenLayout)
        connectSkelLayout.addLayout(excludeJointsLayout)
        mainLayout.addLayout(connectSkelLayout)
        mainLayout.addWidget(self.connectSkelBtn)

        mainLayout.addWidget(Separator())

        constSkelLayout = QtWidgets.QHBoxLayout()
        constSkelLayout.addWidget(self.constSkelLabel)
        constSkelLayout.addWidget(self.constSkelLE)
        constSkelLayout.addWidget(self.disconSkelBtn)
        constSkelLayout.addWidget(self.reconSkelBtn)
        mainLayout.addLayout(constSkelLayout)

        mainLayout.addWidget(Separator())

        poseMainLayout = QtWidgets.QHBoxLayout()
        poseMainLayout.addWidget(self.poseList)
        poseBtnsLayout = QtWidgets.QVBoxLayout()
        poseBtnsLayout.addWidget(self.savePoseBtn)
        poseBtnsLayout.addWidget(self.removePoseBtn)
        poseMainLayout.addLayout(poseBtnsLayout)
        mainLayout.addLayout(poseMainLayout)

    def createConnections(self):
        self.createJntBtn.clicked.connect(skeleton.createJointsOnSelection)
        self.jntOnCenterBtn.clicked.connect(self.jointOnCenter)
        self.jntOnManipBtn.clicked.connect(self.jointOnManipulator)

        self.jntsFromObjBtn.clicked.connect(self.createFKChainFromSelection)
        self.resetOrientBtn.clicked.connect(self.resetChildJointsOrient)

        self.upTypeCb.currentTextChanged.connect(self.displayUpTypeSubWidgets)
        self.crvNumJointsSlider.intSlider.valueChanged.connect(self.createJointsFromCurve)
        self.crvLocalAxisChkBox.stateChanged.connect(self.showHideLocalAxis)

        self.numSegSlider.intSlider.valueChanged.connect(self.createSegJoints)

        self.jntSizeSlider.floatSlider.valueChanged.connect(self.setJointDisplayScale)
        self.mirrorSkelBtn.clicked.connect(self.mirrorSkeleton)
        self.excludeJointsLE.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.excludeJointsLE.customContextMenuRequested.connect(self.showExcludeJointsLEContextMenu)
        self.connectSkelBtn.clicked.connect(self.connectSkeleton)

        self.disconSkelBtn.clicked.connect(self.disconSkeleton)
        self.reconSkelBtn.clicked.connect(self.reconSkeleton)

        self.poseList.itemClicked.connect(self.__restorePose)
        self.poseList.itemDoubleClicked.connect(self.__renamePose)
        self.savePoseBtn.clicked.connect(self.__savePose)
        self.removePoseBtn.clicked.connect(self.__removePose)

    def setDefault(self):
        self.jntOnCenterBtn.setIcon(QtGui.QIcon(':CenterPivot.png'))
        self.jntOnManipBtn.setIcon(QtGui.QIcon(':channelBoxUseManips.png'))
        self.jntsFromObjBtn.setIcon(QtGui.QIcon(':kinJoint.png'))
        self.resetOrientBtn.setIcon(QtGui.QIcon(':menuIconReset.png'))
        self.crvUpObjLe.hide()
        self.crvChainChkBox.setChecked(True)
        self.segChainChkBox.setChecked(True)
        self.crvLocalAxisChkBox.setChecked(True)
        self.maintainOffsetChkBox.setChecked(True)
        self.setCurrentJointDisplaySacle()
        self.__populatePoseList()

    def setJointDisplayScale(self, val):
        displayVal = val / self.jntSizeSlider.factor
        cmds.jointDisplayScale(displayVal)
        self.jntSizeSlider.floatLe.setText(str(displayVal))

    def mirrorSkeleton(self):
        searchStr = self.srcSkelSearchLE.text()
        replaceStr = self.oppSkelReplaceLE.text()
        sels = cmds.ls(sl=True)
        if sels:
            skeleton.mirrorSkeleton(sels[0], searchStr, replaceStr)

    def showExcludeJointsLEContextMenu(self, pos):
        menu = QtWidgets.QMenu(self.excludeJointsLE)
        menu.addAction('Aad Selection', self.addSelection)
        menu.exec_(self.excludeJointsLE.mapToGlobal(pos))

    def addSelection(self):
        selsStr = ''
        concatenateStr = ', '

        sels = cmds.ls(sl=True)
        oldList = self.excludeJointsLE.text()
        if oldList:
            sels = list(set(oldList.split(', ') + sels))

        for sel in sels:
            if sels.index(sel) == len(sels)-1:
                concatenateStr = ''
            selsStr += (sel + concatenateStr)

        self.excludeJointsLE.setText(selsStr)

    def connectSkeleton(self):
        driverRoot = self.driverSkelLE.text()
        drivenRoot = self.drivenSkelLE.text()
        excludeJoints = self.excludeJointsLE.text().split(', ')
        maintainOffset = self.maintainOffsetChkBox.isChecked()
        skeleton.connectSkeletonToOther(driverRoot, drivenRoot, excludeJoints, maintainOffset)

    def disconSkeleton(self):
        skelRoot = self.constSkelLE.text()
        self.__connectInfo = {}
        skeleton.disconnect(skelRoot, self.__connectInfo)

    def reconSkeleton(self):
        skelRoot = self.constSkelLE.text()
        skeleton.reconnect(skelRoot, self.__connectInfo)

    def setCurrentJointDisplaySacle(self):
        curJntDisScale = cmds.jointDisplayScale(q=True)
        self.jntSizeSlider.floatSlider.setValue(curJntDisScale*self.jntSizeSlider.factor)

    def jointOnCenter(self):
        cmds.undoInfo(openChunk=True)
        skeleton.jointOnCenter()
        cmds.undoInfo(closeChunk=True)

    def jointOnManipulator(self):
        cmds.undoInfo(openChunk=True)
        skeleton.jointOnManipulator()
        cmds.undoInfo(closeChunk=True)

    def createFKChainFromSelection(self):
        cmds.undoInfo(openChunk=True)

        objs = cmds.ls(os=True, fl=True)
        skeleton.fkChainFromSelection(objs)

        cmds.undoInfo(closeChunk=True)

    def resetChildJointsOrient(self):
        cmds.undoInfo(openChunk=True)
        joints = cmds.ls(sl=True, type='joint')
        for jnt in joints:
            skeleton.resetJointsOrient(jnt)
        cmds.undoInfo(closeChunk=True)

    def showHideLocalAxis(self, state):
        if self.crvJnts:
            skeleton.showHideLocalAxis(self.crvJnts, state)

    def displayUpTypeSubWidgets(self, text):
        if text == 'Vector':
            self.upVectorXLe.show()
            self.upVectorYLe.show()
            self.upVectorZLe.show()
            self.crvUpObjLe.hide()
        elif text == 'Object':
            self.crvUpObjLe.show()
            self.upVectorXLe.hide()
            self.upVectorYLe.hide()
            self.upVectorZLe.hide()

    def createJointsFromCurve(self, val):
        sels = cmds.ls(sl=True)
        upType = self.upTypeCb.currentText()
        upVectorX = self.upVectorXLe.text()
        upVectorY = self.upVectorYLe.text()
        upVectorZ = self.upVectorZLe.text()
        upVector = [float(upVectorX), float(upVectorY), float(upVectorZ)]
        upObj = self.crvUpObjLe.lineEdit.text()
        chain = self.crvChainChkBox.checkState()
        localAxis = self.crvLocalAxisChkBox.checkState()

        if not sels: return
        currentCrv = sels[0]
        if not self.crv: self.crv = currentCrv

        if self.crv != currentCrv:
            self.crv = currentCrv
            self.crvJnts = None

        cmds.undoInfo(openChunk=True)

        if self.crvJnts:
            cmds.delete(self.crvJnts)

        self.crvJnts = skeleton.jointsFromCurve(self.crv, val, upType, upVector, upObj, chain, localAxis)
        cmds.select(self.crv, r=True)

        cmds.undoInfo(closeChunk=True)

    def createSegJoints(self, val):
        chain = self.segChainChkBox.checkState()

        sels = cmds.ls(sl=True, type='joint')
        if not sels:
            return
        startJnt = sels[0]

        if not self.segStartJnt:
            self.segStartJnt = startJnt
            self.segEndJnt = cmds.listRelatives(startJnt, type='joint')

        # If selected joint changed refresh data
        elif self.segStartJnt and startJnt != self.segStartJnt:
            self.segStartJnt = startJnt
            self.segEndJnt = cmds.listRelatives(startJnt, type='joint')
            self.segJnts = None

        cmds.undoInfo(openChunk=True)

        if skeleton.getParent(self.segEndJnt):
            cmds.parent(self.segEndJnt, world=True)

        if self.segJnts:
            try:
                cmds.delete(self.segJnts)
            except:
                pass

        self.segJnts = skeleton.addJointSegments(self.segStartJnt, self.segEndJnt, val, chain)

        cmds.undoInfo(closeChunk=True)

    def __populatePoseList(self):
        self.poseList.clear()

        dagPoses = cmds.ls(type='dagPose')
        for dagPose in dagPoses:
            poseListItem = QtWidgets.QListWidgetItem(dagPose)
            self.poseList.addItem(poseListItem)

    def __savePose(self):
        # Get root joint of skeleton
        sels = cmds.ls(sl=True, type='joint')
        if not sels or len(sels) > 1 or cmds.nodeType(sels[0]) != 'joint' or cmds.listRelatives(p=True, type='joint'):
            cmds.confirmDialog(title='Warning', message='Select a joint of skeleton root.')
            return
        else:
            rootJnt = sels[0]

        # Save dag pose
        result = cmds.promptDialog(
            title='Save Pose',
            message='Enter Pose Name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if result == 'OK':
            poseName = cmds.promptDialog(query=True, text=True)
            if cmds.objExists(poseName):
                cmds.delete(poseName)
            cmds.select(rootJnt, hi=True, r=True)
            cmds.dagPose(save=True, selection=True, name=poseName)

            self.__populatePoseList()

    def __restorePose(self):
        selPose = self.poseList.selectedItems()
        if selPose:
            cmds.dagPose(selPose[0].text(), restore=True)

    def __removePose(self):
        selPose = self.poseList.selectedItems()
        if selPose:
            cmds.delete(selPose[0].text())
            self.__populatePoseList()

    def __renamePose(self):
        selPose = self.poseList.selectedItems()[0]
        result = cmds.promptDialog(
            title='Rename Pose',
            message='Enter New Name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if result == 'OK':
            newPoseName = cmds.promptDialog(query=True, text=True)
            cmds.rename(selPose.text(), newPoseName)
            self.__populatePoseList()


class LoadSelsLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(LoadSelsLineEdit, self).__init__(parent)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showLineEditPopupMenu)

    def showLineEditPopupMenu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.addAction('Load Selections', self.setSelection)
        menu.exec_(self.mapToGlobal(pos))

    def setSelection(self):
        selsStr = ''
        concatenateStr = ','
        sels = cmds.ls(sl=True)

        for sel in sels:
            if sels.index(sel) == len(sels)-1:
                concatenateStr = ''
            selsStr += (sel + concatenateStr)

        self.setText(selsStr)


class LoadSelLineEditGrp(QtWidgets.QWidget):
    def __init__(self, label=''):
        super(LoadSelLineEditGrp, self).__init__()

        # Create widgets
        self.label = QtWidgets.QLabel(label)
        self.lineEdit = LoadSelsLineEdit()

        # Create Layouts
        mainLayout = QtWidgets.QHBoxLayout(self)
        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.lineEdit)


class IntSliderGrp(QtWidgets.QWidget):
    def __init__(self, label='', min=2, max=50):
        super(IntSliderGrp, self).__init__()

        # Create widgets
        self.label = QtWidgets.QLabel(label)
        self.intLe = QtWidgets.QLineEdit()
        self.intLe.setFixedWidth(50)
        self.intLe.setText(str(min))
        self.intSlider = QtWidgets.QSlider()
        self.intSlider.setFixedWidth(200)
        self.intSlider.setOrientation(QtCore.Qt.Horizontal)
        self.intSlider.setMinimum(min)
        self.intSlider.setMaximum(max)

        # Create Layouts
        mainLayout = QtWidgets.QHBoxLayout(self)
        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.intLe)
        mainLayout.addWidget(self.intSlider)

        # Creaet Connections
        self.intLe.editingFinished.connect(self.updateSlider)
        self.intSlider.valueChanged.connect(lambda val: self.intLe.setText(str(val)))

    def updateSlider(self):
        val = self.intLe.text()
        self.intSlider.setValue(int(val))


class FloatSliderGrp(QtWidgets.QWidget):
    def __init__(self, label='', min=0.01, max=20.0, decimalPoint=2):
        super(FloatSliderGrp, self).__init__()

        self.factor = 10.0 ** decimalPoint
        self.min = min * self.factor
        self.max = max * self.factor

        # Create widgets
        self.label = QtWidgets.QLabel(label)
        self.floatLe = QtWidgets.QLineEdit()
        self.floatLe.setFixedWidth(50)
        self.floatLe.setText(str(1.0))
        self.floatSlider = QtWidgets.QSlider()
        self.floatSlider.setFixedWidth(200)
        self.floatSlider.setOrientation(QtCore.Qt.Horizontal)
        self.floatSlider.setMinimum(self.min)
        self.floatSlider.setMaximum(self.max)

        # Create Layouts
        mainLayout = QtWidgets.QHBoxLayout(self)
        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.floatLe)
        mainLayout.addWidget(self.floatSlider)

        # Creaet Connections
        self.floatLe.editingFinished.connect(self.updateSlider)

    def updateSlider(self):
        val = float(self.floatLe.text()) * self.factor
        self.floatSlider.setValue(float(val))


class Separator(QtWidgets.QFrame):
    def __init__(self):
        super(Separator, self).__init__()

        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
