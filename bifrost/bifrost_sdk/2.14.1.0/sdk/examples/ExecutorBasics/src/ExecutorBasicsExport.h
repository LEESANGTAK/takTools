//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef EXECUTOR_BASICS_EXPORT
#define EXECUTOR_BASICS_EXPORT

#ifdef _WIN32
#ifdef EXECUTOR_BASICS_TRANSLATION_EXPORT
#define EXECUTOR_BASICS_TRANSLATION_SHARED_DECL __declspec(dllexport)
#else
#define EXECUTOR_BASICS_TRANSLATION_SHARED_DECL __declspec(dllimport)
#endif
#elif defined(__GNUC__)
#define EXECUTOR_BASICS_TRANSLATION_SHARED_DECL __attribute__((visibility("default")))
#else
#define EXECUTOR_BASICS_TRANSLATION_SHARED_DECL
#endif

#endif
