import imp
from PySide2 import QtWidgets
from PySide2 import QtCore

import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

from . import advancedSkeletonHelper as ash; imp.reload(ash)


def getMayaMainWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mayaWinPtr), QtWidgets.QWidget)


class AdvancedSkeletonHelperUI(QtWidgets.QDialog):
    MAYA_WIN = getMayaMainWin()

    def __init__(self, parent=MAYA_WIN):
        super(AdvancedSkeletonHelperUI, self).__init__(parent)

        self.__ashObj = ash.AdvancedSkeletonHelper()

        self.setWindowTitle('Advanced Skeleton Helper')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    def createWidgets(self):
        self.matchFitBtn = QtWidgets.QPushButton('Match Fit to the Skeleton')
        self.alignAnkleBtn = QtWidgets.QPushButton('Align Ankle Orientation to world')
        self.createSkinLocBtn = QtWidgets.QPushButton('Create Model Pose Locators')
        self.createBuildLocBtn = QtWidgets.QPushButton('Create Rig Pose Locators')
        self.goModelPoseFitBtn = QtWidgets.QPushButton('Go Fit to Model Pose')
        self.goRigPoseFitBtn = QtWidgets.QPushButton('Go Fit to Rig Pose')
        self.matchCtrlToModelPoseBtn = QtWidgets.QPushButton('Match Controls To Model Pose')
        self.matchToRigPoseCtrlBtn = QtWidgets.QPushButton('Match Controls to Rig Pose')
        self.createZeroGrpBtn = QtWidgets.QPushButton('Create Zero Group')
        self.removeZeroGrpBtn = QtWidgets.QPushButton('Remove Zero Group')
        self.createHikCharDefBtn = QtWidgets.QPushButton('Create HumanIK Character Definition')
        self.createHikCustomRigDefBtn = QtWidgets.QPushButton('Create HumanIK Custom Rig Definition')
        self.createHikNodeSetBtn = QtWidgets.QPushButton('Create HumanIK Node Set')
        self.cleanupOutlinerBtn = QtWidgets.QPushButton('Clean Up Outliner')
        self.setupBaseBtn = QtWidgets.QPushButton('Setup Global')
        self.createIKJntsBtn = QtWidgets.QPushButton('Create Unreal IK Joints')
        self.removeFromAsSystemBtn = QtWidgets.QPushButton('Remove Selections from AS System')
        self.connectSetsBtn = QtWidgets.QPushButton('Connects sets to "Group"')

    def createLayouts(self):
        mainLo = QtWidgets.QVBoxLayout(self)
        mainLo.setMargin(0)
        mainLo.setSpacing(0)

        mainLo.addWidget(self.matchFitBtn)
        # mainLo.addWidget(self.alignAnkleBtn)
        # mainLo.addWidget(self.createSkinLocBtn)
        # mainLo.addWidget(self.createBuildLocBtn)
        # mainLo.addWidget(self.goModelPoseFitBtn)
        # mainLo.addWidget(self.goRigPoseFitBtn)
        # mainLo.addWidget(self.matchCtrlToModelPoseBtn)
        # mainLo.addWidget(self.matchToRigPoseCtrlBtn)
        # mainLo.addWidget(self.createZeroGrpBtn)
        # mainLo.addWidget(self.removeZeroGrpBtn)
        # mainLo.addWidget(self.createHikCharDefBtn)
        # mainLo.addWidget(self.createHikCustomRigDefBtn)
        # mainLo.addWidget(self.createHikNodeSetBtn)
        # mainLo.addWidget(self.cleanupOutlinerBtn)
        mainLo.addWidget(self.setupBaseBtn)
        mainLo.addWidget(self.createIKJntsBtn)
        # mainLo.addWidget(self.removeFromAsSystemBtn)
        mainLo.addWidget(self.connectSetsBtn)

    def createConnections(self):
        self.matchFitBtn.clicked.connect(self.__ashObj.matchFitSkeleton)
        self.alignAnkleBtn.clicked.connect(self.__ashObj.alignAnkleOriToWorld)
        self.createSkinLocBtn.clicked.connect(self.__ashObj.createModelPoseLocs)
        self.createBuildLocBtn.clicked.connect(self.__ashObj.createRigPoseLocs)
        self.goModelPoseFitBtn.clicked.connect(self.__ashObj.goToModelPoseFit)
        self.goRigPoseFitBtn.clicked.connect(self.__ashObj.goToRigPoseFit)
        self.createZeroGrpBtn.clicked.connect(self.__ashObj.createZeroGroup)
        self.removeZeroGrpBtn.clicked.connect(self.__ashObj.removeZeroGroup)
        self.matchCtrlToModelPoseBtn.clicked.connect(self.__ashObj.matchControlToModelPose)
        self.matchToRigPoseCtrlBtn.clicked.connect(self.__ashObj.matchControlToRigPose)
        self.setupBaseBtn.clicked.connect(self.__ashObj.setupBase)
        self.createHikCharDefBtn.clicked.connect(self.createHikCharDef)
        self.createHikCustomRigDefBtn.clicked.connect(self.createHikCustomRigDef)
        self.createHikNodeSetBtn.clicked.connect(self.__ashObj.createHikNodeSet)
        self.cleanupOutlinerBtn.clicked.connect(self.__ashObj.cleanupOutliner)
        self.createIKJntsBtn.clicked.connect(self.__ashObj.createIKJoints)
        self.removeFromAsSystemBtn.clicked.connect(self.__ashObj.removeSelsFromAsSystem)
        self.connectSetsBtn.clicked.connect(self.__ashObj.connectSetToGroup)

    def createHikCharDef(self):
        charName, ok = QtWidgets.QInputDialog.getText(self, 'HumanIK Character Definition', 'Character Name:')
        if ok and charName:
            ash.AdvancedSkeletonHelper.createHikCharDef(charName)

    def createHikCustomRigDef(self):
        charName, ok = QtWidgets.QInputDialog.getText(self, 'HumanIK Custom Rig Definition', 'Character Name:')
        if ok and charName:
            ash.AdvancedSkeletonHelper.createHikCustomRig(charName)
