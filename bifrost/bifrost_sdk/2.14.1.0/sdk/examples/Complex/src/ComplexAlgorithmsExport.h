//-
// =============================================================================
// Copyright 2022 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#pragma once

#if defined(_WIN32)
#define COMPLEX_ALGORITHMS_EXPORT __declspec(dllexport)
#define COMPLEX_ALGORITHMS_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define COMPLEX_ALGORITHMS_EXPORT __attribute__((visibility("default")))
#define COMPLEX_ALGORITHMS_IMPORT __attribute__((visibility("default")))
#else
#define COMPLEX_ALGORITHMS_EXPORT
#define COMPLEX_ALGORITHMS_IMPORT
#endif

#if defined(COMPLEX_ALGORITHMS_BUILD_NODEDEF_DLL)
#define COMPLEX_ALGORITHMS_DECL COMPLEX_ALGORITHMS_EXPORT
#else
#define COMPLEX_ALGORITHMS_DECL COMPLEX_ALGORITHMS_IMPORT
#endif
