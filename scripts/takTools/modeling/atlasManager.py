from maya import cmds

from ..utils import material as matUtil
from ..utils import uv as uvUtil

from importlib import reload; reload(matUtil)
from importlib import reload; reload(uvUtil)



class AtlasManager():
    DEFAULT_GRID_COUNT = 2
    DEFAULT_CELL_SIZE = 100.0

    def __init__(self):
        self._gridCount = 2
        self._cellSize = 100.0
        self._textureSize = 4096

    def show(self):
        if cmds.window("atlasManagerWin", exists=True):
            cmds.deleteUI("atlasManagerWin", window=True)

        self.win = cmds.window("atlasManagerWin", title="Atlas Manager")
        cmds.columnLayout(adjustableColumn=True)

        cmds.rowColumnLayout(numberOfColumns=3)

        # --- Grid GUIs --- start
        cmds.columnLayout(adjustableColumn=True)
        cmds.optionMenuGrp(label="Grid:", columnWidth=[(1, 75)], cc=self._updateGrid)
        cmds.menuItem(label="2x2")
        cmds.menuItem(label="3x3")
        cmds.menuItem(label="4x4")

        self._gridLayout = cmds.gridLayout(numberOfColumns=2, cellWidthHeight=(self._cellSize, self._cellSize), vis=True)
        cmds.textField()
        cmds.textField()
        cmds.textField()
        cmds.textField()
        cmds.setParent('..')
        cmds.setParent('..')
        # --- Grid GUIs --- end

        cmds.separator(width=10, horizontal=False, style='in')

        # --- Texture GUIs --- start
        cmds.columnLayout(adjustableColumn=True)
        cmds.optionMenuGrp(label="Texture Size:", columnWidth=[(1, 70)], cc=self._updateTextureSize)
        cmds.menuItem(label="4096x4096")
        cmds.menuItem(label="2048x2048")
        self._diffuseTxtFldBtnGrp = cmds.textFieldButtonGrp(label="Diffuse Texture Path: ", bl='<<', bc=lambda : self._showFileDialog(self._diffuseTxtFldBtnGrp))
        self._normalTxtFldBtnGrp = cmds.textFieldButtonGrp(label="Normal Texture Path: ", bl='<<', bc=self._showFileDialog)
        cmds.setParent('..')
        cmds.setParent('..')
        # --- Texture GUIs --- end

        cmds.separator(height=10, style='in')
        cmds.button(label="Atlas UVs and Textures", command=self.atlasButtonCmd)

        cmds.window(self.win, e=True, widthHeight=(600, 300))
        cmds.showWindow(self.win)

    def _updateGrid(self, selectedItem):
        # Clear existing text fields
        children = cmds.gridLayout(self._gridLayout, query=True, childArray=True) or []
        cmds.deleteUI(children)

        # Update grid layout
        self._gridCount = int(selectedItem.split('x')[0])
        self._cellSize = AtlasManager.DEFAULT_CELL_SIZE * (AtlasManager.DEFAULT_GRID_COUNT/self._gridCount)
        numTxtFields = self._gridCount * self._gridCount
        cmds.gridLayout(self._gridLayout, edit=True, numberOfColumns=self._gridCount, cellWidthHeight=(self._cellSize, self._cellSize))
        for i in range(numTxtFields):
            cmds.textField(p=self._gridLayout)

    def _updateTextureSize(self, selectedItem):
        self._textureSize = int(selectedItem.split('x')[0])

    def _showFileDialog(self, *args):
        filePath = cmds.fileDialog2(fileMode=0, caption="Select Texture File")
        if filePath:
            callingTxtFldBtnGrp = args[0]
            cmds.textFieldButtonGrp(callingTxtFldBtnGrp, edit=True, text=filePath[0])

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

        # Atlas diffuse texture
        diffuseTexturePath = cmds.textFieldButtonGrp(self._diffuseTxtFldBtnGrp, q=True, text=True)
        if diffuseTexturePath:
            matUtil.atlasTextures(meshes, atlasImageWidthHeight=self._textureSize, atlasImagePath=diffuseTexturePath, type='diffuse')

        # Atlas normal texture
        normalTexturePath = cmds.textFieldButtonGrp(self._normalTxtFldBtnGrp, q=True, text=True)
        if normalTexturePath:
            matUtil.atlasTextures(meshes, atlasImageWidthHeight=self._textureSize, atlasImagePath=normalTexturePath, type='normal')

        # Create and assign material with atlas textures
        mat = cmds.shadingNode('blinn', n='atlasMat', asShader=True)
        cmds.select([mesh for mesh in meshes if not mesh == ''], r=True)
        cmds.hyperShade(assign=mat)

        if diffuseTexturePath:
            diffuseTextureNode = cmds.shadingNode('file', asTexture=True)
            cmds.setAttr(f'{diffuseTextureNode}.fileTextureName', diffuseTexturePath, type='string')
            cmds.connectAttr(f'{diffuseTextureNode}.outColor', f'{mat}.color')

        if normalTexturePath:
            normalTextureNode = cmds.shadingNode('file', asTexture=True)
            cmds.setAttr(f'{normalTextureNode}.fileTextureName', normalTexturePath, type='string')
            bump2dNode = cmds.shadingNode('bump2d', asUtility=True)
            cmds.connectAttr(f'{normalTextureNode}.outAlpha', f'{bump2dNode}.bumpValue')
            cmds.connectAttr(f'{bump2dNode}.outNormal', f'{mat}.normalCamera')