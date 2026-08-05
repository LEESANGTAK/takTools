import os
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import maya.cmds as cmds


def enableChildNodes(rootNode, nodeType='constraint', enable=False):
    nodeStateTable = {0: 2, 1: 0}
    cnsts = cmds.listRelatives(rootNode, ad=True, type=nodeType, fullPath=True) or []
    for cnst in cnsts:
        cmds.setAttr('{0}.nodeState'.format(cnst), nodeStateTable[enable])


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
        fullName = cmds.ls(str(dagNode), long=True)[0]
        curDepth = fullName.count('|')
        if curDepth < minDepth:
            minDepth = curDepth
            topDagNode = dagNode

    return topDagNode

def getShapeFromComponent(component):
    return str(component).split('.')[0]


def findMultiAttributeEmptyIndex(node, attribute):
    """
    Find available index of multi attribute.
    Args:
        node (string): Node name.
        attribute (string): Attribute name

    Returns:
        Available index
    """
    index = 0
    while True:
        attrName = '{0}.{1}[{2}]'.format(node, attribute, index)
        connections = cmds.listConnections(attrName, source=True, destination=False, plugs=True)
        if connections:
            index += 1
            continue
        return index


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
    for item in cmds.lsUI(editors=True) or []:
        try:
            cmds.modelEditor(item, edit=True, editorChanged="")
        except RuntimeError:
            pass


def removeUnknowns():
    # Remove unknown nodes
    unknownNodes = cmds.ls(type="unknown") or []
    for node in unknownNodes:
        cmds.lockNode(node, lock=False)
        cmds.delete(node)

    # Remove unknown plugins
    unknownPlugins = cmds.unknownPlugin(q=True, l=True) or []
    for plugin in unknownPlugins:
        cmds.unknownPlugin(plugin, r=True)


def removeVaccine():
    # Remove script jobs
    jobs = cmds.scriptJob(lj=True) or []
    for job in jobs:
        if "antivirus" in job or 'vaccine' in job:
            jobId = job.split(":")[0]
            if jobId.isdigit():
                cmds.scriptJob(k=int(jobId), f=True)

    # Remove script nodes
    for sNode in ['breed_gene', 'vaccine_gene']:
        try:
            cmds.delete(sNode)
        except RuntimeError:
            pass

    # Remove python files
    userDocsDir = os.path.expanduser('~')
    scriptsDir = os.path.join(userDocsDir, 'maya', 'scripts')
    for item in os.listdir(scriptsDir):
        if item in ['userSetup.py', 'vaccine.py', 'vaccine.pyc']:
            os.remove(os.path.join(scriptsDir, item))


def unlockNodes():
    cmds.lockNode('initialShadingGroup', lock=False, lockUnpublished=False)
    for node in cmds.ls() or []:
        if cmds.lockNode(node, q=True):
            cmds.lockNode(node, lock=False)


def setWireColorBySide(obj):
    RIGHT_COLOR = 13
    LEFT_COLOR = 6
    CENTER_COLOR = 17

    posX = round(cmds.xform(obj, q=True, ws=True, t=True)[0], 6)
    print(posX)
    if posX < 0.0:
        color = RIGHT_COLOR
    elif posX > 0.0:
        color = LEFT_COLOR
    else:
        color = CENTER_COLOR

    shps = cmds.listRelatives(obj, s=True, fullPath=True) or []
    if shps:
        for shp in shps:
            cmds.setAttr('{0}.overrideEnabled'.format(shp), 1)
            cmds.setAttr('{0}.overrideColor'.format(shp), color)
    else:
        cmds.setAttr('{0}.overrideEnabled'.format(obj), 1)
        cmds.setAttr('{0}.overrideColor'.format(obj), color)


def cloneAttribute(sourceObj, targetObj, attribute, prefix='', suffix='', unreal=True, connect=True):
    """Copy source object attribute to target object.

    example:
from utils import globalUtil as gUtil

sels = cmds.ls(sl=True)

sourceObj = sels[0]
targetObj = sels[1]

for attr in cmds.listAttr(sourceObj, ud=True):
    gUtil.cloneAttribute(sourceObj, targetObj, attr)
    """

    sourceObj = str(sourceObj)
    targetObj = str(targetObj)
    srcAttrName = '{0}.{1}'.format(sourceObj, attribute)
    trgAttrName = prefix + attribute + suffix

    if unreal:
        attrType = 'double'
    else:
        try:
            attrType = cmds.getAttr(srcAttrName, type=True)
        except RuntimeError:
            attrType = 'double'

    keyable = False
    try:
        keyable = cmds.getAttr(srcAttrName, keyable=True)
    except RuntimeError:
        pass

    if attrType == 'enum':
        enumInfo = cmds.attributeQuery(attribute, node=sourceObj, listEnum=True) or []
        enumNames = []
        if enumInfo:
            enumNames = enumInfo[0].split(':') if isinstance(enumInfo[0], str) else enumInfo
        cmds.addAttr(targetObj, longName=trgAttrName, attributeType='enum', enumName=':'.join(enumNames), keyable=keyable)
    else:
        try:
            minVal = cmds.attributeQuery(attribute, node=sourceObj, minimum=True)[0]
            maxVal = cmds.attributeQuery(attribute, node=sourceObj, maximum=True)[0]
            cmds.addAttr(targetObj, longName=trgAttrName, attributeType=attrType, min=minVal, max=maxVal, keyable=keyable)
        except Exception:
            try:
                cmds.addAttr(targetObj, longName=trgAttrName, attributeType=attrType, keyable=keyable)
            except Exception:
                cmds.addAttr(targetObj, longName=trgAttrName, keyable=keyable)

    if connect:
        cmds.connectAttr(srcAttrName, '{0}.{1}'.format(targetObj, trgAttrName), force=True)


def createSet(suffix='_vtxs_set'):
    sels = cmds.ls(sl=True, fl=True)
    if sels:
        result = cmds.promptDialog(
            title='Create Set',
            message='Enter Name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if result == 'OK':
            text = cmds.promptDialog(query=True, text=True)
            cmds.sets(n=text+suffix)


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


def duplicateRenameSelectionGUI():
    cmds.window('dupRenameSelWin', title="Duplicate and Rename Selection", w=300, h=150, mnb=False, mxb=False)
    cmds.columnLayout(adjustableColumn=True)
    cmds.textFieldGrp('PrefixTxtFldGrp', label='Prefix: ', cw=[(1, 50), (2, 100)])
    cmds.textFieldGrp('SuffixTxtFldGrp', label='Suffix: ', cw=[(1, 50), (2, 100)])
    cmds.textFieldGrp('SearchTxtFldGrp', label='Search: ', cw=[(1, 50), (2, 100)])
    cmds.textFieldGrp('ReplaceTxtFldGrp', label='Replace: ', cw=[(1, 50), (2, 100)])
    cmds.button(label='Duplicate and Rename', command=duplicateRenameSelectionCallback)
    cmds.window('dupRenameSelWin', e=True, w=10, h=10)
    cmds.showWindow('dupRenameSelWin')


def duplicateRenameSelectionCallback(*args):
    prefix = cmds.textFieldGrp('PrefixTxtFldGrp', q=True, text=True)
    suffix = cmds.textFieldGrp('SuffixTxtFldGrp', q=True, text=True)
    search = cmds.textFieldGrp('SearchTxtFldGrp', q=True, text=True)
    replace = cmds.textFieldGrp('ReplaceTxtFldGrp', q=True, text=True)

    duplicateRenameSelection(prefix=prefix, suffix=suffix, search=search, replace=replace)


def duplicateRenameSelection(prefix='', suffix='', search='', replace=''):
    sels = cmds.ls(sl=True, long=True)
    dupSels = cmds.duplicate(sels, rc=True, rr=True, f=True)
    for orig, dup in zip(sels, dupSels):
        origNodes = cmds.ls(orig, dag=True, long=True)
        dupNodes = cmds.ls(dup, dag=True, long=True)

        sortedOrigNodes = sorted(origNodes, key=lambda item: item.count('|'), reverse=True)
        sortedDupNodes = sorted(dupNodes, key=lambda item: item.count('|'), reverse=True)

        for origNode, dupNode in zip(sortedOrigNodes, sortedDupNodes):
            origBaseName = origNode.rsplit('|', 1)[1]
            origBaseNewName = prefix + origBaseName.replace(search, replace) + suffix
            cmds.rename(dupNode, origBaseNewName)
