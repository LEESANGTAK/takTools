import pymel.core as pm
from .. import utils


class KDTree(object):
    def __init__(self):
        self._data = []
        self._tree = None
        self._pointDimension = 3

    def buildData(self, transforms):
        for item in transforms:
            item = pm.PyNode(item)
            name = item.nodeName()
            position = pm.xform(item, q=True, t=True, ws=True)
            self._data.append(
                {
                    'name': name,
                    'position': position
                }
            )

    def buildTree(self):
        self._tree = self._build(self._data)

    def searchNearestData(self, searchPoint, tolerance=0.1):
        bestData, minDist = self._getNearestNeighbor(searchPoint, self._tree)
        if minDist > tolerance:
            return False
        return bestData

    def _build(self, data, depth=0):
        if len(data) <= 0:
            return None

        axis = depth % self._pointDimension

        dataSorted = sorted(data, key=lambda item: item['position'][axis])
        median = len(data) / 2

        return {
            'data': dataSorted[median],
            'left': self._build(dataSorted[:median], depth + 1),
            'right': self._build(dataSorted[median + 1:], depth + 1)
        }

    def _getNearestNeighbor(self, point, node, depth=0, bestData=None, minDist=100000):
        if node is None:
            return bestData, minDist

        currentDistance = utils.distance(point, node['data']['position'])
        if currentDistance < minDist:
            minDist = currentDistance
            bestData = node['data']

        axis = depth % self._pointDimension

        if point[axis] < node['data']['position'][axis]:
            nextNode = node['left']
            oppositeNode = node['right']
        else:
            nextNode = node['right']
            oppositeNode = node['left']

        bestData, minDist = self._getNearestNeighbor(point, nextNode, depth+1, bestData, minDist)
        if abs(point[axis] - node['data']['position'][axis]) < utils.distance(point, bestData['position']):
            bestData, minDist = self._getNearestNeighbor(point, oppositeNode, depth+1, bestData, minDist)

        return bestData, minDist
