import os
import json
import time
from distutils.dir_util import copy_tree
import subprocess
from collections import OrderedDict

from maya import cmds

from imp import reload
from .pipeline import takMayaResourceBrowser as tmrb; reload(tmrb)
from .utils import system as sysUtil


SUBPROCESS_NO_WINDOW = 0x08000000

MODULE_NAME = "takTools"
TOOL_NAME = 'Tak Tools'
MODULE_PATH = __file__.split(MODULE_NAME, 1)[0] + MODULE_NAME
SHELVES_DATA_PATH = '{}/data/shelves'.format(MODULE_PATH.replace('\\', '/'))
DEFAULT_ICONS_DIR = '{}/icons'.format(MODULE_PATH)

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
ICON_DEFAULT = 'commandButton.png'
LABEL_DEFAULT = 'User_Script'
DEFAULT_TASK_TAB = 'Rigging'
NUM_ICONS_PER_ROW = 10
COMMON_TAB_NUM_ROWS = 3
OUTLINER_PERCENTAGE = 50 * scaleFactor

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
    cmds.menuItem(label='Editor', image='shelfTab.png', c=editorGUI, p='editMenu')
    cmds.menuItem(label='Preferences', image='shelfOptions.png', c=prefsGUI, p='editMenu')
    cmds.menu('helpMenu', label='Help', p=WIN_NAME)
    cmds.menuItem(label='Check Update', image='teDownArrow.png', c=checkUpdate, p='helpMenu')
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

            shelves.append(shelfName)

    if selectTab:
        cmds.tabLayout('taskTabLo', e=True, selectTab=selectTab)


def readTaskShelvesInfo(fromGUI=False):
    global taskShelvesInfo

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

    orderedTaskShlvesInfos = sorted(rawTaskShelvesInfos, key=lambda item: item.get('order'))

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

        allShelfButtons[label] = shelfButton

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
    cmds.symbolButton(image='newLayerEmpty.png', c=addShelfButton)
    cmds.symbolButton(image='delete.png', c=deleteShelfButton)
    cmds.setParent('..')
    cmds.textFieldGrp('shelfBtnLabelTxtFldGrp', columnWidth=[(1, 45), (2, COLUMN_WIDTH*0.5)], label='Rename: ', cc=renameShelfButton)
    cmds.textScrollList('shelfContentsTxtScrLs', sc=shelfContentsSelectCallback)

    # Contents of a Shelf Button
    cmds.setParent('editorMainColLo')
    cmds.rowColumnLayout(numberOfColumns=2, columnAlign=[(1, 'right')])

    cmds.text(label='Icon Preview: ')
    cmds.shelfButton('iconPrevShelfBtn', w=ICON_SIZE, h=ICON_SIZE)

    cmds.text(label='Icon Name: ')
    cmds.rowColumnLayout(numberOfColumns=3)
    cmds.textField('iconNameTxtFld', w=(COLUMN_WIDTH*2)-110, tcc=updateIcon)
    cmds.symbolButton(image='fileOpen.png', c=setIcon)
    cmds.symbolButton(image='factoryIcon.png', c=lambda x: setIcon(useMayaResource=True))

    cmds.setParent('..')
    cmds.text('Icon Label: ')
    cmds.textField('iconLabelTxtFld', cc=setIconLabel)

    cmds.text(label='Tooltip: ')
    cmds.textField('tooltipTxtFld', cc=setToolTip)

    cmds.text('Command: ')
    cmds.columnLayout(adj=True)
    cmds.radioButtonGrp('langRadioBtnGrp', label='Language: ', labelArray2=['MEL', 'Python'], numberOfRadioButtons=2, select=2, columnWidth=[(1, 50), (2, 50)])
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
    cmds.textScrollList('shevesTxtScrLs', e=True, removeAll=True)
    for shelf in shelves:
        cmds.textScrollList('shevesTxtScrLs', e=True, append=shelf)


def reorderShelf(direction='up', *args):
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    if selShelf == 'Common':
        return

    selShelfIndex = shelves.index(selShelf)
    if direction == 'up':
        shelves[selShelfIndex], shelves[selShelfIndex-1] = shelves[selShelfIndex-1], shelves[selShelfIndex]
    elif direction == 'down':
        shelves[selShelfIndex+1], shelves[selShelfIndex]  = shelves[selShelfIndex], shelves[selShelfIndex+1]

    refreshShelves(selShelf)
    rebuildTaskShelves(selShelf.split('_')[0])


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
    cmds.radioButtonGrp('langRadioBtnGrp', e=True, select=SOURCE_TYPE_MAPPING.get(shelfBtnInfo.get('sourceType')))
    cmds.scrollField('cmdScrFld', e=True, text=shelfBtnInfo.get('command'))

    # Fill shelf contents rename text field
    cmds.textFieldGrp('shelfBtnLabelTxtFldGrp', e=True, text=selShelfBtnLabel)


def addShelfButton(*args):
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    shelfButtonName = LABEL_DEFAULT

    def _getValidShelfButtonName(shelfButtonName=''):
        index = 0
        validShelfButtonName = shelfButtonName
        while cmds.shelfButton(validShelfButtonName, exists=True):
            validShelfButtonName = '{}{}'.format(shelfButtonName, index)
            index += 1
        return validShelfButtonName

    if cmds.shelfButton(shelfButtonName, exists=True):
        shelfButtonName = _getValidShelfButtonName(shelfButtonName)
    cmds.shelfButton(shelfButtonName, label=shelfButtonName, width=ICON_SIZE, height=ICON_SIZE, image1=ICON_DEFAULT, ann=LABEL_DEFAULT, p=selShelf)
    allShelfButtons[shelfButtonName] = shelfButtonName

    refreshShelves(selShelf, shelfButtonName)


def deleteShelfButton(*args):
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('shelfContentsTxtScrLs', q=True, selectItem=True)[0]
    shelfButton = allShelfButtons.get(selShelfBtnLabel)
    cmds.deleteUI(shelfButton)

    refreshShelves(selShelf)


def renameShelfButton(*args):
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('shelfContentsTxtScrLs', q=True, selectItem=True)[0]
    shelfButton = allShelfButtons.get(selShelfBtnLabel)
    label = cmds.textFieldGrp('shelfBtnLabelTxtFldGrp', q=True, text=True)
    cmds.shelfButton(shelfButton, e=True, label=label)

    refreshShelves(selShelf, label)


def setIcon(useMayaResource=False, *args):
    if useMayaResource:
        tmrb.TakMayaResourceBrowser.showUI()
    else:
        getFromIconsFolder('iconNameTxtFld')


def getFromIconsFolder(widgetName, *args):
    iconImgPath = cmds.fileDialog2(fileMode=1, caption='Select a Image', startingDirectory=DEFAULT_ICONS_DIR)
    if iconImgPath:
        iconName = os.path.basename(iconImgPath[0])
        cmds.textField(widgetName, e=True, text=iconName)


def updateIcon(*args):
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('shelfContentsTxtScrLs', q=True, selectItem=True)[0]
    image1 = cmds.textField('iconNameTxtFld', q=True, text=True) or ICON_DEFAULT

    shelfButton = allShelfButtons.get(selShelfBtnLabel)
    cmds.shelfButton(shelfButton, e=True, image1=image1)

    refreshShelves(selShelf, selShelfBtnLabel)


def setIconLabel(*args):
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('shelfContentsTxtScrLs', q=True, selectItem=True)[0]
    iconLabel = cmds.textField('iconLabelTxtFld', q=True, text=True)

    shelfButton = allShelfButtons.get(selShelfBtnLabel)
    cmds.shelfButton(shelfButton, e=True, imageOverlayLabel=iconLabel)

    refreshShelves(selShelf, selShelfBtnLabel)


def setToolTip(*args):
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('shelfContentsTxtScrLs', q=True, selectItem=True)[0]
    tooltip = cmds.textField('tooltipTxtFld', q=True, text=True)

    shelfButton = allShelfButtons.get(selShelfBtnLabel)
    cmds.shelfButton(shelfButton, e=True, annotation=tooltip)

    refreshShelves(selShelf, selShelfBtnLabel)


def setCommand(*args):
    selShelf = cmds.textScrollList('shevesTxtScrLs', q=True, selectItem=True)[0]
    selShelfBtnLabel = cmds.textScrollList('shelfContentsTxtScrLs', q=True, selectItem=True)[0]
    language = SOURCE_TYPE_MAPPING.get(cmds.radioButtonGrp('langRadioBtnGrp', q=True, select=True))
    command = cmds.scrollField('cmdScrFld', q=True, text=True)

    shelfButton = allShelfButtons.get(selShelfBtnLabel)
    cmds.shelfButton(shelfButton, e=True, command=command, sourceType=language)

    refreshShelves(selShelf, selShelfBtnLabel)


def refreshShelves(shelfName='', shelfButtonLabel=''):
    readCommonShelfInfo(fromGUI=True)
    readTaskShelvesInfo(fromGUI=True)

    populateShelvesTextScrollList()

    if shelfName:
        cmds.textScrollList('shevesTxtScrLs', e=True, selectItem=shelfName)
        shelvesSelectCallback()
    if shelfButtonLabel:
        cmds.textScrollList('shelfContentsTxtScrLs', e=True, selectItem=shelfButtonLabel)
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
# ------------


# ------------ Preferences
def prefsGUI(*args):
    print('prefsGUI()')
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
                copyPreferences()
                import takTools.tak_tools as tt
                import imp; imp.reload(tt); tt.UI()
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


def copyPreferences():
    prefsDir = '{}/prefs'.format(MODULE_PATH)
    mayaPrefDir = '{}{}/prefs'.format(cmds.internalVar(uad=True), int(cmds.about(version=True)))
    copy_tree(prefsDir, mayaPrefDir)
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
