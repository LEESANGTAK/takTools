from maya import cmds, mel


MENU_NAME = 'takToolsMenu'


def showMenu():
    if cmds.menu(MENU_NAME, q=True, ex=True):
        cmds.deleteUI(MENU_NAME)

    mayaWindow = mel.eval("$retvalue = $gMainWindow;")
    customMenu = cmds.menu(MENU_NAME, label="Tak Tools", parent=mayaWindow)

    cmds.menuItem(
        label="Custom Shelf",
        command="import takTools.tak_tools as tt\nimport imp;imp.reload(tt)\ntt.UI()",
        sourceType="python",
        parent=customMenu
    )

    ### Display Menu ###
    cmds.menuItem(label="Display", subMenu=True, to=True, parent=customMenu)
    cmds.menuItem(label="Toggle Wire", command="")
    cmds.menuItem(label="Toggle X-Ray for Selection", command="")

    ### Modeling Menu ###
    cmds.menuItem(label="Modeling", subMenu=True, to=True, parent=customMenu)
    cmds.menuItem(
        label="Clean Model",
        image="cleanUpMesh.bmp",
        command="import takTools.modeling.tak_cleanUpModel as tak_cleanUpModel\nimport imp;imp.reload(tak_cleanUpModel)\ntak_cleanUpModel.UI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="XGen Manager",
        image="xgenManager.png",
        command="import takXgenManager.xgenManager as xgm\nimport imp;imp.reload(xgm)\nxgm.XGenManager.showUI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="spPaint3d",
        image="spPaint3d.bmp",
        command="spPaint3d;",
        sourceType="mel"
    )

    ### Rigging Menu ###
    cmds.menuItem(label="Rigging", subMenu=True, to=True, parent=customMenu)

    # Rigging - Skeleton
    cmds.menuItem(divider=True, dividerLabel="Skeleton")

    # Rigging - Skin
    cmds.menuItem(divider=True, dividerLabel="Skin")
    cmds.menuItem(
        label="Skin Tool",
        image="smoothSkin.png",
        command="import takTools.rigging.tak_skinWeights as tak_skinWeights\nimport imp;imp.reload(tak_skinWeights)\ntak_skinWeights.SkinWeights()",
        sourceType="python"
    )
    cmds.menuItem(
        label="bSkinSaver",
        image="save.png",
        command="import takTools.rigging.bSkinSaver as bSkinSaver\nimport imp;imp.reload(bSkinSaver)\nbSkinSaver.showUI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Select Vertices",
        image="selAffectedVertex.png",
        ann="Select affected vertices with selected joint.",
        command="import takTools.common.tak_misc as tak_misc\nimport imp;imp.reload(tak_misc)\ntak_misc.selAffectedVertex()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Select Joints",
        image="selectInfluences.bmp",
        ann="Select skin joints with selected mesh.",
        command="import takTools.common.tak_misc as tak_misc\nimport imp;imp.reload(tak_misc)\ntak_misc.selInflu()",
        sourceType="python"
    )

    # Rigging - Build
    cmds.menuItem(divider=True, dividerLabel="Build")
    cmds.menuItem(
        label="Auto Rigging",
        image="takAutoRig.png",
        command="import takTools.rigging.autoRigging as ar\nimport imp;imp.reload(ar)\n\ntry:\n    arui.close()\n    arui.deleteLater()\nexcept:\n    pass\n\narui = ar.ui.mainUI.MainUI()\narui.show()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Controller",
        image="circle.png",
        command="import takTools.rigging.tak_createCtrl as tak_createCtrl\nimport imp;imp.reload(tak_createCtrl)\ntak_createCtrl.UI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Group",
        image="out_transform.png",
        command="import takTools.rigging.tak_group as tak_group\nimport imp;imp.reload(tak_group)\ntak_group.UI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Attribute Manager",
        image="attributes.png",
        command="import takTools.rigging.tak_attrManager as tak_attrManager;import imp;imp.reload(tak_attrManager);tak_attrManager.ui()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Mirror Object",
        image="polyMirrorGeometry.png",
        command="import takTools.common.tak_misc as tak_misc\nimport imp;imp.reload(tak_misc)\ntak_misc.mirObjUi()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Range of Motion",
        image="ROM.png",
        ann="Create range of motion for selected object",
        command="import takTools.rigging.tak_ROM as tak_ROM\nimport imp;imp.reload(tak_ROM)\ntak_ROM.UI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Multi Constraint",
        image="multiConstraint.bmp",
        ann="Constraint to multiple objects, first select driver then selcet other drivens",
        command="import takTools.rigging.tak_mulConst as tak_mulConst\nimport imp;imp.reload(tak_mulConst)\ntak_mulConst.UI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Copy Mirror SDK",
        image="tak_copySDK.bmp",
        ann="Copy or mirror set driven keyframes",
        command="import takTools.rigging.tak_copyMirrorSDK as tak_copyMirrorSDK\nimport imp;imp.reload(tak_copyMirrorSDK)\ntak_copyMirrorSDK.UI()",
        sourceType="python"
    )

    # Rigging - Misc
    cmds.menuItem(divider=True, dividerLabel="Misc")
    cmds.menuItem(
        label="Clean Rig",
        image="cleanUpRig.png",
        command="import takTools.rigging.tak_cleanUpRig as tak_cleanUpRig\nimport imp;imp.reload(tak_cleanUpRig)\ntak_cleanUpRig.ui()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Attach It",
        image="attachIt.png",
        command="import takTools.rigging.tak_attachIt as tak_attachIt\nimport imp;imp.reload(tak_attachIt)\ntak_attachIt.UI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Arrange Objects",
        image="arrangeObjs.png",
        ann="Arrange selected object in grid",
        command="import takTools.common.tak_misc as tm\nimport imp;imp.reload(tm)\n\ntm.arrangeObjectUI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="LR Target",
        image="LRTarget.bmp",
        ann="Split facial expression to left and right target.",
        command="import takTools.rigging.tak_LRTarget as tak_LRTarget\nimport imp;imp.reload(tak_LRTarget)\ntak_LRTarget.UI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Corrective Blendshape",
        image="correctiveBS.png",
        ann="Corrective blend shape tools.",
        command="import takTools.rigging.tak_correctiveBS as tak_correctiveBS\nimport imp;imp.reload(tak_correctiveBS)\nposCorObj = tak_correctiveBS.UI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Sliding Control",
        image="softMod.png",
        ann="Create sliding softMod control for selected geometry.",
        command="import takTools.common.tak_misc as tak_misc\nimport imp;imp.reload(tak_misc)\n\ntak_misc.setupSoftModCtrl()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Sort Outliner",
        image="sortName.png",
        ann="Sorting selected items in outliner.",
        command="import takTools.common.tak_misc as tak_misc\nimport imp;imp.reload(tak_misc)\ntak_misc.sortOutl()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Copy UV to Orig",
        image="copyUvRiggedMesh.png",
        ann="Copy source mesh's uv to target mesh that rigged.",
        command="import pymel.core as pm\nimport takTools.common.tak_misc as tak_misc\n\nsels = cmds.ls(sl=True)\nsrc = sels[0]\ntrg = sels[1]\n\ntak_misc.copyUvRiggedMesh(src, trg)",
        sourceType="python"
    )

    ### Animation Menu ###
    cmds.menuItem(label="Animation", subMenu=True, to=True, parent=customMenu)
    cmds.menuItem(
        label="Move All",
        image="moveAll.png",
        command="import takMaxAniTools as tmat\nimport imp;imp.reload(tmat)\ntmat.moveAll.setupMoveAll()",
        sourceType="python"
    )

    ### FX Menu ###
    cmds.menuItem(label="FX", subMenu=True, to=True, parent=customMenu)

    ### Misc Menu ###
    cmds.menuItem(label="Misc", subMenu=True, to=True, parent=customMenu)
    cmds.menuItem(
        label="Resource Browser",
        image="imageDisplay.png",
        command="import takTools.pipeline.takMayaResourceBrowser as tmrb;tmrb.TakMayaResourceBrowser.showUI()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Remove Panel Callbacks",
        image="menuIconPanels.png",
        ann="Remove model panel callbacks.",
        command="import takTools.utils.mayaUI as uiUtils\nimport imp;imp.reload(uiUtils)\n\nuiUtils.removeModelPanelCallbacks()",
        sourceType="python"
    )
    cmds.menuItem(
        label="Cleanup Scene",
        image="cleanupScene.png",
        ann="Remove unknown nodes and plugins.",
        command="import takTools.utils.globalUtil as gUtil;import imp;imp.reload(gUtil);gUtil.cleanupMayaScene()",
        sourceType="python"
    )
