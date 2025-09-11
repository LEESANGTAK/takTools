//-
// =============================================================================
// Copyright 2023 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \brief Bifrost standard math types.

#ifndef BIFROST_MATH_TYPES_H
#define BIFROST_MATH_TYPES_H

#include <Amino/Core/BuiltInTypes.h>
#include <Amino/Cpp/Annotate.h>

// Use a define, other clang-format gets confused.
// WARNING: Ignoring namespace is an internal feature, should not be used by
// external code.
#define BIFROST_IGNORE_NAMESPACE AMINO_ANNOTATE("Amino::Namespace ignore")
namespace Bifrost BIFROST_IGNORE_NAMESPACE {
#undef BIFROST_IGNORE_NAMESPACE

#define TYPE_KIND(kind) "{type_kind, " kind "}"
#define WPLAYOUT(layout) "{watchpoint_layout, " layout "}"

#define WPLAYOUT_VECTOR_2 "($x\\, $y)"
#define WPLAYOUT_VECTOR_3 "($x\\, $y\\, $z)"
#define WPLAYOUT_VECTOR_4 "($x\\, $y\\, $z\\, $w)"

#define WPLAYOUT_MATRIX_2x2 \
    "\\[\
($\\{c0.x\\}\\, $\\{c1.x\\})\\, \
($\\{c0.y\\}\\, $\\{c1.y\\})\\]"
#define WPLAYOUT_MATRIX_2x3 \
    "\\[\
($\\{c0.x\\}\\, $\\{c1.x\\}\\, $\\{c2.x\\})\\, \
($\\{c0.y\\}\\, $\\{c1.y\\}\\, $\\{c2.y\\})\\]"
#define WPLAYOUT_MATRIX_2x4 \
    "\\[\
($\\{c0.x\\}\\, $\\{c1.x\\}\\, $\\{c2.x\\}\\, $\\{c3.x\\})\\, \
($\\{c0.y\\}\\, $\\{c1.y\\}\\, $\\{c2.y\\}\\, $\\{c3.y\\})\\]"
#define WPLAYOUT_MATRIX_3x2 \
    "\\[\
($\\{c0.x\\}\\, $\\{c1.x\\}\\)\\, \
($\\{c0.y\\}\\, $\\{c1.y\\}\\)\\, \
($\\{c0.z\\}\\, $\\{c1.z\\})\\]"
#define WPLAYOUT_MATRIX_3x3 \
    "\\[\
($\\{c0.x\\}\\, $\\{c1.x\\}\\, $\\{c2.x\\}\\)\\, \
($\\{c0.y\\}\\, $\\{c1.y\\}\\, $\\{c2.y\\}\\)\\, \
($\\{c0.z\\}\\, $\\{c1.z\\}\\, $\\{c2.z\\}\\)\\]"
#define WPLAYOUT_MATRIX_3x4 \
    "\\[\
($\\{c0.x\\}\\, $\\{c1.x\\}\\, $\\{c2.x\\}\\, $\\{c3.x\\})\\, \
($\\{c0.y\\}\\, $\\{c1.y\\}\\, $\\{c2.y\\}\\, $\\{c3.y\\})\\, \
($\\{c0.z\\}\\, $\\{c1.z\\}\\, $\\{c2.z\\}\\, $\\{c3.z\\})\\]"
#define WPLAYOUT_MATRIX_4x2 \
    "\\[\
($\\{c0.x\\}\\, $\\{c1.x\\}\\)\\, \
($\\{c0.y\\}\\, $\\{c1.y\\}\\)\\, \
($\\{c0.z\\}\\, $\\{c1.z\\}\\)\\, \
($\\{c0.w\\}\\, $\\{c1.w\\}\\)\\]"
#define WPLAYOUT_MATRIX_4x3 \
    "\\[\
($\\{c0.x\\}\\, $\\{c1.x\\}\\, $\\{c2.x\\})\\, \
($\\{c0.y\\}\\, $\\{c1.y\\}\\, $\\{c2.y\\})\\, \
($\\{c0.z\\}\\, $\\{c1.z\\}\\, $\\{c2.z\\})\\, \
($\\{c0.w\\}\\, $\\{c1.w\\}\\, $\\{c2.w\\})\\]"
#define WPLAYOUT_MATRIX_4x4 \
    "\\[\
($\\{c0.x\\}\\, $\\{c1.x\\}\\, $\\{c2.x\\}\\, $\\{c3.x\\})\\, \
($\\{c0.y\\}\\, $\\{c1.y\\}\\, $\\{c2.y\\}\\, $\\{c3.y\\})\\, \
($\\{c0.z\\}\\, $\\{c1.z\\}\\, $\\{c2.z\\}\\, $\\{c3.z\\})\\, \
($\\{c0.w\\}\\, $\\{c1.w\\}\\, $\\{c2.w\\}\\, $\\{c3.w\\})\\]"

namespace Math {

/// \brief Order of rotation around the different axes.
enum class AMINO_ANNOTATE("Amino::Enum") rotation_order : int {
    XYZ = 0, ///< Rotate around X, then Y, then Z
    YZX = 1, ///< Rotate around Y, then Z, then X
    ZXY = 2, ///< Rotate around Z, then X, then Y
    XZY = 3, ///< Rotate around X, then Z, then Y
    YXZ = 4, ///< Rotate around Y, then X, then Z
    ZYX = 5  ///< Rotate around Z, then Y, then X
};

/// \brief A vector of two floats, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") float2 {
    Amino::float_t x; ///< The 'x' member of the vector
    Amino::float_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three floats, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") float3 {
    Amino::float_t x; ///< The 'x' member of the vector
    Amino::float_t y; ///< The 'y' member of the vector
    Amino::float_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four floats, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") float4 {
    Amino::float_t x; ///< The 'x' member of the vector
    Amino::float_t y; ///< The 'y' member of the vector
    Amino::float_t z; ///< The 'z' member of the vector
    Amino::float_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of floats.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") float2x2 {
    float2 c0; ///< The first column of the matrix
    float2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of floats.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") float3x2 {
    float3 c0; ///< The first column of the matrix
    float3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of floats.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") float4x2 {
    float4 c0; ///< The first column of the matrix
    float4 c1; ///< The second column of the matrix
};

/// \brief A matrix with tree columns and two rows of floats.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") float2x3 {
    float2 c0; ///< The first column of the matrix
    float2 c1; ///< The second column of the matrix
    float2 c2; ///< The third column of the matrix
};

/// \brief A matrix with tree columns and tree rows of floats.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") float3x3 {
    float3 c0; ///< The first column of the matrix
    float3 c1; ///< The second column of the matrix
    float3 c2; ///< The third column of the matrix
};

/// \brief A matrix with tree columns and four rows of floats.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") float4x3 {
    float4 c0; ///< The first column of the matrix
    float4 c1; ///< The second column of the matrix
    float4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of floats.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") float2x4 {
    float2 c0; ///< The first column of the matrix
    float2 c1; ///< The second column of the matrix
    float2 c2; ///< The third column of the matrix
    float2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of floats.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") float3x4 {
    float3 c0; ///< The first column of the matrix
    float3 c1; ///< The second column of the matrix
    float3 c2; ///< The third column of the matrix
    float3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of floats.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") float4x4 {
    float4 c0; ///< The first column of the matrix
    float4 c1; ///< The second column of the matrix
    float4 c2; ///< The third column of the matrix
    float4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two doubles, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") double2 {
    Amino::double_t x; ///< The 'x' member of the vector
    Amino::double_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three doubles, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") double3 {
    Amino::double_t x; ///< The 'x' member of the vector
    Amino::double_t y; ///< The 'y' member of the vector
    Amino::double_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four doubles, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") double4 {
    Amino::double_t x; ///< The 'x' member of the vector
    Amino::double_t y; ///< The 'y' member of the vector
    Amino::double_t z; ///< The 'z' member of the vector
    Amino::double_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of doubles.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") double2x2 {
    double2 c0; ///< The first column of the matrix
    double2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of doubles.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") double3x2 {
    double3 c0; ///< The first column of the matrix
    double3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of doubles.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") double4x2 {
    double4 c0; ///< The first column of the matrix
    double4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of doubles.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") double2x3 {
    double2 c0; ///< The first column of the matrix
    double2 c1; ///< The second column of the matrix
    double2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and three rows of doubles.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") double3x3 {
    double3 c0; ///< The first column of the matrix
    double3 c1; ///< The second column of the matrix
    double3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of doubles.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") double4x3 {
    double4 c0; ///< The first column of the matrix
    double4 c1; ///< The second column of the matrix
    double4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of doubles.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") double2x4 {
    double2 c0; ///< The first column of the matrix
    double2 c1; ///< The second column of the matrix
    double2 c2; ///< The third column of the matrix
    double2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of doubles.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") double3x4 {
    double3 c0; ///< The first column of the matrix
    double3 c1; ///< The second column of the matrix
    double3 c2; ///< The third column of the matrix
    double3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of doubles.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") double4x4 {
    double4 c0; ///< The first column of the matrix
    double4 c1; ///< The second column of the matrix
    double4 c2; ///< The third column of the matrix
    double4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two chars, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") char2 {
    Amino::char_t x; ///< The 'x' member of the vector
    Amino::char_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three chars, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") char3 {
    Amino::char_t x; ///< The 'x' member of the vector
    Amino::char_t y; ///< The 'y' member of the vector
    Amino::char_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four chars, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") char4 {
    Amino::char_t x; ///< The 'x' member of the vector
    Amino::char_t y; ///< The 'y' member of the vector
    Amino::char_t z; ///< The 'z' member of the vector
    Amino::char_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") char2x2 {
    char2 c0; ///< The first column of the matrix
    char2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") char3x2 {
    char3 c0; ///< The first column of the matrix
    char3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") char4x2 {
    char4 c0; ///< The first column of the matrix
    char4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") char2x3 {
    char2 c0; ///< The first column of the matrix
    char2 c1; ///< The second column of the matrix
    char2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and three rows of chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") char3x3 {
    char3 c0; ///< The first column of the matrix
    char3 c1; ///< The second column of the matrix
    char3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") char4x3 {
    char4 c0; ///< The first column of the matrix
    char4 c1; ///< The second column of the matrix
    char4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") char2x4 {
    char2 c0; ///< The first column of the matrix
    char2 c1; ///< The second column of the matrix
    char2 c2; ///< The third column of the matrix
    char2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") char3x4 {
    char3 c0; ///< The first column of the matrix
    char3 c1; ///< The second column of the matrix
    char3 c2; ///< The third column of the matrix
    char3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") char4x4 {
    char4 c0; ///< The first column of the matrix
    char4 c1; ///< The second column of the matrix
    char4 c2; ///< The third column of the matrix
    char4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two shorts, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") short2 {
    Amino::short_t x; ///< The 'x' member of the vector
    Amino::short_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three shorts, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") short3 {
    Amino::short_t x; ///< The 'x' member of the vector
    Amino::short_t y; ///< The 'y' member of the vector
    Amino::short_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four shorts, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") short4 {
    Amino::short_t x; ///< The 'x' member of the vector
    Amino::short_t y; ///< The 'y' member of the vector
    Amino::short_t z; ///< The 'z' member of the vector
    Amino::short_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") short2x2 {
    short2 c0; ///< The first column of the matrix
    short2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") short3x2 {
    short3 c0; ///< The first column of the matrix
    short3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") short4x2 {
    short4 c0; ///< The first column of the matrix
    short4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") short2x3 {
    short2 c0; ///< The first column of the matrix
    short2 c1; ///< The second column of the matrix
    short2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and tree rows of shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") short3x3 {
    short3 c0; ///< The first column of the matrix
    short3 c1; ///< The second column of the matrix
    short3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") short4x3 {
    short4 c0; ///< The first column of the matrix
    short4 c1; ///< The second column of the matrix
    short4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") short2x4 {
    short2 c0; ///< The first column of the matrix
    short2 c1; ///< The second column of the matrix
    short2 c2; ///< The third column of the matrix
    short2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") short3x4 {
    short3 c0; ///< The first column of the matrix
    short3 c1; ///< The second column of the matrix
    short3 c2; ///< The third column of the matrix
    short3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") short4x4 {
    short4 c0; ///< The first column of the matrix
    short4 c1; ///< The second column of the matrix
    short4 c2; ///< The third column of the matrix
    short4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two ints, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") int2 {
    Amino::int_t x; ///< The 'x' member of the vector
    Amino::int_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three ints, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") int3 {
    Amino::int_t x; ///< The 'x' member of the vector
    Amino::int_t y; ///< The 'y' member of the vector
    Amino::int_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four ints, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") int4 {
    Amino::int_t x; ///< The 'x' member of the vector
    Amino::int_t y; ///< The 'y' member of the vector
    Amino::int_t z; ///< The 'z' member of the vector
    Amino::int_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") int2x2 {
    int2 c0; ///< The first column of the matrix
    int2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") int3x2 {
    int3 c0; ///< The first column of the matrix
    int3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") int4x2 {
    int4 c0; ///< The first column of the matrix
    int4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") int2x3 {
    int2 c0; ///< The first column of the matrix
    int2 c1; ///< The second column of the matrix
    int2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and three rows of ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") int3x3 {
    int3 c0; ///< The first column of the matrix
    int3 c1; ///< The second column of the matrix
    int3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") int4x3 {
    int4 c0; ///< The first column of the matrix
    int4 c1; ///< The second column of the matrix
    int4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") int2x4 {
    int2 c0; ///< The first column of the matrix
    int2 c1; ///< The second column of the matrix
    int2 c2; ///< The third column of the matrix
    int2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") int3x4 {
    int3 c0; ///< The first column of the matrix
    int3 c1; ///< The second column of the matrix
    int3 c2; ///< The third column of the matrix
    int3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") int4x4 {
    int4 c0; ///< The first column of the matrix
    int4 c1; ///< The second column of the matrix
    int4 c2; ///< The third column of the matrix
    int4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two longs, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") long2 {
    Amino::long_t x; ///< The 'x' member of the vector
    Amino::long_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three longs, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") long3 {
    Amino::long_t x; ///< The 'x' member of the vector
    Amino::long_t y; ///< The 'y' member of the vector
    Amino::long_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four longs, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") long4 {
    Amino::long_t x; ///< The 'x' member of the vector
    Amino::long_t y; ///< The 'y' member of the vector
    Amino::long_t z; ///< The 'z' member of the vector
    Amino::long_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") long2x2 {
    long2 c0; ///< The first column of the matrix
    long2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") long3x2 {
    long3 c0; ///< The first column of the matrix
    long3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") long4x2 {
    long4 c0; ///< The first column of the matrix
    long4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") long2x3 {
    long2 c0; ///< The first column of the matrix
    long2 c1; ///< The second column of the matrix
    long2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and three rows of longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") long3x3 {
    long3 c0; ///< The first column of the matrix
    long3 c1; ///< The second column of the matrix
    long3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") long4x3 {
    long4 c0; ///< The first column of the matrix
    long4 c1; ///< The second column of the matrix
    long4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") long2x4 {
    long2 c0; ///< The first column of the matrix
    long2 c1; ///< The second column of the matrix
    long2 c2; ///< The third column of the matrix
    long2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") long3x4 {
    long3 c0; ///< The first column of the matrix
    long3 c1; ///< The second column of the matrix
    long3 c2; ///< The third column of the matrix
    long3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") long4x4 {
    long4 c0; ///< The first column of the matrix
    long4 c1; ///< The second column of the matrix
    long4 c2; ///< The third column of the matrix
    long4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two unsigned chars, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") uchar2 {
    Amino::uchar_t x; ///< The 'x' member of the vector
    Amino::uchar_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three unsigned chars, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") uchar3 {
    Amino::uchar_t x; ///< The 'x' member of the vector
    Amino::uchar_t y; ///< The 'y' member of the vector
    Amino::uchar_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four unsigned chars, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") uchar4 {
    Amino::uchar_t x; ///< The 'x' member of the vector
    Amino::uchar_t y; ///< The 'y' member of the vector
    Amino::uchar_t z; ///< The 'z' member of the vector
    Amino::uchar_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of unsigned chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") uchar2x2 {
    uchar2 c0; ///< The first column of the matrix
    uchar2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of unsigned chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") uchar3x2 {
    uchar3 c0; ///< The first column of the matrix
    uchar3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of unsigned chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") uchar4x2 {
    uchar4 c0; ///< The first column of the matrix
    uchar4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of unsigned chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") uchar2x3 {
    uchar2 c0; ///< The first column of the matrix
    uchar2 c1; ///< The second column of the matrix
    uchar2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and three rows of unsigned chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") uchar3x3 {
    uchar3 c0; ///< The first column of the matrix
    uchar3 c1; ///< The second column of the matrix
    uchar3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of unsigned chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") uchar4x3 {
    uchar4 c0; ///< The first column of the matrix
    uchar4 c1; ///< The second column of the matrix
    uchar4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of unsigned chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") uchar2x4 {
    uchar2 c0; ///< The first column of the matrix
    uchar2 c1; ///< The second column of the matrix
    uchar2 c2; ///< The third column of the matrix
    uchar2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of unsigned chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") uchar3x4 {
    uchar3 c0; ///< The first column of the matrix
    uchar3 c1; ///< The second column of the matrix
    uchar3 c2; ///< The third column of the matrix
    uchar3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of unsigned chars.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") uchar4x4 {
    uchar4 c0; ///< The first column of the matrix
    uchar4 c1; ///< The second column of the matrix
    uchar4 c2; ///< The third column of the matrix
    uchar4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two unsigned shorts, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") ushort2 {
    Amino::ushort_t x; ///< The 'x' member of the vector
    Amino::ushort_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three unsigned shorts, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") ushort3 {
    Amino::ushort_t x; ///< The 'x' member of the vector
    Amino::ushort_t y; ///< The 'y' member of the vector
    Amino::ushort_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four unsigned shorts, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") ushort4 {
    Amino::ushort_t x; ///< The 'x' member of the vector
    Amino::ushort_t y; ///< The 'y' member of the vector
    Amino::ushort_t z; ///< The 'z' member of the vector
    Amino::ushort_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of unsigned shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") ushort2x2 {
    ushort2 c0; ///< The first column of the matrix
    ushort2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of unsigned shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") ushort3x2 {
    ushort3 c0; ///< The first column of the matrix
    ushort3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of unsigned shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") ushort4x2 {
    ushort4 c0; ///< The first column of the matrix
    ushort4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of unsigned shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") ushort2x3 {
    ushort2 c0; ///< The first column of the matrix
    ushort2 c1; ///< The second column of the matrix
    ushort2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and three rows of unsigned shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") ushort3x3 {
    ushort3 c0; ///< The first column of the matrix
    ushort3 c1; ///< The second column of the matrix
    ushort3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of unsigned shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") ushort4x3 {
    ushort4 c0; ///< The first column of the matrix
    ushort4 c1; ///< The second column of the matrix
    ushort4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of unsigned shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") ushort2x4 {
    ushort2 c0; ///< The first column of the matrix
    ushort2 c1; ///< The second column of the matrix
    ushort2 c2; ///< The third column of the matrix
    ushort2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of unsigned shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") ushort3x4 {
    ushort3 c0; ///< The first column of the matrix
    ushort3 c1; ///< The second column of the matrix
    ushort3 c2; ///< The third column of the matrix
    ushort3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of unsigned shorts.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") ushort4x4 {
    ushort4 c0; ///< The first column of the matrix
    ushort4 c1; ///< The second column of the matrix
    ushort4 c2; ///< The third column of the matrix
    ushort4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two unsigned ints, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") uint2 {
    Amino::uint_t x; ///< The 'x' member of the vector
    Amino::uint_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three unsigned ints, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") uint3 {
    Amino::uint_t x; ///< The 'x' member of the vector
    Amino::uint_t y; ///< The 'y' member of the vector
    Amino::uint_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four unsigned ints, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") uint4 {
    Amino::uint_t x; ///< The 'x' member of the vector
    Amino::uint_t y; ///< The 'y' member of the vector
    Amino::uint_t z; ///< The 'z' member of the vector
    Amino::uint_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of unsigned ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") uint2x2 {
    uint2 c0; ///< The first column of the matrix
    uint2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of unsigned ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") uint3x2 {
    uint3 c0; ///< The first column of the matrix
    uint3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of unsigned ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") uint4x2 {
    uint4 c0; ///< The first column of the matrix
    uint4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of unsigned ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") uint2x3 {
    uint2 c0; ///< The first column of the matrix
    uint2 c1; ///< The second column of the matrix
    uint2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and three rows of unsigned ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") uint3x3 {
    uint3 c0; ///< The first column of the matrix
    uint3 c1; ///< The second column of the matrix
    uint3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of unsigned ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") uint4x3 {
    uint4 c0; ///< The first column of the matrix
    uint4 c1; ///< The second column of the matrix
    uint4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of unsigned ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") uint2x4 {
    uint2 c0; ///< The first column of the matrix
    uint2 c1; ///< The second column of the matrix
    uint2 c2; ///< The third column of the matrix
    uint2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of unsigned ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") uint3x4 {
    uint3 c0; ///< The first column of the matrix
    uint3 c1; ///< The second column of the matrix
    uint3 c2; ///< The third column of the matrix
    uint3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of unsigned ints.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") uint4x4 {
    uint4 c0; ///< The first column of the matrix
    uint4 c1; ///< The second column of the matrix
    uint4 c2; ///< The third column of the matrix
    uint4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two unsigned longs, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") ulong2 {
    Amino::ulong_t x; ///< The 'x' member of the vector
    Amino::ulong_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three unsigned longs, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") ulong3 {
    Amino::ulong_t x; ///< The 'x' member of the vector
    Amino::ulong_t y; ///< The 'y' member of the vector
    Amino::ulong_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four unsigned longs, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") ulong4 {
    Amino::ulong_t x; ///< The 'x' member of the vector
    Amino::ulong_t y; ///< The 'y' member of the vector
    Amino::ulong_t z; ///< The 'z' member of the vector
    Amino::ulong_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of unsigned longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") ulong2x2 {
    ulong2 c0; ///< The first column of the matrix
    ulong2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of unsigned longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") ulong3x2 {
    ulong3 c0; ///< The first column of the matrix
    ulong3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of unsigned longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") ulong4x2 {
    ulong4 c0; ///< The first column of the matrix
    ulong4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of unsigned longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") ulong2x3 {
    ulong2 c0; ///< The first column of the matrix
    ulong2 c1; ///< The second column of the matrix
    ulong2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and three rows of unsigned longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") ulong3x3 {
    ulong3 c0; ///< The first column of the matrix
    ulong3 c1; ///< The second column of the matrix
    ulong3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of unsigned longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") ulong4x3 {
    ulong4 c0; ///< The first column of the matrix
    ulong4 c1; ///< The second column of the matrix
    ulong4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of unsigned longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") ulong2x4 {
    ulong2 c0; ///< The first column of the matrix
    ulong2 c1; ///< The second column of the matrix
    ulong2 c2; ///< The third column of the matrix
    ulong2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of unsigned longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") ulong3x4 {
    ulong3 c0; ///< The first column of the matrix
    ulong3 c1; ///< The second column of the matrix
    ulong3 c2; ///< The third column of the matrix
    ulong3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of unsigned longs.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") ulong4x4 {
    ulong4 c0; ///< The first column of the matrix
    ulong4 c1; ///< The second column of the matrix
    ulong4 c2; ///< The third column of the matrix
    ulong4 c3; ///< The fourth column of the matrix
};

/// \brief A vector of two bools, x and y.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_2) "]") bool2 {
    Amino::bool_t x; ///< The 'x' member of the vector
    Amino::bool_t y; ///< The 'y' member of the vector
};

/// \brief A vector of three bools, x, y and z.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_3) "]") bool3 {
    Amino::bool_t x; ///< The 'x' member of the vector
    Amino::bool_t y; ///< The 'y' member of the vector
    Amino::bool_t z; ///< The 'z' member of the vector
};

/// \brief A vector of four bools, x, y, z and w.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "vector") ", " WPLAYOUT(WPLAYOUT_VECTOR_4) "]") bool4 {
    Amino::bool_t x; ///< The 'x' member of the vector
    Amino::bool_t y; ///< The 'y' member of the vector
    Amino::bool_t z; ///< The 'z' member of the vector
    Amino::bool_t w; ///< The 'w' member of the vector
};

/// \brief A matrix with two columns and two rows of bools.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x2) "]") bool2x2 {
    bool2 c0; ///< The first column of the matrix
    bool2 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and three rows of bools.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x2) "]") bool3x2 {
    bool3 c0; ///< The first column of the matrix
    bool3 c1; ///< The second column of the matrix
};

/// \brief A matrix with two columns and four rows of bools.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x2) "]") bool4x2 {
    bool4 c0; ///< The first column of the matrix
    bool4 c1; ///< The second column of the matrix
};

/// \brief A matrix with three columns and two rows of bools.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x3) "]") bool2x3 {
    bool2 c0; ///< The first column of the matrix
    bool2 c1; ///< The second column of the matrix
    bool2 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and three rows of bools.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x3) "]") bool3x3 {
    bool3 c0; ///< The first column of the matrix
    bool3 c1; ///< The second column of the matrix
    bool3 c2; ///< The third column of the matrix
};

/// \brief A matrix with three columns and four rows of bools.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x3) "]") bool4x3 {
    bool4 c0; ///< The first column of the matrix
    bool4 c1; ///< The second column of the matrix
    bool4 c2; ///< The third column of the matrix
};

/// \brief A matrix with four columns and two rows of bools.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_2x4) "]") bool2x4 {
    bool2 c0; ///< The first column of the matrix
    bool2 c1; ///< The second column of the matrix
    bool2 c2; ///< The third column of the matrix
    bool2 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and three rows of bools.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_3x4) "]") bool3x4 {
    bool3 c0; ///< The first column of the matrix
    bool3 c1; ///< The second column of the matrix
    bool3 c2; ///< The third column of the matrix
    bool3 c3; ///< The fourth column of the matrix
};

/// \brief A matrix with four columns and four rows of bools.
struct AMINO_ANNOTATE("Amino::Struct metadata=[" TYPE_KIND(
    "matrix") ", " WPLAYOUT(WPLAYOUT_MATRIX_4x4) "]") bool4x4 {
    bool4 c0; ///< The first column of the matrix
    bool4 c1; ///< The second column of the matrix
    bool4 c2; ///< The third column of the matrix
    bool4 c3; ///< The fourth column of the matrix
};

#undef WPLAYOUT_VECTOR_2
#undef WPLAYOUT_VECTOR_3
#undef WPLAYOUT_VECTOR_4

#undef WPLAYOUT_MATRIX_2x2
#undef WPLAYOUT_MATRIX_2x3
#undef WPLAYOUT_MATRIX_2x4
#undef WPLAYOUT_MATRIX_3x2
#undef WPLAYOUT_MATRIX_3x3
#undef WPLAYOUT_MATRIX_3x4
#undef WPLAYOUT_MATRIX_4x2
#undef WPLAYOUT_MATRIX_4x3
#undef WPLAYOUT_MATRIX_4x4

#undef TYPE_KIND
#undef WPLAYOUT

} // namespace Math
} // namespace BIFROST_IGNORE_NAMESPACE
#endif
