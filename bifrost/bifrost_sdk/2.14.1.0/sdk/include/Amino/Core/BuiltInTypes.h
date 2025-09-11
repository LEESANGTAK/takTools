//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file  BuiltInTypes.h
///
/// \brief C++ representation of integral and floating point Amino data types at
///        runtime.
///
/// \see   Amino::BuiltInTypes

#ifndef AMINO_BUILTIN_TYPES_H
#define AMINO_BUILTIN_TYPES_H

#include <type_traits>

namespace Amino {

//==============================================================================
// TYPE ALIASES
//==============================================================================

/// \name C++ representation of built-in Amino data types at runtime.
///
/// Amino provides many integral data types that can flow in between nodes
/// within a graph. Namely, those are:
///
///   - Signed integers: char, short, int, long
///   - Unsigned integers: uchar, ushort, uint, ulong
///   - Floating-points: float, double
///   - Boolean: bool
///   - Enumerations
///
/// Each of those is represented by a matching C++ data type, defined by one the
/// following type alias.
///
/// \warning The Amino compiler and runtime requires the exact type listed below
/// be used.
///
/// \{

/// \brief Type alias for Amino's char type, a signed 8-bit integer
using char_t = signed char;

/// \brief Type alias for Amino's short type, a signed 16-bit integer
using short_t = signed short;

/// \brief Type alias for Amino's int type, a signed 32-bit integer
using int_t = signed int;

/// \brief Type alias for Amino's long type, a signed 64-bit integer
using long_t = signed long long;

/// \brief Type alias for Amino's uchar type, an unsigned 8-bit integer
using uchar_t = unsigned char;

/// \brief Type alias for Amino's ushort type, an unsigned 16-bit integer
using ushort_t = unsigned short;

/// \brief Type alias for Amino's uint type, an unsigned 32-bit integer
using uint_t = unsigned int;

/// \brief Type alias for Amino's ulong type, an unsigned 64-bit integer
using ulong_t = unsigned long long;

/// \brief Type alias for Amino's 32-bit float-point number
using float_t = float;

/// \brief Type alias for Amino's 64-bit float-point number
using double_t = double;

/// \brief Type alias for Amino's bool type, a boolean
using bool_t = bool;

/// \brief Type alias for the underlying type of Amino's enumerations.
using enum_underlying_t = int_t;

/// \brief Type alias for a standin for a Amino's enumeration type.
///
/// Can be useful to define type traits, or to create overload sets with an
/// overload expecting an enum type, which may have an implementation that
/// differs from the overload taking the underlying type of the enum type for
/// example.
enum class enum_t : enum_underlying_t {};

/// \}

//==============================================================================
// STATIC ASSERTIONS
//==============================================================================

// These assertions are present mainly for the purposes of verifying that the
// setting of the end-user compiler are appropriate. This validates the
// assumptions made by the Amino compiler.

static_assert(
    std::is_same<std::underlying_type_t<enum_t>, enum_underlying_t>::value,
    "enum_t's underlying type mismatch.");

// clang-format off
static_assert(sizeof(char_t  ) == 1,   "char_t should be a  8-bit integer");
static_assert(sizeof(short_t ) == 2,  "short_t should be a 16-bit integer");
static_assert(sizeof(int_t   ) == 4,    "int_t should be a 32-bit integer");
static_assert(sizeof(long_t  ) == 8,   "long_t should be a 64-bit integer");

static_assert(sizeof(uchar_t ) == 1,  "uchar_t should be a  8-bit integer");
static_assert(sizeof(ushort_t) == 2, "ushort_t should be a 16-bit integer");
static_assert(sizeof(uint_t  ) == 4,   "uint_t should be a 32-bit integer");
static_assert(sizeof(ulong_t ) == 8,  "ulong_t should be a 64-bit integer");

static_assert(sizeof(float_t ) == 4,  "float_t should be a 32-bit number");
static_assert(sizeof(double_t) == 8, "double_t should be a 64-bit number");

static_assert(sizeof(bool_t  ) == 1, "bool_t should occupy one byte");
static_assert(sizeof(enum_t  ) == 4, "enum_t should be a 32-bit integer");
// clang-format on

// clang-format off
static_assert(std::is_integral<char_t  >::value,   "char_t should be an integer");
static_assert(std::is_integral<short_t >::value,  "short_t should be an integer");
static_assert(std::is_integral<int_t   >::value,    "int_t should be an integer");
static_assert(std::is_integral<long_t  >::value,   "long_t should be an integer");
static_assert(std::is_integral<uchar_t >::value,  "uchar_t should be an integer");
static_assert(std::is_integral<ushort_t>::value, "ushort_t should be an integer");
static_assert(std::is_integral<uint_t  >::value,   "uint_t should be an integer");
static_assert(std::is_integral<ulong_t >::value,  "ulong_t should be an integer");
static_assert(std::is_integral<bool_t  >::value,   "bool_t should be an integer");
// clang-format on

static_assert(
    std::is_floating_point<float_t>::value,
    "float_t should be a floating point number");
static_assert(
    std::is_floating_point<double_t>::value,
    "double_t should be a floating point number");
static_assert(
    std::is_integral<enum_underlying_t>::value,
    "enum_t's underlying type should be an integer");

// clang-format off
static_assert(std::is_signed<char_t >::value,  "char_t should be signed");
static_assert(std::is_signed<short_t>::value, "short_t should be signed");
static_assert(std::is_signed<int_t  >::value,   "int_t should be signed");
static_assert(std::is_signed<long_t >::value,  "long_t should be signed");

static_assert(std::is_unsigned<uchar_t >::value,  "uchar_t should be unsigned");
static_assert(std::is_unsigned<ushort_t>::value, "ushort_t should be unsigned");
static_assert(std::is_unsigned<uint_t  >::value,   "uint_t should be unsigned");
static_assert(std::is_unsigned<ulong_t >::value,  "ulong_t should be unsigned");

static_assert(std::is_unsigned<bool_t >::value,    "bool_t should be unsigned");
// clang-format on

static_assert(
    std::is_signed<enum_underlying_t>::value,
    "enum_t's underlying type should be signed");

} // namespace Amino

#endif // AMINO_AMINOBUILTINTYPES_H
