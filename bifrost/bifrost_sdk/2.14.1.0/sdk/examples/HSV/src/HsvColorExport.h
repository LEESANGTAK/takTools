//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef HSV_COLOR_EXPORT_H
#define HSV_COLOR_EXPORT_H

#if defined(_WIN32)
#define HSV_COLOR_EXPORT __declspec(dllexport)
#define HSV_COLOR_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define HSV_COLOR_EXPORT __attribute__((visibility("default")))
#define HSV_COLOR_IMPORT __attribute__((visibility("default")))
#else
#define HSV_COLOR_EXPORT
#define HSV_COLOR_IMPORT
#endif

#if defined(HSV_COLOR_BUILD_NODEDEF_DLL)
#define HSV_COLOR_DECL HSV_COLOR_EXPORT
#else
#define HSV_COLOR_DECL HSV_COLOR_IMPORT
#endif

#endif
