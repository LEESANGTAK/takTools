//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "MeshWeldUVOps.h"

#include <Examples/GeoSDK/MeshWeldUV.h>

#include <Bifrost/Geometry/Validator.h>

void Examples::GeoSDK::weld_uvs(Bifrost::Object&     mesh,
                                float                tolerance,
                                Amino::String const& uv_set_name) {
    // In general, geometry from the graph should be validated before being
    // processed by C++ algorithms. This makes writing the algorithms somewhat
    // easier, as one can make assertions about the data without checking for
    // validity inside the algorithm.
    if (!Bifrost::Geometry::validateMesh(mesh)) return;

    Examples::GeoSDK::MeshUVWelder welder(mesh);
    welder.weld(tolerance, uv_set_name);
}
