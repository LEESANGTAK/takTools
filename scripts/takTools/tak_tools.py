"""
Author: TAK
Website: https://ta-note.com
Created: 12/22/2015
Updated: 02/05/2022

Description:
    Custom shelf tool to organize shelf buttons more efficiently.
"""

import os
import re
import json
from functools import partial

from maya import cmds

from .utils import system as sysUtil


MODULE_NAME = "takTools"
WIN_NAME = "{0}Win".format(MODULE_NAME)
CONFIG_FILENAME = "{}_config.json".format(MODULE_NAME)
TAK_TOOLS_CONFIG_PATH = cmds.internalVar(userAppDir=True) + "config"

SHELF_HEIGHT = 42


def UI():
    # Load configuration info
    config = {}
    if os.path.exists(TAK_TOOLS_CONFIG_PATH):
        with open(TAK_TOOLS_CONFIG_PATH, 'r') as f:
            config = json.load(f)

    # Set workspace width value
    if config:
        workspaceWidth = config['workspaceWidth']
    else:
        sysObj = sysUtil.System()
        workspaceWidth = sysObj.screenWidth / 10.0

    if cmds.window(WIN_NAME, exists=True):
        cmds.deleteUI(WIN_NAME)
    if cmds.dockControl(MODULE_NAME, exists=True):
        cmds.deleteUI(MODULE_NAME)

    # Main menu section
    cmds.window(WIN_NAME)
    cmds.menuBarLayout(WIN_NAME)
    cmds.menu('fileMenu', label = 'File', p = WIN_NAME)
    cmds.menuItem(label = 'Save Tools', c = saveTools, p = 'fileMenu')
    cmds.menu('editMenu', label = 'Edit', p = WIN_NAME)
    cmds.menuItem(label = 'Add Tool', c = addToolUi, p = 'editMenu')
    cmds.menuItem(label = 'Store Config', c = storeConfig, p = 'editMenu')

    cmds.paneLayout('mainPaneLo', configuration = 'horizontal2', paneSize = [(2, 50, 50)])

    cmds.formLayout('mainFormLo', p = 'mainPaneLo')

    # common tools section #
    cmds.tabLayout('cmnToolTabLo', tv = False, p = 'mainFormLo')
    cmds.shelfLayout('Common', h = (SHELF_HEIGHT * 4), parent = 'cmnToolTabLo')
    cmds.shelfButton(annotation = 'Set maya preference.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'setPref.bmp', command = 'import takTools.pipeline.tak_shotSetUp as tak_shotSetUp\nimport imp\nimp.reload(tak_shotSetUp)\ntak_shotSetUp.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Content Browser', width = 35, height = 35, imageOverlayLabel = '', image1 = 'teContentBrowser.png', command = 'OpenContentBrowser', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Open with current working directory.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'fileOpen.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.openCWD()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Save as in current working directory.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'fileSave.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.saveCWD()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Edit the references for the current scene', width = 35, height = 35, imageOverlayLabel = '', image1 = 'out_reference.png', command = 'ReferenceEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select all the children of the current selection', width = 35, height = 35, imageOverlayLabel = 'SH', image1 = 'menuIconEdit.png', command = 'SelectHierarchy', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Freeze Transformations', width = 35, height = 35, imageOverlayLabel = 'FT', image1 = 'menuIconModify.png', command = 'FreezeTransformations', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Center Pivot', width = 35, height = 35, imageOverlayLabel = 'CP', image1 = 'menuIconModify.png', command = 'CenterPivot', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Namespace Editor', width = 35, height = 35, imageOverlayLabel = 'Name', image1 = 'namespaceEditor.png', command = 'NamespaceEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Component Editor', width = 35, height = 35, imageOverlayLabel = 'CpEd', image1 = 'menuIconWindow.png', command = 'ComponentEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'UV Texture Editor', width = 35, height = 35, imageOverlayLabel = '', image1 = 'UVEditorUV.png', command = 'TextureViewWindow', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Display and edit connections in shading networks', width = 35, height = 35, imageOverlayLabel = '', image1 = 'hypershade.png', command = 'HypershadeWindow', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Display relationships among nodes in your scene graphically', width = 35, height = 35, imageOverlayLabel = '', image1 = 'nodeGrapherRemoveNodes.png', command = 'NodeEditorWindow', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Make connections between object attributes', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mergeConnections.png', command = 'ConnectionEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Expression Editor', width = 35, height = 35, imageOverlayLabel = '', image1 = 'out_expression.png', command = 'ExpressionEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Edit animation curves', width = 35, height = 35, imageOverlayLabel = '', image1 = 'out_animCurveTA.png', command = 'GraphEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'CVs', image1 = 'menuIconDisplay.png', command = 'ToggleCVs', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Object Details', width = 35, height = 35, imageOverlayLabel = 'objDtail', image1 = 'menuIconDisplay.png', command = 'ToggleObjectDetails', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'PCount', image1 = 'menuIconDisplay.png', command = 'TogglePolyCount', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Frame Rate', width = 35, height = 35, imageOverlayLabel = 'FRate', image1 = 'menuIconDisplay.png', command = 'ToggleFrameRate', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'CFrame', image1 = 'menuIconDisplay.png', command = 'ToggleCurrentFrame', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Camera Names', width = 35, height = 35, imageOverlayLabel = 'Cam', image1 = 'menuIconDisplay.png', command = 'ToggleCameraNames', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Toggle x-ray mode for selection.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'xRay.bmp', command = '{\n    string $selection[] = `ls -sl`;  \n    \n    for ($cur in $selection){\n        \n        int $result[] = `displaySurface -q -x $cur `;\n        if ( $result[0] )\n            displaySurface -x 0 $cur ;\n        else\n            displaySurface -x 1 $cur ;\n            \n    }    \n}', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Toggle wire mode for selection.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'UVTBWireFrame.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.Wire()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Preset', image1 = 'hypershade.png', command = 'import takTools.modeling.tak_matPreset as tak_matPreset\nimport imp\nimp.reload(tak_matPreset)\ntak_matPreset.MatPreset.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'ShpRGB', image1 = 'colorPresetSpectrum.png', command = 'from takTools.common import tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.setShapeColorRGB()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Wire', image1 = 'hairPaintSpecular.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.setJntColorUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Set ouliner color', width = 35, height = 35, imageOverlayLabel = 'Outliner', image1 = 'hairPaintSpecular.png', command = 'import takTools.common.tak_outlinerColor as tc\nimport imp\nimp.reload(tc)\ntc.showUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Sorting selected items in outliner.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'sortName.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.sortOutl()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Renamer', width = 35, height = 35, imageOverlayLabel = '', image1 = 'quickRename.png', command = 'from takRenamer import main;import imp;imp.reload(main);main.showUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Delete construction history, unlock normal, unlock attr, delete intermediate shapes, freeze transform', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cleanUpMesh.bmp', command = 'import takTools.modeling.tak_cleanUpModel as tak_cleanUpModel\nimport imp\nimp.reload(tak_cleanUpModel)\ntak_cleanUpModel.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Set Manager', width = 35, height = 35, imageOverlayLabel = '', image1 = 'objectSet.svg', command = 'from imp import reload; import setManager as sm; reload(sm)\nsmGUI = sm.gui.ManagerGUI()\nsmGUI.show()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Layout script editor horizontally', width = 35, height = 35, imageOverlayLabel = 'ScriptEditor', image1 = 'defaultTwoSideBySideLayout.png', command = 'from takTools.utils import qtUtil;qtUtil.editScriptEditorHorizontal()', sourceType = 'python')

    cmds.separator('mainSep', h = 10, style = 'in', p = 'mainFormLo')

    # task tools section #
    # create tab
    cmds.tabLayout('taskTabLo', p = 'mainFormLo')
    riggingTab = cmds.formLayout('RiggingFormLo', w = 37 * 10, p = 'taskTabLo')
    aniTab = cmds.formLayout('AnimationFormLo', w = 37 * 10, p = 'taskTabLo')
    modelTab = cmds.formLayout('ModelingFormLo', w = 37 * 10, p = 'taskTabLo')
    fxTab = cmds.formLayout('FxFormLo', w = 37 * 10, p = 'taskTabLo')
    miscTab = cmds.formLayout('MiscFormLo', w = 37 * 10, p = 'taskTabLo')
    cmds.tabLayout('taskTabLo', e = True, tabLabel = [(riggingTab, 'Rigging'), (aniTab, 'Animation'), (modelTab, 'Modeling'), (fxTab, 'Fx'), (miscTab, 'Misc')])


    # Editing main layout
    cmds.formLayout('mainFormLo', e = True,
        attachForm = [('cmnToolTabLo', 'top', 0), ('cmnToolTabLo', 'left', 0), ('cmnToolTabLo', 'right', 0), ('mainSep', 'left', 0), ('mainSep', 'right', 0), ('taskTabLo', 'left', 0), ('taskTabLo', 'right', 0), ('taskTabLo', 'bottom', 0)],
        attachControl = [('mainSep', 'top', 5, 'cmnToolTabLo'), ('taskTabLo', 'top', 5, 'mainSep')])

    # rigging tab
    cmds.scrollLayout('riggingScrLo', childResizable = True, p = 'RiggingFormLo')
    cmds.formLayout('RiggingFormLo', e = True, attachForm = [('riggingScrLo', 'top', 0), ('riggingScrLo', 'bottom', 0), ('riggingScrLo', 'left', 0), ('riggingScrLo', 'right', 0)])
    cmds.frameLayout('riggingDisplayFrameLo', label = 'Display', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Display', h = (SHELF_HEIGHT * 1), p = 'riggingDisplayFrameLo')
    cmds.shelfButton(annotation = 'toggle -state on -localAxis;', width = 35, height = 35, imageOverlayLabel = 'LRAO', image1 = 'commandButton.png', command = 'toggle -state on -localAxis;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'toggle -state off -localAxis;', width = 35, height = 35, imageOverlayLabel = 'LRAF', image1 = 'commandButton.png', command = 'toggle -state off -localAxis;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Customize the joint scale', width = 35, height = 35, imageOverlayLabel = 'JS', image1 = 'menuIconDisplay.png', command = 'jdsWin', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Change the joint style', width = 35, height = 35, imageOverlayLabel = '', image1 = 'jointStyle.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.drawJntStyle()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Change display type.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'displayType.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.displayType()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Display affected', width = 35, height = 35, imageOverlayLabel = 'DA', image1 = 'pythonFamily.png', command = 'import takTools.utils.display as dp\nimport imp\nimp.reload(dp)\ndp.displayAffectedToggle()', sourceType = 'python')

    cmds.frameLayout('riggingEditMdlFrameLo', label = 'Edit Model', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Edit_Model', h = (SHELF_HEIGHT * 3), p = 'riggingEditMdlFrameLo')
    cmds.shelfButton(annotation = 'abSymMesh;', width = 35, height = 35, imageOverlayLabel = 'abSym', image1 = 'symmetrize.png', command = 'abSymMesh;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Assign lambert with a selected texture.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'lambertWithSelectedTexture.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.assignLambertWithSelectedTexture()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign solid color material with grabed color.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'solColorMat.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.solidColMat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Duplicate selected shader network.', width = 35, height = 35, imageOverlayLabel = 'Dup', image1 = 'out_lambert.png', command = 'pm.mel.hyperShadePanelMenuCommand("hyperShadePanel1", "duplicateShadingNetwork");', sourceType = 'python')
    cmds.shelfButton(annotation = 'Duplicate material and assign duplicated material.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'dupMatAssign.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.dupMatAndAssign()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign the material of first selection to the others', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copyMat.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.copyMat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Copy selected objects texture', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copyTexture.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.copyTexRenameUI()', sourceType = 'python')
    cmds.shelfButton(annotation = "\tCut selected geometry with selected joints.\n\tUsing 'js_cutPlane.mel' script.\n\tSelect first joints and geometry last.", width = 35, height = 35, imageOverlayLabel = '', image1 = 'cutGeoWithJoints.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.cutGeoWithJnts()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Add plane for cutting polygonal geometry', width = 35, height = 35, imageOverlayLabel = '', image1 = 'addPlane.bmp', command = 'source js_cutPlane;\njs_cutPlane_create;\n', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Cut selected object with planes', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cutPlaneDone.bmp', command = 'source js_cutPlane;\njs_cutPlane_cut 1;\n', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Sculpt a geometry object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'putty.png', command = 'SculptGeometryTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Grab Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'Grab.png', command = 'SetMeshGrabTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Erase Target Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'Erase.png', command = 'SetMeshEraseTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Smooth Target Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'SmoothTarget.png', command = 'SetMeshSmoothTargetTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Assign random color lamber.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ranColLam.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.ranColLam()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Copy all uv sets and material from source to target.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copyUvMat.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.copyUvMat()', sourceType = 'python')
    cmds.shelfButton(annotation = "Copy source mesh's uv to target mesh that rigged", width = 35, height = 35, imageOverlayLabel = '', image1 = 'copyUvRiggedMesh.png', command = 'import pymel.core as pm\nimport takTools.common.tak_misc as tak_misc\n\nsels = pm.ls(sl=True)\nsrc = sels[0]\ntrg = sels[1]\n\ntak_misc.copyUvRiggedMesh(src, trg)', sourceType = 'python')
    cmds.shelfButton(annotation = 'File Texture Manager', width = 35, height = 35, imageOverlayLabel = '', image1 = 'texManger.bmp', command = 'FileTextureManager;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Reduce', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyReduce.png', command = 'expandPolyGroupSelection; doPerformPolyReduceArgList 3 {"1","0","0","1","1","1","1","1","1","0.5","0.5","0.5","0.5","0.5","0.5","0","0.01","0","1","0","0.0","1","1","","1","1","50","0","0","1","0","0","0","0"};', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Remesh', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyRemesh.png', command = 'polyRemesh -maxEdgeLength 1 -useRelativeValues 1 -collapseThreshold 20 -smoothStrength 0 -tessellateBorders 1 -interpolationType 2', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Retopologize', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyRetopo.png', command = 'polyRetopo -constructionHistory 1 -replaceOriginal 1 -preserveHardEdges 0 -topologyRegularity 1.0 -faceUniformity 0 -anisotropy 0.75 -targetFaceCount 1000 -targetFaceCountTolerance 10', sourceType = 'mel')

    cmds.frameLayout('riggingDeformationFrameLo', label = 'Deformation', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Deformation', h = (SHELF_HEIGHT * 4), p = 'riggingDeformationFrameLo')
    cmds.shelfButton(annotation = 'Create a skeleton and manage skeleton poses.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'takSkeleton.png', command = 'import takSkeleton as ts\nimport imp\nimp.reload(ts)\nts.gui.showUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'DNA Editor', width = 35, height = 35, imageOverlayLabel = 'DNA', image1 = 'MHC.png', command = 'from imp import reload\nimport dna_editor; reload(dna_editor)\ndna_editor.gui.show()', sourceType = 'python')
    cmds.shelfButton(annotation = "EA's SSD(Smooth Skin Deformation) tool with custom GUI.", width = 35, height = 35, imageOverlayLabel = '', image1 = 'dembones.jpg', command = 'import dem_bones\ndem_bones.showUI()', sourceType = 'python')
    cmds.shelfButton(annotation = '"takRigLogic" pose editor.', width = 35, height = 35, imageOverlayLabel = 'Editor', image1 = 'dembones.jpg', command = 'import imp\nimport editPoseGUI\nimp.reload(editPoseGUI)\ngui = editPoseGUI.EditPoseGUI()\ngui.show()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'HIKCharacterToolSkeleton_100.png', command = 'from imp import reload\nimport takSkelMeshManager as tsm; reload(tsm)\ntsm.showUI()\n', sourceType = 'python')
    cmds.shelfButton(annotation = 'Set skin weights', width = 35, height = 35, imageOverlayLabel = '', image1 = 'skinWeight.png', command = 'import takTools.rigging.tak_skinWeights as tak_skinWeights\nimport imp\nimp.reload(tak_skinWeights)\ntak_skinWeights.showUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select affected vertices by a selected influence', width = 35, height = 35, imageOverlayLabel = '', image1 = 'selAffectedVertex.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.selAffectedVertex()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select influence(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'selectInfluences.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.selInflu()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select all the child joints', width = 35, height = 35, imageOverlayLabel = '', image1 = 'selChldJnt.bmp', command = "### Select Joint in Hierarchy ###\njntList = cmds.ls(sl = True, dag = True, type = 'joint')\ncmds.select(jntList)", sourceType = 'python')
    cmds.shelfButton(annotation = 'Select surface(s) and a joint.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'smoothSkin.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.smoothSkinBind()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Rebind Skin.', width = 35, height = 35, imageOverlayLabel = 'Rebind', image1 = 'smoothSkin.png', command = 'import takTools.utils.skin as skinUtil\nimport imp\nimp.reload(skinUtil)\nsels = pm.selected()\nfor sel in sels: skinUtil.reBind(sel)', sourceType = 'python')
    cmds.shelfButton(annotation = 'Detach Skin', width = 35, height = 35, imageOverlayLabel = '', image1 = 'detachSkin.png', command = 'DetachSkin', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'SSD', image1 = 'menuIconSkinning.png', command = 'BakeDeformerTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create range of motion for selected object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ROM.png', command = 'import takTools.rigging.tak_ROM as tak_ROM\nimport imp\nimp.reload(tak_ROM)\ntak_ROM.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Weight Hammer on Edge Loop', width = 35, height = 35, imageOverlayLabel = '', image1 = 'weightHammerOnEdgeLoop.bmp', command = "### Weight Hammer on Edge Loop ###\ncmds.SelectEdgeLoopSp()\nmel.eval('weightHammerVerts;')", sourceType = 'python')
    cmds.shelfButton(annotation = 'from maya import cmds, mel\n\nweightHammerBrush = cmds.artSelectCt...', width = 35, height = 35, imageOverlayLabel = '', image1 = 'weightHammer.png', command = "from maya import cmds, mel\n\nweightHammerBrush = cmds.artSelectCtx(beforeStrokeCmd='select -cl;', afterStrokeCmd='if (size(`ls -sl`) > 0){WeightHammer;}')\ncmds.setToolTo(weightHammerBrush)", sourceType = 'python')
    cmds.shelfButton(annotation = 'tf_smoothSkinWeight', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tf_smoothSkin.bmp', command = 'import takTools.rigging.averageVertexSkinWeightBrush as averageVertexSkinWeightBrush\nimport imp\nimp.reload(averageVertexSkinWeightBrush)\naverageVertexSkinWeightBrush.paint()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Paint Smooth Weights Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'brSmoothWeights.svg', command = 'if (! `pluginInfo -q -loaded brSmoothWeights`)\n{\n    loadPlugin brSmoothWeights;\n}\nbrSmoothWeightsToolCtx;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Paint skin weights tool options', width = 35, height = 35, imageOverlayLabel = '', image1 = 'paintSkinWeights.png', command = 'ArtPaintSkinWeightsToolOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select either a single skin or the source and the destination skin.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirrorSkinWeight.png', command = 'MirrorSkinWeights', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select the source surface and the destination surface or component.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copySkinWeight.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.addInfCopySkin()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Separate selected faces as separated skin mesh.', width = 35, height = 35, imageOverlayLabel = 'DupSkin', image1 = 'polyDuplicateFacet.png', command = 'import takTools.utils.skin as skinUtil\nimport imp\nimp.reload(skinUtil)\nskinUtil.duplicateSkinMesh()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select source skin geo and target geo', width = 35, height = 35, imageOverlayLabel = 'Overlap', image1 = 'polyConvertToVertices.png', command = 'import takTools.utils.skin as skinUtil\nimport imp\nimp.reload(skinUtil)\nsels = cmds.ls(sl=True)\ntrg = sels.pop(-1)\nfor src in sels: skinUtil.copySkinOverlapVertices(src, trg)', sourceType = 'python')
    cmds.shelfButton(annotation = 'Add influences. Select influences and geometry.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'addWrapInfluence.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.addInfUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Remove Influence', width = 35, height = 35, imageOverlayLabel = '', image1 = 'removeWrapInfluence.png', command = 'RemoveInfluence', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'bSkin', image1 = 'save.png', command = 'import takTools.rigging.bSkinSaver as bSkinSaver\nimport imp\nimp.reload(bSkinSaver)\nbSkinSaver.showUI()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tak_helperJoint.png', command = 'import takTools.rigging.tak_helperJoint as tak_helperJoint\nimport imp\nimp.reload(tak_helperJoint)\ntak_helperJoint.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Corrective blend shape tools.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'correctiveBS.png', command = 'import takTools.rigging.tak_correctiveBS as tak_correctiveBS\nimport imp\nimp.reload(tak_correctiveBS)\nposCorObj = tak_correctiveBS.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'LRTarget.bmp', command = 'import takTools.rigging.tak_LRTarget as tak_LRTarget\nimport imp\nimp.reload(tak_LRTarget)\ntak_LRTarget.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Shape Editor', width = 35, height = 35, imageOverlayLabel = '', image1 = 'blendShapeEditor.png', command = 'ShapeEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'editDfmMember.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.editDfmMemberUI()', sourceType = 'python')

    cmds.frameLayout('riggingBuildFrameLo', label = 'Control', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Build', h = (SHELF_HEIGHT * 4), p = 'riggingBuildFrameLo')
    cmds.shelfButton(annotation = 'from imp import reload\nimport rigBuilder; reload(rigBuilder)\nrig...', width = 35, height = 35, imageOverlayLabel = 'RB', image1 = 'pythonFamily.png', command = 'from imp import reload\nimport rigBuilder; reload(rigBuilder)\nrigBuilder.mainWindow.show()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Tak auto rigging', width = 35, height = 35, imageOverlayLabel = '', image1 = 'takAutoRig.png', command = 'import takTools.rigging.autoRigging as ar\nimport imp\nimp.reload(ar)\n\ntry:\n    arui.close()\n    arui.deleteLater()\nexcept:\n    pass\n\narui = ar.ui.mainUI.MainUI()\narui.show()', sourceType = 'python')
    cmds.shelfButton(annotation = 'AdvancedSkeleton', width = 35, height = 35, imageOverlayLabel = '', image1 = 'AS.png', command = 'source "AdvancedSkeleton.mel";AdvancedSkeleton;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'import takTools.rigging.advancedSkeletonHelperUI as ashUI\nimport imp\nimp.reload(ashUI)\n\n...', width = 35, height = 35, imageOverlayLabel = 'Helper', image1 = 'AS.png', command = 'import takTools.rigging.advancedSkeletonHelperUI as ashUI\nimport imp\nimp.reload(ashUI)\n\ntry:\n    ashUIObj.close()\nexcept:\n    pass\n\nashUIObj = ashUI.AdvancedSkeletonHelperUI()\nashUIObj.show()\n', sourceType = 'python')
    cmds.shelfButton(annotation = 'b1 hair dynamic tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'hairChain.bmp', command = 'source IH_buildSpIkChain.mel;\nIH_buildSpIkChain();', sourceType = 'mel')
    cmds.shelfButton(annotation = "Additional functions for the 'IH_buildSpIkChain.mel' script.", width = 35, height = 35, imageOverlayLabel = '', image1 = 'forHairChain.png', command = 'import takTools.rigging.tak_addFuncForIHBuildSpIkChain as tak_addFuncForIHBuildSpIkChain\nimport imp\nimp.reload(tak_addFuncForIHBuildSpIkChain)\ntak_addFuncForIHBuildSpIkChain.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'js_createStretchSpline', width = 35, height = 35, imageOverlayLabel = '', image1 = 'scaleJoint.bmp', command = 'source js_createStretchSplineUI;\njs_createStretchSplineUI;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Stretchy Ik Creation', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ikStretch.bmp', command = 'source js_createIkStretchUI;\njs_createIkStretchUI', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'multiConnections.png', command = 'import takTools.rigging.tak_multiConnectAttr as tak_multiConnectAttr\nimport imp\nimp.reload(tak_multiConnectAttr)\ntak_multiConnectAttr.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Constraint to multiple objects, first select driver then selcet other drivens', width = 35, height = 35, imageOverlayLabel = '', image1 = 'multiConstraint.bmp', command = 'import takTools.rigging.tak_mulConst as tak_mulConst\nimport imp\nimp.reload(tak_mulConst)\ntak_mulConst.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Make group', width = 35, height = 35, imageOverlayLabel = '', image1 = 'group.bmp', command = 'import takTools.rigging.tak_group as tak_group\nimport imp\nimp.reload(tak_group)\ntak_group.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create control curves', width = 35, height = 35, imageOverlayLabel = '', image1 = 'control.bmp', command = 'import takTools.rigging.tak_createCtrl as tak_createCtrl\nimport imp\nimp.reload(tak_createCtrl)\ntak_createCtrl.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror controls', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirSelCon.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.mirCtrlShapeUi()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror control one to one.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirConOneToOne.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.mirConSel()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror selected objects', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirrorObj.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.mirObjUi()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Copy or mirror set driven keyframes', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tak_copySDK.bmp', command = 'import takTools.rigging.tak_copyMirrorSDK as tak_copyMirrorSDK\nimport imp\nimp.reload(tak_copyMirrorSDK)\ntak_copyMirrorSDK.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Set driven key options', width = 35, height = 35, imageOverlayLabel = 'Set.', image1 = 'menuIconKeys.png', command = 'SetDrivenKey', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'matchTransform.bmp', command = 'import takTools.rigging.tak_matchTransform as tak_matchTransform\nimport imp\nimp.reload(tak_matchTransform)\ntak_matchTransform.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'attrManager.png', command = 'import takTools.rigging.tak_attrManager as tak_attrManager\nimport imp\nimp.reload(tak_attrManager)\ntak_attrManager.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Transfer selected transform channel values to the parent.', width = 35, height = 35, imageOverlayLabel = 'Transfer', image1 = 'zeroDepth.png', command = 'import takTools.utils.transform as tu\nimport imp\nimp.reload(tu)\n\nsels = pm.selected()\nfor sel in sels:\n    tu.transferValueToParent(sel)', sourceType = 'python')
    cmds.shelfButton(annotation = 'Set up space switching.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tak_setupSpaceSwitching.png', command = 'import takTools.rigging.tak_setupSpaceSwitching as tak_setupSpaceSwitching\nimport imp\nimp.reload(tak_setupSpaceSwitching)\ntak_setupSpaceSwitching.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'attachIt.png', command = 'import takTools.rigging.tak_attachIt as tak_attachIt\nimport imp\nimp.reload(tak_attachIt)\ntak_attachIt.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'pickwalkDesigner.png', command = 'from takPickwalkDesigner import pdWindow\nimport imp\nimp.reload(pdWindow)\n\ntry:\n    pdWin.close()\nexcept:\n    pass\n\npdWin = pdWindow.PDWindow()\n', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cleanUpRig.png', command = 'import takTools.rigging.tak_cleanUpRig as tak_cleanUpRig\nimport imp\nimp.reload(tak_cleanUpRig)\ntak_cleanUpRig.ui()', sourceType = 'python')

    cmds.frameLayout('riggingExtraFrameLo', label = 'Extra Tools', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Extra_Tools', h = (SHELF_HEIGHT * 3), p = 'riggingExtraFrameLo')
    cmds.shelfButton(annotation = 'Allows interaction with objects during playback', width = 35, height = 35, imageOverlayLabel = '', image1 = 'interactivePlayback.png', command = 'InteractivePlayback', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'qualoth_icon.png', command = 'import takTools.fx.qualoth_simulation_manager as qualoth_simulation_manager\nimport imp\nimp.reload(qualoth_simulation_manager)\nqualoth_simulation_manager.main()', sourceType = 'python')
    cmds.shelfButton(annotation = 'nCloth set up with skined geometry.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'nClothSetUp.png', command = 'import takTools.rigging.tak_nClothSetUp as tak_nClothSetUp\nimport imp\nimp.reload(tak_nClothSetUp)\ntak_nClothSetUp.nClothSetUp()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create locator to keep place for selected items.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'placeHolder.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.plcHldr()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create curve with selected objects.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'crvFromSels.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.crvFromSelsUi()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyEdgeToCurves.png', command = 'meshName = pm.selected()[0].node().getTransform();pm.polyToCurve(form=2, degree=3, n=meshName+"_crv")', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create curve from edge ring with an selected edge.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'curveFromEdgeRing.png', command = 'import takTools.utils.mesh as meshUtil\nimport imp\nimp.reload(meshUtil)\nselEdge = pm.selected()[0]\nmeshUtil.curveFromEdgeRing(selEdge, "{0}_crv".format(selEdge.node().getTransform()))\n', sourceType = 'python')
    cmds.shelfButton(annotation = 'CV Curve Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'curveCV.png', command = 'CVCurveTool', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'curveEP.png', command = 'EPCurveTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Rebuild Curve Options', width = 35, height = 35, imageOverlayLabel = '', image1 = 'rebuildCurve.png', command = 'RebuildCurveOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Arrange selected object in grid', width = 35, height = 35, imageOverlayLabel = '', image1 = 'arrangeObjs.png', command = 'import takTools.common.tak_misc as tm\nimport imp\nimp.reload(tm)\n\ntm.arrangeObjectUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'OBB_BoundingBox', width = 35, height = 35, imageOverlayLabel = '', image1 = 'OBB_boundingBox.png', command = 'from maya import cmds\nfrom takTools.rigging.OBB.api import OBB\nmeshes = cmds.ls(selection=True)\nif len(meshes) == 0:\n   raise RuntimeError("Nothing selected!")\nfor mesh in meshes:\n    obbBoundBoxPnts = OBB.from_points(mesh)\n    obbCube = cmds.polyCube(ch=False, name="pointMethod_GEO")[0]\n    cmds.xform(obbCube, matrix=obbBoundBoxPnts.matrix)\n    cmds.rename(obbCube, mesh + \'_OBB\')', sourceType = 'python')
    cmds.shelfButton(annotation = 'OBB_Lattice', width = 35, height = 35, imageOverlayLabel = '', image1 = 'OBB_lattice.png', command = 'from maya import cmds\nfrom takTools.rigging.OBB.api import OBB\nmesh = cmds.ls(selection=True)\nif len(mesh) == 0:\n   raise RuntimeError("Nothing selected!")\nobbBoundBoxPnts = OBB.from_points(mesh)\nlattice = cmds.lattice(dv=(2, 2, 2),\n                       objectCentered=True,\n                       name="pointMethod_LATTICE\t")\ncmds.xform(lattice[1], matrix=obbBoundBoxPnts.matrix)\ncmds.xform(lattice[2], matrix=obbBoundBoxPnts.matrix)', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create sliding softMod control for selected geometry.', width = 35, height = 35, imageOverlayLabel = 'SlidingControl', image1 = 'softMod.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\n\ntak_misc.setupSoftModCtrl()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Convert soft selection to cluster.', width = 35, height = 35, imageOverlayLabel = 'SoftCluster', image1 = 'cluster.png', command = 'import takTools.utils.cluster as clusterUtils\nimport imp\nimp.reload(clusterUtils)\n\nclusterUtils.softSelectionToCluster()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Convert mash to joints', width = 35, height = 35, imageOverlayLabel = 'MASHtoJoints', image1 = 'pythonFamily.png', command = 'from maya import cmds\nfrom takTools.utils import MASH as mashUtil\nimport imp\nimp.reload(mashUtil)\n\nwaiter = cmds.ls(sl=True)[0]\njoints = mashUtil.buildJoints(waiter)\nmashUtil.buildSkinMesh(waiter, joints)', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Fold', image1 = 'commandButton.png', command = 'source makeFoldingRig.mel;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'autoSwim.bmp', command = 'import takTools.rigging.tak_autoSwim as tak_autoSwim\nimport imp\nimp.reload(tak_autoSwim)\ntak_autoSwim.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Show js_rotationOrderWin', width = 35, height = 35, imageOverlayLabel = '', image1 = 'rotate_M.png', command = 'source "js_rotationOrderWin.mel";\njs_rotationOrderWin();', sourceType = 'mel')


    # animation tab
    cmds.scrollLayout('aniScrLo', childResizable = True, p = 'AnimationFormLo')
    cmds.formLayout('AnimationFormLo', e = True, attachForm = [('aniScrLo', 'top', 0), ('aniScrLo', 'bottom', 0), ('aniScrLo', 'left', 0), ('aniScrLo', 'right', 0)])
    cmds.frameLayout('aniCtrlSelFrameLo', label = 'Control Select', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Control_Select', h = SHELF_HEIGHT, p = 'aniCtrlSelFrameLo')
    cmds.shelfButton(annotation = 'Save controls selected', width = 35, height = 35, imageOverlayLabel = '', image1 = 'pos2Shelf.bmp', command = 'pose2shelf', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Selector:biped', width = 35, height = 35, imageOverlayLabel = '', image1 = 'asBiped.png', command = 'source "biped.mel";', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Selector:face', width = 35, height = 35, imageOverlayLabel = '', image1 = 'asFace.png', command = 'source "face.mel";', sourceType = 'mel')
    cmds.shelfButton(annotation = 'picker', width = 35, height = 35, imageOverlayLabel = '', image1 = 'picker.png', command = 'source "picker.mel";', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'colorPickCursor.png', command = '\nimport ARSpicker\nARSpicker.picker.main()\n', sourceType = 'python')

    cmds.frameLayout('aniDisplayFrameLo', label = 'Display', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Display', h = SHELF_HEIGHT, p = 'aniDisplayFrameLo')
    cmds.shelfButton(annotation = 'Convert selected keyframe(s) into breakdown tick(s).', width = 35, height = 35, imageOverlayLabel = 'breakdown', image1 = 'breakdown.png', command = 'keyframe -tds on;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected keyframe(s) into key tick(s).', width = 35, height = 35, imageOverlayLabel = 'key', image1 = 'key.png', command = 'keyframe -tds off;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create ouline.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'bhGhostIcon.png', command = 'source bhGhost.mel;\nbhGhost;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select object(s) to generate a motion trail over time.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'motionTrail.png', command = 'doMotionTrail 2 { "snapshot  -motionTrail 1  -increment 1 -startTime `playbackOptions -query -min` -endTime `playbackOptions -query -max`", "1","0","0","1","1","1"}', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Frame Range HUD Toggle', width = 35, height = 35, imageOverlayLabel = '', image1 = 'eye.png', command = 'import takTools.utils.display as dpUtil;import imp;imp.reload(dpUtil);dpUtil.frameRangeHUDToggle();', sourceType = 'python')

    cmds.frameLayout('aniCrvFrameLo', label = 'Animation Curve', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Animation_Curve', h = SHELF_HEIGHT, p = 'aniCrvFrameLo')
    cmds.shelfButton(annotation = 'Set default keyframe tangent to the step mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'steped.png', command = 'keyTangent -global -itt linear;\nkeyTangent -global -ott step;\n', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Set default keyframe tangent to the spline mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'spline.png', command = 'keyTangent -global -itt spline;\nkeyTangent -global -ott spline;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Set default keyframe tangent to the linear mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'linear.bmp', command = 'keyTangent -global -itt linear;\nkeyTangent -global -ott linear;\n', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected animation curve to the cycle mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'makeCycle.bmp', command = 'animCurveEditor -edit -displayInfinities true graphEditor1GraphEd;\nsetInfinity -pri cycle;\nsetInfinity -poi cycle;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected animation curve to the cycle with offset mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cycleOffset.bmp', command = 'animCurveEditor -edit -displayInfinities true graphEditor1GraphEd;\nsetInfinity -pri cycleRelative;\nsetInfinity -poi cycleRelative;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected animation curve to the linear mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'makeLinear.bmp', command = 'animCurveEditor -edit -displayInfinities true graphEditor1GraphEd;\nsetInfinity -pri linear;\nsetInfinity -poi linear;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected animation curve to the constant mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'makeConstant.bmp', command = 'animCurveEditor -edit -displayInfinities false graphEditor1GraphEd;\nsetInfinity -poi constant;\nsetInfinity -pri constant;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Set easy in and easy out.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'easyEase.bmp', command = 'source easyEasyEase.mel;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Static Channels', width = 35, height = 35, imageOverlayLabel = 'SC', image1 = 'menuIconEdit.png', command = 'DeleteAllStaticChannels', sourceType = 'mel')

    cmds.frameLayout('aniPoseFrameLo', label = 'Pose', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Pose', h = SHELF_HEIGHT, p = 'aniPoseFrameLo')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'studioLibrary.png', command = 'import os\nimport sys\n    \nimport studiolibrary\nstudiolibrary.main()\n', sourceType = 'python')
    cmds.shelfButton(annotation = 'tweenMachine', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tweenMachine.xpm', command = 'source tweenMachine.mel;\ntweenMachine;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Mirror selected controls', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirrorCtrl.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.mirrorCtrlsUI()', sourceType = 'python')


    cmds.frameLayout('aniRefineShapeFrameLo', label = 'Refine Shape', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Refine_Shape', h = SHELF_HEIGHT, p = 'aniRefineShapeFrameLo')
    cmds.shelfButton(annotation = 'Sculpt a geometry object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'putty.png', command = 'SculptGeometryTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Correct problematic shape of animated geometry.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'aniSculpt.bmp', command = 'import takTools.animation.tak_aniSculpt as tak_aniSculpt\nimport imp\nimp.reload(tak_aniSculpt)\ntak_aniSculpt.UI()', sourceType = 'python')

    cmds.frameLayout('aniExtraFrameLo', label = 'Extra Tools', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Extra_Tools', h = SHELF_HEIGHT * 2, p = 'aniExtraFrameLo')
    cmds.shelfButton(annotation = 'Quicktime playblast with Pdplayer', width = 35, height = 35, imageOverlayLabel = '', image1 = 'playblastMov.png', command = 'source "makePlayblastMov.mel";\nmakePlayblastMov;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Delete keys and set default value', width = 35, height = 35, imageOverlayLabel = 'dflt', image1 = 'deleteKeys.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.delKeySetDflt()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Delete keys for selected controls', width = 35, height = 35, imageOverlayLabel = '', image1 = 'deleteKeys.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.delKey()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Delete constraints on the selected object(s)', width = 35, height = 35, imageOverlayLabel = '', image1 = 'deleteConstraints.bmp', command = 'DeleteConstraints', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Offset keyframe for selected object(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'offsetKey.bmp', command = 'import takTools.animation.tak_offsetKeyframe as tak_offsetKeyframe\nimport imp\nimp.reload(tak_offsetKeyframe)\ntak_offsetKeyframe.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Random offset keyframe for selected object(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'SMO_RandomOffsetKeysIcon.png', command = 'SMO_RandomOffsetKeys', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create procedure oscillate animation.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'oscillateMaker.bmp', command = 'import takTools.animation.tak_oscillateMaker as tak_oscillateMaker\nimport imp\nimp.reload(tak_oscillateMaker)\ntak_oscillateMaker.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'b1 nCloth tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'b1nCloth.bmp', command = 'source "D40clothTool.mel";', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Bake IH_HairChain tool.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'bakeHairChain.png', command = 'IH_BakeHairChain;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Hair Chain Baker', width = 35, height = 35, imageOverlayLabel = '', image1 = 'hairChainBaker.png', command = 'import takTools.animation.dynamicSplineBaker as dsb\nimport imp\nimp.reload(dsb)\ndsb.DynamicSplineBaker()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Interactive Playback', width = 35, height = 35, imageOverlayLabel = '', image1 = 'interactivePlayback.png', command = 'InteractivePlayback', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Clean up animation scene.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tak_cleanUpAniScene.png', command = 'import takTools.animation.tak_cleanUpAniScene as tak_cleanUpAniScene\nimport imp\nimp.reload(tak_cleanUpAniScene)\ntak_cleanUpAniScene.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Retargeting source animation to target.', width = 35, height = 35, imageOverlayLabel = 'DEV', image1 = 'takRetargeterIcon.png', command = 'import takRetargeter.ui as tru\nimport imp\nimp.reload(tru)\n\ntry:\n    trUI.close()\nexcept:\n    pass\n\ntrUI = tru.takRetargeterUI.TakRetargeterUI()\ntrUI.show()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Link Constraint', width = 35, height = 35, imageOverlayLabel = '', image1 = 'out_parentConstraint.png', command = 'from takMaxAniTools import linkConstraintUI as linkCnstUI\nimport imp\nimp.reload(linkCnstUI)\n\nui = linkCnstUI.LinkConstraintUI()\nui.show()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Publish animation.', width = 35, height = 35, imageOverlayLabel = 'DEV', image1 = 'out_timeEditorAnimSource.png', command = 'import takAniPublisher.aniPublisherCtrl as apctrl\nimport imp\nimp.reload(apctrl)\n\napCtrl = apctrl.AniPublisherCtrl()\napCtrl.showUI()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'springMagic.png', command = "execfile(r'C:\\GoogleDrive\\programs_env\\maya\\modules\\SpringMagic\\springMagic.py')", sourceType = 'python')
    cmds.shelfButton(annotation = 'Create overlap animation easily.', width = 35, height = 35, imageOverlayLabel = 'Overlapper', image1 = 'play_hover.png', command = 'source "Overlapper release 1-1.mel";OverlapperRelease;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'BookmarkManager;', width = 35, height = 35, imageOverlayLabel = '', image1 = 'Bookmark.png', command = 'BookmarkManager;', sourceType = 'mel')


    # modeling tab
    cmds.scrollLayout('mdlScrLo', childResizable = True, p = 'ModelingFormLo')
    cmds.formLayout('ModelingFormLo', e = True, attachForm = [('mdlScrLo', 'top', 0), ('mdlScrLo', 'bottom', 0), ('mdlScrLo', 'left', 0), ('mdlScrLo', 'right', 0)])
    cmds.frameLayout('mdlDisplayFrameLo', label = 'Display', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Display', h = (SHELF_HEIGHT * 1), p = 'mdlDisplayFrameLo')
    cmds.shelfButton(annotation = 'Vertex Normals', width = 35, height = 35, imageOverlayLabel = 'VN', image1 = 'menuIconDisplay.png', command = 'ToggleVertexNormalDisplay', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Face Normals', width = 35, height = 35, imageOverlayLabel = 'FN', image1 = 'menuIconDisplay.png', command = 'ToggleFaceNormalDisplay', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Normals Size...', width = 35, height = 35, imageOverlayLabel = 'NS', image1 = 'menuIconDisplay.png', command = 'ChangeNormalSize', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyNormalUnlock.png', command = 'polyNormalPerVertex -ufn true', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Auto Smoothing Groups', width = 35, height = 35, imageOverlayLabel = 'Auto', image1 = 'polyHardEdge.png', command = 'source "dp_autoSmoothingGroups.mel";', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySoftEdge.png', command = 'SoftPolyEdgeElements 1', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyNormal.png', command = 'ReversePolygonNormals', sourceType = 'mel')

    cmds.frameLayout('mdlSelFrameLo', label = 'Selection', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Selection', h = SHELF_HEIGHT, p = 'mdlSelFrameLo')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'selectSkipedEdgeRing.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.selEveryNUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Selects all parallel edges that form an edge ring based on the current selection', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyConvertToEdgeRing.png', command = 'polySelectSp -ring;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Selects all connected edges that form an edge loop based on the current selection', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyConvertToEdgeLoop.png', command = 'polySelectSp -loop;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySelectUsingConstraints.png', command = 'PolygonSelectionConstraints', sourceType = 'mel')

    cmds.frameLayout('mdlEditCpntFrameLo', label = 'Edit Component', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Edit_Component', h = (SHELF_HEIGHT * 3), p = 'mdlEditCpntFrameLo')
    cmds.shelfButton(annotation = 'Snap to X 0 for selected vertex(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'zeroVtx.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.zeroVtx()', sourceType = 'python')
    cmds.shelfButton(annotation = "Snap selected vertices to the target geometry's closest border vertex.", width = 35, height = 35, imageOverlayLabel = '', image1 = 'snapToClosestBorderVtx.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.snapToBrdrVtx()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Delete the selected Vertices / Edges.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyDelEdgeVertex.png', command = 'DeletePolyElements;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Collapse the selected edges or faces.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyCollapseEdge.png', command = 'performPolyCollapse 0;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Merge vertices / border edges based on selection.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyMerge.png', command = 'polyMergeVertex  -d 0.001 -am 1 -ch 1;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Interactively select and merge vertices', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyMergeVertex.png', command = 'MergeVertexTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Extrude the selected component', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyExtrudeFacet.png', command = 'performPolyExtrude 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Fill Hole', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyCloseBorder.png', command = 'FillHole', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Append to Polygon Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyAppendFacet.png', command = 'setToolTo polyAppendFacetContext ; polyAppendFacetCtx -e -pc `optionVar -q polyKeepFacetsPlanar` polyAppendFacetContext', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create a bridge between two sets of edges or faces', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyBridge.png', command = 'polyBridgeEdge -ch 1 -divisions 0 -twist 0 -taper 1 -curveType 0 -smoothingAngle 30;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Merge selected edge(s)', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySewEdge.png', command = 'cmds.polySewEdge(tolerance = 1)', sourceType = 'python')
    cmds.shelfButton(annotation = 'Detach selected edge(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'detachEdges.png', command = 'cmds.DetachEdgeComponent()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Multi-Cut Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'multiCut_NEX32.png', command = 'dR_multiCutTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Connect Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'connect_NEX32.png', command = 'dR_connectTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Split selected edge ring.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySplitEdgeRing.png', command = 'SplitEdgeRingTool;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Offset Edge Loop Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyDuplicateEdgeLoop.png', command = 'performPolyDuplicateEdge 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert to edge loop and set edge flow.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'edgeFlow.bmp', command = 'cmds.SelectEdgeLoopSp()\ncmds.polyEditEdgeFlow()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Slide edge loops or paths along their neighbouring edges', width = 35, height = 35, imageOverlayLabel = '', image1 = 'slideEdgeTool.png', command = 'SlideEdgeTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create a bevel along the selected edges', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyBevel.png', command = 'polyPerformAction "polyBevel -offset 0.5 -offsetAsFraction 1 -autoFit 1 -segments 1 -worldSpace 1 -uvAssignment 1 -fillNgons 1 -mergeVertices 1 -mergeVertexTolerance 0.0001 -smoothingAngle 30 -miteringAngle 180 -angleTolerance 180" e 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Chamfer the selected vertices', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyChamfer.png', command = 'polyChamferVtx 1 0.25 0;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Extract the currently selected faces from their shell and shows a manipulator to adjust their offset', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyChipOff.png', command = 'import takTools.utils.mesh as meshUtils;import imp;imp.reload(meshUtils);meshUtils.extractFace()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Duplicate the currently selected faces in a new shell and shows a manipulator to adjust their offset', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyDuplicateFacet.png', command = 'import takTools.utils.mesh as meshUtils;import imp;imp.reload(meshUtils);meshUtils.duplicateFace()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Crease Set Editor...', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyCrease.png', command = 'python "from maya.app.general import creaseSetEditor; creaseSetEditor.showCreaseSetEditor()"', sourceType = 'mel')

    cmds.frameLayout('mdlEditGeoFrameLo', label = 'Edit Mesh', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Edit_Mesh', h = (SHELF_HEIGHT * 3), p = 'mdlEditGeoFrameLo')
    cmds.shelfButton(annotation = 'Unsmooth', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyUnsmooth.png', command = 'polyUnsmooth -caching 1 -constructionHistory 1 -replaceOriginal 1 -divisionLevels 1', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'delSupportEdges.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.delSupportEdgesUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'retopoOptionItem', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyTriangulate.png', command = 'PolyRetopoOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'edgeRingCollapse.bmp', command = 'polyConvertToRingAndCollapse;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'deleteEdgeLoop.bmp', command = 'cmds.SelectEdgeLoopSp()\ncmds.SelectEdgeLoopSp()\ncmds.DeleteEdge()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Quad Draw Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'quadDraw_NEX32.png', command = 'dR_quadDrawTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Sculpt a geometry object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'putty.png', command = 'SculptGeometryTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Grab Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'Grab.png', command = 'SetMeshGrabTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Sculpt Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'Sculpt.png', command = 'SetMeshSculptTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Relax Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'Relax.png', command = 'SetMeshRelaxTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Pinch Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'Pinch.png', command = 'SetMeshPinchTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create symmetry mesh on x axis.', width = 35, height = 35, imageOverlayLabel = 'symX', image1 = 'pythonFamily.png', command = "import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.symmetry('x')", sourceType = 'python')
    cmds.shelfButton(annotation = 'Create symmetry mesh on z axis.', width = 35, height = 35, imageOverlayLabel = 'symZ', image1 = 'pythonFamily.png', command = "import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.symmetry('z')", sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror selected object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirrorObj.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.mirObjUi()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror geometry across an axis', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyMirrorGeometry.png', command = 'polyMirrorFace -ws 1  -direction 1 -mergeMode 1 -ch 1 -p 0 0 0 -mt 0.001;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select edge loops.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'separateGeo.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.sepGeoWithEdge()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select faces.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'sepGeo.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.sepGeoWithFace()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Combine and merge vertex.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cbMrgGeo.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.cbMrgGeo()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Combine and rename with parent.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'combineRenameWithParent.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.combineAndRenameWithParentName()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Combine and assign random color.', width = 35, height = 35, imageOverlayLabel = 'CombineRandomMat', image1 = 'render_rampShader.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.combineAndAssignRandomMat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Separate the selected polygon object shells or the shells of any selected faces from the object into distinct objects', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySeparate.png', command = 'SeparatePolygon', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Combine the selected polygon objects into one single object to allow operations such as merges or face trims', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyUnite.png', command = 'polyPerformAction polyUnite o 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Add polygons to the selected polygon objects to smooth them', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySmooth.png', command = 'polyPerformAction "polySmooth  -mth 0 -dv 1 -peh 0 -bnr 1 -c 1 -kb 1 -ksb 1 -khe 0 -kt 1 -kmb 1 -suv 1 -sl 1 -dpe 1 -ps 0.1 -ro 1" f 0', sourceType = 'mel')

    cmds.frameLayout('mdlMatFrameLo', label = 'Material', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Material', h = SHELF_HEIGHT, p = 'mdlMatFrameLo')
    cmds.shelfButton(annotation = 'Assign the material of first selection to the others', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copyMat.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.copyMat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign random color lamber.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ranColLam.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.ranColLam()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign solid color material with grabed color.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'solColorMat.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.solidColMat()', sourceType = 'python')

    cmds.frameLayout('mdlAppFrameLo', label = 'Extra Tools', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Extra_Tools', h = (SHELF_HEIGHT * 3), p = 'mdlAppFrameLo')
    cmds.shelfButton(annotation = 'Export selected object to ZBrush.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'GoZBrush.xpm', command = 'source "C:/Users/Public/Pixologic/GoZApps/Maya/GoZBrushFromMaya.mel"', sourceType = 'mel')
    cmds.shelfButton(annotation = 'uvlayout_open()', width = 35, height = 35, imageOverlayLabel = '', image1 = 'uvlayout.png', command = 'uvlayout_open()', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Run phothoshop.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'photoshop.bmp', command = "import subprocess\nsubprocess.Popen('C:\\Program Files\\Adobe\\Adobe Photoshop CS6 (64 Bit)\\Photoshop.exe')", sourceType = 'python')
    cmds.shelfButton(annotation = 'Duplicate object along the path', width = 35, height = 35, imageOverlayLabel = '', image1 = 'DupAlongPathToolbox.png', command = 'source DupAlongPathToolbox.mel;DupAlongPathToolbox;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Instance Along Curve', width = 35, height = 35, imageOverlayLabel = 'IAC', image1 = 'menuIconEdit.png', command = 'instanceAlongCurve', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Run spPaint3d.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'spPaint3d.bmp', command = 'spPaint3d', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create a curve on the grid or live surface specifying control vertices', width = 35, height = 35, imageOverlayLabel = '', image1 = 'curveCV.png', command = 'CVCurveTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create a curve on the grid or live surface specifying edit points', width = 35, height = 35, imageOverlayLabel = '', image1 = 'curveEP.png', command = 'EPCurveTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Rebuild curve options', width = 35, height = 35, imageOverlayLabel = '', image1 = 'rebuildCurve.png', command = 'RebuildCurveOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Polygon Edges to Curve', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyEdgeToCurves.png', command = 'meshName = pm.selected()[0].node().getTransform();pm.polyToCurve(form=2, degree=3, n=meshName+"_crv")', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'shelf_wireMeshFromCurve.png', command = 'if (! `pluginInfo -q -loaded "wire"`)\n{\n    loadPlugin "wire";\n}\nwireMeshFromCurve;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert nurbs curves to polygon geomtry', width = 35, height = 35, imageOverlayLabel = '', image1 = 'curveToPoly.png', command = 'import takTools.modeling.tak_curveToPoly as tak_curveToPoly\nimport imp\nimp.reload(tak_curveToPoly)\ntak_curveToPoly.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Convert selected curves to polygon stripe.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'crvToStripe.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.crvToPolyStrp()', sourceType = 'python')
    cmds.shelfButton(annotation = 'This script will attempt to Spherify the current selected objects or components.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'spherizeSelection.png', command = 'import takTools.modeling.spherize as spherize\nspherize.sphereizedSelection()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Align into circlular shape for selected edge loop.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'alignCircle.bmp', command = 'source _sort_circle_tool.mel;\n_sort_circle_tool;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Flatten geometry into uv space.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mopKnit.png', command = 'mopKnitOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Loft', width = 35, height = 35, imageOverlayLabel = '', image1 = 'skin.png', command = 'doPerformLoft("1", {"1","1","1","0","3","1","0","1"} )', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Creating hair guide curves from polygon tube.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'hairTools.png', command = 'import takTools.modeling.hairTools as hairTools\nimport imp\nimp.reload(hairTools)\nhairTools.hairballUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create water drop.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'waterDropGenerator_shelfIcon.png', command = 'import takTools.modeling.waterDropUI as waterDropUI\nimport imp\nimp.reload(waterDropUI)', sourceType = 'python')
    cmds.shelfButton(annotation = 'icPolyScatter;', width = 35, height = 35, imageOverlayLabel = '', image1 = 'icPolyScatter.png', command = 'icPolyScatter;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Boolean hard surface modeling', width = 35, height = 35, imageOverlayLabel = 'SpeedCut', image1 = 'pythonFamily.png', command = 'import takTools.modeling.speedCut as speedCut\nimport imp\nimp.reload(speedCut)', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Voxel', image1 = 'commandButton.png', command = 'source Voxel_Model_Generator_v4.mel;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'takXgenManager.png', command = '\nimport takXgenManager.xgenManager as xgManager;import imp;imp.reload(xgManager)\n\nxgmg = xgManager.XGenManager()\nxgmg.show()\n', sourceType = 'python')
    cmds.shelfButton(annotation = '3D Cut and Sew UV Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'CutSewUVTool.png', command = 'SetCutSewUVTool', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'ChkOn', image1 = 'commandButton.png', command = 'textureWindowDisplayCheckered(1, 1);', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'ChkOff', image1 = 'commandButton.png', command = 'textureWindowDisplayCheckered(1, 0);', sourceType = 'mel')


    # Fx Tab
    cmds.scrollLayout('fxScrLo', childResizable = True, p = 'FxFormLo')
    cmds.formLayout('FxFormLo', e = True, attachForm = [('fxScrLo', 'top', 0), ('fxScrLo', 'bottom', 0), ('fxScrLo', 'left', 0), ('fxScrLo', 'right', 0)])
    cmds.frameLayout('particleFrameLo', label = 'Particle', collapsable = True, p = 'fxScrLo')
    cmds.shelfLayout('Fx_Particle', h = (SHELF_HEIGHT * 1), p = 'particleFrameLo')
    cmds.shelfButton(annotation = 'Emit from Object', width = 35, height = 35, imageOverlayLabel = '', image1 = 'emitter.png', command = 'dynExecuteEmitterCommands 0 "emitter -type omni -r 100 -sro 0 -nuv 0 -cye none -cyi 1 -spd 1 -srn 0 -nsp 1 -tsp 0 -mxd 0 -mnd 0 -dx 1 -dy 0 -dz 0 -sp 0 " 1', sourceType = 'mel')

    cmds.frameLayout('RBDFrameLo', label = 'RBD', collapsable = True, p = 'fxScrLo')
    cmds.shelfLayout('Fx_RBD', h = (SHELF_HEIGHT * 1), p = 'RBDFrameLo')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'yd_crackut.bmp', command = 'source yd_crackut.mel;\nyd_crackut;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'crackMe.bmp', command = 'source crackMe175.mel;\ncrackMe;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'AxCrack.bmp', command = 'source AxCrack.mel;\nAxCrack;', sourceType = 'mel')

    cmds.frameLayout('volumeFrameLo', label = 'Volume', collapsable = True, p = 'fxScrLo')
    cmds.shelfLayout('Fx_Volume', h = (SHELF_HEIGHT * 1), p = 'volumeFrameLo')
    cmds.shelfButton(annotation = 'Create 3D Container', width = 35, height = 35, imageOverlayLabel = '', image1 = 'fluidCreate3D.png', command = 'create3DFluid 10 10 10 10 10 10', sourceType = 'mel')

    cmds.frameLayout('fluidFrameLo', label = 'Fluid', collapsable = True, p = 'fxScrLo')
    cmds.shelfLayout('Fx_Fluid', h = (SHELF_HEIGHT * 1), p = 'fluidFrameLo')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'droplet.png', command = 'import takTools.modeling.tak_dropletCreator as tdc\nimport imp\nimp.reload(tdc)\ntdc.UI()', sourceType = 'python')


    # misc tab
    cmds.scrollLayout('miscScrLo', childResizable = True, p = 'MiscFormLo')
    cmds.formLayout('MiscFormLo', e = True, attachForm = [('miscScrLo', 'top', 0), ('miscScrLo', 'bottom', 0), ('miscScrLo', 'left', 0), ('miscScrLo', 'right', 0)])
    cmds.frameLayout('miscFrameLo', label = 'Misc', collapsable = True, p = 'miscScrLo')
    cmds.shelfLayout('Misc_Misc', h = (SHELF_HEIGHT * 3), p = 'miscFrameLo')
    cmds.shelfButton(annotation = 'Remove unknown nodes, plugins, callbacks, scriptjobs', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cleanupScene.png', command = 'from takTools.utils import globalUtil;import imp;imp.reload(globalUtil); globalUtil.cleanupMayaScene()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Clear output window', width = 35, height = 35, imageOverlayLabel = 'ClOutWin', image1 = 'menuIconWindow.png', command = 'from takTools.utils import system as sysUtil\nimport imp\nimp.reload(sysUtil)\n\nsysUtil.clearOutputWindow()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Search maya resource images.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'imageDisplay.png', command = 'import takTools.pipeline.takMayaResourceBrowser as tmrb\n\ntmrb.TakMayaResourceBrowser.showUI()\n', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create an icon image', width = 35, height = 35, imageOverlayLabel = '', image1 = 'UVEditorSnapshot.png', command = 'from takTools.common import iconMaker\nimport imp\nimp.reload(iconMaker)\n\ngui = iconMaker.IconMakerGUI()\ngui.show()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Save specific scene information as a file.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'saveSceneInfo.png', command = 'import takTools.pipeline.tak_saveSceneInfo as tak_saveSceneInfo\nimport imp\nimp.reload(tak_saveSceneInfo)\ntak_saveSceneInfo.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create folder structure.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'prjFldSet.bmp', command = 'import takTools.pipeline.tak_prjFolderSetup as tak_prjFolderSetup\nimport imp\nimp.reload(tak_prjFolderSetup)\ntak_prjFolderSetup.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Load or reload or delete references.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'fileRef.png', command = 'import takTools.pipeline.tak_fileRef as tak_fileRef\nimport imp\nimp.reload(tak_fileRef)\ntak_fileRef.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Rename refrence node and namespace.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'renameRefNode.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.renameRefNode()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Change line width.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'lineWidth.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.lineWidth()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Shake selected camera.', width = 35, height = 35, imageOverlayLabel = 'Shake', image1 = 'Camera.png', command = 'import takTools.utils.camera as camUtils\nimport imp\nimp.reload(camUtils)\n\ncam = pm.selected()[0]\ncamUtils.shakeCamera(cam)\n', sourceType = 'python')
    cmds.shelfButton(annotation = 'Bake selected camera', width = 35, height = 35, imageOverlayLabel = '', image1 = 'bakeCam.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.bakeCam()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Bake selected camera to use in AE.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mayaCamToAE.png', command = 'import takTools.pipeline.tak_mayaCamToAE as tak_mayaCamToAE\nimport imp\nimp.reload(tak_mayaCamToAE)\ntak_mayaCamToAE.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Export selected camera for using in 3ds Max.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mayaCamToMax.png', command = 'import takTools.pipeline.tak_mayaCamToMax as tak_mayaCamToMax\nimport imp\nimp.reload(tak_mayaCamToMax)\ntak_mayaCamToMax.mayaCamToMax()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create camera following selected object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'followingCam.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.followingCam()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create locators per frame with selected object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'trackingLoc.bmp', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.trackingLoc()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Render viewport.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ikasRenderView.bmp', command = 'source ikas_renderViewBr', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Attach specular sphere to selected vertex(s) or selected two edges.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'specSphere.png', command = 'import takTools.common.tak_misc as tak_misc\nimport imp\nimp.reload(tak_misc)\ntak_misc.attachSpecSphere()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Batch playblast.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'batchPB.png', command = 'import takTools.pipeline.tak_batchPB as tak_batchPB\nimport imp\nimp.reload(tak_batchPB)\ntak_batchPB.batchPB()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Save and load render layer set up.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'saveRenderLayer.png', command = 'import takTools.pipeline.tak_saveRenderLayer as tak_saveRenderLayer\nimport imp\nimp.reload(tak_saveRenderLayer)\nrenLyrSaveObj = tak_saveRenderLayer.SaveRenderLayer()\nrenLyrSaveObj.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Edit maya ascii file contents.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'editMayaAscii.png', command = 'import takTools.pipeline.tak_editMayaAsciiFile as tak_editMayaAsciiFile\nimport imp\nimp.reload(tak_editMayaAsciiFile)\ntak_editMayaAsciiFile.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Clean up a fbx file.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'fbxReview.png', command = 'from imp import reload\nimport takFBXExporter as tfbxe; reload(tfbxe)\n\ntfbxe.gui.fbxCleanerUI.show()', sourceType = 'python')
    cmds.shelfButton(annotation = 'from takTools.utils import drawingFuncCurves as dfc\nimport imp\nimp.reload(dfc)\n...', width = 35, height = 35, imageOverlayLabel = 'FuncCurves', image1 = 'sineCurveProfile.png', command = 'from takTools.utils import drawingFuncCurves as dfc\nimport imp\nimp.reload(dfc)\n\ndfc.showUI()', sourceType = 'python')

    cmds.frameLayout('tempFrameLo', label = 'Temp', collapsable = True, p = 'miscScrLo')
    cmds.shelfLayout('Misc_Temp', h = (SHELF_HEIGHT * 2), p = 'tempFrameLo')
    cmds.shelfButton(annotation = 'Set interactive mode for skin clusters.', width = 35, height = 35, imageOverlayLabel = 'InterSkin', image1 = 'pythonFamily.png', command = "for skin in pm.ls(type='skinCluster'):\n    skin.normalizeWeights.set(1)", sourceType = 'python')
    cmds.shelfButton(annotation = 'Set segmentScaleCompensate to false for selected skin clusters.', width = 35, height = 35, imageOverlayLabel = 'SegScaleOff', image1 = 'pythonFamily.png', command = "for jnt in pm.selected(type='joint'):\n    jnt.segmentScaleCompensate.set(False)", sourceType = 'python')
    cmds.shelfButton(annotation = 'Set color space to raw for normal maps.', width = 35, height = 35, imageOverlayLabel = 'RawNormal', image1 = 'pythonFamily.png', command = "for node in pm.ls(type='bump2d'):\n    node.inputs(type='file')[0].colorSpace.set('Raw')", sourceType = 'python')
    cmds.shelfButton(annotation = 'Set tangentSpace to Left Handed for meshes.', width = 35, height = 35, imageOverlayLabel = 'TanSpace', image1 = 'pythonFamily.png', command = "for mesh in pm.ls(type='mesh'):\n    mesh.tangentSpace.set(2)", sourceType = 'python')


    # Outliner
    cmds.frameLayout('olFrameLo', labelVisible = False, p = 'mainPaneLo')
    panel = cmds.outlinerPanel()
    outliner = cmds.outlinerPanel(panel, query=True, outlinerEditor=True)
    cmds.outlinerEditor( outliner, edit=True, mainListConnection='worldList', selectionConnection='modelList', showShapes=False, showAssignedMaterials=False, showReferenceNodes=True, showReferenceMembers=True, showAttributes=False, showConnected=False, showAnimCurvesOnly=False, autoExpand=False, showDagOnly=True, ignoreDagHierarchy=False, expandConnections=False, showCompounds=True, showNumericAttrsOnly=False, highlightActive=True, autoSelectNewObjects=False, doNotSelectNewObjects=False, transmitFilters=False, showSetMembers=True, setFilter='defaultSetFilter', ignoreHiddenAttribute=False )

    # Dock window to left side
    cmds.dockControl(MODULE_NAME, area='left', content=WIN_NAME, w=workspaceWidth)

SHELF_LIST = ['Common',
'Rigging_Display', 'Rigging_Edit_Model', 'Rigging_Build', 'Rigging_Deformation', 'Rigging_Extra_Tools',
'Animation_Control_Select', 'Animation_Display', 'Animation_Animation_Curve', 'Animation_Pose', 'Animation_Refine_Shape', 'Animation_Extra_Tools',
'Modeling_Display', 'Modeling_Selection', 'Modeling_Edit_Component', 'Modeling_Edit_Mesh', 'Modeling_Material', 'Modeling_Extra_Tools',
'Fx_Particle', 'Fx_RBD', 'Fx_Volume', 'Fx_Fluid',
'Misc_Misc', 'Misc_Temp']
START_SHELFS = ['Rigging_Display', 'Animation_Control_Select', 'Modeling_Display', 'Fx_Particle', 'Misc_Misc']


def saveTools(*args):
    """
    Save tak_tools with current state.
    """
    # Read tool file
    with open(__file__, 'r') as f:
        contents = f.read()

    # Get shelf buttons for each shelfLayout
    for shelf in SHELF_LIST:
        btns = getBtns(shelf)

        curBtnCodes = ''

        # Get shelf button code for each shelf button
        for btn in btns:
            shelfBtnCode = getBtnInfo(btn)
            curBtnCodes += shelfBtnCode + '\n'

        # Find code block that related with specific shelf in contents
        codeBlock = re.search(r'.*%s.*\n((\s+cmds.shelfButton.*\n){0,100})' %shelf, contents).group(1)

        # Replace prior button codes to current shelf button codes in contents
        contents = contents.replace(codeBlock, curBtnCodes)

    # Save tool file
    with open(__file__, 'w') as f:
        f.write(contents)

    print('"Tak Tools" is saved successfully.')


def getBtns(layout):
    '''
    Query buttons in specific shelf.
    '''
    btns = cmds.shelfLayout(layout, q = True, childArray = True)

    return btns


def getBtnInfo(btn):
    '''
    Get button's source code.
    '''
    ano = cmds.shelfButton(btn, q = True, annotation = True)
    imgLlb = cmds.shelfButton(btn, q = True, imageOverlayLabel = True)
    img1 = cmds.shelfButton(btn, q = True, image1 = True)
    cmd = cmds.shelfButton(btn, q = True, command = True)
    srcType = cmds.shelfButton(btn, q = True, sourceType = True)

    shelfBtnCode = "    cmds.shelfButton(annotation = %s, width = 35, height = 35, imageOverlayLabel = '%s', image1 = '%s', command = %s, sourceType = '%s')" %(repr(str(ano)), imgLlb, img1,  repr(str(cmd)), srcType)

    return shelfBtnCode


def addToolUi(*args):
    '''
    UI for add a new tool to the specific shelf.
    '''
    winName = 'addToolWin'

    # Check if window exists
    if cmds.window(winName, exists = True):
        cmds.deleteUI(winName)

    # Create window
    cmds.window(winName, title = 'Add Tool')

    # Widgets

    cmds.tabLayout(tv = False)

    cmds.columnLayout('mainColLo', adj = True)

    cmds.optionMenu('shlfOptMenu', label = 'Shelf: ')
    for shelf in SHELF_LIST:
        if shelf in START_SHELFS:
            cmds.menuItem(divider=True)
        cmds.menuItem(label = shelf, p = 'shlfOptMenu')
    cmds.textFieldGrp('annoTxtFldGrp', columnWidth = [(1, 110), (2, 100)], label = 'Annotation: ')
    cmds.textFieldButtonGrp('imgTxtFldBtnGrp', columnWidth = [(1, 110), (2, 100)], label = 'Image: ', buttonLabel = '...', bc = partial(loadImgPath, 'imgTxtFldBtnGrp'))
    cmds.textFieldGrp('imgOverLblTxtFldGrp', columnWidth = [(1, 110), (2, 100)], label = 'Image Overlay Label: ')
    cmds.textFieldGrp('cmdTxtFldGrp', columnWidth = [(1, 110), (2, 100)], label = 'Command: ')
    cmds.optionMenu('srcTypeOptMenu', label = 'Source Type: ')
    cmds.menuItem(label = 'python', p = 'srcTypeOptMenu')
    cmds.menuItem(label = 'mel', p = 'srcTypeOptMenu')

    cmds.separator(h = 5, style = 'none')

    cmds.button(label = 'Apply', h = 50, c = addTool)

    # Show window
    cmds.window(winName, e = True, w = 100, h = 100)
    cmds.showWindow(winName)


def storeConfig(*args):
    configInfo = {
        'workspaceWidth': cmds.dockControl(MODULE_NAME, q=True, w=True),
    }

    with open(TAK_TOOLS_CONFIG_PATH, 'w') as f:
        json.dump(configInfo, f, indent=4)


def addTool(*args):
    '''
    Add tool with options.
    '''
    # Get options
    shlf = cmds.optionMenu('shlfOptMenu', q = True, value = True)
    anno = cmds.textFieldGrp('annoTxtFldGrp', q = True, text = True)
    img = cmds.textFieldButtonGrp('imgTxtFldBtnGrp', q = True, text = True)
    imgOverLbl = cmds.textFieldGrp('imgOverLblTxtFldGrp', q = True, text = True)
    cmd = cmds.textFieldGrp('cmdTxtFldGrp', q = True, text = True)
    srcType = cmds.optionMenu('srcTypeOptMenu', q = True, value = True)

    # Set default image when user do not define image
    if not img:
        if srcType == 'mel':
            img = 'commandButton.png'
        elif srcType == 'python':
            img = 'pythonFamily.png'

    # Evaluate command string
    eval("cmds.shelfButton(annotation = %s, width = 35, height = 35, imageOverlayLabel = '%s', image1 = '%s', command = %s, sourceType = '%s', p = '%s')" %(repr(str(anno)), imgOverLbl, img,  repr(str(cmd)), srcType, shlf))

    # Close popup window
    cmds.deleteUI('addToolWin')


def loadImgPath(widgetName, *args):
    iconImgPath = cmds.fileDialog2(fileMode = 1, caption = 'Select a Image')
    if iconImgPath:
        iconName = os.path.basename(iconImgPath[0])
        cmds.textFieldButtonGrp(widgetName, e = True, text = iconName)
