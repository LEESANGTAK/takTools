#include "takCurveCollision.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin(MObject obj) {
    MStatus status;

    MFnPlugin pluginFn(obj, "tak", "1.0", "Any");

    status = pluginFn.registerNode(
        TakCurveCollision::name,
        TakCurveCollision::id,
        TakCurveCollision::creator,
        TakCurveCollision::initialize,
        MPxNode::kDeformerNode
    );
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return MS::kSuccess;
}

MStatus uninitializePlugin(MObject obj) {
    MStatus status;

    MFnPlugin pluginFn(obj);

    status = pluginFn.deregisterNode(
        TakCurveCollision::id
    );
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return MS::kSuccess;
}