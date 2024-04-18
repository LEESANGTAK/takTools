import functools
from PySide2 import QtWidgets

from shiboken2 import wrapInstance
from shiboken2 import getCppPointer

import maya.OpenMayaUI as omui
from maya import cmds


def mayaUI(WidgetClass):
    """Set widget's parent to the maya main window."""
    origInit = WidgetClass.__init__
    def __init__(self):  # Wrapper method
        functools.update_wrapper(__init__, WidgetClass.__init__)  # Make wrapper method to like wrapped method

        mayaWinWidget = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)

        origInit(self, mayaWinWidget)  # Call warpped method
    WidgetClass.__init__ = __init__  # Replace wrapped method to wrapper method
    return WidgetClass


def dockable(wscName):
    """
    Convert QtWidget to dockable maya ui.
    A widget should have "_instance" and "_title" class variables.
    "_instance" variable is stands for storing a widget instance. "_title" variable is stands for setting the window title.

    :param wscName: Workspace control name
    :type wscName: str
    """
    def decorator(WidgetClass):
        # Override show method
        origShow = WidgetClass.show
        def show(self):  # Wrapper method
            functools.update_wrapper(show, WidgetClass.show)  # Make wrapper method to like wrapped method

            if not cmds.workspaceControl(wscName, q=True, exists=True):
                cmds.workspaceControl(wscName)
            omui.MQtUtil.addWidgetToMayaLayout(int(getCppPointer(WidgetClass._instance)[0]), int(omui.MQtUtil.findControl(wscName)))
            cmds.workspaceControl(wscName, e=True, label=WidgetClass._title)
            cmds.workspaceControl(wscName, e=True, vis=True, restore=True)

            origShow(self)  # Call warpped method
        WidgetClass.show = show  # Replace wrapped method to wrapper method

        # Override close method
        origClose = WidgetClass.close
        def close(self):
            functools.update_wrapper(close, WidgetClass.close)  # Make wrapper method to like wrapped method
            cmds.workspaceControl(wscName, e=True, vis=False)
            origClose(self)
        WidgetClass.close = close

        return WidgetClass
    return decorator
