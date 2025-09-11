//-
// =============================================================================
// Copyright 2023 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CORE_INTERNAL_DEBUG_TYPE_ID_H
#define AMINO_CORE_INTERNAL_DEBUG_TYPE_ID_H

/// \cond AMINO_INTERNAL_DOCS
///
/// \file  DebugTypeId.h
/// \see Amino::Internal::DebugTypeId

#include <Amino/Core/CoreExport.h>
#include <Amino/Core/String.h>
#include <Amino/Core/TypeId.h>

namespace Amino {
namespace Internal {

/// \brief Internal helper class to get a debug type name from a \ref TypeId.
///
/// \warning Should only be used for debugging purposes. Those type names are an
/// implementation details and are subject to changes, therefore no tests should
/// rely on the result of this function outside of Amino.
class AMINO_CORE_SHARED_DECL DebugTypeId final {
public:
    /// \copydoc DebugTypeId
    static String getTypeNameForDebugOnly(TypeId const& typeId);

    /// \brief DebugTypeId is not constructible.
    /// \{
    DebugTypeId()  = delete;
    ~DebugTypeId() = delete;
    /// \}
};
} // namespace Internal
} // namespace Amino
/// \endcond

#endif
