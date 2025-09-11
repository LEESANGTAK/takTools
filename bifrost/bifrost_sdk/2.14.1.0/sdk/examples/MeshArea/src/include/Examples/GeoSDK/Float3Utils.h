//-
// ===========================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// ===========================================================================
//+

/// \file Float3Utils.h
/// \brief Math utility functions for float3s.

#ifndef EXAMPLES_MATH_UTILS_H
#define EXAMPLES_MATH_UTILS_H

#include <Bifrost/Math/Types.h>

#include <functional>
#include <cmath>
#include <limits>

namespace Examples {
namespace Math {
using float3 = Bifrost::Math::float3;

/// \brief Componentwise addition of two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return The sum of v1 and v2.
inline float3 operator+(const float3& v1, const float3& v2) {
    float3 res = {v1.x + v2.x, v1.y + v2.y, v1.z + v2.z};
    return res;
}

/// \brief Componentwise subtraction of two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return The difference of v1 and v2.
inline float3 operator-(const float3& v1, const float3& v2) {
    float3 res = {v1.x - v2.x, v1.y - v2.y, v1.z - v2.z};
    return res;
}

/// \brief Compnentwise negation of a float3.
/// \param v1 The float3 to negate.
/// \return The negation of v1.
inline float3 operator-(const float3& v1) {
    float3 res = {-v1.x, -v1.y, -v1.z};
    return res;
}

/// \brief Componentwise addition of a two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return The sum in v1.
inline float3& operator+=(float3& v1, const float3& v2) {
    v1.x += v2.x;
    v1.y += v2.y;
    v1.z += v2.z;
    return v1;
}

/// \brief Componentwise subtraction of a two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return The difference in v1.
inline float3& operator-=(float3& v1, const float3& v2) {
    v1.x -= v2.x;
    v1.y -= v2.y;
    v1.z -= v2.z;
    return v1;
}

/// \brief Componentwise multiplication of a two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return The product in v1.
inline float3& operator*=(float3& v1, const float3& v2) {
    v1.x *= v2.x;
    v1.y *= v2.y;
    v1.z *= v2.z;
    return v1;
}

/// \brief Componentwise division of a two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return The quotient in v1.
inline float3& operator/=(float3& v1, const float3& v2) {
    if (std::abs(v2.x) > std::numeric_limits<float>::min()) v1.x /= v2.x;
    if (std::abs(v2.y) > std::numeric_limits<float>::min()) v1.y /= v2.y;
    if (std::abs(v2.z) > std::numeric_limits<float>::min()) v1.z /= v2.z;
    return v1;
}

/// \brief Componentwise division of a float3 by a scalar.
/// \param v1 The float3.
/// \param t The scalar.
/// \return The quotient in v1.
inline float3& operator/=(float3& v1, const float t) {
    if (std::abs(t) > std::numeric_limits<float>::min()) {
        v1.x /= t;
        v1.y /= t;
        v1.z /= t;
    }
    return v1;
}

/// \brief Componentwise multiplication of a float3 by a scalar.
/// \param v1 The float3.
/// \param t The scalar.
/// \return The product in v1.
inline float3& operator*=(float3& v1, const float t) {
    v1.x *= t;
    v1.y *= t;
    v1.z *= t;
    return v1;
}

/// \brief Cross product of two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return The cross product of v1 and v2.
inline float3 cross(const float3& v1, const float3& v2) {
    return float3{v1.y * v2.z - v1.z * v2.y, v1.z * v2.x - v1.x * v2.z,
                  v1.x * v2.y - v1.y * v2.x};
}

/// \brief Dot product of two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return The dot product of v1 and v2.
inline float dot(const float3& v1, const float3& v2) {
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
}

/// \brief Squared magnitude of a float3.
/// \param v The float3.
/// \return The squared magnitude of v.
inline float magSqr(const float3& v) {
    return v.x * v.x + v.y * v.y + v.z * v.z;
}

/// \brief Magnitude of a float3.
/// \param v The float3.
/// \return The magnitude of v.
inline float mag(const float3& v) { return std::sqrt(magSqr(v)); }

/// \brief Distance between two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return The distance between v1 and v2.
inline float dist(const float3& v1, const float3& v2) {
    return mag(v1-v2);
}

/// \brief Normalize a float3.
/// \param v The float3.
/// \param def The default value to return if the magnitude of v is zero.
/// \return The normalized float3.
inline float3 normalize(const float3& v, const float3& def) {
    float3      out_v(v);
    const float vmag = mag(out_v);
    if (std::abs(vmag) > std::numeric_limits<float>::min())
        return out_v *= float(1) / vmag;
    else
        return def;
}

/// \brief Normalize a float3.
/// \param v The float3.
/// \return The normalized float3 or itself if the magnitude is zero.
inline float3 normalize(const float3& v) { return normalize(v, v); }

/// \brief Componentwise smaller-than of two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return True if v1 is smaller than v2, false otherwise.
inline bool operator<(const float3& v1, const float3& v2) {
    if( v1.x < v2.x ) return true;
    if( v2.x < v1.x ) return false;
    if( v1.y < v2.y ) return true;
    if( v2.y < v1.y ) return false;
    if( v1.z < v2.z ) return true;
    if( v2.z < v1.z ) return false;
    return false;
}

/// \brief Componentwise greater-than of two float3s.
/// \param v1 The first float3.
/// \param v2 The second float3.
/// \return True if v1 is greater than v2, false otherwise.
inline bool operator>(const float3& v1, const float3& v2) {
    if( v1.x > v2.x ) return true;
    if( v2.x > v1.x ) return false;
    if( v1.y > v2.y ) return true;
    if( v2.y > v1.y ) return false;
    if( v1.z > v2.z ) return true;
    if( v2.z > v1.z ) return false;
    return false;
}

} // namespace Math
} // namespace Examples

#endif // EXAMPLES_MATH_UTILS_H
