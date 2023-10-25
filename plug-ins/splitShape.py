"""
Author: LEE SANGTAK
Contact: chst27@gmail.com
"""

from maya import OpenMaya
from maya import OpenMayaMPx

VENDOR = 'Tak'
VERSION = '1.0'

class SplitShape(OpenMayaMPx.MPxCommand):
    name = 'splitShape'

    numberOfDivisionShortFlag = '-nd'
    numberOfDivisionLongFlag = '-numberOfDivision'

    def __init__(self):
        super(SplitShape, self).__init__()

        self.baseGeo = None
        self.targetGeo = None
        self.numOfDivision = 2
        self.dgMod = OpenMaya.MDGModifier()
        self.dagMod = OpenMaya.MDagModifier()
        self.createdNodes = OpenMaya.MObjectArray()

    @staticmethod
    def creator():
        return OpenMayaMPx.asMPxPtr(SplitShape())

    @staticmethod
    def newSyntax():
        syntax = OpenMaya.MSyntax()

        syntax.addArg(OpenMaya.MSyntax.kString)
        syntax.addArg(OpenMaya.MSyntax.kString)
        syntax.addFlag(SplitShape.numberOfDivisionShortFlag, SplitShape.numberOfDivisionLongFlag, OpenMaya.MSyntax.kLong)

        syntax.setObjectType(OpenMaya.MSyntax.kSelectionList, 2, 2)
        syntax.useSelectionAsDefault(True)

        return syntax

    def parseArgs(self, args):
        argData = OpenMaya.MArgDatabase(self.syntax(), args)

        try:
            self.baseGeo = argData.commandArgumentString(0)
            self.targetGeo = argData.commandArgumentString(1)
        except:
            self.baseGeo = self.getArgFromSelection(0, argData)
            self.targetGeo = self.getArgFromSelection(1, argData)

        if argData.isFlagSet(SplitShape.numberOfDivisionShortFlag):
            self.numOfDivision = argData.flagArgumentInt(SplitShape.numberOfDivisionShortFlag, 0)

    def doIt(self, args):
        self.parseArgs(args)
        self.redoIt()

    def isUndoable(self):
        return True

    def redoIt(self):
        dgFn = OpenMaya.MFnDependencyNode()
        dagFn = OpenMaya.MFnDagNode()

        # Get initialShadingGroup set
        initialShadingGrp = OpenMaya.MObject()
        selLs = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getSelectionListByName('initialShadingGroup', selLs)
        selLs.getDependNode(0, initialShadingGrp)
        initShadingGrpSet = OpenMaya.MFnSet(initialShadingGrp)

        # Create rampBlendShape node and find plugs
        try:
            rampBS = self.dgMod.createNode('rampBlendShape')
        except:
            raise RuntimeError('rampBlendShape plug-in is needed')
        dgFn.setObject(rampBS)
        rampBSBaseGeoPlug = dgFn.findPlug('baseGeo')
        rampBSTargetGeoPlug = dgFn.findPlug('targetGeo')
        rampBSOutGeoPlug = dgFn.findPlug('outGeo')
        rampBSCenterPlug = dgFn.findPlug('center')
        rampBSRangePlug = dgFn.findPlug('range')
        self.createdNodes.append(rampBS)

        # Connect baseGeo.outmesh to rampBlendshape node
        baseGeoDagPath = SplitShape.getDagPathFromString(self.baseGeo)
        baseGeoDagPath.extendToShapeDirectlyBelow(0)
        dagFn.setObject(baseGeoDagPath)
        baseGeoOutMeshPlug = dagFn.findPlug('outMesh')
        self.dgMod.connect(baseGeoOutMeshPlug, rampBSBaseGeoPlug)

        # Connect targetGeo.outMesh to rampBlendShape node
        targetGeoDagPath = SplitShape.getDagPathFromString(self.targetGeo)
        targetGeoDagPath.extendToShapeDirectlyBelow(0)
        dagFn.setObject(targetGeoDagPath)
        targetGeoOutMeshPlug = dagFn.findPlug('outMesh')
        self.dgMod.connect(targetGeoOutMeshPlug, rampBSTargetGeoPlug)

        outGeo = self.dagMod.createNode('mesh')
        self.dagMod.renameNode(outGeo, 'outGeo#')
        self.dagMod.doIt()
        initShadingGrpSet.addMember(outGeo)
        self.createdNodes.append(outGeo)

        outGeoPath = OpenMaya.MDagPath()
        outGeoTransformPath = outGeoPath
        OpenMaya.MDagPath().getAPathTo(outGeo, outGeoPath)
        outGeoPath.extendToShapeDirectlyBelow(0)
        dagFn.setObject(outGeoPath)
        outGeoInMeshPlug = dagFn.findPlug('inMesh')
        self.dgMod.connect(rampBSOutGeoPlug, outGeoInMeshPlug)

        self.dgMod.doIt()

        dagFn.setObject(baseGeoDagPath)
        baseGeoBoundingBox = dagFn.boundingBox()
        width = baseGeoBoundingBox.width()
        divisionRange = width / (self.numOfDivision - 1)
        startCenter = -(width / 2)

        rampBSRangePlug.setDouble(divisionRange)
        dagFn.setObject(outGeoTransformPath)
        for i in xrange(self.numOfDivision):
            rampBSCenterPlug.setDouble(startCenter)
            dupObj = dagFn.duplicate()
            self.createdNodes.append(dupObj)
            initShadingGrpSet.addMember(dupObj)
            startCenter += divisionRange

    def undoIt(self):
        for i in xrange(self.createdNodes.length()):
            self.dagMod.deleteNode(self.createdNodes[i])

    @staticmethod
    def getArgFromSelection(index, argData):
        selObjs = OpenMaya.MSelectionList()
        argData.getObjects(selObjs)

        dagPath = OpenMaya.MDagPath()
        selObjs.getDagPath(index, dagPath)
        return dagPath.partialPathName()

    @staticmethod
    def getDagPathFromString(string):
        selList = OpenMaya.MSelectionList()
        selList.add(string)

        dagPath = OpenMaya.MDagPath()
        selList.getDagPath(0, dagPath)

        return dagPath

    @staticmethod
    def getMObjectFromString(string):
        selList = OpenMaya.MSelectionList()
        selList.add(string)

        mObj = OpenMaya.MObject()
        selList.getDependNode(0, mObj)

        return mObj


def initializePlugin(mObj):
    pluginFn = OpenMayaMPx.MFnPlugin(mObj, VENDOR, VERSION)
    try:
        pluginFn.registerCommand(SplitShape.name, SplitShape.creator, SplitShape.newSyntax)
    except:
        raise RuntimeError('Failed to register command: %s' % SplitShape.name)


def uninitializePlugin(mObj):
    pluginFn = OpenMayaMPx.MFnPlugin(mObj)
    try:
        pluginFn.deregisterCommand(SplitShape.name)
    except:
        raise RuntimeError('Failed to deregister command: %s' % SplitShape.name)
