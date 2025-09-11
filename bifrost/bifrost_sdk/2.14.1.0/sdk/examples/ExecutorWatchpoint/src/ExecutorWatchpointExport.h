//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#ifndef EXECUTOR_WATCHPOINT_EXPORT_H
#define EXECUTOR_WATCHPOINT_EXPORT_H

#if defined(_WIN32)
#define EXECUTOR_WATCHPOINT_EXPORT __declspec(dllexport)
#define EXECUTOR_WATCHPOINT_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define EXECUTOR_WATCHPOINT_EXPORT __attribute__((visibility("default")))
#define EXECUTOR_WATCHPOINT_IMPORT __attribute__((visibility("default")))
#else
#define EXECUTOR_WATCHPOINT_EXPORT
#define EXECUTOR_WATCHPOINT_IMPORT
#endif

#if defined(EXECUTOR_WATCHPOINT_BUILD_DLL)
#define EXECUTOR_WATCHPOINT_DECL EXECUTOR_WATCHPOINT_EXPORT
#else
#define EXECUTOR_WATCHPOINT_DECL EXECUTOR_WATCHPOINT_IMPORT
#endif

#endif
