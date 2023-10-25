"""
Author: Tak
Website: tak.ta-note.com

Created: 02/19/2021
Updated: 02/22/2021

Requirements:
FK/IK switch and source objects attributes must be in single "Hub Node".
"Hub Node" can be any dag node.

# Attributes order in "Hub Node"
    fkIkSwitch
    fkJointStart
    fkJointMid
    fkJointEnd
    ikJointStart
    ikJointMid
    ikJointEnd
    fkControllerStart
    fkControllerMid
    fkControllerEnd
    ikController
    poleVectorController

    * Attributes order have to same as above.
    * Start: Top node of two-bone limb. e.g.) shoulder / hip
    * Mid: Second node of two-bone limb. e.g.) elbow / knee
    * End: End node of two-bone limb. e.g.) wrist / ankle

# "fkIkSwitch" attribute
    name: fkIk
    type: enum [fk, ik]

    * Enum items must keep in order as fk first and ik second.
    * "fkIkSwitch" attribute must be connect to controllers with proxy attribute.
    * Codes that adding fkIk proxy attribute to controllers is like below.
      fkCtrls = ['shoulder_L_fk_ctrl', 'elbow_L_fk_ctrl', 'wrist_L_fk_ctrl']
      ikCtrls = ['arm_L_ik_ctrl', 'arm_L_poleVector_ctrl']
      hubNode = 'arm_L_fkIk_switcher'
      switchAttrName = 'fkIk'
      pm.addAttr(hubNode, longName=switchAttrName, at='enum', en=['fk', 'ik'], keyable=False)
      for ctrl in fkCtrls + ikCtrls:
          pm.addAttr(ctrl, ln=switchAttrName, proxy='{0}.{1}'.format(hubNode, switchAttrName), keyable=True)

# Source objects attributes
    type: message

    * Must connected with source object's message attribute. e.g.) shoulder_L_fk_ctrl.message >> hubNode.fkControllerStart


* Test Code *
pm.delete(pm.ls(type='fkIkSnapper'))
pm.flushUndo()
pm.unloadPlugin('fkIkSnapper')
pm.loadPlugin('fkIkSnapper')
pm.createNode('fkIkSnapper')
"""

import logging

import pymel.core as pm
from maya.api import OpenMaya as om


def maya_useNewAPI():
    """ Say to maya that using api 2.0 """
    pass


logger = logging.getLogger("FkIkSnapper")
logger.setLevel(logging.INFO)

NODE_NAME = "fkIkSnapper"
NODE_ID = om.MTypeId(0x00002746)


class FkIkSnapper(om.MPxNode):
    # Message type enum
    EVENT_MSG_ID = 0
    DG_MSG_ID = 1
    NODE_MSG_ID = 2

    # Switch attribute state enum
    FK_STATE = 0
    IK_STATE = 1

    FKIK_ATTR = "fkIk"

    registeredSwitchHubs = []
    callbackIdInfo = {EVENT_MSG_ID: [], DG_MSG_ID: [], NODE_MSG_ID: []}

    def __init__(self):
        super(FkIkSnapper, self).__init__()

        self._lastSelCtrl = None
        self._lastFkIkState = None

        self._cleanupCallbacks()  # Prevent same callback created
        self._addCallbacks()

    def _addCallbacks(self):
        FkIkSnapper.callbackIdInfo[FkIkSnapper.EVENT_MSG_ID].append(om.MEventMessage.addEventCallback("SelectionChanged", self._getSwitchInfoCB))
        FkIkSnapper.callbackIdInfo[FkIkSnapper.DG_MSG_ID].append(om.MDGMessage.addNodeRemovedCallback(self._removeCallbacksCB, "dependNode"))

    def _snapControllersCB(self, *args):
        sels = om.MGlobal.getActiveSelectionList()
        if sels.isEmpty():
            return

        selObj = sels.getDependNode(0)
        if not FkIkSnapper._isValidController(selObj):
            return

        switchHubNode = FkIkSnapper._getSwitchHubNode(selObj)
        if not FkIkSnapper._isRegisteredHub(switchHubNode):  # Add selection changed callback when unregistered "Hub Node" found
            FkIkSnapper.callbackIdInfo[FkIkSnapper.NODE_MSG_ID].append(om.MNodeMessage.addAttributeChangedCallback(switchHubNode, self._fkIkAttrChangedCB))
            FkIkSnapper.registeredSwitchHubs.append(switchHubNode)

        fkIkState = FkIkSnapper._getFkIkState(switchHubNode)
        self._lastFkIkState = fkIkState

        self._matchControllers(selObj, fkIkState)

    def _getSwitchInfoCB(self, *args):
        sels = om.MGlobal.getActiveSelectionList()
        if sels.isEmpty():
            return

        selObj = sels.getDependNode(0)
        if not FkIkSnapper._isValidController(selObj):
            return

        switchHubNode = FkIkSnapper._getSwitchHubNode(selObj)
        if not FkIkSnapper._isRegisteredHub(switchHubNode):  # Add selection changed callback when unregistered "Hub Node" found
            FkIkSnapper.callbackIdInfo[FkIkSnapper.NODE_MSG_ID].append(om.MNodeMessage.addAttributeChangedCallback(switchHubNode, self._fkIkAttrChangedCB))
            FkIkSnapper.registeredSwitchHubs.append(switchHubNode)
        self._lastSelCtrl = selObj

        fkIkState = FkIkSnapper._getFkIkState(switchHubNode)
        self._lastFkIkState = fkIkState

    def _fkIkAttrChangedCB(self, *args):
        if self._lastFkIkState == None:
            return

        sels = om.MGlobal.getActiveSelectionList()
        if sels.isEmpty():
            return

        selObj = sels.getDependNode(0)
        if FkIkSnapper._isValidController(selObj):
            ctrlFn = om.MFnDependencyNode(selObj)
            fkIkState = ctrlFn.findPlug(FkIkSnapper.FKIK_ATTR, True).asInt()
            if fkIkState != self._lastFkIkState:
                self._matchControllers(self._lastSelCtrl, self._lastFkIkState)

    @staticmethod
    def _isRegisteredHub(switchHubNode):
        return switchHubNode in FkIkSnapper.registeredSwitchHubs

    @staticmethod
    def _getFkIkState(switchHubNode):
        switchHubNodeFn = om.MFnDependencyNode(switchHubNode)
        fkIkAttrPlug = switchHubNodeFn.findPlug(FkIkSnapper.FKIK_ATTR, True)
        return fkIkAttrPlug.asInt()

    def _matchControllers(self, ctrlObj, fkIkState):
        self._lastSelCtrl = ctrlObj

        switchHubNode = FkIkSnapper._getSwitchHubNode(ctrlObj)
        fkJnts, ikJnts, fkCtrls, ikCtrl, pvCtrl = FkIkSnapper._getSourceObjNames(switchHubNode)

        if fkIkState == FkIkSnapper.FK_STATE:
            FkIkSnapper._snapIkToFk(ikCtrl, pvCtrl, fkJnts)
        elif fkIkState == FkIkSnapper.IK_STATE:
            FkIkSnapper._snapFkToIk(fkCtrls, ikJnts)

    @staticmethod
    def _isValidController(mObj):
        dgFn = om.MFnDependencyNode(mObj)
        fkIkAttr = dgFn.attribute(FkIkSnapper.FKIK_ATTR)
        if fkIkAttr.isNull():
            return False
        return True

    @staticmethod
    def _getSwitchHubNode(ctrlObj):
        dgFn = om.MFnDependencyNode(ctrlObj)
        ctrlConnectedPlugs = dgFn.getConnections()
        for plug in ctrlConnectedPlugs:
            if plug.partialName() == FkIkSnapper.FKIK_ATTR:
                return plug.source().node()

    @staticmethod
    def _getSourceObjNames(switchHubNode):
        """Gets fkJoints, ikJoints, fkControllers, ikControl, poleVectorControl information with switch "Hub Node"

        Args:
            switchHubNode (MObject): Node that has all attributes for switching rig and snapping controller.

        Returns:
            Tuple: Objects names for snap controller.
        """
        sourceObjNames = []

        switchHubNodeFn = om.MFnDependencyNode(switchHubNode)
        for i in range(switchHubNodeFn.attributeCount()):
            attrFn = om.MFnAttribute(switchHubNodeFn.attribute(i))
            if attrFn.dynamic:  # Check whether is user defined attribute
                srcPlug = switchHubNodeFn.findPlug(switchHubNodeFn.attribute(i), True).source()
                if not srcPlug:  # Attribtue must connected with message attribute
                    continue
                sourceObjNames.append(om.MFnDependencyNode(srcPlug.node()).name())

        # sourceObjNames[0] is nullptr
        fkJnts = sourceObjNames[1:4]
        ikJnts = sourceObjNames[4:7]
        fkCtrls = sourceObjNames[7:10]
        ikCtrl = sourceObjNames[10]
        pvCtrl = sourceObjNames[11]

        return fkJnts, ikJnts, fkCtrls, ikCtrl, pvCtrl

    @staticmethod
    def _snapFkToIk(fkCtrls, ikJnts):
        logger.info("Snap fk controllers to ik joints.")
        for fkCtrl, ikJnt in zip(fkCtrls, ikJnts):
            ikJntTrans = pm.xform(ikJnt, q=True, t=True, ws=True)
            ikJntRot = pm.xform(ikJnt, q=True, ro=True, ws=True)

            pm.xform(fkCtrl, t=ikJntTrans, ws=True)
            pm.xform(fkCtrl, ro=ikJntRot, ws=True)

    @staticmethod
    def _snapIkToFk(ikCtrl, pvCtrl, fkJnts):
        logger.info("Snap ik controllers to fk joints.")
        fkEndJntTrans = pm.xform(fkJnts[-1], q=True, t=True, ws=True)
        fkEndJntRot = pm.xform(fkJnts[-1], q=True, ro=True, ws=True)

        pm.xform(ikCtrl, t=fkEndJntTrans, ws=True)
        pm.xform(ikCtrl, ro=fkEndJntRot, ws=True)
        pm.xform(pvCtrl, t=FkIkSnapper._getPoleVectorPosition(fkJnts), ws=True)

    @staticmethod
    def _getPoleVectorPosition(fkJnts):
        startVector = pm.dt.Vector(pm.xform(fkJnts[0], q=True, rp=True, ws=True))
        midVector = pm.dt.Vector(pm.xform(fkJnts[1], q=True, rp=True, ws=True))
        endVector = pm.dt.Vector(pm.xform(fkJnts[2], q=True, rp=True, ws=True))

        startToEndCenter = startVector + ((endVector - startVector) / 2)
        poleVector = midVector - startToEndCenter
        polePos = midVector + poleVector

        return polePos

    def _removeCallbacksCB(self, *args):
        """When fkIkSnapper node deleted all callbacks should be deleted.
        """
        delNode = args[0]
        if 'fkIkSnapper' in om.MFnDependencyNode(delNode).name():
            FkIkSnapper._cleanupCallbacks()
            FkIkSnapper.registeredSwitchHubs = []

    @staticmethod
    def _cleanupCallbacks():
        logger.info("Remove Callbacks")
        eventMsgId = FkIkSnapper.callbackIdInfo[FkIkSnapper.EVENT_MSG_ID]
        dgMsgId = FkIkSnapper.callbackIdInfo[FkIkSnapper.DG_MSG_ID]
        nodeMsgId = FkIkSnapper.callbackIdInfo[FkIkSnapper.NODE_MSG_ID]

        logger.debug("eventMsgId: {0}, eventMsgId: {1}, nodeMsgId: {2}".format(eventMsgId, dgMsgId, nodeMsgId))

        if eventMsgId:
            om.MEventMessage.removeCallbacks(eventMsgId)
        if dgMsgId:
            om.MDGMessage.removeCallbacks(dgMsgId)
        if nodeMsgId:
            om.MNodeMessage.removeCallbacks(nodeMsgId)

        FkIkSnapper.callbackIdInfo = {FkIkSnapper.EVENT_MSG_ID: [], FkIkSnapper.DG_MSG_ID: [], FkIkSnapper.NODE_MSG_ID: []}

    @classmethod
    def creator(cls):
        return FkIkSnapper()

    @classmethod
    def initialize(cls):
        pass

    def compute(self, plug, dataBlock):
        pass


def initializePlugin(pluginObj):
    pluginFn = om.MFnPlugin(pluginObj, 'Tak', '1.0')

    try:
        pluginFn.registerNode(NODE_NAME, NODE_ID, FkIkSnapper.creator, FkIkSnapper.initialize, om.MPxNode.kDependNode)
    except:
        om.MGlobal.displayError('Fail to register node {0}.'.format(NODE_NAME))

def uninitializePlugin(pluginObj):
    pluginFn = om.MFnPlugin(pluginObj)

    try:
        pluginFn.deregisterNode(NODE_ID)
    except:
        om.MGlobal.displayError('Fail to deregister node {0}.'.format(NODE_NAME))
