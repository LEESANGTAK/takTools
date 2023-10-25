import maya.api.OpenMaya as om
import pymel.core as pm

from . import globalUtil


def createOutJoints(joints, suffix='_outJnt'):
    newJoints = []
    joints = [pm.PyNode(jnt) for jnt in joints]

    for jnt in joints:
        newJnt = pm.duplicate(jnt, n=jnt + suffix, po=True)[0]
        parentCnst = pm.parentConstraint(newJnt, jnt, mo=True)
        parentCnst.interpType.set(2)
        newJnt.s >> jnt.s
        newJoints.append(newJnt)
        pm.parent(newJnt, world=True)

    for jnt in joints:
        jntParent = jnt.getParent()
        if jntParent:
            newJntParent = jntParent + suffix
            if pm.objExists(newJntParent):
                pm.parent(jnt + suffix, newJntParent)

    pm.parent(newJoints[0], world=True)

    return newJoints

def createJointChain(joints, suffix):
    newJoints = []
    joints = [pm.PyNode(jnt) for jnt in joints]

    for jnt in joints:
        newJnt = pm.duplicate(jnt, n=jnt + suffix, po=True)[0]
        newJoints.append(newJnt)
        pm.parent(newJnt, world=True)

    for i in xrange(len(joints)):
        if i == 0:
            continue
        joints[i-1] | joints[i]

    pm.parent(newJoints[0], world=True)

    return newJoints