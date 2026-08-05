"""
Author: Sangtak Lee
Contact: chst27@gmail.com
"""


import maya.cmds as cmds
import maya.mel as mel


def getHairSystems(nucleus):
    hairSystems = []
    hairSystems = cmds.listConnections('%s.startFrame' % nucleus, source=False, destination=True, type='hairSystem', shapes=True) or []
    return hairSystems


def getNucleusControllerAttributes(nucleus):
    enableCtrlAttr = None
    startFrameCtrlAttr = None
    enable_plugs = cmds.listConnections('%s.enable' % nucleus, source=True, destination=False, plugs=True) or []
    start_plugs = cmds.listConnections('%s.startFrame' % nucleus, source=True, destination=False, plugs=True) or []
    enableCtrlAttr = enable_plugs[0] if enable_plugs else '%s.enable' % nucleus
    startFrameCtrlAttr = start_plugs[0] if start_plugs else '%s.startFrame' % nucleus
    return enableCtrlAttr, startFrameCtrlAttr


def getSplineIkCurve(hairSystem):
    splineIkCurve = None
    follicle_nodes = cmds.listConnections(hairSystem, source=False, destination=True, type='follicle', shapes=True) or []
    if not follicle_nodes:
        return None
    follicle = follicle_nodes[0]
    dynCurves = cmds.listConnections(follicle, source=False, destination=True, type='nurbsCurve', shapes=True) or []
    if not dynCurves:
        return None
    dynCurve = dynCurves[0]
    blendShapes = cmds.listConnections(dynCurve, source=False, destination=True, type='blendShape') or []
    if blendShapes:
        splineCandidates = cmds.listConnections(blendShapes[0], source=False, destination=True, type='nurbsCurve', shapes=True) or []
        splineIkCurve = splineCandidates[0] if splineCandidates else dynCurve
    else:
        splineIkCurve = dynCurve
    return splineIkCurve


def getDynCurve(hairSystem):
    dynCrv = None
    out_attr = '%s.outputHair' % hairSystem
    outputs = cmds.listConnections(out_attr) or []
    if not outputs:
        return None
    follicle = outputs[0]
    dynCrvs = cmds.listConnections('%s.outCurve' % follicle, source=False, destination=True, type='nurbsCurve', shapes=True) or []
    return dynCrvs[0] if dynCrvs else None


def getBakeLocators(dynCrv):
    bakeLocs = []
    pocis = cmds.listConnections('%s.worldSpace' % dynCrv, source=False, destination=True, type='pointOnCurveInfo') or []
    for p in pocis:
        # pointOnCurveInfo.result.position -> connection to transform
        connected = cmds.listConnections('%s.result' % p, source=False, destination=True, type='transform') or []
        if not connected:
            # try result.position attr
            connected = cmds.listConnections('%s.result.position' % p, source=False, destination=True, type='transform') or []
        if connected:
            parent = connected[0]
            # find child transform under that locator
            children = cmds.listRelatives(parent, children=True, type='transform') or []
            if children:
                bakeLocs.append(children[0])
    return bakeLocs


def getIkHandle(splineIkCurve):
    ikHandle = None
    iks = cmds.listConnections('%s.worldSpace' % splineIkCurve, source=False, destination=True, type='ikHandle') or []
    return iks[0] if iks else None


def getControls(dynCrv):
    controls = []
    pntOnCrvInfos = cmds.listConnections(dynCrv, source=False, destination=True, type='pointOnCurveInfo') or []
    for p in pntOnCrvInfos:
        parents = cmds.listConnections(p, source=False, destination=True, type='transform') or []
        if not parents:
            continue
        bakeLocParent = parents[0]
        children = cmds.listRelatives(bakeLocParent, children=True) or []
        if not children:
            continue
        ctrlName = children[0].replace('_bake_loc', '')
        controls.append(ctrlName)
    return controls


def getJoints(splineIkCurve):
    joints = []
    iks = cmds.listConnections(splineIkCurve, source=False, destination=True, type='ikHandle') or []
    if not iks:
        return []
    ikHandle = iks[0]
    startJoints = cmds.listConnections(ikHandle, source=True, destination=False, type='joint') or []
    if not startJoints:
        return []
    startJoint = startJoints[0]
    # get all descendant joints
    joints = cmds.listRelatives(startJoint, ad=True, type='joint') or []
    joints = list(reversed(joints)) + [startJoint]
    return joints


def bakeDynToControllers(bakeLocators):
    minFrame = cmds.playbackOptions(q=True, min=True)
    maxFrame = cmds.playbackOptions(q=True, max=True)

    ctrls = []
    ctrlSpaceLocs = []
    for bakeLoc in bakeLocators:
        ctrl = bakeLoc.split('_bake_loc')[0]
        ctrls.append(ctrl)
        try:
            cmds.matchTransform(ctrl, bakeLoc)
        except Exception:
            pass
        cmds.cutKey(ctrl, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'], clear=True)

        ctrlSpaceLoc = cmds.spaceLocator(name='{}_space_loc'.format(ctrl))[0]
        ctrlSpaceLocs.append(ctrlSpaceLoc)
        cmds.parentConstraint(bakeLoc, ctrlSpaceLoc, mo=False)

    cmds.bakeResults(
        ctrlSpaceLocs,
        simulation=True,
        time=(minFrame, maxFrame),
        sampleBy=1,
        attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'],
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        bakeOnOverrideLayer=False,
        controlPoints=False,
        shape=False
    )

    for ctrlSpaceLoc, ctrl in zip(ctrlSpaceLocs, ctrls):
        cmds.parentConstraint(ctrlSpaceLoc, ctrl, mo=False)
    cmds.bakeResults(
        ctrls,
        simulation=True,
        time=(minFrame, maxFrame),
        sampleBy=1,
        attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'],
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        bakeOnOverrideLayer=False,
        controlPoints=False,
        shape=False
    )
    cmds.delete(ctrlSpaceLocs)

def bakeDynToJoints(joints, endCtrs=[]):
    minFrame = cmds.playbackOptions(q=True, min=True)
    maxFrame = cmds.playbackOptions(q=True, max=True)

    cmds.bakeResults(
        joints,
        simulation=True,
        time=(minFrame, maxFrame),
        sampleBy=1,
        attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'],
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        bakeOnOverrideLayer=False,
        controlPoints=False,
        shape=False
    )

    if endCtrs:
        for endCtr in endCtrs:
            endCtr.bakeType.set(0)
            endCtr.IkBlend.set(0)


def deleteKeys(objects):
    if not objects:
        cmds.error('There is no transform to delete keys')
    cmds.select(objects, r=True)
    mel.eval('DeleteKeys;')
    cmds.select(clear=True)


def getIhHairchainData(endCtrs):
    ihHairchainData = {'ctrList': [], 'bakeCtrList': [], 'bakeOutList': [], 'jointList': []}
    for ctr in endCtrs:
        prefix = ctr.replace('_ctrEnd_crv', '')
        ihHairchainData['ctrList'].extend(cmds.ls(prefix + '_ctr*_crv') or [])
        ihHairchainData['bakeCtrList'].extend(cmds.ls(prefix + '_bake*_crv') or [])
        ihHairchainData['bakeOutList'].extend(cmds.ls(prefix + '_bakeOut*_jnt', type='joint') or [])
        ihHairchainData['jointList'].extend(cmds.ls(prefix + '_*_jnt', type='joint') or [])
    return ihHairchainData


def bakeIhHairchainControl(ihHairchainData):
    cmds.cutKey(ihHairchainData['ctrList'], attribute=['tx', 'ty', 'tz'], clear=True)

    for bakeCtr in ihHairchainData['bakeCtrList']:
        bakeCtrZero = bakeCtr.replace('_crv', '_zero')
        ctrZero = bakeCtrZero.replace('_bake', '_ctr')
        pc = cmds.parentConstraint(ctrZero, bakeCtrZero, mo=False)
        cmds.delete(pc)
        pc2 = cmds.pointConstraint(bakeCtr.replace('_bake', '_ctr'), bakeCtr, mo=False)
        cmds.delete(pc2)

    pntConstraints = []
    for bakeOut in ihHairchainData['bakeOutList']:
        bakeCtr = bakeOut.replace('_bakeOut', '_bake').replace('_jnt', '_crv')
        pntConstraints.append(cmds.pointConstraint(bakeOut, bakeCtr, mo=True))

    minFrame = cmds.playbackOptions(q=True, min=True)
    maxFrame = cmds.playbackOptions(q=True, max=True)
    cmds.bakeResults(
        ihHairchainData['bakeCtrList'],
        simulation=True,
        time=(minFrame, maxFrame),
        sampleBy=1,
        attribute=['tx', 'ty', 'tz'],
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        bakeOnOverrideLayer=False,
        controlPoints=False,
        shape=False
        )
    cmds.delete(pntConstraints)

    for bakeCtr in ihHairchainData['bakeCtrList']:
        ctr = bakeCtr.replace('_bake', '_ctr')
        cmds.cutKey(bakeCtr, time=':', attribute=['tx', 'ty', 'tz'], hierarchy='none')
        try:
            cmds.pasteKey(ctr, option='insert', copies=1, connect=True, timeOffset=0, floatOffset=0, valueOffset=0)
        except Exception:
            pass


def bakeIhHairchainJoint(joints, endCtrs):
    try:
        cmds.bakeResults()
    except Exception:
        pass


class DynamicSplineBaker(object):
    name = 'dynSplineBaker'

    # Attributes
    bakeType = ['Controller', 'Joint']
    namespaceMenu = None
    solverTxtScrlList = None
    dynCtrlsTxtScrlList = None
    bakeTypeMenu = None
    dynOnOffBtn = None
    objects = []

    def __init__(self):
        super(DynamicSplineBaker, self).__init__()

        if cmds.window(DynamicSplineBaker.name, q=True, exists=True):
            cmds.deleteUI(DynamicSplineBaker.name)

        win = cmds.window(DynamicSplineBaker.name, title='Dynamic Spline Baker', mnb=False, mxb=False)

        cmds.tabLayout(tabsVisible=False)
        cmds.columnLayout(adj=True, rowSpacing=5)
        self.namespaceMenu = cmds.optionMenu(label='Namespace: ', changeCommand=lambda item: self.populateDynPartsTxtScrlList(item))

        cmds.separator(style='in', h=3)

        cmds.rowColumnLayout(numberOfColumns=3, columnSpacing=[(2, 5), (3, 5)], columnWidth=[(1,150), (2,150)])

        cmds.columnLayout(adj=True, rowSpacing=5, columnAlign='left')
        cmds.text(label='Solvers')
        self.solverTxtScrlList = cmds.textScrollList(selectCommand=lambda *a: self.populateDynCtrlsTxtScrlList())

        cmds.setParent('..')
        cmds.columnLayout(adj=True, rowSpacing=5, columnAlign='left')
        cmds.text(label='Dynamic Controllers')
        self.dynCtrlsTxtScrlList = cmds.textScrollList(allowMultiSelection=True, selectCommand=lambda *a: self.selectDynCtrls())
        cmds.popupMenu()
        cmds.menuItem(label='Select All Controllers', command=lambda *a: self.selectAllDynCtrls())

        cmds.setParent('..')
        cmds.columnLayout(adj=True, rowSpacing=5)
        cmds.separator(h=10, style='none')
        self.dynOnOffBtn = cmds.button(label='Dynamic On/Off', command=lambda *a: self.dynOnOff())
        cmds.rowColumnLayout(numberOfColumns=2)

        cmds.setParent('..')
        self.bakeTypeMenu = cmds.optionMenu(label='Bake Type: ')
        cmds.menuItem(label='Controller')
        cmds.menuItem(label='Joint')
        cmds.separator(h=10, style='in')
        cmds.button(label='Bake Dynamic', height=70, command=lambda *a: self.bakeDynamic(cmds.optionMenu(self.bakeTypeMenu, q=True, value=True)))
        cmds.button(label='Delete Keys', command=lambda *a: self.delKeys())
        cmds.button(label='Reset Controls', command=lambda *a: self.resetControls())

        cmds.window(win, edit=True, widthHeight=(300,200))
        cmds.showWindow(win)

        self.buildObjects()
        self.populateNamespaceMenu()
        self.populateDynPartsTxtScrlList(cmds.optionMenu(self.namespaceMenu, q=True, value=True))

    def buildObjects(self):
        namespaces = []
        defaultNamespaces = set(['UI', 'shared'])
        namespaces = list(set(cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []) - defaultNamespaces)
        if not namespaces:
            all_nucleus = cmds.ls(type='nucleus') or []
            hairChainNucleuses = [n for n in all_nucleus if getHairSystems(n)]
            if hairChainNucleuses:
                self.objects.append({'namespace': ':', 'nucleuses': hairChainNucleuses})
        for namespace in namespaces:
            items = cmds.namespaceInfo(namespace, listOnlyDependencyNodes=True) or []
            nucleuses = [item for item in items if cmds.nodeType(item) == 'nucleus']
            hairChainNucleuses = [nucleus for nucleus in nucleuses if getHairSystems(nucleus)]
            if hairChainNucleuses:
                self.objects.append({'namespace': namespace, 'nucleuses': hairChainNucleuses})

    def populateNamespaceMenu(self):
        for obj in self.objects:

            cmds.menuItem(label=obj['namespace'], parent=self.namespaceMenu)

    def populateDynPartsTxtScrlList(self, namespace):
        cmds.textScrollList(self.solverTxtScrlList, e=True, removeAll=True)
        for obj in self.objects:
            if namespace == obj['namespace']:
                for nucleus in obj['nucleuses']:
                    cmds.textScrollList(self.solverTxtScrlList, e=True, append=nucleus.replace(namespace+':', ''))

    def populateDynCtrlsTxtScrlList(self, *args):
        namespace = cmds.optionMenu(self.namespaceMenu, q=True, value=True)
        cmds.textScrollList(self.dynCtrlsTxtScrlList, e=True, removeAll=True)
        sel = cmds.textScrollList(self.solverTxtScrlList, q=True, selectItem=True) or []
        nucleus = namespace + ':' + sel[0]

        dyn_ctrl = list(set(cmds.listConnections(nucleus, source=True, destination=False, type='transform') or []))
        if dyn_ctrl:
            cmds.select(dyn_ctrl, r=True)

        enableAttr, startFrameAttr = getNucleusControllerAttributes(nucleus)
        try:
            cmds.cutKey(enableAttr, clear=True)
        except Exception:
            pass
        try:
            cmds.cutKey(startFrameAttr, clear=True)
        except Exception:
            pass

        self.updateDynOfOffBtn()

        dynCtrls = []
        hairSystems = getHairSystems(nucleus)
        for hairSystem in hairSystems:
            try:  # In case JH Hairchain Rig or TAK's spline rig
                splineIkCurve = getSplineIkCurve(hairSystem)
                joints = sorted(getJoints(splineIkCurve))
                vis_conn = cmds.listConnections('%s.visibility' % joints[0], source=False, destination=True, type='transform') or []
                if vis_conn:
                    dynCtrls.append(vis_conn[0])
            except:  # In case IH Hairchain Rig
                s = cmds.listConnections('%s.startCurveAttract' % hairSystem, source=True, destination=False, type='transform') or []
                if s:
                    dynCtrls.append(s[0])

        for dynCtrl in dynCtrls:
            cmds.textScrollList(self.dynCtrlsTxtScrlList, e=True, append=dynCtrl.replace(namespace+':', ''))

    def dynOnOff(self, *args):
        namespace = cmds.optionMenu(self.namespaceMenu, q=True, value=True)
        sel = cmds.textScrollList(self.solverTxtScrlList, q=True, selectItem=True) or []
        nucleus = namespace + ':' + sel[0]
        enableAttr, startFrameAttr = getNucleusControllerAttributes(nucleus)
        try:
            enabled = cmds.getAttr(enableAttr)
        except Exception:
            enabled = None
        hairSystem = getHairSystems(nucleus)[0]
        end_items = cmds.textScrollList(self.dynCtrlsTxtScrlList, q=True, allItems=True) or []
        endCtrs = [namespace + ':' + ctr for ctr in end_items]
        try:
            sim_method = cmds.getAttr('%s.simulationMethod' % hairSystem)
        except Exception:
            sim_method = None
        if enabled and sim_method == 3:
            try:
                cmds.setAttr(enableAttr, False)
            except Exception:
                pass
            try:
                cmds.setAttr(startFrameAttr, 100000)
            except Exception:
                pass
            cmds.button(self.dynOnOffBtn, edit=True, bgc=(0.75, 0.25, 0.0), label='Dynamic Off')
            if endCtrs:
                try:
                    if cmds.attributeQuery('dynamicType', node=endCtrs[0], exists=True):
                        cmds.setAttr('%s.dynamicType' % endCtrs[0], 0)
                except Exception:
                    pass
            for endCtr in endCtrs:
                try:
                    if cmds.attributeQuery('Constraint', node=endCtr, exists=True):
                        try:
                            cmds.cutKey('%s.Constraint' % endCtr, clear=True)
                        except Exception:
                            pass
                        cmds.setAttr('%s.Constraint' % endCtr, 1)
                except Exception:
                    pass
        else:
            try:
                cmds.setAttr(enableAttr, True)
            except Exception:
                pass
            try:
                cmds.setAttr(startFrameAttr, cmds.playbackOptions(q=True, min=True))
            except Exception:
                pass
            cmds.button(self.dynOnOffBtn, edit=True, bgc=(0.0, 0.75, 0.25), label='Dynamic On')
            if endCtrs:
                try:
                    if cmds.attributeQuery('dynamicType', node=endCtrs[0], exists=True):
                        cmds.setAttr('%s.dynamicType' % endCtrs[0], 2)
                except Exception:
                    pass
            for endCtr in endCtrs:
                try:
                    if cmds.attributeQuery('Constraint', node=endCtr, exists=True):
                        try:
                            cmds.cutKey('%s.Constraint' % endCtr, clear=True)
                        except Exception:
                            pass
                        cmds.setAttr('%s.Constraint' % endCtr, 0)
                except Exception:
                    pass

    def updateDynOfOffBtn(self):
        namespace = cmds.optionMenu(self.namespaceMenu, q=True, value=True)
        sel = cmds.textScrollList(self.solverTxtScrlList, q=True, selectItem=True) or []
        nucleus = namespace + ':' + sel[0]
        enableAttr, startFrameAttr = getNucleusControllerAttributes(nucleus)
        try:
            enabled = cmds.getAttr(enableAttr)
        except Exception:
            enabled = None
        hairSystem = getHairSystems(nucleus)[0]
        try:
            sim_method = cmds.getAttr('%s.simulationMethod' % hairSystem)
        except Exception:
            sim_method = None
        if enabled and sim_method == 3:
            cmds.button(self.dynOnOffBtn, edit=True, bgc=(0.0, 0.75, 0.25), label='Dynamic On')
        else:
            cmds.button(self.dynOnOffBtn, edit=True, bgc=(0.75, 0.25, 0.0), label='Dynamic Off')

    def selectDynCtrls(self):
        namespace = cmds.optionMenu(self.namespaceMenu, q=True, value=True)
        sel = cmds.textScrollList(self.dynCtrlsTxtScrlList, q=True, selectItem=True) or []
        dynCtrls = [namespace + ':' + ctrl for ctrl in sel]
        if dynCtrls:
            cmds.select(dynCtrls, r=True)

    def selectAllDynCtrls(self, *args):
        namespace = cmds.optionMenu(self.namespaceMenu, q=True, value=True)
        all_items = cmds.textScrollList(self.dynCtrlsTxtScrlList, q=True, allItems=True) or []
        allDynCtrls = [namespace + ':' + ctrl for ctrl in all_items]
        cmds.textScrollList(self.dynCtrlsTxtScrlList, e=True, selectItem=all_items)
        if allDynCtrls:
            cmds.select(allDynCtrls, r=True)

    def bakeDynamic(self, bakeType):
        namespace = cmds.optionMenu(self.namespaceMenu, q=True, value=True)
        sel = cmds.textScrollList(self.solverTxtScrlList, q=True, selectItem=True) or []
        nucleus = namespace + ':' + sel[0]

        enableAttr, startFrameAttr = getNucleusControllerAttributes(nucleus)
        try:
            cmds.setAttr(enableAttr, True)
        except Exception:
            pass
        cmds.button(self.dynOnOffBtn, edit=True, bgc=(0.0, 0.75, 0.25), label='Dynamic On')
        try:
            cmds.setAttr(startFrameAttr, cmds.playbackOptions(q=True, min=True))
        except Exception:
            pass
        end_items = cmds.textScrollList(self.dynCtrlsTxtScrlList, q=True, allItems=True) or []
        endCtrs = [namespace + ':' + ctr for ctr in end_items]
        if endCtrs:
            try:
                if cmds.attributeQuery('dynamicType', node=endCtrs[0], exists=True):
                    cmds.setAttr('%s.dynamicType' % endCtrs[0], 2)
            except Exception:
                pass
        for endCtr in endCtrs:
            try:
                if cmds.attributeQuery('Constraint', node=endCtr, exists=True):
                    try:
                        cmds.cutKey('%s.Constraint' % endCtr, clear=True)
                    except Exception:
                        pass
                    cmds.setAttr('%s.Constraint' % endCtr, 0)
            except Exception:
                pass

        hairSystems = getHairSystems(nucleus)
        allJoints = []
        allBakeLocs = []
        for hairSystem in hairSystems:
            try:  # In case JH Hairchain Rig or TAK's spline rig
                splineIkCurve = getSplineIkCurve(hairSystem)
                dynCrv = getDynCurve(hairSystem)
                allJoints.extend(getJoints(splineIkCurve))
                if bakeType == 'Controller':
                    allBakeLocs.extend(getBakeLocators(dynCrv))
            except:  # In case IH Hairchain Rig
                break

        try:  # In case JH Hairchain Rig or TAK's spline rig
            try:
                cmds.refresh(suspend=True)
            except Exception:
                pass
            bakeDynToControllers(allBakeLocs) if bakeType == 'Controller' else bakeDynToJoints(allJoints)
            try:
                cmds.refresh(suspend=False)
            except Exception:
                pass
        except:  # In case IH Hairchain Rig
            for endCtr in endCtrs:
                try:
                    if cmds.attributeQuery('Constraint', node=endCtr, exists=True):
                        try:
                            cmds.setAttr('%s.Constraint' % endCtr, 0)
                        except Exception:
                            pass
                except Exception:
                    pass
            ihHairchainData = getIhHairchainData(endCtrs)
            bakeIhHairchainControl(ihHairchainData) if bakeType == 'Controller' else bakeDynToJoints(ihHairchainData['jointList'], endCtrs)
            if endCtrs:
                try:
                    if cmds.attributeQuery('dynamicType', node=endCtrs[0], exists=True):
                        cmds.setAttr('%s.dynamicType' % endCtrs[0], 0)
                except Exception:
                    pass

        enableAttr, startFrameAttr = getNucleusControllerAttributes(nucleus)
        try:
            cmds.setAttr(enableAttr, False)
        except Exception:
            pass
        try:
            cmds.setAttr(startFrameAttr, 100000)
        except Exception:
            pass
        self.updateDynOfOffBtn()

    def delKeys(self, *args):
        namespace = cmds.optionMenu(self.namespaceMenu, q=True, value=True)
        sel = cmds.textScrollList(self.solverTxtScrlList, q=True, selectItem=True) or []
        nucleus = namespace + ':' + sel[0]
        allJoints = []
        allControls = []
        allIkHandles = []
        hairSystems = getHairSystems(nucleus)
        for hairSystem in hairSystems:
            try:  # In case JH Hairchain Rig or TAK's spline rig
                splineIkCurve = getSplineIkCurve(hairSystem)
                allJoints.extend(getJoints(splineIkCurve))
                allIkHandles.append(getIkHandle(splineIkCurve))
                allControls.extend(getControls(getDynCurve(hairSystem)))
            except:  # In case IH Hairchain Rig
                break

        try:  # In case JH Hairchain Rig or TAK's spline rig
            deleteKeys(allControls)
            deleteKeys(allJoints)
            for ikHandle in allIkHandles:
                try:
                    cmds.setAttr('%s.ikBlend' % ikHandle, 1)
                except Exception:
                    pass
        except:  # In case IH Hairchain Rig
            end_items = cmds.textScrollList(self.dynCtrlsTxtScrlList, q=True, allItems=True) or []
            endCtrs = [namespace + ':' + ctr for ctr in end_items]
            ihHairchainData = getIhHairchainData(endCtrs)
            deleteKeys(ihHairchainData['ctrList'])
            deleteKeys(ihHairchainData['jointList'])
            for endCtr in endCtrs:
                try:
                    cmds.setAttr('%s.bakeType' % endCtr, 0)
                except Exception:
                    pass
                try:
                    cmds.setAttr('%s.IkBlend' % endCtr, 1)
                except Exception:
                    pass

    def resetControls(self, *args):
        namespace = cmds.optionMenu(self.namespaceMenu, q=True, value=True)
        sel = cmds.textScrollList(self.solverTxtScrlList, q=True, selectItem=True) or []
        nucleus = namespace + ':' + sel[0]
        allControls = []
        hairSystems = getHairSystems(nucleus)
        for hairSystem in hairSystems:
            try:  # In case JH Hairchain Rig or TAK's spline rig
                allControls.extend(getControls(getDynCurve(hairSystem)))
            except:  # In case IH Hairchain Rig
                break

        attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        try:  # In case JH Hairchain Rig or TAK's spline rig
            for ctrl in allControls:
                for attr in attrs:
                    try:
                        cmds.setAttr('%s.%s' % (ctrl, attr), 0)
                    except Exception:
                        pass
        except:  # In case IH Hairchain Rig
            end_items = cmds.textScrollList(self.dynCtrlsTxtScrlList, q=True, allItems=True) or []
            endCtrs = [namespace + ':' + ctr for ctr in end_items]
            ihHairchainData = getIhHairchainData(endCtrs)
            for ctr in ihHairchainData['ctrList']:
                for attr in attrs:
                    try:
                        cmds.setAttr('%s.%s' % (ctr, attr), 0)
                    except Exception:
                        pass
