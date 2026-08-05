from maya import cmds
from functools import partial


class UI(object):
    name = 'outlinerColorWin'
    colorSwatchIds = [
        1, 2, 3, 11, 24,
        21, 12, 10, 25, 4,
        13, 20, 8, 30, 9,
        5, 6, 18, 15, 29,
        28, 7, 27, 19, 23,
        26, 14, 17, 22, 16
    ]

    def __init__(self):
        super(UI, self).__init__()
        colorTable = None
        window = None

    def show(self):
        self._build()
        cmds.showWindow(self.window)

    def _build(self):
        self.window = cmds.window(
            UI.name,
            title='Ouliner Color',
            minimizeButton=False,
            maximizeButton=False
        )

        cmds.columnLayout(
            columnAttach=('both', 5),
            backgroundColor=[.2, .2, .2],
            adj=True
        )

        self.colorTable = cmds.gridLayout(
            allowEmptyCells=False,
            numberOfRowsColumns=(10, 5),
            cellWidthHeight=(40, 24),
            backgroundColor=(.2, .2, .2)
        )

        cmds.window(self.window, e=True, w=10, h=10)

        self._populateColorTable()

    def _populateColorTable(self):
        for index in UI.colorSwatchIds:
            cmds.canvas(
                ('%s%i' % ('colorCanvas_', index)),
                rgb=cmds.colorIndex(index, q=True),
                pc=partial(setOutlinerColor, index),
                p=self.colorTable
            )


def showUI():
    if cmds.window(UI.name, q=True, exists=True):
            cmds.deleteUI(UI.name)
    ui = UI()
    ui.show()


def setOutlinerColor(index):
    selNods = cmds.ls(sl=True)
    if index == 3:
        for node in selNods:
            cmds.setAttr(f'{node}.useOutlinerColor', False)
        return

    rgb = cmds.colorIndex(index, q=True)
    for node in selNods:
        cmds.setAttr(f'{node}.useOutlinerColor', True)
        cmds.setAttr(f'{node}.outlinerColor', *rgb)
