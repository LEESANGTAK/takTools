'''
Author: Sangtak Lee
Contact: chst27@gmail.com

Description:
This script is for cleaning up the models before into the rigging stage.

Updated:
07/05/2022

Usage:
import tak_cleanUpModel
reload(tak_cleanUpModel)
tak_cleanUpModel.UI()
'''

import os
import re
import shutil
from functools import partial

import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya


def UI():
    winName = 'CUMWin'
    if cmds.window(winName, exists = True):
        cmds.deleteUI(winName)
    cmds.window(winName, title = 'Cleanup Model', mnb = False, mxb = False)

    cmds.tabLayout('mainTab', tv = False)
    cmds.columnLayout('procColLay', adj = True)

    # unique name section
    cmds.setParent('procColLay')
    cmds.frameLayout(label = 'Correct Naming', collapsable = True, collapse = True)
    cmds.rowColumnLayout('uniqNameRowColLay', numberOfColumns=3, columnSpacing=[(2, 5), (3, 5)])
    cmds.button(label="Check Namespace", w=127, c=chkNamespace)
    cmds.button('uniqTransformButt', w=127, label='Check Unique Name', c=uniqTransformName)
    cmds.button('autoUniqButt', w=127, label='Auto Unique Name', c=autoUniqName)

    # Check the mesh errors
    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout(label = 'Geometry Error Check', collapsable = True, collapse = True)
    cmds.rowColumnLayout('mdlErrChkRowColLay', numberOfColumns = 3, columnSpacing = [(2, 5), (3, 5)])
    cmds.button(label = 'Nonmanifold Geometry', w=128, c=lambda args: mel.eval('polyCleanupArgList 3 { "0","2","1","0","0","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","1","0" };selectMode -component;selectType -pv true;string $selLs[] = `ls -sl`;if(size($selLs) == 0){selectMode -object;}'))
    cmds.button(label = 'More than 4-Side', w=128, c=lambda args: mel.eval('polyCleanupArgList 4 { "0","2","1","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    cmds.button(label = 'Overlapped Vertex', w=128, c=lambda args: mel.eval('polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0" };'))
    cmds.button(label = 'Overlapped Root Curve', w=128, c=findOverlappedRootCurve)
    cmds.button(label = 'Check UV Sets', w=128, c=checkUVSets)
    cmds.button(label = 'Left handed tangent space', w=128, c=setTangentSapceLeftHanded)

    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout(label = 'Manual Check List', collapsable = True, collapse = True)
    cmds.checkBox('mdlGridChkBox', label = 'World Position: Center of the Grid in Front and Side, Bottom on Grid', cc = partial(chkBoxCC, 'mdlGridChkBox'))
    cmds.checkBox('scaleChkBox', label = 'Scale: Compare to other characters, Real World Scale', cc = partial(chkBoxCC, 'scaleChkBox'))
    cmds.checkBox('dfltStateChkBox', label = 'Default Pose: Middle Pose between extreme poses', cc = partial(chkBoxCC, 'dfltStateChkBox'))
    cmds.checkBox('topoChkBox', label = 'Topology: Deformable/Continuous Flow, Enough Resolution, Quad', cc = partial(chkBoxCC, 'topoChkBox'))
    cmds.checkBox('hiddenChkBox', label = 'Hidden Area: Inner Eyelid, Inner Mouth, Inner Cloth', cc = partial(chkBoxCC, 'hiddenChkBox'))

    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout('symFrameLo', label = 'Symmetry', collapsable = True, collapse = True)
    cmds.columnLayout('symColLo', adj = True)
    cmds.rowColumnLayout('checkSymRowColLo', numberOfColumns=3, columnSpacing=[(2, 3), (3, 3)])
    cmds.text(label='Search Tolerance: ')
    cmds.floatField('ctVtxTolFltFld', v = 0.001)
    cmds.button('symChkButton', label = 'Check Symmetry', c = checkSym)
    cmds.setParent('symColLo')
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.floatSliderGrp(label='Match Sym Vertex: ', field=True, value=0.001, min=0.001, max=1.000, step=0.001, columnWidth=[(1, 93), (2, 40), (3, 150)], cc=matchMirrorVtxPosition)
    cmds.button(label='translateX to Zero', c=zeroVtx)
    cmds.setParent('symColLo')
    cmds.separator()
    cmds.text(label = 'Warning! Check uv is correctly copied.\nFor uv comparison recommended to duplicate original mesh.')
    cmds.radioButtonGrp('symSmpSpcRdoBtn', label = 'Sample Space for UV Copy: ', numberOfRadioButtons = 3, labelArray3 = ['World', 'Component', 'Topology'], select = 1, columnWidth = [(2, 70), (3, 100), (4, 70)])
    cmds.rowColumnLayout('symRowColLay', numberOfColumns = 2, columnSpacing=[(2, 20)])
    cmds.button('makeSymButton', label = 'Make Symmetry', c = makeSym)
    cmds.radioButtonGrp('symOptRadButGrp', numberOfRadioButtons = 2, labelArray2 = ['x to -x', '-x to x'], columnWidth = [(1, 60), (2, 50)], select = 1)
    cmds.setParent('symFrameLo')

    # Material Clean Up
    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout(label = 'Material Clean Up', collapsable = True, collapse = True)
    # cmds.button(label="Check material that assigned to face", c=chkFaceAssignedMat)
    cmds.rowColumnLayout('viewShaderRowColLay', numberOfColumns = 3, columnWidth = [(1, 135), (2, 135), (3, 120)], columnSpacing = [(2, 2), (3, 2)])
    cmds.button(label = 'Correct Materials', c = correctMaterials, ann='Correct normal map color space to have raw and remove ambient color.')
    cmds.button(label = 'Separate Faces by Mat', c = partial(sepCombineByMat, 'separate'))
    cmds.button(label = 'Package Textures', c = showPackageTexturesUI)
    cmds.button(label = 'Combine Faces by Mat', c = partial(sepCombineByMat, 'combine'))
    cmds.button(label = 'Combine Objects by Mat', c = combineObjByMat, ann = 'Select poly objects.')

    cmds.setParent('procColLay')
    cmds.separator(h = 5, style = 'in')
    cmds.frameLayout(label = 'Essential Procedures', collapsable = True)
    cmds.columnLayout(adj = True)
    cmds.button(label = 'Delete Junk Child of Shape', c = delChildOfShape)
    cmds.button('matchShapeButt', label = 'Match Shape Name', c = matchShape)
    cmds.button('histButton', label = 'Unlock Attribute, Break Connections', c = cleanChBox)
    cmds.button('frzBtn', label = 'Freeze Transform', c = freezeTrnf)
    cmds.button('resetVtxBtn', label = 'Reset Vertex', c = resetVtx)
    cmds.button(label = 'Delete History', c = delHis)
    cmds.button('intermButton', label = 'Delete Intermediate Object', c = delInterMediObj)
    cmds.button(label = 'Off Drawing Override of Shape, Double Sided On, Primary visibility On', c = setShpAttrs)

    cmds.button('allButton', label = 'All in One', c = allInOne, h = 40, bgc = [1, 0.5, 0.2])

    cmds.window(winName, edit = True, w = 400, h = 300)
    cmds.showWindow(winName)

    cmds.showWindow()


def texScrListSelCmd(widgetName, *args):
    selItem = cmds.textScrollList(widgetName, q = True, selectItem = True)
    cmds.select(selItem, r = True)


def chkBoxCC(wdgName, *args):
    chkState = cmds.checkBox(wdgName, q = True, v = True)

    if chkState:
        cmds.checkBox(wdgName, e = True, enable = False)


# --------------------------------------------------------
# Name related functions
# --------------------------------------------------------
def chkNamespace(*args):
    '''
    Check unused namespace.
    '''

    namespaceList = cmds.namespaceInfo(lon=True)
    ignoreNamespaces = ['UI', 'shared']
    for _namespace in namespaceList:
        if not _namespace in ignoreNamespaces:
            cmds.NamespaceEditor()
            break

def notUniqNameExsistChk():
    '''
    Check if not unique named object exists in the current scene.
    '''

    sceneList = cmds.ls()

    if '|' in str(sceneList):
        return True
    else:
        return False

def uniqTransformName(*args):
    # UI
    if cmds.window('utnWin', exists = True):
        cmds.deleteUI('utnWin')
    cmds.window('utnWin', title = 'Unique Transform Name')
    cmds.frameLayout('mainframLay', labelVisible = False)
    cmds.textScrollList('utnTexScr', ams = True, selectCommand = partial(texScrListSelCmd, 'utnTexScr'), doubleClickCommand = utnDoubClicCmd)
    cmds.popupMenu()
    cmds.menuItem(label = 'Refresh List', c = utnPopuTexScr)
    cmds.menuItem(label = 'Delete Selected', c = utnDelSel)
    cmds.window('utnWin', e = True, w = 300, h = 300)

    result = notUniqNameExsistChk()

    if result:
        cmds.showWindow('utnWin')
        utnPopuTexScr()

def utnPopuTexScr(*args):
    if cmds.textScrollList('utnTexScr', q = True, allItems = True):
        cmds.textScrollList('utnTexScr', e = True, removeAll = True)
    # populate scroll list with not unique transform name
    sceneList = cmds.ls()
    for item in sceneList:
        if '|' in item and cmds.objectType(item) != 'mesh':
            cmds.textScrollList('utnTexScr', e = True, append = item)

def utnDelSel(*args):
    selItems = cmds.textScrollList('utnTexScr', q = True, selectItem = True)
    cmds.delete(selItems)

def utnDoubClicCmd(*args):
    origName = cmds.textScrollList('utnTexScr', q = True, selectItem = True)[0]
    origNiceName = origName.rsplit('|')[-1]
    result = cmds.promptDialog(title = 'Rename Object',
                               message = 'Enter Name:',
                               button = ['OK', 'Cancel'],
                               defaultButton = 'OK',
                               cancelButton = 'Cancel',
                               dismissString = 'Cancel',
                               text = origNiceName)
    if result == 'OK':
        newName = cmds.promptDialog(q = True, text = True)
        cmds.rename(origName, newName)
    # refresh unique name list
    utnPopuTexScr()


def autoUniqName(*args):
    sels = pm.selected()
    if sels:
        notUniqueNodes = [node for node in sels if '|' in node.name()]
    else:
        notUniqueNodes = [node for node in pm.ls() if '|' in node.name()]

    newNameInfo = {}
    for node in notUniqueNodes:
        newNameInfo[node] = node.replace('|', '_')

    for node, newName in newNameInfo.items():
        node.rename(newName)

def matchShape(*args):
    selList = cmds.ls(sl = True, type = 'transform')

    for sel in selList:
        # Get shape name
        shpLs = cmds.listRelatives(sel, s = True, fullPath = True)

        if shpLs:
            shapName = shpLs[0]

            # If not match to transform name then rename.
            if shapName != '%sShape' %sel:
                # In case transform name is not unique.
                if '|' in sel:
                    niceShpBaseName = sel.rsplit('|')[-1]
                    cmds.rename(shapName, '%sShape' %niceShpBaseName)
                else:
                    cmds.rename(shapName, '%sShape' %sel)


# --------------------------------------------------------
# Geometry error check related functions
# --------------------------------------------------------
def findOverlappedRootCurve(*args):
    rootCVs = [crv.getShape().cv[0] for crv in pm.selected()]
    thresholds = 0.1
    stackedCvs = []
    for i in range(len(rootCVs)):
        iCvPos = rootCVs[i].getPosition(space='world')
        for cv in rootCVs[i+1:]:
            cvPos = cv.getPosition(space='world')
            if (cvPos - iCvPos).length() <= thresholds:
                stackedCvs.extend([rootCVs[i], cv])

    stackedCrvs = [cv.node().getTransform() for cv in stackedCvs]
    pm.select(stackedCrvs, r=True)


def checkUVSets(*args):
    DEFAULT_UV_SET_NAME = 'map1'
    errorMeshes = []

    for sel in pm.selected():
        uvSets = sel.getUVSetNames()
        if len(uvSets) > 1:
            errorMeshes.append(sel)
        elif len(uvSets) == 1 and DEFAULT_UV_SET_NAME != uvSets[0]:
            pm.polyUVSet(rename=True, newUVSet=DEFAULT_UV_SET_NAME, uvSet=uvSets[0])
            print('UV Set "{}" in {} has been renamed to "{}".'.format(uvSets[0], sel, DEFAULT_UV_SET_NAME))
    if errorMeshes:
        pm.warning('{errorMeshes} are have more than one UV Set.'.format(errorMeshes=str(errorMeshes)))
        pm.mel.uvSetEditor()


def setTangentSapceLeftHanded(*args):
    for obj in pm.selected():
        meshes = obj.getChildren(type='mesh', ni=True)
        if meshes:
            for mesh in meshes:
                mesh.tangentSpace.set(2)



# --------------------------------------------------------
# Symmetry related functions
# --------------------------------------------------------
def getVtxInfo(sel):
    numOfVtx = cmds.polyEvaluate(v = True)
    leftVtxDic = {}
    rightVtxDic = {}
    centerVtxDic = {}

    try:
        ctVtxTol = cmds.floatField('ctVtxTolFltFld', q = True, v = True)
    except:
        ctVtxTol = 0.001

    for i in range(numOfVtx):
        iPos = cmds.pointPosition('%s.vtx[%d]' %(sel, i), local = True)
        # refine raw iPos data
        for val in range(len(iPos)):
            if 'e' in str(iPos[val]):
              iPos[val] = 0.0
            else:
              iPos[val] = float('%.3f' %iPos[val])
        # classify depend on x position
        if -ctVtxTol <= iPos[0] <= ctVtxTol:
            centerVtxDic['%s.vtx[%d]' %(sel, i)] = tuple(iPos)
        if iPos[0] > 0:
            leftVtxDic['%s.vtx[%d]' %(sel, i)] = tuple(iPos)
        if iPos[0] < 0:
            rightVtxDic['%s.vtx[%d]' %(sel, i)] = tuple(iPos)
    return leftVtxDic, rightVtxDic, centerVtxDic

def getSidestVtx(vtxInfoDic):
    vtxName = ''
    sidestVal = 0

    for vtx in vtxInfoDic.keys():
        vtxPosition = vtxInfoDic[vtx]
        if sidestVal < abs(vtxPosition[0]):
            vtxName = vtx
            sidestVal = abs(vtxPosition[0])

    return vtxName

def checkSym(*args):
    sel = cmds.ls(sl = True)[0]
    aSymVtxList = []
    # get data
    leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(sel)
    # search asymmetrical vertices
    for lVtx in leftVtxDic.keys():
        symVtxPos = -leftVtxDic[lVtx][0], leftVtxDic[lVtx][1], leftVtxDic[lVtx][2]
        if not symVtxPos in rightVtxDic.values():
            aSymVtxList.append(lVtx)
    for rVtx in rightVtxDic.keys():
        symVtxPos = -rightVtxDic[rVtx][0], rightVtxDic[rVtx][1], rightVtxDic[rVtx][2]
        if not symVtxPos in leftVtxDic.values():
            aSymVtxList.append(rVtx)
    # report the result
    if aSymVtxList:
            cmds.warning('"%s" is not symmetrical.' %sel)
            cmds.select(aSymVtxList)
            return False
    else:
        mel.eval('print "%s is symmetrical."' %sel)
    return True

def matchMirrorVtxPosition(searchTolerance):
    vtxs = cmds.ls(sl=True, fl=True)
    if not '.' in str(vtxs):
        return

    lfVtxs = [vtx for vtx in vtxs if cmds.pointPosition(vtx, local=True)[0] > 0]
    rtVtxs = list(set(vtxs) - set(lfVtxs))

    nonMatchVtxs = []

    for leftVtx in lfVtxs:
        vtxPoint = OpenMaya.MPoint(*cmds.pointPosition(leftVtx, local=True))
        mirrorPoint = OpenMaya.MPoint(-vtxPoint.x, vtxPoint.y, vtxPoint.z)

        mirrorVtx = findMirrorVtx(mirrorPoint, rtVtxs, searchTolerance=searchTolerance)
        if mirrorVtx:
            rtVtxs.pop(rtVtxs.index(mirrorVtx))
            cmds.xform(mirrorVtx, translation=[mirrorPoint.x, mirrorPoint.y, mirrorPoint.z], os=True)
        else:
            nonMatchVtxs.append(leftVtx)

    cmds.select(nonMatchVtxs, rtVtxs, r=True)


def findMirrorVtx(mirrorPoint, vtxList, searchTolerance):
    resultVtx = None
    minDistance = 100
    for vtx in vtxList:
        vtxPoint = OpenMaya.MPoint(*cmds.pointPosition(vtx, local=True))
        vec = vtxPoint - mirrorPoint
        if vec.length() <= searchTolerance and vec.length() <= minDistance:
            minDistance = vec.length()
            resultVtx = vtx
    return resultVtx


def zeroVtx(*args):
    vtxs = pm.selected(fl=True)
    for vtx in vtxs:
        vtxPos = vtx.getPosition(space='world')
        vtx.setPosition((0, vtxPos[1], vtxPos[2]), space='world')


def makeSym(*args):
    selLs = cmds.ls(sl = True)

    # When user select center edge loop.
    if '.e' in selLs[0]:
        numOfShells = cmds.polyEvaluate(shell = True)
        if numOfShells > 1:
            cmds.confirmDialog(title = 'Warning', message = 'Selected mesh is made of combining several geometry. Separate mesh and try it again.')
            return False

        centerEdgeLoop = selLs
        objName = centerEdgeLoop[0].split('.')[0]
        uvKeepGeo = cmds.duplicate(objName, n = '{0}_uvKeep_geo'.format(objName))

        mel.eval('PolySelectConvert 3;')
        zeroVtx()

        cmds.select(centerEdgeLoop, r = True)
        cmds.DetachComponent()

        leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(objName)

        symOpt = cmds.radioButtonGrp('symOptRadButGrp', q = True, select = True)

        # If user select 'x to -x' mean left to right.
        if symOpt == 1:
            rightestVtx = getSidestVtx(rightVtxDic)
            cmds.select(rightestVtx, r = True)
            mel.eval('PolySelectConvert 1;') # Convert vertex selection to face.

            rightestFace = cmds.ls(sl = True, fl = True)[0]
            rightestFaceId = int(re.search(r'.+f\[(\d+)\]', rightestFace).group(1))
            cmds.polySelect(extendToShell = rightestFaceId)
            cmds.delete()

            # mirror geometry
            mirrorNode = cmds.polyMirrorFace(objName, ws = True, direction = 1, mergeMode = 0, mergeThreshold = 0.001, ch = True)
            cmds.polyMirrorFace(mirrorNode, e = True, pivotX = 0.0)

        # If user select '-x to x' mean right to left.
        if symOpt == 2:
            leftestVtx = getSidestVtx(leftVtxDic)
            cmds.select(leftestVtx, r = True)
            mel.eval('PolySelectConvert 1;') # Convert vertex selection to face.

            leftestFace = cmds.ls(sl = True, fl = True)[0]
            leftestFaceId = int(re.search(r'.+f\[(\d+)\]', leftestFace).group(1))
            cmds.polySelect(extendToShell = leftestFaceId)
            cmds.delete()

            # mirror geometry
            mirrorNode = cmds.polyMirrorFace(objName, ws = True, direction = 1, mergeMode = 0, mergeThreshold = 0.001, ch = True)
            cmds.polyMirrorFace(mirrorNode, e = True, pivotX = 0.0)

    # When user select object.
    else:
        objName = selLs[0]
        uvKeepGeo = cmds.duplicate(objName, n = '{0}_uvKeep_geo'.format(objName))

        leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(objName)

        symOpt = cmds.radioButtonGrp('symOptRadButGrp', q = True, select = True)

        if centerVtxDic.keys():
            cmds.select(list(centerVtxDic.keys()), r = True)
            mel.eval('SelectEdgeLoopSp;')
            zeroVtx()

        leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(objName) # Refresh vertex position information.

        # If user select 'x to -x' mean left to right.
        if symOpt == 1:
            cmds.select(list(rightVtxDic.keys()), r = True)
            mel.eval('PolySelectConvert 1;') # Convert vertex selection to face.
            cmds.delete()

            # mirror geometry
            mirrorNode = cmds.polyMirrorFace(objName, ws = True, direction = 1, ch = True)
            cmds.polyMirrorFace(mirrorNode, e = True, pivotX = 0.0)

        # If user select 'x to -x' mean right to left.
        if symOpt == 2:
            cmds.select(list(leftVtxDic.keys()), r = True)
            mel.eval('PolySelectConvert 1;') # Convert vertex selection to face.
            cmds.delete()

            # mirror geometry
            mirrorNode = cmds.polyMirrorFace(objName, ws = True, direction = 1, ch = True)
            cmds.polyMirrorFace(mirrorNode, e = True, pivotX = 0.0)


    leftVtxDic, rightVtxDic, centerVtxDic = getVtxInfo(objName)
    if centerVtxDic.keys():
        cmds.select(list(centerVtxDic.keys()), r = True)
        cmds.polyMergeVertex(distance = 0.001)


    # Copy uv from uv keeped geometry to new symmetrized geometry.
    smpSpc = cmds.radioButtonGrp('symSmpSpcRdoBtn', q = True, select = True)
    if smpSpc == 2:
        smpSpc = 4
    elif smpSpc == 3:
        smpSpc = 5
    cmds.transferAttributes(uvKeepGeo, objName, transferUVs = 2, sampleSpace = smpSpc)

    cmds.delete(objName, ch = True)
    cmds.delete(uvKeepGeo)

    cmds.select(objName, r = True)


# --------------------------------------------------------
# Material related functions
# --------------------------------------------------------
def combineObjByMat(*args):
    '''
    Combine objects that assigned same material.
    '''

    # Get material list
    selLs = cmds.ls(sl = True)
    matLs = getMatLs(selLs)

    # Iterate for materials
    for mat in matLs:
        # Select by material
        cmds.hyperShade(objects = mat)

        # Get transform node
        selLs = cmds.ls(sl = True)
        trsfLs = getTrsfLs(selLs)

        # Combine objects
        if len(trsfLs) == 1:
            cmds.select(trsfLs[0])
            cmds.hyperShade(assign = mat)
        else:
            combinedMesh = cmds.polyUnite(trsfLs)
            cmds.delete(combinedMesh, ch=True)
            cmds.rename(combinedMesh[0], '{mat}_mesh'.format(mat=mat))


def getMatLs(objLs):
    '''
    Get all materials assigned to given objecs.
    '''

    matLs = []

    for obj in objLs:
        mat = getMatFromSel(obj)
        matLs.extend(mat)

    return list(set(matLs))


def getTrsfLs(selLs):
    '''
    Get all transform node from selected objects.
    '''

    trsfLs = []

    for sel in selLs:
        objType = cmds.objectType(sel)
        if objType == 'transform':
            trsfLs.extend(sel)
        else:
            # Recurse until find parent transform node
            while objType != 'transform':
                sel = cmds.listRelatives(sel, p = True, path = True)
                objType = cmds.objectType(sel)

            trsfLs.extend(sel)

    return list(set(trsfLs))


def reAssignMatToObj(*args):
    sels = pm.selected()
    for sel in sels:
        shadingEngine = sel.getShape().connections(type='shadingEngine', s=False)[0]
        mat = shadingEngine.surfaceShader.connections(d=False)[0]
        pm.delete(shadingEngine)
        pm.select(sel, r=True)
        pm.hyperShade(assign=mat)


def showPackageTexturesUI(*args):
    pm.window('packageTexturesUI', title='Package Textures', mnb=False, mxb=False)
    pm.columnLayout(adj=True)
    pm.textFieldButtonGrp('textureDir', label='Texture Directory:', bl='<<', bc=getTextureDir)
    pm.button(label='Apply', c=packageTextures)
    pm.showWindow()

def getTextureDir(*args):
    textureDir = pm.fileDialog2(fileMode=3)
    if textureDir:
        pm.textFieldButtonGrp('textureDir', e=True, text=textureDir[0])

def packageTextures(*args):
    textureDir = pm.textFieldButtonGrp('textureDir', q=True, text=True)
    for fileTexture in pm.ls(type='file'):
        oldTexturePath = fileTexture.fileTextureName.get()
        fileName = os.path.basename(oldTexturePath)
        try:
            newTexturePath = os.path.join(textureDir, fileName)
            shutil.copyfile(oldTexturePath, newTexturePath)
            fileTexture.fileTextureName.set(newTexturePath)
        except:
            print('"{}" is not exists.'.format(oldTexturePath))
    pm.deleteUI('packageTexturesUI')

def reAssignMatToface(*args):
    sels = pm.selected()
    for sel in sels:
        shadingEngine = sel.getShape().connections(type='shadingEngine', s=False)[0]
        mat = shadingEngine.surfaceShader.connections(d=False)[0]
        pm.delete(shadingEngine)
        pm.select(sel.f, r=True)
        pm.hyperShade(assign=mat)
    pm.select(cl=True)


def sepCombineByMat(mode, *args):
    '''
    Separate face by material main function.
    '''

    selObjLs = cmds.ls(sl = True, long = True)

    selGeoFaceMatLs = faceAssignedMat(selObjLs)

    delGeoLs = []

    for mat in selGeoFaceMatLs:
        cmds.hyperShade(objects = mat)
        matAssignGeoLs = cmds.ls(sl = True)
        faces = cmds.filterExpand(matAssignGeoLs, ex = False, sm = 34)

        if faces:
            matAssignedFaceShapes = getShapesFromFaces(faces)
            matAssignedShapes = cmds.ls(matAssignGeoLs, type = 'mesh')
            toCombineGeoLs = []

            for faceShp in matAssignedFaceShapes:
                trsf = cmds.listRelatives(faceShp, p = True, fullPath = True)
                if trsf[0] in selObjLs: # Do it for selected objects only.
                    dupGeo = cmds.duplicate(trsf, renameChildren = True)

                    shpCorFaces = getCorrespondFaces(faceShp, faces)
                    dupGeoFaces = replaceGeoName(dupGeo[0], shpCorFaces)

                    cmds.select(dupGeoFaces, r = True)
                    cmds.InvertSelection()
                    cmds.delete()

                    # Remove faces from shading group
                    shapeName = cmds.listRelatives(dupGeo, ni = True, path = True, s = True)
                    sgName = list(set(cmds.listConnections('%s.instObjGroups.objectGroups' %shapeName[0], d = True, type = "shadingEngine")))
                    cmds.select('%s.f[*]' %dupGeo[0], r = True)
                    cmds.sets(remove = sgName[0])

                    # Select faces and assign material
                    cmds.select('{}.f[:]'.format(dupGeo[0]), r = True)
                    cmds.hyperShade(assign = mat)
                    cmds.rename(dupGeo, mat+'_geo')
                    cmds.delete(ch = True)

                    toCombineGeoLs.extend(dupGeo)
                    delGeoLs.extend(trsf)

                    print('>> "%s" has face assigned material.' %trsf)

                if mode == 'combine':
                    if len(toCombineGeoLs) > 1:
                        cmds.select(toCombineGeoLs, r = True)
                        finalGeo = cmds.polyUnite(toCombineGeoLs)
                        cmds.select(finalGeo, r = True)
                        cmds.hyperShade(assign = mat)
                    elif len(toCombineGeoLs) == 1:
                        cmds.select(toCombineGeoLs, r = True)
                        cmds.hyperShade(assign = mat)

                    cmds.delete(ch = True)

    if delGeoLs:
        cmds.delete(delGeoLs)
    else:
        OpenMaya.MGlobal.displayInfo('>> There is no object that material assigned to face.')

    cmds.select(cl=True)


def faceAssignedMat(geoLs):
    matLs = []

    for geo in geoLs:
        shape = cmds.listRelatives(geo, s=True)[0]
        sgName = cmds.listConnections('%s.instObjGroups.objectGroups' % shape, d = True, type = "shadingEngine")
        matName = cmds.ls(cmds.listConnections(sgName), materials = True)
        matLs.extend(matName)

    return list(set(matLs))


def getShapesFromFaces(faces):
    faceShpLs = []
    for face in faces:
        faceShpLs.extend(cmds.listRelatives(face, p = True, path = True))
    return list(set(faceShpLs))


def getCorrespondFaces(shp, faces):
    geoName = cmds.listRelatives(shp, p = True, path = True)
    faceLs = []
    for face in faces:
        if geoName[0] in face:
            faceLs.append(face)
    return faceLs


def replaceGeoName(geoName, faces):
    newShpFaces = []
    for face in faces:
        newShpFaces.append(geoName + '.' + face.split('.')[-1])
    return newShpFaces


def getMatFromSel(obj):
    """ Get material From selected object """

    shapeName = cmds.listRelatives(obj, ni=True, path=True, s=True)

    if shapeName:
        sgName = cmds.listConnections(shapeName[0], d=True, type="shadingEngine")
        matName = [mat for mat in cmds.ls(cmds.listConnections(sgName), materials=True) if not cmds.nodeType(mat) == 'displacementShader']

        return list(set(matName))

def findShadingEngine(startNode):
    destinationNodes = cmds.listConnections(startNode, s = False, scn = True)

    resultShadingEngine = ''

    if destinationNodes:
        for node in destinationNodes:
            if cmds.nodeType(node) == 'shadingEngine':
                resultShadingEngine = node
            else:
                pass

        if resultShadingEngine:
            return resultShadingEngine
        else:
            for node in destinationNodes:
                result = findShadingEngine(node)
                if result:
                    return result


# --------------------------------------------------------
# Misc functions
# --------------------------------------------------------
def cleanChBox(*args):
    mel.eval('source channelBoxCommand;')
    attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']
    selList = cmds.ls(sl = True)

    for sel in selList:
        # If sel is shape, skip sel.
        if cmds.objectType(sel) == 'mesh' or "Shape" in sel:
            continue
        # unlock attribute
        for attr in attrList:
            cmds.setAttr(sel + '.' + str(attr), lock = False)
        # break connections
        for attr in attrList:
            cmds.delete('{0}.{1}'.format(sel, attr), inputConnectionsAndNodes = True)
            mel.eval('CBdeleteConnection' + ' %s.%s;' %(sel, attr))

    cmds.select(selList, r = True)


def resetVtx(*args):
    selList = cmds.ls(sl = True)

    # progress window
    cmds.progressWindow(title = 'Reset Vertex', minValue = 0, maxValue = len(selList), progress = 0, status = 'Stand by', isInterruptable = True)

    for sel in selList:
        if cmds.progressWindow(q = True, isCancelled = True):
            break

        cmds.progressWindow(e = True, progress = selList.index(sel), status = 'Working on \'%s\'' %(sel))

        if not cmds.listRelatives(sel, path = True, s = True, ni = True):
            continue
        else:
            # Reset vertex
            try:
                cmds.delete(cmds.polyMoveVertex(sel, localTranslate = (0, 0, 0)))
            except:
                pass

    cmds.progressWindow(e = True, progress = 0, status = 'Reset Vertex Work Done.')
    cmds.progressWindow(endProgress = True)

    cmds.select(selList, r = True)


def delHis(*args):
    cmds.delete(ch = True)


def delInterMediObj(*args):
    selList = cmds.ls(sl = True)
    for sel in selList:
        # delete intermediate object
        itmdShapList = cmds.ls(sel, dag = True, s = True, io = True)
        for shap in itmdShapList:
            intmResult = cmds.getAttr('%s.intermediateObject' %(shap))
            if intmResult:
                cmds.delete(shap)
                print ('Intermediate object "%s" is deleted.' %shap)


def setShpAttrs(*args):
    selList = cmds.ls(sl = True)
    for sel in selList:
        if cmds.objectType(sel) == 'transform':
            selShape = cmds.listRelatives(sel, c = True, s = True, path = True)
            # If transform has no shape, skip to next item.
            if not selShape:
                continue
            elif len(selShape) > 1:
                continue
                # cmds.error("%s object has more than one shape." %sel)
            else:
                # Check if selShape is uniqe.
                if not len(cmds.ls(selShape)) == 1:
                    cmds.error("%s object's name is not uniqe. May exists same object name." %sel)

            # turn off drawing override of the shape
            drovInput = cmds.listConnections('%s.drawOverride' %selShape[0], s = True, d = False, p = True)
            if drovInput:
                cmds.disconnectAttr(drovInput[0], '%s.drawOverride' %selShape[0])
            cmds.setAttr('%s.overrideEnabled' %selShape[0], 0)
            if cmds.objExists('%s.doubleSided' %selShape[0]):
                cmds.setAttr('%s.doubleSided' %selShape[0], 1)
            if cmds.objExists('%s.opposite' %selShape[0]):
                cmds.setAttr('%s.opposite' %selShape[0], 0)
            if cmds.objExists('%s.primaryVisibility' %selShape[0]):
                cmds.setAttr('%s.primaryVisibility' %selShape[0], 1)

        # if sel is shape, set overrideEnabeld to 0
        elif cmds.objectType(sel) == 'mesh':
            drovInput = cmds.listConnections('%s.drawOverride' %sel, s = True, d = False, p = True)
            if drovInput:
                cmds.disconnectAttr(drovInput[0], '%s.drawOverride' %sel)
            cmds.setAttr('%s.overrideEnabled' %sel, 0)
            cmds.setAttr('%s.doubleSided' %sel, 1)
            cmds.setAttr('%s.opposite' %sel, 0)
            cmds.setAttr('%s.primaryVisibility' %sel, 1)
        else:
            pass


def freezeTrnf(*args):
    '''
    Freeze transform.
    '''

    sels = cmds.ls(sl = True, dag = True)

    # Get place3dTexture nodes.
    plc3dTexLs = cmds.ls(sl = True, dag = True, type = 'place3dTexture')

    # Get place3dTexture nodes's parent group.
    plc3dTexGrpLs = []
    for plce3dTex in plc3dTexLs:
        plc3dTexGrpLs.append(cmds.listRelatives(plce3dTex, p = True, path = True)[0])

    plc3dTexGrpLs = list(set(plc3dTexGrpLs))


    # Get ordered list for group.
    plc3dTexDic = {}
    for grp in plc3dTexGrpLs:
        plc3dTexLsInOrder = cmds.listRelatives(grp, path = True)
        plc3dTexLsInOrder = [x for x in plc3dTexLsInOrder if 'Shape' not in x]
        plc3dTexDic[grp] = plc3dTexLsInOrder

    # Parent to the world.
    for plc3dTex in plc3dTexLs:
        cmds.parent(plc3dTex, world = True)

    # Remove place3dTexture in selection list.
    for plce3dTex in plc3dTexLs:
        sels.remove(plce3dTex)

    # Freeze transform.
    cmds.select(sels, r = True)
    cmds.makeIdentity(apply = True)

    # Parent to the world for all childs of plce3dTexGrp.
    for grp in plc3dTexDic.keys():
        for item in plc3dTexDic[grp]:
            if not cmds.listRelatives(item, p = True) == None:
                cmds.parent(item, world = True)

    # Turn back.
    for grp in plc3dTexDic.keys():
        for item in plc3dTexDic[grp]:
            cmds.parent(item, grp)

    cmds.select(sels, r = True)


def delChildOfShape(*args):
    """ Delete children of shape that isn't necessary """
    shapes = pm.ls(sl=True, type='shape')
    for shape in shapes:
        junkShapes = shape.listRelatives()
        if junkShapes:
            pm.delete(junkShapes)


def correctMaterials(*args):
    for mat in pm.ls(materials=True):
        # Set ambient color to 0
        try:
            mat.ambientColor.set(0, 0, 0)
        except:
            pass
        # Remove FBX ascii space string
        searchStr = 'FBXASC032'
        relpaceStr = ''
        try:
            mat.rename(mat.replace(searchStr, relpaceStr))
        except:
            pass

    # Set color space of the normal map to raw
    for node in pm.ls(type='bump2d'):
        fileNode = node.inputs(type='file')
        if fileNode:
            fileNode[0].colorSpace.set('Raw')
            fileNode[0].ignoreColorSpaceFileRules.set(True)



def allInOne(*args):
    delHis()
    delChildOfShape()
    matchShape()
    cleanChBox()
    freezeTrnf()
    resetVtx()
    delHis()
    delInterMediObj()
    setShpAttrs()
