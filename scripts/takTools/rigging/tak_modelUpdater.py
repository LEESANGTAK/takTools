"""
Author: Sangtak Lee
Contact: chst27@gmail.com

Description:
This script is for updating new version model to the rig.

Test Code:
import modelUpdater as mu
reload(mu)

mdlPath = r'P:\1802_D51\4.Asset\prp\airinStaff\mdl\release\r002\prp_airinStaff_mdl_r002.ma'
mdlObj = mu.Model(mdlPath)

mdlUpdater = mu.ModelUpdater(mdlObj)
mdlUpdater.main()
"""


import pymel.core as pm
from ..common import tak_lib
from ..common import tak_misc
from ..modeling import tak_cleanUpModel


class Model(object):
    def __init__(self, filePath, namespace='temp'):
        super(Model, self).__init__()
        self.filePath = filePath
        self.namespace = namespace
        self.lod03Grp = namespace+':lod03_GRP'
        self.meshes = None


class ModelUpdater(object):
    oldLod02Grp = None
    model = None
    lod03Grp = None
    lod02Grp = None

    def __init__(self, modelObj, searchStr, replaceStr):
        super(ModelUpdater, self).__init__()
        # Input Attributes
        self.model = modelObj
        self.searchStr = searchStr
        self.replaceStr = replaceStr
        # Private Attributes
        self.lod03Grp = pm.PyNode('lod03_GRP') if pm.objExists('lod03_GRP') else None
        self.lod02Grp = pm.PyNode('lod02_GRP') if pm.objExists('lod02_GRP') else None
        self.wrapFailMeshes = []
        self.notCopySkinMeshes = []

    def main(self):
        self.cleanupOldModel()
        self.importModel()
        self.cleanupNewModel()
        self.createLod02()
        self.connectPlace3dTexture()
        self.connectBlendshape()
        self.copySkin()
        self.connectFfd()
        self.createWrap()
        self.createDeltaMush()
        self.createTension()
        self.createTransferAttr()
        self.connectTransform()
        self.connectFollicle()
        connectRivet()
        self.showResult()

    def cleanupOldModel(self):
        pm.delete(self.lod03Grp.getChildren())
        if pm.objExists('old_lod02_GRP'):
            pm.delete('old_lod02_GRP')
        self.oldLod02Grp = pm.createNode('transform', n='old_lod02_GRP')
        [node.setParent(self.oldLod02Grp) for node in self.lod02Grp.getChildren()]
        for node in self.oldLod02Grp.getChildren(ad=True, path=True, type='transform'):
            nodeBaseName = node.split('|')[-1]
            node.rename('old_' + nodeBaseName)

    def importModel(self):
        pm.importFile(self.model.filePath, namespace=self.model.namespace)
        self.model.meshes = pm.ls(pm.listRelatives(self.model.lod03Grp, ad=True, ni=True), type='mesh')

    def cleanupNewModel(self):
        newLod03Grp = pm.PyNode('%s:lod03_GRP' % (self.model.namespace))
        [child.setParent(self.lod03Grp) for child in newLod03Grp.getChildren()]
        pm.delete('%s:root' % (self.model.namespace))

        pm.namespace(force=True, moveNamespace=(':%s' % (self.model.namespace), ':'))
        pm.namespace(removeNamespace=self.model.namespace)

    def createLod02(self):
        tempLod02Grp = tak_lib.duplicateRename(self.lod03Grp, prefix='lod02_')
        lod02Meshes = tempLod02Grp.getChildren(ad=True, type='mesh', ni=True)

        pm.select([mesh.getParent() for mesh in lod02Meshes], r=True)
        tak_misc.dupMatAndAssign()

        pm.select(lod02Meshes, r=True)
        pm.mel.eval('setDisplaySmoothness 1;')
        pm.mel.eval('SoftPolyEdgeElements 1;')

        pm.select(tempLod02Grp, hi=True, r=True)
        tak_cleanUpModel.allInOne()

        [child.setParent(self.lod02Grp) for child in tempLod02Grp.getChildren()]
        pm.delete(tempLod02Grp)

    def connectPlace3dTexture(self):
        pm.delete(self.lod02Grp.getChildren(ad=True, type='place3dTexture'))

        oldMdlPlace3dTexs = [getPlace3dTex(mesh) for mesh in self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True) if getPlace3dTex(mesh) != None]
        newMdlPlace3dTexs = [getPlace3dTex(mesh) for mesh in self.lod02Grp.getChildren(ad=True, type='mesh', ni=True) if getPlace3dTex(mesh) != None]

        for oldMdlPlace3dTex in oldMdlPlace3dTexs:
            baseName = oldMdlPlace3dTex.replace('old_lod02_', '')
            matchingNewPlace3dTex = getMatchingNode(
                                        baseName,
                                        newMdlPlace3dTexs
                                    )
            if matchingNewPlace3dTex:
                parentCnsts = list(set(oldMdlPlace3dTex.connections(d=False, type='parentConstraint')))
                pointCnsts = list(set(oldMdlPlace3dTex.connections(d=False, type='pointConstraint')))
                orientCnsts = list(set(oldMdlPlace3dTex.connections(d=False, type='orientConstraint')))
                scaleCnsts = list(set(oldMdlPlace3dTex.connections(d=False, type='scaleConstraint')))
                oldParent = oldMdlPlace3dTex.getParent()
                oldParentParentCnsts = list(set(oldParent.connections(d=False, type='parentConstraint')))
                oldParentScaleCnsts = list(set(oldParent.connections(d=False, type='scaleConstraint')))

                newParent = oldParent.replace('old_', '')
                matchingNewPlace3dTex.setParent(newParent)
                if parentCnsts:
                    pm.parentConstraint(
                        parentCnsts[0].target[0].targetParentMatrix.connections()[0],
                        matchingNewPlace3dTex,
                        mo=True
                    )
                if pointCnsts:
                    pm.pointConstraint(
                        pointCnsts[0].target[0].targetParentMatrix.connections()[0],
                        matchingNewPlace3dTex,
                        mo=True
                    )
                if orientCnsts:
                    pm.orientConstraint(
                        orientCnsts[0].target[0].targetParentMatrix.connections()[0],
                        matchingNewPlace3dTex,
                        mo=True
                    )
                if scaleCnsts:
                    pm.scaleConstraint(
                        scaleCnsts[0].target[0].targetParentMatrix.connections()[0],
                        matchingNewPlace3dTex,
                        mo=True
                    )
                if oldParentParentCnsts:
                    pm.parentConstraint(
                        oldParentParentCnsts[0].target[0].targetParentMatrix.connections()[0],
                        newParent,
                        mo=True
                    )
                if oldParentScaleCnsts:
                    pm.scaleConstraint(
                        oldParentScaleCnsts[0].target[0].targetParentMatrix.connections()[0],
                        newParent,
                        mo=True
                    )

                matchingNewPlace3dTex.rename('lod02_'+baseName)

    def copySkin(self):
        [attr.set(0) for attr in pm.ls('*.geometryVis')]
        for oldMesh in self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True):
            newMesh = oldMesh.replace(self.searchStr, self.replaceStr)
            if not pm.objExists(newMesh):
                self.notCopySkinMeshes.append(oldMesh)
                continue
            try:
                tak_lib.copySkin(oldMesh, pm.PyNode(newMesh))
            except:
                self.notCopySkinMeshes.append(oldMesh)

    def copyMaterial(self):
        self.notCopiedMatMeshes = []
        for oldMesh in self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True):
            newMesh = oldMesh.replace(self.searchStr, self.replaceStr)
            if not pm.objExists(newMesh):
                self.notCopiedMatMeshes.append(oldMesh)
                continue
            try:
                tak_lib.copyMat(oldMesh, pm.PyNode(newMesh))
            except:
                self.notCopiedMatMeshes.append(oldMesh)

    def connectBlendshape(self):
        geos = self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True)
        blendShapes = getDeformers(geos, deformerType='blendShape')
        if not blendShapes:
            return
        for blendShape in blendShapes:
            targets = [target for target in pm.listAttr(blendShape.weight, multi=True) if 'weight' not in target and pm.objExists(target)]
            if not targets:
                continue
            bsBaseObjs = blendShape.getBaseObjects()
            if len(bsBaseObjs) == 1:
                oldBaseObject = bsBaseObjs[0].getParent()
                newBlendshape = pm.blendShape(targets, oldBaseObject.replace(self.searchStr, self.replaceStr), frontOfChain=True, topologyCheck=False)[0]
            else:  # In case blendshape using group like facial group
                i = 1
                findRoot = False
                while not findRoot:
                    try:
                        oldBaseObject = bsBaseObjs[0].getParent(generations=i)
                        newBlendshape = pm.blendShape(targets, oldBaseObject.replace(self.searchStr, self.replaceStr), frontOfChain=True, topologyCheck=False)[0]
                        findRoot = True
                    except RuntimeError:  # When fail to blendshape try to next parent group
                        i += 1

            for target in targets:
                oldBsTargetVal = blendShape.attr(target).get()
                newBlendshape.attr(target).set(oldBsTargetVal)
                inputs = blendShape.attr(target).connections(plugs=True)
                if inputs:
                    inputs[0] >> newBlendshape.attr(target)

    def connectFfd(self):
        geos = self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True)
        ffds = getDeformers(geos, deformerType='ffd')
        if not ffds:
            return
        for ffd in ffds:
            ffdSet = ffd.connections(type='objectSet', s=False)[0]
            meshes = [mesh.replace(self.searchStr, self.replaceStr) for mesh in ffdSet.connections(type='mesh', d=False)]
            pm.sets(ffdSet, add=meshes)

    def createWrap(self):
        geos = self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True)
        wraps = getDeformers(geos, deformerType='wrap')
        if not wraps:
            return
        for wrap in wraps:
            oldDrivenMesh = wrap.outputGeometry.listHistory(future=True, type='mesh')[0]
            newDrivenMesh = oldDrivenMesh.replace(self.searchStr, self.replaceStr)
            oldDriverMesh = wrap.driverPoints.connections()[0]
            newDriverMesh = oldDriverMesh.replace(self.searchStr, self.replaceStr)
            if pm.objExists(newDrivenMesh):
                newDrivenMesh = pm.PyNode(newDrivenMesh)
                pm.select(newDrivenMesh, newDriverMesh, r=True)
                pm.mel.eval('CreateWrap;')
                newWrap = newDrivenMesh.inMesh.connections()[0]
                for attr in wrap.listAttr(keyable=True):
                    attrName = attr.attrName()
                    newWrap.attr(attrName).set(attr.get())
            else:
                self.wrapFailMeshes.append(oldDrivenMesh)

    def createDeltaMush(self):
        geos = self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True)
        deltaMushes = getDeformers(geos, deformerType='deltaMush')
        if not deltaMushes:
            return
        for mush in deltaMushes:
            deltaMushSet = mush.connections(type='objectSet', s=False)[0]
            meshes = list(set([mesh.replace(self.searchStr, self.replaceStr) for mesh in deltaMushSet.connections(type='mesh', d=False)]))
            pm.select(meshes, r=True)
            newDeltaMush = pm.deltaMush()
            for attr in mush.listAttr(keyable=True):
                if 'weight' in attr.name():
                    continue
                newDeltaMush.attr(attr.attrName()).set(attr.get())
                attrConnections = attr.connections(d=False, plugs=True)
                if attrConnections:
                    for connection in attrConnections:
                        connection >> newDeltaMush.attr(attr.attrName())

    def createTension(self):
        geos = self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True)
        tensions = getDeformers(geos, deformerType='tension')
        if not tensions:
            return
        for tensionNode in tensions:
            tensionSet = tensionNode.connections(type='objectSet', s=False)[0]
            meshes = list(set([mesh.replace(self.searchStr, self.replaceStr) for mesh in tensionSet.connections(type='mesh', d=False)]))
            pm.select(meshes, r=True)
            newTension = pm.tension()
            for attr in tensionNode.listAttr(keyable=True):
                if 'weight' in attr.name():
                    continue
                newTension.attr(attr.attrName()).set(attr.get())
                attrConnections = attr.connections(d=False, plugs=True)
                if attrConnections:
                    for connection in attrConnections:
                        connection >> newTension.attr(attr.attrName())

    def createTransferAttr(self):
        for mesh in self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True):
            transferAttrNodes = mesh.listHistory(ag=True, ac=True, type='transferAttributes')
            if transferAttrNodes:
                oldTransferAttrNode = mesh.listHistory(ag=True, ac=True, type='transferAttributes')[0]
                newTransferNode = pm.duplicate(transferAttrNodes)[0]

                inputs = oldTransferAttrNode.source.connections(plugs=True)
                outputs = oldTransferAttrNode.outputGeometry.connections(plugs=True)

                for input in inputs:
                    pm.PyNode(input.replace(self.searchStr, self.replaceStr)) >> newTransferNode.source[0]
                for output in outputs:
                    newTransferNode.outputGeometry[0] >> pm.PyNode(output.replace(self.searchStr, self.replaceStr))

    def connectTransform(self):
        for oldTrsf in self.oldLod02Grp.getChildren(ad=True, type='transform'):
            attrs = oldTrsf.listAttr(keyable=True)
            for attr in attrs:
                inputs = attr.connections(d=False, plugs=True)
                if inputs:
                    newAttr = attr.replace('old_', '')
                    if pm.objExists(newAttr):
                        inputs[0] >> newAttr

    def showResult(self):
        if self.notCopySkinMeshes:
            pm.warning('Not skin copied meshes: \n' + str(self.notCopySkinMeshes))
        if self.wrapFailMeshes:
            pm.warning('Fail wraped meshes: \n' + str(self.wrapFailMeshes))
        if self.notCopiedMatMeshes:
            pm.warning('Fail to copy material meshes: \n' + str(self.notCopiedMatMeshes))

    def connectFollicle(self):
        for oldMesh in self.oldLod02Grp.getChildren(ad=True, type='mesh', ni=True):
            newMeshName = oldMesh.replace('old_', '')
            newMesh = pm.PyNode(newMeshName) if pm.objExists(newMeshName) else None
            follicles = oldMesh.outMesh.connections(s=False, type='follicle')
            if follicles:
                for fol in follicles:
                    if not newMesh:
                        oldMesh.outMesh // fol.inputMesh
                    else:
                        newMesh.outMesh >> fol.inputMesh


def getDeformers(geos, deformerType):
    """
    Get all deformers for given type.

    Args:
        geos (list<geometry>): Geometry list.
        deformerType (str): Deformer type name.
    """
    allDeformers = []
    for geo in geos:
        deformers = tak_lib.getAllDeformers(geo.name())
        if not deformers:
            continue
        allDeformers.extend(deformers)
    results = list(set([pm.PyNode(deformer) for deformer in allDeformers if pm.nodeType(deformer) == deformerType]))
    return results


def connectRivet(searchStr='old_', replaceStr=''):
    for node in pm.ls(type='curveFromMeshEdge'):
        inputPlug = node.inputMesh.connections(plugs=True)[0]
        pm.PyNode(inputPlug.replace(searchStr, replaceStr)) >> node.inputMesh


def getPlace3dTex(mesh):
    place3dTexs = []
    try:
        shadingEngine = mesh.connections(s=False, type='shadingEngine')[0]
        place3dTexs = shadingEngine.listHistory(type='place3dTexture')
    except:
        pass
    if place3dTexs:
        return place3dTexs[0]


def getMatchingNode(name, nodes):
    for node in nodes:
        if name in node.name():
            return node
        else:
            continue


class UI(object):
    def __init__(self):
        super(UI, self).__init__()
        self.__winName = 'modelUpdaterWin'
        self.__mdlUpdater = None
        self.mdlPathWdg = None
        self.searchStrWdg = None
        self.replaceStrWdg = None
        self.__build()

    def __build(self):
        if pm.window(self.__winName, q=True, exists=True):
            pm.deleteUI(self.__winName)

        pm.window(self.__winName, title='Model Updater', mnb=False, mxb=False)

        pm.columnLayout(adj=True)
        pm.text('Match rig pose to model before update.')
        self.mdlPathWdg = pm.textFieldButtonGrp(
                                    label='Model Path: ',
                                    buttonLabel='...',
                                    columnWidth=[(1, 70)],
                                    bc=self._getPath
                                )
        self.searchStrWdg = pm.textFieldGrp(label='Search String: ', text='old_', columnWidth=[(1, 80), (2, 50)])
        self.replaceStrWdg = pm.textFieldGrp(label='Replace String: ', text='', columnWidth=[(1, 80), (2, 50)])
        pm.button(label='Import Model', c=self.__importMdl)
        pm.button(label='Place 3D Texture', c=lambda x: self.__mdlUpdater.connectPlace3dTexture())
        pm.button(label='Blend Shape', c=lambda x: self.__mdlUpdater.connectBlendshape())
        pm.button(label='Skin', c=lambda x: self.__mdlUpdater.copySkin())
        pm.button(label='FFD', c=lambda x: self.__mdlUpdater.connectFfd())
        pm.button(label='Wrap', c=lambda x: self.__mdlUpdater.createWrap())
        pm.button(label='Delta Mush', c=lambda x: self.__mdlUpdater.createDeltaMush())
        pm.button(label='Tension', c=lambda x: self.__mdlUpdater.createTension())
        pm.button(label='Transfer Attributes', c=lambda x: self.__mdlUpdater.createTransferAttr())
        pm.button(label='Transform Attributes', c=lambda x: self.__mdlUpdater.connectTransform())
        pm.button(label='Follicle', c=lambda x: self.__mdlUpdater.connectFollicle())
        pm.button(label='Rivet', c=lambda x: connectRivet())
        pm.button(label='Material', c=lambda x: self.__mdlUpdater.copyMaterial())
        pm.button(label='Show Result', c=lambda x: self.__mdlUpdater.showResult())
        pm.button(label='All in One', c=self.__allInOne)

        pm.window(self.__winName, e=True, w=10, h=10)
        pm.showWindow(self.__winName)

    def _getPath(self):
        mdlPath = pm.fileDialog2(dialogStyle=1, fileMode=1, fileFilter='Maya Files (*.ma *.mb)')[0]
        pm.textFieldButtonGrp(self.mdlPathWdg, e=True, text=mdlPath)

    def __importMdl(self, *args):
        mdlPath = pm.textFieldButtonGrp(self.mdlPathWdg, q=True, text=True)
        searchStr = pm.textFieldGrp(self.searchStrWdg, q=True, text=True)
        replaceStr = pm.textFieldGrp(self.replaceStrWdg, q=True, text=True)
        mdlObj = Model(mdlPath)
        self.__mdlUpdater = ModelUpdater(mdlObj, searchStr, replaceStr)
        self.__mdlUpdater.cleanupOldModel()
        self.__mdlUpdater.importModel()
        self.__mdlUpdater.cleanupNewModel()
        self.__mdlUpdater.createLod02()

    def __allInOne(self, *args):
        self.importModel()
        self.__mdlUpdater.main()
