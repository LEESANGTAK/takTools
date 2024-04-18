from PySide2.QtWidgets import *


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
