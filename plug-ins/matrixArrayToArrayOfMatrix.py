"""
pluginName = 'matrixArrayToArrayOfMatrix'
pm.loadPlugin(pluginName)
aomNode = pm.createNode('matrixArrayToArrayOfMatrix')
pm.PyNode('MASH1').matrixOutPP >> aomNode.inMatrixArray

aomNode.inMatrixArray.disconnect()
pm.delete(pm.ls(type='matrixArrayToArrayOfMatrix'))
pm.flushUndo()
pm.unloadPlugin(pluginName)
"""

from maya import OpenMayaMPx
from maya import OpenMaya


class MatrixArrayToArrayOfMatrix(OpenMayaMPx.MPxNode):
    NAME = 'matrixArrayToArrayOfMatrix'
    ID = OpenMaya.MTypeId(0x00002739)

    IN_MATRIX_ARRAY = OpenMaya.MObject()
    OUT_ARRAY_OF_MATRIX = OpenMaya.MObject()

    def __init__(self):
        super(MatrixArrayToArrayOfMatrix, self).__init__()

    @classmethod
    def nodeCreator(cls):
        return OpenMayaMPx.asMPxPtr(cls())

    @classmethod
    def nodeInitializer(cls):
        fnTypeAttr = OpenMaya.MFnTypedAttribute()
        fnMtxAttr = OpenMaya.MFnMatrixAttribute()

        cls.IN_MATRIX_ARRAY = fnTypeAttr.create('inMatrixArray', 'inMatrixArray', OpenMaya.MFnMatrixArrayData.kMatrixArray)

        cls.OUT_ARRAY_OF_MATRIX = fnMtxAttr.create('outMatrix', 'outMatrix')
        fnMtxAttr.setWritable(False)
        fnMtxAttr.setStorable(False)
        fnMtxAttr.setArray(True)
        fnMtxAttr.setUsesArrayDataBuilder(True)

        cls.addAttribute(cls.IN_MATRIX_ARRAY)
        cls.addAttribute(cls.OUT_ARRAY_OF_MATRIX)

        cls.attributeAffects(cls.OUT_ARRAY_OF_MATRIX, cls.OUT_ARRAY_OF_MATRIX)

    def compute(self, plug, dataBlock):
        if plug == self.OUT_ARRAY_OF_MATRIX:
            matrixArrayObj = dataBlock.inputValue(self.IN_MATRIX_ARRAY).data()
            fnMtxArrayData = OpenMaya.MFnMatrixArrayData(matrixArrayObj)
            matrixArray = fnMtxArrayData.array()

            outArrayOfMatrixHandle = dataBlock.outputArrayValue(self.OUT_ARRAY_OF_MATRIX)
            builder = outArrayOfMatrixHandle.builder()
            for i in range(matrixArray.length()):
                elementHandle = builder.addElement(i)
                elementHandle.setMMatrix(matrixArray[i])
            outArrayOfMatrixHandle.set(builder)
            dataBlock.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter


def initializePlugin(mObject):
    fnPlugin = OpenMayaMPx.MFnPlugin(mObject, 'Tak', '1.0')
    try:
        fnPlugin.registerNode(MatrixArrayToArrayOfMatrix.NAME,
                              MatrixArrayToArrayOfMatrix.ID,
                              MatrixArrayToArrayOfMatrix.nodeCreator,
                              MatrixArrayToArrayOfMatrix.nodeInitializer)
    except:
        OpenMaya.MGlobal.displayError('Failed to register node: {}'.format(MatrixArrayToArrayOfMatrix.NAME))


def uninitializePlugin(mObject):
    fnPlugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        fnPlugin.deregisterNode(MatrixArrayToArrayOfMatrix.ID)
    except:
        OpenMaya.MGlobal.displayError('Failed to deregister node: {}'.format(MatrixArrayToArrayOfMatrix.NAME))
