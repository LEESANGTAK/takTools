//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They
// may not be disclosed to, copied  or used by any third party without the
// prior written consent of Autodesk, Inc.
// =============================================================================
//+

#include "MeshAreaOps.h"

#include <Examples/GeoSDK/MeshArea.h>

float Examples::GeoSDK::compute_mesh_area(Bifrost::Object const &mesh, MeshAreaComputeMode mode){
    Examples::GeoSDK::FaceMeshView faceContainer(mesh);

    switch (mode) {
        case MeshAreaComputeMode::Newell: return faceContainer.computeAreaNewell();
        case MeshAreaComputeMode::Shoelace: return faceContainer.computeAreaShoelace();
        case MeshAreaComputeMode::FanOut: return faceContainer.computeAreaFanOut();
    }
    assert((false) && "All cases are covered");
    return 0.0F;
}
