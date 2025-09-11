//-
// =============================================================================
// Copyright 2023 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file  PtrFwd.h
/// \brief Amino::Ptr's forward declarations.

#ifndef AMINO_PTR_FWD_H
#define AMINO_PTR_FWD_H

namespace Amino {

template <typename T>
class Ptr;

template <typename T>
class MutablePtr;

template <typename T>
class PtrGuard;

struct PointeeManager;

} // namespace Amino

#endif
