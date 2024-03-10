"""
Author: Tak
Website: https://ta-note.com
Description:
    Drag and drop install.py file in maya viewport.
    "<moduleName>.mod" file will created in "Documents\maya\modules" directory automatically.
"""

import os
import sys
import imp

from maya import cmds, mel


MODULE_PATH = os.path.dirname(__file__).replace('\\', '/')
MODULE_NAME = MODULE_PATH.rsplit('/', 1)[-1]
MAYA_VERSION = int(cmds.about(version=True))
# Need to modify below depend on module
MODULE_VERSION = 'any'
# SHELF_ICON_FILE = <'icon.png'>
# SHELF_BUTTON_COMMAND = <'''
# Write command here
# '''>


def onMayaDroppedPythonFile(*args, **kwargs):
    createModuleFile()
    addEnvPaths()
    # addShelfButtons()
    run()
    cmds.confirmDialog(title='Info', message='"{}" module installed successfully.'.format(MODULE_NAME))


# Folders in the module directory that named as "icons, plug-ins, scripts" are automatically added to the maya environment variables.
def createModuleFile():
    moduleFileName = '{}.mod'.format(MODULE_NAME)

    contents = '''+ MAYAVERSION:2020 {0} {1} {2}
MAYA_PLUG_IN_PATH +:= plug-ins/2020
MAYA_SCRIPT_PATH +:= scripts/mel

+ MAYAVERSION:2022 {0} {1} {2}
MAYA_PLUG_IN_PATH +:= plug-ins/2022
MAYA_SCRIPT_PATH +:= scripts/mel

+ MAYAVERSION:2023 {0} {1} {2}
MAYA_PLUG_IN_PATH +:= plug-ins/2023
MAYA_SCRIPT_PATH +:= scripts/mel

+ MAYAVERSION:2024 {0} {1} {2}
MAYA_PLUG_IN_PATH +:= plug-ins/2024
MAYA_SCRIPT_PATH +:= scripts/mel
'''.format(MODULE_NAME, MODULE_VERSION, MODULE_PATH)

    with open(os.path.join(getModulesDirectory(), moduleFileName), 'w') as f:
        f.write(contents)


def getModulesDirectory():
    modulesDir = None

    mayaAppDir = cmds.internalVar(uad=True)
    modulesDir = os.path.join(mayaAppDir, 'modules')

    if not os.path.exists(modulesDir):
        os.mkdir(modulesDir)

    return modulesDir


def addEnvPaths():
    # Add plug-ins paths
    pluginsPaths = mel.eval('getenv "MAYA_PLUG_IN_PATH";')
    pluginsPaths += ';{}/plug-ins'.format(MODULE_PATH)
    pluginsPaths += ';{}/plug-ins/{}'.format(MODULE_PATH, MODULE_VERSION)
    mel.eval('putenv "MAYA_PLUG_IN_PATH" "{}";'.format(pluginsPaths))

    # Add mel script paths
    melScriptPaths = mel.eval('getenv "MAYA_SCRIPT_PATH";')
    melScriptPaths += ';{}/scripts/mel'.format(MODULE_PATH)
    mel.eval('putenv "MAYA_SCRIPT_PATH" "{}";'.format(melScriptPaths))
    mel.eval('rehash();')

    # Add python script paths
    pythonPath = '{}/scripts'.format(MODULE_PATH)
    if not pythonPath in sys.path:
        sys.path.append(pythonPath)


# def addShelfButtons():
#     curShelf = getCurrentShelf()

#     cmds.shelfButton(
#         command=SHELF_BUTTON_COMMAND,
#         annotation=MODULE_NAME,
#         sourceType='Python',
#         image=SHELF_ICON_FILE,
#         image1=SHELF_ICON_FILE,
#         parent=curShelf
#     )


# def getCurrentShelf():
#     curShelf = None

#     shelf = mel.eval('$gShelfTopLevel = $gShelfTopLevel')
#     curShelf = cmds.tabLayout(shelf, query=True, selectTab=True)

#     return curShelf


def run():
    imp.load_source('', '{}/scripts/userSetup.py'.format(MODULE_PATH))
