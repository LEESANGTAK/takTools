import pymel.core as pm
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
        self.window.show()

    def _build(self):
        self.window = pm.window(
            UI.name,
            title='Ouliner Color',
            minimizeButton=False,
            maximizeButton=False
        )

        pm.columnLayout(
            columnAttach=('both', 5),
            backgroundColor=[.2, .2, .2],
            adj=True
        )

        self.colorTable = pm.gridLayout(
            allowEmptyCells=False,
            numberOfRowsColumns=(10, 5),
            cellWidthHeight=(40, 24),
            backgroundColor=(.2, .2, .2)
        )

        pm.window(self.window, e=True, w=10, h=10)

        self._populateColorTable()

    def _populateColorTable(self):
        for index in UI.colorSwatchIds:
            pm.canvas(
                ('%s%i' % ('colorCanvas_', index)),
                rgb=pm.colorIndex(index, q=True),
                pc=partial(setOutlinerColor, index),
                p=self.colorTable
            )


def showUI():
    if pm.window(UI.name, q=True, exists=True):
            pm.deleteUI(UI.name)
    ui = UI()
    ui.show()


def setOutlinerColor(index):
    selNods = pm.selected()
    if index == 3:
        for node in selNods:
            node.useOutlinerColor.set(False)
        return

    rgb = pm.colorIndex(index, q=True)
    for node in selNods:
        node.useOutlinerColor.set(True)
        node.outlinerColor.set(rgb)
