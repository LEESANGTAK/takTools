//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef SIMPLE_STRING_EXPORT_H
#define SIMPLE_STRING_EXPORT_H

#if defined(_WIN32)
#define SIMPLE_STRING_EXPORT __declspec(dllexport)
#define SIMPLE_STRING_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define SIMPLE_STRING_EXPORT __attribute__((visibility("default")))
#define SIMPLE_STRING_IMPORT __attribute__((visibility("default")))
#else
#error Unsupported platform.
#endif

#if defined(SIMPLE_STRING_BUILD_NODEDEF_DLL)
#define SIMPLE_STRING_DECL SIMPLE_STRING_EXPORT
#else
#define SIMPLE_STRING_DECL SIMPLE_STRING_IMPORT
#endif

#endif
