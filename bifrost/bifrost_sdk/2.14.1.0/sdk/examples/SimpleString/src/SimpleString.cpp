//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "SimpleString.h"

#include <string>

//------------------------------------------------------------------------------
//
void Examples::SDK::join_strings(const Amino::String& first,
                                 const Amino::String& second,
                                 Amino::String&       concatenated) {
    concatenated = first + second;
}

//------------------------------------------------------------------------------
//
void Examples::SDK::integer_to_string(int from, Amino::String& to) {
    std::string converted_int = std::to_string(from);

    to = Amino::String(converted_int.c_str(), converted_int.size());
}
