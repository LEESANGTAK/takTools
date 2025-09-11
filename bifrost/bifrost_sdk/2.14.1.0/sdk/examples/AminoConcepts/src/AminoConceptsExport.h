//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef AMINO_CONCEPTS_EXPORT_H
#define AMINO_CONCEPTS_EXPORT_H

#if defined(_WIN32)
#define AMINO_CONCEPTS_EXPORT __declspec(dllexport)
#define AMINO_CONCEPTS_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define AMINO_CONCEPTS_EXPORT __attribute__((visibility("default")))
#define AMINO_CONCEPTS_IMPORT __attribute__((visibility("default")))
#else
#define AMINO_CONCEPTS_EXPORT
#define AMINO_CONCEPTS_IMPORT
#endif

#if defined(AMINO_CONCEPTS_BUILD_NODEDEF_DLL)
#define AMINO_CONCEPTS_DECL AMINO_CONCEPTS_EXPORT
#else
#define AMINO_CONCEPTS_DECL AMINO_CONCEPTS_IMPORT
#endif

#endif
