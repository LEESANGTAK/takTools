//-
// ===========================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// ===========================================================================
//+

/// \file Float2Utils.h
/// \brief Math utility functions for float2s.

#ifndef EXAMPLES_MATH_FLOAT2_UTILS_H
#define EXAMPLES_MATH_FLOAT2_UTILS_H

#include <Bifrost/Math/Types.h>

#include <cmath>
#include <functional>
#include <limits>

namespace Examples {
namespace Math {
using Bifrost::Math::float2;

/// \brief Distance between two float2s.
/// \param v1 The first float2.
/// \param v2 The second float2.
/// \return The distance between v1 and v2.
inline float dist(const float2& v1, const float2& v2) {
    const float2 dv = {v1.x - v2.x, v1.y - v2.y};
    return std::sqrt(dv.x * dv.x + dv.y * dv.y);
}

/// \brief Componentwise division of a two float2s.
/// \param v1 The first float2.
/// \param v2 The second float2.
/// \return The quotient in v1.
inline float2& operator/=(float2& v1, const float t) {
    if (std::abs(t) > std::numeric_limits<float>::min()) {
        v1.x /= t;
        v1.y /= t;
    }
    return v1;
}

/// \brief Componentwise addition of a two float2s.
/// \param v1 The first float2.
/// \param v2 The second float2.
/// \return The sum in v1.
inline float2& operator+=(float2& v1, const float2& v2) {
    v1.x += v2.x;
    v1.y += v2.y;
    return v1;
}

} // namespace Math
} // namespace Examples

#endif // EXAMPLES_MATH_UTILS_H
