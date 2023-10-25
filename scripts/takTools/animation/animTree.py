"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Created: 2019.04.05
Description:
    You can animating static modeled tree things roughly.
"""

import maya.api.OpenMaya as om
import pymel.core as pm
import random


class UI(object):
    winName = 'animTreeUI'

    def __init__(self):
        if pm.window(self.winName, q=True, exists=True):
            pm.deleteUI(self.winName)

        self.buildUI()
        pm.showWindow(self.winName)

    def buildUI(self):
        pm.window(self.winName, title='Animating Tree', menuBar=True, mnb=False, mxb=False)
        pm.menu('extraToolsMenu', label='Extra Tools')
        pm.menuItem(label='Create Joint Tree', c=UI.createJointTree)
        pm.columnLayout(adj=True, columnAlign='left')
        pm.textFieldGrp('treeNameTextFieldGrp', label='Tree Name: ', columnAlign=[(1, 'left')], columnWidth=[(1, 60)])
        pm.separator(h=10, style='in')
        pm.text(label='Meshes: ')
        pm.textScrollList('meshTextScrollList')
        pm.popupMenu()
        pm.menuItem(label='Load Selected', c=lambda *args: UI.populateTextScrollList('meshTextScrollList'))
        pm.menuItem(label='Add Selected', c=lambda *args: UI.addToTextScrollList('meshTextScrollList'))
        pm.separator(h=10, style='in')
        pm.textFieldGrp('trunkTextFieldGrp', label='Trunk Joint: ', columnAlign=[(1, 'left')], columnWidth=[(1, 110)])
        pm.popupMenu()
        pm.menuItem(label='Load Selected', c=lambda *args: UI.populateTextField('trunkTextFieldGrp'))
        pm.text(label='Main Branch Joints: ')
        pm.textScrollList('mainBranchTextScrollList')
        pm.popupMenu()
        pm.menuItem(label='Load Selected', c=lambda *args: UI.populateTextScrollList('mainBranchTextScrollList'))
        pm.menuItem(label='Add Selected', c=lambda *args: UI.addToTextScrollList('mainBranchTextScrollList'))
        pm.text(label='Sub Branch Joints: ')
        pm.textScrollList('subBranchTextScrollList')
        pm.popupMenu()
        pm.menuItem(label='Load Selected', c=lambda *args: UI.populateTextScrollList('subBranchTextScrollList'))
        pm.menuItem(label='Add Selected', c=lambda *args: UI.addToTextScrollList('subBranchTextScrollList'))
        pm.button(label='Build', c=self.main)
        pm.window(self.winName, e=True, w=100, h=100)

    @staticmethod
    def populateTextScrollList(widgetName):
        sels = [str(item) for item in pm.selected()]
        items = pm.textScrollList(widgetName, q=True, allItems=True)
        if items:
            pm.textScrollList(widgetName, e=True, removeAll=True)
        pm.textScrollList(widgetName, e=True, append=sels)

    @staticmethod
    def addToTextScrollList(widgetName):
        sels = [str(item) for item in pm.selected()]
        items = pm.textScrollList(widgetName, q=True, allItems=True)
        if items:
            sels = list(set(sels) - set(items))
        pm.textScrollList(widgetName, e=True, append=sels)

    @staticmethod
    def populateTextField(widgeName):
        sel = pm.selected()[0]
        pm.textFieldGrp(widgeName, e=True, text=str(sel))

    def main(self, *args):
        # Get data
        treeName = pm.textFieldGrp('treeNameTextFieldGrp', q=True, text=True)
        meshes = [pm.PyNode(item).getShape() for item in pm.textScrollList('meshTextScrollList', q=True, allItems=True)]
        rootJnt = pm.textFieldGrp('trunkTextFieldGrp', q=True, text=True)
        mainBranchJnts = pm.textScrollList('mainBranchTextScrollList', q=True, allItems=True)
        subBranchJnts = pm.textScrollList('subBranchTextScrollList', q=True, allItems=True)

        # Duplicate referencing materials and reassign
        self.reassignMaterial(meshes)

        # Orient joint
        pm.select(rootJnt, r=True, hi=True)
        pm.joint(e=True, oj='xzy', secondaryAxisOrient='xdown', ch=False, zso=True)

        # Bind
        influences = pm.selected()
        for mesh in meshes:
            pm.skinCluster(influences, mesh, mi=5, dr=4.0, tsb=True, omi=False, nw=True)

        controller = self.createController(treeName)
        hierarchyInfo = self.saveHierachyInfo(mainBranchJnts+subBranchJnts)

        if mainBranchJnts:
            pm.parent(mainBranchJnts, w=True)
        if subBranchJnts:
            pm.parent(subBranchJnts, w=True)

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
        controller = pm.spaceLocator(n='{}_ctrl'.format(name))

        pm.addAttr(controller, ln='offset', at='double', keyable=True)
        for control in controls:
            pm.addAttr(controller, ln=control, at='enum', en='---------------:')
            pm.setAttr('{}.{}'.format(controller, control), channelBox=True)
            for attr in attrs:
                pm.addAttr(controller, ln='{}_{}'.format(control, attr), at='double', keyable=True, dv=0.1)

        return controller

    def saveHierachyInfo(self, joints):
        hierarchyInfo = {}

        for jnt in joints:
            hierarchyInfo[jnt] = pm.PyNode(jnt).getParent()

        return hierarchyInfo

    def reParentBranches(self, hierarchyInfo):
        for branch, parent in hierarchyInfo.iteritems():
            parent|branch

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
            pm.select(rootJoint, hi=True, r=True)
            joints = pm.selected()
            for joint in joints:
                exprStr += '\n{0}.rotateX = $valX;\n{0}.rotateY = $valY;\n{0}.rotateZ = $valZ;\n'.format(str(joint))
        pm.expression(string=exprStr)

    def setDefaultValue(self, controller):
        controller.trunk_speed.set(0.0)
        controller.trunk_amplitude.set(0.0)

        controller.mainBranch_speed.set(0.05)
        controller.mainBranch_amplitude.set(0.25)

        controller.subBranch_speed.set(0.075)
        controller.subBranch_amplitude.set(0.5)

    def reassignMaterial(self, meshes):
        for mesh in meshes:
            sgName = pm.listConnections(mesh, d=True, type="shadingEngine")
            mats = [mat for mat in pm.ls(pm.listConnections(sgName), materials=True) if not pm.nodeType(mat) == 'displacementShader']

            pm.select(mats[0], r=True)
            pm.hyperShade(duplicate=True)
            dupMat = pm.ls(sl=True)[0]

            pm.select(mesh, r=True)
            pm.hyperShade(assign=dupMat)

    @staticmethod
    def createJointTree(*args):
        result = pm.promptDialog(
            title='Create Joint Tree',
            message='Number of Joints:',
            button=['Create', 'Cancel'],
            defaultButton='Create',
            cancelButton='Cancel',
            dismissString='Cancel',
            text=150
        )

        if result == 'Create':
            numOfJnts = int(pm.promptDialog(q=True, text=True))
        else:
            return

        result = pm.promptDialog(
            title='Set Growth Axis',
            message='+X or +Y or +Z\n-X or -Y or -Z:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel',
            text='+Y'
        )

        if result == 'OK':
            sortingAxis = pm.promptDialog(q=True, text=True)
        else:
            return

        # Scatter joints
        mesh = pm.selected()[0].getShape()
        numOfVtxs = mesh.numVertices()
        sampleVtxIds = random.sample(range(numOfVtxs), numOfJnts)
        jnts = []
        for id in sampleVtxIds:
            vtxPos = mesh.vtx[id].getPosition(space='world')
            jnts.append(pm.joint(position=vtxPos))
            pm.select(cl=True)

        # Make tree joint hierarchy
        reverse = False if '-' in sortingAxis else True
        jnts.sort(key=lambda jnt: jnt.attr('translate'+sortingAxis[-1]).get(), reverse=reverse)
        for jnt in jnts:
            distance = 1000
            parentJnt = None
            for remainJnt in jnts[jnts.index(jnt)+1:]:
                length = (om.MVector(jnt.getTranslation(ws=True)) - om.MVector(remainJnt.getTranslation(ws=True))).length()
                if length < distance:
                    distance = length
                    parentJnt = remainJnt
            if parentJnt:
                parentJnt|jnt