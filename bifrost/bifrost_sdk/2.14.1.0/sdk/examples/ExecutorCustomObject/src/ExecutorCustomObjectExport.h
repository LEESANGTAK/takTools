//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef EXECUTOR_CUSTOM_OBJECT_EXPORT
#define EXECUTOR_CUSTOM_OBJECT_EXPORT

#ifdef _WIN32
#ifdef EXECUTOR_CUSTOM_OBJECT_TRANSLATION_EXPORT
#define EXECUTOR_CUSTOM_OBJECT_TRANSLATION_SHARED_DECL __declspec(dllexport)
#else
#define EXECUTOR_CUSTOM_OBJECT_TRANSLATION_SHARED_DECL __declspec(dllimport)
#endif
#elif defined(__GNUC__)
#define EXECUTOR_CUSTOM_OBJECT_TRANSLATION_SHARED_DECL __attribute__((visibility("default")))
#else
#define EXECUTOR_CUSTOM_OBJECT_TRANSLATION_SHARED_DECL
#endif

#endif
