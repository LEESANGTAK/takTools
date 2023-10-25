#pragma once

#include <maya/MPxDeformerNode.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MPoint.h>
#include <maya/MItGeometry.h>
#include <maya/MGlobal.h>
#include <maya/MString.h>
#include <maya/MFnMesh.h>
#include <maya/MMatrix.h>
#include <maya/MBoundingBox.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MDagPath.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MPointArray.h>
#include <maya/MItCurveCV.h>
#include <maya/MIntArray.h>

class TakCurveCollision : MPxDeformerNode {
public:
    static MTypeId id;
    static MString name;

    static MObject colliderMesh;
    static MObject colliderBoundingBox;
    static MObject colliderBoundingBoxMin;
    static MObject colliderBoundingBoxMax;
    static MObject colliderBoundingBoxSize;
    static MObject colliderWorldMatrix;
    static MObject aThreshold;
    static MObject aOffset;
    static MObject aSmooth;

public:
            TakCurveCollision();
    virtual ~TakCurveCollision();

    static  void* creator();
    static  MStatus initialize();
    virtual MStatus deform(
        MDataBlock& dataBlock,
        MItGeometry& geoIter,
        const MMatrix& localToWorldMatrix,
        unsigned int geomIndex
    );

private:
    MStatus getCurveBoundingBox(MObject& curve, MBoundingBox& curveBB);
    MStatus smoothPoints(MPointArray& points);
};