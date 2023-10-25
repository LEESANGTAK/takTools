"Fourth order Runge Kutta method to solve the second order differential equation for mass-spring-damper systems"

__author__ = "Paolo Dominici"
__version__ = "Version: 1.0"
__date__ = "Date: 2008/12/04"

import sys, math
from maya import OpenMaya, OpenMayaAnim, OpenMayaMPx

nodeName = "rungeKutta"
spNodeId = OpenMaya.MTypeId(0x58805)

# node definition
class spNode(OpenMayaMPx.MPxNode):
	currentTime = OpenMaya.MObject()
	targetPosition = OpenMaya.MObject()
	springConstant = OpenMaya.MObject()
	dampingRatio = OpenMaya.MObject()
	frameIterations = OpenMaya.MObject()
	outPosition = OpenMaya.MObject()
	outVelocity = OpenMaya.MObject()
	
	k = 0.0
	c = 0.0
	
	lastTime = 0.0
	lastPos = [0.0, 0.0, 0.0]
	lastVel = [0.0, 0.0, 0.0]
	
	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)
	
	def compute(self, plug, dataBlock):
		if plug == spNode.outPosition or plug == spNode.outVelocity:
			# get inputs
			currentTime = dataBlock.inputValue(spNode.currentTime).asTime().value()
			startTime = OpenMayaAnim.MAnimControl.animationStartTime().value()
			targetPosition = dataBlock.inputValue(spNode.targetPosition).asFloat3()
			frameIterations = dataBlock.inputValue(spNode.frameIterations).asInt()
			
			self.k = dataBlock.inputValue(spNode.springConstant).asFloat()
			dr = dataBlock.inputValue(spNode.dampingRatio).asFloat()
			self.c = 2.0 * dr * math.sqrt(self.k)
			
			# compute
			if currentTime <= startTime:
				self.lastTime = startTime
				self.lastPos = list(targetPosition)
				self.lastVel = [0.0, 0.0, 0.0]
				h = 0.0
			else:
				# if the iterations are 2 the time step is half the frame difference
				deltaTime = currentTime - self.lastTime
				# force deltaTime to be not greater than 1.0 (to avoid eccessive movement when scrubbing back and forth)
				if deltaTime > 1.0:
					deltaTime = 1.0
				elif deltaTime < -1.0:
					deltaTime = -1.0
				
				h = deltaTime/frameIterations
				
				self.lastTime = currentTime
				
				for iter in xrange(frameIterations):
					deltaPos = [self.lastPos[i]-targetPosition[i] for i in xrange(3)]
					
					for i in xrange(3):
						r = self.rk4(deltaPos[i], self.lastVel[i], h)
						
						self.lastPos[i] = r[0] + targetPosition[i]
						self.lastVel[i] = r[1]
			
			if plug == spNode.outPosition:
				result = self.lastPos
				outputHandle = dataBlock.outputValue(spNode.outPosition)
				outputHandle.set3Float(result[0], result[1], result[2])
			else:
				result = self.lastVel
				outputHandle = dataBlock.outputValue(spNode.outVelocity)
				outputHandle.set3Float(result[0], result[1], result[2])
			
			dataBlock.setClean(plug)
		
		return OpenMaya.kUnknownParameter
	
	def msd(self, x, dx):
		return -dx*self.c - x*self.k
	
	# get pos and vel
	def rk4(self, x, dx, h):
		k1x = dx
		k1v = self.msd(x, k1x)
		
		k2x = dx + k1v*h*0.5
		k2v = self.msd(x + k1x*h*0.5, k2x)
		
		k3x = dx + k2v*h*0.5
		k3v = self.msd(x + k2x*h*0.5, k3x)
		
		k4x = dx + k3v*h
		k4v = self.msd(x + k3x*h, k4x)
		
		return (x + (k1x + 2*k2x + 2*k3x + k4x)*h/6, dx + (k1v + 2*k2v + 2*k3v + k4v)*h/6)

# creator
def nodeCreator():
	return OpenMayaMPx.asMPxPtr(spNode())

# initializer
def nodeInitializer():
	# input
	uAttr = OpenMaya.MFnUnitAttribute()
	spNode.currentTime = uAttr.create("currentTime", "t", OpenMaya.MFnUnitAttribute.kTime, 1.0)
	uAttr.setKeyable(True)
	
	nAttr = OpenMaya.MFnNumericAttribute()
	spNode.targetPosition = nAttr.createPoint("targetPosition", "tp")
	nAttr.setKeyable(True)
	
	nAttr = OpenMaya.MFnNumericAttribute()
	spNode.springConstant = nAttr.create("springConstant", "k", OpenMaya.MFnNumericData.kFloat, 0.5)
	nAttr.setMin(0.0)
	nAttr.setKeyable(True)
	
	nAttr = OpenMaya.MFnNumericAttribute()
	spNode.dampingRatio = nAttr.create("dampingRatio", "dr", OpenMaya.MFnNumericData.kFloat, 0.5)
	nAttr.setMin(0.0)
	nAttr.setMax(1.0)
	nAttr.setKeyable(True)
	
	nAttr = OpenMaya.MFnNumericAttribute()
	spNode.frameIterations = nAttr.create("frameIterations", "fi", OpenMaya.MFnNumericData.kInt, 1)
	nAttr.setMin(1)
	nAttr.setMax(5)
	nAttr.setChannelBox(True)
	
	nAttr = OpenMaya.MFnNumericAttribute()
	spNode.outPosition = nAttr.createPoint("outPosition", "op")
	nAttr.setWritable(False)
	
	nAttr = OpenMaya.MFnNumericAttribute()
	spNode.outVelocity = nAttr.createPoint("outVelocity", "ov")
	nAttr.setWritable(False)
	
	# add attributes
	spNode.addAttribute(spNode.currentTime)
	spNode.addAttribute(spNode.targetPosition)
	spNode.addAttribute(spNode.springConstant)
	spNode.addAttribute(spNode.dampingRatio)
	spNode.addAttribute(spNode.frameIterations)
	spNode.addAttribute(spNode.outPosition)
	spNode.addAttribute(spNode.outVelocity)
	
	spNode.attributeAffects(spNode.currentTime, spNode.outPosition)
	spNode.attributeAffects(spNode.currentTime, spNode.outVelocity)

def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.registerNode(nodeName, spNodeId, nodeCreator, nodeInitializer)
	except:
		sys.stderr.write("Failed to register node: $s\n" % nodeName)

def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode(spNodeId)
	except:
		sys.stderr.write("Failed to deregister node: $s\n" % nodeName)
