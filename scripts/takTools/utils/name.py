import maya.cmds as cmds
import time
import re


def renameChildren(rootNode, prefix='', suffix='', search='', replace=''):
    children = cmds.listRelatives(rootNode, allDescendents=True, type='transform', fullPath=True) or []
    for node in children:
        nodeName = node.split('|')[-1]
        newName = prefix + nodeName + suffix
        newName = newName.replace(search, replace)
        try:
            cmds.rename(node, newName)
        except RuntimeError:
            pass


def componentNameFromId(index, object, componentType):
    """
    Return full component name from given index.

    Args:
        index (int): Component id.
        object (str): Mesh or Nurbs name.
        componentType (str): Component type name. ['vertex', 'edge', 'face']

    Returns:
        [type]: [description]
    """
    typeTable = {
        'vertex': 'vtx',
        'edge': 'e',
        'face': 'f',
    }
    obj = object
    if cmds.nodeType(obj) == 'transform':
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        if shapes:
            obj = shapes[0]

    return '{0}.{1}[{2}]'.format(obj, typeTable[componentType], index)


def idFromComponentName(componentName):
    id = None

    result = re.search(r'.*?\[(\d+)\]', componentName)
    if result:
        id = result.group(1)

    return int(id)


def convertNiceComponentName(componentName):
    """
    Replace character dot and square bracket to underscore.

    Args:
        componentName (str): Vertex or edge or face or cv name.

    Returns:
        str: Converted name.
    """
    replaceInfo = {
        r'[\.]': '_',
        r'[\[\]]': ''
    }

    for searchPattern, replaceCharacter in replaceInfo.items():
        componentName = re.sub(searchPattern, replaceCharacter, componentName)

    return componentName


def removeNamespaces(replaceChar='_'):
    """
    Remove namespaces in current scene.

    Args:
        replaceChar (str, optional): A character for replace character semi-colon(':'). Defaults to '_'.
    """

    startTime = time.time()
    namespaceChar = ':'

    allNodes = cmds.ls(long=True) or []
    for node in allNodes:
        if namespaceChar in node:
            newName = node.replace(namespaceChar, replaceChar)
            try:
                cmds.rename(node, newName)
            except RuntimeError:
                pass

    allNamespaces = cmds.namespaceInfo(listOnlyNamespaces=True) or []
    for namespace in allNamespaces:
        if namespace in ('UI', 'shared'):
            continue
        try:
            cmds.namespace(rm=namespace, mergeNamespaceWithRoot=True)
        except RuntimeError:
            pass

    duration = time.time() - startTime
    print('Remove namespace job done in %ss.' % duration)


def copyName(source, target, stripNamespace=True):
    srcName = source.split(':')[-1] if stripNamespace else source
    try:
        cmds.rename(target, srcName)
    except RuntimeError:
        pass
