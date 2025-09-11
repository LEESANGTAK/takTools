//-
// ===========================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// ===========================================================================
//+

#ifndef EXAMPLE_MATH_FLOAT4X4_UTILS_H
#define EXAMPLE_MATH_FLOAT4X4_UTILS_H

#include "Float4Utils.h"

#include <Bifrost/Math/Types.h>

#include <cmath>

namespace Examples {
namespace Math {
using Bifrost::Math::float4x4;

/// \brief Componentwise multiplication of two 4x4 matrices
/// \param v1 The first 4x4 matrix.
/// \param v2 The second 4x4 matrix.
/// \return v1 multiplied componentwise by v2.
inline float4x4& operator*=(float4x4& v1, const float4x4& v2) {
    v1.c0 *= v2.c0;
    v1.c1 *= v2.c1;
    v1.c2 *= v2.c2;
    v1.c3 *= v2.c3;
    return v1;
}

/// \brief Componentwise multiplication of a 4x4 matrix by a scalar
/// \param v1 The 4x4 matrix.
/// \param t The scalar.
/// \return v1 multiplied componentwise by t.
inline float4x4& operator*=(float4x4& v1, const float t) {
    v1.c0 *= t;
    v1.c1 *= t;
    v1.c2 *= t;
    v1.c3 *= t;
    return v1;
}

/// \brief Componentwise division of two 4x4 matrices
/// \param v1 The first 4x4 matrix.
/// \param v2 The second 4x4 matrix.
/// \return v1 divided componentwise by v2.
inline float4x4& operator/=(float4x4& v1, const float4x4& v2) {
    v1.c0 /= v2.c0;
    v1.c1 /= v2.c1;
    v1.c2 /= v2.c2;
    v1.c3 /= v2.c3;
    return v1;
}

/// \brief Componentwise division of a 4x4 matrix by a scalar
/// \param v1 The 4x4 matrix.
/// \param t The scalar.
/// \return v1 divided componentwise by t.
inline float4x4& operator/=(float4x4& v1, const float t) {
    v1.c0 /= t;
    v1.c1 /= t;
    v1.c2 /= t;
    v1.c3 /= t;
    return v1;
}

/// \brief Transform 3d vector by 4x4 transform
/// \param matrix The 4x4 transform matrix.
/// \param vec The 3d vector to transform.
/// \param w controls the interpretation of vec. If w is 1.0, vec is interpreted as a point and a
/// translation is applied. If w is 0.0, vec is interpreted as a direction and no translation is
/// applied.
/// \return The transformed vector.
inline Bifrost::Math::float3 transform(const Bifrost::Math::float4x4& matrix,
                                       const Bifrost::Math::float3&   vec,
                                       float                          w = 1.0F) {
    Bifrost::Math::float4 r{};
    r.x = vec.x * matrix.c0.x + vec.y * matrix.c1.x + vec.z * matrix.c2.x + w * matrix.c3.x;
    r.y = vec.x * matrix.c0.y + vec.y * matrix.c1.y + vec.z * matrix.c2.y + w * matrix.c3.y;
    r.z = vec.x * matrix.c0.z + vec.y * matrix.c1.z + vec.z * matrix.c2.z + w * matrix.c3.z;
    r.w = vec.x * matrix.c0.w + vec.y * matrix.c1.w + vec.z * matrix.c2.w + w * matrix.c3.w;
    return {r.x, r.y, r.z};
}

/// \brief Multiply two matrices
/// \param m1 The first matrix.
/// \param m2 The second matrix.
/// \return The product of m1 and m2.
inline Bifrost::Math::float4x4 operator*(const Bifrost::Math::float4x4& m1,
                                         const Bifrost::Math::float4x4& m2) {
    Bifrost::Math::float4x4 r{};

    // row 0
    r.c0.x = m1.c0.x * m2.c0.x + m1.c1.x * m2.c0.y + m1.c2.x * m2.c0.z + m1.c3.x * m2.c0.w;
    r.c1.x = m1.c0.x * m2.c1.x + m1.c1.x * m2.c1.y + m1.c2.x * m2.c1.z + m1.c3.x * m2.c1.w;
    r.c2.x = m1.c0.x * m2.c2.x + m1.c1.x * m2.c2.y + m1.c2.x * m2.c2.z + m1.c3.x * m2.c2.w;
    r.c3.x = m1.c0.x * m2.c3.x + m1.c1.x * m2.c3.y + m1.c2.x * m2.c3.z + m1.c3.x * m2.c3.w;

    // row 1
    r.c0.y = m1.c0.y * m2.c0.x + m1.c1.y * m2.c0.y + m1.c2.y * m2.c0.z + m1.c3.y * m2.c0.w;
    r.c1.y = m1.c0.y * m2.c1.x + m1.c1.y * m2.c1.y + m1.c2.y * m2.c1.z + m1.c3.y * m2.c1.w;
    r.c2.y = m1.c0.y * m2.c2.x + m1.c1.y * m2.c2.y + m1.c2.y * m2.c2.z + m1.c3.y * m2.c2.w;
    r.c3.y = m1.c0.y * m2.c3.x + m1.c1.y * m2.c3.y + m1.c2.y * m2.c3.z + m1.c3.y * m2.c3.w;

    // row 2
    r.c0.z = m1.c0.z * m2.c0.x + m1.c1.z * m2.c0.y + m1.c2.z * m2.c0.z + m1.c3.z * m2.c0.w;
    r.c1.z = m1.c0.z * m2.c1.x + m1.c1.z * m2.c1.y + m1.c2.z * m2.c1.z + m1.c3.z * m2.c1.w;
    r.c2.z = m1.c0.z * m2.c2.x + m1.c1.z * m2.c2.y + m1.c2.z * m2.c2.z + m1.c3.z * m2.c2.w;
    r.c3.z = m1.c0.z * m2.c3.x + m1.c1.z * m2.c3.y + m1.c2.z * m2.c3.z + m1.c3.z * m2.c3.w;

    // row 3
    r.c0.w = m1.c0.w * m2.c0.x + m1.c1.w * m2.c0.y + m1.c2.w * m2.c0.z + m1.c3.w * m2.c0.w;
    r.c1.w = m1.c0.w * m2.c1.x + m1.c1.w * m2.c1.y + m1.c2.w * m2.c1.z + m1.c3.w * m2.c1.w;
    r.c2.w = m1.c0.w * m2.c2.x + m1.c1.w * m2.c2.y + m1.c2.w * m2.c2.z + m1.c3.w * m2.c2.w;
    r.c3.w = m1.c0.w * m2.c3.x + m1.c1.w * m2.c3.y + m1.c2.w * m2.c3.z + m1.c3.w * m2.c3.w;

    return r;
}

/// \brief Get element (i,j) from 4x4 matrix
/// \param i The row index.
/// \param j The column index.
/// \return The element at (i,j).
inline float& get(Bifrost::Math::float4x4& matrix, int i, int j) {
    static float zero = 0.F;
    switch (i) {
        case 0:
            switch (j) {
                case 0: return matrix.c0.x;
                case 1: return matrix.c1.x;
                case 2: return matrix.c2.x;
                case 3: return matrix.c3.x;
                default: assert(false); return zero;
            }
        case 1:
            switch (j) {
                case 0: return matrix.c0.y;
                case 1: return matrix.c1.y;
                case 2: return matrix.c2.y;
                case 3: return matrix.c3.y;
                default: assert(false); return zero;
            }
        case 2:
            switch (j) {
                case 0: return matrix.c0.z;
                case 1: return matrix.c1.z;
                case 2: return matrix.c2.z;
                case 3: return matrix.c3.z;
                default: assert(false); return zero;
            }
        case 3:
            switch (j) {
                case 0: return matrix.c0.w;
                case 1: return matrix.c1.w;
                case 2: return matrix.c2.w;
                case 3: return matrix.c3.w;
                default: assert(false); return zero;
            }
        default: assert(false); return zero;
    }
}

/// \brief Get element (i,j) from 4x4 matrix (const)
/// \param i The row index.
/// \param j The column index.
/// \return The element at (i,j).
inline float const& get(Bifrost::Math::float4x4 const& matrix, int i, int j) {
    return get(const_cast<Bifrost::Math::float4x4&>(matrix), i, j);
}

/// \brief Invert matrix using Gaussian elimination
/// \param matrix The matrix to invert.
/// \param out_matrix The inverted matrix.
/// \return True if the matrix was successfully inverted, false otherwise.
inline bool invert(const Bifrost::Math::float4x4& matrix, Bifrost::Math::float4x4& out_matrix) {
    auto s = Bifrost::Math::float4x4{
        {1.F, 0.F, 0.F, 0.F}, {0.F, 1.F, 0.F, 0.F}, {0.F, 0.F, 1.F, 0.F}, {0.F, 0.F, 0.F, 1.F}};
    auto t = matrix;

    // forward elimination
    for (int i = 0; i < 3; i++) {
        int   pivot     = i;
        float pivotsize = std::abs(get(t, i, i));

        for (int j = i + 1; j < 4; j++) {
            float tmp = std::abs(get(t, j, i));
            if (tmp > pivotsize) {
                pivot     = j;
                pivotsize = tmp;
            }
        }

        if (pivotsize < std::numeric_limits<decltype(pivotsize)>::min()) {
            return false;
        }

        if (pivot != i) {
            for (int j = 0; j < 4; j++) {
                std::swap(get(t, i, j), get(t, pivot, j));
                std::swap(get(s, i, j), get(s, pivot, j));
            }
        }
        for (int j = i + 1; j < 4; j++) {
            float f = get(t, j, i) / get(t, i, i);

            for (int k = 0; k < 4; k++) {
                get(t, j, k) -= f * get(t, i, k);
                get(s, j, k) -= f * get(s, i, k);
            }
        }
    }

    // back-substitution
    for (int i = 3; i >= 0; --i) {
        float f = get(t, i, i);

        if (std::abs(f) < std::numeric_limits<decltype(f)>::min()) {
            return false;
        }

        for (int j = 0; j < 4; j++) {
            get(t, i, j) /= f;
            get(s, i, j) /= f;
        }

        for (int j = 0; j < i; j++) {
            f = get(t, j, i);

            for (int k = 0; k < 4; k++) {
                get(t, j, k) -= f * get(t, i, k);
                get(s, j, k) -= f * get(s, i, k);
            }
        }
    }

    out_matrix = s;
    return true;
}

/// \brief Transpose matrix
/// \param matrix The matrix to transpose.
/// \param out_matrix The transposed matrix.
inline void transpose(const Bifrost::Math::float4x4& matrix, Bifrost::Math::float4x4& out_matrix) {
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j) {
            get(out_matrix, i, j) = get(matrix, j, i);
        }
}

} // namespace Math
} // namespace Examples

#endif // EXAMPLE_MATH_FLOAT4X4_UTILS_H
