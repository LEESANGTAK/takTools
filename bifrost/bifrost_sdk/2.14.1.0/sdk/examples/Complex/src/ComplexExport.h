//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef COMPLEX_EXPORT_H
#define COMPLEX_EXPORT_H

#if defined(_WIN32)
#define COMPLEX_EXPORT __declspec(dllexport)
#define COMPLEX_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define COMPLEX_EXPORT __attribute__((visibility("default")))
#define COMPLEX_IMPORT __attribute__((visibility("default")))
#else
#define INDEX_SET_EXPORT
#define INDEX_SET_IMPORT
#endif

#if defined(COMPLEX_BUILD_NODEDEF_DLL)
#define COMPLEX_DECL COMPLEX_EXPORT
#else
#define COMPLEX_DECL COMPLEX_IMPORT
#endif

#endif
