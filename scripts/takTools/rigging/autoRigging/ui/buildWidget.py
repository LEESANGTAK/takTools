from PySide2 import QtCore, QtGui, QtWidgets

import pymel.core as pm
import maya.cmds as cmds

from ..base import general
from ..base import module

from ..utils import joint as jntUtil

from .forms import baseForm
from .forms import limbForm
from .forms import simpleFKForm
from .forms import vertebraForm
from .forms import splineForm
from .forms import singleJointsForm

from ..module import base
from ..module import limb
from ..module import simpleFK
from ..module import vertebra
from ..module import spline
from ..module import singleJoints


class BuildWidget(QtWidgets.QWidget):
    def __init__(self):
        super(BuildWidget, self).__init__()

        self.module_form_info = {
            'base': baseForm.BaseForm(),
            'limb': limbForm.LimbForm(),
            'simpleFK': simpleFKForm.SimpleFKForm(),
            'vertebra': vertebraForm.VertebraForm(),
            'spline': splineForm.SplineForm(),
            'singleJoints': singleJointsForm.SingleJointsForm(),
        }

        self.createWidgets()
        self.populateWidgets()
        self.createLayouts()
        self.createConnections()

    def createWidgets(self):
        self.modulesWidget = QtWidgets.QListWidget()
        self.moduleAttrWidget = QtWidgets.QStackedWidget()
        self.buildBtn = QtWidgets.QPushButton('Build Module')

    def populateWidgets(self):
        for moduleName, form in self.module_form_info.items():
            self.modulesWidget.addItem(moduleName)
            self.moduleAttrWidget.addWidget(form)

    def createLayouts(self):
        moduleLayout = QtWidgets.QHBoxLayout()
        moduleLayout.addWidget(self.modulesWidget)
        moduleLayout.addWidget(self.moduleAttrWidget)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addLayout(moduleLayout)
        mainLayout.addWidget(self.buildBtn)

    def createConnections(self):
        self.modulesWidget.currentTextChanged.connect(self.showModlueAttributes)
        self.buildBtn.clicked.connect(self.buildModule)

    def showModlueAttributes(self, moduleName):
        moduleFormWidget = self.module_form_info.get(moduleName)
        self.moduleAttrWidget.setCurrentWidget(moduleFormWidget)

    def buildModule(self):
        selModule = self.modulesWidget.currentItem().text()
        selModuleForm = self.module_form_info.get(selModule)

        if selModule == 'base':
            BuildWidget.buildBase(selModuleForm)
        elif selModule == 'limb':
            BuildWidget.buildLimb(selModuleForm)
        elif selModule == 'simpleFK':
            BuildWidget.buildSimpleFK(selModuleForm)
        elif selModule == 'vertebra':
            BuildWidget.buildVertebra(selModuleForm)
        elif selModule == 'spline':
            BuildWidget.buildSpline(selModuleForm)
        elif selModule == 'singleJoints':
            BuildWidget.buildSingleJoints(selModuleForm)

    @staticmethod
    def buildBase(moduleForm):
        model = moduleForm.modelLe.text()
        skeleton = moduleForm.skeletonLe.text()
        zAxisUp = moduleForm.zAxisUpChk.checkState()
        rootCtrl = moduleForm.rootCtrlChk.checkState()
        ctrlShape = moduleForm.ctrlShapeCb.currentText()

        skeleton = skeleton.split(',') if skeleton else None

        pm.undoInfo(openChunk=True)
        base.build(model, skeleton, zAxisUp, ctrlShape, rootCtrl)
        pm.undoInfo(closeChunk=True)

    @staticmethod
    def buildLimb(moduleForm):
        name = moduleForm.nameLe.text()
        limbJnts = moduleForm.limbJntsLe.text()
        fkChk = moduleForm.fkChk.isChecked()
        ikChk = moduleForm.ikChk.isChecked()
        fkIkSwitchChk = moduleForm.fkIkSwitchChk.isChecked()
        twistChk = moduleForm.twistChk.isChecked()
        upTwistJoints = moduleForm.upTwistJntsLe.text()
        lowTwistJoints = moduleForm.lowTwistJntsLe.text()
        aimAxisSign = moduleForm.aimAxisSignCb.currentText()
        parentGrp = moduleForm.parentGrpLe.text()

        pm.undoInfo(openChunk=True)

        moduleObj = module.Module(name)

        limbSkeletonJoints = limbJnts.split(',')
        outJoints = limb.createDrivingJoints(limbSkeletonJoints, '_outJnt')
        pm.parent(outJoints[0], moduleObj.outGrp)

        if fkChk:
            fkJoints, fkCtrlGrp, fkRigGrp = limb.buildFK(name, outJoints)
            pm.parent(fkRigGrp, moduleObj.systemGrp)

        if ikChk:
            ikJoints, ikCtrlGrp, ikRigGrp = limb.buildIK(name, outJoints)
            pm.parent(ikRigGrp, moduleObj.systemGrp)

        if fkIkSwitchChk:
            switchCtrl, choiceNodes = limb.setupSwitch(name, fkJoints, ikJoints, outJoints)
            # Fk/Ik visibility
            fkIkVisReverseNode = pm.createNode('reverse', n=name + '_fkIkRigVis_reverse')
            switchCtrl.transform.fkIk >> fkIkVisReverseNode.inputX
            fkIkVisReverseNode.outputX >> fkRigGrp.visibility
            switchCtrl.transform.fkIk >> ikRigGrp.visibility

            pm.parent(switchCtrl.spaceGrp, moduleObj.ctrlGrp)

        if twistChk:
            upTwistJoints = upTwistJoints.split(',')
            lowTwistJoints = lowTwistJoints.split(',')
            aimAxisSign = 1 if aimAxisSign == '+' else -1
            twistRigGrp, clstCtrlGrp = limb.setupTwist(name, outJoints, limbSkeletonJoints, upTwistJoints, lowTwistJoints, aimAxisSign)

            # Bend controller visibility
            pm.addAttr(switchCtrl.transform, at='bool', ln='bendCtrlVis', keyable=True)
            switchCtrl.transform.bendCtrlVis >> clstCtrlGrp.visibility

            pm.parent(twistRigGrp, moduleObj.topGrp)

        if parentGrp:
            pm.parent(moduleObj.topGrp, parentGrp)

        moduleObj.outGrp.hide()
        pm.undoInfo(closeChunk=True)

    @staticmethod
    def buildSimpleFK(moduleForm):
        name = moduleForm.nameLe.text()
        joints = moduleForm.jointsLe.text().split(',')
        attachTo = moduleForm.attachToLe.text()
        parentGrp = moduleForm.parentGrpLe.text()

        pm.undoInfo(openChunk=True)
        simpleFK.build(name, joints, attachTo, parentGrp)
        pm.undoInfo(closeChunk=True)

    @staticmethod
    def buildSingleJoints(moduleForm):
        name = moduleForm.nameLe.text()
        joints = moduleForm.jointsLe.text()
        attachTo = moduleForm.attachToLe.text()
        parentGrp = moduleForm.parentGrpLe.text()

        pm.undoInfo(openChunk=True)
        singleJoints.build(name, joints, attachTo, parentGrp)
        pm.undoInfo(closeChunk=True)

    @staticmethod
    def buildVertebra(moduleForm):
        name = moduleForm.nameLe.text()
        joints = moduleForm.jointsLe.text().split(',')
        parentGrp = moduleForm.parentGrpLe.text()

        pm.undoInfo(openChunk=True)
        vertebraObj = vertebra.Vertebra(name, joints, parentGroup=parentGrp)
        vertebraObj.build()
        pm.undoInfo(closeChunk=True)

    @staticmethod
    def buildSpline(moduleForm):
        name = moduleForm.nameLe.text()
        joints = moduleForm.jointsLe.text().split(',')
        numCtrls = moduleForm.numCtrlLe.text()
        stretchOpt = moduleForm.stretchChkBox.checkState()
        twistOpt = moduleForm.twistChkBox.checkState()
        rollOpt = moduleForm.rollChkBox.checkState()
        thickOpt = moduleForm.thickChkBox.checkState()
        slideOpt = moduleForm.slideChkBox.checkState()
        fkOpt = moduleForm.fkChkBox.checkState()
        waveOpt = moduleForm.waveChkBox.checkState()
        dynamicOpt = moduleForm.dynamicChkBox.checkState()
        globalOpt = moduleForm.globalChkBox.checkState()
        parentGrp = moduleForm.parentGrpLe.text()

        pm.undoInfo(openChunk=True)
        spline.build(
            name,
            joints,
            int(numCtrls),
            stretchOpt,
            twistOpt,
            rollOpt,
            thickOpt,
            slideOpt,
            fkOpt,
            waveOpt,
            dynamicOpt,
            globalOpt,
            parentGrp
        )
        pm.undoInfo(closeChunk=True)
