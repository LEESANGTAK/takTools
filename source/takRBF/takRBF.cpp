#include "takRBF.h"


MTypeId TakRBF::id(0x00002741);
MString TakRBF::name("takRBF");

MObject TakRBF::aBasisFunc;
MObject TakRBF::aSmoothness;
MObject TakRBF::aPoseX;
MObject TakRBF::aPoseY;
MObject TakRBF::aPoseZ;
MObject TakRBF::aPose;

MObject TakRBF::aOutWeight;
MObject TakRBF::aTargetX;
MObject TakRBF::aTargetY;
MObject TakRBF::aTargetZ;
MObject TakRBF::aTarget;

MObject TakRBF::aOutColor;
MObject TakRBF::aInColor;

MObject TakRBF::aOutMatrix;
MObject TakRBF::aInMatrix;


void* TakRBF::creator() {
    return new TakRBF;
}

MStatus TakRBF::initialize() {
    MStatus status;

    MFnNumericAttribute numAttr;
    MFnEnumAttribute enuAttr;
    MFnMatrixAttribute mtxAttr;

    // -------------------------------------
    // Output attributes
    // -------------------------------------
    aOutWeight = numAttr.create("outWeight", "outWeight", MFnNumericData::kFloat);
    numAttr.setStorable(false);
    numAttr.setWritable(false);
    numAttr.setArray(true);
    numAttr.setUsesArrayDataBuilder(true);
    addAttribute(aOutWeight);

    aOutColor = numAttr.createColor("outColor", "outColor");
    numAttr.setStorable(false);
    numAttr.setWritable(false);
    addAttribute(aOutColor);

    aOutMatrix = mtxAttr.create("outMatrix", "outMatrix");
    mtxAttr.setStorable(false);
    mtxAttr.setWritable(false);
    addAttribute(aOutMatrix);

    // -------------------------------------
    // Input attributes
    // -------------------------------------
    aBasisFunc = enuAttr.create("basisFunc", "basisFunc");
    enuAttr.addField("gaussian", 0);
    enuAttr.addField("multiQuadratic", 1);
    enuAttr.addField("inverseMultiQuadratic", 2);
    enuAttr.setKeyable(true);
    addAttribute(aBasisFunc);
    attributeAffects(aBasisFunc, aOutWeight);
    attributeAffects(aBasisFunc, aOutColor);
    attributeAffects(aBasisFunc, aOutMatrix);

    aSmoothness = numAttr.create("smoothness", "smoothness", MFnNumericData::kDouble, 3.0);
    numAttr.setMin(0.00001);
    numAttr.setKeyable(true);
    addAttribute(aSmoothness);
    attributeAffects(aSmoothness, aOutWeight);
    attributeAffects(aSmoothness, aOutColor);
    attributeAffects(aSmoothness, aOutMatrix);

    aPoseX = numAttr.create("poseX", "poseX", MFnNumericData::kDouble);
    aPoseY = numAttr.create("poseY", "poseY", MFnNumericData::kDouble);
    aPoseZ = numAttr.create("poseZ", "poseZ", MFnNumericData::kDouble);
    aPose = numAttr.create("pose", "pose", aPoseX, aPoseY, aPoseZ);
    addAttribute(aPose);
    attributeAffects(aPose, aOutWeight);
    attributeAffects(aPose, aOutColor);
    attributeAffects(aPose, aOutMatrix);

    aTargetX = numAttr.create("targetX", "targetX", MFnNumericData::kDouble);
    aTargetY = numAttr.create("targetY", "targetY", MFnNumericData::kDouble);
    aTargetZ = numAttr.create("targetZ", "targetZ", MFnNumericData::kDouble);
    aTarget = numAttr.create("target", "target", aTargetX, aTargetY, aTargetZ);
    numAttr.setArray(true);
    numAttr.setDisconnectBehavior(MFnAttribute::kDelete);
    addAttribute(aTarget);
    attributeAffects(aTarget, aOutWeight);
    attributeAffects(aTarget, aOutColor);
    attributeAffects(aTarget, aOutMatrix);

    aInColor = numAttr.createColor("inColor", "inColor");
    numAttr.setArray(true);
    numAttr.setDisconnectBehavior(MFnAttribute::kDelete);
    addAttribute(aInColor);
    attributeAffects(aInColor, aOutColor);

    aInMatrix = mtxAttr.create("inMatrix", "inMatrix");
    mtxAttr.setArray(true);
    mtxAttr.setDisconnectBehavior(MFnAttribute::kDelete);
    addAttribute(aInMatrix);
    attributeAffects(aInMatrix, aOutMatrix);

    return MS::kSuccess;
}

MatrixXd TakRBF::getTargetsDistMatrix(const MPointArray& targetsPos) {
    MatrixXd targetsDistMatrix;
    targetsDistMatrix.resize(mNumTargets, mNumTargets);
    MPoint currentPos, otherPos;
    for (unsigned i = 0; i < mNumTargets; i++)
    {
        currentPos = targetsPos[i];
        for (unsigned j = 0; j < mNumTargets; j++)
        {
            otherPos = targetsPos[j];
            targetsDistMatrix(i, j) = RBF((otherPos - currentPos).length());
        }
    }

    return targetsDistMatrix;
}

MatrixXd TakRBF::getPoseToTargetsMatrix(const MPoint& posePos, const MPointArray& targetsPos) {
    MatrixXd poseToTargetsMatrix;
    poseToTargetsMatrix.resize(1, mNumTargets);
    for (unsigned i = 0; i < mNumTargets; i++) {
        poseToTargetsMatrix(0, i) = RBF((targetsPos[i] - posePos).length());
    }

    return poseToTargetsMatrix;
}

void TakRBF::makeIdentityMatrix(MatrixXd& matrix) {
    for (unsigned i = 0; i < mNumTargets; i++) {
        for (unsigned j = 0; j < mNumTargets; j++) {
            if (i == j) {
                matrix(i, j) = 1;
            }
            else {
                matrix(i, j) = 0;
            }
        }
    }
}

double TakRBF::RBF(const double& dist) {
    double outVal;

    // gaussian
    if (mBasisFunc == 0) {
        outVal = exp(-(pow(dist, 2) / pow(mSmoothness, 2)));
    }
    // multiQuadratic
    else if (mBasisFunc == 1) {
        outVal = pow((pow(dist, 2) + pow(mSmoothness, 2)), 0.5);
    }
    // inverseMultiQuadratic
    else if (mBasisFunc == 2) {
        outVal = pow((pow(dist, 2) + pow(mSmoothness, 2)), -0.5);
    }
    else {
        return MS::kInvalidParameter;
    }

    return outVal;
}

MDoubleArray TakRBF::matrixToDoubleArray(const MMatrix& matirx) {
    MDoubleArray flatMatrix;
    for (unsigned int i = 0; i < 4; i++) {
        for (unsigned int j = 0; j < 4; j++) {
            flatMatrix.append(matirx[i][j]);
        }
    }
    return flatMatrix;
}

MMatrix TakRBF::doubleArrayToMatrix(const MDoubleArray& flatMatrix) {
    MMatrix resultMatrix;

    double matrixDouble[4][4];
    for (unsigned int i = 0; i < 4; i++) {
        for (unsigned int j = 0; j < 4; j++) {
            matrixDouble[i][j] = flatMatrix[i*4+j];
        }
    }

    return MMatrix(matrixDouble);
}

TakRBF::TakRBF() {}

TakRBF::~TakRBF() {}

MStatus TakRBF::compute(const MPlug& plug, MDataBlock& dataBlock) {
    MStatus status;

    // Check requsted plug is valid
    if (plug != aOutWeight && plug != aOutColor && plug != aOutMatrix) {
        return MS::kUnknownParameter;
    }

    mBasisFunc = dataBlock.inputValue(aBasisFunc).asShort();
    mSmoothness = dataBlock.inputValue(aSmoothness).asDouble();

    // Get pose position.
    MDataHandle poseHndl = dataBlock.inputValue(aPose, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    double poseX = poseHndl.child(aPoseX).asDouble();
    double poseY = poseHndl.child(aPoseY).asDouble();
    double poseZ = poseHndl.child(aPoseZ).asDouble();
    MPoint posePos = MPoint(poseX, poseY, poseZ);

    // Get distance matrix for targets position.
    MArrayDataHandle targetsPosHandle = dataBlock.inputArrayValue(aTarget, &status);
    mNumTargets = targetsPosHandle.elementCount();
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MPointArray targetsPos;
    for (unsigned i = 0; i < mNumTargets; i++) {
        targetsPosHandle.jumpToArrayElement(i);

        double targetX = targetsPosHandle.inputValue().child(aTargetX).asDouble();
        double targetY = targetsPosHandle.inputValue().child(aTargetY).asDouble();
        double targetZ = targetsPosHandle.inputValue().child(aTargetZ).asDouble();

        targetsPos.append(MPoint(targetX, targetY, targetZ));
    }
    MatrixXd targetsDistMatrix = getTargetsDistMatrix(targetsPos);

    // Get pose to targets distance matrix.
    MatrixXd poseToTargetsMatrix = getPoseToTargetsMatrix(posePos, targetsPos);

    if (plug == aOutWeight) {
        MatrixXd inWeightsMatrix;
        inWeightsMatrix.resize(mNumTargets, mNumTargets);
        makeIdentityMatrix(inWeightsMatrix);

        MatrixXd weightMatrix = targetsDistMatrix.inverse() * inWeightsMatrix;
        MatrixXd outWeightsMatrix = poseToTargetsMatrix * weightMatrix;

        MArrayDataHandle outWeightsArrayHndl = dataBlock.outputArrayValue(aOutWeight);
        MArrayDataBuilder builder = outWeightsArrayHndl.builder(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        for (unsigned i = 0; i < mNumTargets; i++) {
            MDataHandle elementHndl = builder.addElement(i, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            float weight = float(outWeightsMatrix(0, i));
            elementHndl.setFloat(weight);
        }
        status = outWeightsArrayHndl.set(builder);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (plug == aOutColor) {
        // Get inColors data
        MArrayDataHandle inColorsHndl = dataBlock.inputArrayValue(aInColor, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MFloatVectorArray inColors;
        unsigned int numInColors = inColorsHndl.elementCount();
        for (unsigned int i = 0; i < numInColors; i++) {
            inColorsHndl.jumpToArrayElement(i);
            inColors.append(inColorsHndl.inputValue().asFloatVector());
        }

        // Get inColors matrix
        MatrixXf inColorsMatrix;
        unsigned int numChannel(3);
        inColorsMatrix.resize(numInColors, numChannel);
        for (unsigned int i = 0; i < inColors.length(); i++) {
            for (unsigned int j = 0; j < numChannel; j++) {
                inColorsMatrix(i, j) = inColors[i][j];
            }
        }

        // Get weight matrix
        MatrixXf m_targetsDistMatrixF = targetsDistMatrix.cast<float>();
        MatrixXf weightMatrix = m_targetsDistMatrixF.inverse() * inColorsMatrix;

        // Get result
        MatrixXf m_poseToTargetsMatrixF = poseToTargetsMatrix.cast<float>();
        MatrixXf resultColor = m_poseToTargetsMatrixF * weightMatrix;

        // Set out color
        MDataHandle outColorHndl = dataBlock.outputValue(aOutColor, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MFloatVector outColor(resultColor(0, 0), resultColor(0, 1), resultColor(0, 2));
        outColorHndl.setMFloatVector(outColor);
    }

    if (plug == aOutMatrix) {
        // Get inMatrix data
        MArrayDataHandle inMatricesHndl = dataBlock.inputArrayValue(aInMatrix, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrixArray inMatrices;
        unsigned int numInMatrices = inMatricesHndl.elementCount();
        for (unsigned int i = 0; i < numInMatrices; i++) {
            inMatricesHndl.jumpToArrayElement(i);
            inMatrices.append(inMatricesHndl.inputValue().asMatrix());
        }

        // Get inMatrix matrix
        MatrixXd inMatrixMatrix;
        unsigned int numChannel = 16;
        inMatrixMatrix.resize(numInMatrices, numChannel);
        for (unsigned int i = 0; i < numInMatrices; i++) {
            for (unsigned int j = 0; j < numChannel; j++) {
                MDoubleArray flatMatrix = matrixToDoubleArray(inMatrices[i]);
                inMatrixMatrix(i, j) = flatMatrix[j];
            }
        }

        MatrixXd weightMatrix = targetsDistMatrix.inverse() * inMatrixMatrix;
        MatrixXd outMatrixMatrix = poseToTargetsMatrix * weightMatrix;
        
        MDoubleArray flatMatrix;
        for (unsigned int i = 0; i < numChannel; i++) {
            flatMatrix.append(outMatrixMatrix(0, i));
        }
        MMatrix resultMatrix = doubleArrayToMatrix(flatMatrix);

        MDataHandle outMatrixHndl = dataBlock.outputValue(aOutMatrix);
        outMatrixHndl.setMMatrix(resultMatrix);
    }

    dataBlock.setClean(plug);
    return MS::kSuccess;
}
