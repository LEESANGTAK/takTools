import math


def clamp(value, minValue, maxValue):
    return max(min(value, maxValue), minValue)


def normalize(value, minValue, maxValue):
    value = value * 1.0
    return (value - minValue) / (maxValue - minValue)


def lerp(weight, minValue, maxValue):
    weight = clamp(weight, 0.0, 1.0) * 1.0
    return minValue + (maxValue - minValue) * weight


def remap(value, oldMin, oldMax, newMin, newMax):
    value = clamp(value, oldMin, oldMax) * 1.0
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
    vecA = aEndPoint - aStartPoint
    vecB = bEndPoint - bStartPoint

    areaAB = vecA.cross(vecB).length()
    vecAB = bStartPoint - aStartPoint
    areaABB = vecAB.cross(vecB).length()

    ratio = areaABB / areaAB

    intersectPoint = aStartPoint + (vecA * ratio)

    return intersectPoint
