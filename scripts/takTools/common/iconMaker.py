from maya.api import OpenMaya as om
from maya.api import OpenMayaUI as omui
from maya import cmds
import pymel.core as pm
import os


MODULE_NAME = 'takTools'
MODULE_PATH = __file__.split(MODULE_NAME, 1)[0].replace('\\', '/') + MODULE_NAME


class IconMakerGUI(object):
    DEFAULT_ICON_PATH = '{}/icons/icon.png'.format(MODULE_PATH)

    def __init__(self):
        self.__build()
        self.__createCaptureCam()
        self.__connect()
        pm.setAttr("hardwareRenderingGlobals.multiSampleEnable", True)
        curLineWidth = pm.displayPref(q=True, lineWidth=True)
        pm.floatSliderGrp(self.__lineWidthSlider, e=True, v=curLineWidth)

    def show(self):
        pm.showWindow(self.__win)
        self.__fitAllObjects()

    def __build(self):
        if pm.modelEditor('captureModelEditor', exists=True):
            cmds.deleteUI('captureModelEditor')

        self.__win = pm.window(title='Icon Maker GUI', mnb=False, mxb=False)

        mainFormLayout = pm.formLayout()

        buttonLayout = pm.rowColumnLayout(numberOfColumns=6)
        self.__sizeOptMenuGrp = pm.optionMenuGrp(label='Size: ', columnWidth=[(1, 30), (2, 30)])
        pm.menuItem(label='32')
        pm.menuItem(label='64')
        pm.menuItem(label='128')
        pm.optionMenuGrp(self.__sizeOptMenuGrp, e=True, v='64')
        self.__lineWidthSlider = pm.floatSliderGrp(label='Line Width: ', min=1.0, max=10.0, columnWidth=[(1, 70), (2, 70)])
        self.__wireBtn = pm.symbolButton(image='WireFrame.png')
        self.__wireShadeBtn = pm.symbolButton(image='WireFrameOnShaded.png')
        self.__textureBtn = pm.symbolButton(image='Textured.png')
        self.__fitBtn = pm.symbolButton(image='zoom.png')

        pm.setParent(mainFormLayout)
        self.__modelEditor = pm.modelEditor('captureModelEditor')
        pm.modelEditor(self.__modelEditor, e=True, hud=False)
        pm.modelEditor(self.__modelEditor, e=True, grid=False)
        pm.modelEditor(self.__modelEditor, e=True, displayTextures=False)
        pm.modelEditor(self.__modelEditor, e=True, displayAppearance='smoothShaded')
        pm.modelEditor(self.__modelEditor, edit=True, jointXray=True)

        captureLayout = pm.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 30), (2, 260), (3, 38)])
        self.__iconPathBtn = pm.symbolButton(image='fileOpen.png')
        self.__filePathFld = pm.textField(text=IconMakerGUI.DEFAULT_ICON_PATH)
        self.__captureBtn = pm.symbolButton(image='UVEditorSnapshot.png')

        pm.formLayout(mainFormLayout, edit=True,
            attachForm=[
                (buttonLayout, 'top', 0), (buttonLayout, 'left', 0), (buttonLayout, 'right', 0),
                (self.__modelEditor, 'left', 0), (self.__modelEditor, 'right', 0),
                (captureLayout, 'bottom', 0), (captureLayout, 'left', 0), (captureLayout, 'right', 0)
            ],
            attachControl=[
                (self.__modelEditor, 'top', 0, buttonLayout), (self.__modelEditor, 'bottom', 0, captureLayout)
            ]
        )

        pm.window(self.__win, e=True, w=100, h=394, sizeable=False)

    def __createCaptureCam(self):
        self.__capCam = pm.camera(n='captureCam')[0]
        self.__capCam.translate.set(0, 15, 0)
        self.__capCam.rotate.set(-90, 0, 0)
        self.__capCam.focalLength.set(500)
        self.__capCam.hide()
        pm.modelEditor(self.__modelEditor, edit=True, camera=self.__capCam)

    def __connect(self):
        pm.window(self.__win, e=True, closeCommand=self.__closeCallback)
        pm.floatSliderGrp(self.__lineWidthSlider, e=True, dragCommand=self.__setLineWidth)
        pm.symbolButton(self.__wireBtn, e=True, command=self.__toggleWireframe)
        pm.symbolButton(self.__wireShadeBtn, e=True, command=self.__toggleWireframeShade)
        pm.symbolButton(self.__textureBtn, e=True, command=self.__toggleDisplayTexture)
        pm.symbolButton(self.__fitBtn, e=True, command=self.__fitAllObjects)
        pm.symbolButton(self.__iconPathBtn, e=True, command=self.__getFilePath)
        pm.symbolButton(self.__captureBtn, e=True, command=self.__captureViewport)

    def __closeCallback(self):
        pm.delete(self.__capCam)

    def __setLineWidth(self, *args):
        width = pm.floatSliderGrp(self.__lineWidthSlider, q=True, value=True)
        pm.modelEditor(self.__modelEditor, e=True, lineWidth=width)

    def __toggleWireframe(self, *args):
        curDisplayAppearance = pm.modelEditor(self.__modelEditor, q=True, displayAppearance=True)
        if curDisplayAppearance == 'wireframe':
            pm.modelEditor(self.__modelEditor, e=True, displayAppearance='smoothShaded')
            pm.symbolButton(self.__wireBtn, e=True, bgc=(0.267, 0.267, 0.267))
        elif curDisplayAppearance == 'smoothShaded':
            pm.modelEditor(self.__modelEditor, e=True, displayAppearance='wireframe')
            pm.symbolButton(self.__wireBtn, e=True, bgc=(0.322, 0.522, 0.651))

    def __toggleWireframeShade(self, *args):
        wireframeOnShaded = pm.modelEditor(self.__modelEditor, q=True, wireframeOnShaded=True)
        if wireframeOnShaded:
            pm.modelEditor(self.__modelEditor, e=True, wireframeOnShaded=False)
            pm.symbolButton(self.__wireShadeBtn, e=True, bgc=(0.267, 0.267, 0.267))
        else:
            pm.modelEditor(self.__modelEditor, e=True, wireframeOnShaded=True)
            pm.symbolButton(self.__wireShadeBtn, e=True, bgc=(0.322, 0.522, 0.651))

    def __toggleDisplayTexture(self, *args):
        displayTextures = pm.modelEditor(self.__modelEditor, q=True, displayTextures=True)
        if displayTextures:
            pm.modelEditor(self.__modelEditor, e=True, displayTextures=False)
            pm.symbolButton(self.__textureBtn, e=True, bgc=(0.267, 0.267, 0.267))
        else:
            pm.modelEditor(self.__modelEditor, e=True, displayTextures=True)
            pm.symbolButton(self.__textureBtn, e=True, bgc=(0.322, 0.522, 0.651))

    def __fitAllObjects(self, *args):
        pm.modelEditor(self.__modelEditor, e=True, activeView=True)
        pm.viewFit(all=True)

    def __getFilePath(self, *args):
        startDir = os.path.dirname(pm.textField(self.__filePathFld, q=True, text=True))
        filePath = pm.fileDialog2(fileMode=0, caption='Save as', fileFilter='*.png;;*.jpg', startingDirectory=startDir)
        if filePath:
            pm.textField(self.__filePathFld, e=True, text=filePath[0])

    def __captureViewport(self, *args):
        pm.setFocus('modelPanel4')  # This is a tricky part

        iconSize = int(pm.optionMenuGrp(self.__sizeOptMenuGrp, q=True, v=True))
        iconPath = pm.textField(self.__filePathFld, q=True, text=True)
        ext = os.path.splitext(iconPath)[-1].strip('.')

        img = om.MImage()
        view = omui.M3dView.getM3dViewFromModelEditor(self.__modelEditor.name())
        view.pushViewport(0, 0, view.portWidth(), view.portHeight())
        view.refresh()
        view.readColorBuffer(img, True)
        view.popViewport()
        img.resize(iconSize, iconSize)
        img.writeToFile(iconPath, ext)

        if cmds.textField('iconNameTxtFld', exists=True):
            cmds.textField('iconNameTxtFld', e=True, text=os.path.basename(iconPath))
            pm.deleteUI(self.__win)
