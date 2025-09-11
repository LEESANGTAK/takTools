//-
// =============================================================================
// Copyright 2025 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file  NamingUtilities.h
/// \brief A collection of Naming Utility methods.

#ifndef AMINO_CORE_NAMING_UTILITIES_H
#define AMINO_CORE_NAMING_UTILITIES_H

//==============================================================================
// EXTERNAL DECLARATIONS
//==============================================================================

#include "CoreExport.h"

#include <Amino/Core/StringView.h>

namespace Amino {
class String;
}

namespace Amino {

//==============================================================================
// CLASS NamingUtilities
//==============================================================================

/// \brief A collection of Naming Utility methods.
class AMINO_CORE_SHARED_DECL NamingUtilities {
public:
    /// \brief Convert a string to a legal name by removing invalid characters.
    ///
    /// \details This method will clean up any illegal characters from a name
    /// to make it usable by external packages and also by the compiler
    /// back-end. The cleaning rules are:
    /// -# Valid characters are a-z A-Z 0-9 _ (excluding spaces).
    /// -# If the input name is empty (which is not a legal name), the output
    ///    name is a single underscore (i.e. "" becomes "_").
    /// -# Invalid characters at the start of the name are dropped: "+++abc"
    ///    becomes "abc".
    /// -# If the first valid character is a digit then an underscore is
    ///    inserted as the leading character: "012" becomes "_012".
    /// -# Invalid characters in the rest of the name are replaced with
    ///    underscore.
    /// -# Leading underscores and illegal characters are removed leaving one
    ///    underscore. If the leading underscore that is left after the removal
    ///    is followed by A-Z then this character is changed to lower case:
    ///    "___ABC" becomes "_aBC".
    ///
    /// \param [inout] name The name to legalize
    ///
    /// \return Returns true if the legalized name is different than the
    /// original name, false otherwise.
    static bool legalize(String& name);

    /// \copybrief   legalize
    /// See \ref legalize for conversion details.
    ///
    /// \param [in]  name       The name to legalize
    /// \param [out] legalName  The output legalized name
    ///
    /// \return Returns true if the legalized name is different than the
    /// original name, false otherwise.
    static bool getLegalName(StringView const& name, String& legalName);

    /// \brief Check if a name is legal.
    ///
    /// \details This method will check if a name requires clean up using the
    /// rules listed in \ref getLegalName.
    ///
    /// \param [in] name The name to check
    /// \return Returns true if the name is legal, false otherwise
    static bool isLegalName(StringView const& name);

public:
    /// \brief \ref NamingUtilities are static functions only.
    /// \{
    NamingUtilities()                                  = delete;
    NamingUtilities(const NamingUtilities&)            = delete;
    NamingUtilities& operator=(const NamingUtilities&) = delete;
    /// \}
};

} // namespace Amino

#endif
