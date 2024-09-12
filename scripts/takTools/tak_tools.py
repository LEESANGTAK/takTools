"""
Author: Tak
Website: https://ta-note.com
Created: 12/22/2015

Description:
    Custom shelf tool to organize shelf buttons more efficiently.
"""

import os
import json
import pprint
from distutils.dir_util import copy_tree
import subprocess
from functools import partial
from collections import OrderedDict

from maya import cmds

from imp import reload
from .pipeline import takMayaResourceBrowser as tmrb; reload(tmrb)
from .utils import system as sysUtil


# Version constants
VERSION_MAJOR = 2
VERSION_MINOR = 0
VERSION_MICRO = 0

# Size values are based on 4k(3840*2160) monitor
# Caculate scale factor depend on monitor height
DEFAULT_DISPLAY_HEIGHT = 2160
sysObj = sysUtil.System()
scaleFactor = sysObj.screenHeight / float(DEFAULT_DISPLAY_HEIGHT)

# Preferences
ICON_SIZE = 32
ICON_MARGINE = 6
NUM_ICONS_PER_ROW = 10
COMMON_TAB_NUM_ROWS = 3
OUTLINER_PERCENTAGE = 50 * scaleFactor

PANE_WIDTH = ICON_SIZE * (NUM_ICONS_PER_ROW + 1)
COMMON_TAB_HEIGHT = (ICON_SIZE + ICON_MARGINE) * COMMON_TAB_NUM_ROWS
COMMON_TAB_PERCENTAGE = (COMMON_TAB_HEIGHT / float(sysObj.screenHeight)) * 100
ADAPTED_OULINER_PERCENTAGE = OUTLINER_PERCENTAGE + COMMON_TAB_PERCENTAGE
SCROLL_AREA_HEIGHT = sysObj.screenHeight * ((100-ADAPTED_OULINER_PERCENTAGE) * 0.01) * 0.5

SHELVES = ['Common']
MODULE_NAME = "takTools"
TOOL_NAME = 'Tak Tools'
MODULE_PATH = __file__.split(MODULE_NAME, 1)[0] + MODULE_NAME
SHELVES_DATA_PATH = '{}/data/shelves'.format(MODULE_PATH.replace('\\', '/'))

WIN_NAME = "{0}Win".format(MODULE_NAME)
WIN_TITLE = '{} {}.{}.{}'.format(TOOL_NAME, VERSION_MAJOR, VERSION_MINOR, VERSION_MICRO)

SUBPROCESS_NO_WINDOW = 0x08000000

SOURCE_TYPE_MAPPING = {'mel': 1, 'python': 2}


# Global variables
commonShelfInfo = {}
taskShelvesInfo = {}
allShelfButtons = {}


def UI():
    if cmds.window(WIN_NAME, exists=True):
        cmds.deleteUI(WIN_NAME)
    if cmds.dockControl(MODULE_NAME, exists=True):
        cmds.deleteUI(MODULE_NAME)

    cmds.window(WIN_NAME, title=WIN_TITLE, tlb=True)

    # Main menu
    cmds.menuBarLayout(WIN_NAME)
    cmds.menu('editMenu', label='Edit', p=WIN_NAME)
    cmds.menuItem(label='Add...', c=addToolGUI, p='editMenu')
    cmds.menuItem(label='Editor...', c=editorGUI, p='editMenu')
    cmds.menuItem(label='Preferences', c=prefsGUI, p='editMenu')
    cmds.menu('helpMenu', label='Help', p=WIN_NAME)
    cmds.menuItem(label='Check Update', c=checkUpdate, p='helpMenu')
    cmds.menuItem(label='About', c='', p='helpMenu')

    cmds.paneLayout('mainPaneLo', configuration='horizontal2', w=PANE_WIDTH, paneSize=[(2, 50, 90)])

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
    cmds.dockControl(MODULE_NAME, label=WIN_TITLE, area='left', content=WIN_NAME)


# ------------ Save & Load
def loadCommonShelf():
    global allShelfButtons
    global commonShelfInfo

    commonShelfFile = '{}/Common.json'.format(SHELVES_DATA_PATH)
    with open(commonShelfFile, 'r') as f:
        commonShelfInfo = json.load(f, object_pairs_hook=OrderedDict)
    for shelfButtonInfo in commonShelfInfo.get('shelfButtonInfos'):
        shelfBtn = cmds.shelfButton(
            label=shelfButtonInfo.get('label'),
            annotation=shelfButtonInfo.get('annotation'),
            width=ICON_SIZE, height=ICON_SIZE,
            image1=shelfButtonInfo.get('image1'),
            imageOverlayLabel=shelfButtonInfo.get('imageOverlayLabel'),
            command=shelfButtonInfo.get('command'),
            sourceType=shelfButtonInfo.get('sourceType'),
            noDefaultPopup=shelfButtonInfo.get('noDefaultPopup'),
            p='Common')
        allShelfButtons[shelfButtonInfo.get('label')] = shelfBtn


def loadTaskShelves(*args):
    global allShelfButtons
    global taskShelvesInfo

    taskShelvesInfo = getTaskShelvesInfo()

    for tabName, frameInfo in taskShelvesInfo.items():
        # Create tab for shelves
        tabControl = cmds.scrollLayout(childResizable=True, h=SCROLL_AREA_HEIGHT, p='taskTabLo')
        cmds.tabLayout('taskTabLo', e=True, tabLabel=[tabControl, tabName])

        for frameName, frameData in frameInfo.items():
            shelfName = '{}_{}'.format(tabName, frameName)

            # Create frame layout with frame data
            frameLo = cmds.frameLayout(shelfName, label=frameName, collapsable=True, collapse=frameData.get('collapse'), p=tabControl)

            # Add shelf buttons to the shelf layout in the frame layout
            shelfButtonInfos = frameData.get('shelfButtonInfos')
            numRows = int(len(shelfButtonInfos) / NUM_ICONS_PER_ROW) + 1
            shelf = cmds.shelfLayout(shelfName, ch=((ICON_SIZE + ICON_MARGINE) * numRows), p=frameLo)
            for shelfButtonInfo in shelfButtonInfos:
                shelfBtn = cmds.shelfButton(
                    label=shelfButtonInfo.get('label'),
                    annotation=shelfButtonInfo.get('annotation'),
                    width=ICON_SIZE, height=ICON_SIZE,
                    image1=shelfButtonInfo.get('image1'),
                    imageOverlayLabel=shelfButtonInfo.get('imageOverlayLabel'),
                    command=shelfButtonInfo.get('command'),
                    sourceType=shelfButtonInfo.get('sourceType'),
                    noDefaultPopup=shelfButtonInfo.get('noDefaultPopup'),
                    p=shelf)
                allShelfButtons[shelfButtonInfo.get('label')] = shelfBtn

            SHELVES.append(shelfName)


def getTaskShelvesInfo():
    taskShelvesInfo = OrderedDict()
    taskShelfFiles = [shelfFile for shelfFile in os.listdir(SHELVES_DATA_PATH) if not 'Common' in shelfFile]

    # Read shelves info in order
    taksShelvesInfo = []
    for taskShelfFile in taskShelfFiles:
        filePath = '{}/{}'.format(SHELVES_DATA_PATH, taskShelfFile)
        with open(filePath, 'r') as f:
            shelfInfo = json.load(f, object_pairs_hook=OrderedDict)
            taksShelvesInfo.append(shelfInfo)
    orderedTaskShlvesInfos = sorted(taksShelvesInfo, key=lambda item: item.get('order'))

    # Get tab data
    for taskShelfInfo in orderedTaskShlvesInfos:
        tabName = taskShelfInfo.get('tabName')
        taskShelvesInfo[tabName] = OrderedDict()

    # Get frame data
    for taskShelfInfo in orderedTaskShlvesInfos:
        tabName = taskShelfInfo.get('tabName')
        frameName = taskShelfInfo.get('frameName')
        taskShelvesInfo[tabName][frameName] = OrderedDict()
        taskShelvesInfo[tabName][frameName]['collapse'] = taskShelfInfo.get('collapse')
        taskShelvesInfo[tabName][frameName]['shelfButtonInfos'] = taskShelfInfo.get('shelfButtonInfos')

    return taskShelvesInfo


def saveShelves(*args):
    for i, shelf in enumerate(SHELVES):
        shelfInfo = OrderedDict()

        if not shelf == 'Common':
            tabName, frameName = shelf.split('_')
            shelfInfo['order'] = str(i).zfill(2)
            shelfInfo['tabName'] = tabName
            shelfInfo['frameName'] = frameName
            shelfInfo['collapse'] = cmds.frameLayout(shelf, q=True, collapse=True)

        shelfButtonInfos = []
        shelfButtons = cmds.shelfLayout(shelf, q=True, childArray=True)
        for shelfButton in shelfButtons:
            label = cmds.shelfButton(shelfButton, q=True, label=True) or cmds.shelfButton(shelfButton, q=True, command=True)[:20] + '...' + cmds.shelfButton(shelfButton, q=True, command=True)[-20:]
            shelfButtonInfo = {
                'label': label,
                'annotation': cmds.shelfButton(shelfButton, q=True, ann=True),
                'image1': cmds.shelfButton(shelfButton, q=True, image1=True),
                'imageOverlayLabel': cmds.shelfButton(shelfButton, q=True, imageOverlayLabel=True),
                'command': cmds.shelfButton(shelfButton, q=True, command=True),
                'sourceType': cmds.shelfButton(shelfButton, q=True, sourceType=True),
                'noDefaultPopup': True
            }
            shelfButtonInfos.append(shelfButtonInfo)
        shelfInfo['shelfButtonInfos'] = shelfButtonInfos

        filePath = '{}/{}.json'.format(SHELVES_DATA_PATH, shelf)
        with open(filePath, 'w') as f:
            json.dump(shelfInfo, f, indent=4)
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
    cmds.textFieldGrp('labelTxtFldGrp', cw=[(1, 100), (2, 100)], label='label: ')
    cmds.textFieldGrp('annoTxtFldGrp', cw=[(1, 100), (2, 100)], label='Annotation: ')

    cmds.rowLayout(numberOfColumns=3)
    cmds.textFieldGrp('imgTxtFldGrp', cw=[(1, 100), (2, 100)], label='Image: ')
    cmds.symbolButton(image='fileOpen.png', c=partial(loadImgPath, 'imgTxtFldGrp'))
    cmds.symbolButton(image='factoryIcon.png', c=tmrb.TakMayaResourceBrowser.showUI)

    cmds.setParent('..')
    cmds.textFieldGrp('imgOverLblTxtFldGrp', cw=[(1, 100), (2, 100)], label='Image Overlay Label: ')
    cmds.textFieldGrp('cmdTxtFldGrp', cw=[(1, 100), (2, 100)], label='Command: ')
    cmds.optionMenu('srcTypeOptMenu', label='Source Type: ')
    cmds.menuItem(label='python', p='srcTypeOptMenu')
    cmds.menuItem(label='mel', p='srcTypeOptMenu')

    cmds.separator(h=5, style='none')

    cmds.button(label='Apply', h=50, c=addTool)

    # Show window
    cmds.window(winName, e=True, w=10, h=10)
    cmds.showWindow(winName)


def addTool(*args):
    '''
    Add tool with options.
    '''
    # Get options
    label = cmds.textFieldGrp('labelTxtFldGrp', q=True, text=True)
    annotation = cmds.textFieldGrp('annoTxtFldGrp', q=True, text=True)
    image1 = cmds.textFieldGrp('imgTxtFldGrp', q=True, text=True)
    imageOverlayLabel = cmds.textFieldGrp('imgOverLblTxtFldGrp', q=True, text=True)
    command = cmds.textFieldGrp('cmdTxtFldGrp', q=True, text=True)
    sourcType = cmds.optionMenu('srcTypeOptMenu', q=True, value=True)
    shelf = cmds.optionMenu('shlfOptMenu', q=True, value=True)

    # Set default image when user do not define image
    if not image1:
        if sourcType == 'mel':
            image1 = 'commandButton.png'
        elif sourcType == 'python':
            image1 = 'pythonFamily.png'

    # Evaluate command string
    cmds.shelfButton(
        label=label,
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
        cmds.textFieldGrp(widgetName, e=True, text=iconName)
# ------------


# ------------ Preferences
def prefsGUI(*args):
    print('prefsGUI()')
# ------------


# ------------ Edit Tool
COLUMN_WIDTH = 200
def editorGUI(*args):
    winName = 'editorWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)
    cmds.window(winName, title='Tak Tools Editor', tlb=True, p=WIN_NAME)

    cmds.tabLayout(tv=False)
    cmds.columnLayout('mainColLo', adj=True)

    # Shelves and Shelf Contents
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, COLUMN_WIDTH), (3, COLUMN_WIDTH)])

    cmds.frameLayout(label='Shelves')
    cmds.columnLayout(adj=True)
    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.symbolButton(image='moveLayerUp.png')
    cmds.symbolButton(image='moveLayerDown.png')
    cmds.symbolButton(image='newLayerEmpty.png')
    cmds.symbolButton(image='delete.png')
    cmds.setParent('..')
    cmds.textFieldGrp('shelfNameTxtFldGrp', columnWidth=[(1, 45), (2, COLUMN_WIDTH*0.5)], label='Rename: ')
    cmds.textScrollList('shevesTxtScrLs', sc=shelvesSelectCallback)

    cmds.setParent('..')
    cmds.setParent('..')
    cmds.separator(w=5, style='none')

    cmds.frameLayout(label='Shelf Contents')
    cmds.columnLayout(adj=True)
    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.symbolButton(image='moveLayerUp.png')
    cmds.symbolButton(image='moveLayerDown.png')
    cmds.symbolButton(image='newLayerEmpty.png')
    cmds.symbolButton(image='delete.png')
    cmds.setParent('..')
    cmds.textFieldGrp('shelfBtnLabelTxtFldGrp', columnWidth=[(1, 45), (2, COLUMN_WIDTH*0.5)], label='Rename: ')
    cmds.textScrollList('shelfContentsTxtScrLs', sc=shelfContentsSelectCallback)

    # Contents of a Shelf Button
    cmds.setParent('mainColLo')
    cmds.rowColumnLayout(numberOfColumns=2, columnAlign=[(1, 'right')])

    cmds.text(label='Icon Preview: ')
    cmds.shelfButton('iconPrevShelfBtn', w=ICON_SIZE, h=ICON_SIZE)

    cmds.text(label='Icon Name: ')
    cmds.rowColumnLayout(numberOfColumns=3)
    cmds.textField('iconNameTxtFld', w=(COLUMN_WIDTH*2)-110, cc=updateIcon)
    cmds.symbolButton(image='fileOpen.png')
    cmds.symbolButton(image='factoryIcon.png')

    cmds.setParent('..')
    cmds.text('Icon Label: ')
    cmds.textField('iconLabelTxtFld')

    cmds.text(label='Tooltip: ')
    cmds.textField('tooltipTxtFld')

    cmds.text('Command: ')
    cmds.columnLayout(adj=True)
    cmds.radioButtonGrp('langRadioBtnGrp', label='Language: ', labelArray2=['MEL', 'Python'], numberOfRadioButtons=2, select=2, columnWidth=[(1, 50), (2, 50)])
    cmds.scrollField('cmdScrFld', w=(COLUMN_WIDTH*2)-110, h=100)

    # Buttons
    cmds.setParent('mainColLo')
    cmds.rowColumnLayout(numberOfColumns=2, columnOffset=[(2, 'left', 5)])
    cmds.button(label='Save All Shelves', w=COLUMN_WIDTH, c=saveShelves)
    cmds.button(label='Close', w=COLUMN_WIDTH, c=lambda x: cmds.deleteUI(winName))

    cmds.window(winName, e=True, w=10, h=10)
    cmds.showWindow(winName)

    populateShelvesTextScrollList()


def populateShelvesTextScrollList():
    for shelf in SHELVES:
        cmds.textScrollList('shevesTxtScrLs', e=True, append=shelf)


def shelvesSelectCallback(*args):
    # Populate shelf contents text scroll list
    cmds.textScrollList('shelfContentsTxtScrLs', e=True, removeAll=True)

    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]

    shelfContents = None
    if selShelf == 'Common':
        shelfContents = [shelfButtonInfo.get('label') for shelfButtonInfo in commonShelfInfo.get('shelfButtonInfos')]
    else:
        tabName, frameName = selShelf.split('_')
        shelfContents = [shelfButtonInfo.get('label') for shelfButtonInfo in taskShelvesInfo.get(tabName).get(frameName).get('shelfButtonInfos')]

    for shelfContent in shelfContents:
        cmds.textScrollList('shelfContentsTxtScrLs', e=True, append=shelfContent)

    # Fill shelves rename text field
    cmds.textFieldGrp('shelfNameTxtFldGrp', e=True, text=selShelf)


def shelfContentsSelectCallback(*args):
    # Populate shelf button GUIs
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('shelfContentsTxtScrLs', q=True, selectItem=True)[0]

    shelfBtnInfo = None
    if selShelf == 'Common':
        shelfBtnInfo = _findShelfButtonInfo('Common', selShelf, selShelfBtnLabel)
    else:
        shelfBtnInfo = _findShelfButtonInfo('Task', selShelf, selShelfBtnLabel)

    cmds.shelfButton('iconPrevShelfBtn', e=True, image=shelfBtnInfo.get('image1'), imageOverlayLabel=shelfBtnInfo.get('imageOverlayLabel'))
    cmds.textField('iconNameTxtFld', e=True, text=shelfBtnInfo.get('image1'))
    cmds.textField('iconLabelTxtFld', e=True, text=shelfBtnInfo.get('imageOverlayLabel'))
    cmds.textField('tooltipTxtFld', e=True, text=shelfBtnInfo.get('annotation'))
    cmds.radioButtonGrp('langRadioBtnGrp', e=True, select=SOURCE_TYPE_MAPPING[shelfBtnInfo.get('sourceType')])
    cmds.scrollField('cmdScrFld', e=True, text=shelfBtnInfo.get('command'))

    # Fill shelf contents rename text field
    cmds.textFieldGrp('shelfBtnLabelTxtFldGrp', e=True, text=selShelfBtnLabel)


def updateIcon(*args):
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('shelfContentsTxtScrLs', q=True, selectItem=True)[0]
    image1 = cmds.textField('iconNameTxtFld', q=True, text=True)

    # Update data
    if selShelf == 'Common':
        shelfButtonInfo = _findShelfButtonInfo('Common', selShelf, selShelfBtnLabel)
    else:
        shelfButtonInfo = _findShelfButtonInfo('Task', selShelf, selShelfBtnLabel)
    shelfButtonInfo['image1'] = image1

    # Update Editor
    cmds.shelfButton('iconPrevShelfBtn', e=True, image1=image1)

    # Update shelf button
    shelfBtn = allShelfButtons.get(selShelfBtnLabel)
    cmds.shelfButton(shelfBtn, e=True, image1=image1)


def _findShelfButtonInfo(type='', taskShelf='', shelfButtonLabel=''):
    shelfButtonInfos = None
    if type == 'Common':
        shelfButtonInfos = commonShelfInfo.get('shelfButtonInfos')
    elif type == 'Task':
        tabName, frameName = taskShelf.split('_')
        shelfButtonInfos = taskShelvesInfo.get(tabName).get(frameName).get('shelfButtonInfos')

    for shelfButtonInfo in shelfButtonInfos:
        if shelfButtonLabel == shelfButtonInfo.get('label'):
            return shelfButtonInfo
    return None
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
    prefsDir = '{}/prefs'.format(MODULE_PATH)
    mayaPrefDir = '{}{}/prefs'.format(cmds.internalVar(uad=True), int(cmds.about(version=True)))
    copy_tree(prefsDir, mayaPrefDir)
# ------------
