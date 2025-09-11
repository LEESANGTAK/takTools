//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file This is example shows how to create a simple struct and overload a
/// node operator.

#ifndef COMPLEX_H
#define COMPLEX_H

#include "ComplexExport.h"

// For the macros used to expose types/functions to Amino
#include <Amino/Cpp/Annotate.h>

namespace Examples {
namespace SDK {

//==============================================================================
// STRUCT Complex
//==============================================================================

/// \brief Define a structure representing a complex number.
///
/// The structure has the name "Complex" and is defined in the "Examples::SDK"
/// namespace. Its fully qualified name is therefore "Examples::SDK::Complex".
/// This fully qualified name is therefore a unique identifier for our "Complex"
/// struct.
struct AMINO_ANNOTATE("Amino::Struct") COMPLEX_DECL Complex {
    float real;
    float imaginary;
};

COMPLEX_DECL void polar(float                   magnitude,
                        float                   phase /* rads */,
                        Examples::SDK::Complex& polar)
    AMINO_ANNOTATE("Amino::Node");

} // namespace SDK
} // namespace Examples

//==============================================================================
// NAMESPACE Core::Math
//==============================================================================

namespace Core {
namespace Math {

/// \brief Computes the log (base e) of a complex number.
///
/// This is how to add an overload to the existing Core::Math::log_base_e
/// overloads. This operation takes one input (the value of which to compute the
/// log) named 'value' and has one output (the log result) named 'logarithm'.
///
/// The Core::Math::log_base_e already exists in the library and allows
/// computing the log (base e) of different types like float and double scalars
/// and vectors (e.g. float, double, Math::float2, Math::double3, etc.). By
/// adding this overload, this means that this node can now also be used on
/// values of this 'Complex' type. This group of overloads named
/// "Core::Math::log_base_e" together form an overload set.
///
/// To form a valid overload set, the different overloads must satisfy some
/// requirements. In particular:
///  1) They must have the same number of inputs and the same number of outputs
///  2) They must have the same names for their input and output parameters, in
///     the same order.
///  3) They must NOT have the exact same input types as another overload.
///
/// The constraint #3 is obvious; it's also illegal in C/C++ since the compiler
/// can't decide which function to call as both functions are as good candidates
/// for the argument types. They're therefore ambiguous.
///
/// The constraint #1 and #2 are necessary in Amino, but not in C/C++. It's
/// important in Amino because it must be possible to know how many inputs
/// and outputs the *overload set* has (not the overload) and what are the names
/// of the ports without resolving the types of the arguments. For example, this
/// allows knowing that 'log_base_e' has one input named 'value' and one output
/// named 'logarithm', regardless of the type of argument that will ultimately
/// be passed to the node. Only then will the compiler know which exact version
/// of 'log_base_e' to call.
///
/// Note: The output argument 'logarithm' has to be passed by reference (&)
/// because Amino doesn't currently support returning custom structs by value
/// (using the "return" keyword).
///
/// Note: The implementation of the functions exposed to Amino must be defined
/// in the source .cpp file, not in the header .h file, even if the
/// implementation is really short. That's because a linkable symbol must be
/// added in the shared library to allow Amino to call it.
COMPLEX_DECL void log_base_e(const Examples::SDK::Complex& value,
                             Examples::SDK::Complex&       logarithm)
    AMINO_ANNOTATE("Amino::Node");

} // namespace Math
} // namespace Core

#endif // COMPLEX_H
