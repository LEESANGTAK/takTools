import os
import json
import time
import subprocess
from collections import OrderedDict
from distutils.dir_util import copy_tree

from maya import cmds, mel

from imp import reload
from .pipeline import takMayaResourceBrowser as tmrb; reload(tmrb)
from .common import iconMaker as im; reload(im)
from .utils import system as sysUtil


def getAllIcons():
    allIcons = []
    iconPaths = mel.eval('getenv "XBMLANGPATH";').split(';')
    for iconPath in iconPaths:
        if os.path.exists(iconPath):
            allIcons.extend(os.listdir(iconPath))
    allIcons.extend(cmds.resourceManager(nameFilter='*.png'))
    return list(set(allIcons))


MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION >= 2022:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser

SUBPROCESS_NO_WINDOW = 0x08000000

MODULE_NAME = "takTools"
TOOL_NAME = 'Tak Tools'
MODULE_PATH = __file__.split(MODULE_NAME, 1)[0] + MODULE_NAME
PREFERENCES_FILE_PATH = '{}/data/preferences.ini'.format(MODULE_PATH)
SHELVES_DATA_PATH = '{}/data/shelves'.format(MODULE_PATH.replace('\\', '/'))
DEFAULT_ICONS_DIR = '{}/icons'.format(MODULE_PATH)
ALL_ICONS = getAllIcons()

# Version constants
VERSION_MAJOR = 2
VERSION_MINOR = 2
VERSION_MICRO = 2

# Size values are based on 4k(3840*2160) monitor
# Caculate scale factor depend on monitor height
DEFAULT_DISPLAY_HEIGHT = 2160
sysObj = sysUtil.System()
scaleFactor = sysObj.screenHeight / float(DEFAULT_DISPLAY_HEIGHT)

# Preferences
config = ConfigParser()
config.read(PREFERENCES_FILE_PATH)

ICON_SIZE = config.getint('Icon', 'iconSize')
ICON_MARGINE = 6
ICON_DEFAULT = 'commandButton.png'
SHELF_DEFAULT_NAME = 'Tab_Frame'
SHELF_BUTTON_DEFAULT_LABEL = 'User_Script'
DEFAULT_TASK_TAB = config.get('Tab', 'defaultTaskTab')
NUM_ICONS_PER_ROW = config.getint('Icon', 'numIconsPerRow')
COMMON_TAB_NUM_ROWS = config.getint('Tab', 'commonTabNumRows')
OUTLINER_PERCENTAGE = config.getint('Panel', 'outlinerPercentage') * scaleFactor

PANE_WIDTH = ICON_SIZE * (NUM_ICONS_PER_ROW + 1)
COMMON_TAB_HEIGHT = (ICON_SIZE + ICON_MARGINE) * COMMON_TAB_NUM_ROWS
COMMON_TAB_PERCENTAGE = (COMMON_TAB_HEIGHT / float(sysObj.screenHeight)) * 100
ADAPTED_OULINER_PERCENTAGE = OUTLINER_PERCENTAGE + COMMON_TAB_PERCENTAGE
SCROLL_AREA_HEIGHT = sysObj.screenHeight * ((100-ADAPTED_OULINER_PERCENTAGE) * 0.01) * 0.5

WIN_NAME = "{0}Win".format(MODULE_NAME)
SOURCE_TYPE_MAPPING = {'mel': 1, 'python': 2, 1: 'mel', 2: 'python'}

# Global variables
shelves = ['Common']
commonShelfInfo = {}
taskShelvesInfo = {}
allShelfButtons = {}
maxOrderNum = 0


def UI():
    if cmds.window(WIN_NAME, exists=True):
        cmds.deleteUI(WIN_NAME)
    if cmds.dockControl(MODULE_NAME, exists=True):
        cmds.deleteUI(MODULE_NAME)

    cmds.window(WIN_NAME, title=TOOL_NAME, tlb=True)

    # Main menu
    cmds.menuBarLayout(WIN_NAME)
    cmds.menu('fileMenu', label='File', p=WIN_NAME)
    cmds.menuItem(label='Save', image='save.png', c=writeShelvesToFile, p='fileMenu')
    cmds.menuItem(label='Restore', image='refresh.png', c=restore, p='fileMenu')
    cmds.menu('editMenu', label='Edit', p=WIN_NAME)
    cmds.menuItem(label='Editor', image='passSetRelationEditor.png', c=editorGUI, p='editMenu')
    cmds.menuItem(label='Preferences', image='shelfOptions.png', c=prefsGUI, p='editMenu')
    cmds.menu('helpMenu', label='Help', p=WIN_NAME)
    cmds.menuItem(label='Check Update', image='teDownArrow.png', c=checkUpdate, p='helpMenu')
    cmds.menuItem(label='Hotkeys Info', c=hotkeysInfo, p='helpMenu')
    cmds.menuItem(label='About Tak Tools', image='info.png', c=aboutGUI, p='helpMenu')

    cmds.paneLayout('mainPaneLo', configuration='horizontal2', w=PANE_WIDTH, paneSize=[(2, 50, 90)])

    cmds.columnLayout('mainColLo', adj=True)

    # Common tab
    cmds.tabLayout('cmnToolTabLo', tv=False, p='mainColLo')
    cmds.shelfLayout('Common', h=COMMON_TAB_HEIGHT, parent='cmnToolTabLo')
    readCommonShelfInfo()
    rebuildCommonShelf()

    cmds.separator('mainSep', style='in', p='mainColLo')

    # Task tabs
    cmds.tabLayout('taskTabLo', p='mainColLo')
    readTaskShelvesInfo()
    rebuildTaskShelves()

    # Outliner
    cmds.frameLayout('olFrameLo', labelVisible=False, p='mainPaneLo')
    panel = cmds.outlinerPanel()
    outliner = cmds.outlinerPanel(panel, query=True, outlinerEditor=True)
    cmds.outlinerEditor( outliner, edit=True, mainListConnection='worldList', selectionConnection='modelList', showShapes=False, showAssignedMaterials=False, showReferenceNodes=True, showReferenceMembers=True, showAttributes=False, showConnected=False, showAnimCurvesOnly=False, autoExpand=False, showDagOnly=True, ignoreDagHierarchy=False, expandConnections=False, showCompounds=True, showNumericAttrsOnly=False, highlightActive=True, autoSelectNewObjects=False, doNotSelectNewObjects=False, transmitFilters=False, showSetMembers=True, setFilter='defaultSetFilter', ignoreHiddenAttribute=False )

    # Dock window to left side
    cmds.dockControl(MODULE_NAME, label=TOOL_NAME, area='left', content=WIN_NAME)


# ------------ Load & Save
def rebuildCommonShelf():
    global allShelfButtons

    # Remove existing tabs
    commonShelfButtons = cmds.shelfLayout('Common', query=True, childArray=True)
    if commonShelfButtons:
        for commonshelfButton in commonShelfButtons:
            cmds.shelfLayout('Common', edit=True, remove=commonshelfButton)

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


def readCommonShelfInfo(fromGUI=False):
    global commonShelfInfo

    if fromGUI:
        commonShelfInfo = getShelfInfoFromGUI(shelfName='Common')
    else:
        commonShelfFile = '{}/Common.json'.format(SHELVES_DATA_PATH)
        with open(commonShelfFile, 'r') as f:
            commonShelfInfo = json.load(f, object_pairs_hook=OrderedDict)


def rebuildTaskShelves(selectTab=DEFAULT_TASK_TAB, *args):
    global allShelfButtons
    global shelves

    # Remove existing tab
    if cmds.tabLayout('taskTabLo', exists=True):
        cmds.deleteUI('taskTabLo')

    # Build tabs
    cmds.tabLayout('taskTabLo', p='mainColLo')
    shelves = ['Common']
    for tabName, frameInfo in taskShelvesInfo.items():
        # Create tab for shelves
        tabControl = cmds.scrollLayout(tabName, childResizable=True, h=SCROLL_AREA_HEIGHT, p='taskTabLo')
        cmds.tabLayout('taskTabLo', e=True, tabLabel=[tabControl, tabName])

        for frameName, frameData in frameInfo.items():
            shelfName = '{}_{}'.format(tabName, frameName)

            # Create frame layout with frame data
            frameLayout = cmds.frameLayout('{}FrameLayout'.format(shelfName), label=frameName, collapsable=True, collapse=frameData.get('collapse'), p=tabControl)

            # Add shelf buttons to the shelf layout in the frame layout
            shelfButtonInfos = frameData.get('shelfButtonInfos')
            numRows = int(len(shelfButtonInfos) / NUM_ICONS_PER_ROW) + 1
            shelf = cmds.shelfLayout(shelfName, ch=((ICON_SIZE + ICON_MARGINE) * numRows), p=frameLayout)

            for shelfButtonInfo in shelfButtonInfos:
                image = shelfButtonInfo.get('image1')
                # if not image in ALL_ICONS:
                #     image = 'noPreview.png'

                shelfBtn = cmds.shelfButton(
                    label=shelfButtonInfo.get('label'),
                    annotation=shelfButtonInfo.get('annotation'),
                    width=ICON_SIZE, height=ICON_SIZE,
                    image1=image,
                    imageOverlayLabel=shelfButtonInfo.get('imageOverlayLabel'),
                    command=shelfButtonInfo.get('command'),
                    sourceType=shelfButtonInfo.get('sourceType'),
                    noDefaultPopup=shelfButtonInfo.get('noDefaultPopup'),
                    p=shelf)
                allShelfButtons[_getShelfButtonKey(shelfName, shelfButtonInfo.get('label'))] = shelfBtn

            shelves.append(shelfName)

    tabs = cmds.tabLayout('taskTabLo', q=True, tabLabel=True)
    if tabs and selectTab in tabs:
        cmds.tabLayout('taskTabLo', e=True, selectTab=selectTab)


def readTaskShelvesInfo(fromGUI=False):
    global taskShelvesInfo
    global maxOrderNum

    taskShelvesInfo = OrderedDict()
    rawTaskShelvesInfos = []

    if fromGUI:
        for i, shelf in enumerate(shelves):
            if shelf == 'Common':
                continue
            shelfInfo = getShelfInfoFromGUI(i, shelf)
            rawTaskShelvesInfos.append(shelfInfo)
    else:
        taskShelfFiles = [shelfFile for shelfFile in os.listdir(SHELVES_DATA_PATH) if not 'Common' in shelfFile]
        for taskShelfFile in taskShelfFiles:
            filePath = '{}/{}'.format(SHELVES_DATA_PATH, taskShelfFile)
            with open(filePath, 'r') as f:
                shelfInfo = json.load(f, object_pairs_hook=OrderedDict)
                rawTaskShelvesInfos.append(shelfInfo)

    if not rawTaskShelvesInfos:
        return

    orderedTaskShlvesInfos = sorted(rawTaskShelvesInfos, key=lambda item: int(item.get('order')))
    maxOrderNum = int(orderedTaskShlvesInfos[-1].get('order'))

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


def writeShelvesToFile(*args):
    for i, shelf in enumerate(shelves):
        shelfInfo = getShelfInfoFromGUI(i, shelf)
        filePath = '{}/{}.json'.format(SHELVES_DATA_PATH, shelf)
        with open(filePath, 'w') as f:
            json.dump(shelfInfo, f, indent=4)


def restore(*args):
    answer = cmds.confirmDialog(title='Warning', message='Restore Tak Tools from the shelf files.\nUnsaved data will be lost.\nAre you sure?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')
    if answer == 'Yes':
        from imp import reload
        from takTools import tak_tools as tt; reload(tt)
        tt.UI()


def getShelfInfoFromGUI(index=0, shelfName=''):
    global allShelfButtons

    shelfInfo = OrderedDict()

    if not shelfName == 'Common':
        tabName, frameName = shelfName.split('_')
        shelfInfo['order'] = str(index).zfill(2)
        shelfInfo['tabName'] = tabName
        shelfInfo['frameName'] = frameName
        shelfInfo['collapse'] = cmds.frameLayout('{}FrameLayout'.format(shelfName), q=True, collapse=True)

    shelfButtonInfos = []
    shelfButtons = cmds.shelfLayout(shelfName, q=True, childArray=True)
    if shelfButtons:
        for shelfButton in shelfButtons:
            label = cmds.shelfButton(shelfButton, q=True, label=True) or cmds.shelfButton(shelfButton, q=True, command=True)[:20] + '...' + cmds.shelfButton(shelfButton, q=True, command=True)[-20:]
            command = cmds.shelfButton(shelfButton, q=True, command=True) or cmds.scrollField('cmdScrFld', q=True, text=True)
            shelfButtonInfo = {
                'label': label,
                'annotation': cmds.shelfButton(shelfButton, q=True, ann=True),
                'image1': cmds.shelfButton(shelfButton, q=True, image1=True),
                'imageOverlayLabel': cmds.shelfButton(shelfButton, q=True, imageOverlayLabel=True),
                'command': command,
                'sourceType': cmds.shelfButton(shelfButton, q=True, sourceType=True),
                'noDefaultPopup': True
            }
            shelfButtonInfos.append(shelfButtonInfo)

            allShelfButtons[_getShelfButtonKey(shelfName, shelfButtonInfo.get('label'))] = shelfButton

    shelfInfo['shelfButtonInfos'] = shelfButtonInfos

    return shelfInfo
# ------------


# ------------ Editor
COLUMN_WIDTH = 200
def editorGUI(*args):
    winName = 'editorWin'
    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)
    cmds.window(winName, title='Tak Tools Editor', tlb=True, p=WIN_NAME)

    cmds.tabLayout(tv=False)
    cmds.columnLayout('editorMainColLo', adj=True)

    # Shelves and Shelf Contents
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, COLUMN_WIDTH), (3, COLUMN_WIDTH)])

    cmds.frameLayout(label='Shelves')
    cmds.columnLayout(adj=True)
    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.symbolButton(image='moveLayerUp.png', c=lambda x: reorderShelf('up'))
    cmds.symbolButton(image='moveLayerDown.png', c=lambda x: reorderShelf('down'))
    cmds.symbolButton(image='newLayerEmpty.png', c=addShelf)
    cmds.symbolButton(image='delete.png', c=deleteShelf)
    cmds.setParent('..')
    cmds.textFieldGrp('shelfNameTxtFldGrp', columnWidth=[(1, 45), (2, COLUMN_WIDTH*0.5)], label='Rename: ', cc=renameShelf)
    cmds.textScrollList('editorShevesTxtScrLs', sc=shelvesSelectCallback)

    cmds.setParent('..')
    cmds.setParent('..')
    cmds.separator(w=5, style='none')

    cmds.frameLayout(label='Shelf Contents')
    cmds.columnLayout(adj=True)
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.symbolButton(image='newLayerEmpty.png', c=addShelfButton)
    cmds.symbolButton(image='delete.png', c=deleteShelfButton)
    cmds.setParent('..')
    cmds.textFieldGrp('shelfBtnLabelTxtFldGrp', columnWidth=[(1, 45), (2, COLUMN_WIDTH*0.5)], label='Rename: ', cc=renameShelfButton)
    cmds.textScrollList('editorShelfContentsTxtScrLs', ams=True, sc=shelfContentsSelectCallback)

    # Contents of a Shelf Button
    cmds.setParent('editorMainColLo')
    cmds.rowColumnLayout(numberOfColumns=2, columnAlign=[(1, 'right')])

    cmds.text(label='Icon Preview: ')
    cmds.shelfButton('iconPrevShelfBtn', w=ICON_SIZE, h=ICON_SIZE, ndp=True, c=evalCommand)

    cmds.text(label='Icon Name: ')
    cmds.rowColumnLayout(numberOfColumns=4)
    cmds.textField('iconNameTxtFld', w=(COLUMN_WIDTH*2)-130, tcc=updateIcon)
    cmds.symbolButton(image='factoryIcon.png', c=lambda x: setIcon(useMayaResource=True))
    cmds.symbolButton(image='UVEditorSnapshot.png', c=lambda x: setIcon(iconMaker=True))
    cmds.symbolButton(image='fileOpen.png', c=setIcon)

    cmds.setParent('..')
    cmds.text('Icon Label: ')
    cmds.textField('iconLabelTxtFld', cc=setIconLabel)

    cmds.text(label='Tooltip: ')
    cmds.textField('tooltipTxtFld', cc=setToolTip)

    cmds.text('Command: ')
    cmds.columnLayout(adj=True)
    cmds.radioButtonGrp('langRadioBtnGrp', label='Language: ', labelArray2=['MEL', 'Python'], numberOfRadioButtons=2, select=2, columnWidth=[(1, 50), (2, 50)], cc=setCommand)
    cmds.scrollField('cmdScrFld', w=(COLUMN_WIDTH*2)-110, h=100, cc=setCommand)

    # Buttons
    cmds.setParent('editorMainColLo')
    cmds.rowColumnLayout(numberOfColumns=2, columnOffset=[(2, 'left', 5)])
    cmds.button(label='Save All Shelves', w=COLUMN_WIDTH, c=writeShelvesToFile)
    cmds.button(label='Close', w=COLUMN_WIDTH, c=lambda x: cmds.deleteUI(winName))

    cmds.window(winName, e=True, w=10, h=10)
    cmds.showWindow(winName)

    readCommonShelfInfo(fromGUI=True)
    readTaskShelvesInfo(fromGUI=True)
    populateShelvesTextScrollList()


def populateShelvesTextScrollList():
    cmds.textScrollList('editorShevesTxtScrLs', e=True, removeAll=True)
    for shelf in shelves:
        cmds.textScrollList('editorShevesTxtScrLs', e=True, append=shelf)


def reorderShelf(direction='up', *args):
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    if selShelf == 'Common':
        return

    selShelfIndex = shelves.index(selShelf)
    if direction == 'up':
        shelves[selShelfIndex], shelves[selShelfIndex-1] = shelves[selShelfIndex-1], shelves[selShelfIndex]
    elif direction == 'down':
        shelves[selShelfIndex+1], shelves[selShelfIndex]  = shelves[selShelfIndex], shelves[selShelfIndex+1]

    refreshEditorShelves(selShelf)
    rebuildTaskShelves(selShelf.split('_')[0])


def shelvesSelectCallback(*args):
    # Populate shelf contents text scroll list
    cmds.textScrollList('editorShelfContentsTxtScrLs', e=True, removeAll=True)
    cmds.textFieldGrp('shelfBtnLabelTxtFldGrp', e=True, text='')

    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    tabName = None

    shelfContents = None
    if selShelf == 'Common':
        shelfContents = [shelfButtonInfo.get('label') for shelfButtonInfo in commonShelfInfo.get('shelfButtonInfos')]
    else:
        tabName, frameName = selShelf.split('_')
        shelfContents = [shelfButtonInfo.get('label') for shelfButtonInfo in taskShelvesInfo.get(tabName).get(frameName).get('shelfButtonInfos')]

    for shelfContent in shelfContents:
        cmds.textScrollList('editorShelfContentsTxtScrLs', e=True, append=shelfContent)

    # Fill shelves rename text field
    cmds.textFieldGrp('shelfNameTxtFldGrp', e=True, text=selShelf)

    if tabName:
        cmds.tabLayout('taskTabLo', e=True, selectTab=tabName)


def shelfContentsSelectCallback(*args):
    # Populate shelf button GUIs
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('editorShelfContentsTxtScrLs', q=True, selectItem=True)[0]

    shelfBtnInfo = None
    if selShelf == 'Common':
        shelfBtnInfo = _findShelfButtonInfo('Common', selShelf, selShelfBtnLabel)
    else:
        shelfBtnInfo = _findShelfButtonInfo('Task', selShelf, selShelfBtnLabel)

    cmds.shelfButton('iconPrevShelfBtn', e=True, image=shelfBtnInfo.get('image1'), imageOverlayLabel=shelfBtnInfo.get('imageOverlayLabel'))
    cmds.textField('iconNameTxtFld', e=True, text=shelfBtnInfo.get('image1'))
    cmds.textField('iconLabelTxtFld', e=True, text=shelfBtnInfo.get('imageOverlayLabel'))
    cmds.textField('tooltipTxtFld', e=True, text=shelfBtnInfo.get('annotation'))
    cmds.radioButtonGrp('langRadioBtnGrp', e=True, select=SOURCE_TYPE_MAPPING.get(shelfBtnInfo.get('sourceType')))
    cmds.scrollField('cmdScrFld', e=True, text=shelfBtnInfo.get('command'))

    # Fill shelf contents rename text field
    cmds.textFieldGrp('shelfBtnLabelTxtFldGrp', e=True, text=selShelfBtnLabel)


def addShelfButton(*args):
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    shelfButtonName = SHELF_BUTTON_DEFAULT_LABEL

    def _getValidShelfButtonName(shelfButtonName=''):
        index = 0
        validShelfButtonName = shelfButtonName
        while cmds.shelfButton(validShelfButtonName, exists=True):
            validShelfButtonName = '{}{}'.format(shelfButtonName, index)
            index += 1
        return validShelfButtonName

    if cmds.shelfButton(shelfButtonName, exists=True):
        shelfButtonName = _getValidShelfButtonName(shelfButtonName)
    cmds.shelfButton(shelfButtonName, label=shelfButtonName, width=ICON_SIZE, height=ICON_SIZE, image1=ICON_DEFAULT, ann=SHELF_BUTTON_DEFAULT_LABEL, p=selShelf)
    allShelfButtons[_getShelfButtonKey(selShelf, shelfButtonName)] = shelfButtonName

    refreshEditorShelves(selShelf, shelfButtonName)


def deleteShelfButton(*args):
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabels = cmds.textScrollList('editorShelfContentsTxtScrLs', q=True, selectItem=True)
    for selShelfBtnLabel in selShelfBtnLabels:
        shelfButton = allShelfButtons.get(_getShelfButtonKey(selShelf, selShelfBtnLabel))
        cmds.deleteUI(shelfButton)

    refreshEditorShelves(selShelf)


def addShelf(*args):
    newShelfName = SHELF_DEFAULT_NAME

    def _getValidShelfName(shelfName=''):
        index = 0
        validShelfName = shelfName
        while os.path.exists('{}/{}.json'.format(SHELVES_DATA_PATH, validShelfName)):
            validShelfName = '{}{}'.format(shelfName, index)
            index += 1
        return validShelfName

    newShelfFilePath = '{}/{}.json'.format(SHELVES_DATA_PATH, newShelfName)
    if os.path.exists(newShelfFilePath):
        newShelfName = _getValidShelfName(newShelfName)

    newShelfFilePath = '{}/{}.json'.format(SHELVES_DATA_PATH, newShelfName)
    tabName, frameName = newShelfName.split('_')
    defaultShelfInfo = {
        'order': str(maxOrderNum+1).zfill(2),
        'tabName': tabName,
        'frameName': frameName,
        'collapse': False,
        'shelfButtonInfos': []
    }
    with open(newShelfFilePath, 'w') as f:
        json.dump(defaultShelfInfo, f, indent=4)

    readTaskShelvesInfo(fromGUI=False)
    rebuildTaskShelves(tabName)
    refreshEditorShelves(newShelfName)


def deleteShelf(*args):
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]

    if selShelf == 'Common':
        cmds.warning('"Common" shelf can not be deleted.')
        return

    answer = cmds.confirmDialog(title='Warning', message='Unsaved data will be lost. And this can not be undo.\nAre you sure?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')
    if answer == 'No':
        return

    os.remove('{}/{}.json'.format(SHELVES_DATA_PATH, selShelf))

    readTaskShelvesInfo(fromGUI=False)
    rebuildTaskShelves()
    refreshEditorShelves()
    cmds.textFieldGrp('shelfNameTxtFldGrp', e=True, text='')


def renameShelf(*args):
    oldShelfName = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    newShelfName = cmds.textFieldGrp('shelfNameTxtFldGrp', q=True, text=True)

    # Error checks
    if oldShelfName == newShelfName:
        return

    if oldShelfName == 'Common':
        cmds.warning('"Common" shelf can not be renamed.')
        cmds.textFieldGrp('shelfNameTxtFldGrp', e=True, text='Common')
        return

    splitedNewShelfName = newShelfName.split('_')
    if len(splitedNewShelfName) != 2:
        cmds.error('Shelf name should be in form with "TabName_FrameName".')
        return

    # Start renaming process
    answer = cmds.confirmDialog(title='Warning', message='Unsaved data will be lost.\nAre you sure?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')
    if answer == 'No':
        return

    oldShelfFilePath = '{}/{}.json'.format(SHELVES_DATA_PATH, oldShelfName)
    newShelfFilePath = '{}/{}.json'.format(SHELVES_DATA_PATH, newShelfName)

    # Read old shelf file
    with open(oldShelfFilePath, 'r') as f:
        shelfInfo = json.load(f)

    # Replace tab and frame name value
    shelfInfo['tabName'] = splitedNewShelfName[0]
    shelfInfo['frameName'] = splitedNewShelfName[1]

    # Write new shelf file
    with open(newShelfFilePath, 'w') as f:
        json.dump(shelfInfo, f, indent=4)

    # Remove old shelf file
    os.remove(oldShelfFilePath)

    readTaskShelvesInfo(fromGUI=False)
    rebuildTaskShelves(splitedNewShelfName[0])
    refreshEditorShelves(newShelfName)


def renameShelfButton(*args):
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('editorShelfContentsTxtScrLs', q=True, selectItem=True)[0]
    shelfButton = allShelfButtons.get(_getShelfButtonKey(selShelf, selShelfBtnLabel))
    label = cmds.textFieldGrp('shelfBtnLabelTxtFldGrp', q=True, text=True)
    cmds.shelfButton(shelfButton, e=True, label=label)

    refreshEditorShelves(selShelf, label)


def evalCommand(*args):
    lang = SOURCE_TYPE_MAPPING.get(cmds.radioButtonGrp('langRadioBtnGrp', q=True, select=True))
    cmd = cmds.scrollField('cmdScrFld', q=True, text=True)
    if lang == 'python':
        cmds.evalDeferred(cmd)
    elif lang == 'mel':
        mel.eval(cmd)


def setIcon(useMayaResource=False, iconMaker=False, *args):
    if useMayaResource:
        tmrb.TakMayaResourceBrowser.showUI()
    elif iconMaker:
        gui = im.IconMakerGUI()
        gui.show()
    else:
        getFromIconsFolder('iconNameTxtFld')


def getFromIconsFolder(widgetName, *args):
    iconImgPath = cmds.fileDialog2(fileMode=1, caption='Select a Image', startingDirectory=DEFAULT_ICONS_DIR)
    if iconImgPath:
        iconName = os.path.basename(iconImgPath[0])
        cmds.textField(widgetName, e=True, text=iconName)


def updateIcon(*args):
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('editorShelfContentsTxtScrLs', q=True, selectItem=True)
    if not selShelfBtnLabel:
        return
    selShelfBtnLabel = selShelfBtnLabel[0]
    image1 = cmds.textField('iconNameTxtFld', q=True, text=True) or ICON_DEFAULT

    shelfButton = allShelfButtons.get(_getShelfButtonKey(selShelf, selShelfBtnLabel))
    cmds.shelfButton(shelfButton, e=True, image1=image1)

    refreshEditorShelves(selShelf, selShelfBtnLabel)


def setIconLabel(*args):
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('editorShelfContentsTxtScrLs', q=True, selectItem=True)[0]
    iconLabel = cmds.textField('iconLabelTxtFld', q=True, text=True)

    shelfButton = allShelfButtons.get(_getShelfButtonKey(selShelf, selShelfBtnLabel))
    cmds.shelfButton(shelfButton, e=True, imageOverlayLabel=iconLabel)

    refreshEditorShelves(selShelf, selShelfBtnLabel)


def setToolTip(*args):
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('editorShelfContentsTxtScrLs', q=True, selectItem=True)[0]
    tooltip = cmds.textField('tooltipTxtFld', q=True, text=True)

    shelfButton = allShelfButtons.get(_getShelfButtonKey(selShelf, selShelfBtnLabel))
    cmds.shelfButton(shelfButton, e=True, annotation=tooltip)

    refreshEditorShelves(selShelf, selShelfBtnLabel)


def setCommand(*args):
    print('setCommand()')
    selShelf = cmds.textScrollList('editorShevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('editorShelfContentsTxtScrLs', q=True, selectItem=True)[0]
    language = SOURCE_TYPE_MAPPING.get(cmds.radioButtonGrp('langRadioBtnGrp', q=True, select=True))
    command = cmds.scrollField('cmdScrFld', q=True, text=True)

    shelfButton = allShelfButtons.get(_getShelfButtonKey(selShelf, selShelfBtnLabel))
    cmds.shelfButton(shelfButton, e=True, command=command, sourceType=language)

    refreshEditorShelves(selShelf, selShelfBtnLabel)


def refreshEditorShelves(shelfName='', shelfButtonLabel='', fromGUI=True):
    if fromGUI:
        readCommonShelfInfo(fromGUI=True)
        readTaskShelvesInfo(fromGUI=True)
    else:
        readCommonShelfInfo(fromGUI=False)
        readTaskShelvesInfo(fromGUI=False)

    populateShelvesTextScrollList()

    if shelfName:
        cmds.textScrollList('editorShevesTxtScrLs', e=True, selectItem=shelfName)
        shelvesSelectCallback()
    if shelfButtonLabel:
        cmds.textScrollList('editorShelfContentsTxtScrLs', e=True, selectItem=shelfButtonLabel)
        shelfContentsSelectCallback()


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

def _getShelfButtonKey(shelfName, shelfButtonName):
    # This prevent error when same shelf button exists in the another shelf
    return '{}{}'.format(shelfName, shelfButtonName)
# ------------


# ------------ Preferences
def prefsGUI(*args):
    prefWinName = '{}PrefWin'.format(MODULE_NAME)
    if cmds.window(prefWinName, ex=True):
        cmds.deleteUI(prefWinName)
    cmds.window(prefWinName, title='Preferences'.format(TOOL_NAME), tlb=True, p=WIN_NAME)
    cmds.tabLayout(tv=False)
    cmds.columnLayout(adj=True)
    cmds.intFieldGrp('outlinerPercentageIntFldGrp', label='Outliner Percentage: ', v1=config.getint('Panel', 'outlinerPercentage'))
    cmds.intFieldGrp('commonTabNumRowsIntFldGrp', label='Common Tab Number of Rows: ', v1=COMMON_TAB_NUM_ROWS)
    cmds.optionMenuGrp('defaultTaskTabOptMenuGrp', label='Default Task Tab: ')
    for tab in taskShelvesInfo.keys():
        cmds.menuItem(label=tab)
    cmds.intFieldGrp('iconSizeIntFldGrp', label='Icon Size: ', v1=ICON_SIZE)
    cmds.intFieldGrp('numIconsPerRowIntFldGrp', label='Number of Icons Per Row: ', v1=NUM_ICONS_PER_ROW)
    cmds.rowColumnLayout(numberOfColumns=2, columnOffset=[(2, 'left', 5)])
    cmds.button(label='Apply', w=110, c=applyPreferences)
    cmds.button(label='Close', w=110, c=lambda x: cmds.deleteUI(prefWinName))
    cmds.window(prefWinName, e=True, w=10, h=10)
    cmds.showWindow(prefWinName)


def applyPreferences(*args):
    outlinerPercentage = cmds.intFieldGrp('outlinerPercentageIntFldGrp', q=True, v1=True)
    commonTabNumRows = cmds.intFieldGrp('commonTabNumRowsIntFldGrp', q=True, v1=True)
    defaultTaskTab = cmds.optionMenuGrp('defaultTaskTabOptMenuGrp', q=True, value=True)
    iconSize = cmds.intFieldGrp('iconSizeIntFldGrp', q=True, v1=True)
    numIconsPerRow = cmds.intFieldGrp('numIconsPerRowIntFldGrp', q=True, v1=True)

    config = ConfigParser()
    if MAYA_VERSION >= 2022:
        config['Panel'] = {
            'outlinerPercentage': outlinerPercentage
        }

        config['Tab'] = {
            'commonTabNumRows': commonTabNumRows,
            'defaultTaskTab': defaultTaskTab
        }

        config['Icon'] = {
            'iconSize': iconSize,
            'numIconsPerRow': numIconsPerRow
        }
    else:
        config.add_section('Panel')
        config.set('Panel', 'outlinerPercentage', outlinerPercentage)
        config.add_section('Tab')
        config.set('Tab', 'commonTabNumRows', commonTabNumRows)
        config.set('Tab', 'defaultTaskTab', defaultTaskTab)
        config.add_section('Icon')
        config.set('Icon', 'iconSize', iconSize)
        config.set('Icon', 'numIconsPerRow', numIconsPerRow)

    with open(PREFERENCES_FILE_PATH, 'w') as f:
        config.write(f)

    restore()
# ------------


# ------------ Git Utils
def checkUpdate(self):
    if isOutdated():
        result = cmds.confirmDialog(
            title=TOOL_NAME,
            message="New version is detected. Do you want to update?",
            button=['Yes','No'],
            defaultButton='Yes',
            cancelButton='No',
            dismissString='No'
        )
        if 'Yes' == result:
            succeed = update()
            if succeed:
                copyMayaPreferences()

                # Reload tool
                import takTools.tak_tools as tt
                import imp; imp.reload(tt); tt.UI()

                # Reload hotkey set
                if 'takTools' in cmds.hotkeySet(q=True, hotkeySetArray=True):
                    cmds.hotkeySet('takTools', e=True, delete=True)
                    cmds.hotkeySet(e=True, ip="C:/Users/chst2/Documents/maya/2024/prefs/hotkeys/takTools.mhk")
                    cmds.hotkeySet('takTools', e=True, current=True)
    else:
        cmds.confirmDialog(title=TOOL_NAME, message='You have latest version.\nEnjoy!')


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


def copyMayaPreferences():
    prefsDir = '{}/prefs'.format(MODULE_PATH)
    mayaPrefDir = '{}{}/prefs'.format(cmds.internalVar(uad=True), int(cmds.about(version=True)))
    copy_tree(prefsDir, mayaPrefDir)
# ------------


# ------------ Hotkeys Info
def hotkeysInfo(*ags):
    message = '''
Shift + 1 + LMB: Display Marking Menu
Shift + 2 + LMB: Select Marking Menu
Shift + 3 + LMB: Rigging Marking Menu
Shift + 4 + LMB: Skinning Marking Menu
Ctrl + Alt + D: Toggle Deformers
Ctrl + Alt + S: Select Hierarchy
Ctrl + Alt + Z: Go to Bind Pose
'''
    cmds.confirmDialog(title=TOOL_NAME, message=message, button='OK')
# ------------


# ------------ About
def aboutGUI(*ags):
    message = '''
Author: Sangtak Lee
Contact: https://ta-note.com

Created: 12/22/2015
Version: {}.{}.{}

Custom shelf tool to organize shelf buttons more efficiently.
{} Sangtak Lee, All rights reserved.
'''.format(
    VERSION_MAJOR, VERSION_MINOR, VERSION_MICRO,
    time.localtime().tm_year,
)
    cmds.confirmDialog(title=TOOL_NAME, message=message, button='OK')
# ------------
