"""
Author: Tak
Website: https://ta-note.com
Description:
    Drag and drop this file to the maya viewport.
    "<ModuleName>.mod" file will be created in the "Documents\maya\modules" directory.
"""

import os
import sys
import imp
import shutil

from maya import cmds, mel


MODULE_NAME = 'takTools'
RAW_MODULE_PATH = os.path.dirname(__file__).replace('\\', '/')
MODULE_PATH = '{}scripts/{}'.format(cmds.internalVar(userAppDir=True), MODULE_NAME)
MAYA_VERSION = int(cmds.about(version=True))
# Need to modify below depend on module
AVAILABLE_VERSIONS = [2020, 2022, 2024]
MODULE_VERSION = 'any'


def onMayaDroppedPythonFile(*args, **kwargs):
    removeOldInstallModule()
    copyModuleFiles()
    addEnvPaths()
    runScripts()
    createModuleFile()
    cmds.confirmDialog(title='Info', message='"{}" module installed successfully.'.format(MODULE_NAME))


def removeOldInstallModule():
    foundOldInstall = False
    for modName in sys.modules:
        if modName == 'install':
            foundOldInstall = True
            break
    if foundOldInstall:
        del(sys.modules[modName])


def copyModuleFiles():
    for item in os.listdir(RAW_MODULE_PATH):
        if item == '.gitignore':
            continue
        rawPath = '{}/{}'.format(RAW_MODULE_PATH, item)
        userPath = '{}/{}'.format(MODULE_PATH, item)
        try:
            shutil.copytree(rawPath, userPath)
        except:
            shutil.copyfile(rawPath, userPath)


def runScripts():
    # Install python packages. Packages will be installed in "C:\Users\<User Name>\AppData\Roaming\Python\<Python Version>\site-packages"
    os.putenv('MayaVersion', str(MAYA_VERSION))
    os.system('{}/bat/install_python_packages.bat'.format(MODULE_PATH))

    imp.load_source('', '{}/scripts/userSetup.py'.format(MODULE_PATH))


def addEnvPaths():
    # Add python paths
    pythonPaths = [
        '{}/scripts'.format(MODULE_PATH),
    ]
    for pythonPath in pythonPaths:
        sys.path.append(pythonPath)

    # Add mel script paths
    melScriptPaths = mel.eval('getenv "MAYA_SCRIPT_PATH";')
    melScriptPaths += ';{}/scripts/mel'.format(MODULE_PATH)
    mel.eval('putenv "MAYA_SCRIPT_PATH" "{}";'.format(melScriptPaths))
    mel.eval('rehash();')

    # Add plug-ins paths
    pluginsPaths = mel.eval('getenv "MAYA_PLUG_IN_PATH";')
    pluginsPaths += ';{}/plug-ins'.format(MODULE_PATH)
    pluginsPaths += ';{}/plug-ins/{}'.format(MODULE_PATH, MAYA_VERSION)
    mel.eval('putenv "MAYA_PLUG_IN_PATH" "{}";'.format(pluginsPaths))

    # Add icon folder path
    iconPaths = mel.eval('getenv "XBMLANGPATH";')
    iconPaths += ';{}/icons'.format(MODULE_PATH)
    mel.eval('putenv "XBMLANGPATH" "{}";'.format(iconPaths))


# Folders in the module directory that named as "icons, plug-ins, scripts" are automatically added to the maya environment variables.
def createModuleFile():
    moduleFileName = '{}.mod'.format(MODULE_NAME)

    contentsBlock = '''+ MAYAVERSION:{0} {1} {2} {3}
MAYA_SCRIPT_PATH +:= scripts/mel
MAYA_PLUG_IN_PATH +:= plug-ins/{0}

'''
    contents = ''
    for availVersion in AVAILABLE_VERSIONS:
        contents += contentsBlock.format(availVersion, MODULE_NAME, MODULE_VERSION, MODULE_PATH)

    with open(os.path.join(getModulesDirectory(), moduleFileName), 'w') as f:
        f.write(contents)


def getModulesDirectory():
    modulesDir = None

    mayaAppDir = cmds.internalVar(uad=True)
    modulesDir = os.path.join(mayaAppDir, 'modules')

    if not os.path.exists(modulesDir):
        os.mkdir(modulesDir)

    return modulesDir
