//-
//*****************************************************************************
// Copyright (c) 2023 Autodesk, Inc.
// All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

//
/// \file Bifrost/Object/ObjectFwd.h
///
/// \brief Bifrost object interface forward declaration.
///

#ifndef BIFROST_OBJECT_FWD_H
#define BIFROST_OBJECT_FWD_H

#include "ObjectExport.h"

#include <Amino/Cpp/Annotate.h>
#include <Amino/Cpp/ClassDeclare.h>

//------------------------------------------------------------------------------
/// \cond AMINO_INTERNAL_DOCS
/// \brief Use a define, otherwise clang-format gets confused.
/// \warning : Ignoring namespace is an internal feature, should not be used by
// external code.
#define BIFROST_IGNORE_NAMESPACE AMINO_ANNOTATE("Amino::Namespace ignore")
namespace Bifrost BIFROST_IGNORE_NAMESPACE {
#undef BIFROST_IGNORE_NAMESPACE
/// \endcond

class Object;

} // namespace BIFROST_IGNORE_NAMESPACE

/// \brief Macro for generating the getDefault entry point declaration related
/// to a given opaque type.
/// \see ClassDeclare.h
AMINO_DECLARE_DEFAULT_CLASS(OBJECT_DECL, Bifrost::Object);

#endif // AMINO_BIFROST_OBJECT_FWD_H
