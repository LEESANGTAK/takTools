import pymel.core as pm


def normalize(value, minValue, maxValue):
    value = value * 1.0
    return (value - minValue) / (maxValue - minValue)


def lerp(weight, minValue, maxValue):
    weight = pm.util.clamp(weight, 0.0, 1.0) * 1.0
    return minValue + (maxValue - minValue) * weight


def remap(value, oldMin, oldMax, newMin, newMax):
    value = pm.util.clamp(value, oldMin, oldMax) * 1.0
    return lerp(normalize(value, oldMin, oldMax), newMin, newMax)
