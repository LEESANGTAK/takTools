import logging

import pymel.core as pm


logger = logging.getLogger("Rig Optimizer")
logger.setLevel(logging.DEBUG)


class RigOptimizer(object):
    NODE_TYPES = ["wrap", "constraint", "skinCluster", "blendShape", "ffd"]

    def __init__(self):
        self.wrap = None
        self.constraint = None
        self.skinCluster = None
        self.blendShape = None
        self.ffd = None

    def inspect(self):
        for nodeType in RigOptimizer.NODE_TYPES:
            setattr(self, nodeType, pm.ls(type=nodeType))

        for attr in self.__dict__.keys():
            nodes = getattr(self, attr)
            logger.info("{0}: {1}".format(attr, len(nodes)))

    def optimize(self):
        self.optimizeConstraints()

    def optimizeConstraints(self):
        notConvertedConstraints = []
        for const in self.constraint:
            constType = const.nodeType()
            if not constType in ["parentConstraint", "pointConstraint", "orientConstraint"]:
                notConvertedConstraints.append(const)
                continue

            constInfo = self.getConstraintInfo(const)
            driven = constInfo["driven"]
            driverWeights = self.getDriverWeights(constInfo["driverInfos"])
            wtAddMtx = pm.createNode("wtAddMatrix", n="{}_wtAddMtx".format(driven))

            for i, driverInfo in enumerate(constInfo["driverInfos"]):
                driverMultMatrix = self.buildDriverMatrix(driverInfo["driver"], driven, constType)
                driverMultMatrix.matrixSum >> wtAddMtx.wtMatrix[i].matrixIn
                if driverInfo["weightDriver"]:
                    driverInfo["weightDriver"] >> wtAddMtx.wtMatrix[i].weightIn
                else:
                    wtAddMtx.wtMatrix[i].weightIn.set(float(driverWeights[i])/sum(driverWeights))  # Set normalized weight

            toLocalMultMatrix = pm.createNode("multMatrix", n="{0}_multMtx".format(driven))
            wtAddMtx.matrixSum >> toLocalMultMatrix.matrixIn[0]
            if driven.getParent():
                driven.getParent().worldInverseMatrix >> toLocalMultMatrix.matrixIn[1]

            decomposeMtx = pm.createNode("decomposeMatrix", n="{0}_decMtx".format(driven))
            toLocalMultMatrix.matrixSum >> decomposeMtx.inputMatrix

            # Connect to driven channels
            if constType == "parentConstraint":
                decomposeMtx.outputTranslateX >> driven.translateX
                decomposeMtx.outputTranslateY >> driven.translateY
                decomposeMtx.outputTranslateZ >> driven.translateZ
                decomposeMtx.outputRotateX >> driven.rotateX
                decomposeMtx.outputRotateY >> driven.rotateY
                decomposeMtx.outputRotateZ >> driven.rotateZ
            elif constType == "pointConstraint":
                decomposeMtx.outputTranslateX >> driven.translateX
                decomposeMtx.outputTranslateY >> driven.translateY
                decomposeMtx.outputTranslateZ >> driven.translateZ
            elif constType == "orientConstraint":
                decomposeMtx.outputRotateX >> driven.rotateX
                decomposeMtx.outputRotateY >> driven.rotateY
                decomposeMtx.outputRotateZ >> driven.rotateZ

            pm.delete(const)

        logger.debug("notConvertedConstraints: {0}".format(notConvertedConstraints))

    def getConstraintInfo(self, const):
        constInfo = {
            "driverInfos": [],
            "driven": None
        }

        # Get drivers
        drivers = []
        for targetParentMatrixAttr in pm.listAttr(const.target, multi=True, string="targetParentMatrix"):
            drivers.extend(const.attr(targetParentMatrixAttr).inputs())

        # Get drivers info
        for i, driver in enumerate(drivers):
            driverInfo = {
                "driver": None,
                "weight": 0.0,
                "weightDriver": None
            }

            driverInfo["driver"] = driver
            driverInfo["weight"] = const.target[i].targetWeight.get()
            weightAttr = const.target[i].targetWeight.inputs(plugs=True)[0]
            weightDriver = weightAttr.inputs(plugs=True)
            if weightDriver:
                driverInfo["weightDriver"] = weightDriver[0]
            constInfo["driverInfos"].append(driverInfo)

        # Get driven
        constInfo["driven"] = const.constraintParentInverseMatrix.inputs()[0]

        return constInfo

    def getDriverWeights(self, driverInfos):
        driverWeights = []
        for driverInfo in driverInfos:
            driverWeights.append(driverInfo["weight"])
        return driverWeights

    def buildDriverMatrix(self, driver, driven, constraintType):
        multMtx = pm.createNode("multMatrix", n="{0}_driverMultMtx".format(driver))
        multMtx.matrixIn[0].set(driven.worldMatrix.get() * driver.worldInverseMatrix.get())
        if constraintType == "parentConstraint":
            driver.worldMatrix >> multMtx.matrixIn[1]
        elif constraintType == "pointConstraint":
            decMtx = pm.createNode("decomposeMatrix", n="{0}_pointDecMtx".format(driver))
            composeMtx = pm.createNode("composeMatrix", n="{0}_pointComposeMtx".format(driver))
            driver.worldMatrix >> decMtx.inputMatrix
            decMtx.outputTranslate >> composeMtx.inputTranslate
            composeMtx.outputMatrix >> multMtx.matrixIn[1]
        elif constraintType == "orientConstraint":
            decMtx = pm.createNode("decomposeMatrix", n="{0}_orientDecMtx".format(driver))
            composeMtx = pm.createNode("composeMatrix", n="{0}_orientComposeMtx".format(driver))
            driver.worldMatrix >> decMtx.inputMatrix
            decMtx.outputRotate >> composeMtx.inputRotate
            composeMtx.outputMatrix >> multMtx.matrixIn[1]

        return multMtx
