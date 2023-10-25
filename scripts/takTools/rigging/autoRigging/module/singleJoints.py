import maya.cmds as cmds
import pymel.core as pm

from ..base import module
from ..base import general
from ..base import controller


def build(
    name,
    joints,
    attachTo=None,
    parentGrp=None,
):
    joints = [pm.PyNode(jnt) for jnt in joints.split(',')]

    # Create module
    moduleObj = module.Module(name)

    # Create out joints
    outJoints = createOutJoints(joints)

    # Create controls
    ctrls = createControls(outJoints)

    # Cleanup outliner
    pm.parent(outJoints, moduleObj.outGrp)
    for ctrl in ctrls:
        pm.parent(ctrl.spaceGrp, moduleObj.ctrlGrp)

    moduleObj.outGrp.hide()
    moduleObj.systemGrp.hide()

def createOutJoints(joints):
    outJnts = []

    for jnt in joints:
        outJnt = pm.duplicate(jnt, n='{0}_outJnt'.format(jnt), po=True)[0]
        pm.parentConstraint(outJnt, jnt, mo=True)
        outJnt.s >> jnt.s
        outJnts.append(outJnt)

    return outJnts

def createControls(outJoints):
    ctrls = []

    for jnt in outJoints:
        ctrl = controller.Controller(jnt.replace('_outJnt', '_ctrl'), shape='cube')
        ctrl.createGroups()
        ctrl.matchTo(jnt, position=True, orientation=True)
        ctrl.connectTo(jnt, parent=True, scale=True)
        ctrls.append(ctrl)

    return ctrls
