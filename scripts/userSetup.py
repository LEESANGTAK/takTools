import maya.cmds as cmds


cmds.undoInfo(state=True, infinity=True)
cmds.optionVar(iv=("undoIsInfinite", 1))

cmds.optionVar(iv=("isIncrementalSaveEnabled", 0))
cmds.evalDeferred("cmds.keyTangent(e=True, g=True, itt='linear')", lowestPriority=True)
cmds.evalDeferred("cmds.keyTangent(e=True, g=True, ott='linear')", lowestPriority=True)


try:
    cmds.commandPort(n=':20200', sourceType='mel')
    cmds.commandPort(n=':20201', sourceType='python')
except:
    pass


cmds.evalDeferred("import takTools.takToolsMenu as takToolsMenu;takToolsMenu.showMenu()", lowestPriority=True)
cmds.evalDeferred("from takTools import tak_tools;tak_tools.UI()", lowestPriority=True)
cmds.evalDeferred("from takTools.common import errorFix_look", lowestPriority=True)
