//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file TwistDeformerExport.h
/// \brief Symbol visibility macros.

#ifndef TWIST_DEFORMER_EXPORT_H
#define TWIST_DEFORMER_EXPORT_H

#if defined(_WIN32)
#define TWIST_DEFORMER_EXPORT __declspec(dllexport)
#define TWIST_DEFORMER_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define TWIST_DEFORMER_EXPORT __attribute__((visibility("default")))
#define TWIST_DEFORMER_IMPORT __attribute__((visibility("default")))
#else
#error Unsupported platform.
#endif

#if defined(TWIST_DEFORMER_BUILD_DLL)
#define TWIST_DEFORMER_DECL TWIST_DEFORMER_EXPORT
#else
#define TWIST_DEFORMER_DECL TWIST_DEFORMER_IMPORT
#endif

#endif
