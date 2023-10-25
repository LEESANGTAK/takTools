import pymel.core as pm


class Color():
    YELLOW = 17
    RED = 13
    LIGHT_RED = 20
    BLUE = 6
    GREEN = 14
    SKY_BLUE = 18
    DARK_BLUE = 15
    WHITE = 16


class Space():
    LOCAL = 'local'
    WORLD = 'world'


class ControlShape():
    CIRCLE_X = 'circleX'
    CIRCLE_Y = 'circleY'
    CIRCLE_Z = 'circleZ'
    SPHERE = 'sphere'
    CUBE = 'cube'
    CLOTH = 'cloth'
    GEAR = 'gear'
    MAIN = 'main'
    SQUARE = 'square'
    SQUARE_ROUNDED = 'squareRounded'


class Vector():
    X = pm.datatypes.Vector(1, 0, 0)
    Y = pm.datatypes.Vector(0, 1, 0)
    Z = pm.datatypes.Vector(0, 0, 1)
