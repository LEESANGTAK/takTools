import pymel.core as pm


def shakeCamera(camera, amplitude=1.0, speed=0.1):
    spaceLoc = pm.spaceLocator(n='camSpace_loc')
    shakeLoc = pm.spaceLocator(n='camShake_loc')
    spaceLoc | shakeLoc

    decMatrix = pm.createNode('decomposeMatrix')
    shakeLoc.worldMatrix >> decMatrix.inputMatrix
    decMatrix.outputTranslate >> camera.translate
    decMatrix.outputRotate >> camera.rotate

    pm.addAttr(spaceLoc, ln='amplitude', keyable=True, dv=amplitude, min=0.0)
    pm.addAttr(spaceLoc, ln='speed', keyable=True, dv=speed, min=0.0)
    pm.addAttr(spaceLoc, ln='offset', keyable=True, dv=0)
    pm.addAttr(spaceLoc, ln='translateXOnOff', keyable=True, dv=1.0, min=0.0, max=1.0)
    pm.addAttr(spaceLoc, ln='translateYOnOff', keyable=True, dv=1.0, min=0.0, max=1.0)
    pm.addAttr(spaceLoc, ln='rotateXOnOff', keyable=True, dv=1.0, min=0.0, max=1.0)
    pm.addAttr(spaceLoc, ln='rotateYOnOff', keyable=True, dv=1.0, min=0.0, max=1.0)

    exprStr = '''
float $amp = {0}.amplitude;
float $speed = {0}.speed;
float $offset = {0}.offset;
float $transXOnOff = {0}.translateXOnOff;
float $transYOnOff = {0}.translateYOnOff;
float $rotateXOnOff = {0}.rotateXOnOff;
float $rotateYOnOff = {0}.rotateYOnOff;
float $horizontalMove = noise((frame + $offset + 50) * $speed)*0.01 * $amp;
float $verticalMove = noise((frame + $offset) * $speed)*0.01 * $amp;

{1}.translateX = $horizontalMove * $transXOnOff;
{1}.rotateY = rad_to_deg($horizontalMove) * $rotateYOnOff;
{1}.translateY = $verticalMove * $transYOnOff;
{1}.rotateX = rad_to_deg($verticalMove) * $rotateXOnOff;
    '''.format(spaceLoc, shakeLoc)

    pm.expression(s=exprStr, ae=True, uc='all', n='shakeCam_expr')

    pm.select(spaceLoc, r=True)
