//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef SIMPLE_ASSOCIATIVE_EXPORT_H
#define SIMPLE_ASSOCIATIVE_EXPORT_H

#if defined(_WIN32)
#define SIMPLE_ASSOCIATIVE_EXPORT __declspec(dllexport)
#define SIMPLE_ASSOCIATIVE_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define SIMPLE_ASSOCIATIVE_EXPORT __attribute__((visibility("default")))
#define SIMPLE_ASSOCIATIVE_IMPORT __attribute__((visibility("default")))
#else
#error Unsupported platform.
#endif

#if defined(SIMPLE_ASSOCIATIVE_BUILD_NODEDEF_DLL)
#define SIMPLE_ASSOCIATIVE_DECL SIMPLE_ASSOCIATIVE_EXPORT
#else
#define SIMPLE_ASSOCIATIVE_DECL SIMPLE_ASSOCIATIVE_IMPORT
#endif

#endif
