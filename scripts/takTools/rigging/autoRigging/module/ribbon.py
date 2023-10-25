import maya.cmds as cmds

from ..base import module


class Ribbon(object):
    def __init__(self):
        self.name = None
        self.startJoint = None
        self.endJoint = None
        self.skinJoints = []

        self.module = None
        self.outJoints = None
        self.surface = None
        self.controls = None

    def build(self):
        self.module = self.createModule(self.name)

        self.skinJoints.append(self.startJoint)
        betweenJoints = getBetweenJoints(self.startJoint, self.endJoint)
        self.skinJoints.append(betweenJoints)
        self.skinJoints.append(self.endJoint)

        self.outJoints = self.createOutJoints(self.skinJoints)
        self.surface = self.createSurface(self.outJoints)

    def createModule(self, name):
        moduleObj = None

        moduleObj = module.Module(name)

        return moduleObj

    def createOutJoints(self, skinJoints):
        outJoints = []

        for skinJnt in skinJoints:
            outJnt = cmds.duplicate(skinJnt, n='{0}_outJnt'.format(skinJnt), po=True)[0]

            cmds.parentConstraint(outJnt, skinJnt, mo=True)
            outJnt.s >> skinJnt.s

            cmds.parent(outJnt, world=True)

            outJoints.append(outJnt)

        return outJoints

    def createSurface(self, joints):
        surface = None
        return surface

    def createCluster(self, surface):
        clusters = []
        return clusters

    def createControls(self, clusters):
        ctrls = []
        return ctrls


def getBetweenJoints(startJoint, endJoint):
    betweenJoints = []

    childJoints = cmds.listRelatives(startJoint, ad=True, type='joint')
    childJoints.sort()

    for childJnt in childJoints:
        if childJnt == endJoint:
            break
        betweenJoints.append(childJnt)

    return betweenJoints