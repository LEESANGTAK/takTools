//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include <Examples/GeoSDK/TwistDeformer.h>

#include <Examples/GeoSDK/Float3Utils.h>
#include <Examples/GeoSDK/Float4x4Utils.h>

#include <Bifrost/Geometry/GeoProperty.h>
#include <Bifrost/Geometry/GeoPropertyGuard.h>
#include <Bifrost/Geometry/Validator.h>

#include <Amino/Core/Any.h>

#include <algorithm>
#include <vector>

using Bifrost::Geometry::Index;
using Bifrost::Math::float3;
using Bifrost::Math::float4x4;

using namespace Examples::Math;

namespace {

/// \brief Creates a matrix from the given translation vector.
float4x4 translationMatrix(float3 const& translation) {
    float4x4 result{};
    result.c0.x = 1.0F;
    result.c1.y = 1.0F;
    result.c2.z = 1.0F;

    result.c3.x = translation.x;
    result.c3.y = translation.y;
    result.c3.z = translation.z;
    result.c3.w = 1.0F;
    return result;
}

/// \brief Creates a rotation matrix from the given axis and angle.
/// ref: https://www.euclideanspace.com/maths/geometry/rotations/conversions/angleToMatrix/
///
/// \param axis The axis of rotation. It must be normalized
/// \param angle The angle of rotation in radians. It represents a right-handed rotation.
/// \return A rotation matrix.
float4x4 rotationMatrix(float3 const& axis, float angle) {
    float4x4    result{};
    const float c = cosf(angle);
    const float s = sinf(angle);
    const float t = 1.0F - c;
    const float x = axis.x;
    const float y = axis.y;
    const float z = axis.z;
    result.c0.x   = t * x * x + c;
    result.c0.y   = t * x * y + z * s;
    result.c0.z   = t * x * z - y * s;
    result.c0.w   = 0.0F;
    result.c1.x   = t * x * y - z * s;
    result.c1.y   = t * y * y + c;
    result.c1.z   = t * y * z + x * s;
    result.c1.w   = 0.0F;
    result.c2.x   = t * x * z + y * s;
    result.c2.y   = t * y * z - x * s;
    result.c2.z   = t * z * z + c;
    result.c2.w   = 0.0F;
    result.c3.x   = 0.0F;
    result.c3.y   = 0.0F;
    result.c3.z   = 0.0F;
    result.c3.w   = 1.0F;
    return result;
}
} // namespace

Examples::GeoSDK::TwistDeformer::TwistDeformer(Bifrost::Object& points) : m_points(points) {}

void Examples::GeoSDK::TwistDeformer::deform(float                        twistAmount,
                                             Bifrost::Math::float3 const& twistPosition,
                                             Bifrost::Math::float3 const& twistAxis) {
    float3 const kUp = {0.0F, 1.0F, 0.0F};

    // bail out on bad input.
    if (mag(twistAxis) < 0.0001F) return;

    // Create the matrix that transforms the points into the space of the twist deformer. In this
    // space the twist is always around the origin, along the kUp axis.
    auto worldToTwist = [&]() {
        // First move the points to the origin.
        auto const negativePos = twistPosition * -1.0F;
        auto const tMatrix     = translationMatrix(negativePos);

        // Get the axis of rotation to line up the twist axis and kUp.
        auto const twistAxisNormalized = normalize(twistAxis, kUp);
        auto const twistAxisCrossUp    = normalize(cross(twistAxisNormalized, kUp), kUp);

        // Get the angle between axis and kUp.
        auto const twistAxisDotUp        = dot(twistAxisNormalized, kUp);
        auto const angleBetweenAxisAndUp = acosf(twistAxisDotUp);

        // Rotate local space so the input axis lines up with the kUp axis.
        const float4x4 rMatrix = rotationMatrix(twistAxisCrossUp, angleBetweenAxisAndUp);

        return rMatrix * tMatrix;
    }();

    float4x4 twistToWorld{};
    if (!Examples::Math::invert(worldToTwist, twistToWorld)) return;

    // Get write access to the point positions through a property guard.
    //
    // The guard will extract the data array from the mesh, and provide non-const/write access to it.
    // Upon destruction, the guard will set the data back into the mesh. If there are no other
    // references to the data, they will be modified in-place and no copy-on-write will occur.
    // See Amino::MutablePtr
    auto positions = Bifrost::Geometry::createDataGeoPropGuard<Bifrost::Math::float3>(
        m_points, Bifrost::Geometry::sPointPosition);

    // Since it is a precondition that the input geometry is a valid points geo, there is no need
    // to check for a nullptr, as the point positions are a canonical property of all point-based
    // geometries.
    assert(positions);

    // transform the points into local twist space.
    for (auto& position : positions.data()) {
        position = transform(worldToTwist, position);
    }

    // Convert the twist amount from degrees to radians.
    twistAmount *= 3.14159265358979323846F / 180.0F;

    // Get the bounding box of the transformed points.
    float minY = std::numeric_limits<float>::max();
    float maxY = std::numeric_limits<float>::lowest();
    for (auto& position : positions.data()) {
        minY = std::min(minY, position.y);
        maxY = std::max(maxY, position.y);
    }

    // Apply the twist. The normalized value of the y-coordinate is used to determine the amount of
    // rotation to apply.
    auto const ySize = maxY - minY;
    for (auto& position : positions.data()) {
        auto const y         = position.y - minY;
        auto const yTwist    = twistAmount * (y / ySize);
        auto const rotMatrix = rotationMatrix(kUp, yTwist);
        position             = transform(rotMatrix, position);
    }

    // transform the points back into world space.
    for (auto& position : positions.data()) {
        position = transform(twistToWorld, position);
    }

    // Upon destruction, the updated positions will be set back into the mesh by the
    // DataGeoPropGuard.
}
