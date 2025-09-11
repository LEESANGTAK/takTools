//-
// =============================================================================
// Copyright 2025 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file  Cancellation.h
///
/// \see Amino::isJobCancelled()

#ifndef AMINO_CANCELLATION_H
#define AMINO_CANCELLATION_H

#pragma message("Cancellation.h is deprecated. Use a StopToken instead.")

#include "internal/Deprecated.h"

#include <Amino/Core/internal/ConfigMacros.h>

//==============================================================================
// EXTERNAL DECLARATIONS
//==============================================================================

namespace Amino {

AMINO_INTERNAL_DEPRECATED(
    "Amino::isJobCancelled is deprecated and now always returns false. "
    "Use a 'StopToken const& jobport instead. ")
inline bool isJobCancelled() { return Internal::deprecated_getFalse(); }

} // namespace Amino

#endif
