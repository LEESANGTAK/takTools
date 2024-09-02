"""
Author: Tak
Website: https://ta-note.com
Created: 12/22/2015

Description:
    Custom shelf tool to organize shelf buttons more efficiently.
"""

import os
import json
import subprocess
from functools import partial
import pprint

from maya import cmds

from .utils import system as sysUtil


SUBPROCESS_NO_WINDOW = 0x08000000

MODULE_NAME = "takTools"
MODULE_PATH = __file__.split(MODULE_NAME, 1)[0] + MODULE_NAME

CONFIG_FILENAME = "{}_config.json".format(MODULE_NAME)
TAK_TOOLS_CONFIG_PATH = cmds.internalVar(userAppDir=True) + "config"

ROW_HEIGHT = 50
NUM_ICONS_PER_ROW = 10
ICON_SIZE = 35
MARGIN = 5
SHELVES = ['Common']
START_SHELFS = ['Rigging_Display', 'Animation_Select', 'Modeling_Display', 'Fx_Particle', 'Misc_Misc']
SHELVES_DATA_PATH = '{}/data/shelves'.format(MODULE_PATH.replace('\\', '/'))

WIN_NAME = "{0}Win".format(MODULE_NAME)


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

    # Main menu
    cmds.window(WIN_NAME)
    cmds.menuBarLayout(WIN_NAME)
    cmds.menu('fileMenu', label='File', p=WIN_NAME)
    cmds.menuItem(label='Save', c=saveShelves, p='fileMenu')
    cmds.menuItem(label='Load', c=loadTaskShelves, p='fileMenu')
    cmds.menu('editMenu', label='Edit', p=WIN_NAME)
    cmds.menuItem(label='Add Tool', c=addToolUi, p='editMenu')
    cmds.menuItem(label='Store Config', c=storeConfig, p='editMenu')
    cmds.menu('helpMenu', label='Help', p=WIN_NAME)
    cmds.menuItem(label='Check Update', c=checkUpdate, p='helpMenu')

    cmds.paneLayout('mainPaneLo', configuration='horizontal2', paneSize=[(2, 50, 50)])

    cmds.columnLayout('mainColLo', adj=True)

    # Common tab
    cmds.tabLayout('cmnToolTabLo', tv=False, p='mainColLo')
    cmds.shelfLayout('Common', h=(ROW_HEIGHT * 4), parent='cmnToolTabLo')
    loadCommonShelf()

    cmds.separator('mainSep', style='in', p='mainColLo')

    # Task tabs
    cmds.tabLayout('taskTabLo', p='mainColLo')
    loadTaskShelves()

    # Outliner
    cmds.frameLayout('olFrameLo', labelVisible=False, p='mainPaneLo')
    panel = cmds.outlinerPanel()
    outliner = cmds.outlinerPanel(panel, query=True, outlinerEditor=True)
    cmds.outlinerEditor( outliner, edit=True, mainListConnection='worldList', selectionConnection='modelList', showShapes=False, showAssignedMaterials=False, showReferenceNodes=True, showReferenceMembers=True, showAttributes=False, showConnected=False, showAnimCurvesOnly=False, autoExpand=False, showDagOnly=True, ignoreDagHierarchy=False, expandConnections=False, showCompounds=True, showNumericAttrsOnly=False, highlightActive=True, autoSelectNewObjects=False, doNotSelectNewObjects=False, transmitFilters=False, showSetMembers=True, setFilter='defaultSetFilter', ignoreHiddenAttribute=False )

    # Dock window to left side
    cmds.dockControl(MODULE_NAME, area='left', content=WIN_NAME, w=workspaceWidth)


# ------------ Save & Load
def saveShelves(*args):
    for shelf in SHELVES:
        shelfInfo = {}
        shelfButtons = cmds.shelfLayout(shelf, q=True, childArray=True)
        for i, shelfButton in enumerate(shelfButtons):
            shelfButtonInfo = {
                'annotation': cmds.shelfButton(shelfButton, q=True, ann=True),
                'image1': cmds.shelfButton(shelfButton, q=True, image1=True),
                'imageOverlayLabel': cmds.shelfButton(shelfButton, q=True, imageOverlayLabel=True),
                'command': cmds.shelfButton(shelfButton, q=True, command=True),
                'sourceType': cmds.shelfButton(shelfButton, q=True, sourceType=True)
            }
            shelfInfo[i] = shelfButtonInfo

        filePath = '{}/{}.json'.format(SHELVES_DATA_PATH, shelf)
        with open(filePath, 'w') as f:
            json.dump(shelfInfo, f, indent=4)


def loadCommonShelf():
    commonShelfFile = '{}/Common.json'.format(SHELVES_DATA_PATH)
    with open(commonShelfFile, 'r') as f:
        commonShelfInfo = json.load(f)
    for index, shelfButtonInfo in commonShelfInfo.items():
        cmds.shelfButton(
            annotation=shelfButtonInfo['annotation'],
            width=ICON_SIZE, height=ICON_SIZE,
            image1=shelfButtonInfo['image1'],
            imageOverlayLabel=shelfButtonInfo['imageOverlayLabel'],
            command=shelfButtonInfo['command'],
            sourceType=shelfButtonInfo['sourceType'],
            p='Common')


def loadTaskShelves(*args):
    shelvesInfo = getTaskShelvesInfo()
    for tabName, frameInfo in shelvesInfo.items():
        tabControl = cmds.scrollLayout(childResizable=True, h=500, p='taskTabLo')
        cmds.tabLayout('taskTabLo', e=True, tabLabel=[tabControl, tabName])
        for frameName, shelfButtonInfos in frameInfo.items():
            shelfName = '{}_{}'.format(tabName, frameName)
            SHELVES.append(shelfName)
            frameLo = cmds.frameLayout(label=frameName, collapse=False, collapsable=True, p=tabControl)
            numRows = int(len(shelfButtonInfos) / NUM_ICONS_PER_ROW) + 1
            shelf = cmds.shelfLayout(shelfName, h=(ICON_SIZE + MARGIN) * numRows, p=frameLo)
            for shelfButtonInfo in shelfButtonInfos:
                cmds.shelfButton(
                    annotation=shelfButtonInfo['annotation'],
                    width=ICON_SIZE, height=ICON_SIZE,
                    image1=shelfButtonInfo['image1'],
                    imageOverlayLabel=shelfButtonInfo['imageOverlayLabel'],
                    command=shelfButtonInfo['command'],
                    sourceType=shelfButtonInfo['sourceType'],
                    p=shelf)


def getTaskShelvesInfo():
    shelvesInfo = {}

    shelfFiles = [shelfFile for shelfFile in os.listdir(SHELVES_DATA_PATH) if not 'Common' in shelfFile]

    # Get tabs
    for shelfFile in shelfFiles:
        shelfName = shelfFile.split('.')[0]
        tabName = shelfName.split('_')[0]
        shelvesInfo[tabName] = {}

    # Get frames
    for shelfFile in shelfFiles:
        shelfName = shelfFile.split('.')[0]
        splitedName = shelfName.split('_')
        tabName = splitedName[0]
        frameName = splitedName[1] if len(splitedName) == 2 else splitedName[0]
        filePath = '{}/{}'.format(SHELVES_DATA_PATH, shelfFile)
        with open(filePath, 'r') as f:
            shelfInfo = json.load(f)
        shelvesInfo[tabName][frameName] = [shelfData for index, shelfData in shelfInfo.items()]

    return shelvesInfo

# ------------


# ------------ Add Tool
def addToolUi(*args):
    '''
    UI for add a new tool to the specific shelf.
    '''
    winName = 'addToolWin'

    # Check if window exists
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    # Create window
    cmds.window(winName, title='Add Tool')

    # Widgets

    cmds.tabLayout(tv=False)

    cmds.columnLayout('mainColLo', adj=True)

    cmds.optionMenu('shlfOptMenu', label='Shelf: ')
    for shelf in SHELVES:
        if shelf in START_SHELFS:
            cmds.menuItem(divider=True)
        cmds.menuItem(label=shelf, p='shlfOptMenu')
    cmds.textFieldGrp('annoTxtFldGrp', columnWidth=[(1, 110), (2, 100)], label='Annotation: ')
    cmds.textFieldButtonGrp('imgTxtFldBtnGrp', columnWidth=[(1, 110), (2, 100)], label='Image: ', buttonLabel='...', bc=partial(loadImgPath, 'imgTxtFldBtnGrp'))
    cmds.textFieldGrp('imgOverLblTxtFldGrp', columnWidth=[(1, 110), (2, 100)], label='Image Overlay Label: ')
    cmds.textFieldGrp('cmdTxtFldGrp', columnWidth=[(1, 110), (2, 100)], label='Command: ')
    cmds.optionMenu('srcTypeOptMenu', label='Source Type: ')
    cmds.menuItem(label='python', p='srcTypeOptMenu')
    cmds.menuItem(label='mel', p='srcTypeOptMenu')

    cmds.separator(h=5, style='none')

    cmds.button(label='Apply', h=50, c=addTool)

    # Show window
    cmds.window(winName, e=True, w=100, h=100)
    cmds.showWindow(winName)


def addTool(*args):
    '''
    Add tool with options.
    '''
    # Get options
    shlf = cmds.optionMenu('shlfOptMenu', q=True, value=True)
    anno = cmds.textFieldGrp('annoTxtFldGrp', q=True, text=True)
    img = cmds.textFieldButtonGrp('imgTxtFldBtnGrp', q=True, text=True)
    imgOverLbl = cmds.textFieldGrp('imgOverLblTxtFldGrp', q=True, text=True)
    cmd = cmds.textFieldGrp('cmdTxtFldGrp', q=True, text=True)
    srcType = cmds.optionMenu('srcTypeOptMenu', q=True, value=True)

    # Set default image when user do not define image
    if not img:
        if srcType == 'mel':
            img = 'commandButton.png'
        elif srcType == 'python':
            img = 'pythonFamily.png'

    # Evaluate command string
    eval("cmds.shelfButton(annotation='%s', width=35, height=35, image1='%s', imageOverlayLabel='%s', command='%s', sourceType='%s', p='%s')".format(anno, img, imgOverLbl, cmd, srcType, shlf))

    # Close popup window
    cmds.deleteUI('addToolWin')


def loadImgPath(widgetName, *args):
    iconImgPath = cmds.fileDialog2(fileMode=1, caption='Select a Image')
    if iconImgPath:
        iconName = os.path.basename(iconImgPath[0])
        cmds.textFieldButtonGrp(widgetName, e=True, text=iconName)
# ------------


# ------------ Edit Tool
def editToolGUI(shelfLayout, index):
    cmds.window(title='Edit Tool', tlb=True)
    cmds.columnLayout(adj=True)
    cmds.textFieldGrp('annoTxtFldGrp', columnWidth=[(1, 110), (2, 100)], label='Annotation: ', text=annotation)
    cmds.textFieldButtonGrp('imgTxtFldBtnGrp', columnWidth=[(1, 110), (2, 100)], label='Image: ', buttonLabel='...', bc=partial(loadImgPath, 'imgTxtFldBtnGrp'), text=image)
    cmds.textFieldGrp('imgOverLblTxtFldGrp', columnWidth=[(1, 110), (2, 100)], label='Image Overlay Label: ', text=imageOverlayLabel)
    cmds.textFieldGrp('cmdTxtFldGrp', columnWidth=[(1, 110), (2, 100)], label='Command: ', text=command)
    cmds.optionMenu('srcTypeOptMenu', label='Source Type: ')
    cmds.menuItem(label='python', p='srcTypeOptMenu')
    cmds.menuItem(label='mel', p='srcTypeOptMenu')
    cmds.separator(h=5, style='none')
    cmds.button(label='Apply', h=50, c='')
    cmds.showWindow()
    cmds.optionMenu('srcTypeOptMenu', e=True, value=sourceType)
# ------------


# ------------ Git Utils
def checkUpdate(self):
    if isOutdated():
        result = cmds.confirmDialog(
            title=MODULE_NAME,
            message="New version is detected. Do you want to update?",
            button=['Yes','No'],
            defaultButton='Yes',
            cancelButton='No',
            dismissString='No'
        )
        if 'Yes' == result:
            succeed = update()
            if succeed:
                import takTools.tak_tools as tt
                import imp; imp.reload(tt)
                tt.UI()
    else:
        cmds.confirmDialog(title=MODULE_NAME, message='You have latest version.\nEnjoy!')


def isOutdated():
    # Navigate to the specific repository
    os.chdir(MODULE_PATH)

    try:
        # Fetch the latest commits from the remote repository
        subprocess.call(["git", "fetch"], creationflags=SUBPROCESS_NO_WINDOW)

        # Get the local and remote HEAD commit hashes
        local_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], creationflags=SUBPROCESS_NO_WINDOW).strip()
        remote_commit = subprocess.check_output(["git", "rev-parse", "@{u}"], creationflags=SUBPROCESS_NO_WINDOW).strip()

        # Compare the local and remote commits
        if local_commit != remote_commit:
            return True  # Local repo is outdated

    except subprocess.CalledProcessError as e:
        print("Error: {}".format(e))
        return False

    return False  # Local repo is up-to-date


def update():
    try:
        # Pull the latest changes from the remote repository
        subprocess.call(["git", "pull"], creationflags=SUBPROCESS_NO_WINDOW)
        print("Update is done successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to update: {}".format(e))
        return False
# ------------



def storeConfig(*args):
    configInfo = {
        'workspaceWidth': cmds.dockControl(MODULE_NAME, q=True, w=True),
    }

    with open(TAK_TOOLS_CONFIG_PATH, 'w') as f:
        json.dump(configInfo, f, indent=4)
