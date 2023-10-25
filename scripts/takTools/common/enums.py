import pymel.core as pm


class Color(object):
    yellow = 17
    red = 13
    blue = 6
    green = 14
    skyBlue = 18
    white = 16


class Space(object):
    object = 'object'
    world = 'world'


class ControlShape(object):
    circleX = 'circleX'
    circleY = 'circleY'
    circleZ = 'circleZ'
    sphere = 'sphere'
    cube = 'cube'
    cloth = 'cloth'
    gear = 'gear'
    main = 'main'
    square = 'square'
    squareRounded = 'squareRounded'


class Vector(object):
    X = pm.datatypes.Vector(1, 0, 0)
    Y = pm.datatypes.Vector(0, 1, 0)
    Z = pm.datatypes.Vector(0, 0, 1)
