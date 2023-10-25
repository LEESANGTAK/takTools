import pymel.core as pm
import maya.cmds as cmds

from . import environment as envUtil


def displayAffectedToggle():
    displayAffected = pm.displayPref(q=True, displayAffected=True)
    pm.displayPref(displayAffected=not displayAffected)


def displayModelOnlyToggle():
    curPanel = cmds.getPanel(withFocus=True)
    state = cmds.modelEditor(curPanel, q=True, clipGhosts=True)

    if state:
        cmds.modelEditor(curPanel, e=True, allObjects=False)
        cmds.modelEditor(curPanel, e=True, polymeshes=True)
        cmds.modelEditor(curPanel, e=True, strokes=True)
        cmds.modelEditor(curPanel, e=True, pluginShapes=True)

    else:
        cmds.modelEditor(curPanel, e=True, allObjects=True)


def showHUD(widgetName, label, sectionNum=2, command='', event=''):
    """Finds available block and display hud.

    Args:
        widgetName (str): HUD widget name. Used for delete.
        label (str): Label name.
        sectionNum (int, optional): 1 to 4 for upper section 5 to 9 for lower section. Defaults to 2.
        command (str, optional): Function name. e.g. 'getFrameRange()'
        event (str, optional): Need when command option used.
    """

    allHUDs = cmds.headsUpDisplay(listHeadsUpDisplays=True)

    hudsInSection = []
    for hud in allHUDs:
        if cmds.headsUpDisplay(hud, q=True, s=True) == sectionNum:
            hudsInSection.append(hud)

    blockNum = 0
    if hudsInSection:
        invalidBlocks = []
        for hud in hudsInSection:
            invalidBlock = cmds.headsUpDisplay(hud, q=True, b=True)
            invalidBlocks.append(invalidBlock)

        blockNum = max(invalidBlocks) + 1

    cmds.headsUpDisplay(
        widgetName,
        s=sectionNum,
        b=blockNum,
        label=label,
        blockSize='small',
        labelFontSize='small'
    )
    if command:
        cmds.headsUpDisplay(widgetName, e=True, command=command, event=event)


def frameRangeHUDToggle():
    wdgName = 'frameRangeHUD'
    label = 'Frame Range: '
    section = 9

    if cmds.headsUpDisplay(wdgName, exists=True):
        cmds.headsUpDisplay(wdgName, remove=True)
    else:
        showHUD(wdgName, label, section, envUtil.getFrameRange, 'playbackRangeChanged')

