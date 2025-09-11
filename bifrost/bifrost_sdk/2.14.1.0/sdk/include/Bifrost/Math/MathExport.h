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
/// \file Bifrost/Math/MathExport.h
///
/// \brief Definition of macros for symbol visibility.
///

#ifndef BIFROST_MATH_EXPORT_H_
#define BIFROST_MATH_EXPORT_H_

#if defined(_WIN32)
#if defined(BIFROST_MATH_BUILD_SHARED)
#define BIFROST_MATH_SHARED_DECL __declspec(dllexport)
#else
#define BIFROST_MATH_SHARED_DECL __declspec(dllimport)
#endif
#elif defined(__GNUC__)
#define BIFROST_MATH_SHARED_DECL __attribute__((visibility("default")))
#else
#error "Unsupported platform."
#endif

#endif
