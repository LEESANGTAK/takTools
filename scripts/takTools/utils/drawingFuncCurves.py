import math
from maya import cmds, mel

crv = None
FUNC_TABLE = {
    'sin': lambda x: math.sin(x),
    'noise': lambda x: mel.eval('noise({})'.format(x))
}

def drawFunctionCurve(func, frequency, amplitude, offset):
    global FUNC_TABLE
    input = 0
    points = []

    while input < 30:
        output = FUNC_TABLE[func](input * frequency - offset) * amplitude
        points.append((input, output, 0))
        input += 1

    return cmds.curve(ep=points, d=3, n='{}_crv'.format(func))


def showUI():
    cmds.window(title='Drawing Function Curve', mnb=False, mxb=False, cc=closeCallback)
    cmds.columnLayout(adj=True)
    cmds.optionMenu('funcWidget', label='Function:', changeCommand=drawCallback)
    cmds.menuItem(label='sin')
    cmds.menuItem(label='noise')
    cmds.floatSliderGrp('freqWidget', label='Frequency:', field=True, min=0, max=5, v=1, dc=drawCallback)
    cmds.floatSliderGrp('offWidget', label='Offset:', field=True, min=-10, v=0, max=10, dc=drawCallback)
    cmds.floatSliderGrp('ampWidget', label='Amplitude:', field=True, min=0, max=5, v=1, dc=drawCallback)
    cmds.textFieldGrp('funcWidget', label='Function:')
    cmds.showWindow()


def drawCallback(*args):
    global crv
    if crv:
        cmds.delete(crv)

    func = cmds.optionMenu('funcWidget', q=True, v=True)
    freq = cmds.floatSliderGrp('freqWidget', q=True, v=True)
    off = cmds.floatSliderGrp('offWidget', q=True, v=True)
    amp = cmds.floatSliderGrp('ampWidget', q=True, v=True)

    funcText = 'y = {func}(x * {freq} - {off}) * {amp}'.format(
        func=func,
        freq=freq,
        off=off,
        amp=amp
    )
    cmds.textFieldGrp('funcWidget', e=True, text=funcText)

    crv = drawFunctionCurve(func, freq, amp, off)


def closeCallback(*args):
    global crv
    if crv:
        cmds.delete(crv)
