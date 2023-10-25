#include "takCurveCollision.h"

MTypeId TakCurveCollision::id(0x00002740);
MString TakCurveCollision::name("takCurveCollision");

MObject TakCurveCollision::colliderMesh;
MObject TakCurveCollision::colliderBoundingBox;
MObject TakCurveCollision::colliderBoundingBoxMin;
MObject TakCurveCollision::colliderBoundingBoxMax;
MObject TakCurveCollision::colliderBoundingBoxSize;
MObject TakCurveCollision::colliderWorldMatrix;
MObject TakCurveCollision::aThreshold;
MObject TakCurveCollision::aOffset;
MObject TakCurveCollision::aSmooth;

TakCurveCollision::TakCurveCollision() {};
TakCurveCollision::~TakCurveCollision() {};

void* TakCurveCollision::creator() {
    return new TakCurveCollision();
}

MStatus TakCurveCollision::initialize() {
    MStatus status;

    MFnNumericAttribute numAttr;
    MFnTypedAttribute typeAttr;
    MFnCompoundAttribute compAttr;
    MFnMatrixAttribute matrixAttr;

    colliderMesh = typeAttr.create("colliderMesh", "cm", MFnData::kMesh);
    typeAttr.setHidden(true);

    colliderBoundingBoxMin = numAttr.createPoint("colliderBoundingBoxMin", "cbbn");
    colliderBoundingBoxMax = numAttr.createPoint("colliderBoundingBoxMax", "cbbx");
    colliderBoundingBoxSize = numAttr.createPoint("colliderBoundingBoxSize", "cbbs");
    colliderBoundingBox = compAttr.create("colliderBoundingBox", "cbb");
    compAttr.addChild(colliderBoundingBoxMin);
    compAttr.addChild(colliderBoundingBoxMax);
    compAttr.addChild(colliderBoundingBoxSize);

    colliderWorldMatrix = matrixAttr.create("colliderWorldMatrix", "cwm");

    aThreshold = numAttr.create("aThreshold", "cth", MFnNumericData::kDouble, 50.0);
    numAttr.setKeyable(true);

    aOffset = numAttr.create("aOffset", "coff", MFnNumericData::kFloat, 0.0f);
    numAttr.setMin(0.0f);
    numAttr.setKeyable(true);

    aSmooth = numAttr.create("aSmooth", "cs", MFnNumericData::kInt, 0);
    numAttr.setMin(0);
    numAttr.setKeyable(true);

    addAttribute(colliderMesh);
    addAttribute(colliderBoundingBox);
    addAttribute(colliderWorldMatrix);
    addAttribute(aThreshold);
    addAttribute(aOffset);
    addAttribute(aSmooth);

    attributeAffects(colliderMesh, outputGeom);
    attributeAffects(colliderBoundingBox, outputGeom);
    attributeAffects(colliderWorldMatrix, outputGeom);
    attributeAffects(aThreshold, outputGeom);
    attributeAffects(aOffset, outputGeom);
    attributeAffects(aSmooth, outputGeom);

    return MS::kSuccess;
}

MStatus TakCurveCollision::deform(MDataBlock& dataBlock, MItGeometry& geoIter, const MMatrix& localToWorldMatirx, unsigned int geoIndex) {
    MStatus status;

    float env = dataBlock.inputValue(envelope).asFloat();
    if (env == 0.0f) {
        return MS::kSuccess;
    }

    double threshold = dataBlock.inputValue(aThreshold).asDouble();
    float offset = dataBlock.inputValue(aOffset).asFloat();
    int smooth = dataBlock.inputValue(aSmooth).asInt();

    MArrayDataHandle inputArrayHndl = dataBlock.outputArrayValue(input, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    inputArrayHndl.jumpToElement(geoIndex);
    MDataHandle inputGeoHndl = inputArrayHndl.outputValue();
    MObject inputCrv = inputGeoHndl.child(inputGeom).asNurbsCurve();
    MBoundingBox curveBB;
    getCurveBoundingBox(inputCrv, curveBB);

    MPoint colliderBBMin = dataBlock.inputValue(colliderBoundingBoxMin).asVector();
    MPoint colliderBBMax = dataBlock.inputValue(colliderBoundingBoxMax).asVector();
    MMatrix colliderWsMatrix = dataBlock.inputValue(colliderWorldMatrix).asMatrix();
    MBoundingBox colliderBB;
    colliderBB.expand(colliderBBMin);
    colliderBB.expand(colliderBBMax);
    colliderBB.transformUsing(colliderWsMatrix);

    if (!curveBB.intersects(colliderBB, threshold)) {
        return MS::kSuccess;
    }

    MDataHandle meshHndl = dataBlock.inputValue(colliderMesh, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MObject colliderMesh = meshHndl.asMesh();
    if (colliderMesh.isNull()) {
        return MS::kSuccess;
    }
    MFnMesh meshFn(colliderMesh, &status);

    // Get deformed cvs
    MPoint cvPnt, collidePnt;
    MVector normal, cvToCollidePntVector;
    double dotResult;
    MMatrix worldToLocalMatrix = localToWorldMatirx.inverse();
    MPointArray cvsDeformed;
    MIntArray collidingIndices;
    while (!geoIter.isDone()) {
        cvPnt = geoIter.position();
        cvPnt *= localToWorldMatirx;
        status = meshFn.getClosestPointAndNormal(cvPnt, collidePnt, normal, MSpace::kWorld);
        collidePnt += normal * offset;
        cvToCollidePntVector = collidePnt - cvPnt;
        dotResult = normal * -cvToCollidePntVector;
        if (dotResult < 0.0) {
            cvPnt += cvToCollidePntVector * env;
            collidingIndices.append(geoIter.index());
        }
        cvsDeformed.append(cvPnt);
        geoIter.next();
    }

    if (smooth) {
        MPointArray smoothedPoints;
        for (int i = 0; i < smooth; i++) {
            smoothPoints(cvsDeformed);
        }
    }

    // Set result
    geoIter.reset();
    int index = 0;
    while (!geoIter.isDone()) {
        cvPnt = cvsDeformed[index] * worldToLocalMatrix;
        geoIter.setPosition(cvPnt);
        index++;
        geoIter.next();
    }

    return MS::kSuccess;
}

MStatus TakCurveCollision::getCurveBoundingBox(MObject& curve, MBoundingBox& curveBB) {
    MStatus status;

    MItCurveCV cvIt = MItCurveCV(curve, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    while (!cvIt.isDone()) {
        curveBB.expand(cvIt.position(MSpace::kWorld));
        cvIt.next();
    }

    return MS::kSuccess;
}

MStatus TakCurveCollision::smoothPoints(MPointArray& points) {
    MStatus status;

    MPointArray tempPoints(points);

    for (unsigned i = 1; i < tempPoints.length()-1; i++) {
        MVector prePoint = MVector(tempPoints[i - 1]);
        MVector curPoint = MVector(tempPoints[i]);
        MVector postPoint = MVector(tempPoints[i + 1]);

        points[i] = MPoint((prePoint + curPoint + postPoint) / 3);
    }

    return MS::kSuccess;
}
