'''
Toolname: multi constraint
Author: Sang-tak Lee
Contact: chst27@nate.com

usage: import tak_mulConst
       tak_mulConst.UI()
'''


import maya.cmds as cmds
from functools import partial


def UI():
    # check the window existing
    if cmds.window('win', q = True, exists = True): cmds.deleteUI('win')
    
    # create window
    cmds.window('win', title = 'Multi Constraint')
    
    # set the main formLayout
    cmds.formLayout('mainFormLay', numberOfDivisions = 100)
    
    # create main tab layout
    cmds.tabLayout('mainTabLay', tabsVisible = False)
    cmds.tabLayout('subTabLay', tabsVisible = False, scrollable = True)
    
    # main columnLayout
    cmds.columnLayout('mainColLay', adj = True)    
    
    # sub formLayout
    cmds.formLayout('subFormLay', nd = 100, h = 240)
    
    # create driver, driven frame
    cmds.frameLayout('drvFram', label = 'Driver')
    
    # formLayout in driver frameLayout
    cmds.formLayout('drvFormLay', nd = 100)
    
    cmds.textScrollList('drvTexScLi', allowMultiSelection = True, sc = partial(sel, 'drvTexScLi'))
    cmds.button('drvLoadSelButt', label = 'Load Sel', c = partial(load, 'drvTexScLi'))
    cmds.button('drvAddButt', label = 'Add', c = partial(add, 'drvTexScLi'))
    cmds.button('drvDelButt', label = 'Del', c = partial(_del, 'drvTexScLi'))
        
    # parent driver formLayout to the driver frameLayout
    cmds.setParent('drvFram')
    
    # arrange driver formLayout
    cmds.formLayout('drvFormLay', e = True,
                    attachForm = [('drvTexScLi', 'top', 5), ('drvTexScLi', 'left', 5), ('drvTexScLi', 'right', 5), ('drvLoadSelButt', 'left', 5), ('drvLoadSelButt', 'bottom', 5), ('drvDelButt', 'right', 5), ('drvDelButt', 'bottom', 5), ('drvAddButt', 'bottom', 5)],
                    attachPosition = [('drvLoadSelButt', 'right', 5, 35), ('drvDelButt', 'left', 5, 65)],
                    attachControl = [('drvAddButt', 'left', 5, 'drvLoadSelButt'), ('drvAddButt', 'right', 5, 'drvDelButt'), ('drvTexScLi', 'bottom', 5, 'drvAddButt')])
    
    # parent driver frameLayout to the subFormLayout
    cmds.setParent('subFormLay')    
    
    # driven frameLayout
    cmds.frameLayout('drnFram', label = 'Driven')
    
    # formLayout in driver frameLayout
    cmds.formLayout('drnFormLay', nd = 100)
    
    cmds.textScrollList('drnTexScLi', allowMultiSelection = True, sc = partial(sel, 'drnTexScLi'))
    cmds.button('drnLoadSelButt', label = 'Load Sel', c = partial(load, 'drnTexScLi'))
    cmds.button('drnAddButt', label = 'Add', c = partial(add, 'drnTexScLi'))
    cmds.button('drnDelButt', label = 'Del', c = partial(_del, 'drnTexScLi'))
    
    # parent driver formLayout to the driver frameLayout
    cmds.setParent('drnFram')
    
    # arrange driver formLayout
    cmds.formLayout('drnFormLay', e = True,
                    attachForm = [('drnTexScLi', 'top', 5), ('drnTexScLi', 'left', 5), ('drnTexScLi', 'right', 5), ('drnLoadSelButt', 'left', 5), ('drnLoadSelButt', 'bottom', 5), ('drnDelButt', 'right', 5), ('drnDelButt', 'bottom', 5), ('drnAddButt', 'bottom', 5)],
                    attachPosition = [('drnLoadSelButt', 'right', 5, 35), ('drnDelButt', 'left', 5, 65)],
                    attachControl = [('drnAddButt', 'left', 5, 'drnLoadSelButt'), ('drnAddButt', 'right', 5, 'drnDelButt'), ('drnTexScLi', 'bottom', 5, 'drnAddButt')])    
    
    # parent driven frameLayout to the subFormLayout
    cmds.setParent('subFormLay')   
    
    # parent subFormLayout to the subTabLayout
    cmds.setParent('mainColLay')
    
    # arrange the subFormLayout
    cmds.formLayout('subFormLay', e = True,
                    attachForm = [('drvFram', 'top', 5), ('drvFram', 'left', 5), ('drnFram', 'top', 5), ('drnFram', 'right', 5), ('drvFram', 'bottom', 5), ('drnFram', 'bottom', 5)],
                    attachPosition = [('drvFram', 'right', 5, 50), ('drnFram', 'left', 5, 50)])
    
    # separator
    cmds.separator(h = 15, style = 'in')
    
    # type of constraint check boxes
    cmds.checkBoxGrp('constChkBox', label = 'Type of Constraint: ', numberOfCheckBoxes = 4, label1 = 'Point', label2 = 'Orient', label3 = 'Scale', label4 = 'Parent', on4 = partial(parentOn, 'constChkBox'), on1 = partial(pntOn, 'constChkBox'), on2 = partial(OriOn, 'constChkBox'), v4 = True)
    cmds.checkBoxGrp('constChkBox1', label = '', numberOfCheckBoxes = 1, label1 = 'Aim', on1 = partial(aimLoOn, 'aimOptColLo'), of1 = partial(aimLoOff, 'aimOptColLo'))

    # Aim constraint options.
    cmds.columnLayout('aimOptColLo', adj = True, visible = False)
    cmds.separator(style = 'in', h = 5)
    cmds.floatFieldGrp('aimVecFltFldGrp', numberOfFields = 3, label = 'Driven Aim Vector: ', value1 = 1.0, value2 = 0.0, value3 = 0.0)
    cmds.floatFieldGrp('upVecFltFldGrp', numberOfFields = 3, label = 'Driven Up Vector: ', value1 = 0.0, value2 = 0.0, value3 = 1.0)
    cmds.optionMenuGrp('wrldUpTypeOptMenuGrp', l = 'Up Vector Follow Type:', cc = aimUiEnDis)
    cmds.menuItem(label = 'Scene Up')
    cmds.menuItem(label = 'Object Up')
    cmds.menuItem(label = 'Object Rotation Up')
    cmds.menuItem(label = 'Vector')
    cmds.menuItem(label = 'None')
    cmds.optionMenuGrp('wrldUpTypeOptMenuGrp', e = True, v ='Vector')
    cmds.textFieldGrp('wrldUpObjTxtFldGrp', label = 'Up Vector Follow Object: ', enable = False)
    cmds.floatFieldGrp('wrldUpVecFltFldGrp', numberOfFields = 3, label = 'Up Vector Follow Vector: ', value1 = 1.0, value2 = 0.0, value3 = 0.0)
    cmds.separator(style = 'in', h = 5)
    cmds.setParent('mainColLay')


    cmds.checkBoxGrp('cnstAxesChkBoxGrp', label = 'Constraint Axes: ', numberOfCheckBoxes = 4, label1 = 'All', label2 = 'X', label3 = 'Y', label4 = 'Z', v1 = True, on1 = partial(cnstAxesAllOn, 'cnstAxesChkBoxGrp'), on2 = partial(cnstAxesXYZOn, 'cnstAxesChkBoxGrp'), on3 = partial(cnstAxesXYZOn, 'cnstAxesChkBoxGrp'), on4 = partial(cnstAxesXYZOn, 'cnstAxesChkBoxGrp'))
    
    # maintain offset option checkBox
    cmds.checkBoxGrp('mainOffBox', v1 = True, label = 'Maintain offset: ', numberOfCheckBoxes = 1)      
    
    # parent mainColumnLayout
    cmds.setParent('subTabLay')   
    
    # parent mainTabLayout to the mainFormLayout
    cmds.setParent('mainFormLay')    
    
    # create apply, close button
    cmds.button('appButt', label = 'Apply', c = app)
    cmds.button('closButt', label = 'Close', c = delWin)
    
    # arrange the mainFormLayout
    cmds.formLayout('mainFormLay', e= True,
                    attachForm = [('mainTabLay', 'top', 5), ('mainTabLay', 'left', 5), ('mainTabLay', 'right', 5),
                                  ('appButt', 'left', 5), ('appButt', 'bottom', 5),
                                  ('closButt', 'right', 5), ('closButt', 'bottom', 5)],
                    attachControl = [('appButt', 'top', 5, 'mainTabLay'), ('closButt', 'top', 5, 'mainTabLay')],
                    attachPosition = [('mainTabLay', 'bottom', 5, 90),
                                      ('appButt', 'right', 2.5, 50), ('closButt', 'left', 2.5, 50)])
    
    # set the window size and show the window
    cmds.window('win', e = True, w = 570, h = 400, sizeable = True)
    cmds.showWindow('win')


# define function for 'load sel' button
def load(texScLiName, arg = None):
    selList = cmds.ls(sl = True)
    cmds.textScrollList(texScLiName, e = True, ra = True)
    cmds.textScrollList(texScLiName, e = True, append = selList)

    
# define function for 'add' button
def add(texScLiName, arg = None):
    selList = set(cmds.ls(sl = True))
    
    # get current driver textScrollList all items
    curItems = cmds.textScrollList(texScLiName, q = True, allItems = True)
    
    # in case that current items exists
    if curItems:
        
        # make current items to the set data type
        curItems = set(curItems)
        
        # if exists the same item in current items, remove the item in selection list
        addList = list(selList - curItems)
        
        cmds.textScrollList(texScLiName, e = True, append = addList)
    
    # in case that current items not exists
    else:
        selList = cmds.ls(sl = True)
        cmds.textScrollList(texScLiName, e = True, append = selList)

        
# define the function that 'del' button
def _del(texScLiName, arg = None):
    selItems = cmds.textScrollList(texScLiName, q = True, selectItem = True)
    cmds.textScrollList(texScLiName, e = True, removeItem = selItems)    

    
# apply button
def app(*args):
    # get the drivers
    drivers = cmds.textScrollList('drvTexScLi', q = True, allItems = True)
    
    # get the drivens
    drivens = cmds.textScrollList('drnTexScLi', q = True, allItems = True)
    
    # get type of constraint option
    pointOpt = cmds.checkBoxGrp('constChkBox', q = True, v1 = True)
    orientOpt = cmds.checkBoxGrp('constChkBox', q = True, v2 = True)
    scaleOpt = cmds.checkBoxGrp('constChkBox', q = True, v3 = True)
    parentOpt = cmds.checkBoxGrp('constChkBox', q = True, v4 = True)
    aimOpt = cmds.checkBoxGrp('constChkBox1', q = True, v1 = True)

    # Constraint axes options.
    allAxes = cmds.checkBoxGrp('cnstAxesChkBoxGrp', q = True, v1 = True)
    xAxes = cmds.checkBoxGrp('cnstAxesChkBoxGrp', q = True, v2 = True)
    yAxes = cmds.checkBoxGrp('cnstAxesChkBoxGrp', q = True, v3 = True)
    zAxes = cmds.checkBoxGrp('cnstAxesChkBoxGrp', q = True, v4 = True)

    skipAxesLs = []

    if allAxes:
        skipAxesLs = []
    else:
        if not xAxes:
            skipAxesLs.append('x')
        if not yAxes:
            skipAxesLs.append('y')
        if not zAxes:
            skipAxesLs.append('z')

    
    # get if maintain offset
    mainOffOpt = cmds.checkBoxGrp('mainOffBox', q = True, v1 = True)
    
    # go constraints
    if pointOpt: point(drivers, drivens, mainOffOpt, skipAxesLs)
    if orientOpt: orient(drivers, drivens, mainOffOpt, skipAxesLs)
    if scaleOpt: scale(drivers, drivens, mainOffOpt, skipAxesLs)
    if parentOpt: parent(drivers, drivens, mainOffOpt, skipAxesLs)
    if aimOpt: aim(drivers, drivens, mainOffOpt, skipAxesLs)

        
# command that close window
def delWin(*args):
    cmds.deleteUI('win')
 
    
# point constraint function
def point(drivers, drivens, mainOffOpt, skipAxesLs, arg = None):
    for driver in drivers:
        for driven in drivens:
            cmds.pointConstraint(driver, driven, mo = mainOffOpt, skip = skipAxesLs)


# orient constraint function
def orient(drivers, drivens, mainOffOpt, skipAxesLs, arg = None):
    for driver in drivers:
        for driven in drivens:
            cmds.orientConstraint(driver, driven, mo = mainOffOpt, skip = skipAxesLs)

            
# scale constraint function
def scale(drivers, drivens, mainOffOpt, skipAxesLs, arg = None):
    for driver in drivers:
        for driven in drivens:
            cmds.scaleConstraint(driver, driven, mo = mainOffOpt, skip = skipAxesLs)


# parent constraint function
def parent(drivers, drivens, mainOffOpt, skipAxesLs, arg = None):
    for driver in drivers:
        for driven in drivens:
            cmds.parentConstraint(driver, driven, mo = mainOffOpt, st = skipAxesLs, sr = skipAxesLs)
 

# parent constraint function
def aim(drivers, drivens, mainOffOpt, skipAxesLs, arg = None):
    aimVec = cmds.floatFieldGrp('aimVecFltFldGrp', q = True, v = True)
    upVec = cmds.floatFieldGrp('upVecFltFldGrp', q = True, v = True)
    wrldUpType = cmds.optionMenuGrp('wrldUpTypeOptMenuGrp', q = True, v = True)
    wrldUpVec = cmds.floatFieldGrp('wrldUpVecFltFldGrp', q = True, v = True)
    wrldUpObj = cmds.textFieldGrp('wrldUpObjTxtFldGrp', q = True, text = True)

    for driver in drivers:
        for driven in drivens:
            if wrldUpType == 'Scene Up':
                cmds.aimConstraint(driver, driven, mo = mainOffOpt, skip = skipAxesLs, aimVector = aimVec, upVector = upVec, worldUpType = "scene")

            if wrldUpType == 'Object Up':
                cmds.aimConstraint(driver, driven, mo = mainOffOpt, skip = skipAxesLs, aimVector = aimVec, upVector = upVec, worldUpType = "object", worldUpObject = wrldUpObj)

            if wrldUpType == 'Object Rotation Up':
                cmds.aimConstraint(driver, driven, mo = mainOffOpt, skip = skipAxesLs, aimVector = aimVec, upVector = upVec, worldUpType = "objectrotation", worldUpVector = wrldUpVec, worldUpObject = wrldUpObj)

            if wrldUpType == 'Vector':
                cmds.aimConstraint(driver, driven, mo = mainOffOpt, skip = skipAxesLs, aimVector = aimVec, upVector = upVec, worldUpType = "vector", worldUpVector = wrldUpVec)

            if wrldUpType == 'None':
                cmds.aimConstraint(driver, driven, mo = mainOffOpt, skip = skipAxesLs, aimVector = aimVec, upVector = upVec, worldUpType = "none")

            
# define the function when item in textScrollList selected
def sel(texScLiName):
    # get selected items in specified textScrollList
    selItems = cmds.textScrollList(texScLiName, q = True, selectItem = True)
    
    cmds.select(cl = True)
    
    # select items
    for item in selItems:
        cmds.select(item, add = True)

        
# define the command when parent option on
def parentOn(chkBoxGrpName, arg = None):
    # disable point and orient check option
    cmds.checkBoxGrp(chkBoxGrpName, e = True, v1 = False, v2 = False)
    cmds.checkBoxGrp('constChkBox1', e = True, v1 = False)
    cmds.columnLayout('aimOptColLo', e = True, visible = False)

    
# Point or orient constraint option on function.
def pntOn(chkBoxGrpName, arg = None):
    cmds.checkBoxGrp(chkBoxGrpName, e = True, v4 = False)

def OriOn(chkBoxGrpName, arg = None):
    cmds.checkBoxGrp(chkBoxGrpName, e = True, v4 = False)
    cmds.checkBoxGrp('constChkBox1', e = True, v1 = False)
    cmds.columnLayout('aimOptColLo', e = True, visible = False)

# Aim option layout visible function.
def aimLoOn(aimColLoName, arg = None):
        cmds.checkBoxGrp('constChkBox', e = True, v2 = False, v4 = False)
        cmds.columnLayout(aimColLoName, e = True, visible = True)

def aimLoOff(aimColLoName, arg = None):
        cmds.columnLayout(aimColLoName, e = True, visible = False)


# Aim option ui enable function.
def aimUiEnDis(*args):
    # Get world up type option selected.
    selWrldUpType = cmds.optionMenuGrp('wrldUpTypeOptMenuGrp', q = True, v = True)

    if selWrldUpType == 'Scene Up':
        cmds.floatFieldGrp('wrldUpVecFltFldGrp', e = True, enable = False)
        cmds.textFieldGrp('wrldUpObjTxtFldGrp', e = True, enable = False)

    elif selWrldUpType == 'Object Up':
        cmds.floatFieldGrp('wrldUpVecFltFldGrp', e = True, enable = False)
        cmds.textFieldGrp('wrldUpObjTxtFldGrp', e = True, enable = True)

    if selWrldUpType == 'Object Rotation Up':
        cmds.floatFieldGrp('wrldUpVecFltFldGrp', e = True, enable = True)
        cmds.textFieldGrp('wrldUpObjTxtFldGrp', e = True, enable = True)

    if selWrldUpType == 'Vector':
        cmds.floatFieldGrp('wrldUpVecFltFldGrp', e = True, enable = True)
        cmds.textFieldGrp('wrldUpObjTxtFldGrp', e = True, enable = False)

    if selWrldUpType == 'None':
        cmds.floatFieldGrp('wrldUpVecFltFldGrp', e = True, enable = False)
        cmds.textFieldGrp('wrldUpObjTxtFldGrp', e = True, enable = False)


# Constraint axes all on function.
def cnstAxesAllOn(cnstAxesChkBoxName, arg = None):
    cmds.checkBoxGrp(cnstAxesChkBoxName, e = True, v2 = False, v3 = False, v4 = False)


# Constraint axes x, y, z on function.
def cnstAxesXYZOn(cnstAxesChkBoxName, arg = None):
    cmds.checkBoxGrp(cnstAxesChkBoxName, e = True, v1 = False)