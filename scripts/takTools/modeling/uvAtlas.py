from maya import cmds

from ..utils import uv as uvUtil

from importlib import reload

reload(uvUtil)



class UVAtlas():
    DEFAULT_GRID_COUNT = 2
    DEFAULT_CELL_SIZE = 100.0

    def __init__(self):
        self._gridCount = 2
        self._cellSize = 100.0

    def show(self):
        if cmds.window("uvAtlasWin", exists=True):
            cmds.deleteUI("uvAtlasWin", window=True)

        self.win = cmds.window("uvAtlasWin", title="UV Atlas", mnb=False, mxb=False)
        cmds.columnLayout(adjustableColumn=True)

        # --- Grid GUIs --- start
        cmds.optionMenuGrp(label="Grid:", columnWidth=[(1, 75)], cc=self._updateGrid)
        cmds.menuItem(label="2x2")
        cmds.menuItem(label="4x4")

        self._gridLayout = cmds.gridLayout(numberOfColumns=2, cellWidthHeight=(self._cellSize, self._cellSize), vis=True)
        cmds.textField()
        cmds.textField()
        cmds.textField()
        cmds.textField()
        cmds.setParent('..')
        # --- Grid GUIs --- end

        cmds.separator(height=10, style='in')
        cmds.button(label="Atlas UV", command=self.atlasButtonCmd)

        cmds.window(self.win, e=True, widthHeight=(100, 100))
        cmds.showWindow(self.win)

    def _updateGrid(self, selectedItem):
        # Clear existing text fields
        children = cmds.gridLayout(self._gridLayout, query=True, childArray=True) or []
        cmds.deleteUI(children)

        # Update grid layout
        self._gridCount = int(selectedItem.split('x')[0])
        self._cellSize = UVAtlas.DEFAULT_CELL_SIZE * (UVAtlas.DEFAULT_GRID_COUNT/self._gridCount)
        numTxtFields = self._gridCount * self._gridCount
        cmds.gridLayout(self._gridLayout, edit=True, numberOfColumns=self._gridCount, cellWidthHeight=(self._cellSize, self._cellSize))
        for i in range(numTxtFields):
            cmds.textField(p=self._gridLayout)

    def atlasButtonCmd(self, *args):
        # Get mesh list from text fields matching the UV layout
        textFields = cmds.gridLayout(self._gridLayout, q=True, childArray=True)
        orderedTextFields = []
        for row in range(self._gridCount-1, -1, -1):
            for col in range(self._gridCount):
                index = row * self._gridCount + col
                orderedTextFields.append(textFields[index])
        meshes = [cmds.textField(tf, q=True, text=True) for tf in orderedTextFields]

        uvUtil.atlasUVs(meshes)
