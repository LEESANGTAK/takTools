//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file TwistDeformer.h
/// \brief Class to help twist the positions of a point-based geometry.

#ifndef TWIST_DEFORMER_H
#define TWIST_DEFORMER_H

#include "TwistDeformerExport.h"

#include <Bifrost/Geometry/GeoPropertyKey.h>
#include <Bifrost/Math/Types.h>
#include <Bifrost/Object/Object.h>

#include <Amino/Core/Array.h>
#include <Amino/Core/String.h>

namespace Examples {
namespace GeoSDK {

/// \brief  Class to twist a point-based geometry.
///
/// A point-based geometry is any geometry that adheres to the points geometry schema. The schema
/// simply requires the geometry to contain a point_component property and point_position property.
class TWIST_DEFORMER_DECL TwistDeformer {
public:
    TwistDeformer()                                 = delete;
    TwistDeformer(TwistDeformer const&)             = delete;
    TwistDeformer(TwistDeformer&&)                  = delete;
    TwistDeformer(Bifrost::Object&& points)         = delete;
    TwistDeformer& operator=(TwistDeformer const&)  = delete;
    TwistDeformer& operator=(TwistDeformer const&&) = delete;

    /// \brief Construct a deformer for the given geometry.
    /// \param points The point-based geometry to deform.
    explicit TwistDeformer(Bifrost::Object& points);

public:
    /// \brief Deform the geometry.
    /// \pre The geometry must be a valid points geo.
    /// \param twistAmount The amount of rotation in radians.
    /// \param twistPosition The point in world-space, that the twist will be centered around.
    /// \param twistAxis The axis of rotation.
    void deform(float                        twistAmount,
                Bifrost::Math::float3 const& twistPosition = {},
                Bifrost::Math::float3 const& twistAxis     = {0.0F, 1.0F, 0.0F});

private:
    Bifrost::Object& m_points;
};

} // namespace GeoSDK
} // namespace Examples

#endif // TWIST_DEFORMER_H
