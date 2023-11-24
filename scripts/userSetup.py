import pymel.core as pm
import maya.cmds as cmds


cmds.undoInfo(state=True, infinity=True)
cmds.optionVar(iv=("undoIsInfinite", 1))

cmds.optionVar(iv=("isIncrementalSaveEnabled", 0))
pm.evalDeferred("cmds.keyTangent(e=True, g=True, itt='linear')", lowestPriority=True)
pm.evalDeferred("cmds.keyTangent(e=True, g=True, ott='linear')", lowestPriority=True)


try:
    pm.commandPort(n=':20200', sourceType='mel')
    pm.commandPort(n=':20201', sourceType='python')
except:
    pass


pm.evalDeferred("import takTools.pipeline.takToolsMenu as takToolsMenu;takToolsMenu.showMenu()", lowestPriority=True)
pm.evalDeferred("from takTools.utils import qtUtil;qtUtil.editScriptEditorHorizontal()", lowestPriority=True)
pm.evalDeferred("from takTools import tak_tools;tak_tools.UI()", lowestPriority=True)
pm.evalDeferred("from takTools.common import errorFix_look", lowestPriority=True)
