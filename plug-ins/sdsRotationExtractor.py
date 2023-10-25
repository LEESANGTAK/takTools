# Copyright (c) 2021 PUBG Corporation.  All Rights Reserved.

__copyright__ = """
Copyright (c) 2021 PUBG Corporation.  All Rights Reserved.
"""

__doc__ = """A simple node to extract Yaw, Pitch and Roll from a base and a transform matrix """
__author__ = "'kchu"
__email__ = "kchu@strikingdistancestudios.com"
__date__ = "March 01, 2021"

import math
from maya import OpenMaya, OpenMayaMPx


class YawPitchRoll(OpenMayaMPx.MPxNode):
    kPluginNodeName = "sdsRotationExtractor"
    kPluginNodeId = OpenMaya.MTypeId(0x00137980)

    axis_FV = (OpenMaya.MFloatVector.xAxis,
               OpenMaya.MFloatVector.yAxis,
               OpenMaya.MFloatVector.zAxis,
               OpenMaya.MFloatVector.xNegAxis,
               OpenMaya.MFloatVector.yNegAxis,
               OpenMaya.MFloatVector.zNegAxis,)

    @staticmethod
    def range_secu_(dot, mini=-1.0, maxi=1.0):
        if dot > maxi:
            return maxi
        elif dot < mini:
            return mini
        else:
            return dot

    @staticmethod
    def FM_to_MM(fm):
        valueList = [
                fm(0, 0), fm(0, 1), fm(0, 2), fm(0, 3),
                fm(1, 0), fm(1, 1), fm(1, 2), fm(1, 3),
                fm(2, 0), fm(2, 1), fm(2, 2), fm(2, 3),
                fm(3, 0), fm(3, 1), fm(3, 2), fm(3, 3)]
        outMat = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(valueList, outMat)
        return outMat

    @staticmethod
    def MM_to_FM(mm):
        valueList = [
                mm(0, 0), mm(0, 1), mm(0, 2), mm(0, 3),
                mm(1, 0), mm(1, 1), mm(1, 2), mm(1, 3),
                mm(2, 0), mm(2, 1), mm(2, 2), mm(2, 3),
                mm(3, 0), mm(3, 1), mm(3, 2), mm(3, 3)]
        outMat = OpenMaya.MFloatMatrix()
        OpenMaya.MScriptUtil.createFloatMatrixFromList(valueList, outMat)
        return outMat

    @classmethod
    def nodeCreator(cls):
        return OpenMayaMPx.asMPxPtr(cls())

    @classmethod
    def nodeInitializer(cls):
        matrixAttr = OpenMaya.MFnMatrixAttribute()
        unitAttr = OpenMaya.MFnUnitAttribute()
        enumAttr = OpenMaya.MFnEnumAttribute()

        cls.rotMatrix = matrixAttr.create("rotationMatrix", "rm", OpenMaya.MFnNumericData.kFloat)
        cls.rotBaseMatrix = matrixAttr.create("baseRotationMatrix", "brm", OpenMaya.MFnNumericData.kFloat)

        cls.aimAxis = enumAttr.create("aimAxis", "aa", 0)
        enumAttr.addField("x", 0)
        enumAttr.addField("y", 1)
        enumAttr.addField("z", 2)
        enumAttr.addField("-x", 3)
        enumAttr.addField("-y", 4)
        enumAttr.addField("-z", 5)
        cls.upAxis = enumAttr.create("upAxis", "ua", 1)
        enumAttr.addField("x", 0)
        enumAttr.addField("y", 1)
        enumAttr.addField("z", 2)
        enumAttr.addField("-x", 3)
        enumAttr.addField("-y", 4)
        enumAttr.addField("-z", 5)

        # outputs
        cls.simpleRoll = unitAttr.create("simpleRoll", "sr", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)

        cls.pitch = unitAttr.create("pitch", "p", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)
        cls.pitchYaw = unitAttr.create("pitchYaw", "py", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)

        cls.yaw = unitAttr.create("yaw", "y", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)
        cls.yawPitch = unitAttr.create("yawPitch", "yp", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)

        cls.roll = unitAttr.create("roll", "r", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)

        cls.rollPitch = unitAttr.create("rollPitch", "rp", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)
        cls.rollPitchYaw = unitAttr.create("rollPitchYaw", "rpy", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)

        cls.rollYaw = unitAttr.create("rollYaw", "ry", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)
        cls.rollYawPitch = unitAttr.create("rollYawPitch", "ryp", OpenMaya.MFnUnitAttribute.kAngle, .0)
        unitAttr.setWritable(False)

        # add + affect
        for attr in (cls.rotMatrix, cls.aimAxis, cls.rotBaseMatrix,
                     cls.simpleRoll, cls.upAxis, cls.pitch, cls.pitchYaw, cls.yaw, cls.yawPitch,
                     cls.roll, cls.rollPitch, cls.rollPitchYaw, cls.rollYaw, cls.rollYawPitch,):
            cls.addAttribute(attr)

        for attr in (cls.aimAxis, cls.upAxis, cls.rotMatrix, cls.rotBaseMatrix,):
            cls.attributeAffects(attr, cls.roll)
            cls.attributeAffects(attr, cls.pitch)
            cls.attributeAffects(attr, cls.yaw)

            cls.attributeAffects(attr, cls.simpleRoll)
            cls.attributeAffects(attr, cls.rollPitchYaw)
            cls.attributeAffects(attr, cls.rollYawPitch)

            cls.attributeAffects(attr, cls.yawPitch)
            cls.attributeAffects(attr, cls.pitchYaw)

            cls.attributeAffects(attr, cls.rollPitch)
            cls.attributeAffects(attr, cls.rollYaw)

        # AE reorder
        cls.init_AETemplate()

    @classmethod
    def init_AETemplate(cls):
        AE_cmd = '''
		global proc AE[nodeType]Template( string $nodeName )
		{
		editorTemplate -beginScrollLayout;
			editorTemplate -beginLayout "Main Attributes" -collapse 0;
				editorTemplate -addControl "rotBaseMatrix";
				editorTemplate -addControl "aimAxis";
			editorTemplate -endLayout;
			editorTemplate -addExtraControls;
		editorTemplate -endScrollLayout;
		}
		'''.replace("[nodeType]", cls.kPluginNodeName)
        OpenMaya.MGlobal.executeCommand(AE_cmd)

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, data):

        if not plug in (self.roll, self.yaw, self.pitch, self.simpleRoll, self.rollYawPitch, self.rollPitchYaw, self.rollPitch, self.rollYaw, self.yawPitch, self.pitchYaw):
            return

        # Reference of joint that rotates
        rot_FM = data.inputValue(self.rotMatrix).asFloatMatrix() * data.inputValue(self.rotBaseMatrix).asFloatMatrix().inverse()

        aim_id = data.inputValue(self.aimAxis).asInt()
        up_id = data.inputValue(self.upAxis).asInt()

        aimPositiv_id, upPositiv_id = aim_id % 3, up_id % 3
        lastPositiv_id = list(frozenset((0, 1, 2)) - frozenset((aimPositiv_id, upPositiv_id)))[0]

        # Vectors
        aim1_FV = self.axis_FV[aim_id]
        up1_FV = self.axis_FV[up_id]
        last1_FV = aim1_FV ^ up1_FV

        aim2_FV = self.axis_FV[aim_id] * rot_FM
        up2_FV = self.axis_FV[up_id] * rot_FM
        last2_FV = aim2_FV ^ up2_FV

        if plug == self.simpleRoll:

            # Axis of a matrix with same aim2 and up1
            lastA_FV = (aim2_FV ^ up1_FV).normal()
            upA_FV = (lastA_FV ^ aim2_FV).normal()

            dot = self.range_secu_(upA_FV * up2_FV)
            simpleRoll_rad = .0

            if dot < 1.0:
                sign = 1.0

                dot2 = lastA_FV * up2_FV
                if dot2 < .0:
                    sign = -1.0

                simpleRoll_rad = math.acos(dot) * sign

            data.outputValue(self.simpleRoll).setMAngle(OpenMaya.MAngle(simpleRoll_rad))

        elif plug in (self.pitch, self.pitchYaw):

            aim2proj = [aim2_FV[0], aim2_FV[1], aim2_FV[2]]
            aim2proj[lastPositiv_id] = .0
            aim2proj_FV = OpenMaya.MFloatVector(aim2proj[0], aim2proj[1], aim2proj[2]).normal()

            # Angle between aim1 and aim2proj
            dot = self.range_secu_(aim1_FV * aim2proj_FV)
            pitch_rad = .0
            up2proj_FV = OpenMaya.MFloatVector(up2_FV)

            if dot < 1.0:
                sign = 1.0

                up2proj_FV = last1_FV ^ aim2proj_FV
                dot2 = up2proj_FV * aim1_FV

                if dot2 > .0:
                    sign = -1.0

                pitch_rad = math.acos(dot) * sign

            if plug == self.pitch:
                data.outputValue(self.pitch).setMAngle(OpenMaya.MAngle(pitch_rad))

            else:
                # pitchYaw
                dot = self.range_secu_(aim2proj_FV * aim2_FV)
                pitchYaw_rad = .0

                if dot < 1.0:
                    sign = 1.0

                    last2proj_FV = aim2_FV ^ up2proj_FV
                    dot2 = last2proj_FV * aim2proj_FV

                    if dot2 < .0:
                        sign = -1.0

                    pitchYaw_rad = math.acos(dot) * sign

                data.outputValue(self.pitchYaw).setMAngle(OpenMaya.MAngle(pitchYaw_rad))

        elif plug in (self.yaw, self.yawPitch):

            # proj1 = aim2 avec axeUp a 0
            aim2proj = [aim2_FV[0], aim2_FV[1], aim2_FV[2]]
            aim2proj[upPositiv_id] = .0
            aim2proj_FV = OpenMaya.MFloatVector(aim2proj[0], aim2proj[1], aim2proj[2]).normal()

            # angle entre aim1 et proj1
            dot = self.range_secu_(aim1_FV * aim2proj_FV)
            yaw_rad = .0
            last2proj_FV = OpenMaya.MFloatVector(last2_FV)

            if dot < 1.0:
                sign = 1.0

                last2proj_FV = aim2proj_FV ^ up1_FV
                dot2 = last2proj_FV * aim1_FV

                if dot2 < .0:
                    sign = -1.0

                yaw_rad = math.acos(dot) * sign

            if plug == self.yaw:
                data.outputValue(self.yaw).setMAngle(OpenMaya.MAngle(yaw_rad))

            else:
                # yawPitch
                dot = self.range_secu_(aim2proj_FV * aim2_FV)
                yawPitch_rad = .0

                if dot < 1.0:
                    sign = 1.0

                    up2proj_FV = last2proj_FV ^ aim2_FV
                    dot2 = up2proj_FV * aim2proj_FV

                    if dot2 > .0:
                        sign = -1.0

                    yawPitch_rad = math.acos(dot) * sign

                data.outputValue(self.yawPitch).setMAngle(OpenMaya.MAngle(yawPitch_rad))

        # Forced to calculate chilRoll for rollYawPitch and rollPitchYaw
        elif plug in (self.roll, self.rollPitch, self.rollYawPitch, self.rollPitchYaw, self.rollYaw,):

            # Pivot and angle from the triangle + quaternion with negative angle
            # Forced to go through MV to do Quaternion + rotateBy after
            pivot_FV = (aim1_FV ^ aim2_FV).normal()
            pivot_MV = OpenMaya.MVector(pivot_FV.x, pivot_FV.y, pivot_FV.z)

            angle_rad = aim1_FV.angle(aim2_FV)  # for scale
            rot_Q = OpenMaya.MQuaternion(-angle_rad, pivot_MV)

            # Make a copy of up2 and rotateBy quaternion
            # Twisted Up
            up2_rot_MV = OpenMaya.MVector(up2_FV.x, up2_FV.y, up2_FV.z)
            up2_rot_MV = up2_rot_MV.rotateBy(rot_Q)
            up2_rot_FV = OpenMaya.MFloatVector(up2_rot_MV[0], up2_rot_MV[1], up2_rot_MV[2])

            # Bind the dot of this new vector with respect to its origin
            # if it is less than 1 indicates that there is a twist
            dot = self.range_secu_(up2_rot_FV * up1_FV)
            roll_rad = .0

            if dot < 1.0:
                # arccosine of the dot returns an absolute angle
                # to recover the sign of the twist, test a 2nd dot
                sign = 1.0

                last2_rot_FV = aim1_FV ^ up2_rot_FV
                dot2 = last2_rot_FV * up1_FV

                if dot2 > .0:
                    sign = -1.0

                roll_rad = math.acos(dot) * sign

            if plug == self.roll:
                data.outputValue(self.roll).setMAngle(OpenMaya.MAngle(roll_rad))
            else:
                # chilPitch and chilYaw
                # twist_FM twisted around aim1_axis
                aim1_MV = OpenMaya.MVector(aim1_FV.x, aim1_FV.y, aim1_FV.z)

                twist_Q = OpenMaya.MQuaternion(roll_rad, aim1_MV)
                twist_FM = self.MM_to_FM(twist_Q.asMatrix())
                twist_FM_inv = twist_FM.inverse()

                # aim1 remains the same in the 2 benchmarks
                aim1twist_FV = OpenMaya.MFloatVector(aim1_FV)
                aim2twist_FV = aim2_FV * twist_FM_inv

                # Keeping this code comment for test 2nd dot product for 180 test
                # Used for dot2 (sign of angles)
                # up1twist_FV		= up1_FV * twist_FM
                # last1twist_FV		= last1_FV * twist_FM

                if plug in (self.rollYawPitch, self.rollYaw):

                    aim2proj = [aim2twist_FV[0], aim2twist_FV[1], aim2twist_FV[2]]
                    aim2proj[upPositiv_id] = .0
                    aim2proj_FV = OpenMaya.MFloatVector(aim2proj[0], aim2proj[1], aim2proj[2]).normal()

                    # angle entre aim1 et proj2
                    dot = self.range_secu_(aim1twist_FV * aim2proj_FV)
                    rollYaw_rad = .0

                    # sert pour dot2 de rollYawPitch
                    last2proj_FV = aim2proj_FV ^ up1_FV

                    if dot < 1.0:
                        sign = 1.0

                        dot2 = last2proj_FV * aim1twist_FV
                        if dot2 < .0:
                            sign = -1.0

                        rollYaw_rad = math.acos(dot) * sign

                    if plug == self.rollYaw:
                        data.outputValue(self.rollYaw).setMAngle(OpenMaya.MAngle(rollYaw_rad))
                    else:
                        # rollYawPitch
                        dot = self.range_secu_(aim2proj_FV * aim2twist_FV)
                        rollYawPitch_rad = .0

                        if dot < 1.0:
                            sign = 1.0

                            up2proj_FV = last2proj_FV ^ aim2twist_FV
                            dot2 = up2proj_FV * aim2proj_FV

                            if dot2 > .0:
                                sign = -1.0
                            rollYawPitch_rad = math.acos(dot) * sign

                        data.outputValue(self.rollYawPitch).setMAngle(OpenMaya.MAngle(rollYawPitch_rad))

                elif plug in (self.rollPitch, self.rollPitchYaw):

                    aim2proj = [aim2twist_FV[0], aim2twist_FV[1], aim2twist_FV[2]]
                    aim2proj[lastPositiv_id] = .0
                    aim2proj_FV = OpenMaya.MFloatVector(aim2proj[0], aim2proj[1], aim2proj[2]).normal()

                    # Angle between aim1 and proj1
                    dot = self.range_secu_(aim1twist_FV * aim2proj_FV)
                    rollPitch_rad = .0

                    # used for dot2 of rollPitchYaw
                    up2proj_FV = last1_FV ^ aim2proj_FV

                    if dot < 1.0:
                        sign = 1.0

                        dot2 = up2proj_FV * aim1twist_FV
                        if dot2 > .0:
                            sign = -1.0

                        rollPitch_rad = math.acos(dot) * sign

                    if plug == self.rollPitch:
                        data.outputValue(self.rollPitch).setMAngle(OpenMaya.MAngle(rollPitch_rad))
                    else:
                        # rollPitchYaw
                        dot = self.range_secu_(aim2proj_FV * aim2twist_FV)
                        rollPitchYaw_rad = .0

                        if dot < 1.0:
                            sign = 1.0

                            last2proj_FV = aim2twist_FV ^ up2proj_FV
                            dot2 = last2proj_FV * aim2proj_FV

                            if dot2 < .0:
                                sign = -1.0

                            rollPitchYaw_rad = math.acos(dot) * sign

                        data.outputValue(self.rollPitchYaw).setMAngle(OpenMaya.MAngle(rollPitchYaw_rad))

        data.setClean(plug)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Kelvin Chu -- kchu@pubg.com", "1.0", "Any")
    try:
        mplugin.registerNode(YawPitchRoll.kPluginNodeName, YawPitchRoll.kPluginNodeId, YawPitchRoll.nodeCreator, YawPitchRoll.nodeInitializer)
    except:
        OpenMaya.MGlobal.displayError("Failed to register command: %s\n" % YawPitchRoll.kPluginNodeName)
        raise


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(YawPitchRoll.kPluginNodeId)
    except:
        OpenMaya.MGlobal.displayError("Failed to unregister node: %s\n" % YawPitchRoll.kPluginNodeName)
        raise
