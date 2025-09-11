//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef VECTOR_LENGTH_EXPORT_H
#define VECTOR_LENGTH_EXPORT_H

#if defined(_WIN32)
#define VECTOR_LENGTH_EXPORT __declspec(dllexport)
#define VECTOR_LENGTH_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define VECTOR_LENGTH_EXPORT __attribute__((visibility("default")))
#define VECTOR_LENGTH_IMPORT __attribute__((visibility("default")))
#else
#define VECTOR_LENGTH_EXPORT
#define VECTOR_LENGTH_IMPORT
#endif

#if defined(VECTOR_LENGTH_BUILD_NODEDEF_DLL)
#define VECTOR_LENGTH_DECL VECTOR_LENGTH_EXPORT
#else
#define VECTOR_LENGTH_DECL VECTOR_LENGTH_IMPORT
#endif

#endif
