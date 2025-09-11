//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

/// \file MeshAreaOpsExport.h
/// \brief Symbol visibility macros.

#ifndef MESH_AREA_OPS_EXPORT_H
#define MESH_AREA_OPS_EXPORT_H

#if defined(_WIN32)
#define MESH_AREA_OPS_EXPORT __declspec(dllexport)
#define MESH_AREA_OPS_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define MESH_AREA_OPS_EXPORT __attribute__((visibility("default")))
#define MESH_AREA_OPS_IMPORT __attribute__((visibility("default")))
#else
#error Unsupported platform.
#endif

#if defined(MESH_AREA_OPS_BUILD_DLL)
#define MESH_AREA_OPS_DECL MESH_AREA_OPS_EXPORT
#else
#define MESH_AREA_OPS_DECL MESH_AREA_OPS_IMPORT
#endif

#endif
