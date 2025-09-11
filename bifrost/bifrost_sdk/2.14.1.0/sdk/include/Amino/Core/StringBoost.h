//-
// =============================================================================
// Copyright 2023 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

/// \file  StringBoost.h

#ifndef AMINO_CORE_STRING_BOOST_H
#define AMINO_CORE_STRING_BOOST_H

#include "StringStl.h"

namespace Amino {
/// \brief Boost hash specialization for Amino::String
inline std::size_t hash_value(String const& b) {
    std::hash<String> hasher;
    return hasher(b);
}
} // namespace Amino

#endif
