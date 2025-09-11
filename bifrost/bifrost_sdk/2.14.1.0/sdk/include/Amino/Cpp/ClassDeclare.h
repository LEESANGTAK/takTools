//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file ClassDeclare.h
///
/// \brief Macros used to declare functions and traits about classes exposed to
/// Amino.
///
/// This should be included in the .h file, and its counterpart \ref
/// ClassDefine.h should be included in the .cpp file.

#ifndef AMINO_CLASS_DECLARE_H_
#define AMINO_CLASS_DECLARE_H_

#include <Amino/Core/internal/DefaultClassDeclare.h>

//==============================================================================
// DECLARATION FOR AMINO CLASS / OPAQUE C++ TYPES DEFAULT VALUES
//==============================================================================

/// \brief Macro for generating the getDefault entry point declaration related
/// to a given opaque type.
///
/// \warning The \ref AMINO_DECLARE_DEFAULT_CLASS must be added in the header
/// file. It must be added in the global namespace (i.e. not in a namespace).
///
/// This is necessary to allow Amino graphs to create default values for
/// opaque, class types.
#define AMINO_DECLARE_DEFAULT_CLASS(API, TYPE) \
    AMINO_INTERNAL_DECLARE_DEFAULT_CLASS(API, TYPE)

#endif
