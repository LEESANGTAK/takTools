from maya.api import OpenMaya as om
from maya.api import OpenMayaUI as omui
import pymel.core as pm
import os


class IconMakerGUI(object):
    DEFAULT_ICON_PATH = pm.about(preferences=True) + '/prefs/icons/icon.png'

    def __init__(self):
        self.__build()
        self.__createCaptureCam()
        self.__connect()
        pm.setAttr("hardwareRenderingGlobals.multiSampleEnable", True)

    def show(self):
        pm.showWindow(self.__win)
        self.__fitAllObjects()
        pm.mel.eval("setRendererInModelPanel $gLegacyViewport modelPanel4")

    def __build(self):
        self.__win = pm.window(title='Icon Maker GUI', mnb=False, mxb=False)

        mainFormLayout = pm.formLayout()

        buttonLayout = pm.rowColumnLayout(numberOfColumns=5)
        self.__sizeIntFldGrp = pm.intFieldGrp(label='Size: ', v1=128, columnWidth=[(1, 30), (2, 30)])
        self.__lineWidthSlider = pm.floatSliderGrp(label='Line Width: ', min=1.0, max=5.0, columnWidth=[(1, 70), (2, 70)])
        self.__wireBtn = pm.symbolButton(image='WireFrame.png')
        self.__textureBtn = pm.symbolButton(image='Textured.png')
        self.__fitBtn = pm.symbolButton(image='zoom.png')

        pm.setParent(mainFormLayout)
        self.__modelEditor = pm.modelEditor('captureModelEditor')
        pm.modelEditor(self.__modelEditor, e=True, hud=False)
        pm.modelEditor(self.__modelEditor, e=True, grid=False)
        pm.modelEditor('{}'.format(self.__modelEditor), e=True, displayTextures=False)
        pm.modelEditor(self.__modelEditor, e=True, displayAppearance='smoothShaded')

        captureLayout = pm.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 30), (2, 230), (3, 38)])
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

        pm.window(self.__win, e=True, w=100, h=363, sizeable=False)

    def __createCaptureCam(self):
        self.__capCam = pm.camera(n='captureCam')[0]
        self.__capCam.translate.set(0, 15, 0)
        self.__capCam.rotate.set(-90, 0, 0)
        self.__capCam.hide()
        pm.modelEditor(self.__modelEditor, edit=True, camera=self.__capCam)

    def __connect(self):
        pm.window(self.__win, e=True, closeCommand=self.__closeCallback)
        pm.floatSliderGrp(self.__lineWidthSlider, e=True, dragCommand=self.__setLineWidth)
        pm.symbolButton(self.__wireBtn, e=True, command=self.__toggleWireframe)
        pm.symbolButton(self.__textureBtn, e=True, command=self.__toggleDisplayTexture)
        pm.symbolButton(self.__fitBtn, e=True, command=self.__fitAllObjects)
        pm.symbolButton(self.__iconPathBtn, e=True, command=self.__getFilePath)
        pm.symbolButton(self.__captureBtn, e=True, command=self.__captureViewport)

    def __closeCallback(self):
        pm.delete(self.__capCam)
        pm.mel.eval("setRendererInModelPanel $gViewport2 modelPanel4")

    def __setLineWidth(self, *args):
        width = pm.floatSliderGrp(self.__lineWidthSlider, q=True, value=True)
        pm.modelEditor('{}'.format(self.__modelEditor), e=True, lineWidth=width)

    def __toggleWireframe(self, *args):
        curDisplayAppearance = pm.modelEditor('{}'.format(self.__modelEditor), q=True, displayAppearance=True)
        if curDisplayAppearance == 'wireframe':
            pm.modelEditor('{}'.format(self.__modelEditor), e=True, displayAppearance='smoothShaded')
            pm.symbolButton(self.__wireBtn, e=True, bgc=(0.267, 0.267, 0.267))
        elif curDisplayAppearance == 'smoothShaded':
            pm.modelEditor('{}'.format(self.__modelEditor), e=True, displayAppearance='wireframe')
            pm.symbolButton(self.__wireBtn, e=True, bgc=(0.322, 0.522, 0.651))

    def __toggleDisplayTexture(self, *args):
        curDisplayAppearance = pm.modelEditor('{}'.format(self.__modelEditor), q=True, displayAppearance=True)
        if curDisplayAppearance != 'smoothShaded':
            pm.modelEditor('{}'.format(self.__modelEditor), e=True, displayAppearance='smoothShaded')
            pm.modelEditor('{}'.format(self.__modelEditor), e=True, displayTextures=True)
            pm.symbolButton(self.__wireBtn, e=True, bgc=(0.267, 0.267, 0.267))
        else:
            curTextureState = pm.modelEditor('{}'.format(self.__modelEditor), q=True, displayTextures=True)
            pm.modelEditor('{}'.format(self.__modelEditor), e=True, displayTextures=not curTextureState)

        isDisplayTexture = pm.modelEditor('{}'.format(self.__modelEditor), q=True, displayTextures=True)
        if isDisplayTexture:
            pm.symbolButton(self.__textureBtn, e=True, bgc=(0.322, 0.522, 0.651))
        else:
            pm.symbolButton(self.__textureBtn, e=True, bgc=(0.267, 0.267, 0.267))

    def __fitAllObjects(self, *args):
        pm.modelEditor(self.__modelEditor, e=True, activeView=True)
        pm.viewFit(all=True)

    def __getFilePath(self, *args):
        filePath = pm.fileDialog2(fileMode=0, caption='Save as', fileFilter='*.png;;*.jpg')
        if filePath:
            pm.textField(self.__filePathFld, e=True, text=filePath[0])

    def __captureViewport(self, *args):
        img = om.MImage()
        view = omui.M3dView.getM3dViewFromModelEditor(self.__modelEditor.name())
        view.readColorBuffer(img, True)
        iconSize = pm.intFieldGrp(self.__sizeIntFldGrp, q=True, v1=True)
        img.resize(iconSize, iconSize, False)
        iconPath = pm.textField(self.__filePathFld, q=True, text=True)
        ext = os.path.splitext(iconPath)[-1].strip('.')
        img.writeToFile(iconPath, ext)
