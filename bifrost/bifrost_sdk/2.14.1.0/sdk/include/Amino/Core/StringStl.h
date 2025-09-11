//-
// =============================================================================
// Copyright 2023 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

/// \file  StringStl.h

#ifndef AMINO_CORE_STRING_STL_H
#define AMINO_CORE_STRING_STL_H

#include "String.h"

#include <ostream>
#include <string>

namespace std {

/// \brief Hash specialization for Amino::String
template <>
struct hash<Amino::String> {
    using argument_type = Amino::String;
    using result_type   = size_t;

    result_type operator()(const argument_type& str) const {
        return hash<string>()(str.c_str());
    }
};

} // namespace std

namespace Amino {

/// \brief Insert the contents of the string \p str into the output stream \p
/// os.
///
/// \param os The output stream
///
/// \param str The string to be inserted.
///
/// \return The same \p os output stream passed as argument.
inline std::ostream& operator<<(std::ostream& os, const String& str) {
    os << str.c_str();
    return os;
}

} // namespace Amino

#endif
