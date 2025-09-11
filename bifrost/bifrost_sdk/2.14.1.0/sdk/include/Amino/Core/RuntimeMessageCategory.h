//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

/// \file RuntimeMessageCategory.h
/// \ref  Amino::RuntimeMessageCategory

#ifndef AMINO_CORE_RUNTIME_MESSAGE_CATEGORY_H
#define AMINO_CORE_RUNTIME_MESSAGE_CATEGORY_H

//==============================================================================
// NAMESPACE Amino
//==============================================================================

namespace Amino {

//==============================================================================
// ENUM RuntimeMessageCategory
//==============================================================================

/// \brief Category of the message logged at runtime (when executing a graph).
enum class RuntimeMessageCategory : unsigned short {
    kError = 1,   ///< The message refers to an error that prevents the regular
                  ///  execution of the current action.
    kWarning = 2, ///< The message refers to a warning that doesn't prevent the
                  ///  execution of the current action.
    kInfo = 3     ///< The message provides information to the user.
};

} // namespace Amino

#endif // AMINO_CORE_RUNTIME_MESSAGE_CATEGORY_H
