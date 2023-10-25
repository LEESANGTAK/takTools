'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 2014-06-11

Description:
This script is useful for secondary overlapping animation kind of antena or earing or spring.

Usage:
1. Place tak_oscillateMaker.py file in your scripts folder.
2. In the python tab in maya, write below command.
import tak_oscillateMaker
tak_oscillateMaker.UI()
'''

import maya.cmds as cmds

def UI():
    if cmds.window('omWin', exists = True): cmds.deleteUI('omWin')

    cmds.window('omWin', title = 'Oscillate Maker')

    cmds.tabLayout('mainTab', tv = False)
    cmds.tabLayout('subTab', tv = False, scrollable = True)

    cmds.columnLayout('mainCol')

    cmds.optionMenu('attrMenu', label = 'Attribute:   ')

    # populate the attribute optionMenu
    popAttrMenu()

    cmds.separator(h = 5)
    cmds.textFieldGrp("amountText", label = "Amount: ", columnAlign = [(1, "left")], columnWidth = [(1, 57), (2, 81)])

    cmds.separator(h = 5)
    cmds.textFieldGrp("numText", label = "Number of: ", columnAlign = [(1, "left")], columnWidth = [(1, 57), (2, 81)])

    cmds.separator(h = 5)
    cmds.textFieldGrp("interText", label = "Interval: ", columnAlign = [(1, "left")], columnWidth = [(1, 57), (2, 81)])

    cmds.separator(h = 5)
    cmds.button("doButton", label = "Do it", w = 141, h = 40, c = app)

    cmds.setParent('subTab')


    cmds.window('omWin', e = True, w = 166, h = 170)
    cmds.showWindow('omWin')


# populate attrMenu with attributes of selection
def popAttrMenu():
    attrList = cmds.listAttr(keyable = True)

    for attr in attrList:
        cmds.menuItem(label = attr, parent = "attrMenu")


# main funtion
def app(*args):
    # object list that selected
    selObjs = cmds.ls(sl = True)

    # get the selected attribute
    attr = cmds.optionMenu('attrMenu', q = True, v = True)

    # option informations
    amount = int(cmds.textFieldGrp("amountText", q = True, text = True))
    numOf = int(cmds.textFieldGrp("numText", q = True, text = True))
    interval = int(cmds.textFieldGrp("interText", q = True, text = True))

    # get current frame
    curFrame = cmds.currentTime(q = True)

    # get current attribute value
    curAttrVal = cmds.getAttr("%s.%s" %(selObjs[0], attr))

    # set amount to relative to curAttrVal
    resultValue = curAttrVal + amount

    # calculate decrement of attribute value
    decrement = float(amount) / float(numOf)

    # set signal variable
    signal = -1

    for n in range(numOf + 1):
        # set keyframe
        cmds.setKeyframe(*selObjs, attribute = attr, v = resultValue, t = curFrame)

        # if initial amount value is negative, change the signal
        if amount < 0: signal = 1

        # recalculate amount
        amount = (abs(amount) - abs(decrement)) * signal

        # get result value for keyframe
        resultValue = curAttrVal + amount

        # change signal to make oscillate
        signal *= -1

        # set next frame
        curFrame += interval