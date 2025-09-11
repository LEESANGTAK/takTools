//-
//*****************************************************************************
// Copyright (c) 2024 Autodesk, Inc.
// All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

//
/// \file GeometryExport.h
///
/// \brief Definition of macros for symbol visibility.
///

#ifndef BIFROST_GEOMETRY_EXPORT_H
#define BIFROST_GEOMETRY_EXPORT_H

#if defined(_WIN32)
#define BIFROST_GEOMETRY_EXPORT __declspec(dllexport)
#define BIFROST_GEOMETRY_IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
#define BIFROST_GEOMETRY_EXPORT __attribute__ ((visibility("default")))
#define BIFROST_GEOMETRY_IMPORT __attribute__ ((visibility("default")))
#else
#define BIFROST_GEOMETRY_EXPORT
#define BIFROST_GEOMETRY_IMPORT
#endif

#if defined(BIFROST_GEOMETRY_BUILD_DLL)
#define BIFROST_GEOMETRY_DECL BIFROST_GEOMETRY_EXPORT
#else
#define BIFROST_GEOMETRY_DECL BIFROST_GEOMETRY_IMPORT
#endif

#ifndef BIFMETADOC
#define BIFMETADOC(fDoc) \
    "{documentation, \\../docs/\\$\\{language\\}/" fDoc "}"
#endif

#ifndef BIFMETAICN
#define BIFMETAICN(fIcn) "{icon, \\../icons/" fIcn ".svg}"
#endif

#endif
