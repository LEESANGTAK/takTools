from maya import cmds


def shakeCamera(camera, amplitude=1.0, speed=0.1):
    spaceLoc = cmds.spaceLocator(n='camSpace_loc')[0]
    shakeLoc = cmds.spaceLocator(n='camShake_loc')[0]
    cmds.parent(shakeLoc, spaceLoc)

    decMatrix = cmds.createNode('decomposeMatrix')
    cmds.connectAttr('{}.worldMatrix'.format(shakeLoc), '{}.inputMatrix'.format(decMatrix), force=True)
    cmds.connectAttr('{}.outputTranslate'.format(decMatrix), '{}.translate'.format(camera), force=True)
    cmds.connectAttr('{}.outputRotate'.format(decMatrix), '{}.rotate'.format(camera), force=True)

    cmds.addAttr(spaceLoc, ln='amplitude', keyable=True, dv=amplitude, min=0.0)
    cmds.addAttr(spaceLoc, ln='speed', keyable=True, dv=speed, min=0.0)
    cmds.addAttr(spaceLoc, ln='offset', keyable=True, dv=0)
    cmds.addAttr(spaceLoc, ln='translateXOnOff', keyable=True, dv=1.0, min=0.0, max=1.0)
    cmds.addAttr(spaceLoc, ln='translateYOnOff', keyable=True, dv=1.0, min=0.0, max=1.0)
    cmds.addAttr(spaceLoc, ln='rotateXOnOff', keyable=True, dv=1.0, min=0.0, max=1.0)
    cmds.addAttr(spaceLoc, ln='rotateYOnOff', keyable=True, dv=1.0, min=0.0, max=1.0)

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

    cmds.expression(s=exprStr, ae=True, uc='all', n='shakeCam_expr')

    cmds.select(spaceLoc, r=True)
