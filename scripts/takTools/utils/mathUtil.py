import math
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


def remapVal(value, oldMin, oldMax, newMin, newMax):
    return newMin + ((value - oldMin)*(newMax - newMin)) / (oldMax - oldMin)


def distance(pointA, pointB):
    squareSum = 0
    for point1Component, point2Component in zip(pointA, pointB):
        difference = point2Component - point1Component
        squareSum += math.pow(difference, 2)
    return math.sqrt(squareSum)


def lineIntersection(aStartPoint, aEndPoint, bStartPoint, bEndPoint):
    """
Example:
asLoc = pm.spaceLocator(n='aStart_loc', position=(0, -3, 0))
aeLoc = pm.spaceLocator(n='aEnd_loc', position=(0, 3, 0))
bsLoc = pm.spaceLocator(n='bStart_loc', position=(-3, 0, 0))
beLoc = pm.spaceLocator(n='bEnd_loc', position=(3, 0, 0))

aStartPoint = asLoc.worldPosition.get()
aEndPoint = aeLoc.worldPosition.get()
bStartPoint = bsLoc.worldPosition.get()
bEndPoint = beLoc.worldPosition.get()

intersectPoint = lineIntersection(aStartPoint, aEndPoint, bStartPoint, bEndPoint)
intersectLoc = pm.spaceLocator(n='intersect_loc')
intersectLoc.t.set(intersectPoint)
    """
    vecA = aEndPoint - aStartPoint
    vecB = bEndPoint - bStartPoint

    areaAB = vecA.cross(vecB).length()
    vecAB = bStartPoint - aStartPoint
    areaABB = vecAB.cross(vecB).length()

    ratio = areaABB / areaAB

    intersectPoint = aStartPoint + (vecA * ratio)

    return intersectPoint
