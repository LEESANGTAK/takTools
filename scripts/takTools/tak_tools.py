"""
Author: Tak
Website: https://ta-note.com
Created: 12/22/2015

Description:
    Custom shelf tool to organize shelf buttons more efficiently.
"""

import os
import json
import shutil
import subprocess
from functools import partial
from collections import OrderedDict

from maya import cmds

from imp import reload
from .pipeline import takMayaResourceBrowser as tmrb; reload(tmrb)
from .utils import system as sysUtil


# Preferences
ICON_SIZE = 32
NUM_ICONS_PER_ROW = 10
COMMON_TAB_NUM_ROWS = 3
OUTLINER_PERCENTAGE = 60

# Size values are based on 4k(3840*2160) monitor
# Caculate scale factor depend on monitor height
DEFAULT_DISPLAY_HEIGHT = 2160
sysObj = sysUtil.System()
scaleFactor = sysObj.screenHeight / float(DEFAULT_DISPLAY_HEIGHT)

ICON_MARGINE = 6 * scaleFactor
PANE_WIDTH = ICON_SIZE * (NUM_ICONS_PER_ROW + 1)
COMMON_TAB_HEIGHT = (ICON_SIZE + ICON_MARGINE) * COMMON_TAB_NUM_ROWS
COMMON_TAB_PERCENTAGE = (COMMON_TAB_HEIGHT / float(sysObj.screenHeight)) * 100
ADAPTED_OULINER_PERCENTAGE = OUTLINER_PERCENTAGE + COMMON_TAB_PERCENTAGE
SCROLL_AREA_HEIGHT = (sysObj.screenHeight - COMMON_TAB_HEIGHT) * ((100-ADAPTED_OULINER_PERCENTAGE) * 0.01)

SHELVES = ['Common']
MODULE_NAME = "takTools"
MODULE_PATH = __file__.split(MODULE_NAME, 1)[0] + MODULE_NAME
SHELVES_DATA_PATH = '{}/data/shelves'.format(MODULE_PATH.replace('\\', '/'))

WIN_NAME = "{0}Win".format(MODULE_NAME)

SUBPROCESS_NO_WINDOW = 0x08000000


def UI():
    if cmds.window(WIN_NAME, exists=True):
        cmds.deleteUI(WIN_NAME)
    if cmds.dockControl(MODULE_NAME, exists=True):
        cmds.deleteUI(MODULE_NAME)

    cmds.window(WIN_NAME)

    # Main menu
    cmds.menuBarLayout(WIN_NAME)
    cmds.menu('fileMenu', label='File', p=WIN_NAME)
    cmds.menuItem(label='Save', c=saveShelves, p='fileMenu')
    cmds.menu('editMenu', label='Edit', p=WIN_NAME)
    cmds.menuItem(label='Add Tool', c=addToolGUI, p='editMenu')
    cmds.menuItem(label='Edit Tool', c=editToolGUI, p='editMenu')
    cmds.menuItem(divider=True)
    cmds.menuItem(label='Preferences', c=prefsGUI, p='editMenu')
    cmds.menu('helpMenu', label='Help', p=WIN_NAME)
    cmds.menuItem(label='Check Update', c=checkUpdate, p='helpMenu')

    cmds.paneLayout('mainPaneLo', configuration='horizontal2', w=PANE_WIDTH, paneSize=[(2, 50, ADAPTED_OULINER_PERCENTAGE)])

    cmds.columnLayout('mainColLo', adj=True)

    # Common tab
    cmds.tabLayout('cmnToolTabLo', tv=False, p='mainColLo')
    cmds.shelfLayout('Common', h=COMMON_TAB_HEIGHT, parent='cmnToolTabLo')
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
    cmds.dockControl(MODULE_NAME, area='left', content=WIN_NAME)


# ------------ Save & Load
def saveShelves(*args):
    for shelf in SHELVES:
        shelfInfo = OrderedDict()
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
        commonShelfInfo = json.load(f, object_pairs_hook=OrderedDict)
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
        tabControl = cmds.scrollLayout(childResizable=True, h=SCROLL_AREA_HEIGHT, p='taskTabLo')
        cmds.tabLayout('taskTabLo', e=True, tabLabel=[tabControl, tabName])
        for frameName, shelfButtonInfos in frameInfo.items():
            shelfName = '{}_{}'.format(tabName, frameName)
            SHELVES.append(shelfName)
            frameLo = cmds.frameLayout(label=frameName, collapse=False, collapsable=True, p=tabControl)
            numRows = int(len(shelfButtonInfos) / NUM_ICONS_PER_ROW) + 1
            shelf = cmds.shelfLayout(shelfName, ch=((ICON_SIZE + ICON_MARGINE) * numRows), p=frameLo)
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
    shelvesInfo = OrderedDict()

    shelfFiles = [shelfFile for shelfFile in os.listdir(SHELVES_DATA_PATH) if not 'Common' in shelfFile]

    # Get tabs
    for shelfFile in shelfFiles:
        shelfName = shelfFile.split('.')[0]
        tabName = shelfName.split('_')[0]
        shelvesInfo[tabName] = OrderedDict()

    # Get frames
    for shelfFile in shelfFiles:
        shelfName = shelfFile.split('.')[0]
        splitedName = shelfName.split('_')
        tabName = splitedName[0]
        frameName = splitedName[1] if len(splitedName) == 2 else splitedName[0]
        filePath = '{}/{}'.format(SHELVES_DATA_PATH, shelfFile)
        with open(filePath, 'r') as f:
            shelfInfo = json.load(f, object_pairs_hook=OrderedDict)
        shelvesInfo[tabName][frameName] = [shelfData for index, shelfData in shelfInfo.items()]

    return shelvesInfo

# ------------


# ------------ Add Tool
def addToolGUI(*args):
    '''
    UI for add a new tool to the specific shelf.
    '''
    winName = 'addToolWin'

    # Check if window exists
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    # Create window
    cmds.window(winName, title='Add Tool', tlb=True)

    # Widgets

    cmds.tabLayout(tv=False)

    cmds.columnLayout('mainColLo', adj=True)

    cmds.optionMenu('shlfOptMenu', label='Shelf: ')
    for shelf in SHELVES:
        cmds.menuItem(label=shelf, p='shlfOptMenu')
    cmds.textFieldGrp('annoTxtFldGrp', columnWidth=[(1, 110), (2, 100)], label='Annotation: ')

    cmds.rowLayout(numberOfColumns=2)
    cmds.textFieldButtonGrp('imgTxtFldBtnGrp', columnWidth=[(1, 110), (2, 100)], label='Image: ', buttonLabel='...', bc=partial(loadImgPath, 'imgTxtFldBtnGrp'))
    cmds.symbolButton(image='imageDisplay.png', c=tmrb.TakMayaResourceBrowser.showUI)

    cmds.setParent('..')
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
    shelf = cmds.optionMenu('shlfOptMenu', q=True, value=True)
    annotation = cmds.textFieldGrp('annoTxtFldGrp', q=True, text=True)
    image1 = cmds.textFieldButtonGrp('imgTxtFldBtnGrp', q=True, text=True)
    imageOverlayLabel = cmds.textFieldGrp('imgOverLblTxtFldGrp', q=True, text=True)
    command = cmds.textFieldGrp('cmdTxtFldGrp', q=True, text=True)
    sourcType = cmds.optionMenu('srcTypeOptMenu', q=True, value=True)

    # Set default image when user do not define image
    if not image1:
        if sourcType == 'mel':
            image1 = 'commandButton.png'
        elif sourcType == 'python':
            image1 = 'pythonFamily.png'

    # Evaluate command string
    cmds.shelfButton(
        annotation=annotation,
        width=ICON_SIZE, height=ICON_SIZE,
        image1=image1, imageOverlayLabel=imageOverlayLabel,
        command=command, sourceType=sourcType,
        p=shelf
    )

    # Close popup window
    cmds.deleteUI('addToolWin')


def loadImgPath(widgetName, *args):
    iconImgPath = cmds.fileDialog2(fileMode=1, caption='Select a Image')
    if iconImgPath:
        iconName = os.path.basename(iconImgPath[0])
        cmds.textFieldButtonGrp(widgetName, e=True, text=iconName)
# ------------


# ------------ Preferences
def prefsGUI(*args):
    print('prefsGUI()')
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
                copyPreferences()
                import takTools.tak_tools as tt
                import imp; imp.reload(tt); tt.UI()
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


def copyPreferences():
    # Copy preferences files
    prefsDir = '{}/prefs'.format(MODULE_PATH)
    mayaPrefDir = '{}/{}/prefs'.format(cmds.internalVar(uad=True), int(cmds.about(version=True)))
    shutil.copytree(prefsDir, mayaPrefDir, dirs_exist_ok=True)
# ------------
