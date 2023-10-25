import logging
from maya.api import OpenMaya as om
import pymel.core as pm

import sys
MAYA_VERSION = int(pm.about(version=True))
MASH_API_PATH = 'C:/Program Files/Autodesk/Maya{}/plug-ins/MASH/scripts/MASH'.format(MAYA_VERSION)
sys.path.append(MASH_API_PATH)

import api as mapi
import openMASH as omash

from . import globalUtil
from . import mesh as meshUtil
from . import matrix as matrixUtil
from . import material as matUtil


logger = logging.getLogger(__name__)


def buildJoints(waiter):
    allNodes = mapi.getAllNodesInNetwork(waiter)

    # Check a MASH_Python node
    pythonNode = findMashNode(allNodes, "MASH_Python")
    if not pythonNode:
        logger.error('Needs a MASH_Python node.')
        pm.select(waiter, r=True, ne=True)
        return

    # Create MASH_Breakout node if not exists
    breakoutNode = findMashNode(allNodes, "MASH_Breakout")
    if not breakoutNode:
        breakoutNode = pm.mel.MASHaddNode("MASH_Breakout", waiter)

    # Create joints
    md = omash.MASHData(pythonNode)
    joints = []
    for i in range(md.count()):
        jnt = pm.createNode('joint', n='{}_Joint_{}'.format(waiter, i))
        jnt.inheritsTransform.set(False)
        joints.append(jnt)
    rootJnt = pm.createNode('joint', n='{}_joint_root'.format(waiter))
    pm.parent(joints, rootJnt)

    # Connect joints
    breakoutNode = pm.PyNode(breakoutNode)
    for i, jnt in enumerate(joints):
        breakoutNode.attr('outputs[{}]'.format(i)).translate >> jnt.translate
        breakoutNode.attr('outputs[{}]'.format(i)).rotate >> jnt.rotate
        breakoutNode.attr('outputs[{}]'.format(i)).scale >> jnt.scale

    return joints


def buildSkinMesh(waiter, joints):
    allNodes = mapi.getAllNodesInNetwork(waiter)

    pythonNode = findMashNode(allNodes, 'MASH_Python')
    reproNode = findMashNode(allNodes, 'MASH_Repro')

    if not isBeforeWaiter(pythonNode):
        # If MASH_ID node placed in after MASH_Python node, object id can't retrived.
        logger.error('{pythonNode} node must be placed before MASH_Waiter node. That is {pythonNode} node must be placed on the top of the stack in the MASH Editor.'.format(pythonNode=pythonNode))
        return

    md = omash.MASHData(pythonNode)
    reproMesh = pm.listHistory(reproNode, future=True, type='mesh')[0]
    skinMesh = createSkinMesh(md, reproNode, joints)
    pm.transferAttributes(reproMesh, skinMesh, transferUVs=2)
    pm.delete(skinMesh, ch=True)
    skinClst = pm.skinCluster(joints, skinMesh, tsb=True, bm=0, wd=0, omi=False, mi=1, dr=4.0)
    matUtil.copyMaterial(reproMesh, skinMesh)
    reproMesh.getTransform().hide()

    # Refine skin weights
    mashPointsNumVertices = getMashPointsNumvertices(md, reproNode)
    mashIndexVerticesId = getMashIndexVerticesId(md.count(), mashPointsNumVertices)
    for i, verticesId in enumerate(mashIndexVerticesId):
        pm.skinPercent(skinClst, '{}.vtx[{}:{}]'.format(skinMesh, verticesId[0], verticesId[-1]), transformValue=[(joints[i], 1.0)])

    return skinMesh


def isBeforeWaiter(mashNode):
    mashNode = pm.PyNode(mashNode)
    return bool(mashNode.outputs(type='MASH_Waiter'))


def createSkinMesh(mashData, reproNode, joints):
    skinMesh = None
    dupMeshes = []
    for i in range(mashData.count()):
        sourceMesh = getSourceMesh(int(round(mashData.id[i])), reproNode)
        dupSourceMesh = pm.duplicate(sourceMesh, renameChildren=True)[0]
        pm.makeIdentity(dupSourceMesh, apply=True)
        dupMeshes.append(dupSourceMesh)
        pm.matchTransform(dupSourceMesh, joints[i])
    skinMesh = pm.polyUnite(dupMeshes, ch=False)[0]
    return skinMesh


def getMashPointsNumvertices(mashData, reproNode):
    mashPointsNumVertices = []
    for i in range(mashData.count()):
        sourceMesh = getSourceMesh(int(round(mashData.id[i])), reproNode)
        fnMesh = om.MFnMesh(globalUtil.getDagPath(sourceMesh.name()))
        mashPointsNumVertices.append(fnMesh.numVertices)
    return mashPointsNumVertices


def getSourceMesh(index, reproNode):
    reproNode = pm.PyNode(reproNode)
    return reproNode.instancedGroup[index].instancedMesh.inputs(type='mesh')[0]


def getMashIndexVerticesId(numMashPoints, mashPointsNumVertices):
    mashIndexVerticesIdList = []
    sumNumVertices = 0
    for i in range(numMashPoints):
        numVertices = mashPointsNumVertices[i]
        mashIndexVerticesIdList.append(range(sumNumVertices, sumNumVertices+numVertices))
        sumNumVertices += numVertices
    return mashIndexVerticesIdList


def findMashNode(mashNodes, searchType):
    resultNode = None
    for mashNode in mashNodes:
        if pm.nodeType(mashNode) == searchType:
            resultNode = mashNode
    return resultNode

