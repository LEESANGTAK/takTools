from ctypes import *


user32 = windll.user32
EnumWindowsProc = WINFUNCTYPE(c_int, c_int, c_int)


class System(object):
    def __init__(self):
        super(System, self).__init__()
        self._screenWidth = None
        self._screenHeight = None

        self._getScreenSize()

    @property
    def screenWidth(self):
        return self._screenWidth

    @property
    def screenHeight(self):
        return self._screenHeight

    def _getScreenSize(self):
        user32 = windll.user32
        self._screenWidth = user32.GetSystemMetrics(0)
        self._screenHeight = user32.GetSystemMetrics(1)


def clearOutputWindow():
    print("Clearing Maya output window")
    out = get_handle("Output Window")
    if not out:
        print("Output window wasn't found")
    else:
        ch = get_handle("", out[0])
        if ( ch[0] ):
            user32.SendMessageA(ch[0], 0x00B1, 0, -1)
            user32.SendMessageA(ch[0], 0x00C2, 1, "")
        else:
            print("Child window wasn't found")


def get_handle(title, parent = None):
    """ Returns handles to windows with matching titles """
    rHwnd = []
    def EnumCB(hwnd, lparam, match = title.lower(), rHwnd = rHwnd):
        # child
        if lparam == 1:
            rHwnd.append(hwnd)
            return False

        title = c_buffer(' ' * 256)
        user32.GetWindowTextA(hwnd, title, 255)
        if title.value.lower() == match:
            rHwnd.append(hwnd)
            return False
        return True

    if parent is not None:
        user32.EnumChildWindows(parent, EnumWindowsProc(EnumCB), 1)
    else:
        user32.EnumWindows(EnumWindowsProc(EnumCB), 0)
    return rHwnd
