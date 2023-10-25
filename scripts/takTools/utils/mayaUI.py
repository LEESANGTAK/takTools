'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This module is a set of functions that related with maya ui.
'''


from maya import cmds, mel
from ctypes import *



def loadSel(wdgType, wdgName, *args):
    '''
    Fill the text field with selected object.
    '''

    sel = cmds.ls(sl = True)[0]

    eval('cmds.%s("%s", e = True, text = sel)' %(wdgType, wdgName))


def populateTxtScrList(wdgType, wdgName, *args):
    '''
    Description:
    Populate text scroll list with selected objects.

    Arguments:
    wdgType(string), wdgName(string)

    Returns:
    Nothing
    '''

    selList = cmds.ls(sl = True, fl = True)

    items = eval('cmds.%s("%s", q = True, allItems = True)' %(wdgType, wdgName))
    if items:
        eval('cmds.%s("%s", e = True, removeAll = True)' %(wdgType, wdgName))

    eval('cmds.%s("%s", e = True, append = %s)' %(wdgType, wdgName, selList))


def txtScrLsSC(wdgName):
    '''
    textScrollList select command.
    '''

    selItem = cmds.textScrollList(wdgName, q = True, selectItem = True)
    cmds.select(selItem, r = True)


def getObjectPopMenus():
    objectPopMenus = []
    for menu in cmds.lsUI(menus=True):
        if "ObjectPop" in menu:
            objectPopMenu = menu.split(" ")[-1]
            objectPopMenus.append(objectPopMenu)
    return objectPopMenus


def restoreObjectPopMenu():
    objectPopMenus = getObjectPopMenus()
    for objectPopMenu in objectPopMenus:
        mel.eval('menu -edit -postMenuCommand ' '"buildObjectMenuItemsNow ' + objectPopMenu.replace('"', '') + '"' + objectPopMenu)
