import pymel.core as pm

crv = None
FUNC_TABLE = {'sin': pm.mel.sin, 'noise': pm.mel.noise}

def drawFunctionCurve(func, frequency, amplitude, offset):
    global FUNC_TABLE
    input = 0
    points = []

    while input < 30:
        output = FUNC_TABLE[func](input * frequency - offset) * amplitude
        points.append((input, output, 0))
        input += 1

    return pm.curve(ep=points, d=3, n='{}_crv'.format(func))


def showUI():
    pm.window(title='Drawing Function Curve', mnb=False, mxb=False, cc=closeCallback)
    pm.columnLayout(adj=True)
    pm.optionMenu('funcWidget', label='Function:', changeCommand=drawCallback)
    pm.menuItem(label='sin')
    pm.menuItem(label='noise')
    pm.floatSliderGrp('freqWidget', label='Frequency:', field=True, min=0, max=5, v=1, dc=drawCallback)
    pm.floatSliderGrp('offWidget', label='Offset:', field=True, min=-10, v=0, max=10, dc=drawCallback)
    pm.floatSliderGrp('ampWidget', label='Amplitude:', field=True, min=0, max=5, v=1, dc=drawCallback)
    pm.textFieldGrp('funcWidget', label='Function:')
    pm.showWindow()


def drawCallback(*args):
    global crv
    if crv:
        pm.delete(crv)

    func = pm.optionMenu('funcWidget', q=True, v=True)
    freq = pm.floatSliderGrp('freqWidget', q=True, v=True)
    off = pm.floatSliderGrp('offWidget', q=True, v=True)
    amp = pm.floatSliderGrp('ampWidget', q=True, v=True)

    funcText = 'y = {func}(x * {freq} - {off}) * {amp}'.format(
        func=func,
        freq=freq,
        off=off,
        amp=amp
    )
    pm.textFieldGrp('funcWidget', e=True, text=funcText)

    crv = drawFunctionCurve(func, freq, amp, off)


def closeCallback(*args):
    global crv
    if crv:
        pm.delete(crv)
