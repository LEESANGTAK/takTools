import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


mel.eval('source channelBoxCommand;')
mel.eval('source cleanUpScene;')


def ui():
    winName = 'cleanUpRigWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)
    if cmds.window('ripGrpWin', exists=True):
        cmds.deleteUI('ripGrpWin')

    cmds.window(winName, title='Clean Up Rig', mnb=False, mxb=False)

    cmds.columnLayout('mainColLo', p=winName, adj=True)

    cmds.button(label="Tag Working Data", c=tagWorkingData)
    cmds.button(label="Delete Working Data", c=deleteWorkingData)
    cmds.button(label="Delete unused shading nodes.", c=deleteUnusedShadingNodes)
    cmds.separator(h=5, style='in')
    cmds.button(label="Add Selected or rigGeo and Model to 'geo_layer'", c=addGeoLayer,
                annotation='Add selected geometries to the geo_layer.')
    cmds.button(label="Remove Unused Influences in 'geo_layer'", c=rmvUnuseInf)
    cmds.button(label='Visibility Attributes Set Up on Selected Control', c=visCtrl)
    cmds.text(label="# Publish custom attributes(blendshape, texture) to skeleton root.")
    cmds.separator(h=5, style='in')
    cmds.button(label="Lock Geometry Transform", c=lockGeoTransforms)
    cmds.button(label="Delete Display/Render/Animation Layers", c=delAllLayers)
    cmds.button(label="Delete Keys", c=delKeys)
    cmds.button(label="Check Namespace", c=chkNamespace)
    cmds.button(label="Hide Joints", c=hideJoints)
    cmds.button(label='Remove Unused Animation Curves', c='''mel.eval('deleteUnusedCommon("animCurve", 0, uiRes("m_cleanUpScene.kDeletingUnusedAnimationCurves2"));')''')
    cmds.button(label="All in One", c=allInOne, h=40, bgc=[0, 0.5, 0.5])

    cmds.window(winName, e=True, w=200, h=50)
    cmds.showWindow(winName)


def addGeoLayer(*args):
    sels = pm.selected()

    if not pm.objExists('geo_layer'):
        geoLayer = pm.createNode('displayLayer', n='geo_layer')
    else:
        geoLayer = pm.PyNode('geo_layer')

    meshes = []
    for sel in sels:
        meshes.extend([mesh.getTransform() for mesh in pm.ls(sel, dag=True, type='mesh')])

    if meshes:
        geoLayer.addMembers(meshes)


def visCtrl(*args):
    '''
    Set up visibility control for the rig.
    '''

    visCtrl = cmds.ls(sl=True)[0]

    # Check if attributes exists
    visAttrDic = {'geometryVis': ['enum', 'Normal', 'Template', 'Reference']}

    for visAttr in visAttrDic.keys():
        if cmds.objExists('%s.%s' % (visCtrl, visAttr)):
            continue
        else:
            if visAttrDic[visAttr][0] == 'enum':
                joinStr = ':'
                cmds.addAttr(visCtrl, ln=visAttr, at=visAttrDic[visAttr][0], en=joinStr.join(visAttrDic[visAttr][1:]))
                cmds.setAttr('%s.%s' % (visCtrl, visAttr), channelBox=True)
            elif visAttrDic[visAttr][0] == 'bool':
                if visAttr == 'modelVis':
                    cmds.addAttr(visCtrl, ln=visAttr, at=visAttrDic[visAttr][0], keyable=False)
                    if cmds.objExists('lod01_GRP'):
                        models = cmds.listRelatives('lod01_GRP')
                        if models:
                            for model in models:
                                cmds.connectAttr('%s.%s' % (visCtrl, visAttr), '%s.visibility' % model, f=True)

                    if cmds.objExists('lod02_GRP'):
                        models = cmds.listRelatives('lod02_GRP')
                        for model in models:
                            cmds.connectAttr('%s.%s' % (visCtrl, visAttr), '%s.visibility' % model, f=True)
                    else:
                        models = cmds.listRelatives('lod03_GRP')
                        for model in models:
                            cmds.connectAttr('%s.%s' % (visCtrl, visAttr), '%s.visibility' % model, f=True)
                else:
                    cmds.addAttr(visCtrl, ln=visAttr, at=visAttrDic[visAttr][0])
                    cmds.setAttr('%s.%s' % (visCtrl, visAttr), channelBox=True)

    # Connect attributes
    if not cmds.isConnected('%s.geometryVis' % visCtrl, 'geo_layer.displayType'):
        cmds.connectAttr('%s.geometryVis' % visCtrl, 'geo_layer.displayType', f=True)
    if cmds.objExists('facial_gui_grp'):
        if not cmds.isConnected('%s.facialControlVis' % visCtrl, 'facial_gui_grp.visibility'):
            cmds.connectAttr('%s.facialControlVis' % visCtrl, 'facial_gui_grp.visibility', f=True)
    if cmds.objExists('extra_ctrl_grp'):
        if not cmds.isConnected('%s.extraControlVis' % visCtrl, 'extra_ctrl_grp.visibility'):
            cmds.connectAttr('%s.extraControlVis' % visCtrl, 'extra_ctrl_grp.visibility', f=True)
    if cmds.objExists('floorContactCheck_geo'):
        if not cmds.isConnected('%s.floorContactCheckVis' % visCtrl, 'floorContactCheck_geo.visibility'):
            cmds.connectAttr('%s.floorContactCheckVis' % visCtrl, 'floorContactCheck_geo.visibility', f=True)

    # LOD visibility control setup
    if cmds.objExists('lod01_GRP'):
        mel.eval('CBdeleteConnection "lod01_GRP.visibility"')
    if cmds.objExists('lod02_GRP'):
        mel.eval('CBdeleteConnection "lod02_GRP.visibility"')
    if cmds.objExists('lod03_GRP'):
        mel.eval('CBdeleteConnection "lod03_GRP.visibility"')

    if cmds.objExists('lod02_GRP') and cmds.objExists('lod01_GRP'):
        cmds.setDrivenKeyframe('lod01_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=1)
        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=0)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=0)

        cmds.setDrivenKeyframe('lod01_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=0)
        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=1)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=0)

        cmds.setDrivenKeyframe('lod01_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=0)
        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=0)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=1)

    elif cmds.objExists('lod02_GRP') and not cmds.objExists('lod01_GRP'):
        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=0)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=0, v=0)

        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=1)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=1, v=0)

        cmds.setDrivenKeyframe('lod02_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=0)
        cmds.setDrivenKeyframe('lod03_GRP.visibility', cd='%s.lodVis' % visCtrl, dv=2, v=1)

    elif cmds.objExists('lod02_GRP') and not cmds.objExists('lod01_GRP'):
        pass

    # Dynamic control visibility setup
    if cmds.objExists('dyn_ctr_crv'):
        if cmds.objExists('dyn_ctr_crv.clothSolverOnOff') and cmds.objExists('dyn_ctr_crv.hairSolverOnOff'):
            dynExprStr = '''
            // Expression for Dynamic Visibility //
            string $clothSolverState = dyn_ctr_crv.clothSolverOnOff;
            string $hairSolverState = dyn_ctr_crv.hairSolverOnOff;

            if (($hairSolverState == 1) || ($clothSolverState == 1)){
                geometry.visibility = 0;
                Geometry.visibility = 0;
            }
            else if (($hairSolverState == 0) && ($clothSolverState == 0)){
                geometry.visibility = 1;
                Geometry.visibility = 1;
            }
            '''
            cmds.expression(s=dynExprStr, ae=True, uc='all', n='dynVis_expr')

    # Turn off smooth preview for low poly group.
    if cmds.objExists('Geometry'):
        cmds.select("Geometry", r=True)
        mel.eval('setDisplaySmoothness 1;')

    cmds.select(visCtrl, r=True)


def rmvUnuseInf(*args):
    '''
    Remove unused skin influences for skin geometries.
    '''

    for shp in cmds.editDisplayLayerMembers('geo_layer', q=True):
        allDefSets = cmds.listSets(object=shp, type=2, extendToShape=True)
        if 'skinCluster' in str(allDefSets):
            cmds.select(shp, r=True)
            mel.eval('RemoveUnusedInfluences;')


def chkNamespace(*args):
    '''
    Check unused namespace.
    '''

    namespaceList = cmds.namespaceInfo(lon=True)
    ignoreNamespaces = ['UI', 'shared']
    for _namespace in namespaceList:
        if not _namespace in ignoreNamespaces:
            cmds.NamespaceEditor()
            break


def isDeformed(geometry):
    geo = pm.PyNode(geometry)
    shapes = geo.getShapes()
    for shape in shapes:
        if shape.isIntermediateObject():
            return True
    return False

def lockGeoTransforms():
    meshePaths = cmds.ls(type='mesh', long=True)
    transforms = []
    for meshPath in meshePaths:
        meshTransform = meshPath.split('|')[-2]
        if isDeformed(meshTransform):
            meshParents = meshPath.split('|')[:-1]
            for meshParent in meshParents:
                try:
                    if cmds.objectType(meshParent) == 'transform':
                        transforms.append(meshParent)
                except:
                    pass
    geoTransforms = list(set(transforms))
    for geoTransform in geoTransforms:
        geoTransform = pm.PyNode(geoTransform)
        geoTransform.translate.lock()
        geoTransform.rotate.lock()
        geoTransform.scale.lock()


def delKeys(*args):
    ctrls = []

    cmds.currentTime(0)

    advancedSkeletonControllerSet = 'ControlSet'
    if cmds.objExists(advancedSkeletonControllerSet):
        asCtrls = cmds.select(cmds.sets(advancedSkeletonControllerSet, q=True), r=True)
        ctrls.append(asCtrls)

    for crv in cmds.ls(type='nurbsCurve'):
        crvTransform = cmds.listRelatives(crv, parent=True)[0]
        ctrls.append(crvTransform)

    cmds.select(ctrls)
    mel.eval('doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","0","animationList","0","noOptions","0","0" };')

    cmds.select(cl=True)


def hideJoints(*args):
    '''
    Hide all joints in current scene.
    '''

    jntLs = cmds.ls(type='joint')
    for jnt in jntLs:
        cmds.setAttr('%s.drawStyle' % jnt, 2)


def delAllLayers(*args):
    # cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')
    disLayList = cmds.ls(type='displayLayer')
    renLayList = cmds.ls(type='renderLayer')
    aniLyrLs = cmds.ls(type='animLayer')

    for disLay in disLayList:
        if disLay in ['defaultLayer', 'geo_layer', 'jointLayer']:
            pass
        else:
            cmds.delete(disLay)

    # for renLay in renLayList:
    #     if renLay != 'defaultRenderLayer':
    #         cmds.delete(renLay)

    for aniLyr in aniLyrLs:
        if aniLyr == 'BaseAnimation':
            cmds.delete(aniLyr)



def tagWorkingData(*args):
    for sel in pm.selected():
        pm.addAttr(sel, ln='K_tag', dt='string')
        sel.K_tag.set('workingData')


def deleteUnusedShadingNodes(*args):
    pm.mel.hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")


def deleteWorkingData(*args):
    tagAttrs = pm.ls('*.K_tag')
    for tagAttr in tagAttrs:
        if tagAttr.get() == 'workingData':
            pm.delete(tagAttr.node())


def turnOffVisMiscNodes():
    # Turn off visibility of place3dTexture nodes.
    plc3dTexLs = cmds.ls(type='place3dTexture')
    for plc3dTex in plc3dTexLs:
        try:
            cmds.setAttr(plc3dTex + '.visibility', 0)
        except:
            pass

    # Turn off visibility of nucleus nodes.
    nclsLs = cmds.ls(type='nucleus')
    for ncls in nclsLs:
        cmds.setAttr('%s.visibility' % ncls, False)


def setVisCtrlAttrs():
    visCtrl = cmds.ls('*.geometryVis')
    if visCtrl:
        visCtrl = visCtrl[0].split('.')[0]
        if cmds.objExists(visCtrl + '.facialControlVis'): cmds.setAttr(visCtrl + '.facialControlVis', 1)
        if cmds.objExists(visCtrl + '.extraControlVis'): cmds.setAttr(visCtrl + '.extraControlVis', 1)
        if cmds.objExists(visCtrl + '.footDummyVis'): cmds.setAttr(visCtrl + '.footDummyVis', 1)
        if cmds.objExists(visCtrl + '.geometryVis'): cmds.setAttr(visCtrl + '.geometryVis', 2)
        if cmds.objExists(visCtrl + '.lodVis'): cmds.setAttr(visCtrl + '.lodVis', 1)
        if cmds.objExists(visCtrl + '.correctiveCtrlVis'): cmds.setAttr(visCtrl + '.correctiveCtrlVis', 0)

    globalScaleCtrl = cmds.ls('*.DefaultScale')
    if globalScaleCtrl:
        globalScaleCtrl = globalScaleCtrl[0].split('.')[0]
        try:
            if cmds.objExists(globalScaleCtrl + '.DefaultScale'): cmds.setAttr(globalScaleCtrl + '.DefaultScale', 0, lock=True)
        except:
            pass


def createControllerNodesSet():
    ctrlNodesSetName = 'controllerNodes_set'
    if not pm.objExists(ctrlNodesSetName):
        ctrlNodesSet = pm.createNode('objectSet', n=ctrlNodesSetName)
    else:
        ctrlNodesSet = pm.PyNode(ctrlNodesSetName)

    ctrlNodes = pm.ls(type='controller')
    ctrlNodesSet.addMembers(ctrlNodes)

    advancedSkelSetName = 'Sets'
    if pm.objExists(advancedSkelSetName):
        pm.PyNode(advancedSkelSetName).addMember(ctrlNodesSet)

def allInOne(*args):
    """ Preprocess to publish rig """

    if cmds.objExists('Sets'):
        mel.eval('source "C:/GoogleDrive/programs_env/maya/modules/AdvancedSkeleton5/AdvancedSkeleton5Files/Selector/biped.mel";')
        if cmds.objExists('MotionSystem'):
            cmds.setAttr('MotionSystem.v', True)

    lockGeoTransforms()
    delAllLayers()
    delKeys()
    chkNamespace()
    hideJoints()
    mel.eval('deleteUnusedCommon("animCurve", 0, uiRes("m_cleanUpScene.kDeletingUnusedAnimationCurves2"));')

    setVisCtrlAttrs()
    turnOffVisMiscNodes()
    createControllerNodesSet()

    # Set dynamic control's start frame attributes value to 100000.
    if cmds.objExists('dyn_ctrl'):
        cmds.select('dyn_ctrl')
        dynCtrl = cmds.ls(sl=True)[0]
        udAttrs = cmds.listAttr(dynCtrl, ud=True)
        for attr in udAttrs:
            if 'enable' in attr:
                cmds.setAttr('%s.%s' % (dynCtrl, attr), False)
            if 'startFrame' in attr or 'StartFrame' in attr:
                cmds.setAttr('%s.%s' % (dynCtrl, attr), 100000)
