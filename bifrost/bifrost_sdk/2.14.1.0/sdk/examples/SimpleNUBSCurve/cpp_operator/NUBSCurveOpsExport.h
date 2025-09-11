//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef NUBS_CURVE_OPS_EXPORT_H
#define NUBS_CURVE_OPS_EXPORT_H

#if defined(_WIN32)
#define NUBS_CURVE_OPS_EXPORT __declspec(dllexport)
#define NUBS_CURVE_OPS_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define NUBS_CURVE_OPS_EXPORT __attribute__((visibility("default")))
#define NUBS_CURVE_OPS_IMPORT __attribute__((visibility("default")))
#else
#error Unsupported platform.
#endif

#if defined(NUBS_CURVE_OPS_BUILD_DLL)
#define NUBS_CURVE_OPS_DECL NUBS_CURVE_OPS_EXPORT
#else
#define NUBS_CURVE_OPS_DECL NUBS_CURVE_OPS_IMPORT
#endif

#endif
