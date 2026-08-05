"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Created: 2019.04.05
Description:
    You can animating static modeled tree things roughly.
"""

import maya.api.OpenMaya as om
from maya import cmds
import random


class UI(object):
    winName = 'animTreeUI'

    def __init__(self):
        if cmds.window(self.winName, q=True, exists=True):
            cmds.deleteUI(self.winName)

        self.buildUI()
        cmds.showWindow(self.winName)

    def buildUI(self):
        cmds.window(self.winName, title='Animating Tree', menuBar=True, mnb=False, mxb=False)
        cmds.menu('extraToolsMenu', label='Extra Tools')
        cmds.menuItem(label='Create Joint Tree', c=UI.createJointTree)
        cmds.columnLayout(adj=True, columnAlign='left')
        cmds.textFieldGrp('treeNameTextFieldGrp', label='Tree Name: ', columnAlign=[(1, 'left')], columnWidth=[(1, 60)])
        cmds.separator(h=10, style='in')
        cmds.text(label='Meshes: ')
        cmds.textScrollList('meshTextScrollList')
        cmds.popupMenu()
        cmds.menuItem(label='Load Selected', c=lambda *args: UI.populateTextScrollList('meshTextScrollList'))
        cmds.menuItem(label='Add Selected', c=lambda *args: UI.addToTextScrollList('meshTextScrollList'))
        cmds.separator(h=10, style='in')
        cmds.textFieldGrp('trunkTextFieldGrp', label='Trunk Joint: ', columnAlign=[(1, 'left')], columnWidth=[(1, 110)])
        cmds.popupMenu()
        cmds.menuItem(label='Load Selected', c=lambda *args: UI.populateTextField('trunkTextFieldGrp'))
        cmds.text(label='Main Branch Joints: ')
        cmds.textScrollList('mainBranchTextScrollList')
        cmds.popupMenu()
        cmds.menuItem(label='Load Selected', c=lambda *args: UI.populateTextScrollList('mainBranchTextScrollList'))
        cmds.menuItem(label='Add Selected', c=lambda *args: UI.addToTextScrollList('mainBranchTextScrollList'))
        cmds.text(label='Sub Branch Joints: ')
        cmds.textScrollList('subBranchTextScrollList')
        cmds.popupMenu()
        cmds.menuItem(label='Load Selected', c=lambda *args: UI.populateTextScrollList('subBranchTextScrollList'))
        cmds.menuItem(label='Add Selected', c=lambda *args: UI.addToTextScrollList('subBranchTextScrollList'))
        cmds.button(label='Build', c=self.main)
        cmds.window(self.winName, e=True, w=100, h=100)

    @staticmethod
    def populateTextScrollList(widgetName):
        sels = [str(item) for item in cmds.ls(sl=True)]
        items = cmds.textScrollList(widgetName, q=True, allItems=True)
        if items:
            cmds.textScrollList(widgetName, e=True, removeAll=True)
        cmds.textScrollList(widgetName, e=True, append=sels)

    @staticmethod
    def addToTextScrollList(widgetName):
        sels = [str(item) for item in cmds.ls(sl=True)]
        items = cmds.textScrollList(widgetName, q=True, allItems=True)
        if items:
            sels = list(set(sels) - set(items))
        cmds.textScrollList(widgetName, e=True, append=sels)

    @staticmethod
    def populateTextField(widgeName):
        sel = cmds.ls(sl=True)[0]
        cmds.textFieldGrp(widgeName, e=True, text=str(sel))

    def main(self, *args):
        # Get data
        treeName = cmds.textFieldGrp('treeNameTextFieldGrp', q=True, text=True)
        meshes = [cmds.listRelatives(item, s=True)[0] for item in cmds.textScrollList('meshTextScrollList', q=True, allItems=True)]
        rootJnt = cmds.textFieldGrp('trunkTextFieldGrp', q=True, text=True)
        mainBranchJnts = cmds.textScrollList('mainBranchTextScrollList', q=True, allItems=True)
        subBranchJnts = cmds.textScrollList('subBranchTextScrollList', q=True, allItems=True)

        # Duplicate referencing materials and reassign
        self.reassignMaterial(meshes)

        # Orient joint
        cmds.select(rootJnt, r=True, hi=True)
        cmds.joint(e=True, oj='xzy', secondaryAxisOrient='xdown', ch=False, zso=True)

        # Bind
        influences = cmds.ls(sl=True)
        for mesh in meshes:
            cmds.skinCluster(influences, mesh, mi=5, dr=4.0, tsb=True, omi=False, nw=True)

        controller = self.createController(treeName)
        hierarchyInfo = self.saveHierachyInfo(mainBranchJnts+subBranchJnts)

        if mainBranchJnts:
            cmds.parent(mainBranchJnts, w=True)
        if subBranchJnts:
            cmds.parent(subBranchJnts, w=True)

        self.createExpressions(controller, 'trunk', [rootJnt])
        if mainBranchJnts:
            self.createExpressions(controller, 'mainBranch', mainBranchJnts)
        if subBranchJnts:
            self.createExpressions(controller, 'subBranch', subBranchJnts)

        self.reParentBranches(hierarchyInfo)
        self.setDefaultValue(controller)

    def createController(self, name):
        controls = ['trunk', 'mainBranch', 'subBranch']
        attrs = ['speed', 'amplitude']
        controller = cmds.spaceLocator(n='{}_ctrl'.format(name))

        cmds.addAttr(controller, ln='offset', at='double', keyable=True)
        for control in controls:
            cmds.addAttr(controller, ln=control, at='enum', en='---------------:')
            cmds.setAttr('{}.{}'.format(controller, control), channelBox=True)
            for attr in attrs:
                cmds.addAttr(controller, ln='{}_{}'.format(control, attr), at='double', keyable=True, dv=0.1)

        return controller

    def saveHierachyInfo(self, joints):
        hierarchyInfo = {}

        for jnt in joints:
            hierarchyInfo[jnt] = cmds.listRelatives(jnt, p=True)[0]

        return hierarchyInfo

    def reParentBranches(self, hierarchyInfo):
        for branch, parent in hierarchyInfo.items():
            cmds.parent(branch, parent)

    def createExpressions(self, controller, control, rootJoints):
        offsetX = random.uniform(1, 10000)
        offsetY = random.uniform(1, 10000)
        offsetZ = random.uniform(1, 10000)
        exprStr = '''
        float $speed = {controller}.{control}_speed;
        float $amplitude = {controller}.{control}_amplitude;
        float $offset = {controller}.offset;
        float $offsetX = {0} + $offset;
        float $offsetY = {1} + $offset;
        float $offsetZ = {2} + $offset;
        float $valX = noise(frame*$speed+$offsetX)*$amplitude;
        float $valY = noise(frame*$speed+$offsetY)*$amplitude;
        float $valZ = noise(frame*$speed+$offsetZ)*$amplitude;
        '''.format(offsetX, offsetY, offsetZ, controller=controller, control=control)

        for rootJoint in rootJoints:
            cmds.select(rootJoint, hi=True, r=True)
            joints = cmds.ls(sl=True)
            for joint in joints:
                exprStr += '\n{0}.rotateX = $valX;\n{0}.rotateY = $valY;\n{0}.rotateZ = $valZ;\n'.format(str(joint))
        cmds.expression(string=exprStr)

    def setDefaultValue(self, controller):
        cmds.setAttr(f'{controller}.trunk_speed', 0.0)
        cmds.setAttr(f'{controller}.trunk_amplitude', 0.0)

        cmds.setAttr(f'{controller}.mainbranch_speed', 0.05)
        cmds.setAttr(f'{controller}.mainBranch_amplitude', 0.25)

        cmds.setAttr(f'{controller}.subBranch_speed', 0.075)
        cmds.setAttr(f'{controller}.subBranch_amplitude', 0.5)

    def reassignMaterial(self, meshes):
        for mesh in meshes:
            sgName = cmds.listConnections(mesh, d=True, type="shadingEngine")
            mats = [mat for mat in cmds.ls(cmds.listConnections(sgName), materials=True) if not cmds.nodeType(mat) == 'displacementShader']

            cmds.select(mats[0], r=True)
            cmds.hyperShade(duplicate=True)
            dupMat = cmds.ls(sl=True)[0]

            cmds.select(mesh, r=True)
            cmds.hyperShade(assign=dupMat)

    @staticmethod
    def createJointTree(*args):
        result = cmds.promptDialog(
            title='Create Joint Tree',
            message='Number of Joints:',
            button=['Create', 'Cancel'],
            defaultButton='Create',
            cancelButton='Cancel',
            dismissString='Cancel',
            text=150
        )

        if result == 'Create':
            numOfJnts = int(cmds.promptDialog(q=True, text=True))
        else:
            return

        result = cmds.promptDialog(
            title='Set Growth Axis',
            message='+X or +Y or +Z\n-X or -Y or -Z:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel',
            text='+Y'
        )

        if result == 'OK':
            sortingAxis = cmds.promptDialog(q=True, text=True)
        else:
            return

        # Scatter joints
        mesh = cmds.listRelatives(cmds.ls(sl=True)[0], s=True)[0]
        numOfVtxs = cmds.polyEvaluate(mesh, v=True)
        sampleVtxIds = random.sample(range(numOfVtxs), numOfJnts)
        jnts = []
        for id in sampleVtxIds:
            vtxPos = cmds.pointPosition(f'{mesh}.vtx[{id}]', w=True)
            jnts.append(cmds.joint(position=vtxPos))
            cmds.select(cl=True)

        # Make tree joint hierarchy
        reverse = False if '-' in sortingAxis else True
        jnts.sort(key=lambda jnt: cmds.getAttr(f'{jnt}.translate{sortingAxis[-1]}'), reverse=reverse)
        for jnt in jnts:
            distance = 1000
            parentJnt = None
            for remainJnt in jnts[jnts.index(jnt)+1:]:
                length = (om.MVector(cmds.xform(jnt, q=True, ws=True, t=True)) - om.MVector(cmds.xform(remainJnt, q=True, ws=True, t=True))).length()
                if length < distance:
                    distance = length
                    parentJnt = remainJnt
            if parentJnt:
                cmds.parent(jnt, parentJnt)