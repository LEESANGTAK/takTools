//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file ObjWriter Export.h
/// \brief Symbol visibility macros.

#ifndef OBJ_WRITER_EXPORT_H
#define OBJ_WRITER_EXPORT_H

#if defined(_WIN32)
#define OBJ_WRITER_EXPORT __declspec(dllexport)
#define OBJ_WRITER_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define OBJ_WRITER_EXPORT __attribute__((visibility("default")))
#define OBJ_WRITER_IMPORT __attribute__((visibility("default")))
#else
#error Unsupported platform.
#endif

#if defined(OBJ_WRITER_BUILD_DLL)
#define OBJ_WRITER_DECL OBJ_WRITER_EXPORT
#else
#define OBJ_WRITER_DECL OBJ_WRITER_IMPORT
#endif

#endif
