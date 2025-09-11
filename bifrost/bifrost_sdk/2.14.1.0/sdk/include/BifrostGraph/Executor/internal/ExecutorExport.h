//-
// ================================================================================================
// Copyright 2023 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file ExecutorExport.h
/// \brief BifrostGraph Executor Definition of macros for symbol visibility.
///
/// Use BIFROSTGRAPH_EXECUTOR_SHARED_DECL in your header files.
///
/// Make sure BIFROSTGRAPH_EXECUTOR_BUILD_DLL is defined when compiling

#ifndef BIFROSTGRAPH_EXECUTOR_EXPORT_H
#define BIFROSTGRAPH_EXECUTOR_EXPORT_H

#ifdef _WIN32
#ifdef BIFROSTGRAPH_EXECUTOR_BUILD_DLL
#define BIFROSTGRAPH_EXECUTOR_SHARED_DECL __declspec(dllexport)
#else
#define BIFROSTGRAPH_EXECUTOR_SHARED_DECL __declspec(dllimport)
#endif
#elif defined(__GNUC__)
#define BIFROSTGRAPH_EXECUTOR_SHARED_DECL __attribute__((visibility("default")))
#else
#define BIFROSTGRAPH_EXECUTOR_SHARED_DECL
#endif

#endif
