from maya import cmds


def hashRename(objects, name, startNumber):
    splitedName = name.split('#')
    beforeName = splitedName[0]
    afterName = splitedName[-1]
    padding = name.count('#')
    for i in range(len(objects)):
        newName = '{beforeName}{number}{afterName}'.format(
            beforeName=beforeName,
            number=str(startNumber + i).zfill(padding),
            afterName=afterName
        )
        cmds.rename(objects[i], newName)


def showHashRenamerUI():
    if cmds.window('hashRenamerWindow', q=True, exists=True):
        cmds.deleteUI('hashRenamerWindow')

    cmds.window('hashRenamerWindow', title='Hash Renamer UI', w=200, mnb=False, mxb=False)
    cmds.columnLayout('mainLayout', adj=True)

    cmds.textField('hashNameTextField', placeholderText='Enter name with hash(#) character')

    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.text(label='startNumber: ')
    cmds.intField('startNumberIntField', value=1)

    cmds.setParent('mainLayout')
    cmds.button(label='Apply', c=applyButtonCallback)

    cmds.showWindow()


def applyButtonCallback(*args):
    selectedObjects = cmds.ls(sl=True)
    hashName = cmds.textField('hashNameTextField', q=True, text=True)
    startNumber = cmds.intField('startNumberIntField', q=True, value=True)
    hashRename(selectedObjects, hashName, startNumber)

