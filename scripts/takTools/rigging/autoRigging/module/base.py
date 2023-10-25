import pymel.core as pm

from ..base import controller


def build(model=None, skeleton=None, zAxisUp=True, controlShape='pentagon', rootControl=False):
    allGrp = pm.group(empty=True, n='all')
    meshesGrp = pm.group(empty=True, n='meshes')
    rigGrp = pm.group(empty=True, n='rig')
    geometryGrp = pm.group(empty=True, n='geometry')
    skelGrp = pm.group(empty=True, n='skeleton')
    skelGrp.inheritsTransform.set(False)
    skelGrp.inheritsTransform.lock()
    channels = ['translate', 'rotate', 'scale']
    axes = ['X', 'Y', 'Z']
    for channel in channels:
        for axis in axes:
            skelGrp.attr(channel+axis).lock()
            skelGrp.attr(channel+axis).setKeyable(False)

    modluesGrp = pm.group(empty=True, n='modules')

    rootJnt = pm.createNode('joint', n='root')
    if zAxisUp:
        rootJnt.jointOrientX.set(-90)

    mainCtrl = controller.Controller('main_ctrl', shape=controlShape, color='darkBlue', scale=10)
    mainCtrl.createGroups()
    mainCtrl.lockHide(['scale'], ['X', 'Y', 'Z'])
    globalCtrl = controller.Controller('global_ctrl', shape=controlShape, color='yellow', scale=12)
    globalCtrl.createGroups()

    pm.scaleConstraint(mainCtrl.transform, rootJnt)

    pm.parent(skelGrp, modluesGrp, mainCtrl.transform)
    pm.parent(mainCtrl.spaceGrp, globalCtrl.transform)
    pm.parent(globalCtrl.spaceGrp, geometryGrp, rigGrp)
    pm.parent(meshesGrp, rigGrp, allGrp)
    pm.parent(rootJnt, skelGrp)

    # Root control
    if rootControl:
        rootCtrl = controller.Controller('root_ctrl', shape=controlShape, color='green', scale=14)
        rootCtrl.createGroups()
        pm.parent(rootCtrl.spaceGrp, rigGrp)
        if zAxisUp:
            rootCtrl.spaceGrp.rotateX.set(-90)
            rootCtrl.rotate(90)
        rootCtrl.connectTo(rootJnt, parent=True)
    else:
        mainCtrl.connectTo(rootJnt, parent=True)

    if model:
        pm.parent(model, meshesGrp)
    if skeleton:
        for skel in skeleton:
            pm.parent(skel, rootJnt)
