"""
Author: LEE SANGTAK
Contact: chst27@gmail.com
"""


import re
import Qt

if Qt.__binding__ == "PySide":
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance
elif Qt.__binding__ == "PySide2":
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import pymel.core as pm
import maya.cmds as cmds

from OBB.api import OBB

from takRiggingToolkit.base import control
from ..common import tak_misc


def getMayaMainWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaWinPtr), QWidget)


class SourceType(object):
    mesh = 0
    joint = 1


class SimplePropAutoRigger(QDialog):
    def __init__(self, parent=getMayaMainWin()):  # initialize interface
        super(SimplePropAutoRigger, self).__init__(parent)
        self.setWindowTitle("Simple Prop Auto Rigger")
        self.setWindowFlags(Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose)
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        # Search/Replace Widgets
        self.searchReplaceWidget = QWidget()
        searchReplaceLayout = QGridLayout(self.searchReplaceWidget)
        searchReplaceLayout.addWidget(QLabel("Search: "), 0, 0)
        self.searchLineEdit = QLineEdit("_bnd_jnt")
        searchReplaceLayout.addWidget(self.searchLineEdit, 0, 1)
        searchReplaceLayout.addWidget(QLabel("Replace: "), 1, 0)
        self.replaceLineEdit = QLineEdit("_ctrl")
        searchReplaceLayout.addWidget(self.replaceLineEdit, 1, 1)
        mainLayout.addWidget(self.searchReplaceWidget)
        self.searchReplaceWidget.hide()

        # source type
        srcTypeLayout = QHBoxLayout()
        srcTypeLayout.addWidget(QLabel("Source Type: "))
        self.srcTypeOptComboBox = QComboBox()
        self.srcTypeOptComboBox.setToolTip("Selected source type")
        self.srcTypeOptComboBox.addItems(["Mesh", "Joint"])
        self.srcTypeOptComboBox.currentIndexChanged.connect(self.srcTypeChangedSlot)
        srcTypeLayout.addWidget(self.srcTypeOptComboBox)
        mainLayout.addLayout(srcTypeLayout)

        # union option
        self.unionOptCheckBox = QCheckBox("Union")
        self.unionOptCheckBox.setToolTip("Combine selected meshes as one before create control")
        mainLayout.addWidget(self.unionOptCheckBox)

        # rig name widget
        self.rigNameWidget = QWidget()
        rigNameLayout = QHBoxLayout(self.rigNameWidget)
        rigNameLayout.addWidget(QLabel('Rig Name: '))
        self.rigNameLineEdit = QLineEdit()
        rigNameLayout.addWidget(self.rigNameLineEdit)
        mainLayout.addWidget(self.rigNameWidget)
        self.rigNameWidget.hide()

        # orientation
        self.orientationWidget = QWidget()
        orientLayout = QHBoxLayout(self.orientationWidget)
        orientLayout.addWidget(QLabel("Control Orientation: "))
        self.orientOptComboBox = QComboBox()
        self.orientOptComboBox.addItems(["World", "Object"])
        orientLayout.addWidget(self.orientOptComboBox)
        mainLayout.addWidget(self.orientationWidget)

        # global control option
        self.globalCtrlOptCheckBox = QCheckBox("Global Control")
        mainLayout.addWidget(self.globalCtrlOptCheckBox)

        setupBtn = QPushButton("Set Up")
        setupBtn.clicked.connect(self.setup)
        mainLayout.addWidget(setupBtn)

        self.unionOptCheckBox.stateChanged.connect(self.unionChkBoxChangeSlot)

    def setup(self):  # main method
        sels = pm.selected()
        srcTypeOpt = self.srcTypeOptComboBox.currentText()
        unionOpt = self.unionOptCheckBox.checkState()
        orientOpt = self.orientOptComboBox.currentText()
        globalCtrlOpt = self.globalCtrlOptCheckBox.checkState()

        if srcTypeOpt == "Mesh":
            meshes = SimplePropAutoRigger.getAllMeshes(sels)
            if not meshes:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText("Select mesh")
                msgBox.exec_()
                return
            results = self.setupWithMesh(meshes, unionOpt, orientOpt)
            joints = results[0]
            controlSpaceGrps = results[1]
        elif srcTypeOpt == "Joint":
            joints = sels
            if not isinstance(sels[0], pm.nodetypes.Joint):
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText("Select joint")
                msgBox.exec_()
                return
            controlSpaceGrps = self.setupWithJoint(joints)

        # clean up outliner
        systemGrp = pm.group(joints, n='system_grp')
        ctrlGrp = pm.group(controlSpaceGrps, n='ctrl_grp')

        if globalCtrlOpt:
            globalCtrl = SimplePropAutoRigger.createGlobalControls()
            pm.parent(systemGrp, ctrlGrp, globalCtrl)

    def setupWithMesh(self, meshes, unionOpt, orientOpt):
        origMeshes = []
        jntLs = []
        ctrlSpaceGrpLs = []

        if unionOpt:
            origMeshes = meshes
            meshes = self.createTempCombineMesh(meshes)

        for mesh in meshes:
            # get matrix
            meshMatrix = OBB.from_points(mesh.fullPathName()).matrix
            if orientOpt == "World":  # align orient to world while keep position
                meshMatrix = [1, 0, 0, 0,
                             0, 1, 0, 0,
                             0, 0, 1, 0,
                             meshMatrix[12], meshMatrix[13], meshMatrix[14], 1]

            # create joint
            pm.select(cl=True)
            jnt = pm.joint(n='%s_bnd_jnt' % mesh.name())
            cmds.xform(jnt.name(), matrix=meshMatrix)
            meshScale = max(jnt.scale.get())

            # create control
            ctrlName = mesh + '_ctrl'
            crv = control.Control(ctrlName)
            crv.setColor("skyBlue")
            ctrlSpaceGrp = SimplePropAutoRigger.createCtrlGrp(ctrlName)
            cmds.select(ctrlName + '.cv[*]', r=True)
            cmds.scale(meshScale, meshScale, meshScale, r=True)
            cmds.delete(cmds.parentConstraint(str(jnt), ctrlSpaceGrp, mo=False))
            cmds.makeIdentity(jnt.name(), apply=True)
            cmds.parentConstraint(ctrlName, str(jnt), mo=True)
            SimplePropAutoRigger.lockAndHideAttr(ctrlName)

            # skin
            pm.select(jnt, mesh, r=True)
            tak_misc.smoothSkinBind()
            if origMeshes:
                pm.select(mesh, origMeshes, r=True)
                tak_misc.addInfCopySkin()
                pm.delete(mesh)

            ctrlSpaceGrpLs.append(ctrlSpaceGrp)
            jntLs.append(jnt)

        return jntLs, ctrlSpaceGrpLs

    def setupWithJoint(self, joints):
        ctrlSpaceGrps = []

        for joint in joints:
            crv = control.Control('temp_ctrl', shape="circleY")
            crv.setColor("skyBlue")
            if self.searchLineEdit.text() and self.replaceLineEdit.text():
                ctrlName = re.sub(self.searchLineEdit.text(), self.replaceLineEdit.text(), joint.name())
                if ctrlName == joint.name():
                    ctrlName = joint + "_ctrl"
            else:
                ctrlName = joint + "_ctrl"
            cmds.rename(crv.name, ctrlName)
            ctrlSpaceGrp = SimplePropAutoRigger.createCtrlGrp(ctrlName)
            cmds.delete(cmds.parentConstraint(joint.name(), ctrlSpaceGrp, mo=False))
            cmds.makeIdentity(joint.name(), apply=True)
            cmds.parentConstraint(ctrlName, joint.name(), mo=True)
            SimplePropAutoRigger.lockAndHideAttr(ctrlName)
            ctrlSpaceGrps.append(ctrlSpaceGrp)

        return ctrlSpaceGrps

    def srcTypeChangedSlot(self, index):
        if index == SourceType.mesh:
            self.unionOptCheckBox.show()
            self.orientationWidget.show()
            self.searchReplaceWidget.hide()
        elif index == SourceType.joint:
            self.unionOptCheckBox.hide()
            self.orientationWidget.hide()
            self.searchReplaceWidget.show()

    def unionChkBoxChangeSlot(self, state):
        if state == 2:
            self.rigNameWidget.show()
        else:
            self.rigNameWidget.hide()

    def createTempCombineMesh(self, meshes):
        dupMeshes = pm.duplicate(meshes)
        combinedMesh = pm.polyUnite(dupMeshes, ch=False, n=self.rigNameLineEdit.text())
        return combinedMesh

    @staticmethod
    def getAllMeshes(sels):
        allMeshes = []

        for sel in sels:
            meshes = [mesh.getParent() for mesh in sel.getChildren(allDescendents=True, type='mesh') if 'Orig' not in mesh.name()]
            allMeshes.extend(meshes)

        return allMeshes

    @staticmethod
    def createGlobalControls():
        # Global main control
        glbMainCtrl = control.Control('temp_ctrl', shape='circleY')
        glbMainCtrl.setColor("yellow")
        glbMainCtrlName = cmds.rename(glbMainCtrl.name, 'global_main_ctrl')
        tak_misc.doGroup(glbMainCtrlName, '_zero')

        # Global sub control
        glbSubCtrl = control.Control('temp_ctrl', shape='circleY')
        glbSubCtrl.setColor("yellow")
        glbSubCtrlName = cmds.rename(glbSubCtrl.name, 'global_sub_ctrl')
        tak_misc.doGroup(glbSubCtrlName, '_zero')

        # Clean up outliner
        pm.parent(glbSubCtrlName+'_zero', glbMainCtrlName)
        cmds.group(glbMainCtrlName + '_zero', n='rig')
        return glbSubCtrlName

    @staticmethod
    def createCtrlGrp(ctrl):
        tak_misc.doGroup(ctrl, '_zero')
        tak_misc.doGroup(ctrl, '_extra')

        return ctrl + '_zero'

    @staticmethod
    def lockAndHideAttr(ctrl):
        lockHideAttrLs = ['scaleX', 'scaleY', 'scaleZ', 'visibility']

        for attr in lockHideAttrLs:
            cmds.setAttr('%s.%s' % (ctrl, attr), channelBox=False, keyable=False, lock=True)
