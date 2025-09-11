//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file TwistDeformerOps.h
/// \brief Twist operator.

#ifndef TWIST_DEFORMER_OPS_H
#define TWIST_DEFORMER_OPS_H

#include "TwistDeformerOpsExport.h"

#include <Bifrost/Math/Types.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Cpp/Annotate.h>

namespace Examples {
namespace GeoSDK {

/// \brief Twist deformer for point-based geometry.
///
/// \param points The point-based geometry to deform.
/// \param twist_amount The amount of rotation to apply, in radians.
/// \param position The point in world-space, that the twist will be centered around.
/// \param axis The axis of rotation.
///
/// \note Point-based geometry includes meshes, strands, points, and instances.
TWIST_DEFORMER_OPS_DECL
void twist_points(Bifrost::Object& points      AMINO_ANNOTATE("Amino::InOut outName=out_points"),
                  float                        twist_amount,
                  Bifrost::Math::float3 const& position,
                  Bifrost::Math::float3 const& axis AMINO_ANNOTATE(
                      "Amino::Port value={x:0.0f, y:1.0f, z:0.0f}")) AMINO_ANNOTATE("Amino::Node");

} // namespace GeoSDK
} // namespace Examples

#endif // TWIST_DEFORMER_OPS_H
