import pymel.core as pm

import time
import re



def renameChildren(rootNode, prefix='', suffix='', search='', replace=''):
    rootNode = pm.PyNode(rootNode)
    for node in rootNode.getChildren(ad=True, type='transform'):
        node.rename(prefix + node.nodeName() + suffix)
        node.rename(node.replace(search, replace))


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
    object = pm.PyNode(object)
    if object.nodeType() == 'transform':
        object = object.getShape()

    compoenentName = ''
    compoenentName = '{0}.{1}[{2}]'.format(object, typeTable[componentType], index)
    return compoenentName


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

    allNodes = pm.ls()
    for node in allNodes:
        if namespaceChar in node.name():
            node.rename(node.replace(namespaceChar, replaceChar))

    allNamespaces = pm.listNamespaces()
    for namespace in allNamespaces:
        namespace.remove()

    duration = time.time() - startTime
    pm.displayInfo('Remove namespace job done in %ss.' % duration)


def copyName(source, target, stripNamespace=True):
    src = pm.PyNode(source)
    trg = pm.PyNode(target)

    trg.rename(src.name(stripNamespace=stripNamespace))
