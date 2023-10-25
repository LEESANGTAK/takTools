import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.mel as mel
import sys


kPluginNodeTypeName = "rampValuesNode"

outValuesrampValuesNodeId = OpenMaya.MTypeId(0x89010)
class rampNode(OpenMayaMPx.MPxNode):

        inValue     =   OpenMaya.MObject()
        ramp01      =   OpenMaya.MRampAttribute()
        numSamples     =   OpenMaya.MObject()
        outValues   =   OpenMaya.MObject()


        ##AEtemplate proc for the MRampAtributes
        mel.eval('''
                    global proc AErampValuesNodeTemplate( string $nodeName )
{
	AEswatchDisplay  $nodeName;
	editorTemplate -beginScrollLayout;
		editorTemplate -beginLayout "ramp Node Template" -collapse 0;

			AEaddRampControl ($nodeName+".ramp01");

		editorTemplate -endLayout;

		AEdependNodeTemplate $nodeName;

	editorTemplate -addExtraControls;
	editorTemplate -endScrollLayout;
}

                    ''')

        def __init__(self):
                OpenMayaMPx.MPxNode.__init__(self)

        def postConstructor(self):
                thisNode = self.thisMObject()
                initializeCurveRamp(thisNode, rampNode.ramp01, 0, 0.0, 0.0, 1)
                initializeCurveRamp(thisNode, rampNode.ramp01, 1, 1.0, 1.0, 1)

        def compute(self, plug, dataBlock):
                thisNode = self.thisMObject()
                rampPlug = OpenMaya.MPlug( thisNode, rampNode.ramp01 )
                rampPlug.setAttribute(rampNode.ramp01)
                RampPlug01 = OpenMaya.MPlug(rampPlug.node(), rampPlug.attribute())

                myRamp = OpenMaya.MRampAttribute(RampPlug01.node(), RampPlug01.attribute())

                dataHandle = dataBlock.inputValue(rampNode.inValue)
                twistValue = dataHandle.asDouble()

                dataHandle = dataBlock.inputValue(rampNode.numSamples)
                result = dataHandle.asInt()

                outputHandle = dataBlock.outputArrayValue(rampNode.outValues)
                outputBuilder = outputHandle.builder()
                numElements = outputHandle.elementCount()

                myValAtPos = []
                dels = []

                for i in range(result):
                    quo = 1.0/(result - 1.0)

                    myFloat = quo*i

                    def getValAtPos():
                        valAt_util = OpenMaya.MScriptUtil()
                        valAt_util.createFromDouble(1.0)
                        valAtPtr = valAt_util.asFloatPtr()
                        myRamp.getValueAtPosition(myFloat, valAtPtr)
                        valAtPos = valAt_util.getFloat(valAtPtr)
                        return (valAtPos)

                    myValAtPos.append(getValAtPos())

                    try:
                        outputHandle.jumpToArrayElement(i)
                        outdatahandle = outputHandle.outputValue()
                        outdatahandle.setDouble(myValAtPos[i]*twistValue)

                    except:
                        pass

                for w in range(numElements):
                    try:
                        outputHandle.jumpToArrayElement(w)
                        myIndex = outputHandle.elementIndex()
                    except:
                        pass

                    if (myIndex >= result):
                        try:
                            outputBuilder.removeElement(myIndex)
                        except:
                            pass

                return OpenMaya.kUnknownParameter


def nodeCreator():
        return OpenMayaMPx.asMPxPtr( rampNode() )

def nodeInitializer():

        nAttr = OpenMaya.MFnNumericAttribute()
        rampNode.inValue = nAttr.create( "inValue", "iv", OpenMaya.MFnNumericData.kDouble, 0.0 )
        nAttr.setWritable(1)
        nAttr.setStorable(1)

        rampNode.ramp01= OpenMaya.MRampAttribute.createCurveRamp('ramp01', 'rmp01')

        nAttr = OpenMaya.MFnNumericAttribute()
        rampNode.numSamples = nAttr.create ( "numSamples", "nsamp", OpenMaya.MFnNumericData.kInt, 0 )
        nAttr.setWritable(1)
        nAttr.setStorable(1)

        nAttr = OpenMaya.MFnNumericAttribute()
        rampNode.outValues = nAttr.create( "outValues", "otv", OpenMaya.MFnNumericData.kDouble, 0.0 )
        nAttr.setArray(1)
        nAttr.setStorable(1)
        nAttr.setUsesArrayDataBuilder(1)

        rampNode.addAttribute( rampNode.inValue )
        rampNode.addAttribute( rampNode.ramp01 )
        rampNode.addAttribute ( rampNode.numSamples )
        rampNode.addAttribute( rampNode.outValues )

        rampNode.attributeAffects( rampNode.inValue , rampNode.outValues )
        rampNode.attributeAffects( rampNode.ramp01 , rampNode.outValues )
        rampNode.attributeAffects( rampNode.numSamples , rampNode.outValues )


def initializeCurveRamp(node, rampAttr, index, position, value, interpolation):
    rampPlug = OpenMaya.MPlug(node, rampAttr)
    elementPlug = rampPlug.elementByLogicalIndex(index)

    positionPlug = elementPlug.child(0)
    positionPlug.setFloat(position)

    valuePlug = elementPlug.child(1)
    valuePlug.setFloat(value)

    interpPlug = elementPlug.child(2)
    interpPlug.setInt(interpolation)


def initializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject, "", "1.0", "Any")
        try:
                mplugin.registerNode( kPluginNodeTypeName, outValuesrampValuesNodeId, nodeCreator, nodeInitializer )

        except:
                sys.stderr.write( "Failed to register node: %s" % kPluginNodeTypeName )
                raise

def uninitializePlugin(mobject):
        mplugin = OpenMayaMPx.MFnPlugin(mobject)
        try:
                mplugin.deregisterNode( outValuesrampValuesNodeId )
        except:
                sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeTypeName )
                raise

