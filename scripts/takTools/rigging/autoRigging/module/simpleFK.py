import pymel.core as pm

from ..base import general
from ..base import module
from ..utils import globalUtil


def build(
        name,
        joints,
        attachTo=None,
        parentGrp=None,
    ):
    joints = [pm.PyNode(jnt) for jnt in joints]

    moduleObj = module.Module(name)

    outJoints = createOutJoints(joints)
    buildHierarchy(outJoints)
    ctrls = createControls(outJoints)

    # Cleanup outliner
    pm.parent(outJoints[0], moduleObj.outGrp)
    pm.parent(general.getSpaceGrp(ctrls[0]), moduleObj.ctrlGrp)

    moduleObj.outGrp.hide()
    moduleObj.systemGrp.hide()

def getJointsToDuplicate(startJoint, endJoint):
    jointsToDuplicate = [startJoint]

    childJnts = startJoint.getChildren(ad=True, type='joint')
    childJnts = globalUtil.reverseOrder(childJnts)

    for childJnt in childJnts:
        if childJnt == endJoint:
            jointsToDuplicate.append(endJoint)
            break
        jointsToDuplicate.append(childJnt)

    return jointsToDuplicate

def createOutJoints(joints):
    outJnts = []

    for jnt in joints:
        outJnt = pm.duplicate(jnt, n='{0}_outJnt'.format(jnt.name()), po=True)[0]
        pm.parent(outJnt, world=True)
        pm.parentConstraint(outJnt, jnt, mo=True)
        outJnt.s >> jnt.s
        outJnts.append(outJnt)

    return outJnts

def buildHierarchy(joints):
    for i in range(len(joints)):
        if i == 0:
            continue
        pm.parent(joints[i], joints[i-1])

def createControls(outJoints):
    ctrls = []

    for jnt in outJoints:
        if jnt == outJoints[-1]:
            break
        jntParent = jnt.getParent()
        ctrl = general.createController(jnt, jnt.replace('_outJnt', '_ctrl'), matchRotateOrder=True)
        ctrl.scale >> jnt.scale
        if jntParent:
            parentCtrl = jntParent.replace('_outJnt', '_ctrl')
            pm.PyNode(parentCtrl) | general.getSpaceGrp(ctrl)
        ctrls.append(ctrl)

    return ctrls
