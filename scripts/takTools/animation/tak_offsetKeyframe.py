'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Usage:
import tak_offsetKeyframe
tak_offsetKeyframe.UI()
'''

import maya.cmds as cmds

# UI
def UI():
    if cmds.window('offKeyWin', exists = True): cmds.deleteUI('offKeyWin')

    cmds.window('offKeyWin', title = 'Offset Keyframe')

    cmds.tabLayout('mainTab', tv = False)
    cmds.tabLayout('subTab', tv = False, scrollable = True)

    cmds.formLayout('mainForm', nd = 100, h = 90)

    cmds.text('desText', label = 'Slect objects in order that you want offset.')
    cmds.textFieldGrp('offTexGrp', label = 'Offset Value: ', cw = [(1, 70), (2, 50)])
    cmds.button('appButn', label = 'Apply', c = app)

    cmds.formLayout('mainForm', e = True,
                    attachForm = [('desText', 'top', 5), ('desText', 'left', 5), ('offTexGrp', 'left', 5), ('appButn', 'left', 5), ('appButn', 'bottom', 5), ('appButn', 'right', 5)],
                    attachControl = [('offTexGrp', 'top', 5, 'desText'), ('appButn', 'top', 5, 'offTexGrp')])

    cmds.setParent('subTab')

    cmds.window('offKeyWin', e = True, w = 235, h = 110)
    cmds.showWindow('offKeyWin')


# apply button
def app(*args):
    selList = cmds.ls(sl = True)
    # get offset value
    offVal = float(cmds.textFieldGrp('offTexGrp', q = True, text = True))
    increment = offVal

    for sel in selList:
        cmds.select(sel, r = True)
        cmds.keyframe(e = True, r = True, o = 'over', timeChange = offVal)
        offVal += increment