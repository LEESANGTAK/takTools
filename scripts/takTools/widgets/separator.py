from maya import cmds

MAYA_VERSION = int(cmds.about(version=True))
if MAYA_VERSION <= 2016:
    from PySide.QtWidgets import *
elif 2017 <= MAYA_VERSION <= 2024:
    from PySide2.QtWidgets import *
elif 2025 <= MAYA_VERSION:
    from PySide6.QtWidgets import *


class Separator(QFrame):
    styleInfo = {'in': QFrame.Sunken}

    def __init__(self, style='in'):
        super(Separator, self).__init__()

        self.setFrameShape(QFrame.HLine)
        self.style = style

    @property
    def style(self):
        return self.frameShape()

    @style.setter
    def style(self, style):
        self.setFrameShadow(Separator.styleInfo[style])
