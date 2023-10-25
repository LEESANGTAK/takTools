# The bursh now performs a little faster and also supports undo/redo.
#
# Modified by : nuternativ
#       nuttynew@hotmail.com
#       nuternativtd.blogspot.com
#
# How to use  : 1.Put averageVertexSkinWeightCmd.py to your plugin path. 
#                 (ie. C:\Program Files\Autodesk\<Version>\bin\plug-ins)
#               2.Put averageVertexSkinWeightBrush.py to your python path. 
#                 (ie. C:\Documents and Settings\<username>\My Documents\maya\<Version>\scripts)
#               3.Execute the following python command.
#                 import averageVertexSkinWeightBrush
#                 reload(averageVertexSkinWeightBrush)
#                 averageVertexSkinWeightBrush.paint()
#
################################################################################################



import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.OpenMayaMPx as ompx

kPluginCmdName = "averageVertexSkinWeight"

kIndexFlag = "-i"
kIndexLongFlag = "-index"
kValueFlag = "-v"
kValueLongFlag = "-value"


class AverageVertexSkinWeightCmd(ompx.MPxCommand):

	def __init__(self):
		ompx.MPxCommand.__init__(self)
		self.index = None
		self.value = None
		self.fnSkin = None
		self.component = None
		self.infIndices = None

		self.dagPath = om.MDagPath()
		self.oldWeights = om.MDoubleArray()


	def isUndoable(self):
		return True

	def getSkinCluster(self):
		# selected skinned geo
		selection = om.MSelectionList()
		om.MGlobal.getActiveSelectionList(selection)

		# get dag path for selection
		components = om.MObject()
		try:
			selection.getDagPath( 0, self.dagPath, components )
			self.dagPath.extendToShape()
		except: return

		# get skincluster from shape
		itDG = om.MItDependencyGraph(self.dagPath.node(), om.MFn.kSkinClusterFilter, om.MItDependencyGraph.kUpstream)
		while not itDG.isDone():
			self.fnSkin = oma.MFnSkinCluster(itDG.currentItem())
			found = True
			break


	def doIt(self, args):
		# get the skinCluster for selected mesh
		self.getSkinCluster()
		if  not self.fnSkin:
			om.MGlobal.displayError("Select a meshs transform with skinCluster.")
			return

		argData = om.MArgDatabase(self.syntax(), args)
		
		if argData.isFlagSet(kIndexFlag):
			self.index = argData.flagArgumentInt(kIndexFlag, 0)
		if argData.isFlagSet(kValueFlag):
			self.value = argData.flagArgumentDouble(kValueFlag, 0)

		self.redoIt()

	def undoIt(self):
		self.fnSkin.setWeights(self.dagPath, 
							self.component, 
							self.infIndices, 
							self.oldWeights, 
							False)

	def redoIt(self):
		# get the vertex to operating on
		self.component = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
		om.MFnSingleIndexedComponent(self.component).addElement(self.index)

		surrWeights = om.MDoubleArray()
		infCount = om.MScriptUtil()
		inf = infCount.asUintPtr()
		surrVtxArray = om.MIntArray()

		# create mesh iterator and get conneted vertices for averaging
		mitVtx = om.MItMeshVertex (self.dagPath, self.component)
		mitVtx.getConnectedVertices(surrVtxArray)
		
		# get surrounding vertices 
		surrComponents = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
		om.MFnSingleIndexedComponent(surrComponents).addElements(surrVtxArray)

		# read weight from single vertex (oldWeights) and from the surrounding vertices (surrWeights)
		self.fnSkin.getWeights(self.dagPath, self.component, self.oldWeights, inf)
		self.fnSkin.getWeights(self.dagPath, surrComponents, surrWeights, inf)
		influenceCount = om.MScriptUtil.getUint(inf)

		# get counts
		surrVtxCount = surrVtxArray.length()
		surrWeightsCount = surrWeights.length()

		# reset variable
		self.infIndices = om.MIntArray()
		newWeights = om.MDoubleArray(influenceCount, 0.0)

		invValue = 1.0 - self.value

		# average all the surrounding vertex weights and multiply and blend it over the origWeight with the weight from the artisan brush
		for i in xrange(influenceCount):
			self.infIndices.append(i)
			oldWeightDivSurrCountByInfValue = (self.oldWeights[i] / surrVtxCount) * invValue
			for j in xrange(i, surrWeightsCount, influenceCount):
			  	newWeights[i] += (((surrWeights[j] / surrVtxCount) * self.value) +  oldWeightDivSurrCountByInfValue)

		# set the final weights throught the skinCluster again
		self.fnSkin.setWeights(self.dagPath, 
							self.component, 
							self.infIndices, 
							newWeights, 
							False,
							self.oldWeights)

		
# Creator
def cmdCreator():
	# Create the command
	return ompx.asMPxPtr(AverageVertexSkinWeightCmd())


# Syntax creator
def syntaxCreator():
	syntax = om.MSyntax()
	syntax.addFlag(kIndexFlag, kIndexLongFlag, om.MSyntax.kLong)
	syntax.addFlag(kValueFlag, kValueLongFlag, om.MSyntax.kDouble)
	return syntax


# Initialize the script plug-in
def initializePlugin(mobject):
	mplugin = ompx.MFnPlugin(mobject, "Nuternativ", "1.0", "Any")
	try:
		mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)
	except Exception, e:
		sys.stderr.write('Failed to register command:  %s\n' %kPluginCmdName)
		sys.stderr.write('%s\n' %e)


# Uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = ompx.MFnPlugin(mobject)
	try:
		mplugin.deregisterCommand(kPluginCmdName)
	except Exception, e:
		sys.stderr.write('Failed to de-register command:  %s\n' %kPluginCmdName)
		sys.stderr.write('%s\n' %e)

	
