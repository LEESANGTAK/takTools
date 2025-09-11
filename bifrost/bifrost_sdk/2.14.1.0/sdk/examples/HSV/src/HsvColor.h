//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef HSV_COLOR_H
#define HSV_COLOR_H

#include "HsvColorExport.h"

// For the macros used to expose types/functions to Amino
#include <Amino/Cpp/Annotate.h>

// For the Math vector types (float3, float4, double3, double4).
#include <Bifrost/Math/Types.h>

namespace Examples {
namespace SDK {

/// \brief Transform the RGB(A) color to an HSV color.
///
/// Define overloads called "color_to_HSV" in the namespace "Examples::SDK".
/// Their fully qualified name is therefore "Examples::SDK::color_to_HSV".
///
/// They have one input named 'color' and one output named 'hsv'.
///
/// Together those 4 overloads form an overload set.
///
/// To form a valid overload set, the different overloads must satisfy some
/// constraints. In particular:
///  1) They must have the same number of inputs and the same number of outputs
///  2) They must have the same names for their input and output parameters, in
///     the same order.
///  3) They must NOT have the exact same input types as another overload.
///
/// The constraint #3 is obvious; it's also illegal in C/C++ since the compiler
/// can't decide which function to call as both functions are as good candidates
/// the the argument types. They're therefore ambiguous.
///
/// The constraint #1 and #2 are necessary in Amino, but not in C/C++. It's
/// important because in the Amino, it must be possible to know how many inputs
/// and outputs the *overload set* has (not the individual overloads) and what
/// are the names of the ports without resolving the types of the arguments. For
/// example, this allows knowing that 'color_to_HSV' has one input named 'color'
/// and one output named 'hsv', regardless of the type of argument that will
/// ultimately be passed to the node. Only then will the compiler know which
/// specific version of 'color_to_HSV' to call.
/// \{
HSV_COLOR_DECL
void RGB_to_HSV(Bifrost::Math::float3 const& rgb, Bifrost::Math::float3& hsv)
    AMINO_ANNOTATE("Amino::Node");

HSV_COLOR_DECL
void RGB_to_HSV(Bifrost::Math::float4 const& rgb, Bifrost::Math::float3& hsv)
    AMINO_ANNOTATE("Amino::Node");

HSV_COLOR_DECL
void RGB_to_HSV(Bifrost::Math::double3 const& rgb, Bifrost::Math::double3& hsv)
    AMINO_ANNOTATE("Amino::Node");

HSV_COLOR_DECL
void RGB_to_HSV(Bifrost::Math::double4 const& rgb, Bifrost::Math::double3& hsv)
    AMINO_ANNOTATE("Amino::Node");
/// \}

} // namespace SDK
} // namespace Examples

#endif // HSV_COLOR_H
