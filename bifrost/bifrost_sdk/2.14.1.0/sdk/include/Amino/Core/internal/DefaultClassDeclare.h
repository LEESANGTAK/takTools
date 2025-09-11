//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_DEFAULT_CLASS_DECLARE_H
#define AMINO_CORE_INTERNAL_DEFAULT_CLASS_DECLARE_H

#include "../PtrFwd.h"

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  DefaultClassDeclare.h
/// \brief Functions used to declare the default class getter function of an
///        opaque user type.

namespace Amino {
namespace Internal {
using GetDefaultClassFn = Ptr<void> const& (*)();

template <typename T>
Ptr<T> const& getDefaultClass() = delete;
} // namespace Internal
} // namespace Amino

#define AMINO_INTERNAL_DECLARE_DEFAULT_CLASS(API, TYPE) \
    namespace Amino {                                   \
    namespace Internal {                                \
    template <>                                         \
    API Ptr<TYPE> const& getDefaultClass();             \
    }                                                   \
    }                                                   \
    static_assert(true, "")

/// \endcond
#endif
