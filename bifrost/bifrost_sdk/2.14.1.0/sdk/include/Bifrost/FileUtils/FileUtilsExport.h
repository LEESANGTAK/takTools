//-
// =============================================================================
// Copyright 2023 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

//
/// \file FileUtilsExport.h
///
/// \brief Definition of macros for symbol visibility.
///

#ifndef FILE_UTILS_DECL_H
#define FILE_UTILS_DECL_H

#if defined(_WIN32)
#define FILE_UTILS_EXPORT __declspec(dllexport)
#define FILE_UTILS_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define FILE_UTILS_EXPORT __attribute__((visibility("default")))
#define FILE_UTILS_IMPORT __attribute__((visibility("default")))
#else
#define FILE_UTILS_EXPORT
#define FILE_UTILS_IMPORT
#endif

#if defined(FILE_UTILS_BUILD_DLL)
#define FILE_UTILS_DECL FILE_UTILS_EXPORT
#else
#define FILE_UTILS_DECL FILE_UTILS_IMPORT
#endif

#endif // FILE_UTILS_DECL_H
