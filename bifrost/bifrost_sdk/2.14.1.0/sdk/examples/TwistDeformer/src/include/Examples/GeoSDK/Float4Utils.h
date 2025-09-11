//-

// ===========================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// ===========================================================================

//+

#ifndef EXAMPLES_MATH_FLOAT4_UTILS_H
#define EXAMPLES_MATH_FLOAT4_UTILS_H

#include <Bifrost/Math/Types.h>

namespace Examples {
namespace Math {
using Bifrost::Math::float4;

/// \brief Componentwise multiplication of two float4s.
/// \param v1 The first float4.
/// \param v2 The second float4.
/// \return The product of v1 and v2.
inline float4& operator*=(float4& v1, const float4& v2) {
    v1.x *= v2.x;
    v1.y *= v2.y;
    v1.z *= v2.z;
    v1.w *= v2.w;
    return v1;
}

/// \brief Componentwise multiplication of a float4 by a scalar.
/// \param v1 The float4.
/// \param t The scalar.
/// \return The product of v1 and t.
inline float4& operator*=(float4& v1, const float t) {
    v1.x *= t;
    v1.y *= t;
    v1.z *= t;
    v1.w *= t;
    return v1;
}

/// \brief Componentwise subtraction of two float4s.
/// \param v1 The first float4.
/// \param v2 The second float4.
/// \return v1 minus v2.
inline float4 operator-(const float4& v1, const float4& v2) {
    float4 res = {v1.x - v2.x, v1.y - v2.y, v1.z - v2.z, v1.w - v2.w};
    return res;
}

/// \brief Componentwise divison of two float4s.
/// \param v1 The first float4.
/// \param v2 The second float4.
/// \return v1 divided componentwise by v2.
inline float4& operator/=(float4& v1, const float4& v2) {
    if (std::abs(v2.x) > std::numeric_limits<float>::min()) v1.x /= v2.x;
    if (std::abs(v2.y) > std::numeric_limits<float>::min()) v1.y /= v2.y;
    if (std::abs(v2.z) > std::numeric_limits<float>::min()) v1.z /= v2.z;
    if (std::abs(v2.w) > std::numeric_limits<float>::min()) v1.w /= v2.w;
    return v1;
}

/// \brief Componentwise division of a float4 by a scalar.
/// \param v1 The float4.
//  \param t The scalar.
/// \return v1 divided componentwise by t.
inline float4& operator/=(float4& v1, const float t) {
    if (std::abs(t) > std::numeric_limits<float>::min()) {
        v1.x /= t;
        v1.y /= t;
        v1.z /= t;
        v1.w /= t;
    }
    return v1;
}

} // namespace Math
} // namespace Examples

#endif // EXAMPLES_MATH_FLOAT4_UTILS_H
