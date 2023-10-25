#include <maya/MFnPlugin.h>
#include "takRBF.h"


MStatus initializePlugin(MObject obj)
{
    MStatus status;

    MFnPlugin plugin(obj, "Tak", "1.0", "Any");

    status = plugin.registerNode(TakRBF::name, 
                                 TakRBF::id, 
                                 TakRBF::creator, 
                                 TakRBF::initialize, 
                                 MPxNode::kDependNode);
    if (status != MS::kSuccess) {
        MGlobal::displayError("Fail to register \"takRBF\" node.");
    }

    return MS::kSuccess;
}


MStatus uninitializePlugin(MObject obj)
{
    MStatus status;

    MFnPlugin plugin(obj);

    status = plugin.deregisterNode(TakRBF::id);
    if (status != MS::kSuccess) {
        MGlobal::displayError("Fail to deregister \"takRBF\" node.");
    }

    return MS::kSuccess;
}