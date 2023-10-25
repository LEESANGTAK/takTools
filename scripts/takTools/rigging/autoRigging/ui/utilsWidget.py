from PySide2 import QtWidgets

import pymel.core as pm

from ..base import module
from ..base import general
from ..utils import transform as trsfUtil
from ..utils import dynamic as dynUtil


class UtilWidget(QtWidgets.QWidget):
    def __init__(self):
        super(UtilWidget, self).__init__()

        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    def createWidgets(self):
        self.createModuleBtn = QtWidgets.QPushButton('Create Module')
        self.createOutJointsBtn = QtWidgets.QPushButton('Create Out Joints')
        self.createSkinJointsBtn = QtWidgets.QPushButton('Create Skin Joints')
        self.setupGlobalDynamicBtn = QtWidgets.QPushButton('Setup Global Dynamic Controller', toolTip='Select module groups.')
        self.setupHybridIKBtn = QtWidgets.QPushButton('Setup Hybrid IK')
        self.ctrlToBindPoseBtn = QtWidgets.QPushButton('Match Controllers Bind Pose', toolTip='Select skeleton root first and controllers.')

    def createLayouts(self):
        gridLayout = QtWidgets.QGridLayout(self)
        gridLayout.addWidget(self.createModuleBtn, 0, 0)
        gridLayout.addWidget(self.createOutJointsBtn, 0, 1)
        gridLayout.addWidget(self.createSkinJointsBtn, 0, 2)
        gridLayout.addWidget(self.setupGlobalDynamicBtn, 1, 0)
        gridLayout.addWidget(self.setupHybridIKBtn, 1, 1)
        gridLayout.addWidget(self.ctrlToBindPoseBtn, 1, 2)

    def createConnections(self):
        self.createModuleBtn.clicked.connect(self.createModule)
        self.createOutJointsBtn.clicked.connect(self.createOutJoints)
        self.createSkinJointsBtn.clicked.connect(self.createSkinJoints)
        self.setupGlobalDynamicBtn.clicked.connect(self.setupGlobalDynamicController)
        self.setupHybridIKBtn.clicked.connect(self.setupHybridIK)
        self.ctrlToBindPoseBtn.clicked.connect(self.controllersToBindPose)

    def createModule(self):
        name, ok = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Module Name:', QtWidgets.QLineEdit.Normal)
        if ok:
            module.Module(name)

    def createOutJoints(self):
        pm.undoInfo(openChunk=True)
        joints = pm.ls(sl=True)
        for jnt in joints:
            childJoints = jnt.getChildren(ad=True, type='joint')
            if childJoints:
                jointsChain = (childJoints + [jnt])[::-1]
                general.createJointChain(jointsChain, suffix='_outJnt')
            else:
                outJnt = pm.duplicate(jnt, n='{0}_outJnt'.format(jnt))[0]
                pm.parentConstraint(outJnt, jnt, mo=True)
                pm.scaleConstraint(outJnt, jnt, mo=True)
                pm.parent(outJnt, world=True)
        pm.undoInfo(closeChunk=True)

    def createSkinJoints(self):
        pm.undoInfo(openChunk=True)

        skinJoints = []
        joints = pm.ls(sl=True)
        for jnt in joints:
            skinJnt = jnt.duplicate(n=jnt.replace('_outJnt', ''))[0]
            try:
                pm.parent(skinJnt, w=True)
            except:
                pass
            pm.parentConstraint(jnt, skinJnt, mo=True)
            pm.scaleConstraint(jnt, skinJnt, mo=True)
            skinJnt.segmentScaleCompensate.set(False)
            skinJoints.append(skinJnt)

        for skinJnt in skinJoints:
            for childSkinJnt in skinJnt.getChildren(ad=True, type='joint'):
                childSkinJnt = childSkinJnt.rename(childSkinJnt.replace('_outJnt', ''))
                childJnt = pm.PyNode('{}_outJnt'.format(childSkinJnt))
                pm.parentConstraint(childJnt, childSkinJnt, mo=True)
                pm.scaleConstraint(childJnt, childSkinJnt, mo=True)
                childSkinJnt.segmentScaleCompensate.set(False)

        pm.undoInfo(closeChunk=True)

    def setupGlobalDynamicController(self):
        result = pm.promptDialog(title='Solver Name', message='Enter Name', button=['OK', 'Cancel'], dismissString='Cancel')
        if result == 'OK':
            name = pm.promptDialog(q=True, text=True)
        else:
            return

        pm.undoInfo(openChunk=True)

        hairSystems = [moduleGrp.getChildren(ad=True, type='hairSystem')[0] for moduleGrp in pm.selected()]

        solver = pm.createNode('nucleus', n='{}_nucleus'.format(name))
        solver.inheritsTransform.set(False)
        solver.spaceScale.set(0.05)

        # Create controller
        dynCtrlName = 'dyn_ctrl'
        if not pm.objExists(dynCtrlName):
            dynCtrl = pm.curve(d=1, p=[[-1, 6, 0], [0, 5, 0], [1, 6, 0], [2, 6, 0], [4, 4, 0], [3, 3, 0], [2, 4, 0], [2, 1, 0], [-2, 1, 0], [-2, 4, 0], [-3, 3, 0], [-4, 4, 0], [-2, 6, 0], [-1, 6, 0]], n=dynCtrlName)
            pm.group(dynCtrl, n='{}_zero'.format(dynCtrl))
        else:
            dynCtrl = pm.PyNode(dynCtrlName)

        pm.addAttr(dynCtrl, ln=name, at='enum', en='---------------:')
        pm.setAttr('{}.{}'.format(dynCtrl, name), channelBox=True)
        pm.addAttr(dynCtrl, ln='{}_enable'.format(name), at='bool', keyable=True, dv=False)
        pm.addAttr(dynCtrl, ln='{}_startFrame'.format(name), at='long', keyable=True, dv=100000)
        pm.addAttr(dynCtrl, ln='{}_subSteps'.format(name), at='long', keyable=True, dv=3)

        dynCtrl.attr('{}_enable'.format(name)) >> solver.enable
        dynCtrl.attr('{}_startFrame'.format(name)) >> solver.startFrame
        dynCtrl.attr('{}_subSteps'.format(name)) >> solver.subSteps

        for hairSystem in hairSystems:
            dynUtil.changeSolver(hairSystem, solver)
            localDynCtrl = list(set(hairSystem.inputs(type='transform', exactType=True)))[0]
            dynCtrl.attr('{}_enable'.format(name)) >> localDynCtrl.enable
            dynCtrl.attr('{}_startFrame'.format(name)) >> localDynCtrl.startFrame
            dynCtrl.attr('{}_subSteps'.format(name)) >> localDynCtrl.subSteps

        pm.undoInfo(closeChunk=True)


    def setupHybridIK(self):
        pm.undoInfo(openChunk=True)
        ctrls = pm.ls(sl=True)
        trsfUtil.setupHybridIK(ctrls)
        pm.undoInfo(closeChunk=True)

    def controllersToBindPose(self):
        sels = pm.selected()
        skeletonRoot = sels[0]
        ctrls = sels[1:]
        trsfUtil.matchControllersToBindPose(skeletonRoot, ctrls)
