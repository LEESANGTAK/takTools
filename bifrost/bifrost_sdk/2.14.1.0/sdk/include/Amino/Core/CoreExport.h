//-
// =============================================================================
// Copyright 2023 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================

//+

//
/// \file CoreExport.h
///
/// \brief Definition of macros for symbol visibility.
///

#ifndef AMINO_CORE_EXPORT_H
#define AMINO_CORE_EXPORT_H

#if defined(_WIN32)
#if defined(AMINO_BUILD_CORE_SHARED)
#define AMINO_CORE_SHARED_DECL __declspec(dllexport)
#else
#define AMINO_CORE_SHARED_DECL __declspec(dllimport)
#endif
#elif defined(__GNUC__)
#define AMINO_CORE_SHARED_DECL __attribute__((visibility("default")))
#else
#error "Unsupported platform."
#endif

#endif
