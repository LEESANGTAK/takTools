//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//

#ifndef SIMPLE_NUBS_CURVE_EXPORT_H
#define SIMPLE_NUBS_CURVE_EXPORT_H

#if defined(_WIN32)
#define SIMPLE_NUBS_CURVE_EXPORT __declspec(dllexport)
#define SIMPLE_NUBS_CURVE_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define SIMPLE_NUBS_CURVE_EXPORT __attribute__((visibility("default")))
#define SIMPLE_NUBS_CURVE_IMPORT __attribute__((visibility("default")))
#else
#error Unsupported platform.
#endif

#if defined(SIMPLE_NUBS_CURVE_BUILD_DLL)
#define SIMPLE_NUBS_CURVE_DECL SIMPLE_NUBS_CURVE_EXPORT
#else
#define SIMPLE_NUBS_CURVE_DECL SIMPLE_NUBS_CURVE_IMPORT
#endif

#endif
