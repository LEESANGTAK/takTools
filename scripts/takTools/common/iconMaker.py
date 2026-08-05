from maya.api import OpenMaya as om
from maya.api import OpenMayaUI as omui
from maya import cmds
import os


MODULE_NAME = 'takTools'
MODULE_PATH = __file__.split(MODULE_NAME, 1)[0].replace('\\', '/') + MODULE_NAME


class IconMakerGUI(object):
    DEFAULT_ICON_PATH = '{}/icons/icon.png'.format(MODULE_PATH)

    def __init__(self):
        self.__build()
        self.__createCaptureCam()
        self.__connect()
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", True)
        curLineWidth = cmds.displayPref(q=True, lineWidth=True)
        cmds.floatSliderGrp(self.__lineWidthSlider, e=True, v=curLineWidth)

    def show(self):
        cmds.showWindow(self.__win)
        self.__fitAllObjects()

    def __build(self):
        if cmds.modelEditor('captureModelEditor', exists=True):
            cmds.deleteUI('captureModelEditor')

        self.__win = cmds.window(title='Icon Maker GUI', mnb=False, mxb=False)

        mainFormLayout = cmds.formLayout()

        buttonLayout = cmds.rowColumnLayout(numberOfColumns=6)
        self.__sizeOptMenuGrp = cmds.optionMenuGrp(label='Size: ', columnWidth=[(1, 30), (2, 30)])
        cmds.menuItem(label='32')
        cmds.menuItem(label='64')
        cmds.menuItem(label='128')
        cmds.optionMenuGrp(self.__sizeOptMenuGrp, e=True, v='64')
        self.__lineWidthSlider = cmds.floatSliderGrp(label='Line Width: ', min=1.0, max=10.0, columnWidth=[(1, 70), (2, 70)])
        self.__wireBtn = cmds.symbolButton(image='WireFrame.png')
        self.__wireShadeBtn = cmds.symbolButton(image='WireFrameOnShaded.png')
        self.__textureBtn = cmds.symbolButton(image='Textured.png')
        self.__fitBtn = cmds.symbolButton(image='zoom.png')

        cmds.setParent(mainFormLayout)
        self.__modelEditor = cmds.modelEditor('captureModelEditor')
        cmds.modelEditor(self.__modelEditor, e=True, hud=False)
        cmds.modelEditor(self.__modelEditor, e=True, grid=False)
        cmds.modelEditor(self.__modelEditor, e=True, displayTextures=False)
        cmds.modelEditor(self.__modelEditor, e=True, displayAppearance='smoothShaded')
        cmds.modelEditor(self.__modelEditor, edit=True, jointXray=True)

        captureLayout = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 30), (2, 260), (3, 38)])
        self.__iconPathBtn = cmds.symbolButton(image='fileOpen.png')
        self.__filePathFld = cmds.textField(text=IconMakerGUI.DEFAULT_ICON_PATH)
        self.__captureBtn = cmds.symbolButton(image='UVEditorSnapshot.png')

        cmds.formLayout(mainFormLayout, edit=True,
            attachForm=[
                (buttonLayout, 'top', 0), (buttonLayout, 'left', 0), (buttonLayout, 'right', 0),
                (self.__modelEditor, 'left', 0), (self.__modelEditor, 'right', 0),
                (captureLayout, 'bottom', 0), (captureLayout, 'left', 0), (captureLayout, 'right', 0)
            ],
            attachControl=[
                (self.__modelEditor, 'top', 0, buttonLayout), (self.__modelEditor, 'bottom', 0, captureLayout)
            ]
        )

        cmds.window(self.__win, e=True, w=100, h=394, sizeable=False)

    def __createCaptureCam(self):
        self.__capCam = cmds.camera(n='captureCam')[0]
        cmds.setAttr(self.__capCam + '.translate', 0, 15, 0)
        cmds.setAttr(self.__capCam + '.rotate', -90, 0, 0)
        cmds.setAttr(self.__capCam + '.focalLength', 500)
        cmds.hide(self.__capCam)
        cmds.modelEditor(self.__modelEditor, edit=True, camera=self.__capCam)

    def __connect(self):
        cmds.window(self.__win, e=True, closeCommand=self.__closeCallback)
        cmds.floatSliderGrp(self.__lineWidthSlider, e=True, dragCommand=self.__setLineWidth)
        cmds.symbolButton(self.__wireBtn, e=True, command=self.__toggleWireframe)
        cmds.symbolButton(self.__wireShadeBtn, e=True, command=self.__toggleWireframeShade)
        cmds.symbolButton(self.__textureBtn, e=True, command=self.__toggleDisplayTexture)
        cmds.symbolButton(self.__fitBtn, e=True, command=self.__fitAllObjects)
        cmds.symbolButton(self.__iconPathBtn, e=True, command=self.__getFilePath)
        cmds.symbolButton(self.__captureBtn, e=True, command=self.__captureViewport)

    def __closeCallback(self):
        cmds.delete(self.__capCam)

    def __setLineWidth(self, *args):
        width = cmds.floatSliderGrp(self.__lineWidthSlider, q=True, value=True)
        cmds.modelEditor(self.__modelEditor, e=True, lineWidth=width)

    def __toggleWireframe(self, *args):
        curDisplayAppearance = cmds.modelEditor(self.__modelEditor, q=True, displayAppearance=True)
        if curDisplayAppearance == 'wireframe':
            cmds.modelEditor(self.__modelEditor, e=True, displayAppearance='smoothShaded')
            cmds.symbolButton(self.__wireBtn, e=True, bgc=(0.267, 0.267, 0.267))
        elif curDisplayAppearance == 'smoothShaded':
            cmds.modelEditor(self.__modelEditor, e=True, displayAppearance='wireframe')
            cmds.symbolButton(self.__wireBtn, e=True, bgc=(0.322, 0.522, 0.651))

    def __toggleWireframeShade(self, *args):
        wireframeOnShaded = cmds.modelEditor(self.__modelEditor, q=True, wireframeOnShaded=True)
        if wireframeOnShaded:
            cmds.modelEditor(self.__modelEditor, e=True, wireframeOnShaded=False)
            cmds.symbolButton(self.__wireShadeBtn, e=True, bgc=(0.267, 0.267, 0.267))
        else:
            cmds.modelEditor(self.__modelEditor, e=True, wireframeOnShaded=True)
            cmds.symbolButton(self.__wireShadeBtn, e=True, bgc=(0.322, 0.522, 0.651))

    def __toggleDisplayTexture(self, *args):
        displayTextures = cmds.modelEditor(self.__modelEditor, q=True, displayTextures=True)
        if displayTextures:
            cmds.modelEditor(self.__modelEditor, e=True, displayTextures=False)
            cmds.symbolButton(self.__textureBtn, e=True, bgc=(0.267, 0.267, 0.267))
        else:
            cmds.modelEditor(self.__modelEditor, e=True, displayTextures=True)
            cmds.symbolButton(self.__textureBtn, e=True, bgc=(0.322, 0.522, 0.651))

    def __fitAllObjects(self, *args):
        cmds.modelEditor(self.__modelEditor, e=True, activeView=True)
        cmds.viewFit(all=True)

    def __getFilePath(self, *args):
        startDir = os.path.dirname(cmds.textField(self.__filePathFld, q=True, text=True))
        filePath = cmds.fileDialog2(fileMode=0, caption='Save as', fileFilter='*.png;;*.jpg', startingDirectory=startDir)
        if filePath:
            cmds.textField(self.__filePathFld, e=True, text=filePath[0])

    def __captureViewport(self, *args):
        cmds.setFocus('modelPanel4')  # This is a tricky part

        iconSize = int(cmds.optionMenuGrp(self.__sizeOptMenuGrp, q=True, v=True))
        iconPath = cmds.textField(self.__filePathFld, q=True, text=True)
        ext = os.path.splitext(iconPath)[-1].strip('.')

        img = om.MImage()
        view = omui.M3dView.getM3dViewFromModelEditor(self.__modelEditor)
        view.pushViewport(0, 0, view.portWidth(), view.portHeight())
        view.refresh()
        view.readColorBuffer(img, True)
        view.popViewport()
        img.resize(iconSize, iconSize, False)
        img.writeToFile(iconPath, ext)

        if cmds.textField('iconNameTxtFld', exists=True):
            cmds.textField('iconNameTxtFld', e=True, text=os.path.basename(iconPath))
            cmds.deleteUI(self.__win)
