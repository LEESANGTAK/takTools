import os
import pymel.core as pm
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import maya.cmds as cmds


def enableChildNodes(rootNode, nodeType='constraint', enable=False):
    nodeStateTable = {0: 2, 1: 0}
    cnsts = pm.listRelatives(rootNode, ad=True, type=nodeType)
    for cnst in cnsts:
        cnst.nodeState.set(nodeStateTable[enable])


def getDagPath(nodeName, apiVersion=2):
    if apiVersion == 2:
        mSelLs = om2.MSelectionList()
        mSelLs.add(nodeName)
        dagPath = mSelLs.getDagPath(0)
    elif apiVersion == 1:
        mSelLs = om.MSelectionList()
        mSelLs.add(nodeName)
        dagPath = om.MDagPath()
        mSelLs.getDagPath(0, dagPath)
    return dagPath


def getTopDagNode(dagNodes):
    topDagNode = None

    minDepth = 10000
    for dagNode in dagNodes:
        fullName = dagNode.fullPathName()
        curDepth = fullName.count('|')
        if curDepth < minDepth:
            minDepth = curDepth
            topDagNode = dagNode

    return topDagNode

def getShapeFromComponent(component):
    shapeName = component.split('.')[0]
    return pm.PyNode(shapeName)


def findMultiAttributeEmptyIndex(node, attribute):
    """
    Find available index of multi attribute.
    Args:
        node (string): Node name.
        attribute (string): Attribute name

    Returns:
        Available index
    """
    node = pm.PyNode(node)
    id = 0
    while node.attr(attribute)[id].isConnected():
        id += 1
    return id


def getLogicalIndices(node, attribute):
    """
    Get logical indices by given node and attribute name.

    Arguments:
        node {str} -- Node name
        attribute {str} -- Attribute name

    Returns:
        list -- Logical index list
    """
    logicalIndices = None

    sels = om.MSelectionList()
    sels.add(node)

    mObj = om.MObject()
    sels.getDependNode(0, mObj)

    dgFn = om.MFnDependencyNode(mObj)

    targetPlug = dgFn.findPlug(attribute)

    logicalIndices = om.MIntArray()
    targetPlug.getExistingArrayAttributeIndices(logicalIndices)

    logicalIndices = [index for index in logicalIndices]  # Convert MIntArray to list

    return logicalIndices


def getManipPosition():
    ctxTable = {
        'selectSuperContext': ['Move', cmds.manipMoveContext],
        'moveSuperContext': ['Move', cmds.manipMoveContext],
        'RotateSuperContext': ['Rotate', cmds.manipRotateContext],
        'scaleSuperContext':['Scale', cmds.manipScaleContext]
    }
    curCtx = cmds.currentCtx()
    ctxInfo = ctxTable[curCtx]
    cmds.setToolTo(ctxInfo[0])
    pos = ctxInfo[1](ctxInfo[0], q=True, p=True)
    cmds.setToolTo(curCtx)
    return pos


def cleanupMayaScene():
    removeModelPanelCallbacks()
    removeUnknowns()
    removeVaccine()
    unlockNodes()


def removeModelPanelCallbacks():
    for item in pm.lsUI(editors=True):
        if isinstance(item, pm.ui.ModelEditor):
            pm.modelEditor(item, edit=True, editorChanged="")


def removeUnknowns():
    # Remove unknown nodes
    unknownNodes = pm.ls(type="unknown")
    for node in unknownNodes:
        pm.lockNode(node, lock=False)
        pm.delete(node)

    # Remove unknown plugins
    unknownPlugins = pm.unknownPlugin(q=True, l=True)
    if unknownPlugins:
        for plugin in unknownPlugins:
            pm.unknownPlugin(plugin, r=True)


def removeVaccine():
    # Remove script jobs
    jobs = cmds.scriptJob(lj=True)
    for job in jobs:
        if "antivirus" in job or 'vaccine' in job:
            id = job.split(":")[0]
            if id.isdigit():
                cmds.scriptJob(k=int(id), f=True)

    # Remove script nodes
    for sNode in ['breed_gene', 'vaccine_gene']:
        try:
            pm.delete(sNode)
        except:
            pass

    # Remove python files
    userDocsDir = os.path.expanduser('~')
    scriptsDir = os.path.join(userDocsDir, 'maya', 'scripts')
    for item in os.listdir(scriptsDir):
        if item in ['userSetup.py', 'vaccine.py', 'vaccine.pyc']:
            os.remove(os.path.join(scriptsDir, item))


def unlockNodes():
    pm.lockNode('initialShadingGroup', lock=False, lockUnpublished=False)
    for node in pm.ls():
        if pm.lockNode(node, q=True):
            pm.lockNode(node, lock=False)


def setWireColorBySide(obj):
    RIGHT_COLOR = 13
    LEFT_COLOR = 6
    CENTER_COLOR = 17

    posX = round(pm.xform(obj, q=True, ws=True, t=True)[0], 6)
    print(posX)
    if posX < 0.0:
        color = RIGHT_COLOR
    elif posX > 0.0:
        color = LEFT_COLOR
    else:
        color = CENTER_COLOR

    shps = pm.listRelatives(obj, s=True)
    if shps:
        for shp in shps:
            pm.setAttr('%s|%s.overrideEnabled' % (obj, shp), 1)
            pm.setAttr('%s|%s.overrideColor' % (obj, shp), color)
    else:
        pm.setAttr('%s.overrideEnabled' % (obj), 1)
        pm.setAttr('%s.overrideColor' % (obj), color)


def cloneAttribute(sourceObj, targetObj, attribute, prefix='', suffix='', unreal=True, connect=True):
    """Copy source object attribute to target object.

    example:
from utils import globalUtil as gUtil

sels = pm.selected()

sourceObj = sels[0]
targetObj = sels[1]

for attr in pm.listAttr(sourceObj, ud=True):
    gUtil.cloneAttribute(sourceObj, targetObj, attr)
    """

    srcAttr = pm.PyNode('{0}.{1}'.format(sourceObj, attribute))
    if unreal:
        attrType = 'double'
    else:
        attrType = srcAttr.type()
    targetObj = pm.PyNode(targetObj)
    trgAttrName = prefix + attribute + suffix

    if attrType == 'enum':
        enumInfo = sorted(srcAttr.getEnums().items(), key=lambda item: item[1])
        enumNames = [item[0] for item in enumInfo]
        pm.addAttr(targetObj, longName=trgAttrName, at='enum', en=enumNames, keyable=srcAttr.isKeyable())
    else:
        try:
            pm.addAttr(targetObj, longName=trgAttrName, at=attrType, min=srcAttr.getMin(), max=srcAttr.getMax(), keyable=srcAttr.isKeyable())
        except:
            pm.addAttr(targetObj, longName=trgAttrName, at=attrType, keyable=srcAttr.isKeyable())

    if connect:
        srcAttr >> targetObj.attr(trgAttrName)


def createSet(suffix='_vtxs_set'):
    sels = pm.selected(fl=True)
    if sels:
        result = pm.promptDialog(
            title='Create Set',
            message='Enter Name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if result == 'OK':
            text = pm.promptDialog(query=True, text=True)
            objSet = pm.sets(n=text+suffix)


def getDeformerWeights(deformerName, mesh, valueRange=[0.0, 1.0]):
    """
    deformerName = "textureDeformer1"
    mesh = cmds.ls(sl=True)[0]
    texDefValInfo = getDeformerWeights(deformerName, mesh, valueRange=[0.0, 0.0])
    zeroWeightVtxIndexes = texDefValInfo.keys()
    """
    weightsInfo = {}

    numVtx = cmds.polyEvaluate(mesh, v=True)
    for vtxID in range(numVtx):
        w = cmds.percent(deformerName, "{0}.vtx[{1}]".format(mesh, vtxID), q=True, v=True)[0]
        if valueRange[0] <= w <= valueRange[1]:
            weightsInfo[vtxID] = w

    return weightsInfo
