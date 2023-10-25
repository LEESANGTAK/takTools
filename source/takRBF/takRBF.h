#pragma once

#include <iostream>
#include <Eigen/Dense>

#include <maya/MPxNode.h>
#include <maya/MTypeId.h>
#include <maya/MString.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnGenericAttribute.h>
#include <maya/MFloatPoint.h>
#include <maya/MGlobal.h>
#include <maya/MPointArray.h>
#include <maya/MMatrix.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MArrayDataBuilder.h>
#include <maya/MFloatVectorArray.h>
#include <maya/MMAtrixArray.h>


using namespace Eigen;
using namespace std;


class TakRBF : public MPxNode
{
public:
    static MTypeId id;
    static MString name;

    static MObject aBasisFunc;
    static MObject aSmoothness;
    static MObject aPoseX;
    static MObject aPoseY;
    static MObject aPoseZ;
    static MObject aPose;

    static MObject aOutWeight;
    static MObject aTargetX;
    static MObject aTargetY;
    static MObject aTargetZ;
    static MObject aTarget;

    static MObject aOutColor;
    static MObject aInColor;

    static MObject aOutMatrix;
    static MObject aInMatrix;

public:
    static void* creator();
    static MStatus initialize();

private:
    short mBasisFunc;
    double mSmoothness;
    unsigned int mNumTargets;

private:
    MatrixXd getTargetsDistMatrix(const MPointArray& targetsPos);
    MatrixXd getPoseToTargetsMatrix(const MPoint& posePos, const MPointArray& targetsPos);
    void makeIdentityMatrix(MatrixXd& matrix);
    double RBF(const double& dist);
    MDoubleArray matrixToDoubleArray(const MMatrix& matirx);
    MMatrix doubleArrayToMatrix(const MDoubleArray& flatMatrix);

public:
    TakRBF();
    virtual ~TakRBF() override;

    virtual MStatus compute(const MPlug& plug, MDataBlock& dataBlock) override;
};