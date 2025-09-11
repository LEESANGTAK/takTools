//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "TwistDeformerOps.h"

#include <Examples/GeoSDK/TwistDeformer.h>

#include <Bifrost/Geometry/Validator.h>

void Examples::GeoSDK::twist_points(Bifrost::Object&             points,
                                    float                        twist_amount,
                                    Bifrost::Math::float3 const& position,
                                    Bifrost::Math::float3 const& axis) {
    // Validate the input geometry, since in general, we cannot assume geometry coming from the
    // graph is well-formed.
    Bifrost::Geometry::PointCloudValidator v;
    if (!v.validate(points)) return;

    Examples::GeoSDK::TwistDeformer twister(points);
    twister.deform(twist_amount, position, axis);
}
