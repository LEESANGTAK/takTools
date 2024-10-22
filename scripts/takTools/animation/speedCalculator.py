"""
Author: Tak
Contact: https://ta-note.com

Created: 2024/10/22
Updated: 2024/10/22
"""


from maya import cmds, mel
from maya.api import OpenMaya as om


SPEED_ATTRIBUTE_NAME = 'MoveSpeed'


# ------------ HUD
def speedHUDToggle(object):
    averageSpeedHUDToggle(object)
    currentSpeedHUDToggle(object)


def averageSpeedHUDToggle(object):
    widgetName = '{}AvgSpeedHUD'.format(object)
    label = '"{}" Avg. Speed:'.format(object)
    section = 9

    if cmds.headsUpDisplay(widgetName, exists=True):
        cmds.headsUpDisplay(widgetName, remove=True)
        # Remove speed attribute
        speedAttr = '{}.{}'.format(object, SPEED_ATTRIBUTE_NAME)
        if cmds.objExists(speedAttr):
            cmds.deleteAttr(speedAttr)
    else:
        cmds.addAttr(object, ln=SPEED_ATTRIBUTE_NAME, at='float', keyable=True)
        showHUD(widgetName, label, section, lambda: averageSpeed(object), 'timeChanged')


def currentSpeedHUDToggle(object):
    widgetName = '{}CurSpeedHUD'.format(object)
    label = '"{}" Cur. Speed:'.format(object)
    section = 9

    if cmds.headsUpDisplay(widgetName, exists=True):
        cmds.headsUpDisplay(widgetName, remove=True)
    else:
        showHUD(widgetName, label, section, lambda: currentSpeed(object), 'timeChanged')


def showHUD(widgetName, label, sectionNum=2, command='', event=''):
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
# ------------


# ------------ Functions
def averageSpeed(object):
    fps = mel.eval('currentTimeUnitToFPS()')
    unit = cmds.currentUnit(query=True, linear=True)

    startFrame = cmds.playbackOptions(q=True, min=True)
    endFrame = cmds.playbackOptions(q=True, max=True)

    wholeDist = getDistance(object, startFrame, endFrame)
    wholeTime = (endFrame - startFrame) / fps
    avgSpeed = round(wholeDist / wholeTime, 2)

    cmds.setAttr('{}.{}'.format(object, SPEED_ATTRIBUTE_NAME), avgSpeed)

    return '{} {}/s'.format(avgSpeed, unit)


def currentSpeed(object):
    fps = mel.eval('currentTimeUnitToFPS()')
    unit = cmds.currentUnit(query=True, linear=True)

    curFrame = cmds.currentTime(q=True)

    perDist = getDistance(object, curFrame-1, curFrame)
    perTime = 1 / fps
    curSpeed = round(perDist / perTime, 2)

    return '{} {}/s'.format(curSpeed, unit)


def getDistance(object, startFrame, endFrame):
    dist = 0.0
    for curFrame in range(int(startFrame), int(endFrame+1)):
        if curFrame == startFrame:
            continue
        prePos = om.MPoint(cmds.getAttr('{}.worldMatrix'.format(object), t=curFrame-1)[-4:-1])
        curPos = om.MPoint(cmds.getAttr('{}.worldMatrix'.format(object), t=curFrame)[-4:-1])
        dist += (curPos - prePos).length()
    return dist
