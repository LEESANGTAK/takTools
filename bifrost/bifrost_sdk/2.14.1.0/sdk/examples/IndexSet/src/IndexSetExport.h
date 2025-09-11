//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef INDEX_SET_EXPORT_H
#define INDEX_SET_EXPORT_H

#if defined(_WIN32)
#define INDEX_SET_EXPORT __declspec(dllexport)
#define INDEX_SET_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define INDEX_SET_EXPORT __attribute__((visibility("default")))
#define INDEX_SET_IMPORT __attribute__((visibility("default")))
#else
#define INDEX_SET_EXPORT
#define INDEX_SET_IMPORT
#endif

#if defined(INDEX_SET_BUILD_NODEDEF_DLL)
#define INDEX_SET_DECL INDEX_SET_EXPORT
#else
#define INDEX_SET_DECL INDEX_SET_IMPORT
#endif

#endif
