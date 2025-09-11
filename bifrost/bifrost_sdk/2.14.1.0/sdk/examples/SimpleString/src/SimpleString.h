//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef SIMPLE_STRING_H
#define SIMPLE_STRING_H

#include "SimpleStringExport.h"

#include <Amino/Core/String.h>
#include <Amino/Cpp/Annotate.h>

namespace Examples {
namespace SDK {

//------------------------------------------------------------------------------
//
/// \brief Concatenate first and second string inputs.
SIMPLE_STRING_DECL
void join_strings(const Amino::String& first,
                  const Amino::String& second,
                  Amino::String&       concatenated)
    AMINO_ANNOTATE("Amino::Node");

//------------------------------------------------------------------------------
//
/// \brief Convert an integer to a string.
SIMPLE_STRING_DECL
void integer_to_string(int from, Amino::String& to)
    AMINO_ANNOTATE("Amino::Node");

} // namespace SDK
} // namespace Examples

#endif // SIMPLE_STRING_H
