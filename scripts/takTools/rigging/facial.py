"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Description:
This module contain functions for facial setup.
"""

import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om
import re
from ..common import tak_misc


# Targets that has 'LeftRight' suffix is made as pristine then split to 'Left' side and 'Right' side.
"""
from takTools.rigging import facial
reload(facial)

pm.undoInfo(openChunk=True)
for grp, targets in facial.ARKIT_TARGETS.items():
    grp = pm.createNode('transform', n=grp+'_grp')
    facial.createFacialList('src_facial', targets)
    pm.parent(targets, grp)
pm.undoInfo(closeChunk=True)
"""
ARKIT_TARGETS = {
    'brow': [
        'browInnerUp',
        'browOuterUpLeftRight',
        'browDownLeftRight',
    ],
    'eye': [
        'eyeBlinkLeftRight',
        'eyeWideLeftRight',
        'eyeLookUpLeftRight',
        'eyeLookDownLeftRight',
        'eyeLookInLeftRight',
        'eyeLookOutLeftRight',
        'eyeSquintLeftRight',
    ],
    'cheek': [
        'cheekSquintLeftRight',
        'cheekPuff'
    ],
    'nose': [
        'noseSneerLeftRight'
    ],
    'mouth': [
        'mouthSmileLeftRight',
        'mouthDimpleLeftRight',
        'mouthFrownLeftRight',
        'mouthStretchLeftRight',
        'mouthUpperUpLeftRight',
        'mouthLowerDownLeftRight',
        'mouthPressLeftRight',
        'mouthShrugUpper',
        'mouthShrugLower',
        'mouthRollUpper',
        'mouthRollLower',
        'mouthFunnel',
        'mouthPucker',
        'mouthLeft',
        'mouthRight',
        'mouthClose'
    ],
    'jaw': [
        'jawOpen',
        'jawLeft',
        'jawRight',
        'jawForward'
    ]
}



def createFacialList(facialGrp, facialList):
    '''facialList = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry', 'eyebrow_sad',
                      'eyelid_blink', 'eyelid_smile', 'eyelid_angry', 'eyelid_sad', 'eyelid_big',
                      'lip_smile', 'lip_frown', 'lip_wide', 'lip_narrow', 'lip_openSmileBig', 'lip_angryBig',
                      'a', 'e', 'i', 'o']'''

    for item in facialList:
        cmds.duplicate(facialGrp, n=item, renameChildren=True, returnRootsOnly=True)

    cmds.select(facialList, r=True)

# Extract facial targets from rigged geo
'''
facialRigGrp = pm.PyNode('rig_face_grp')
targetNameList = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry', 'eyebrow_sad',
    'eyelid_blink', 'eyelid_smile', 'eyelid_angry', 'eyelid_sad', 'eyelid_big',
    'lip_wide', 'lip_narrow', 'lip_smile', 'lip_frown', 'lip_openSmileBig', 'lip_angryBig']
startFrame = 11
increment = 20

extractFacialTargets(facialRigGrp, targetNameList, startFrame, increment)
'''
def extractFacialTargets(facialRigGrp, targetNameList, startFrame, increment):
    pm.currentTime(startFrame)
    for trgName in targetNameList:
        facialRigGrp.duplicate(n=trgName, renameChildren=True)
        startFrame+=increment
        pm.currentTime(startFrame)


def extractFacialTargetsWithCtrl(facialGrp, control, lfRtPrefix=['L', 'R']):
    """
    Args:
        facialGrp (pymel.nodetypes.transform): Facial group that contain facial expressions
        control (pymel.nodetypes.transform): Facial control curve
    """
    lfRtAttrs = []
    for attr in control.listAttr(keyable=True):
        if attr.isLocked():
            continue
        attrPrefix = attr.attrName().split('_')[0]
        if attrPrefix in lfRtPrefix:
            lfRtAttrs.append(attr.attrName().replace(attrPrefix, ''))
        else:
            attr.set(1)
            facialGrp.duplicate(renameChildren=True, name='{ctrlName}_{attrName}'.format(ctrlName=control.name(), attrName=attr.attrName()))
            attr.set(0)

    for lfRtAttr in list(set(lfRtAttrs)):
        for prefix in lfRtPrefix:
            control.attr(prefix+lfRtAttr).set(1)
        facialGrp.duplicate(renameChildren=True, name=control.name()+lfRtAttr)
        for prefix in lfRtPrefix:
            control.attr(prefix+lfRtAttr).set(0)


def extractFacialTargets(blendShape, facialGrp):
    trgLs = cmds.listAttr(blendShape + '.w', multi = True)

    for trg in trgLs:
        cmds.setAttr(blendShape + '.' + trg, 1)
        cmds.duplicate(facialGrp, renameChildren = True, n = trg)
        cmds.setAttr(blendShape + '.' + trg, 0)


def connectFacial(facialCtrl, blendshapeNode):
    facialAttrLs = cmds.listAttr(facialCtrl, keyable = True)
    for facialAttr in facialAttrLs:
        facialBsTrgName = re.sub(r'ctrl', facialAttr, facialCtrl)

        if cmds.objExists(blendshapeNode + '.' + facialBsTrgName):
            try:
                cmds.connectAttr(facialCtrl + '.' + facialAttr, blendshapeNode + '.' + facialBsTrgName, f = True)
            except:
                pass

        if 'lip' in facialCtrl:
            if facialAttr in ['a','e', 'i', 'o', 'u']:
                try:
                    cmds.connectAttr(facialCtrl+'.'+facialAttr, blendshapeNode+'.'+facialAttr, f=True)
                except:
                    pass

            facialBsTrgName = re.sub(r'ctrl', facialAttr, facialCtrl)
            if 'lip_L' in facialBsTrgName:
                facialBsTrgName = re.sub(r'lip_L', 'lf_lip', facialBsTrgName)
            elif 'lip_R' in facialBsTrgName:
                facialBsTrgName = re.sub(r'lip_R', 'R_lip', facialBsTrgName)

            if cmds.objExists(blendshapeNode+'.'+facialBsTrgName):
                try:
                    cmds.connectAttr(facialCtrl+'.'+facialAttr, blendshapeNode+'.'+facialBsTrgName, f=True)
                except:
                    pass


### Facial Tertiary ###
def createCurveSystem(name, numOfControls):
    """
    Create curve system with selected edge loop

    Parameters:
        name: Rig name
        numOfControls: Number of local controls
    """

    # Convert edges to curve
    rawCurve = pm.PyNode(pm.polyToCurve(n=name+'_crv', form=2, degree=1)[0])

    # Create joints with rawCurve
    jnts = []
    for cv in rawCurve.cv:
        pm.select(cl=True)
        jnts.append(pm.joint(p=cv.getPosition(space='world'), radius=0.25))
    jnts = renameByPosition(name, jnts)

    # Rebuild curve and delete history
    newCrv = pm.rebuildCurve(rawCurve, spans=numOfControls-3, degree=3)[0]
    pm.delete(newCrv, ch=True)

    # Attach cluster to the curve cvs
    clusters = [pm.cluster(cv)[1] for cv in newCrv.cv]
    clusters = renameByPosition(name, clusters, suffix='clst')
    locatorZeroGrps = []
    for clst in clusters:
        pm.select(clst, r=True)
        locatorZeroGrps.extend(tak_misc.locGrp())
        clst.hide()

    # Set mirrored behavior for right side
    for locatorZeroGrp in locatorZeroGrps:
        locatorZeroGrp = pm.PyNode(locatorZeroGrp)
        if locatorZeroGrp.tx.get() < 0:
            clst, locator, autoGrp = pm.listRelatives(locatorZeroGrp, ad=True, type="transform")
            clst.setParent(w=True)
            locatorZeroGrp.sx.set(-1)
            clst.setParent(locator)

    # Cleanup outliner
    jntGrp = pm.group(jnts, n=name+'_jnt_grp')
    locGrp = pm.group(locatorZeroGrps, n=name+'_loc_grp')
    pm.group(jntGrp, locGrp, newCrv, n=name+'_system_grp')


def renameByPosition(name, transformList, suffix='bnd_jnt'):
    renamedList = []

    if isinstance(transformList[0], pm.nodetypes.Joint):
        if '_R' in name:
            transformList.sort(key=lambda x:x.tx.get(), reverse=True)
        else:
            transformList.sort(key=lambda x:x.tx.get())
    else:
        if '_R' in name:
            transformList.sort(key=lambda x:x.rotatePivotX.get(), reverse=True)
        else:
            transformList.sort(key=lambda x:x.rotatePivotX.get())

    for item in transformList:
        renamedList.append(item.rename('%s_%02d_%s' % (name, transformList.index(item)+1, suffix)))

    return renamedList


def mirrorXTransform(src, trg):
    srcMat = src.worldMatrix.get()
    srcMatX = srcMat[0]
    srcMatY = srcMat[1]
    srcMatZ = srcMat[2]
    srcMatT = srcMat[3]

    mirXMat = [
        -1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]

    mirroredMat = srcMat * pm.dt.Matrix(mirXMat)
    pm.xform(trg, matrix=mirroredMat, ws=True)



def createProjectedCurve(locators, nurbsSurface, name='projected_crv'):
    """
    Create curve with projected point on surface with locators.
    Locators order will be cv order.

    Args:
        locators (list<transform>): Locator transforms.
        nurbsSurface (pymel.nodetypes.NurbsSurface): Nurbs surface to project.
        name (str, optional): Curve name. Defaults to 'projected_crv'.
    """
    follicles = []
    positions = []
    for locator in locators:
        follicleTransform = createProjectedFollicle(locator, nurbsSurface)
        follicles.append(follicleTransform)
        positions.append(follicleTransform.getTranslation(space='world'))

    curve = pm.curve(d=3, p=positions, n=name)

    for follicle in follicles:
        decMatrix = pm.createNode('decomposeMatrix', n='%s_decMatrix' % follicle.name())
        follicle.worldMatrix >> decMatrix.inputMatrix
        decMatrix.outputTranslate >> curve.getShape().controlPoints[follicles.index(follicle)]

    return curve


def createProjectedFollicle(locator, nurbsSurface):
    nurbsSurfaceShape = nurbsSurface.getShape()

    # Create nodes
    closestPointOnSurface = pm.createNode('closestPointOnSurface', n='%s_ClstPntOnSrfc' % locator.name())
    multiplyDivide = pm.createNode('multiplyDivide', n='%s_munDiv' % locator.name())
    follicleShape = pm.createNode('follicle', n='%s_follicleShape' % locator.name())
    follicleTransform = follicleShape.getParent()

    # Connect nodes
    locator.getShape().worldPosition >> closestPointOnSurface.inPosition
    nurbsSurfaceShape.worldSpace >> closestPointOnSurface.inputSurface

    closestPointOnSurface.parameterU >> multiplyDivide.input1X
    closestPointOnSurface.parameterV >> multiplyDivide.input1Y
    nurbsSurfaceShape.minMaxRangeU.maxValueU >> multiplyDivide.input2X
    nurbsSurfaceShape.minMaxRangeV.maxValueV >> multiplyDivide.input2Y
    multiplyDivide.operation.set(2)

    multiplyDivide.outputX >> follicleShape.parameterU
    multiplyDivide.outputY >> follicleShape.parameterV
    nurbsSurfaceShape.worldSpace >> follicleShape.inputSurface

    follicleShape.outTranslate >> follicleTransform.translate
    follicleShape.outRotate >> follicleTransform.rotate

    return follicleTransform



CURVE = 0
SURFACE = 1
def createFacialJoint(vertex, curve, surface, positionTo=CURVE):
    """
    Create a joint oriented to surface. Position can be changed with option.

    Args:
        vertex (pymel.nodetypes.Vertex): Source vertex to find closest point on curve.
        curve (pymel.nodetypes.NurbsCurve): Facial curve.
        surface (pymel.nodetypes.NurbsSurface): Skull surface.
        positionTo (str) : Nurbs geometry to attach joint. [CURVE, SURFACE]

    Returns:
        pymel.nodetypes.Joint: Created joint
    """
    joint = None

    # Get curve function
    mSels = om.MSelectionList()
    mSels.add(curve.name())
    crvDagPath = mSels.getDagPath(0)
    crvFn = om.MFnNurbsCurve(crvDagPath)

    # Get parameter of closest point on curve from vertex
    vtxPnt = om.MPoint(vertex.getPosition())
    closestPntOnCrvParm = crvFn.closestPoint(vtxPnt, space=om.MSpace.kWorld)[1]

    # Create necessary nodes
    pntOnCrvInfo = pm.createNode('pointOnCurveInfo')
    closestPntOnSurface = pm.createNode('closestPointOnSurface')
    normalizeParmDiv = pm.createNode('multiplyDivide')
    folShape = pm.createNode('follicle')
    folTrsf = folShape.getParent()
    joint = pm.createNode('joint', n='%s_jnt' % vertex.name())

    # Point on curve info connections
    curve.worldSpace >> pntOnCrvInfo.inputCurve
    pntOnCrvInfo.parameter.set(closestPntOnCrvParm)
    # pntOnCrvInfo.turnOnPercentage.set(True)

    # Closest point on surface connections
    surface.worldSpace >> closestPntOnSurface.inputSurface
    pntOnCrvInfo.position >> closestPntOnSurface.inPosition

    # Normalize parameterUV of point on surface with nurbs surface parameterUV max value
    normalizeParmDiv.operation.set(2)
    closestPntOnSurface.parameterU >> normalizeParmDiv.input1X
    closestPntOnSurface.parameterV >> normalizeParmDiv.input1Y
    surface.minMaxRangeU.maxValueU >> normalizeParmDiv.input2X
    surface.minMaxRangeV.maxValueV >> normalizeParmDiv.input2Y

    # Follicle connections
    surface.worldSpace >> folShape.inputSurface
    normalizeParmDiv.outputX >> folShape.parameterU
    normalizeParmDiv.outputY >> folShape.parameterV

    # Follicle transform connections depend on option
    if positionTo == CURVE:
        pntOnCrvInfo.position >> folTrsf.translate
    elif positionTo == SURFACE:
        folShape.outTranslate >> folTrsf.translate
    folShape.outRotate >> folTrsf.rotate

    # Parent joint to follicle transform
    folTrsf | joint
    joint.translate.set(0, 0, 0)
    joint.rotate.set(0, 0, 0)
    joint.scale.set(1, 1, 1)

    return joint


def buildFacialController(controller, railSurface, minVal, maxVal):
    """ Attach controller to nurbs surface to sliding controller. """
    controller = pm.PyNode(controller)
    railSurface = pm.PyNode(railSurface)

    pm.rebuildSurface(
        railSurface,
        rebuildType=0,
        keepRange=0,
        spansU=2,
        spansV=0,
        degreeU=3,
        degreeV=1
    )
    pm.delete(railSurface, ch=True)

    pntOnSrfcInfo = pm.createNode('pointOnSurfaceInfo', n='{}_pntOnSrfcInfo'.format(controller))
    zVecProduct = pm.createNode('vectorProduct', n='{}_zVec'.format(controller))
    matrixNode = pm.createNode('fourByFourMatrix', n='{}_matrix'.format(controller))
    decMatrix = pm.createNode('decomposeMatrix', n='{}_decMatrix'.format(controller))
    anchorGrp = pm.createNode('transform', n='{}_anchor'.format(controller))
    revGrp = pm.createNode('transform', n='{}_rev'.format(controller))
    revMul = pm.createNode('multiplyDivide', n='{}_rev_mul'.format(controller))

    controller.setLimit('translateMinX', minVal)
    controller.setLimit('translateMaxX', maxVal)

    pntOnSrfcInfo.parameterV.set(0.5)
    zVecProduct.operation.set(2)
    zVecProduct.normalizeOutput.set(True)
    revMul.input2X.set(-1.0)
    revMul.input2Y.set(-1.0)
    revMul.input2Z.set(-1.0)

    pm.parent(controller, revGrp)
    pm.parent(revGrp, anchorGrp)

    if minVal < 0:
        txRemap = pm.createNode('remapValue', n='{}_tx_remap'.format(controller))
        txRemap.inputMin.set(minVal)
        txRemap.inputMax.set(maxVal)

        zeroToNegOneRemap = pm.createNode('remapValue', n='{}_zeroToNegOne_remap'.format(controller))
        zeroToNegOneRemap.inputMin.set(0)
        zeroToNegOneRemap.inputMax.set(minVal)

        controller.tx >> txRemap.inputValue
        controller.tx >> zeroToNegOneRemap.inputValue
        txRemap.outValue >> pntOnSrfcInfo.parameterU
    else:
        controller.tx >> pntOnSrfcInfo.parameterU

    railSurface.worldSpace >> pntOnSrfcInfo.inputSurface

    pntOnSrfcInfo.normalizedNormal >> zVecProduct.input1
    pntOnSrfcInfo.normalizedTangentU >> zVecProduct.input2

    pntOnSrfcInfo.normalizedTangentUX >> matrixNode.in00
    pntOnSrfcInfo.normalizedTangentUY >> matrixNode.in01
    pntOnSrfcInfo.normalizedTangentUZ >> matrixNode.in02
    zVecProduct.outputX >> matrixNode.in10
    zVecProduct.outputY >> matrixNode.in11
    zVecProduct.outputZ >> matrixNode.in12
    pntOnSrfcInfo.normalizedNormalX >> matrixNode.in20
    pntOnSrfcInfo.normalizedNormalY >> matrixNode.in21
    pntOnSrfcInfo.normalizedNormalZ >> matrixNode.in22
    pntOnSrfcInfo.positionX >> matrixNode.in30
    pntOnSrfcInfo.positionY >> matrixNode.in31
    pntOnSrfcInfo.positionZ >> matrixNode.in32

    matrixNode.output >> decMatrix.inputMatrix

    decMatrix.outputTranslate >> anchorGrp.translate
    decMatrix.outputRotate >> anchorGrp.rotate

    controller.translate >> revMul.input1
    revMul.output >> revGrp.translate


def buildZipperLip(vertices):
    __createJoints(vertices)

def __createJoints(vertices):
    skinClst = pm.mel.eval('findRelatedSkinCluster "%s";' % vertices[0].node())
    infs = pm.skinCluster(skinClst, q=True, inf=True)

    for vtx in vertices:
        jnt = pm.createNode('joint', n=vtx.name()+'zip_jnt')
        jnt.setTranslation(vtx.getPosition())
        for inf in infs:
            weight = round(pm.skinPercent(skinClst, vtx, q=True, transform=inf), 10)
            if weight > 0.0:
                pm.pointConstraint(inf, jnt, mo=True, w=weight)


def connectFACS(facsOut, blendShape, shader):
    fOut = pm.PyNode(facsOut)
    bs = pm.PyNode(blendShape)
    shader = pm.PyNode(shader)

    actionCodings = fOut.listAttr(ud=True)
    for ac in actionCodings:
        try:
            ac >> bs.attr(ac.longName())
        except:
            pass

    # Wrinkle map 0
    fOut.browOuterUpLeft >> shader.wrinkleMap0_WrinkleGroup0X
    fOut.browOuterUpRight >> shader.wrinkleMap0_WrinkleGroup0Y
    fOut.browInnerUpLeft >> shader.wrinkleMap0_WrinkleGroup0Z
    fOut.browInnerUpRight >> shader.wrinkleMap0_WrinkleGroup0W

    fOut.cheekSquintLeft >> shader.wrinkleMap0_WrinkleGroup1X
    fOut.cheekSquintRight >> shader.wrinkleMap0_WrinkleGroup1Y
    # fOut. >> shader.wrinkleMap0_WrinkleGroup1Z
    # fOut. >> shader.wrinkleMap0_WrinkleGroup1W

    fOut.mouthSmileLeft >> shader.wrinkleMap0_WrinkleGroup2X
    fOut.mouthSmileRight >> shader.wrinkleMap0_WrinkleGroup2Y
    fOut.neckTensionLeft >> shader.wrinkleMap0_WrinkleGroup2Z
    fOut.neckTensionRight >> shader.wrinkleMap0_WrinkleGroup2W

    # Wrinkle map 1
    # fOut. >> shader.wrinkleMap1_WrinkleGroup0X
    # fOut. >> shader.wrinkleMap1_WrinkleGroup0Y
    # fOut. >> shader.wrinkleMap1_WrinkleGroup0Z
    # fOut. >> shader.wrinkleMap1_WrinkleGroup0W

    fOut.noseSneerLeft >> shader.wrinkleMap1_WrinkleGroup1X
    fOut.noseSneerRight >> shader.wrinkleMap1_WrinkleGroup1Y
    # fOut. >> shader.wrinkleMap1_WrinkleGroup1Z
    # fOut. >> shader.wrinkleMap1_WrinkleGroup1W

    fOut.mouthStretchLeft >> shader.wrinkleMap1_WrinkleGroup2X
    fOut.mouthStretchRight >> shader.wrinkleMap1_WrinkleGroup2Y
    fOut.mouthPuckerLeft >> shader.wrinkleMap1_WrinkleGroup2Z
    fOut.mouthPuckerRight >> shader.wrinkleMap1_WrinkleGroup2W

    # Wrinkle map 2
    fOut.browDownLeft >> shader.wrinkleMap2_WrinkleGroup0X
    fOut.browDownRight >> shader.wrinkleMap2_WrinkleGroup0Y
    # fOut. >> shader.wrinkleMap2_WrinkleGroup0Z
    # fOut. >> shader.wrinkleMap2_WrinkleGroup0W

    fOut.eyeSquintLeft >> shader.wrinkleMap2_WrinkleGroup1X
    fOut.eyeSquintRight >> shader.wrinkleMap2_WrinkleGroup1Y
    fOut.mouthUpperShrugLeft >> shader.wrinkleMap2_WrinkleGroup1Z
    fOut.mouthUpperShrugRight >> shader.wrinkleMap2_WrinkleGroup1W

    fOut.mouthFrownLeft >> shader.wrinkleMap2_WrinkleGroup2X
    fOut.mouthFrownRight >> shader.wrinkleMap2_WrinkleGroup2Y
    fOut.mouthLowerShrugLeft >> shader.wrinkleMap2_WrinkleGroup2Z
    fOut.mouthLowerShrugRight >> shader.wrinkleMap2_WrinkleGroup2W


def setROMPose(numPose=50):
    for i in range(numPose):
        pm.env.time = i * 10
        pm.setKeyframe()


# -----------------------------------------
# Metahuman Facial retargeting
# -----------------------------------------

if __name__ == '__main__':
    # Create skin joint
    pm.undoInfo(openChunk=True)
    skJnts = []
    for outJnt in pm.selected():
        skJnt = pm.duplicate(outJnt, n=outJnt.replace('_out', ''))[0]
        skJntParent = pm.PyNode(outJnt.getParent().replace('_out', ''))
        skJntParent | skJnt
        outJnt.translate >> skJnt.translate
        outJnt.rotate >> skJnt.rotate
        outJnt.scale >> skJnt.scale
        skJnts.append(skJnt)
    pm.select(skJnts, r=True)
    pm.undoInfo(closeChunk=True)


    # Connect to existing target shape
    bsOut = pm.PyNode('bs_out')
    deltaBS = pm.PyNode('deltaBlendshape5')
    for attr in bsOut.listAttr(ud=True, keyable=True):
        exprName = attr.attrName()
        if deltaBS.hasAttr(exprName):
            attr >> deltaBS.attr(exprName)


    ### Joint Based Facial Rigging ###

    # Eyelid ikh locator align #
    import pymel.core as pm

    eyelidLocs = pm.ls(sl=True)
    for loc in eyelidLocs:

        ikh = loc.getChildren(type='ikHandle')[0]
        ikh.setParent(w=True)

        locZeroGrp = loc.getParent(generations=2)
        locZeroGrp.rotate.set(0,0,0)

        if 'lower' in loc.name():
           locZeroGrp.scaleY.set(-1)

        if 'R_' in loc.name():
            locZeroGrp.scaleX.set(-1)

        ikh.setParent(loc)

    # Locator zero group scaleX set to -1 #
    locators = pm.ls(sl=True)
    for locator in locators:
        locChild = locator.getChildren(type='transform')[0]
        locChild.setParent(world=True)

        zeroGrpName = '%s_zero' % locator.name()
        pm.setAttr('%s.scaleX' % zeroGrpName, -1)

        locChild.setParent(locator)


    # Mirror zero group #
    zeroGrps = pm.ls(sl=True)
    searchStr = 'lf_'
    replaceStr = 'R_'

    for zeroGrp in zeroGrps:
        zeroGrpTrans = zeroGrp.getTranslation()
        zeroGrpRotation = zeroGrp.getRotation()
        zeroGrpScale = zeroGrp.getScale()

        otherSideZeroGrpName = zeroGrp.replace(searchStr, replaceStr)
        otherSideZeroGrp = pm.PyNode(otherSideZeroGrpName)

        otherSideZeroGrp.setTranslation([-zeroGrpTrans.x, zeroGrpTrans.y, zeroGrpTrans.z])
        otherSideZeroGrp.setRotation([zeroGrpRotation.x, -zeroGrpRotation.y, -zeroGrpRotation.z])
        otherSideZeroGrp.setScale([zeroGrpScale[0], zeroGrpScale[1], zeroGrpScale[2]])

    ### Facial Secondary ###

    # Eyelid #
    import pymel.core as pm
    from takTools.common import tak_misc

    # Normal eyelid
    selJnts = pm.selected()
    for jnt in selJnts:
        name = jnt.getChildren()[0].rsplit('_jnt')[0]

        ikh = pm.ikHandle(sj=jnt, ee=jnt.getChildren()[0], solver='ikSCsolver', n=name+'_ikh')[0]
        ikhWsPos = pm.xform(ikh, q=True, ws=True, t=True)

        loc = pm.spaceLocator(n=name+'_loc')
        loc.translate.set(ikhWsPos)
        ikh.setParent(loc)
        tak_misc.doGroup(loc.name(), '_zero')
        tak_misc.doGroup(loc.name(), '_auto')

    # Zipper Lip #
    import pymel.core as pm

    # Distribute constraint weight #
    selJnts = sorted(pm.ls(sl=True), reverse=True)
    segment = len(selJnts)-1
    fullWeight = 1.0
    increment = fullWeight/len(selJnts)

    weight = 1
    for jnt in selJnts:
        weight -= increment
        parentConstraintNode = jnt.getChildren()[0]
        parentConstraintNode.jaw_lockW0.set(weight*weight)


    # Zipper Lip Joints rampValuesNode Set Up #
    import pymel.core as pm
    jnts = pm.selected()

    driverJnts = ['jaw_ctrl', 'jaw_lock_jnt']
    drivenAttr = 'jaw_ctrlW1'

    rampValsNode = pm.createNode('rampValuesNode')
    rampValsNode.inValue.set(1.0)
    rampValsNode.numSamples.set(len(jnts))
    rampValsNode.ramp01[0].ramp01_Interp.set(3)
    rampValsNode.ramp01[0].ramp01_Position.set(0)
    rampValsNode.ramp01[0].ramp01_FloatValue.set(0)
    rampValsNode.ramp01[1].ramp01_Interp.set(3)
    rampValsNode.ramp01[1].ramp01_Position.set(0.6)
    rampValsNode.ramp01[1].ramp01_FloatValue.set(0.4)
    rampValsNode.ramp01[2].ramp01_Interp.set(3)
    rampValsNode.ramp01[2].ramp01_Position.set(1.0)
    rampValsNode.ramp01[2].ramp01_FloatValue.set(1.0)

    for jnt in jnts:
        parentConst = pm.parentConstraint(driverJnts, jnt, mo=True)
        rampValsNode.outValues[jnts.index(jnt)] >> parentConst.attr(drivenAttr)

    # Copy left constraint weight to right #
    selJnts = pm.ls(sl=True)
    for jnt in selJnts:
        parentConstraintNode = jnt.getChildren()[0]
        weightList = parentConstraintNode.getWeightAliasList()
        for weight in weightList:
            val = weight.get()
            oppositeWeight = pm.PyNode(weight.name().replace('lf_', 'R_'))
            oppositeWeight.set(val)

    # Distribute SDK End Value #
    zipperLipJnts = pm.selected()
    zipperLipJnts.sort(key=lambda x:x.tx.get(), reverse=True)
    maxValue = 10.0
    increment = maxValue / len(zipperLipJnts)
    endValue = 0
    for jnt in zipperLipJnts:
        parentConst = jnt.getChildren(type='parentConstraint')[0]
        weightList = parentConst.getWeightAliasList()
        for weight in weightList:
            animCurve = weight.connections(type='animCurve')[0]
            animCurve.setUnitlessInput(1, endValue)
        endValue += increment

    # Create corner locator
    locName = 'lf_outerEyelid_clst_loc'

    sels = pm.selected()

    loc = pm.spaceLocator(n=locName)

    translate = pm.xform(sels[0], q=True, t=True, ws=True)
    scale = sels[0].scale.get()
    pm.xform(loc, t=translate, ws=True)
    loc.scale.set(scale)

    tak_misc.doGroup(str(loc), '_zero')
    tak_misc.doGroup(str(loc), '_auto')

    pm.parent(sels, loc)
    pm.hide(sels)

    # Replace tertiary facial control attaching mesh #
    newAttachMesh = pm.PyNode('lod02_face')
    tertiaryCtrls = pm.selected()
    attachedMesh = tertiaryCtrls[0].getParent(3).translate.connections(destination=False, type='transform')[0].translate.listConnections(destination=False, type='follicle')[0].inputMesh.listConnections(type='mesh', shapes=True)[0]
    for fol in attachedMesh.worldMesh[0].connections(source=False, type='follicle', shapes=True):
        newAttachMesh.getShape().worldMesh[0] >> fol.inputMesh

    # point on poly constraint method
    newAttachMesh = pm.PyNode('lod02_face')
    tertiaryCtrls = pm.selected()
    attachedMesh = tertiaryCtrls[0].getParent(2).translateX.connections(destination=False, type='pointOnPolyConstraint')[0].target.listConnections(type='mesh', shapes=True)[0]
    for pntOnPolyCnst in attachedMesh.worldMesh[0].connections(source=False, type='pointOnPolyConstraint', shapes=True):
        newAttachMesh.getShape().worldMesh[0] >> pntOnPolyCnst.target[0].targetMesh

    # Set left target's rampBlendShape.weight[2]
    lfRampBSList = [meshTrsf.getShape().inMesh.connections()[0] for meshTrsf in pm.selected() if meshTrsf.getShape().inMesh.connections()]
    for rampBS in lfRampBSList:
        rampBS.weightCurveRamp[2].weightCurveRamp_FloatValue.set(1.0)


    for sel in pm.selected():
        pntOnCrvInfo = sel.connections(type='pointOnCurveInfo', d=False)[0]
        decMtrx = sel.connections(type='decomposeMatrix', s=False)[0]
        closestPntOnSrfc = decMtrx.connections(type='closestPointOnSurface', s=False)[0]

        pntOnCrvInfo.position >> closestPntOnSrfc.inPosition

        pm.delete(sel)


    # Create curve on surface
    locators = pm.selected()
    surface = pm.PyNode('eyeball_R_surface')
    createProjectedCurve(locators, surface, name='lowEyelid_R_crv')

    # Create facial joints
    vertices = pm.selected(fl=True)
    name = 'lowEyelid_R'
    curve = pm.PyNode('%s_crv' % name)
    surface = pm.PyNode('eyeball_R_surface')
    i=1
    for vtx in vertices:
        createFacialJoint(vtx, curve, surface, name='%s_%02d_jnt' % (name, i), positionTo='surface')
        i += 1


    # Match surface cvs
    import takRiggingToolkit as trt

    source = pm.PyNode('eyeball_L_surface')
    target = pm.PyNode('eyeball_R_surface')
    trt.utils.general.matchSurfaceCVs(source, target, mirror=True)

